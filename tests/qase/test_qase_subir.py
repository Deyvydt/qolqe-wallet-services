"""QUÉ ES: pruebas unitarias de .github/scripts/qase_subir.py (subida de resultados a Qase).

PARA QUÉ:
  Verifican, SIN red externa, que el script habla bien con la API v1 de Qase: un servidor HTTP
  local falso (http.server en un hilo) imita los endpoints /case, /run y /result.
  Se comprueba: creación de casos faltantes, reutilización de los existentes, creación del run,
  mapeo de estados (xfail → skipped con el defecto), reintento ante 429 y degradación elegante
  (sin token o con errores 500 el script avisa "Qase no disponible" y termina con 0).
"""
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".github" / "scripts"))
import qase_subir  # noqa: E402

pytestmark = pytest.mark.herramienta  # el script excluye esta etiqueta al subir a Qase

JUNIT = """<?xml version="1.0"?><testsuites><testsuite name="pytest">
<testcase classname="a" name="test_pagar_deuda_camino_feliz" time="0.25">
  <properties><property name="etiquetas" value="CA1,G2,HU-G2-02,camino-feliz"/></properties></testcase>
<testcase classname="a" name="test_dia_de_atraso[un dia-x]" time="0.1">
  <properties><property name="etiquetas" value="G2,HU-G2-01"/><property name="defecto" value="DEF-02"/></properties>
  <skipped type="pytest.xfail" message="DEF-02 (ver docs/defectos.md)"/></testcase>
<testcase classname="a" name="test_contrato_openapi" time="3">
  <properties><property name="etiquetas" value="schemathesis"/></properties>
  <failure message="500 en /api/servicios/pagos">traza</failure></testcase>
</testsuite></testsuites>"""

ROBOT = """<?xml version="1.0"?><robot><suite name="e2e"><test name="Pagar agua">
<tag>G2</tag><tag>HU-G2-02</tag><tag>CP-W01</tag>
<status status="PASS" elapsed="4.5"/></test></suite></robot>"""


class FalsoQase(BaseHTTPRequestHandler):
    pedidos, existentes, falla = [], {}, None  # falla: código HTTP fijo, o lista de códigos a devolver primero

    def _responder(self):
        largo = int(self.headers.get("Content-Length") or 0)
        cuerpo = json.loads(self.rfile.read(largo)) if largo else None
        clase = type(self)
        clase.pedidos.append((self.command, self.path, cuerpo, self.headers.get("Token")))
        codigo = clase.falla.pop(0) if isinstance(clase.falla, list) and clase.falla else clase.falla
        if isinstance(codigo, int):
            self.send_response(codigo)
            self.end_headers()
            return
        if self.command == "GET" and self.path.startswith("/case/QOLQE"):
            offset = int(self.path.split("offset=")[1])
            todos = [{"id": i, "title": t} for t, i in clase.existentes.items()]
            resultado = {"total": len(todos), "filtered": len(todos), "entities": todos[offset:offset + 1]}
        elif self.path == "/case/QOLQE":
            resultado = {"id": 100 + len(clase.pedidos)}
        elif self.path == "/run/QOLQE":
            resultado = {"id": 7}
        else:
            resultado = {}
        datos = json.dumps({"status": True, "result": resultado}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(datos)

    do_GET = do_POST = _responder

    def log_message(self, *args):
        pass


@pytest.fixture
def servidor(monkeypatch, tmp_path):
    FalsoQase.pedidos, FalsoQase.existentes, FalsoQase.falla = [], {}, None
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), FalsoQase)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    monkeypatch.setattr(qase_subir, "API", f"http://127.0.0.1:{httpd.server_port}")
    monkeypatch.setattr(qase_subir, "ESPERA", 0)
    monkeypatch.setenv("QASE_API_TOKEN", "token-de-prueba")
    monkeypatch.delenv("GITHUB_STEP_SUMMARY", raising=False)
    (tmp_path / "junit.xml").write_text(JUNIT, encoding="utf-8")
    (tmp_path / "output.xml").write_text(ROBOT, encoding="utf-8")
    yield tmp_path
    httpd.shutdown()


