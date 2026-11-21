"""QUÉ ES: configuración común que pytest carga ANTES de cualquier prueba.

PARA QUÉ:
  1. Hace que las pruebas usen su propia base de datos (datos/pruebas.db), así no borran
     ni modifican los datos de la app que usas en la demo (datos/qolqe.db). También activa
     el modo prueba, que habilita la API de soporte (/api/pruebas/*).
  2. Al terminar cada ejecución imprime en la terminal el RESUMEN AUTOMÁTICO:
     - Reporte total: endpoint (E1..E10 de G2, N1..N9 del núcleo común) × tipo (funcional / técnico, por las etiquetas
       @funcional y @tecnico de cada escenario) × resultado, con totales.
     - Por HU (funcional / técnico) y por técnica, y cada fallo con su defecto.
     - Técnico (Schemathesis): casos generados por endpoint y validación de entrada.
     Los números salen de ESA ejecución: si el código cambia, el resumen cambia.
"""
import os
from collections import defaultdict

import pytest

os.environ.setdefault("QOLQE_BD", "datos/pruebas.db")
os.environ.setdefault("QOLQE_MODO_PRUEBA", "1")

# FALLOS ESPERADOS: pruebas que fallan A PROPÓSITO porque detectan un defecto ya reportado en
# docs/defectos.md. Se marcan como "xfail" (fallo esperado) con el ID del defecto:
#   - el pipeline queda en VERDE, pero el defecto sigue VISIBLE en el reporte (sale como xfailed);
#   - strict=True: si alguien arregla el defecto y la prueba empieza a pasar, pytest lo marca como
#     FALLO (XPASS) para avisar que hay que actualizar esta lista y cerrar el defecto.
# Formato: fragmento del nombre de la prueba → defecto. Un fallo que no esté aquí es "NUEVO":
# rompe el pipeline y hay que analizarlo (posible regresión o defecto nuevo).
DEFECTOS_CONOCIDOS = [
    ("[13 digitos (invalido)-", "DEF-01"),
    ("conteo_de_días_de_atraso_alrededor_del_vencimiento[el mismo dia-", "DEF-02"),
    ("conteo_de_días_de_atraso_alrededor_del_vencimiento[un dia despues-", "DEF-02"),
    ("[el mismo dia del vencimiento-", "DEF-02"),
    ("[un dia de atraso-", "DEF-02"),
    ("[19 dias, bajo el tope-", "DEF-02"),
    ("[60-PENDIENTE]", "DEF-03"),
    ("[60 dias, aun se puede pagar-", "DEF-03"),
    ("ya_vencidas_antes_de_activar", "DEF-04"),
    # Núcleo común (features/api/nucleo_comun.feature)
    ("después_de_cerrar_sesión_el_token_ya_no_es_válido", "DEF-07"),
    ("[secuencia descendente-", "DEF-08"),
    ("un_login_exitoso_reinicia_el_conteo", "DEF-09"),
    ("no_se_puede_transferir_a_una_cuenta_cerrada", "DEF-10"),
    ("[redondeo comercial 0.005-", "DEF-11"),
    ("el_saldo_debe_cubrir_el_monto_más_la_comisión", "DEF-12"),
    ("las_transferencias_interbancarias_cuentan_para_el_límite", "DEF-13"),
    ("transferencias_simultáneas_no_superan_el_límite", "DEF-14"),
]
TECNICAS = ["camino-feliz", "particion", "valor-limite", "efecto", "concurrencia", "seguridad", "contrato", "schemathesis"]
# Endpoints del módulo G2 (docs/requisitos.md, Anexo A) + el proceso diario. Etiqueta @E<n> en cada escenario.
ENDPOINTS = {
    "E1": "GET /api/servicios/empresas",
    "E2": "GET /api/servicios/deudas",
    "E3": "POST /api/servicios/pagos",
    "E4": "GET /api/servicios/pagos",
    "E5": "GET /api/servicios/pagos/{codigo}",
    "E6": "GET /api/servicios/afiliaciones",
    "E7": "POST /api/servicios/afiliaciones",
    "E8": "PUT /api/servicios/afiliaciones/{id}",
    "E9": "DELETE /api/servicios/afiliaciones/{id}",
    "E10": "POST /api/pruebas/procesar-diario",
    # Núcleo común (HU-N-01..09): etiqueta @N<n>
    "N1": "POST /api/usuarios",
    "N2": "POST /api/auth/login",
    "N3": "POST /api/auth/logout",
    "N4": "GET /api/cuentas/me",
    "N5": "PUT /api/cuentas/me",
    "N6": "GET /api/cuentas/me/saldo",
    "N7": "POST /api/cuentas/me/cierre",
    "N8": "POST /api/transferencias",
    "N9": "GET /api/transferencias/comision",
}

