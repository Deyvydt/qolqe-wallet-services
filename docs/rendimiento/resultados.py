"""Secciones 7 y 8 del informe, armadas desde tests/performance/resultados/*/analisis.json."""
import json
from pathlib import Path

RES = Path(__file__).resolve().parents[2] / "tests" / "performance" / "resultados"


def cargar(e):
    return json.loads((RES / e / "analisis.json").read_text(encoding="utf-8"))


def ms(v):
    return "timeout (60 s)" if v and v >= 59000 else f"{v:.0f} ms"


def fila_umbral(nombre, umbral, valor, ok):
    return [nombre, umbral, valor, "Cumple" if ok else "NO cumple"]


def tabla_estable(d, vus):
    e = d["etapas"]["estable"]
    return [
        ["Métrica (estado estable)", "Umbral", "Resultado", "Veredicto"],
        fila_umbral("p95 consultas + login", "< 800 ms", ms(e["p95_consulta_ms"]), e["p95_consulta_ms"] < 800),
        fila_umbral("p95 operaciones de dinero", "< 1 500 ms", ms(e["p95_dinero_ms"]), e["p95_dinero_ms"] < 1500),
        ["p99 consultas / dinero", "(informativo)", f"{ms(e['p99_consulta_ms'])} / {ms(e['p99_dinero_ms'])}", "—"],
        fila_umbral("Errores técnicos (5xx/timeout)", "< 1 %", f"{e['error_tecnico_%']} %", e["error_tecnico_%"] < 1),
        ["Errores de negocio (4xx)", "aparte (datos)", f"{e['error_negocio_%']} %", "—"],
        fila_umbral("Throughput", "≥ 3 000 sesiones/h" if vus == 100 else "(informativo)",
                    f"{e['sesiones_por_hora']} sesiones/h · {e['rps']} req/s",
                    e["sesiones_por_hora"] >= 3000),
        fila_umbral("Integridad del dinero", "0 a medias / duplicadas",
                    "OK: 0 descuadres" if d["integridad_dinero"]["ok"] else "FALLA", d["integridad_dinero"]["ok"]),
    ]


def recursos(d):
    r = d["recursos"]
    m = r["qolqe_mem_MB"]
    return [
        f"Qolqe: CPU promedio {r['qolqe_cpu_%']['prom']} % y máximo {r['qolqe_cpu_%']['max']} % de un núcleo; memoria "
        f"{m['inicio']} MB al inicio, máximo {m['max']} MB, {m['fin']} MB al final.",
        f"k6: CPU promedio {r['k6_cpu_%']['prom']} % y máximo {r['k6_cpu_%']['max']} % de un núcleo; memoria máxima "
        f"{r['k6_mem_MB']['max']} MB. CPU total del equipo: máximo {r['total_cpu_%']['max']} % (< 80 %: la medición es válida).",
    ]


def integridad(d):
    i = d["integridad_dinero"]
    c = i["movimientos_nuevos_por_tipo"]
    return (f"Integridad del dinero ({i['usuarios_revisados']} usuarios revisados): {c.get('TRANSFERENCIA_ENVIADA', 0)} "
            f"transferencias enviadas = {c.get('TRANSFERENCIA_RECIBIDA', 0)} recibidas, {c.get('RECARGA', 0)} recargas, "
            f"{c.get('PAGO_SERVICIO', 0)} pagos; usuarios con descuadre: {len(i['usuarios_con_descuadre'])}; códigos "
            f"repetidos: {len(i['codigos_repetidos'])}; deudas pagadas dos veces: {len(i['deudas_pagadas_dos_veces'])}.")


carga, pico, estres = cargar("carga"), cargar("pico"), cargar("estres")
try:
    resistencia = cargar("resistencia")
except FileNotFoundError:
    resistencia = None

ESCALONES = [k for k in estres["etapas"] if k.isdigit()]
tabla_estres = [["VUs", "req/s", "p95 consultas", "p95 dinero", "Errores técnicos", "Veredicto"]]
for k in ESCALONES:
    e = estres["etapas"][k]
    ok = e["p95_consulta_ms"] < 800 and e["p95_dinero_ms"] < 1500 and e["error_tecnico_%"] < 1
    tabla_estres.append([k, e["rps"], ms(e["p95_consulta_ms"]), ms(e["p95_dinero_ms"]), f"{e['error_tecnico_%']} %",
                         "Cumple" if ok else "NO cumple"])
ultimo_ok = max(int(k) for k in ESCALONES if estres["etapas"][k]["error_tecnico_%"] < 1
                and estres["etapas"][k]["p95_consulta_ms"] < 800)

