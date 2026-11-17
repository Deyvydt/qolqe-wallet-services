# 2. Herramienta seleccionada

Elegimos **k6 v2.1.0** (Grafana k6). Los scripts se escriben en JavaScript y se ejecutan por consola con el executor `ramping-vus`. El dashboard web se exporta a HTML con `K6_WEB_DASHBOARD_EXPORT` y las muestras crudas salen en CSV. El sistema bajo prueba es la API REST de Qolqe Wallet (FastAPI + SQLite).

## 2.1 Por qué k6

- **Los umbrales son código y sirven de criterios de aceptación.** Los requisitos de rendimiento (p. ej. `p(95)<500`, `rate<0.01`) se escriben como `thresholds` en el script. Si alguno no se cumple, k6 termina con un código de salida distinto de 0, así que el requisito funciona como *quality gate* sin tener que revisar los resultados a mano.
- **Scripts versionados y reutilizables en CI.** El script es un archivo `.js` de texto plano que vive en git junto a `tests/` y puede revisarse en un PR. También puede ejecutarse en GitHub Actions como ya hacemos con pytest-bdd y Robot Framework.
- **Bajo consumo de CPU por VU.** Cada VU es una goroutine de Go con un runtime JS liviano, no un hilo del sistema operativo. Esto es importante porque la prueba corre en local y k6 compite por CPU con la app. Si la máquina pasa de ~80 % de CPU, la latencia medida refleja la saturación del equipo de prueba y no la de la API, y el resultado no vale.
- **Etiquetas por operación y por etapa.** Con `tags` cada petición se marca por operación (login, saldo, transferencia) y por etapa de la rampa. Así se calculan percentiles y umbrales por endpoint, no solo un promedio global.
- **Think time y mezcla ponderada fáciles de programar.** El `sleep()` aleatorio y el reparto de operaciones por pesos se escriben con unas pocas líneas de JS, sin plugins.

## 2.2 Comparación con alternativas

| Criterio | **k6** | JMeter | Gatling | Locust | Artillery |
|---|---|---|---|---|---|
| Lenguaje de scripts | JavaScript (ES6) | Plan XML (`.jmx`) desde la GUI; Groovy para lógica | Scala / Java / Kotlin (DSL) | Python | YAML + hooks en JS |
| Recursos por VU | Bajo (goroutine) | Alto (un hilo de JVM por usuario) | Muy bajo (asíncrono, Netty) | Bajo por greenlet, pero 1 núcleo por proceso | Medio (event loop de Node, 1 núcleo) |
| Modelo de concurrencia | VUs sobre goroutines; executors por VUs o por tasa de llegada | Thread groups (hilos bloqueantes) | Usuarios virtuales asíncronos, modelos abierto y cerrado | gevent; con el GIL hacen falta varios procesos/workers para escalar | Fases de tasa de llegada (modelo abierto) |
| Umbrales pass/fail nativos | Sí (`thresholds`, código de salida) | Solo aserciones por muestra; el SLA global requiere plugins o Taurus | Sí (`assertions`) | No nativo; se programa con event hooks | Sí (`ensure`) |
| Reportes | Resumen en consola, dashboard web/HTML, CSV/JSON | Dashboard HTML, listeners | Informe HTML muy completo | Web UI en vivo, CSV, HTML | Consola, JSON; HTML limitado |
| Integración CI | Muy simple (binario único + código de salida) | Posible en modo no-GUI, pero más pesada | Buena (Maven/Gradle/sbt) | Buena (`--headless`) | Buena (npm) |
| Curva de aprendizaje | Baja si se sabe JS | Media; muchos conceptos de GUI | Media-alta (DSL de JVM) | Baja; **es Python, como el equipo** | Baja |
| GUI | No (CLI; k6 Studio aparte para grabar) | Sí, completa y con muchos plugins | Solo el grabador | Web UI | No |

**Conclusión de la comparación.** Locust era la opción más natural por el lenguaje, pero por el GIL un proceso usa un solo núcleo y para subir la carga hay que levantar varios workers, lo que en una sola máquina le quita aún más CPU a la API. JMeter ofrece GUI y plugins, pero consume mucha memoria por hilo y sus `.jmx` en XML son difíciles de revisar en git. Gatling es igual de eficiente, pero exige el ecosistema JVM (Scala/Java/Kotlin), que el equipo no usa. Artillery es liviano, pero lo limita un único event loop y sus reportes son más pobres.

## 2.3 Limitaciones de k6

- **No es un navegador real.** Por defecto solo genera tráfico HTTP: no renderiza ni ejecuta el JS del frontend. Para el alcance de esta prueba, que es la API, esto no es un problema.
- **Su JavaScript no es Node.js.** Corre sobre un runtime propio, así que los módulos npm no funcionan sin empaquetarlos antes (p. ej. con webpack o esbuild). Solo se dispone de los módulos `k6/*` y de las librerías de jslib.
- **No mide recursos del servidor.** k6 solo ve el lado del cliente (latencias, errores, throughput). El uso de CPU y memoria de la API y del propio generador de carga lo medimos aparte con `psutil`.
- **El CSV crudo es grande.** Guarda una fila por métrica y por petición, y en una prueba larga llega a cientos de MB. Hay que post-procesarlo (agregarlo con Python) y no conviene versionarlo.

**En resumen:** k6 es la opción que mejor equilibra bajo consumo en una máquina compartida, criterios de aceptación escritos como umbrales versionables y una integración directa con nuestro pipeline de GitHub Actions.
