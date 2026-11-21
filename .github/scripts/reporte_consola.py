"""QUÉ ES: el REPORTE FINAL EN CONSOLA del pipeline (último paso del último job).

PARA QUÉ: quien abre el run ve en segundos, sin descargar nada, el veredicto, los quality gates,
  los totales por suite, la cobertura por endpoint, los defectos conocidos y las fallas nuevas.
  El detalle navegable sigue en GitHub Pages (HTML) y el historial en Qase.

CÓMO SE USA (desde la raíz del repo, también en local):
  python .github/scripts/reporte_consola.py --api reportes/api/junit.xml \
      --contrato reportes/contrato/junit.xml --web reportes/web/output.xml \
      --evidencia con   (rendimiento: datos-reporte/rendimiento.json)
  En el pipeline lee el resultado de cada job de la variable NEEDS. Sin NEEDS, los gates se deducen
  de los reportes. Respeta NO_COLOR. Solo informa: quien aprueba o bloquea es el job quality-gate.
"""
import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path

from trazabilidad import contar, contexto_run, leer_reporte, nombre_endpoint, tabla_endpoints

ANCHO = 92
COLOR = {"verde": "32", "rojo": "31", "amarillo": "33", "cian": "36", "gris": "90", "negrita": "1"}
GATES = [
    ("contrato", "Contrato OpenAPI", "0 respuestas 5xx · validaciones correctas"),
    ("api", "API funcional + técnica", "0 fallos nuevos · defectos como xfail estricto"),
    ("web", "Web E2E (Gherkin)", "todas las ejecuciones seguidas en verde"),
    ("rendimiento", "Rendimiento (k6 humo)", "p95 < 800/1500 ms · errores < 1 % · dinero íntegro"),
]


def pintar(texto, *estilos):
    if os.environ.get("NO_COLOR"):
        return texto
    return "".join(f"\033[{COLOR[e]}m" for e in estilos) + texto + "\033[0m"


def titulo(texto):
    print()
    print(pintar(f"── {texto} ".ljust(ANCHO, "─"), "cian", "negrita"))


def barra(n, total, largo=20):
    llenos = round(largo * n / total) if total else 0
    return pintar("█" * llenos, "verde") + pintar("░" * (largo - llenos), "gris")


def estado_gate(resultado):
    return {"success": pintar("✔ APROBADO", "verde"), "skipped": pintar("○ NO APLICA", "gris"),
            "failure": pintar("✖ FALLÓ", "rojo", "negrita"),
            "cancelled": pintar("▲ CANCELADO", "amarillo")}.get(resultado, resultado)


def resultado_suite(casos):
    if casos is None:
        return "skipped"
    return "failure" if contar(casos)["failed"] else "success"


def resultados_gates(suites, rendimiento):
    needs = json.loads(os.environ.get("NEEDS") or "{}")
    if needs:
        return {clave: needs.get(clave, {}).get("result", "skipped") for clave, _, _ in GATES}
    calculado = {clave: resultado_suite(suites[clave]) for clave in ("contrato", "api", "web")}
    if rendimiento is None:
        calculado["rendimiento"] = "skipped"
    else:
        ok = rendimiento["umbrales_k6_cumplidos"] and rendimiento["integridad_dinero"]["ok"]
        calculado["rendimiento"] = "success" if ok else "failure"
    return calculado


def veredicto(gates):
    # Sin contrato aprobado nada más corre: un "no aplica" ahí nunca puede dar verde.
    return gates["contrato"] == "success" and not any(r in ("failure", "cancelled") for r in gates.values())


def seccion_gates(gates):
    titulo("QUALITY GATES")
    for clave, nombre, umbral in GATES:
        print(f"  {nombre:<26}{umbral:<52}{estado_gate(gates[clave])}")


def seccion_suites(suites):
    titulo("RESULTADOS POR SUITE")
    print(pintar(f"  {'Suite':<14}{'Total':>6}{'Pasan':>7}{'Esper.':>8}{'Fallan':>8}{'Omit.':>7}   Avance", "gris"))
    acumulado = Counter()
    for nombre, clave in (("Contrato", "contrato"), ("API", "api"), ("Web E2E", "web")):
        casos = suites[clave]
        if casos is None:
            print(f"  {nombre:<14}{pintar('no se ejecutó', 'gris')}")
            continue
        c = contar(casos)
        fila = Counter(passed=c["passed"], xfailed=c["xfailed"], failed=c["failed"], skipped=c["skipped"])
        acumulado += fila
        fallan = pintar(f"{fila['failed']:>8}", "rojo", "negrita") if fila["failed"] else f"{0:>8}"
        print(f"  {nombre:<14}{len(casos):>6}{fila['passed']:>7}{fila['xfailed']:>8}{fallan}{fila['skipped']:>7}   "
              f"{barra(fila['passed'] + fila['xfailed'], len(casos))}")
    total = sum(acumulado.values())
    print(pintar(f"  {'TOTAL':<14}{total:>6}{acumulado['passed']:>7}{acumulado['xfailed']:>8}"
                 f"{acumulado['failed']:>8}{acumulado['skipped']:>7}", "negrita"))
    print(pintar("  Esper. = fallo esperado por un defecto ya reportado · Omit. = escenario web @defecto", "gris"))