PRUEBAS = [
    {"titulo": "Carga · hora punta (100 VUs)", "carpeta": "carga",
     "resumen": [f"Ejecución: {carga['inicio']} → {carga['fin']}. 0 → 100 VUs en 120 s, 600 s estables, 60 s de bajada.",
                 "Veredicto: CUMPLE todos los umbrales con amplio margen."],
     "tabla": tabla_estable(carga, 100),
     "recursos": recursos(carga) + [integridad(carga)],
     "extra": ["Lectura: el p95 se mantiene plano (~90–120 ms) toda la prueba; 0 errores; el throughput acompaña a los VUs. "
               "La memoria muestra un diente de sierra (sube y baja cada 1–2 min): patrón periódico del recolector de "
               "basura de Python, no una fuga. Sesiones/h algo por encima de 3 000 porque la pausa media simulada es 17.5 s."]},
    {"titulo": "Pico · campaña Quincena Qolqe (300 VUs)", "carpeta": "pico",
     "resumen": [f"Ejecución: {pico['inicio']} → {pico['fin']}. 0 → 300 VUs en 300 s (mayoría entra en 5 min), 600 s "
                 "estables, 60 s de bajada.",
                 "Veredicto: CUMPLE; no hay degradación apreciable frente a la hora punta y ninguna operación de dinero "
                 "quedó a medias ni duplicada."],
     "tabla": tabla_estable(pico, 300),
     "recursos": recursos(pico) + [integridad(pico)],
     "extra": ["Lectura: triplicar los usuarios triplica el throughput (8.6 → 25.8 req/s) sin mover el p95: el sistema "
               "todavía no está saturado. La CPU de Qolqe sube a ~31 % de promedio con picos de un núcleo completo."]},
    {"titulo": "Estrés · escalones de 200 VUs hasta 1 600", "carpeta": "estres",
     "resumen": [f"Ejecución: {estres['inicio']} → {estres['fin']}. Escalones de +200 VUs: 60 s de subida + 120 s sostenidos.",
                 f"Veredicto: cumple hasta {ultimo_ok} VUs. En el escalón de 1 200 VUs (~100 req/s) colapsa de forma "
                 "abrupta: p95 = 60 s (timeout de k6), errores técnicos 42 % → 100 % y el throughput cae de ~100 a ~20 req/s. "
                 "No se recupera al bajar la carga."],
     "tabla": tabla_estres,
     "recursos": recursos(estres) + [integridad(estres)],
     "extra": ["El p95 se grafica en escala logarítmica para ver el antes y el después del colapso. Evidencia adicional en "
               "resultados/estres/: hilos_py-spy.txt (estado de los 42 hilos del servidor) y recuperacion.log (13 min "
               "después de terminar, /api/salud seguía sin responder y la memoria en ~1.2 GB; se reinició el servidor)."]},
]
if resistencia:
    PRUEBAS.append({"titulo": "Resistencia · 100 VUs durante 30 min (versión acotada)", "carpeta": "resistencia",
                    "resumen": [f"Ejecución: {resistencia['inicio']} → {resistencia['fin']}. 120 s de subida, 1 800 s estables, 60 s de bajada."],
                    "tabla": tabla_estable(resistencia, 100),
                    "recursos": recursos(resistencia) + [integridad(resistencia)],
                    "extra": ["Tendencia (promedio por bloques de 5 min del estado estable): memoria de Qolqe 84 → 87 → 87 → 87 → "
                              "86 → 88 MB y p95 de consultas 92.6 → 90.3 → 90.7 ms (por bloques de 10 min). La memoria "
                              "mantiene el diente de sierra del recolector de basura sin tendencia creciente: no hay "
                              "indicios de fuga ni de degradación en 30 min. Limitación: 30 min no equivalen a 18 h; la tabla "
                              "de sesiones crece con cada login (≈ 3 400 filas/h) y su efecto en 18 h queda por medir."]})

DIFERENCIAS = [
    "- El estrés se planificó primero en escalones de 100 hasta 600 VUs; la prueba de carga mostró ~12 % de CPU con 100 "
    "VUs, así que se amplió a escalones de 200 hasta 1 600 para encontrar el límite.",
    "- La resistencia de 18 h (6:00–24:00) no es viable en el curso: se ejecutó 30 min a 100 VUs y se analiza la tendencia.",
    "- Tras el estrés el servidor no se recuperó y se reinició antes de la prueba de resistencia.",
    "- La preparación de datos usó 127.0.0.1 en vez de localhost (en Windows, localhost probaba IPv6 primero y tardaba 2 s por llamada).",
]

