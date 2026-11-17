"""Datos de prueba para rendimiento y verificación del dinero.

- preparar(n): reinicia Qolqe, deja n usuarios de carga (900000001…) con S/ 10,000 y 20 deudas
  pendientes cada uno, y devuelve una foto de saldos.
- verificar(foto): comprueba que ninguna operación de dinero quedó a medias ni se aplicó dos veces.

Usa la API de soporte (/api/pruebas/reiniciar y /api/pruebas/saldo). Los usuarios por encima de 200
(la semilla solo trae 200) y las deudas extra se insertan en la BD igual que lo hace la semilla.
"""
import json
import os
import sqlite3
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

RUTA_BD = Path(os.getenv("QOLQE_BD", Path(__file__).resolve().parents[2] / "datos" / "qolqe.db"))

BASE = "http://127.0.0.1:8000"  # en Windows "localhost" prueba IPv6 primero y pierde ~2 s por llamada
SEMILLA = 200          # usuarios de carga que trae Qolqe
DEUDAS_POR_USUARIO = 20


def _api(metodo, ruta, cuerpo=None):
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    req = urllib.request.Request(f"{BASE}{ruta}", data=datos, method=metodo,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read() or b"null")


def _bd():
    c = sqlite3.connect(RUTA_BD, timeout=30)
    c.row_factory = sqlite3.Row
    return c


def celular(n):
    return f"9{n:08d}"


def preparar(n_usuarios):
    _api("POST", "/api/pruebas/reiniciar")
    hoy = datetime.now()  # el reloj de la app no se desfasa en estas pruebas
    with _bd() as bd:
        modelo = bd.execute("SELECT * FROM usuarios WHERE celular = ?", (celular(1),)).fetchone()
        base_id = modelo["id"] - 1
        for n in range(SEMILLA + 1, n_usuarios + 1):  # mismo PIN (2580) y misma forma que la semilla
            uid = base_id + n
            bd.execute("INSERT INTO usuarios (id, dni, nombres, celular, pin_hash, creado_en) VALUES (?,?,?,?,?,?)",
                       (uid, f"7{n:07d}", f"Usuario Carga {n:03d}", celular(n), modelo["pin_hash"], modelo["creado_en"]))
            bd.execute("INSERT INTO cuentas VALUES (?, 0, ?)", (uid, modelo["creado_en"]))
            bd.execute("INSERT INTO limites (usuario_id, limite_diario_cent) VALUES (?, 200000)", (uid,))
            bd.execute("INSERT INTO historial_pin (usuario_id, pin_hash, creado_en) VALUES (?,?,?)",
                       (uid, modelo["pin_hash"], modelo["creado_en"]))
        vence = (hoy + timedelta(days=10)).strftime("%Y-%m-%d")
        bd.executemany(
            "INSERT INTO deudas (empresa, suministro, titular, periodo, monto_cent, vencimiento) VALUES (?,?,?,?,?,?)",
            [("AGUA", f"40000{n:05d}", f"Usuario Carga {n:03d}", f"20{20 + k // 12}-{k % 12 + 1:02d}", 1000, vence)
             for n in range(1, n_usuarios + 1) for k in range(DEUDAS_POR_USUARIO)],
        )
    for n in range(1, n_usuarios + 1):
        _api("PUT", "/api/pruebas/saldo", {"celular": celular(n), "saldo": "10000.00"})
    return foto(n_usuarios)


def foto(n_usuarios):
    with _bd() as bd:
        filas = bd.execute(
            """SELECT u.celular, c.saldo_cent, (SELECT COALESCE(MAX(id), 0) FROM movimientos) AS ultimo_mov
               FROM usuarios u JOIN cuentas c ON c.usuario_id = u.id WHERE u.celular BETWEEN ? AND ?""",
            (celular(1), celular(n_usuarios))).fetchall()
    return {"saldos": {f["celular"]: f["saldo_cent"] for f in filas},
            "ultimo_mov": filas[0]["ultimo_mov"] if filas else 0}


def verificar(antes, n_usuarios):
    """Integridad del dinero: saldo_final − saldo_inicial == suma de movimientos nuevos, para cada usuario;
    cada transferencia con sus 2 movimientos; ningún código de operación repetido."""
    despues = foto(n_usuarios)
    with _bd() as bd:
        mov = dict(bd.execute(
            """SELECT u.celular, SUM(m.importe_cent) FROM movimientos m JOIN usuarios u ON u.id = m.usuario_id
               WHERE m.id > ? GROUP BY u.celular""", (antes["ultimo_mov"],)).fetchall())
        conteo = dict(bd.execute(
            "SELECT tipo, COUNT(*) FROM movimientos WHERE id > ? GROUP BY tipo", (antes["ultimo_mov"],)).fetchall())
        repetidos = bd.execute(
            """SELECT codigo_operacion, COUNT(*) c FROM movimientos WHERE id > ? AND tipo != 'TRANSFERENCIA_RECIBIDA'
               GROUP BY codigo_operacion HAVING c > 1""", (antes["ultimo_mov"],)).fetchall()
        pagos_dobles = bd.execute(
            "SELECT deuda_id, COUNT(*) c FROM pagos_servicio GROUP BY deuda_id HAVING c > 1").fetchall()
    descuadres = {c: (despues["saldos"][c] - s, mov.get(c, 0)) for c, s in antes["saldos"].items()
                  if despues["saldos"][c] - s != mov.get(c, 0)}
    return {
        "usuarios_revisados": len(antes["saldos"]),
        "movimientos_nuevos_por_tipo": conteo,
        "transferencias_completas": conteo.get("TRANSFERENCIA_ENVIADA", 0) == conteo.get("TRANSFERENCIA_RECIBIDA", 0),
        "usuarios_con_descuadre": descuadres,
        "codigos_repetidos": [dict(r) for r in repetidos],
        "deudas_pagadas_dos_veces": [dict(r) for r in pagos_dobles],
        "ok": not descuadres and not repetidos and not pagos_dobles
              and conteo.get("TRANSFERENCIA_ENVIADA", 0) == conteo.get("TRANSFERENCIA_RECIBIDA", 0),
    }


if __name__ == "__main__":  # autoverificación rápida: preparar 5 usuarios y verificar sin carga
    f = preparar(5)
    assert len(f["saldos"]) == 5 and all(s == 1_000_000 for s in f["saldos"].values()), f
    assert verificar(f, 5)["ok"]
    print("datos.py OK")
