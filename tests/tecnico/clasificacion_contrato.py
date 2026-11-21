"""QUÉ ES: lógica de apoyo para las pruebas técnicas de Schemathesis (no es una prueba).

PARA QUÉ: Schemathesis guarda cada solicitud que generó en un archivo HAR. Este módulo
  1. identifica a qué ENDPOINT del módulo G2 (E1..E9) pertenece cada caso;
  2. lo clasifica según la VALIDACIÓN DE ENTRADA que ejercita (obligatoriedad, tipo, rango,
     formato, cabeceras, método), deducida del contrato OpenAPI de /api/servicios/*;
  3. decide si la API respondió lo correcto para esa validación (estado HTTP o `codigo` de error);
  4. genera el reporte HTML reportes/schemathesis/ultimo/reporte.html.
Lo usa tests/tecnico/test_contrato_schemathesis.py en cada ejecución de pytest.
"""
import html
import json
import re
from collections import OrderedDict
from urllib.parse import urlparse

INVALIDA = "SOLICITUD_INVALIDA"
SUMINISTRO_VALIDO = re.compile(r"\d{8,12}")  # R-G2-01

# Endpoint → (método, ruta, ¿exige token?, estado de éxito, códigos de negocio válidos para una solicitud válida)
ENDPOINTS = OrderedDict([
    ("E1", ("GET", "/api/servicios/empresas", False, 200, set())),
    ("E2", ("GET", "/api/servicios/deudas", True, 200, {"EMPRESA_NO_ENCONTRADA", "SIN_DEUDA_PENDIENTE"})),
    ("E3", ("POST", "/api/servicios/pagos", True, 201,
            {"DEUDA_NO_ENCONTRADA", "DEUDA_YA_PAGADA", "DEUDA_EN_COBRANZA", "SALDO_INSUFICIENTE"})),
    ("E4", ("GET", "/api/servicios/pagos", True, 200, {"AFILIACION_NO_ENCONTRADA"})),
    ("E5", ("GET", "/api/servicios/pagos/{codigo_operacion}", True, 200, {"PAGO_NO_ENCONTRADO"})),
    ("E6", ("GET", "/api/servicios/afiliaciones", True, 200, set())),
    ("E7", ("POST", "/api/servicios/afiliaciones", True, 201,
            {"EMPRESA_NO_ENCONTRADA", "SUMINISTRO_NO_ENCONTRADO", "AFILIACION_INVALIDA", "LIMITE_AFILIACIONES",
             "AFILIACION_DUPLICADA"})),
    ("E8", ("PUT", "/api/servicios/afiliaciones/{afiliacion_id}", True, 200,
            {"AFILIACION_NO_ENCONTRADA", "AFILIACION_INVALIDA"})),
    ("E9", ("DELETE", "/api/servicios/afiliaciones/{afiliacion_id}", True, 204,
            {"AFILIACION_NO_ENCONTRADA", "DEBITO_ACTIVO"})),
])

# Validación → (qué se envía y qué se espera, respuestas correctas: estado HTTP (int) o `codigo` de error (str))
VALIDACIONES = OrderedDict([
    ("Válido según el contrato", ("Solicitud que cumple el contrato: decide la regla de negocio", None)),
    ("Obligatoriedad: falta un campo", ("Cuerpo sin un campo obligatorio (required)", {INVALIDA})),
    ("Obligatoriedad: falta un parámetro", ("Query sin un parámetro obligatorio (empresa / suministro)", {INVALIDA})),
    ("Obligatoriedad: sin cuerpo", ("Cuerpo vacío aunque el requestBody es obligatorio", {INVALIDA})),
    ("Tipo: campo con tipo incorrecto", ("Campo con texto, decimal, booleano, null… del tipo equivocado", {INVALIDA})),
    ("Tipo: el cuerpo no es un objeto", ("Cuerpo lista, número, texto o booleano (type: object)", {INVALIDA})),
    ("Tipo: id no es entero", ("Parámetro de ruta o query que no es entero (type: integer)", {INVALIDA})),
    ("Rango: id cero o negativo", ("Entero ≤ 0: no existe ese recurso", {INVALIDA, "DEUDA_NO_ENCONTRADA",
                                                                       "AFILIACION_NO_ENCONTRADA"})),
    ("Rango: entero enorme (> 64 bits)", ("Entero gigante; el contrato no declara máximo (OBS-01): se rechaza", {INVALIDA})),
    ("Formato: suministro o alias (R-G2-01)", ("Suministro fuera de 8–12 dígitos o alias fuera de 3–20 caracteres",
                                               {"SUMINISTRO_INVALIDO", "AFILIACION_INVALIDA", "EMPRESA_NO_ENCONTRADA",
                                                "AFILIACION_NO_ENCONTRADA"})),
    ("Cabecera: sin token", ("Sin Authorization (security: HTTPBearer)", {"NO_AUTENTICADO"})),
    ("Cabecera: token inválido", ("Authorization alterada", {"NO_AUTENTICADO"})),
    ("Cabecera: sin Content-Type", ("Sin Content-Type: application/json", {INVALIDA})),
    ("Método HTTP no permitido", ("PUT, PATCH, OPTIONS… en una ruta que no los declara", {405})),
])

