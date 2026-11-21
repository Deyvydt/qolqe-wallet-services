"""QUÉ ES: sube los resultados de cada ejecución del pipeline a QASE (gestión de casos de prueba).

PARA QUÉ:
  Las pruebas se ejecutan muchas veces (cada push, cada PR). Qase guarda cada ejecución como un
  "test run" y acumula el historial POR CASO: en qué run pasó, en cuál falló y desde cuándo.
  Este script:
    1. Lee los resultados de pytest (JUnit) y de Robot Framework (output.xml) con las mismas
       funciones que usa la matriz de trazabilidad (trazabilidad.py, misma carpeta).
    2. Se asegura de que cada prueba exista como CASO en el repositorio de Qase (busca por título
       y crea las que falten, en la suite que corresponde). El título es estable entre ejecuciones,
       así el historial se acumula siempre en el mismo caso.
    3. Crea un test run con el commit y el enlace al run de GitHub, sube los resultados y lo cierra.
  Si no hay token o Qase falla, imprime "Qase no disponible" y termina con éxito (exit 0):
  la herramienta de gestión nunca rompe el pipeline.

CÓMO SE USA (desde la raíz del repo; el token va en el secret QASE_API_TOKEN):
  python .github/scripts/qase_subir.py --junit reportes/api/junit.xml --robot reportes/web/output.xml \
      --proyecto QOLQE --titulo-run "Pipeline #12" --commit abc1234 --url-run https://github.com/...
  --dry-run  muestra qué casos crearía y qué resultados subiría, sin llamar a la red.
  Solo usa la librería estándar de Python (urllib). API: Qase REST v1 (https://developers.qase.io).
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

from trazabilidad import contexto_run, leer_reporte, nombre_caso

API = os.environ.get("QASE_API_URL", "https://api.qase.io/v1")  # se cambia solo en las pruebas unitarias
ESPERA = 2.0  # segundos base entre reintentos (crece al doble); las pruebas lo ponen en 0
INTENTOS = 4

# Suites ya creadas en el proyecto QOLQE de Qase (id → nombre en la interfaz).
SUITE_API_FUNCIONAL = 1       # 'API - Funcional'
SUITE_API_TECNICO = 2         # 'API - Técnico (contrato, auth, validación)'
SUITE_WEB_NUCLEO = 3          # 'Web E2E - Núcleo común'
SUITE_WEB_G2 = 4              # 'Web E2E - G2 Servicios'
# Campos personalizados del proyecto (id → nombre).
CAMPO_ENDPOINT, CAMPO_HU = "1", "2"

# Endpoint principal de cada HU del módulo G2 (docs/requisitos.md y qolqe/api/servicios.py).
ENDPOINT_POR_HU = {
    "HU-G2-01": "GET /api/servicios/deudas",
    "HU-G2-02": "POST /api/servicios/pagos",
    "HU-G2-03": "POST /api/servicios/afiliaciones",
    "HU-G2-04": "GET /api/servicios/afiliaciones",
    "HU-G2-05": "PUT /api/servicios/afiliaciones/{afiliacion_id}",
    "HU-G2-06": "DELETE /api/servicios/afiliaciones/{afiliacion_id}",
    "HU-G2-07": "GET /api/servicios/pagos/{codigo_operacion}",
}
ETIQUETAS_TECNICAS = {"tecnico", "contrato", "schemathesis"}


class QaseError(Exception):
    pass


# ---------------------------------------------------------------------------------------
# 1. Resultados → casos de Qase
# ---------------------------------------------------------------------------------------
def cargar(rutas_junit, ruta_robot):
    casos = []
    for ruta in list(rutas_junit or []) + ([ruta_robot] if ruta_robot else []):
        _, leidos = leer_reporte(ruta)
        if leidos is None:
            print(f"Aviso: sin resultados en {ruta}", file=sys.stderr)
            continue
        # Las pruebas de este mismo script (tests/qase) no son casos del producto.
        casos += [c for c in leidos if "herramienta" not in c["etiquetas"]]
    return casos


def titulo(c):
    """Estable entre ejecuciones: nivel + nombre de la prueba (+ CP en la web)."""
    return f"[{c['nivel']}] {nombre_caso(c)}"[:255]


def suite(c):
    if c["nivel"] == "web":
        # El núcleo común usa HU sin módulo (HU-1, HU-2...); el módulo G2 usa HU-G2-0X.
        return SUITE_WEB_G2 if "G2" in c["etiquetas"] or any(h.startswith("HU-G2") for h in c["hu"]) \
            else SUITE_WEB_NUCLEO
    if c["nivel"] == "contrato" or ETIQUETAS_TECNICAS & set(c["etiquetas"]):
        return SUITE_API_TECNICO
    return SUITE_API_FUNCIONAL


def endpoint(c):
    return ", ".join(dict.fromkeys(ENDPOINT_POR_HU[h] for h in c["hu"] if h in ENDPOINT_POR_HU))


def datos_caso(c):
    hu = ", ".join(h for h in c["hu"] if h.startswith("HU-"))
    return {
        "title": titulo(c),
        "suite_id": suite(c),
        "description": f"Nivel: {c['nivel']}\nHistoria de usuario: {hu or '—'}\nEndpoint: {endpoint(c) or '—'}",
        "automation": 2,  # 2 = automatizado  # verificar contra la API real
        "tags": c["etiquetas"],
        "custom_field": {CAMPO_ENDPOINT: endpoint(c), CAMPO_HU: hu},
    }


def datos_resultado(c, case_id):
    if c["estado"] == "xfailed":
        estado = "skipped"  # Qase no tiene "fallo esperado": se sube como omitido y se explica
        comentario = f"Fallo esperado: defecto conocido {c['defecto'] or '(sin ID)'} (ver docs/defectos.md). {c['mensaje']}"
    else:
        estado = c["estado"] if c["estado"] in ("passed", "failed", "skipped") else "failed"
        comentario = c["mensaje"]
    resultado = {"case_id": case_id, "status": estado, "time_ms": c.get("duracion_ms", 0)}
    if comentario:
        resultado["comment"] = comentario.strip()
    if estado == "failed" and c["mensaje"]:
        resultado["stacktrace"] = c["mensaje"]
    return resultado


# ---------------------------------------------------------------------------------------
# 2. Cliente mínimo de la API REST v1 de Qase
# ---------------------------------------------------------------------------------------
class Qase:
    def __init__(self, token, base=None):
        self.token, self.base = token, (base or API).rstrip("/")

    def pedir(self, metodo, ruta, cuerpo=None):
        datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
        for intento in range(INTENTOS):
            pedido = urllib.request.Request(self.base + ruta, data=datos, method=metodo, headers={
                "Token": self.token, "Content-Type": "application/json", "Accept": "application/json"})
            try:
                with urllib.request.urlopen(pedido, timeout=30) as respuesta:
                    contenido = json.loads(respuesta.read() or b"{}")
                break
            except urllib.error.HTTPError as error:
                reintentar = error.code == 429 or error.code >= 500
                if not reintentar or intento == INTENTOS - 1:
                    raise QaseError(f"{metodo} {ruta} → HTTP {error.code}: {error.read()[:200]!r}") from None
            except urllib.error.URLError as error:
                if intento == INTENTOS - 1:
                    raise QaseError(f"{metodo} {ruta} → {error.reason}") from None
            time.sleep(ESPERA * 2 ** intento)
        if not contenido.get("status", True):
            raise QaseError(f"{metodo} {ruta} → {contenido.get('errorMessage') or contenido}")
        return contenido.get("result", {})

    def casos_existentes(self, codigo):
        """{título: id} recorriendo todas las páginas."""
        existentes, offset = {}, 0
        while True:
            pagina = self.pedir("GET", f"/case/{codigo}?limit=100&offset={offset}")
            entidades = pagina.get("entities", [])
            existentes.update({e["title"]: e["id"] for e in entidades})
            offset += len(entidades)
            if not entidades or offset >= pagina.get("filtered", pagina.get("total", 0)):
                return existentes


def asegurar_casos(qase, codigo, casos):
    ids = qase.casos_existentes(codigo)
    creados = 0
    for c in casos:
        t = titulo(c)
        if t not in ids:
            ids[t] = qase.pedir("POST", f"/case/{codigo}", datos_caso(c))["id"]
            creados += 1
    print(f"Qase: {len(casos)} casos en este run · {creados} creados · {len(casos) - creados} reutilizados")
    return ids


def subir(qase, codigo, casos, titulo_run, commit, url_run):
    ids = asegurar_casos(qase, codigo, casos)
    run_id = qase.pedir("POST", f"/run/{codigo}", {
        "title": titulo_run,
        "description": f"Commit: {commit}\nRun de GitHub Actions: {url_run or '—'}",
        "cases": sorted({ids[titulo(c)] for c in casos}),
        "is_autotest": True,
    })["id"]
    qase.pedir("POST", f"/result/{codigo}/{run_id}/bulk",
               {"results": [datos_resultado(c, ids[titulo(c)]) for c in casos]})
    qase.pedir("POST", f"/run/{codigo}/{run_id}/complete")
    return run_id


# ---------------------------------------------------------------------------------------
# 3. Programa
# ---------------------------------------------------------------------------------------
def simular(codigo, casos, titulo_run, commit, url_run):
    print(f"[dry-run] Proyecto {codigo} · run '{titulo_run}' · commit {commit} · {url_run or 'sin URL'}")
    for c in casos:
        r = datos_resultado(c, "?")
        print(f"  suite {suite(c)} · {r['status']:<7} · {r['time_ms']:>6} ms · {titulo(c)}")
    print(f"[dry-run] {len(casos)} casos; no se llamó a la red.")


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ctx = contexto_run()
    p = argparse.ArgumentParser(description="Sube los resultados del pipeline a Qase (un test run por ejecución).")
    p.add_argument("--junit", nargs="+", default=[], help="uno o varios JUnit XML de pytest")
    p.add_argument("--robot", help="output.xml de Robot Framework (opcional)")
    p.add_argument("--proyecto", default="QOLQE", help="código del proyecto en Qase")
    p.add_argument("--titulo-run", default=f"Pipeline #{ctx['numero']} · {ctx['rama']}")
    p.add_argument("--commit", default=ctx["commit"])
    p.add_argument("--url-run", default=ctx["url_run"], help="enlace al run de GitHub Actions")
    p.add_argument("--dry-run", action="store_true", help="solo muestra lo que haría, sin red")
    args = p.parse_args(argv)

    casos = cargar(args.junit, args.robot)
    if args.dry_run:
        simular(args.proyecto, casos, args.titulo_run, args.commit, args.url_run)
        return 0
    token = os.environ.get("QASE_API_TOKEN", "").strip()
    if not token:
        print("Qase no disponible: falta el secret QASE_API_TOKEN (se omite la subida).")
        return 0
    if not casos:
        print("Qase no disponible: no hay resultados que subir.")
        return 0
    try:
        run_id = subir(Qase(token), args.proyecto, casos, args.titulo_run, args.commit, args.url_run)
    except Exception as error:  # nunca romper el pipeline por la herramienta de gestión
        print(f"Qase no disponible: {error}")
        return 0
    url = f"https://app.qase.io/run/{args.proyecto}/dashboard/{run_id}"
    print(f"Qase: run #{run_id} → {url}")
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as resumen:
            resumen.write(f"\n### Gestión de casos (Qase)\n\nRun #{run_id} con {len(casos)} resultados: [{url}]({url})\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
