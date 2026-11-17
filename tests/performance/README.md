# Pruebas de rendimiento (Parte 3) · k6

| Archivo | Qué hace |
|---|---|
| `qolqe.js` | Script k6: una iteración = una sesión (login + 6 operaciones ponderadas, pausa de 10–25 s). Escenarios `carga`, `pico`, `estres`, `resistencia`, `humo`. Umbrales del requerimiento como `thresholds`. |
| `datos.py` | Reinicia Qolqe, deja un usuario de carga por VU (900000001…) con S/ 10,000 y 20 deudas cada uno; verifica después que el dinero cuadra (nada a medias ni duplicado). |
| `ejecutar.py` | Orquesta todo: datos → CPU/memoria de Qolqe y k6 (psutil, 1 s) → k6 → verificación → análisis por etapa y por ventanas de 10 s → `graficos.png`. |

## Cómo ejecutar

```bash
# 1) Qolqe sin --reload (un solo proceso) y sin log de accesos
uvicorn qolqe.main:app --port 8000 --no-access-log
# 2) en otra terminal (Python con psutil y matplotlib)
python tests/performance/ejecutar.py carga        # 100 VUs, 13 min
python tests/performance/ejecutar.py pico         # 300 VUs (campaña), 16 min
python tests/performance/ejecutar.py estres       # escalones de 100 VUs (ESCALONES=100,200,...)
python tests/performance/ejecutar.py resistencia  # 100 VUs, 33 min
python tests/performance/ejecutar.py humo         # 2 VUs, 1 min (demo / prueba rápida)
```

Mientras corre, el dashboard en vivo de k6 está en http://localhost:5665.

## Resultados (`resultados/<escenario>/`)

| Archivo | Contenido |
|---|---|
| `reporte_k6.html` | Reporte de la herramienta (dashboard k6 exportado) |
| `resumen_k6.json` | Resumen de k6 con el estado de cada umbral |
| `analisis.json` | p95, p99, throughput, errores técnicos y de negocio por etapa; recursos; integridad del dinero |
| `serie_10s.csv` | Serie temporal cada 10 s (VUs, rps, p95, % errores) |
| `recursos.csv` | CPU y memoria de Qolqe y de k6 cada 1 s, más la CPU total del equipo |
| `graficos.png` | Tiempo de respuesta, throughput, errores y recursos a lo largo de la prueba |