# Validaciones que aplican a cada endpoint (las demás no tienen sentido en él)
_CABECERAS = ["Cabecera: sin token", "Cabecera: token inválido"]
_CUERPO = ["Obligatoriedad: sin cuerpo", "Tipo: el cuerpo no es un objeto", "Tipo: campo con tipo incorrecto",
           "Cabecera: sin Content-Type"]
APLICAN = {
    "E1": ["Válido según el contrato"],
    "E2": ["Válido según el contrato", "Obligatoriedad: falta un parámetro", "Formato: suministro o alias (R-G2-01)",
           *_CABECERAS],
    "E3": ["Válido según el contrato", "Obligatoriedad: falta un campo", *_CUERPO, "Rango: id cero o negativo",
           "Rango: entero enorme (> 64 bits)", *_CABECERAS],
    "E4": ["Válido según el contrato", "Tipo: id no es entero", "Rango: id cero o negativo",
           "Rango: entero enorme (> 64 bits)", *_CABECERAS],
    "E5": ["Válido según el contrato", *_CABECERAS],
    "E6": ["Válido según el contrato", *_CABECERAS],
    "E7": ["Válido según el contrato", "Obligatoriedad: falta un campo", *_CUERPO,
           "Formato: suministro o alias (R-G2-01)", *_CABECERAS],
    "E8": ["Válido según el contrato", *_CUERPO, "Tipo: id no es entero", "Rango: id cero o negativo",
           "Rango: entero enorme (> 64 bits)", "Formato: suministro o alias (R-G2-01)", *_CABECERAS],
    "E9": ["Válido según el contrato", "Tipo: id no es entero", "Rango: id cero o negativo",
           "Rango: entero enorme (> 64 bits)", *_CABECERAS],
    "405": ["Método HTTP no permitido"],
}

# Valores que pydantic (modo flexible) acepta como booleano
_BOOLEANOS = {"0", "off", "f", "false", "n", "no", "1", "on", "t", "true", "y", "yes"}


def _plantilla(ruta: str) -> tuple[str, str] | None:
    """Ruta concreta → (ruta del contrato, valor del parámetro de ruta)."""
    for _, (_, plantilla, *_) in ENDPOINTS.items():
        patron = "^" + re.sub(r"\{[^}]+\}", "([^/]+)", plantilla) + "$"
        encontrado = re.match(patron, ruta)
        if encontrado:
            return plantilla, (encontrado.group(1) if encontrado.groups() else "")
    return None


def _endpoint(metodo: str, plantilla: str) -> str | None:
    return next((e for e, (m, p, *_) in ENDPOINTS.items() if (m, p) == (metodo, plantilla)), None)


def _entero(texto: str) -> int | None:
    return int(texto) if re.fullmatch(r"\s*[+-]?\d+\s*", texto) else None


def _clasificar_entero(valor: int) -> str | None:
    if abs(valor) >= 2**63:
        return "Rango: entero enorme (> 64 bits)"
    if valor <= 0:
        return "Rango: id cero o negativo"
    return None