def _correr(tmp):
    return qase_subir.main(["--junit", str(tmp / "junit.xml"), "--robot", str(tmp / "output.xml"),
                            "--titulo-run", "Pipeline #1", "--commit", "abc1234", "--url-run", "https://gh/run/1"])


def _pedidos(metodo, ruta):
    return [p for p in FalsoQase.pedidos if p[0] == metodo and p[1].startswith(ruta)]


def test_crea_faltantes_reutiliza_existentes_y_sube_resultados(servidor, capsys):
    FalsoQase.existentes = {"[api] pagar deuda camino feliz": 1, "[web] CP-W01 · Pagar agua": 2}
    assert _correr(servidor) == 0

    # Paginación: 2 existentes de a 1 por página → 2 GET
    assert len(_pedidos("GET", "/case/QOLQE")) == 2
    creados = [p[2] for p in _pedidos("POST", "/case/QOLQE")]
    assert {c["title"] for c in creados} == {"[api] dia de atraso [un dia-x]", "[contrato] contrato openapi"}
    xfail = next(c for c in creados if c["title"].startswith("[api]"))
    assert xfail["suite_id"] == 1 and xfail["custom_field"] == {"1": "GET /api/servicios/deudas", "2": "HU-G2-01"}
    assert next(c for c in creados if c["title"].startswith("[contrato]"))["suite_id"] == 2
    assert all(p[3] == "token-de-prueba" for p in FalsoQase.pedidos)

    run = _pedidos("POST", "/run/QOLQE")[0][2]
    assert run["is_autotest"] is True and "abc1234" in run["description"] and "https://gh/run/1" in run["description"]
    assert {1, 2} <= set(run["cases"]) and len(run["cases"]) == 4  # 2 reutilizados + 2 creados

    resultados = {r["case_id"]: r for r in _pedidos("POST", "/result/QOLQE/7/bulk")[0][2]["results"]}
    assert resultados[1] == {"case_id": 1, "status": "passed", "time_ms": 250}
    assert resultados[2]["time_ms"] == 4500
    estados = sorted(r["status"] for r in resultados.values())
    assert estados == ["failed", "passed", "passed", "skipped"]
    omitido = next(r for r in resultados.values() if r["status"] == "skipped")
    assert "defecto conocido DEF-02" in omitido["comment"]
    assert _pedidos("POST", "/run/QOLQE/7/complete")
    assert "https://app.qase.io/run/QOLQE/dashboard/7" in capsys.readouterr().out


def test_suite_web_g2_y_nucleo():
    base = {"nivel": "web", "hu": ["HU-3"], "etiquetas": ["HU-3"]}
    assert qase_subir.suite(base) == 3
    assert qase_subir.suite({**base, "hu": ["HU-G2-01"], "etiquetas": ["G2"]}) == 4


def test_reintenta_ante_429(servidor):
    FalsoQase.falla = [429, 503]
    assert _correr(servidor) == 0
    assert _pedidos("POST", "/run/QOLQE/7/complete")


def test_sin_token_no_llama_a_la_red(servidor, monkeypatch, capsys):
    monkeypatch.delenv("QASE_API_TOKEN")
    assert _correr(servidor) == 0
    assert "Qase no disponible" in capsys.readouterr().out
    assert FalsoQase.pedidos == []


def test_error_500_degrada_sin_romper(servidor, capsys):
    FalsoQase.falla = 500
    assert _correr(servidor) == 0
    assert "Qase no disponible" in capsys.readouterr().out
    assert len(FalsoQase.pedidos) == qase_subir.INTENTOS  # reintentó y se rindió


def test_dry_run_no_usa_red(servidor, capsys):
    assert qase_subir.main(["--junit", str(servidor / "junit.xml"), "--dry-run"]) == 0
    assert "[dry-run] 3 casos" in capsys.readouterr().out
    assert FalsoQase.pedidos == []