def seccion_endpoints(casos):
    if not casos:
        return
    titulo("COBERTURA DE API POR ENDPOINT")
    print(pintar(f"  {'Endpoint':<50}{'Func.':>6}{'Técn.':>6}{'Total':>6}{'Pasan':>6}{'Esper.':>7}{'Fallan':>7}", "gris"))
    filas, total = tabla_endpoints(casos)

    def numeros(fila):
        func, tec, resto = (sum(fila[t].values()) for t in ("funcional", "tecnico", "sin tipo"))
        estados = Counter()
        for t in fila.values():
            estados.update(t)
        return func, tec, func + tec + resto, estados["passed"], estados["xfailed"], estados["failed"]

    for endpoint, fila in filas:
        print(f"  {nombre_endpoint(endpoint)[:49]:<50}" + "".join(
            f"{n:>{w}}" for n, w in zip(numeros(fila), (6, 6, 6, 6, 7, 7))))
    print(pintar(f"  {'TOTAL':<50}" + "".join(f"{n:>{w}}" for n, w in zip(numeros(total), (6, 6, 6, 6, 7, 7))), "negrita"))


def seccion_rendimiento(a):
    if a is None:
        return
    titulo("RENDIMIENTO (k6 humo en CI · carga, pico, estrés y resistencia en tests/performance/resultados)")
    e = a["etapas"].get("estable", {})
    print(f"  p95 consultas {e.get('p95_consulta_ms', '—')} ms   p95 dinero {e.get('p95_dinero_ms', '—')} ms   "
          f"errores técnicos {e.get('error_tecnico_%', '—')} %   peticiones {e.get('peticiones', '—')}")
    print(f"  Umbrales k6: {estado_gate('success' if a['umbrales_k6_cumplidos'] else 'failure')}   "
          f"Integridad del dinero: {estado_gate('success' if a['integridad_dinero']['ok'] else 'failure')}")


def seccion_defectos(casos):
    conocidos = Counter(c["defecto"] for c in casos if c["defecto"] and c["estado"] in ("xfailed", "skipped"))
    if conocidos:
        titulo("DEFECTOS CONOCIDOS DETECTADOS EN ESTA EJECUCIÓN (docs/defectos.md)")
        print("  " + "   ".join(pintar(f"{d} ×{n}", "amarillo") for d, n in sorted(conocidos.items())))
    nuevas = [c for c in casos if c["estado"] == "failed"]
    if nuevas:
        titulo(f"FALLAS NUEVAS ({len(nuevas)})")
        for c in nuevas[:15]:
            print(pintar(f"  ✖ [{c['nivel']}] {c['nombre'][:80]}", "rojo"))
            if c["mensaje"]:
                print(pintar(f"      {c['mensaje'][:84]}", "gris"))
        if len(nuevas) > 15:
            print(pintar(f"  … y {len(nuevas) - 15} más en el reporte HTML", "gris"))


def seccion_enlaces(ctx):
    titulo("DÓNDE VER EL DETALLE")
    usuario, _, repo = ctx["repo"].partition("/")
    enlaces = [("Reportes HTML", f"https://{usuario.lower()}.github.io/{repo}/"),
               ("Historial (Qase)", "https://app.qase.io/project/QOLQE"),
               ("Defectos", ctx["url_defectos"])]
    if ctx["url_run"]:
        enlaces.insert(0, ("Este run", ctx["url_run"]))
    for nombre, url in enlaces:
        print(f"  {nombre:<18}{pintar(url, 'cian')}")


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="Reporte final consolidado en consola.")
    for opcion in ("--api", "--contrato", "--web"):
        p.add_argument(opcion)
    p.add_argument("--evidencia", default="con", choices=("con", "sin"))
    args = p.parse_args(argv)

    suites = {clave: leer_reporte(getattr(args, clave))[1] for clave in ("contrato", "api", "web")}
    archivo = Path("datos-reporte/rendimiento.json")  # ruta fija: no depende de argumentos
    rendimiento = json.loads(archivo.read_text(encoding="utf-8")) if archivo.is_file() else None
    gates = resultados_gates(suites, rendimiento)
    aprobado = veredicto(gates)
    ctx = contexto_run()

    print(pintar("═" * ANCHO, "cian"))
    print(pintar("  QOLQE WALLET · REPORTE FINAL DE PRUEBAS", "negrita"))
    print(pintar(f"  Run #{ctx['numero']} · commit {ctx['commit']} · {os.environ.get('RAMA') or ctx['rama']} · "
                 f"{ctx['fecha']} · evidencia: {args.evidencia}", "gris"))
    print(pintar("═" * ANCHO, "cian"))
    print()
    print("  VEREDICTO: " + (pintar(" ✔ APROBADO ", "verde", "negrita") if aprobado
                             else pintar(" ✖ RECHAZADO ", "rojo", "negrita")))

    seccion_gates(gates)
    seccion_suites(suites)
    api = (suites["api"] or []) + (suites["contrato"] or [])
    seccion_endpoints(api)
    seccion_rendimiento(rendimiento)
    seccion_defectos(api + (suites["web"] or []))
    seccion_enlaces(ctx)
    print(pintar("═" * ANCHO, "cian"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