def _clasificar_cuerpo(endpoint: str, cabeceras: dict, cuerpo: str) -> str | None:
    if "content-type" not in cabeceras:
        return "Cabecera: sin Content-Type"
    if cuerpo == "":
        return "Obligatoriedad: sin cuerpo"
    try:
        datos = json.loads(cuerpo)
    except ValueError:
        return "Tipo: el cuerpo no es un objeto"
    if not isinstance(datos, dict):
        return "Tipo: el cuerpo no es un objeto"
    if endpoint == "E3":
        if "deuda_id" not in datos:
            return "Obligatoriedad: falta un campo"
        valor = datos["deuda_id"]
        if isinstance(valor, float) and valor.is_integer():
            valor = int(valor)  # en JSON Schema, 1.0 también es un "integer" válido
        if not isinstance(valor, int) or isinstance(valor, bool):
            return "Tipo: campo con tipo incorrecto"
        return _clasificar_entero(valor)
    if endpoint == "E7":
        if any(c not in datos for c in ("empresa", "suministro", "alias")):
            return "Obligatoriedad: falta un campo"
        if any(not isinstance(datos[c], str) for c in ("empresa", "suministro", "alias")):
            return "Tipo: campo con tipo incorrecto"
        if not SUMINISTRO_VALIDO.fullmatch(datos["suministro"]) or not 3 <= len(datos["alias"].strip()) <= 20:
            return "Formato: suministro o alias (R-G2-01)"
        return None
    # E8: todos los campos son opcionales
    alias, debito = datos.get("alias"), datos.get("debito_automatico")
    if alias is not None and not isinstance(alias, str):
        return "Tipo: campo con tipo incorrecto"
    if debito is not None and not (isinstance(debito, bool) or debito in (0, 1)
                                   or (isinstance(debito, str) and debito.lower() in _BOOLEANOS)):
        return "Tipo: campo con tipo incorrecto"
    if alias is not None and not 3 <= len(alias.strip()) <= 20:
        return "Formato: suministro o alias (R-G2-01)"
    return None


def clasificar(entrada: dict) -> tuple[str, str]:
    """Devuelve (endpoint, validación de entrada) de un caso del HAR. Endpoint '405' = método no declarado."""
    solicitud = entrada["request"]
    estado = entrada["response"]["status"]
    cabeceras = {c["name"].lower(): c["value"] for c in solicitud["headers"]}
    query = {q["name"]: q["value"] for q in solicitud.get("queryString", [])}
    cuerpo = solicitud.get("postData", {}).get("text", "")
    encontrado = _plantilla(urlparse(solicitud["url"]).path)
    endpoint = _endpoint(solicitud["method"], encontrado[0]) if encontrado else None
    if endpoint is None:
        return "405", "Método HTTP no permitido"
    parametro = encontrado[1]
    if ENDPOINTS[endpoint][2]:
        if "authorization" not in cabeceras:
            return endpoint, "Cabecera: sin token"
        if estado == 401:
            return endpoint, "Cabecera: token inválido"
    validacion = None
    if endpoint == "E2":
        if "empresa" not in query or "suministro" not in query:
            validacion = "Obligatoriedad: falta un parámetro"
        elif not SUMINISTRO_VALIDO.fullmatch(query["suministro"]):
            validacion = "Formato: suministro o alias (R-G2-01)"
    elif endpoint == "E4" and "afiliacion_id" in query:
        valor = _entero(query["afiliacion_id"])
        validacion = "Tipo: id no es entero" if valor is None else _clasificar_entero(valor)
    elif endpoint in ("E8", "E9"):
        valor = _entero(parametro)
        validacion = "Tipo: id no es entero" if valor is None else _clasificar_entero(valor)
    if validacion is None and endpoint in ("E3", "E7", "E8"):
        validacion = _clasificar_cuerpo(endpoint, cabeceras, cuerpo)
    return endpoint, validacion or "Válido según el contrato"


def esperado(endpoint: str, validacion: str) -> set:
    if validacion == "Válido según el contrato":
        _, _, _, exito, codigos = ENDPOINTS[endpoint]
        return {exito, *codigos}
    return VALIDACIONES[validacion][1]


