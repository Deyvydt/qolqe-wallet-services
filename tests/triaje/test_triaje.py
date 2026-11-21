"""Pruebas unitarias del agente de triaje (.github/scripts/triaje_ia.py). Sin red: el modelo se simula."""
import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / ".github" / "scripts"))
import triaje_ia as t  # noqa: E402

JUNIT = """<testsuites><testsuite name="pytest">
  <testcase classname="tests.api.test_x" name="test_pasa"/>
  <testcase classname="tests.api.test_x" name="test_falla[caso]"><failure message="AssertionError: Esperado 422">token=ghp_abc123 traza</failure></testcase>
  <testcase classname="tests.api.test_x" name="test_esperado"><skipped type="pytest.xfail" message="DEF-01"/></testcase>
  <testcase classname="tests.api.test_x" name="test_error"><error message="httpx.ConnectError: Connection refused"/></testcase>
</testsuite></testsuites>"""

ROBOT = """<robot><suite><test name="CP-WEB-01 Pagar"><tag>HU-G2-02</tag><status status="FAIL">locator not found</status></test>
<test name="CP-WEB-02 Conocido"><tag>DEF-02</tag><status status="FAIL">mora 0.43</status></test>
<test name="CP-WEB-03 Ok"><status status="PASS"/></test></suite></robot>"""


def _archivo(tmp_path, nombre, texto):
    ruta = tmp_path / nombre
    ruta.write_text(texto, encoding="utf-8")
    return ruta


def test_extrae_solo_fallas_nuevas_de_junit_y_oculta_secretos(tmp_path):
    fallas = t.extraer_fallas(_archivo(tmp_path, "junit.xml", JUNIT))
    assert [f["prueba"] for f in fallas] == ["tests.api.test_x::falla [caso]", "tests.api.test_x::error"]
    assert "ghp_" not in fallas[0]["mensaje"] and "Esperado 422" in fallas[0]["mensaje"]


def test_extrae_fallas_de_robot_sin_las_de_defecto_conocido(tmp_path):
    fallas = t.extraer_fallas(_archivo(tmp_path, "output.xml", ROBOT))
    assert [f["prueba"] for f in fallas] == ["CP-WEB-01 Pagar"]


def test_reporte_inexistente_o_roto_no_rompe(tmp_path):
    assert t.extraer_fallas(tmp_path / "no.xml") == []
    assert t.extraer_fallas(_archivo(tmp_path, "roto.xml", "<a>")) == []


@pytest.mark.parametrize("mensaje, categoria, defecto", [
    ("Esperado estado PENDIENTE, obtenido EN_COBRANZA", "defecto_real", "DEF-03"),
    ("httpx.ConnectError: Connection refused", "entorno", None),
    ("strict mode violation: locator resolved to 2 elements", "prueba_fragil", None),
    ("Esperado saldo 414.50, obtenido 329.00", "defecto_real", None),
])
def test_clasificador_por_reglas(mensaje, categoria, defecto):
    r = t.clasificar_offline({"prueba": "p", "mensaje": mensaje})
    assert (r["categoria"], r["defecto_conocido"]) == (categoria, defecto)


def test_defectos_conocidos_salen_de_defectos_md():
    assert t.defectos_conocidos() == ["DEF-01", "DEF-02", "DEF-03", "DEF-04", "DEF-05", "DEF-06"]


def test_validacion_rechaza_def_inventado_y_categoria_invalida():
    falla = {"prueba": "p"}
    r = t.validar_respuesta('{"categoria":"entorno","defecto_conocido":"DEF-99","confianza":7}', falla, ["DEF-01"])
    assert r["defecto_conocido"] is None and r["confianza"] == 1.0
    with pytest.raises(t.IANoDisponible):
        t.validar_respuesta('{"categoria":"no_se"}', falla, ["DEF-01"])
    with pytest.raises(t.IANoDisponible):
        t.validar_respuesta("OK", falla, ["DEF-01"])


def test_herramienta_de_codigo_no_sale_del_repo():
    assert t.leer_fragmento_codigo("../../etc/passwd").startswith("Error")
    assert t.leer_fragmento_codigo(".git/config").startswith("Error")
    assert "def dias_de_atraso" in t.leer_fragmento_codigo("qolqe/reglas/servicios.py", 1, 40)


def test_bucle_del_agente_usa_herramientas_y_devuelve_json(monkeypatch):
    respuestas = iter([
        {"content": None, "tool_calls": [{"id": "1", "function": {"name": "leer_defectos", "arguments": "{}"}}]},
        {"content": json.dumps({"categoria": "defecto_real", "defecto_conocido": "DEF-02",
                                "causa_probable": "+1 día", "siguiente_paso": "ver DEF-02", "confianza": 0.9})},
    ])
    vistos = []
    monkeypatch.setattr(t, "_llamar_modelo", lambda mensajes, token: vistos.append(mensajes[-1]) or next(respuestas))
    r = t.triar_con_agente({"prueba": "p", "origen": "pytest", "mensaje": "dias"}, "tk", ["DEF-02"])
    assert (r["categoria"], r["defecto_conocido"], r["herramientas"]) == ("defecto_real", "DEF-02", ["leer_defectos"])
    assert vistos[-1]["role"] == "tool" and "DEF-02" in vistos[-1]["content"]


def test_sin_token_o_con_error_degrada_a_reglas(monkeypatch):
    fallas = [{"prueba": "p", "origen": "pytest", "mensaje": "Connection refused"}]
    resultados, aviso = t.triar(fallas, token=None)
    assert aviso and resultados[0]["fuente"] == "reglas"

    def caido(*_):
        raise t.IANoDisponible("HTTP 429 del modelo")
    monkeypatch.setattr(t, "_llamar_modelo", caido)
    resultados, aviso = t.triar(fallas, token="tk")
    assert aviso == "HTTP 429 del modelo" and resultados[0]["categoria"] == "entorno"
    assert "Triaje IA no disponible" in t.generar_md(resultados, aviso)
