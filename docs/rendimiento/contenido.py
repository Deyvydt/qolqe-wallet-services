"""Texto del Informe de Pruebas de Rendimiento (lo usa generar_informe.py)."""
import json
from pathlib import Path

RES = Path(__file__).resolve().parents[2] / "tests" / "performance" / "resultados"


def cargar(escenario):
    return json.loads((RES / escenario / "analisis.json").read_text(encoding="utf-8"))


SECCIONES = {
    "contexto": [
        "Qolqe Wallet prepara la campaña «Quincena Qolqe» (días 15 y último de cada mes, 12:00–12:15), en la que espera "
        "el triple de usuarios simultáneos que en la hora punta (12:00–13:00, unas 3 000 sesiones/h). El negocio necesita "
        "saber si cumple en hora punta y en el pico de la campaña, y hasta cuántos usuarios simultáneos puede crecer.",
    ],
    "flujos": [
        "Se simula la sesión completa (login + 6 operaciones con la mezcla del requerimiento). Dentro de ella, los flujos "
        "críticos y su criterio:",
        "- Iniciar sesión (100 % de las sesiones) · frecuencia y riesgo: es la puerta de entrada y es costoso en CPU "
        "(PIN con PBKDF2-SHA256 de 200 000 iteraciones). En la campaña, la mayoría inicia sesión en 5 minutos.",
        "- Transferir a otro usuario Qolqe (15 %) · impacto en el dinero y riesgo: mueve saldo entre dos cuentas, "
        "consulta el antifraude (40–120 ms) y no puede quedar a medias ni aplicarse dos veces.",
        "- Consultar saldo y perfil (30 %) · frecuencia: la operación más usada.",
        "- Recargar celular (10 %) y pagar servicios (4 %) · impacto en el dinero: junto con transferir forman el grupo "
        "«operaciones de dinero» con umbral propio de 1.5 s. Pagar servicios es además el módulo del grupo (G2).",
        "Movimientos, contactos, deudas y «otras» también se ejecutan en su proporción, para que la carga sobre la BD sea realista.",
    ],
    "capa": [
        "El requerimiento habla de tiempos de respuesta de operaciones del servidor (consultas, login, "
        "operaciones de dinero), de la tasa de fallas y del throughput. Todo eso se mide en la API REST, que es la que "
        "atiende a la web y a cualquier canal. La interfaz web solo agrega el tiempo de render del navegador, que no "
        "consume recursos de Qolqe; probarla con navegadores reales (k6 browser) multiplicaría el consumo de CPU del "
        "generador en una sola laptop sin cambiar la conclusión.",
    ],
    "herramienta": [
        "Elegimos Grafana k6 v2.1.0, ejecutado por consola (k6 run). En clase se trabajó con JMeter; el enunciado deja "
        "la herramienta a libre elección y para este proyecto k6 tiene ventajas concretas:",
        "- Umbrales como código: los criterios del requerimiento (p(95)<800, p(95)<1500, error<1 %) son thresholds del "
        "script; k6 devuelve PASA/FALLA (código de salida 99 si falla), igual que un quality gate del pipeline de la Parte 2.",
        "- Consumo bajo del generador: cada VU es una goroutine de Go, no un hilo de Java. En entorno local la herramienta "
        "compite por CPU con Qolqe y el resultado no vale si pasa ~80 %; medimos el CPU de k6 en cada prueba (máx. en sección 7).",
        "- Script legible y versionado en git (tests/performance/qolqe.js), revisable en un PR, frente al XML del .jmx.",
        "- Etiquetas por operación y por etapa: permiten p95 por tipo (consulta/dinero) y por escalón de usuarios.",
        "- Think time aleatorio y mezcla ponderada en pocas líneas de JavaScript, sin plugins.",
        "Comparación con alternativas:",
        "@TABLA_HERRAMIENTAS",
        "Limitaciones de k6: no es un navegador real (solo HTTP), su JavaScript no es Node (sin npm sin empaquetar), "
        "no mide CPU/memoria del servidor (lo medimos con psutil) y su CSV crudo es grande (lo resumimos con Python).",
    ],
    "origen": [
        "- VUs hora punta = 3 000 sesiones/h × 120 s por sesión ÷ 3 600 s/h = 100 usuarios simultáneos (ley de Little: "
        "concurrencia = tasa de llegada × tiempo en el sistema).",
        "- VUs campaña = 3 × 100 = 300 («el triple de usuarios simultáneos»). Ramp-up 300 s porque «la mayoría inicia sesión "
        "en los primeros 5 minutos»; duración total 900 s = la ventana 12:00–12:15.",
        "- Ramp-up de la carga = 120 s: una sesión dura 2 min, así las sesiones quedan escalonadas como llegadas reales "
        "y no sincronizadas.",
        "- Iteración k6 = una sesión: login + 6 operaciones, pausa uniforme de 10–25 s entre cada una (media 17.5 s ≈ 18 s). "
        "6 pausas × 17.5 s ≈ 105 s + tiempos de respuesta ≈ 2 min de sesión.",
        "- Distribución: cada una de las 6 operaciones se sortea con los pesos de la tabla del requerimiento (30/15/15/10/10/6/4/10). "
        "«Otras» reparte entre límites, alertas, solicitudes, dispositivos y sesiones.",
        "- Throughput esperado = 3 000 sesiones/h ≈ 0.83 sesiones/s; en peticiones ≈ 7.9 req/s con 100 VUs (saldo y "
        "perfil son 2 peticiones; pagar es consultar + pagar).",
        "- Estrés: escalones de +200 VUs (200 → 1 600), 60 s de subida + 120 s sostenidos (más que una sesión) para ver en "
        "qué escalón deja de cumplir.",
        "- Resistencia: Qolqe opera 18 h al día sin reinicios; se ejecuta 30 min de estado estable a 100 VUs (versión acotada) "
        "para medir la tendencia de la memoria y del p95.",
        "- Datos: un usuario distinto por VU (VU n → celular 9000000n, PIN 2580), saldo S/ 10 000, 20 deudas propias de "
        "S/ 10 (AGUA 40000nnnnn); transferencias de S/ 1 a otro usuario de carga y recargas de S/ 5 a números aleatorios, "
        "para no tocar el límite diario (S/ 2 000) ni el máximo de 5 recargas diarias al mismo número.",
    ],
    "supuestos": [
        "- «Fallar»: solo cuenta como falla técnica una respuesta 5xx, un timeout o una conexión rechazada. Un 4xx es una regla "
        "de negocio (p. ej. LIMITE_DIARIO_EXCEDIDO) y, según el enunciado, indica un problema de datos: se reporta aparte "
        "(error_negocio) y no se suma al 1 %.",
        "- «Sin acumular retrasos» no trae número: se convierte en throughput ≥ 3 000 sesiones/h en estado estable y una "
        "duración de sesión que no crece (p95 de la iteración ≈ 2 min).",
        "- «Degradación razonable» en la campaña no es medible tal como está escrita (falta percentil y valor). Supuesto: "
        "se exigen los mismos umbrales que en hora punta y se reporta cuánto se degradan; lo innegociable es la integridad.",
        "- «Ninguna operación de dinero a medias ni dos veces»: no es un umbral de tiempo sino de integridad. Se verifica "
        "al final de cada prueba en la BD: por cada usuario, saldo final − saldo inicial = suma de sus movimientos nuevos; "
        "toda transferencia enviada tiene su recibida; ningún código de operación ni deuda pagada se repite.",
        "- El throughput mínimo y los percentiles se evalúan en el estado estable (sin rampa ni bajada).",
        "- Pico: el requerimiento no dice cuántos usuarios hay a las 11:59; se modela desde 0 hasta 300 en 5 min (lo más exigente).",
    ],
    "entorno": [
        "Local: Qolqe (uvicorn, 1 proceso, sin --reload y sin log de accesos) y k6 en la misma laptop. "
        "Intel Core i5-11400H (6 núcleos / 12 hilos, 2.7 GHz), 32 GB de RAM, Windows 11 Pro, Python 3.12, SQLite en SSD. "
        "Se eligió local porque Docker Desktop no estaba disponible y evita la latencia de red de Codespaces.",
    ],
    "medicion": [
        "Con psutil, sobre el proceso de Qolqe (PID del puerto 8000) y sobre el proceso de k6, cada 1 s, en "
        "resultados/<prueba>/recursos.csv (hora, CPU % de un núcleo, memoria RSS en MB) más el CPU total del equipo. "
        "ejecutar.py registra la hora de inicio y fin de cada prueba (analisis.json) para cruzar recursos y resultados.",
    ],
    "limitaciones": [
        "- Los resultados son una línea base relativa, no la capacidad de producción: hardware de laptop, SQLite local, "
        "sin red real entre cliente y servidor (latencia de red ≈ 0).",
        "- k6 y Qolqe compiten por la misma CPU; se vigiló que el CPU total del equipo no pase de ~80 %.",
        "- La CPU de un proceso se reporta en % de un núcleo (100 % = un núcleo completo; puede superar 100 % con varios hilos).",
        "- Los usuarios 201 a 1 600 se crearon como copia de los usuarios de carga, sin el historial de 1 000 movimientos "
        "que traen los 200 originales: sus consultas de movimientos son más livianas.",
    ],
    "diferencias": ["@DIFERENCIAS"],
}