def _defecto_conocido(entrada: dict, validacion: str) -> str:
    """DEF-01: un suministro de 13 dígitos se acepta (no se rechaza con 422)."""
    solicitud = entrada["request"]
    texto = solicitud.get("postData", {}).get("text", "") + " ".join(q["value"] for q in solicitud.get("queryString", []))
    if validacion.startswith("Formato") and re.search(r"(?<!\d)\d{13}(?!\d)", texto):
        return "DEF-01"
    return ""


def analizar(entradas: list[dict]) -> list[dict]:
    """Un dict por caso: número, endpoint, validación, método, ruta, cuerpo, estado, respuesta y si es correcto."""
    casos = []
    for numero, entrada in enumerate(entradas, 1):
        endpoint, validacion = clasificar(entrada)
        estado = entrada["response"]["status"]
        texto = entrada["response"]["content"].get("text") or ""
        codigo = None
        try:
            json_resp = json.loads(texto) if texto else {}
            codigo = json_resp.get("codigo") if isinstance(json_resp, dict) else None
            respuesta = codigo or ("lista" if isinstance(json_resp, list) else
                                   f"comprobante {json_resp.get('codigo_operacion', '')}".strip())
        except (ValueError, AttributeError):
            respuesta = texto[:60]
        url = urlparse(entrada["request"]["url"])
        aceptado = esperado(endpoint, validacion)
        correcto = estado < 500 and (estado in aceptado or codigo in aceptado)
        casos.append({
            "numero": numero, "endpoint": endpoint, "validacion": validacion, "metodo": entrada["request"]["method"],
            "ruta": url.path + (f"?{url.query}" if url.query else ""),
            "cuerpo": entrada["request"].get("postData", {}).get("text", "") or "—",
            "estado": estado, "respuesta": respuesta, "correcto": correcto,
            "defecto": "" if correcto else _defecto_conocido(entrada, validacion),
        })
    return casos


def nombre_endpoint(endpoint: str) -> str:
    if endpoint == "405":
        return "Rutas /api/servicios/* con método no declarado"
    metodo, ruta, *_ = ENDPOINTS[endpoint]
    return f"{endpoint} {metodo} {ruta}"


def resumen(casos: list[dict]) -> list[dict]:
    """Una fila por (endpoint, validación aplicable): casos, filas y si todos fueron correctos."""
    filas = []
    for endpoint in [*ENDPOINTS, "405"]:
        for nombre in APLICAN[endpoint]:
            del_grupo = [c for c in casos if c["endpoint"] == endpoint and c["validacion"] == nombre]
            defectos = sorted({c["defecto"] for c in del_grupo if c["defecto"]})
            filas.append({"endpoint": endpoint, "validacion": nombre, "descripcion": VALIDACIONES[nombre][0],
                          "casos": len(del_grupo), "filas": [c["numero"] for c in del_grupo], "defectos": defectos,
                          "correcto": all(c["correcto"] or c["defecto"] for c in del_grupo) if del_grupo else None})
    return filas


_CSS = """:root{--bg:#F5F7FA;--sf:#fff;--fg:#17212F;--mu:#566477;--ln:#D8DFE8;--ac:#1F5FBF;--acs:#E3ECFA;--ok:#1F7A55;--wa:#B4520C}
@media (prefers-color-scheme:dark){:root{--bg:#0F1621;--sf:#172231;--fg:#E6ECF4;--mu:#9AA9BC;--ln:#2A394D;--ac:#7FB0F5;--acs:#1C2F4A;--ok:#6FD3A6;--wa:#F2A36B;color-scheme:dark}}
body{background:var(--bg);color:var(--fg);font:16px/1.55 Verdana,sans-serif;margin:0}
.w{max-width:1100px;margin:0 auto;padding:32px 18px 60px;display:flex;flex-direction:column;gap:24px}
h1{font-size:28px;margin:0}h2{font-size:21px;margin:0}p{margin:0}.mu{color:var(--mu)}
.kpis{display:flex;flex-wrap:wrap;gap:12px}.k{flex:1;min-width:150px;background:var(--sf);border:1px solid var(--ln);border-radius:12px;padding:14px 16px}.k b{display:block;font-size:32px}
.tb{overflow-x:auto;background:var(--sf);border:1px solid var(--ln);border-radius:12px}table{border-collapse:collapse;width:100%;font-size:14px}
th,td{padding:8px 12px;border-bottom:1px solid var(--ln);text-align:left;vertical-align:top}th{font-size:12px;text-transform:uppercase;letter-spacing:.06em;color:var(--mu)}
code{font-family:Consolas,monospace;font-size:13px}.ok{color:var(--ok);font-weight:bold}.wa{color:var(--wa);font-weight:bold}
.pill{background:var(--acs);color:var(--ac);border-radius:99px;padding:2px 9px;font-size:12px;white-space:nowrap}"""


