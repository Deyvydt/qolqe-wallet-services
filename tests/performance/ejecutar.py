"""Ejecuta un escenario de rendimiento de punta a punta y deja la evidencia en resultados/<escenario>/.

Uso (con Qolqe levantado: uvicorn qolqe.main:app --no-access-log):
    python tests/performance/ejecutar.py carga|pico|estres|resistencia|humo

Pasos: prepara datos → mide CPU/memoria de Qolqe y de k6 (psutil, cada 1 s) → corre k6 →
verifica la integridad del dinero → analiza el CSV de k6 por ventanas de 10 s y por etapa → gráficos.
"""
import csv
import gzip
import json
import os
import subprocess
import sys
import threading
import time
from collections import defaultdict
from pathlib import Path

import psutil

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(Path(__file__).parent))
import datos  # noqa: E402

AQUI = Path(__file__).parent
USUARIOS = {"carga": 100, "pico": 300, "resistencia": 100, "humo": 2, "demo": 50}


def pid_qolqe(puerto=8000):
    for c in psutil.net_connections(kind="tcp"):
        if c.laddr and c.laddr.port == puerto and c.status == psutil.CONN_LISTEN:
            return c.pid
    sys.exit("Qolqe no está escuchando en el puerto 8000")


def monitorear(pid, k6, salida, parar):
    """CPU (% de un núcleo, como el script del enunciado) y memoria RSS de Qolqe y de k6."""
    procesos = {"qolqe": psutil.Process(pid), "k6": psutil.Process(k6.pid)}
    for p in procesos.values():
        p.cpu_percent(None)
    with open(salida, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["hora", "seg", "qolqe_cpu_%", "qolqe_mem_MB", "k6_cpu_%", "k6_mem_MB", "total_cpu_%"])
        inicio = time.time()
        while not parar.wait(1):
            fila = [time.strftime("%H:%M:%S"), round(time.time() - inicio)]
            for p in procesos.values():
                try:
                    fila += [p.cpu_percent(None), round(p.memory_info().rss / 1e6, 1)]
                except psutil.Error:
                    fila += ["", ""]
            w.writerow(fila + [psutil.cpu_percent(None)])
            f.flush()


def percentil(valores, p):
    if not valores:
        return None
    v = sorted(valores)
    return round(v[min(len(v) - 1, int(round(p / 100 * (len(v) - 1))))], 1)