TABLA_HERRAMIENTAS = [
    ["Criterio", "k6", "JMeter", "Gatling", "Locust", "Artillery"],
    ["Scripts", "JavaScript", "XML (.jmx) desde GUI; Groovy", "Scala/Java/Kotlin", "Python", "YAML + JS"],
    ["Recursos por VU", "Bajo (goroutine)", "Alto (hilo JVM por usuario)", "Muy bajo (asíncrono)",
     "Bajo, pero 1 núcleo por proceso (GIL)", "Medio (1 event loop)"],
    ["Umbrales pass/fail", "Nativos (thresholds)", "Aserciones por muestra; SLA global con plugins", "Nativos (assertions)",
     "Se programan", "Nativos (ensure)"],
    ["Reportes", "Consola, dashboard HTML, CSV/JSON", "Dashboard HTML", "HTML muy completo", "Web UI, CSV", "Consola, JSON"],
    ["CI/CD", "Binario único + código de salida", "Modo no-GUI, más pesado", "Maven/Gradle", "--headless", "npm"],
    ["GUI", "No (CLI)", "Sí, completa", "Solo grabador", "Web UI", "No"],
    ["Curva de aprendizaje", "Baja (JS)", "Media", "Media-alta", "Baja (Python)", "Baja"],
]

TABLA_TIPOS = [
    ["Carga", "☒ Sí / ☐ No", "Responde «¿cumplimos en hora punta?»: 100 VUs (3 000 sesiones/h) con los umbrales del requerimiento."],
    ["Estrés", "☒ Sí / ☐ No", "Responde «¿hasta cuántos usuarios simultáneos podemos crecer antes de dejar de cumplir?»: "
     "escalones de +200 VUs hasta 1 600."],
    ["Pico (spike)", "☒ Sí / ☐ No", "Responde «¿cumplimos en el pico de la campaña?»: 0 → 300 VUs en 5 min y 10 min sostenidos "
     "(ventana 12:00–12:15), verificando que ninguna operación de dinero quede a medias ni duplicada."],
    ["Resistencia (soak)", "☒ Sí / ☐ No", "«Qolqe opera de 6:00 a 24:00 sin reinicios»: 18 h sin reiniciar pueden revelar "
     "fugas de memoria o crecimiento de tablas (sesiones, movimientos). Se ejecutó una versión acotada de 30 min a 100 VUs "
     "y se mide la tendencia; la de 18 h queda recomendada en preproducción."],
]