def texto_correcto(fila: dict) -> str:
    if fila["correcto"] is None:
        return "No generado"
    if fila["defectos"]:
        return "Defecto " + ", ".join(fila["defectos"])
    return "Sí" if fila["correcto"] else "NO"


def generar_html(casos: list[dict], operacion: str, semilla: str, observaciones: list[str], fecha: str) -> str:
    e = html.escape
    n500 = sum(1 for c in casos if c["estado"] >= 500)
    partes = [f"<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
              f"<title>Schemathesis · G2</title><style>{_CSS}</style><div class=w>",
              f"<div><p class=mu>Pruebas técnicas generadas desde el contrato OpenAPI · ejecución {e(fecha)} · modo {e(semilla)}</p>"
              f"<h1>Schemathesis · {e(operacion)}</h1></div>",
              f"<div class=kpis><div class=k><b>{len(casos)}</b>casos generados</div>"
              f"<div class=k><b>{len({c['endpoint'] for c in casos} - {'405'})}</b>endpoints cubiertos</div>"
              f"<div class=k><b class={'wa' if n500 else 'ok'}>{n500}</b>errores 500</div>"
              f"<div class=k><b>{len(observaciones)}</b>observaciones de Schemathesis</div></div>"]
    if observaciones:
        partes.append("<p>Observaciones: " + " · ".join(e(o) for o in observaciones) + "</p>")
    partes.append("<h2>Validación de entrada por endpoint</h2><div class=tb><table><tr><th>Endpoint</th><th>Validación</th>"
                  "<th>Qué se envió y qué se espera</th><th>Casos</th><th>Filas</th><th>¿Correcto?</th></tr>")
    for fila in resumen(casos):
        texto = texto_correcto(fila)
        clase = "ok" if texto == "Sí" else "wa"
        lista = ", ".join(f"#{n}" for n in fila["filas"][:30]) + (" …" if len(fila["filas"]) > 30 else "") or "—"
        partes.append(f"<tr><td><b>{e(nombre_endpoint(fila['endpoint']))}</b></td><td>{e(fila['validacion'])}</td>"
                      f"<td>{e(fila['descripcion'])}</td><td>{fila['casos']}</td><td>{lista}</td>"
                      f"<td class={clase}>{e(texto)}</td></tr>")
    partes.append("</table></div><h2>Todos los casos</h2><div class=tb><table><tr><th>#</th><th>Endpoint</th>"
                  "<th>Validación</th><th>Método y ruta</th><th>Cuerpo enviado</th><th>Estado</th><th>Respuesta</th></tr>")
    for c in casos:
        partes.append(f"<tr><td>{c['numero']}</td><td>{e(c['endpoint'])}</td><td><span class=pill>{e(c['validacion'])}</span></td>"
                      f"<td><code>{c['metodo']} {e(c['ruta'][:90])}</code></td>"
                      f"<td><code>{e(c['cuerpo'][:110])}</code></td><td class={'ok' if c['correcto'] else 'wa'}>{c['estado']}</td>"
                      f"<td><code>{e(str(c['respuesta']))}{' · ' + e(c['defecto']) if c['defecto'] else ''}</code></td></tr>")
    partes.append("</table></div></div>")
    return "".join(partes)
