"""QUÉ ES: VALIDACIÓN medible del agente de triaje (triaje_ia.py).

PARA QUÉ:
  Corre el agente IA y la línea base por reglas contra fallas etiquetadas a mano
  (tests/triaje/casos_etiquetados.json) y calcula la exactitud de la CATEGORÍA y del DEF asignado.
  Escribe una tabla caso por caso en Markdown.

CÓMO SE USA (desde la raíz del repo):
  ANTHROPIC_API_KEY=... python .github/scripts/validar_triaje.py > reportes/triaje/validacion.md   (o GITHUB_TOKEN para GitHub Models)
  Sin GITHUB_TOKEN solo evalúa la línea base (lo dice en el reporte; no inventa cifras).
"""
import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path

from triaje_ia import MODELO, PROVEEDOR, RAIZ_REPO, clasificar_offline, triar

CASOS = RAIZ_REPO / "tests" / "triaje" / "casos_etiquetados.json"


def puntaje(casos, resultados):
    cat = sum(r["categoria"] == c["esperado"]["categoria"] for c, r in zip(casos, resultados))
    dfx = sum(r["defecto_conocido"] == c["esperado"]["defecto_conocido"] for c, r in zip(casos, resultados))
    return cat, dfx


def _ok(r, c, campo):
    return "✅" if r[campo] == c["esperado"][campo] else "❌"



def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser()
    p.parse_args()

    casos = json.loads(CASOS.read_text(encoding="utf-8"))["casos"]
    base = [clasificar_offline(c) for c in casos]
    ia, aviso = triar(casos, token=os.environ.get("GITHUB_TOKEN"))
    n = len(casos)
    hay_ia = aviso is None

    out = [f"# Validación del agente de triaje · {date.today().isoformat()}", "",
           f"Casos etiquetados: {n} (`tests/triaje/casos_etiquetados.json`). Modelo: `{MODELO}` ({PROVEEDOR}).", ""]
    if not hay_ia:
        out += [f"> ⚠️ El modelo no estuvo disponible ({aviso}); solo se evaluó la línea base por reglas.", ""]
    out += ["| Clasificador | Categoría correcta | DEF correcto |", "|---|---:|---:|"]
    for nombre, res in [("Línea base (reglas)", base)] + ([("Agente IA", ia)] if hay_ia else []):
        cat, dfx = puntaje(casos, res)
        out.append(f"| {nombre} | {cat}/{n} ({cat / n:.0%}) | {dfx}/{n} ({dfx / n:.0%}) |")
    out += ["", "## Caso por caso", "",
            "| Caso | Esperado | Reglas | IA | Herramientas usadas por el agente | Confianza IA |",
            "|---|---|---|---|---|---:|"]
    for c, b, r in zip(casos, base, ia):
        esp = f"{c['esperado']['categoria']} / {c['esperado']['defecto_conocido'] or '—'}"
        reg = f"{b['categoria']} {_ok(b, c, 'categoria')} / {b['defecto_conocido'] or '—'} {_ok(b, c, 'defecto_conocido')}"
        if hay_ia:
            iat = f"{r['categoria']} {_ok(r, c, 'categoria')} / {r['defecto_conocido'] or '—'} {_ok(r, c, 'defecto_conocido')}"
            herr, conf = ", ".join(dict.fromkeys(r.get("herramientas", []))) or "ninguna", f"{r['confianza']:.2f}"
        else:
            iat, herr, conf = "no evaluado", "—", "—"
        out.append(f"| {c['id']} | {esp} | {reg} | {iat} | {herr} | {conf} |")
    texto = "\n".join(out) + "\n"

    print(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
