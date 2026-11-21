"""QUÉ ES: AGENTE DE TRIAJE DE FALLAS. Capacidad de IA del pipeline.

PARA QUÉ:
  Cuando una prueba falla, alguien tiene que leer la traza y decidir: ¿es un defecto del
  producto, una prueba frágil o un problema del entorno (red, timeout, runner)? ¿Es un
  defecto ya reportado (DEF-0X)? Este script hace ese primer análisis y lo deja en el
  resumen del run, para que la persona que revisa empiece con una hipótesis y un siguiente paso.

CÓMO FUNCIONA:
  1. Lee los reportes (JUnit de pytest y/o output.xml de Robot) y saca cada prueba que FALLÓ
     sin estar marcada como defecto conocido (los xfail esperados ya están triados). Un xfail
     estricto que pasa sin querer (XPASS) aparece en JUnit como failure, así que también entra.
  2. Por cada falla corre un bucle de AGENTE contra un LLM de GitHub Models (function calling).
     El modelo puede pedir herramientas antes de responder:
       - leer_defectos()                       → docs/defectos.md (defectos conocidos)
       - ver_diff_commit()                     → git show --stat HEAD (qué cambió)
       - leer_fragmento_codigo(ruta, desde, hasta) → líneas de un archivo DEL REPO
  3. La respuesta final es JSON estricto y se VALIDA: categoría dentro de 3 valores, DEF solo
     de la lista que existe en docs/defectos.md, confianza entre 0 y 1.
  4. Escribe un Markdown en GITHUB_STEP_SUMMARY (o pantalla) y un JSON con el detalle.

  Si no hay token, el modelo falla o hay límite de uso, NO rompe nada: avisa "triaje IA no
  disponible" y muestra la clasificación por reglas (modo --offline). Siempre termina con exit 0.
  Al modelo solo se envían el nombre de la prueba y su traza (sin variables de entorno).

CÓMO SE USA (desde la raíz del repo):
  python .github/scripts/triaje_ia.py reportes/api/junit.xml reportes/web/output.xml --json reportes/triaje.json
  python .github/scripts/triaje_ia.py reportes/api/junit.xml --offline     # solo reglas, sin red
  Variables: GITHUB_TOKEN (permiso models: read), TRIAJE_MODELO (por defecto openai/gpt-4.1-mini).
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

from trazabilidad import RAIZ_REPO, DEFECTOS_MD, agregar_a_summary, nombre_legible

ENDPOINT = "https://models.github.ai/inference/chat/completions"
MODELO = os.environ.get("TRIAJE_MODELO", "openai/gpt-4.1-mini")
CATEGORIAS = ("defecto_real", "prueba_fragil", "entorno")
MAX_TRAZA = 3000      # caracteres de traza que se envían al modelo
MAX_PASOS = 6         # vueltas del bucle del agente por falla
MAX_LINEAS = 120      # líneas máximas que devuelve leer_fragmento_codigo


class IANoDisponible(Exception):
    """Sin token, sin red, límite de uso o respuesta inválida: se degrada a reglas."""


# ---------------------------------------------------------------------------------------
# 1. Extraer fallas de los reportes
# ---------------------------------------------------------------------------------------
def _limpiar(texto):
    """Recorta y quita lo que parezca un secreto antes de mandarlo fuera."""
    texto = re.sub(r"(gh[pousr]_|github_pat_)[A-Za-z0-9_]+", "***", texto or "")
    texto = re.sub(r"(?i)(bearer|authorization|token|password|contraseña)(\W{1,3})\S+", r"\1\2***", texto)
    return texto.strip()[:MAX_TRAZA]


def extraer_fallas(ruta):
    """Devuelve [{prueba, origen, mensaje}] de las pruebas que fallaron sin defecto conocido."""
    if not ruta or not Path(ruta).is_file():
        return []
    try:
        raiz = ET.parse(ruta).getroot()
    except ET.ParseError as error:
        print(f"Aviso: no se pudo leer {ruta}: {error}", file=sys.stderr)
        return []
    fallas = []
    if raiz.tag == "robot":
        for test in raiz.iter("test"):
            status = test.find("status")
            etiquetas = [t.text or "" for t in test.findall("tag") + test.findall("tags/tag")]
            if status is None or status.get("status", "").upper() != "FAIL":
                continue
            if any(re.fullmatch(r"DEF-\d+", e.strip()) for e in etiquetas):
                continue  # fallo esperado: ya está triado
            fallas.append({"prueba": test.get("name", ""), "origen": "robot",
                           "mensaje": _limpiar(status.text)})
    elif raiz.tag in ("testsuites", "testsuite"):
        for tc in raiz.iter("testcase"):
            falla = tc.find("failure")
            if falla is None:
                falla = tc.find("error")
            if falla is None:
                continue
            texto = "\n".join(t for t in (falla.get("message"), falla.text) if t)
            nombre = f"{tc.get('classname', '')}::{nombre_legible(tc.get('name', ''))}".strip(":")
            fallas.append({"prueba": nombre, "origen": "pytest", "mensaje": _limpiar(texto)})
    return fallas


def defectos_conocidos():
    """IDs DEF-xx que existen en docs/defectos.md (la única lista válida para el modelo)."""
    try:
        return sorted(set(re.findall(r"^## (DEF-\d+)", DEFECTOS_MD.read_text(encoding="utf-8"), re.M)))
    except OSError:
        return []


# ---------------------------------------------------------------------------------------
# 2. Línea base: clasificador por reglas (sin red)
# ---------------------------------------------------------------------------------------
REGLAS_ENTORNO = r"connection ?refused|ConnectionError|ECONNREFUSED|Name or service not known|" \
                 r"timed? ?out|ReadTimeout|No space left|503 Service Unavailable"
REGLAS_FRAGIL = r"locator|selector|element not (found|visible)|not attached|strict mode violation|" \
                r"waiting for .*visible|StaleElement|flaky"
# Huellas de los defectos conocidos en las trazas (sacadas de docs/defectos.md).
REGLAS_DEF = [
    ("DEF-03", r"EN_COBRANZA|DEUDA_EN_COBRANZA"),
    ("DEF-04", r"debitos_pagados"),
    ("DEF-01", r"SUMINISTRO_INVALIDO|\b\d{13}\b"),
    ("DEF-02", r"d[ií]as de atraso|dias_atraso|mora"),
    ("DEF-05", r"database is locked|estr[eé]s|1 ?200 VUs"),
    ("DEF-06", r"motivo=sesion|datos viejos|actualiza al instante|responde antes de guardar"),
]


def clasificar_offline(falla):
    m = f"{falla['prueba']}\n{falla['mensaje']}"
    for defecto, patron in REGLAS_DEF:
        if re.search(patron, m, re.I):
            return _resultado(falla, "defecto_real", defecto, f"La traza coincide con la huella de {defecto}.",
                              f"Confirmar contra {defecto} en docs/defectos.md.", 0.6)
    if re.search(REGLAS_FRAGIL, m, re.I):
        return _resultado(falla, "prueba_fragil", None, "Falla al ubicar o esperar un elemento de la página.",
                          "Revisar el locator o la espera; volver a correr la prueba.", 0.5)
    if re.search(REGLAS_ENTORNO, m, re.I):
        return _resultado(falla, "entorno", None, "Error de red, timeout o recurso del runner.",
                          "Volver a ejecutar el job; revisar que el servicio esté levantado.", 0.5)
    return _resultado(falla, "defecto_real", None, "Aserción de negocio fallida sin huella conocida.",
                      "Reproducir a mano y, si se confirma, reportar un defecto nuevo.", 0.3)


def _resultado(falla, categoria, defecto, causa, paso, confianza, fuente="reglas"):
    return {"prueba": falla["prueba"], "categoria": categoria, "defecto_conocido": defecto,
            "causa_probable": causa, "siguiente_paso": paso, "confianza": confianza, "fuente": fuente}


# ---------------------------------------------------------------------------------------
# 3. Herramientas del agente
# ---------------------------------------------------------------------------------------
def leer_defectos():
    return DEFECTOS_MD.read_text(encoding="utf-8")


def ver_diff_commit():
    r = subprocess.run(["git", "show", "--stat", "--format=%h %s", "HEAD"], cwd=RAIZ_REPO,
                       capture_output=True, text=True, encoding="utf-8", timeout=20)
    return (r.stdout or r.stderr)[:4000]


def leer_fragmento_codigo(ruta, desde=1, hasta=60):
    """Solo archivos dentro del repo, nada de .git ni archivos de entorno."""
    destino = (RAIZ_REPO / str(ruta)).resolve()
    if not destino.is_relative_to(RAIZ_REPO) or ".git" in destino.parts or destino.name.startswith(".env"):
        return "Error: ruta fuera del repositorio o no permitida."
    if not destino.is_file():
        return f"Error: no existe {ruta}."
    desde = max(1, int(desde))
    hasta = min(int(hasta), desde + MAX_LINEAS - 1)
    lineas = destino.read_text(encoding="utf-8", errors="replace").splitlines()[desde - 1:hasta]
    return "\n".join(f"{desde + i}: {l}" for i, l in enumerate(lineas))


HERRAMIENTAS = {"leer_defectos": leer_defectos, "ver_diff_commit": ver_diff_commit,
                "leer_fragmento_codigo": leer_fragmento_codigo}

ESQUEMA_HERRAMIENTAS = [
    {"type": "function", "function": {"name": "leer_defectos",
     "description": "Devuelve docs/defectos.md: defectos conocidos DEF-xx con regla, pasos, esperado vs obtenido y causa probable.",
     "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "ver_diff_commit",
     "description": "Devuelve git show --stat HEAD: archivos que cambió el último commit.",
     "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "leer_fragmento_codigo",
     "description": "Lee líneas de un archivo del repositorio (p. ej. qolqe/reglas/servicios.py o tests/api/conftest.py).",
     "parameters": {"type": "object", "properties": {
         "ruta": {"type": "string", "description": "ruta relativa a la raíz del repo"},
         "desde": {"type": "integer"}, "hasta": {"type": "integer"}}, "required": ["ruta"]}}},
]

SISTEMA = """Eres un agente de triaje de fallas de pruebas automatizadas de Qolqe Wallet (módulo G2, pago de servicios).
Recibes UNA prueba fallida con su traza. Usa las herramientas si te ayudan (leer_defectos casi siempre;
el código de reglas está en qolqe/reglas/servicios.py y los pasos de prueba en tests/api/conftest.py).
Clasifica en una categoría:
- defecto_real: el producto no cumple una regla de negocio (la aserción compara un valor de negocio).
- prueba_fragil: la prueba misma es inestable (locator, espera/timing, orden de datos), el producto puede estar bien.
- entorno: infraestructura (red, conexión rechazada, timeout del runner, servicio caído, disco).
Una falla de rendimiento bajo carga que coincide con un defecto documentado es defecto_real.
defecto_conocido: SOLO uno de {defectos} si la falla corresponde claramente a ese defecto; si no, null. No inventes IDs.
Responde al final SOLO con un objeto JSON, sin texto extra:
{{"categoria": "...", "defecto_conocido": "DEF-xx" o null, "causa_probable": "...", "siguiente_paso": "...", "confianza": 0.0-1.0}}
Escribe causa_probable y siguiente_paso en español, máximo 2 frases cada uno."""


# ---------------------------------------------------------------------------------------
# 4. Bucle del agente (GitHub Models, API compatible con OpenAI)
# ---------------------------------------------------------------------------------------
def _llamar_modelo(mensajes, token):
    cuerpo = json.dumps({"model": MODELO, "messages": mensajes, "tools": ESQUEMA_HERRAMIENTAS,
                         "temperature": 0}).encode()
    for intento in range(2):
        req = urllib.request.Request(ENDPOINT, data=cuerpo, method="POST", headers={
            "Authorization": f"Bearer {token}", "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)["choices"][0]["message"]
        except urllib.error.HTTPError as error:
            espera = int(error.headers.get("Retry-After") or 0)
            if error.code == 429 and intento == 0 and espera <= 30:
                time.sleep(espera or 10)
                continue
            raise IANoDisponible(f"HTTP {error.code} del modelo") from error
        except (urllib.error.URLError, TimeoutError, KeyError, ValueError) as error:
            raise IANoDisponible(f"sin respuesta del modelo ({type(error).__name__})") from error
    raise IANoDisponible("límite de uso del modelo")


def validar_respuesta(texto, falla, validos):
    """Convierte la respuesta del modelo en un resultado seguro (o lanza IANoDisponible)."""
    encontrado = re.search(r"\{.*\}", texto or "", re.S)
    if not encontrado:
        raise IANoDisponible("el modelo no devolvió JSON")
    try:
        datos = json.loads(encontrado.group(0))
    except json.JSONDecodeError as error:
        raise IANoDisponible("JSON inválido del modelo") from error
    categoria = datos.get("categoria")
    if categoria not in CATEGORIAS:
        raise IANoDisponible(f"categoría inválida: {categoria!r}")
    defecto = datos.get("defecto_conocido")
    if defecto not in validos:
        defecto = None  # nunca se acepta un DEF que no existe (anti-alucinación)
    try:
        confianza = min(1.0, max(0.0, float(datos.get("confianza", 0))))
    except (TypeError, ValueError):
        confianza = 0.0
    return _resultado(falla, categoria, defecto, str(datos.get("causa_probable", ""))[:400],
                      str(datos.get("siguiente_paso", ""))[:400], confianza, fuente=MODELO)


def triar_con_agente(falla, token, validos):
    mensajes = [{"role": "system", "content": SISTEMA.format(defectos=", ".join(validos))},
                {"role": "user", "content": f"Prueba: {falla['prueba']} ({falla['origen']})\nTraza:\n{falla['mensaje']}"}]
    usadas = []
    for _ in range(MAX_PASOS):
        respuesta = _llamar_modelo(mensajes, token)
        llamadas = respuesta.get("tool_calls") or []
        if not llamadas:
            resultado = validar_respuesta(respuesta.get("content"), falla, validos)
            resultado["herramientas"] = usadas
            return resultado
        mensajes.append({"role": "assistant", "content": respuesta.get("content"), "tool_calls": llamadas})
        for llamada in llamadas:
            nombre = llamada["function"]["name"]
            try:
                args = json.loads(llamada["function"].get("arguments") or "{}")
                salida = HERRAMIENTAS[nombre](**args)
            except Exception as error:  # una herramienta mal pedida no corta el bucle
                salida = f"Error al ejecutar {nombre}: {error}"
            usadas.append(nombre)
            mensajes.append({"role": "tool", "tool_call_id": llamada["id"], "content": salida})
    raise IANoDisponible("el agente no terminó en el máximo de pasos")


def triar(fallas, offline=False, token=None):
    """Devuelve (resultados, aviso). Si la IA no está disponible, usa reglas y lo avisa."""
    if offline:
        return [clasificar_offline(f) for f in fallas], None
    if not token:
        return [clasificar_offline(f) for f in fallas], "no hay GITHUB_TOKEN"
    validos = defectos_conocidos()
    resultados, aviso = [], None
    for f in fallas:
        if aviso is None:
            try:
                resultados.append(triar_con_agente(f, token, validos))
                continue
            except IANoDisponible as error:
                aviso = str(error)  # deja de llamar al modelo; el resto va por reglas
        resultados.append(clasificar_offline(f))
    return resultados, aviso


# ---------------------------------------------------------------------------------------
# 5. Salida
# ---------------------------------------------------------------------------------------
def _md(texto):
    return str(texto if texto is not None else "—").replace("|", "\\|").replace("\n", " ")


def generar_md(resultados, aviso):
    out = ["## 🤖 Triaje de fallas (IA)", ""]
    if aviso:
        out += [f"> ⚠️ **Triaje IA no disponible** ({_md(aviso)}). Se muestra la clasificación por reglas.", ""]
    if not resultados:
        return "\n".join(out + ["No hay fallas nuevas que triar. ✅", ""])
    out += ["Sugerencias automáticas para orientar la revisión: **las confirma una persona** antes de "
            "reportar o cerrar un defecto.", "",
            "| Prueba | Categoría | DEF | Causa probable | Siguiente paso | Confianza | Fuente |",
            "|---|---|---|---|---|---:|---|"]
    for r in resultados:
        out.append(f"| {_md(r['prueba'])} | {r['categoria']} | {_md(r['defecto_conocido'])} | "
                   f"{_md(r['causa_probable'])} | {_md(r['siguiente_paso'])} | {r['confianza']:.2f} | {r['fuente']} |")
    return "\n".join(out + [""])


def ruta_segura(ruta, permitidas):
    """Solo se escribe en carpetas conocidas del repo (evita que un argumento escriba fuera)."""
    ruta = os.path.normpath(ruta).replace("\\", "/")
    carpeta, nombre = os.path.split(ruta)
    if carpeta not in permitidas or not nombre or nombre.startswith("."):
        raise SystemExit(f"La salida debe estar en una de estas carpetas: {', '.join(permitidas)}")
    return Path(carpeta) / os.path.basename(nombre)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="Triaje de fallas de pruebas con un agente LLM (GitHub Models).")
    p.add_argument("reportes", nargs="+", help="JUnit XML de pytest y/o output.xml de Robot")
    p.add_argument("--offline", action="store_true", help="solo clasificador por reglas, sin red")
    p.add_argument("--json", help="ruta donde guardar el resultado en JSON")
    args = p.parse_args()
    try:
        fallas = [f for ruta in args.reportes for f in extraer_fallas(ruta)]
        resultados, aviso = triar(fallas, args.offline, os.environ.get("GITHUB_TOKEN"))
        agregar_a_summary(generar_md(resultados, aviso))
        if args.json:
            destino = ruta_segura(args.json, ("reportes/triaje", "docs/ia"))
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_text(json.dumps({"modelo": MODELO, "aviso": aviso, "resultados": resultados},
                                                  ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as error:  # el triaje nunca bloquea el pipeline
        agregar_a_summary(f"## 🤖 Triaje de fallas (IA)\n\nTriaje no disponible: {error}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