_etiquetas: dict[str, set[str]] = {}
_resultados: dict[str, dict] = {}


def pytest_collection_modifyitems(items):
    for item in items:
        etiquetas = {m.name for m in item.iter_markers()} - {"parametrize", "usefixtures", "xfail"}
        _etiquetas[item.nodeid] = etiquetas
        # Etiquetas del .feature (@HU-G2-02, @CA1, @valor-limite...) dentro del JUnit XML:
        # así el pipeline puede armar la matriz de trazabilidad HU → caso → resultado.
        item.user_properties.append(("etiquetas", ",".join(sorted(etiquetas))))
        defecto = _defecto(item.nodeid)
        if not defecto.startswith("NUEVO"):
            item.add_marker(pytest.mark.xfail(reason=f"{defecto} (ver docs/defectos.md)", strict=True))
            item.user_properties.append(("defecto", defecto))


def pytest_runtest_logreport(report):
    if report.when == "call" or (report.when == "setup" and report.outcome != "passed"):
        mensaje = ""
        if hasattr(report, "wasxfail"):
            # Fallo esperado: falló como se esperaba (xfailed) o pasó sin esperarlo (XPASS strict).
            _resultados[report.nodeid] = {"estado": "xfailed" if report.skipped else "failed",
                                          "mensaje": report.wasxfail or "XPASS: el defecto parece corregido"}
            return
        if report.failed and hasattr(report.longrepr, "reprcrash"):
            mensaje = report.longrepr.reprcrash.message.splitlines()[0]
        _resultados[report.nodeid] = {"estado": report.outcome, "mensaje": mensaje}


def _defecto(nodeid: str) -> str:
    return next((d for fragmento, d in DEFECTOS_CONOCIDOS if fragmento in nodeid), "NUEVO, analizar")


def _nombre(nodeid: str) -> str:
    return nodeid.split("::")[-1].removeprefix("test_").replace("_", " ")


def tipo_de_caso(etiquetas: set[str]) -> str:
    """Funcional o técnico, según la etiqueta @funcional / @tecnico del escenario."""
    return "tecnico" if "tecnico" in etiquetas else ("funcional" if "funcional" in etiquetas else "sin tipo")


def endpoint_de_caso(etiquetas: set[str]) -> str:
    return next((e for e in sorted(etiquetas, key=lambda x: (len(x), x)) if e in ENDPOINTS), "Otros (humo, métodos no declarados)")


def _resumen_por_endpoint(tr):
    """Reporte total: endpoint × (funcional / técnico) × resultado (pasa / esperado / falla)."""
    if not _resultados:
        return
    tr.write_sep("=", "REPORTE TOTAL DE ESCENARIOS · endpoint × tipo × resultado")
    tabla = defaultdict(lambda: {"funcional": [0, 0, 0], "tecnico": [0, 0, 0], "sin tipo": [0, 0, 0]})
    for nodeid, r in _resultados.items():
        etiquetas = _etiquetas.get(nodeid, set())
        indice = {"passed": 0, "xfailed": 1}.get(r["estado"], 2)
        tabla[endpoint_de_caso(etiquetas)][tipo_de_caso(etiquetas)][indice] += 1
    tr.write_line(f"  {'Endpoint':<50}{'Funcional':>11}{'Técnico':>11}{'Total':>7}{'Pasan':>7}{'Esperado':>10}{'Fallan':>8}")
    totales = {"funcional": [0, 0, 0], "tecnico": [0, 0, 0], "sin tipo": [0, 0, 0]}
    orden = [*ENDPOINTS, *sorted(set(tabla) - set(ENDPOINTS))]
    for endpoint in (e for e in orden if e in tabla):
        fila = tabla[endpoint]
        for tipo in totales:
            totales[tipo] = [a + b for a, b in zip(totales[tipo], fila[tipo])]
        _fila_endpoint(tr, f"{endpoint} {ENDPOINTS.get(endpoint, '')}".strip(), fila)
    _fila_endpoint(tr, "TOTAL", totales)
    tr.write_line("  (Funcional/Técnico = casos de cada tipo; Esperado = fallo esperado por un defecto ya reportado)")
    tr.write_line("")


def _fila_endpoint(tr, nombre, fila):
    ok, xf, ko = (fila["funcional"][i] + fila["tecnico"][i] + fila["sin tipo"][i] for i in range(3))
    tr.write_line(f"  {nombre[:49]:<50}{sum(fila['funcional']):>11}{sum(fila['tecnico']):>11}"
                  f"{ok + xf + ko:>7}{ok:>7}{xf:>10}{ko:>8}")


