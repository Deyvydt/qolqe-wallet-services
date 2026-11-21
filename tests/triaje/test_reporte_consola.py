"""Pruebas del reporte final en consola (.github/scripts/reporte_consola.py). Sin red."""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / ".github" / "scripts"))
import reporte_consola as r  # noqa: E402

JUNIT = """<testsuites><testsuite name="pytest">
  <testcase name="test_pasa"><properties><property name="etiquetas" value="funcional,E1"/></properties></testcase>
  <testcase name="test_esperado"><properties><property name="etiquetas" value="tecnico,E2"/>
    <property name="defecto" value="DEF-01"/></properties><skipped type="pytest.xfail" message="DEF-01"/></testcase>
</testsuite></testsuites>"""
JUNIT_ROJO = JUNIT.replace("</testsuite>", '<testcase name="test_rompe"><failure message="Esperado 200"/></testcase></testsuite>')


def _correr(tmp_path, monkeypatch, capsys, junit, needs=None):
    monkeypatch.setenv("NO_COLOR", "1")
    monkeypatch.setenv("NEEDS", json.dumps(needs) if needs else "")
    ruta = tmp_path / "junit.xml"
    ruta.write_text(junit, encoding="utf-8")
    assert r.main(["--api", str(ruta), "--contrato", str(ruta)]) == 0  # solo informa, nunca bloquea
    return capsys.readouterr().out


def test_verde_muestra_aprobado_defectos_y_endpoints(tmp_path, monkeypatch, capsys):
    salida = _correr(tmp_path, monkeypatch, capsys, JUNIT)
    assert "VEREDICTO:  ✔ APROBADO" in salida
    assert "DEF-01 ×2" in salida and "E1 · GET /api/servicios/empresas" in salida


def test_falla_nueva_rechaza_y_se_lista(tmp_path, monkeypatch, capsys):
    salida = _correr(tmp_path, monkeypatch, capsys, JUNIT_ROJO)
    assert "✖ RECHAZADO" in salida and "rompe" in salida and "Esperado 200" in salida


def test_contrato_omitido_nunca_da_verde(tmp_path, monkeypatch, capsys):
    needs = {"contrato": {"result": "skipped"}, "api": {"result": "success"},
             "web": {"result": "success"}, "rendimiento": {"result": "success"}}
    assert "✖ RECHAZADO" in _correr(tmp_path, monkeypatch, capsys, JUNIT, needs)
