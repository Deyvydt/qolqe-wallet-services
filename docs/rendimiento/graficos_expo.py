"""Gráficos anchos (16:9) para la exposición, desde tests/performance/resultados. Salida: docs/rendimiento/img/."""
import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

RES = Path(__file__).resolve().parents[2] / "tests" / "performance" / "resultados"
OUT = Path(__file__).parent / "img"
OUT.mkdir(exist_ok=True)
TINTA, ORO, TEAL, ROJO, SUAVE = "#16302B", "#B7791F", "#1F6F63", "#A63D2A", "#8A9C97"
plt.rcParams.update({"font.size": 15, "axes.edgecolor": SUAVE, "axes.labelcolor": TINTA, "xtick.color": TINTA,
                     "ytick.color": TINTA, "axes.spines.top": False, "axes.spines.right": False,
                     "figure.facecolor": "#F3F5F2", "axes.facecolor": "#F3F5F2"})


def serie(e):
    with open(RES / e / "serie_10s.csv") as f:
        return [{k: float(v) if v else None for k, v in r.items()} for r in csv.DictReader(f)]


def recursos(e):
    with open(RES / e / "recursos.csv") as f:
        return [r for r in csv.DictReader(f) if r["qolqe_cpu_%"]]


def guardar(fig, nombre):
    fig.tight_layout()
    fig.savefig(OUT / nombre, dpi=120)
    plt.close(fig)


# 1. Carga y pico: p95 en el tiempo frente a los umbrales
fig, axs = plt.subplots(1, 2, figsize=(16, 6.2), sharey=True)
for ax, e, titulo in zip(axs, ["carga", "pico"], ["Carga · 100 VUs", "Pico · 300 VUs"]):
    s = serie(e)
    t = [x["seg"] / 60 for x in s]
    ax.plot(t, [x["p95_consulta_ms"] for x in s], color=TEAL, lw=2.5, label="p95 consultas + login")
    ax.plot(t, [x["p95_dinero_ms"] for x in s], color=ORO, lw=2.5, label="p95 dinero")
    ax.axhline(800, color=TEAL, ls="--", lw=1.5)
    ax.axhline(1500, color=ORO, ls="--", lw=1.5)
    ax.text(t[-1], 830, "umbral 800 ms", ha="right", color=TEAL)
    ax.text(t[-1], 1530, "umbral 1 500 ms", ha="right", color=ORO)
    ax2 = ax.twinx()
    ax2.fill_between(t, [x["vus"] for x in s], color=SUAVE, alpha=.18, lw=0)
    ax2.set_ylabel("VUs", color=SUAVE)
    ax2.spines["right"].set_visible(True)
    ax.set_title(titulo, loc="left", fontweight="bold", color=TINTA)
    ax.set_xlabel("minutos")
    ax.set_ylim(0, 1700)
axs[0].set_ylabel("ms")
axs[0].legend(loc="upper left", bbox_to_anchor=(0.02, 0.8), frameon=False)
guardar(fig, "carga_pico.png")

# 2. Estrés por escalón: throughput y p95 (log)
d = json.loads((RES / "estres" / "analisis.json").read_text(encoding="utf-8"))["etapas"]
esc = [k for k in d if k.isdigit()]
x = range(len(esc))
fig, ax = plt.subplots(figsize=(16, 6.4))
colores = [TEAL if d[k]["error_tecnico_%"] < 1 else ROJO for k in esc]
ax.bar(x, [d[k]["rps"] for k in esc], color=colores, alpha=.85, width=.6)
for i, k in enumerate(esc):
    ax.text(i, d[k]["rps"] + 2, f"{d[k]['rps']:.0f} req/s", ha="center", fontsize=13)
ax.set_xticks(list(x), [f"{k} VUs" for k in esc])
ax.set_ylabel("throughput (req/s)")
ax2 = ax.twinx()
ax2.plot(x, [d[k]["p95_consulta_ms"] for k in esc], color=ORO, marker="o", lw=3, label="p95 consultas")
ax2.axhline(800, color=ORO, ls="--", lw=1.5)
ax2.set_yscale("log")
ax2.set_ylabel("p95 (ms, escala log)", color=ORO)
ax2.spines["right"].set_visible(True)
ax2.text(len(esc) - .5, 900, "umbral 800 ms", ha="right", color=ORO)
ax.set_title("Estrés: cumple hasta 1 000 VUs; en 1 200 colapsa (rojo = errores > 1 %)", loc="left",
             fontweight="bold", color=TINTA)
guardar(fig, "estres_escalones.png")

# 3. Colapso: throughput, CPU y memoria en el tiempo
s = serie("estres")
r = recursos("estres")
fig, ax = plt.subplots(figsize=(16, 6.4))
ax.plot([p["seg"] / 60 for p in s], [p["rps"] for p in s], color=TEAL, lw=2.5, label="throughput (req/s)")
cpu = [float(p["qolqe_cpu_%"]) for p in r]
suav = [sum(cpu[max(0, i - 15):i + 1]) / len(cpu[max(0, i - 15):i + 1]) for i in range(len(cpu))]
ax.plot([int(p["seg"]) / 60 for p in r], suav, color=ORO, lw=2.5, label="CPU de Qolqe (% de 1 núcleo, media 15 s)")
ax.set_ylabel("req/s · % CPU")
ax.set_xlabel("minutos desde el inicio")
ax2 = ax.twinx()
ax2.plot([int(p["seg"]) / 60 for p in r], [float(p["qolqe_mem_MB"]) for p in r], color=ROJO, lw=2.5, ls=":",
         label="memoria de Qolqe (MB)")
ax2.set_ylabel("MB", color=ROJO)
ax2.spines["right"].set_visible(True)
ax.axvline(16.3, color=ROJO, lw=1)
ax.text(16.45, ax.get_ylim()[1] * .92, "colapso (1 200 VUs)", color=ROJO)
h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc="upper left", frameon=False)
ax.set_title("En el colapso la CPU baja y la memoria sube: el servidor espera, no trabaja", loc="left",
             fontweight="bold", color=TINTA)
guardar(fig, "estres_colapso.png")

# 4. Resistencia: memoria y p95 a lo largo de 30 min
if (RES / "resistencia" / "serie_10s.csv").exists():
    s = serie("resistencia")
    r = recursos("resistencia")
    fig, ax = plt.subplots(figsize=(16, 6.2))
    ax.plot([int(p["seg"]) / 60 for p in r], [float(p["qolqe_mem_MB"]) for p in r], color=ROJO, lw=1.8,
            label="memoria de Qolqe (MB)")
    ax.set_ylabel("MB", color=ROJO)
    ax.set_xlabel("minutos")
    ax2 = ax.twinx()
    ax2.plot([p["seg"] / 60 for p in s], [p["p95_consulta_ms"] for p in s], color=TEAL, lw=2.5, label="p95 consultas (ms)")
    ax2.plot([p["seg"] / 60 for p in s], [p["p95_dinero_ms"] for p in s], color=ORO, lw=2.5, label="p95 dinero (ms)")
    ax2.set_ylim(0, 400)
    ax2.set_ylabel("ms")
    ax2.spines["right"].set_visible(True)
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper left", frameon=False)
    ax.set_title("Resistencia · 100 VUs durante 30 min", loc="left", fontweight="bold", color=TINTA)
    guardar(fig, "resistencia.png")

print(sorted(p.name for p in OUT.iterdir()))
