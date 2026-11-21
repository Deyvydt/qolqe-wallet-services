"""Prueba de humo: verifica que la app levanta y responde."""
import pytest
from fastapi.testclient import TestClient

from qolqe.main import app


@pytest.mark.tecnico
def test_la_app_responde():
    with TestClient(app) as cliente:
        respuesta = cliente.get("/api/salud")
        assert respuesta.status_code == 200
        assert respuesta.json()["estado"] == "ok"