ANALISIS = {
    "cumplimiento": [
        "Sí en hora punta (100 VUs) y en el pico de la campaña (300 VUs): p95 de consultas ≈ 91–94 ms (umbral 800), p95 de "
        "dinero ≈ 117–120 ms (umbral 1 500), 0 % de errores técnicos, ≥ 3 000 sesiones/h y 0 descuadres de dinero.",
        f"En estrés se cumple hasta {ultimo_ok} VUs (≈ 85 req/s). Deja de cumplir entre 1 000 y 1 200 VUs: en 1 200 todas "
        "las métricas fallan a la vez (p95 = 60 s, errores 42–100 %, throughput cae a ~20 req/s).",
    ],
    "cuello": [
        "Patrón: abrupto (plano hasta ~100 req/s y luego se dispara), propio de un recurso con límite fijo que se agota, y "
        "sin recuperación posterior.",
        "Cuello de botella: el lock de escritura de SQLite (un solo escritor a la vez) combinado con el grupo fijo de 40 "
        "hilos del servidor. Evidencia:",
        "- CPU de Qolqe ≈ 5 % durante el colapso (y la máquina por debajo de 52 %): no es CPU.",
        "- py-spy: los 40 hilos de trabajo están detenidos en una escritura (27 en el INSERT de sesiones del login, 13 en el "
        "UPDATE de saldo), esperando el busy_timeout de 10 s; ningún hilo está en commit ni rollback.",
        "- Desde fuera, BEGIN IMMEDIATE sobre la BD responde «database is locked» minutos después de terminar la prueba.",
        "- Memoria de 150 MB a 1.2 GB: las peticiones se acumulan en cola; throughput de 100 a 20 req/s.",
        "- Los primeros errores de k6 (20:00:57) son conexiones cortadas por el servidor en el login: la cola de conexiones "
        "se rebalsó justo antes del colapso.",
        "Interpretación: el lock de escritura quedó retenido por una transacción abierta que ningún hilo atiende (huérfana). "
        "Con el lock tomado, cada escritura espera 10 s y falla: 40 hilos / 10 s ≈ 4 escrituras/s frente a ~100 peticiones/s "
        "que llegan, y las lecturas quedan atrapadas en la cola de hilos detrás de ellas. Hipótesis sobre el origen (a confirmar "
        "por desarrollo, DEF-05): una petición interrumpida por la desconexión del cliente entre su escritura y su commit.",
        "Aun en el colapso, la integridad del dinero se mantuvo: SQLite deshace lo que no se confirma, y todas las "
        "transferencias enviadas tienen su recibida.",
    ],
    "capacidad": [
        f"≈ {ultimo_ok} usuarios simultáneos cumpliendo todos los criterios (10× la hora punta, 3.3× la campaña), con el "
        "límite entre 1 000 y 1 200 VUs (~85–100 req/s) en este entorno. Es una línea base relativa (laptop, SQLite local), "
        "no la capacidad de producción.",
    ],
    "riesgos": [
        "- Bajo: la campaña (300 VUs) tiene un margen de ~3×; no requiere cambios para cumplir.",
        "- Alto: si un evento supera ~1 000 usuarios simultáneos (campaña viral, bots, reintentos masivos), Qolqe no se degrada "
        "con gracia: se cae del todo y queda caído hasta que alguien lo reinicie, lo que contradice «opera de 6:00 a 24:00 sin "
        "reinicios». En una billetera, horas sin transferir ni pagar implican pérdida de confianza y reclamos.",
        "- Medio: login y transferencias tienen costos fijos (PBKDF2 ≈ 100 ms, antifraude 40–120 ms) que dominan el p95; están "
        "lejos del umbral, pero el antifraude real puede ser más lento que el simulado.",
    ],
    "acciones": [
        "1. Limitar la concurrencia (uvicorn --limit-concurrency o un balanceador con cola acotada) para rechazar el exceso con 503 "
        "rápido en vez de encolar sin fin: degradación controlada y recuperación automática.",
        "2. Transacciones cortas con commit/rollback garantizado dentro de la operación (with conexión:, BEGIN IMMEDIATE) y un "
        "busy_timeout menor; reportar DEF-05 a desarrollo.",
        "3. Para producción, base de datos con concurrencia de escritura (PostgreSQL + pool de conexiones) y varios workers.",
        "4. Health check sobre /api/salud con reinicio automático mientras se corrige lo anterior.",
        "5. Repetir la resistencia de 18 h y el estrés con escalones de 50 VUs entre 1 000 y 1 200 en un entorno de preproducción.",
    ],
}