def _resumen_funcional(tr):
    casos = _resultados
    if not casos:
        return
    tr.write_sep("=", "RESUMEN POR HISTORIA DE USUARIO · pytest-bdd (features/api) + Schemathesis")
    por_hu = defaultdict(lambda: [0, 0, 0])
    por_tipo_hu = defaultdict(lambda: defaultdict(int))
    por_tecnica = defaultdict(lambda: [0, 0, 0])
    for nodeid, r in casos.items():
        etiquetas = _etiquetas.get(nodeid, set())
        hu = sorted(e for e in etiquetas if e.startswith("HU-")) or ["(sin HU)"]
        indice = {"passed": 0, "xfailed": 1}.get(r["estado"], 2)
        por_hu[hu[0]][indice] += 1
        por_tipo_hu[hu[0]][tipo_de_caso(etiquetas)] += 1
        for tecnica in TECNICAS:
            if tecnica in etiquetas:
                por_tecnica[tecnica][indice] += 1
    tr.write_line(f"  {'Historia de usuario':<22}{'Funcional':>11}{'Técnico':>9}{'Casos':>7}{'Pasan':>7}{'Esperado':>10}{'Fallan':>8}")
    for hu in sorted(por_hu):
        ok, xf, ko = por_hu[hu]
        tr.write_line(f"  {hu:<22}{por_tipo_hu[hu]['funcional']:>11}{por_tipo_hu[hu]['tecnico']:>9}"
                      f"{ok + xf + ko:>7}{ok:>7}{xf:>10}{ko:>8}")
    ok, xf, ko = (sum(v[i] for v in por_hu.values()) for i in range(3))
    funcionales = sum(d["funcional"] for d in por_tipo_hu.values())
    tecnicos = sum(d["tecnico"] for d in por_tipo_hu.values())
    tr.write_line(f"  {'TOTAL':<22}{funcionales:>11}{tecnicos:>9}{ok + xf + ko:>7}{ok:>7}{xf:>10}{ko:>8}")
    tr.write_line("  (Esperado = fallo esperado: la prueba detecta un defecto ya reportado)")
    tr.write_line("")
    tr.write_line("  Por técnica: " + " · ".join(
        f"{t} {v[0]}/{sum(v)}" for t, v in ((t, por_tecnica[t]) for t in TECNICAS) if sum(v)))
    fallos = [(n, r) for n, r in casos.items() if r["estado"] != "passed"]
    if fallos:
        tr.write_line("")
        tr.write_line("  Fallos esperados (cada uno evidencia un defecto) y fallos nuevos:")
        for nodeid, r in sorted(fallos, key=lambda x: _defecto(x[0])):
            marca = _defecto(nodeid) if r["estado"] == "xfailed" else "NUEVO, analizar"
            tr.write_line(f"   [{marca}] {_nombre(nodeid)[:95]}")
            if r["mensaje"]:
                tr.write_line(f"            {r['mensaje'][:110]}")
        nuevos = sum(1 for _, r in fallos if r["estado"] != "xfailed")
        defectos = sorted({_defecto(n) for n, _ in fallos} - {"NUEVO, analizar"})
        tr.write_line("")
        tr.write_line(f"  {len(fallos) - nuevos} fallos esperados → defectos conocidos: {', '.join(defectos) or 'ninguno'}"
                      + (f" · {nuevos} fallo(s) NUEVO(S) por analizar" if nuevos else " · sin fallos nuevos"))
    tr.write_line("  Reporte HTML: pytest --html=reportes/pytest/reporte.html --self-contained-html")


def _resumen_tecnico(tr, config):
    datos = getattr(config, "resumen_tecnico", None)
    if datos is None:
        return
    from clasificacion_contrato import nombre_endpoint, texto_correcto
    casos = datos["casos"]
    tr.write_sep("=", f"RESUMEN TÉCNICO · Schemathesis · {datos['operacion']}")
    tr.write_line(f"  {len(casos)} casos generados desde el contrato OpenAPI · errores 500: "
                  f"{sum(1 for c in casos if c['estado'] >= 500)} · modo {datos['semilla']}")
    actual = None
    for f in datos["filas"]:
        if f["endpoint"] != actual:
            actual = f["endpoint"]
            tr.write_line("")
            tr.write_line(f"  {nombre_endpoint(actual)}")
        filas = ", ".join(f"#{n}" for n in f["filas"][:8]) + (" …" if len(f["filas"]) > 8 else "")
        tr.write_line(f"    {f['validacion']:<40}{f['casos']:>6}  {texto_correcto(f):<14}{filas}")
    if datos["observaciones"]:
        tr.write_line("")
        tr.write_line("  Observaciones de Schemathesis (no rompen una HU): " + " · ".join(datos["observaciones"]))
    tr.write_line(f"  Reporte HTML: {datos['reporte']}")


def pytest_terminal_summary(terminalreporter, config):
    _resumen_por_endpoint(terminalreporter)
    _resumen_funcional(terminalreporter)
    _resumen_tecnico(terminalreporter, config)