TABLA_MODELO = [
    ["Parámetro", "Carga (hora punta)", "Pico (campaña)", "Estrés", "Resistencia"],
    ["VUs", "100", "300", "200 → 1 600 (+200)", "100"],
    ["Ramp-up (s)", "120", "300", "60 por escalón", "120"],
    ["Duración (s)", "780 (120 + 600 estable + 60 bajada)", "960 (300 + 600 + 60)", "1 500 (8 × 180 + 60)",
     "1 980 (120 + 1 800 + 60)"],
    ["Think time (ms)", "10 000–25 000 (media 17 500)", "10 000–25 000", "10 000–25 000", "10 000–25 000"],
    ["Distribución de operaciones (%)", "Saldo/perfil 30 · Movimientos 15 · Transferir 15 · Contactos 10 · Recargar 10 · "
     "Deudas 6 · Pagar 4 · Otras 10 (+ 1 login por sesión)", "Igual", "Igual", "Igual"],
]

TABLA_CRITERIOS = [
    ["Tiempo de respuesta", "Consultas + login: p95 < 800 ms · Dinero (transferir, recargar, pagar): p95 < 1 500 ms; "
     "con 100 VUs (carga) y 300 VUs (pico), en estado estable", "Requerimiento, «Lo que esperamos del servicio» (puntos 1 y 2)"],
    ["Tasa de error máxima", "Errores técnicos (5xx, timeout, conexión) < 1 % de las peticiones; 4xx de negocio se "
     "reportan aparte. Integridad del dinero: 0 operaciones a medias o duplicadas", "Requerimiento, punto 3 y 4; "
     "enunciado §5 (422 = datos)"],
    ["Throughput mínimo", "≥ 3 000 sesiones/h (≈ 0.83 sesiones/s, ≈ 7.9 req/s) con 100 VUs, sin que la duración de la "
     "sesión crezca", "Requerimiento, «3 000 sesiones por hora» y «sin acumular retrasos»"],
]

# Las secciones 7 y 8 se completan con los resultados (ver resultados.py)
from resultados import PRUEBAS, ANALISIS, DIFERENCIAS  # noqa: E402

SECCIONES["diferencias"] = DIFERENCIAS