def analizar(csv_k6, carpeta):
    """Lee el CSV crudo de k6 y resume por ventana de 10 s y por etapa."""
    ventanas = defaultdict(lambda: {"reqs": 0, "consulta": [], "dinero": [], "tec": 0, "neg": 0, "vus": 0})
    etapas = defaultdict(lambda: {"reqs": 0, "consulta": [], "dinero": [], "tec": 0, "neg": 0, "t0": 1e18, "t1": 0,
                                  "sesiones": 0})
    por_op = defaultdict(list)
    t0 = None
    with gzip.open(csv_k6, "rt") as f:
        for r in csv.DictReader(f):
            t = int(r["timestamp"])
            t0 = t if t0 is None else min(t0, t)
            tags = dict(x.split("=", 1) for x in r["extra_tags"].split("&") if "=" in x)
            v = ventanas[(t - (t0 or t)) // 10 * 10]
            m = r["metric_name"]
            if m == "vus":
                v["vus"] = max(v["vus"], int(float(r["metric_value"])))
                continue
            e = etapas[tags.get("etapa", "?")] if "etapa" in tags else None
            if m == "http_req_duration":
                ms = float(r["metric_value"])
                v["reqs"] += 1
                v[tags["tipo"]].append(ms)
                por_op[tags["op"]].append(ms)
                if e is not None:
                    e["reqs"] += 1
                    e[tags["tipo"]].append(ms)
                    e["t0"], e["t1"] = min(e["t0"], t), max(e["t1"], t)
                    e["sesiones"] += tags["op"] == "login"  # cada sesión empieza con un login
                    status = int(r["status"] or 0)
                    if status == 0 or status >= 500:
                        v["tec"] += 1
                        e["tec"] += 1
                    elif status >= 400:
                        v["neg"] += 1
                        e["neg"] += 1
    serie = []
    for seg in sorted(ventanas):
        v = ventanas[seg]
        serie.append({"seg": seg, "vus": v["vus"], "rps": round(v["reqs"] / 10, 2),
                      "p95_consulta_ms": percentil(v["consulta"], 95), "p95_dinero_ms": percentil(v["dinero"], 95),
                      "error_tecnico_%": round(100 * v["tec"] / v["reqs"], 2) if v["reqs"] else 0,
                      "error_negocio_%": round(100 * v["neg"] / v["reqs"], 2) if v["reqs"] else 0})
    with open(carpeta / "serie_10s.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(serie[0]))
        w.writeheader()
        w.writerows(serie)
    resumen = {}
    for nombre, e in etapas.items():
        dur = max(1, e["t1"] - e["t0"])
        resumen[nombre] = {
            "peticiones": e["reqs"], "duracion_s": dur, "rps": round(e["reqs"] / dur, 2),
            "sesiones_por_hora": round(e["sesiones"] / dur * 3600),
            "p95_consulta_ms": percentil(e["consulta"], 95), "p95_dinero_ms": percentil(e["dinero"], 95),
            "p99_consulta_ms": percentil(e["consulta"], 99), "p99_dinero_ms": percentil(e["dinero"], 99),
            "error_tecnico_%": round(100 * e["tec"] / e["reqs"], 2) if e["reqs"] else 0,
            "error_negocio_%": round(100 * e["neg"] / e["reqs"], 2) if e["reqs"] else 0,
        }
    resumen["_por_operacion_p95_ms"] = {op: percentil(v, 95) for op, v in sorted(por_op.items())}
    return serie, resumen


def graficar(serie, recursos_csv, carpeta, titulo):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    with open(recursos_csv) as f:
        rec = [r for r in csv.DictReader(f) if r["qolqe_cpu_%"]]
    seg = [s["seg"] / 60 for s in serie]
    fig, ax = plt.subplots(5, 1, figsize=(10, 15), sharex=True)
    ax[0].plot(seg, [s["vus"] for s in serie], color="gray")
    ax[0].set_ylabel("VUs activos")
    ax[1].plot(seg, [s["p95_consulta_ms"] for s in serie], label="p95 consultas + login")
    ax[1].plot(seg, [s["p95_dinero_ms"] for s in serie], label="p95 dinero")
    ax[1].axhline(800, ls="--", color="C0", lw=1, label="umbral 800 ms")
    ax[1].axhline(1500, ls="--", color="C1", lw=1, label="umbral 1500 ms")
    ax[1].set_ylabel("ms")
    if max((s["p95_consulta_ms"] or 0) for s in serie) > 5000:  # colapso: escala log para ver el antes y el después
        ax[1].set_yscale("log")
        ax[1].set_ylabel("ms (escala log)")
    ax[1].legend(fontsize=8)
    ax[2].plot(seg, [s["rps"] for s in serie], color="C2")
    ax[2].set_ylabel("peticiones/s")
    ax[3].plot(seg, [s["error_tecnico_%"] for s in serie], color="C3", label="técnico (5xx/timeout)")
    ax[3].plot(seg, [s["error_negocio_%"] for s in serie], color="C4", label="negocio (4xx)")
    ax[3].axhline(1, ls="--", color="C3", lw=1, label="umbral 1 %")
    ax[3].set_ylabel("% errores")
    ax[3].legend(fontsize=8)
    t = [int(r["seg"]) / 60 for r in rec]
    ax[4].plot(t, [float(r["qolqe_cpu_%"]) for r in rec], label="CPU Qolqe (% de 1 núcleo)")
    ax[4].plot(t, [float(r["k6_cpu_%"]) for r in rec], label="CPU k6 (% de 1 núcleo)")
    ax[4].plot(t, [float(r["total_cpu_%"]) for r in rec], label="CPU total equipo (%)", alpha=.5)
    ax4b = ax[4].twinx()
    ax4b.plot(t, [float(r["qolqe_mem_MB"]) for r in rec], color="k", ls=":", label="Memoria Qolqe (MB)")
    ax4b.set_ylabel("MB")
    ax[4].set_ylabel("% CPU")
    ax[4].legend(fontsize=8, loc="upper left")
    ax4b.legend(fontsize=8, loc="upper right")
    ax[4].set_xlabel("minutos desde el inicio")
    fig.suptitle(titulo)
    fig.tight_layout()
    fig.savefig(carpeta / "graficos.png", dpi=110)


def main(escenario):
    n = int(os.getenv("N_USUARIOS", USUARIOS.get(escenario, max(map(int, os.getenv(
        "ESCALONES", "200,400,600,800,1000,1200,1400,1600").split(","))))))
    carpeta = AQUI / "resultados" / escenario
    carpeta.mkdir(parents=True, exist_ok=True)
    pid = pid_qolqe()
    print(f"[{escenario}] preparando {n} usuarios…")
    antes = datos.preparar(n)
    entorno = {**os.environ, "ESCENARIO": escenario, "N_USUARIOS": str(n),
               "K6_WEB_DASHBOARD": "true", "K6_WEB_DASHBOARD_EXPORT": str(carpeta / "reporte_k6.html")}
    csv_k6 = carpeta / "k6_crudo.csv.gz"
    inicio = time.strftime("%Y-%m-%d %H:%M:%S")
    k6 = subprocess.Popen(["k6", "run", "--quiet", "--out", f"csv={csv_k6}", "--summary-export", str(carpeta / "resumen_k6.json"),
                           str(AQUI / "qolqe.js")], env=entorno)
    parar = threading.Event()
    hilo = threading.Thread(target=monitorear, args=(pid, k6, carpeta / "recursos.csv", parar))
    hilo.start()
    codigo = k6.wait()
    parar.set()
    hilo.join()
    fin = time.strftime("%Y-%m-%d %H:%M:%S")
    integridad = datos.verificar(antes, n)
    serie, resumen = analizar(csv_k6, carpeta)
    with open(carpeta / "recursos.csv") as f:
        rec = [r for r in csv.DictReader(f) if r["qolqe_cpu_%"]]
    recursos = {k: {"max": max(float(r[k]) for r in rec), "prom": round(sum(float(r[k]) for r in rec) / len(rec), 1)}
                for k in ["qolqe_cpu_%", "qolqe_mem_MB", "k6_cpu_%", "k6_mem_MB", "total_cpu_%"]}
    recursos["qolqe_mem_MB"]["inicio"] = float(rec[0]["qolqe_mem_MB"])
    recursos["qolqe_mem_MB"]["fin"] = float(rec[-1]["qolqe_mem_MB"])
    informe = {"escenario": escenario, "inicio": inicio, "fin": fin, "usuarios_preparados": n,
               "umbrales_k6_cumplidos": codigo == 0, "etapas": resumen, "recursos": recursos,
               "integridad_dinero": integridad}
    (carpeta / "analisis.json").write_text(json.dumps(informe, indent=2, ensure_ascii=False), encoding="utf-8")
    graficar(serie, carpeta / "recursos.csv", carpeta, f"Qolqe · escenario {escenario} ({inicio})")
    print(json.dumps({k: informe[k] for k in ["umbrales_k6_cumplidos", "etapas", "recursos"]}, indent=1))
    print("Integridad del dinero OK" if integridad["ok"] else f"INTEGRIDAD FALLÓ: {integridad}")


def regraficar(escenario):
    """Vuelve a dibujar graficos.png desde serie_10s.csv y recursos.csv (sin repetir la prueba)."""
    carpeta = AQUI / "resultados" / escenario
    with open(carpeta / "serie_10s.csv") as f:
        serie = [{k: (float(v) if v else None) for k, v in r.items()} for r in csv.DictReader(f)]
    info = json.loads((carpeta / "analisis.json").read_text(encoding="utf-8"))
    graficar(serie, carpeta / "recursos.csv", carpeta, f"Qolqe · escenario {escenario} ({info['inicio']})")


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[2] == "--regraficar":
        regraficar(sys.argv[1])
    else:
        main(sys.argv[1] if len(sys.argv) > 1 else "humo")
