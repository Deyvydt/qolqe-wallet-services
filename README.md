# Qolqe Wallet · Pruebas del módulo G2 (Pago de servicios y afiliaciones)

Proyecto 2 del curso **CS5383 Pruebas y Verificación de Software**. **Qolqe Wallet** es una billetera digital **ficticia** (FastAPI + SQLite) que se usa como sistema bajo prueba (SUT). Este repositorio contiene las pruebas del grupo **G2** (trabajo individual): API, web E2E, rendimiento y el pipeline de CI/CD.

> ⚠️ **No se modifica el código de `qolqe/`**: el trabajo es probarlo, no repararlo. Todos los datos son ficticios.

| Enlace | Qué hay |
|---|---|
| **Reportes publicados (GitHub Pages)** | https://deyvydt.github.io/qolqe-wallet-services/ |
| Informe final (las 3 partes) | [`docs/informe.md`](docs/informe.md) |
| Defectos DEF-01…06 | [`docs/defectos.md`](docs/defectos.md) |
| Matriz de trazabilidad (último run publicado) | [`docs/trazabilidad.md`](docs/trazabilidad.md) |
| Historial de ejecuciones en Qase | [`docs/trazabilidad-qase.md`](docs/trazabilidad-qase.md) |
| Triaje de fallas con IA (validación) | [`docs/ia/validacion_triaje.md`](docs/ia/validacion_triaje.md) |
| Informe de rendimiento | [`docs/rendimiento/Informe_Rendimiento_G2.docx`](docs/rendimiento/Informe_Rendimiento_G2.docx) · herramienta: [`docs/rendimiento/herramienta.md`](docs/rendimiento/herramienta.md) |
| Requisitos (HU, CA, reglas) | [`docs/requisitos.md`](docs/requisitos.md) |

## Resumen

| Parte | Herramienta | Alcance | Resultado |
|---|---|---|---|
| 1 · API | pytest + pytest-bdd + httpx · Schemathesis | 124 escenarios sobre E1–E10 (72 funcionales / 52 técnicos) | 114 pasan · 10 fallos esperados (DEF-01…04) · 0 nuevos · 0 errores 500 |
| 2 · Web | Robot Framework + Browser + robotframework-gherkin-parser | 27 escenarios Gherkin + 3 `.robot` (núcleo y G2) | 28 pasan · 2 SKIP por DEF-02 (DEF-06 intermitente) |
| 2 · CI/CD | GitHub Actions + Pages + Qase | `contrato → (api ‖ web ‖ rendimiento-humo) → quality-gate → reportes` | Ver [informe §5](docs/informe.md#5-pipeline-cicd-y-quality-gates) |
| 3 · Rendimiento | k6 | Carga, pico, estrés y resistencia | Cumple hasta ~1 000 VUs; colapso en 1 200 (DEF-05) |

## Estructura del repositorio

```
qolqe/                        App bajo prueba (NO modificar)
features/
  api/                        Escenarios Gherkin de la API, uno por grupo de endpoints (g2_*.feature)
  e2e/                        Escenarios Gherkin web: nucleo_comun.feature, g2_servicios.feature
    __init__.robot            Fixtures comunes de los escenarios web
    pasos/                    Frase Gherkin → acciones de los Page Objects (nucleo.resource, g2.resource)
tests/
  conftest.py                 BD propia de pruebas, xfail por DEF y reportes en la terminal
  test_humo.py                Prueba de humo (la app responde)
  api/                        Pasos de pytest-bdd (conftest.py) y test_g2_pago_servicios.py
  tecnico/                    Schemathesis desde el contrato OpenAPI y su clasificador
  e2e/                        Casos .robot, pages/ (Page Objects) y resources/Comun.resource
  performance/                Script k6 (qolqe.js), datos.py y ejecutar.py
    resultados/               Evidencia por escenario: carga, pico, estres, resistencia
  triaje/                     Casos etiquetados y pruebas unitarias del triaje de fallas
.github/
  workflows/                  pruebas.yml (orquestador), _api.yml, _web.yml
  scripts/                    resumen.py, trazabilidad.py, portada.py, triaje_ia.py, validar_triaje.py
docs/                         Informe, requisitos, defectos, trazabilidad, ia/, rendimiento/
```

## Cómo ejecutar

### Instalación (una sola vez)

```bash
python -m venv .venv
.venv\Scripts\activate                      # macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt         # API, contrato y rendimiento (psutil, matplotlib)
pip install -r requirements-e2e.txt         # web: Robot Framework, Browser, gherkin-parser
rfbrowser init chromium                     # descarga Playwright + Chromium (requiere Node 20/22)
```

k6 se instala aparte (binario): https://grafana.com/docs/k6/latest/set-up/install-k6/

### Parte 1 · API (no hace falta levantar la app)

| Comando | Qué ejecuta |
|---|---|
| `pytest` | Todo: Gherkin de API + Schemathesis + humo + pruebas unitarias del triaje, y al final el **reporte total endpoint × tipo × resultado** |
| `pytest tests/api tests/tecnico tests/test_humo.py` | Solo los 124 escenarios de API de G2 |
| `pytest -m E3` | Un endpoint (`E1`…`E10`) |
| `pytest -m "tecnico and E7"` | Un tipo dentro de un endpoint (`funcional` / `tecnico`) |
| `pytest -m HU-G2-02` | Una historia (sirve cualquier etiqueta registrada en `pytest.ini`) |
| `pytest -m schemathesis` | Solo la prueba de contrato |
| `pytest --html=reportes/pytest/reporte.html --self-contained-html` | Todo, con reporte HTML |

El reporte técnico de Schemathesis queda en `reportes/schemathesis/ultimo/reporte.html`. Por defecto Schemathesis es determinista; para casos nuevos al azar: `$env:SCHEMATHESIS_MODO="aleatorio"; pytest -m schemathesis`.

### Parte 2 · Web E2E (con la app levantada)

```bash
# Terminal 1
uvicorn qolqe.main:app --port 8000
# Terminal 2 (en PowerShell, antes: $env:PYTHONIOENCODING='utf-8')
robot --name "Web E2E" --parser GherkinParser --language es --skiponfailure defecto \
      --outputdir reportes/web -v URL:http://127.0.0.1:8000 tests/e2e features/e2e
```

Opciones: `-v EVIDENCIA:sin` (sin capturas), `-v HEADLESS:False` (ver el navegador), `--include HU-G2-02` o `--include CP-W01` (filtrar). Reportes: `reportes/web/report.html` y `log.html`. Detalle en [`tests/e2e/README.md`](tests/e2e/README.md).

### Parte 3 · Rendimiento (con la app levantada, sin `--reload`)

```bash
uvicorn qolqe.main:app --port 8000 --no-access-log
python tests/performance/ejecutar.py humo          # 2 VUs, ~1 min
python tests/performance/ejecutar.py carga         # 100 VUs, 13 min
python tests/performance/ejecutar.py pico          # 300 VUs, 16 min
python tests/performance/ejecutar.py estres        # escalones de +200 VUs hasta 1 600
python tests/performance/ejecutar.py resistencia   # 100 VUs, 33 min
```

Resultados en `tests/performance/resultados/<escenario>/` (ver [`tests/performance/README.md`](tests/performance/README.md)). El informe Word se regenera con `python docs/rendimiento/generar_informe.py docs/rendimiento/Template_Informe_Rendimiento.docx`.

### Pipeline y herramientas auxiliares

| Comando | Para qué |
|---|---|
| GitHub → *Actions* → *Pruebas G2* → *Run workflow* | Ejecución manual del pipeline |
| `python .github/scripts/trazabilidad.py --api reportes/api/junit.xml --web reportes/web/output.xml --salida-md docs/trazabilidad.md` | Regenerar la matriz de trazabilidad desde reportes locales |
| `python .github/scripts/triaje_ia.py reportes/api/junit.xml reportes/web/output.xml --offline` | Triaje de las fallas con la línea base por reglas (sin red) |
| `python .github/scripts/validar_triaje.py --destino docs` | Validar el triaje contra los casos etiquetados (con `GITHUB_TOKEN` evalúa también el modelo) |

---

# Referencia del sistema bajo prueba (Qolqe)

## Requisitos

- Python **3.11 o superior** (recomendado 3.12)
- Git

## Instalación y ejecución

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn qolqe.main:app --reload
```

| Recurso | URL |
|---|---|
| Interfaz web | http://localhost:8000 |
| Documentación de la API (Swagger / OpenAPI) | http://localhost:8000/docs |
| Contrato OpenAPI en JSON | http://localhost:8000/openapi.json |
| Estado del servicio | http://localhost:8000/api/salud |

La primera vez la app crea la base de datos en `datos/` (tarda unos segundos porque genera los usuarios de carga). Para empezar desde cero, borren la carpeta `datos/` o usen `POST /api/pruebas/reiniciar`.

> Ejecuten **un solo proceso** de uvicorn (sin `--workers`). El reloj de pruebas vive en memoria.

### Variables de entorno (opcionales)

| Variable | Por defecto | Uso |
|---|---|---|
| `QOLQE_BD` | `datos/qolqe.db` | Ruta de la base de datos |
| `QOLQE_MODO_PRUEBA` | `1` | `1` habilita la API de soporte para pruebas (`/api/pruebas/*`) |
| `QOLQE_MINUTOS_TOKEN` | `30` | Vigencia del token JWT |
| `QOLQE_CLAVE_SECRETA` | clave de desarrollo | Firma de los tokens |

---

## Funcionalidades

| Módulo | Pantalla | Endpoints principales |
|---|---|---|
| **Núcleo:** registro, sesión, perfil, saldo y transferencias | `/registro`, `/login`, `/inicio`, `/perfil`, `/transferir` | `POST /api/usuarios` · `POST /api/auth/login` · `POST /api/auth/logout` · `GET/PUT /api/cuentas/me` · `POST /api/cuentas/me/cierre` · `GET /api/cuentas/me/saldo` · `POST /api/transferencias` · `GET /api/transferencias/comision` |
| **G1** Recargas y recargas programadas | `/recargas` | `GET /api/recargas/configuracion` · `GET/POST /api/recargas` · `GET/POST /api/recargas/programadas` · `PUT/DELETE /api/recargas/programadas/{id}` · `POST /api/recargas/programadas/{id}/pausar` · `POST .../reanudar` |
| **G2** Pago de servicios y afiliaciones | `/servicios` | `GET /api/servicios/empresas` · `GET /api/servicios/deudas` · `GET/POST /api/servicios/pagos` · `GET /api/servicios/pagos/{codigo}` · `GET/POST /api/servicios/afiliaciones` · `PUT/DELETE /api/servicios/afiliaciones/{id}` |
| **G3** Historial y categorías | `/historial` | `GET /api/movimientos` · `GET /api/movimientos/recientes` · `GET /api/movimientos/{codigo}` · `PUT /api/movimientos/{codigo}/clasificacion` · `GET /api/movimientos/exportar` · `GET/POST /api/categorias` · `PUT/DELETE /api/categorias/{id}` |
| **G4** Contactos y solicitudes de dinero | `/contactos`, `/solicitudes` | `GET/POST /api/contactos` · `PUT/DELETE /api/contactos/{id}` · `GET/POST /api/solicitudes` · `POST /api/solicitudes/{id}/aceptar` · `.../rechazar` · `.../cancelar` |
| **G5** Límites y alertas de consumo | `/limites` | `GET/PUT /api/limites` · `GET/POST /api/limites/alertas` · `PUT/DELETE /api/limites/alertas/{id}` |
| **G6** Seguridad, dispositivos y sesiones | `/seguridad`, `/desbloqueo` | `PUT /api/seguridad/pin` · `POST /api/seguridad/desbloqueo/solicitar` · `.../confirmar` · `GET/POST /api/seguridad/dispositivos` · `PUT/DELETE /api/seguridad/dispositivos/{id}` · `GET/DELETE /api/seguridad/sesiones` · `DELETE /api/seguridad/sesiones/{id}` |

Las **historias de usuario, criterios de aceptación y reglas de negocio** están en `docs/requisitos.md`. Las funciones que las implementan, sin base de datos ni red, están en `qolqe/reglas/`:

```
qolqe/reglas/nucleo.py      qolqe/reglas/servicios.py   qolqe/reglas/contactos.py
qolqe/reglas/recargas.py    qolqe/reglas/historial.py   qolqe/reglas/limites.py
qolqe/reglas/seguridad.py
```

### Autenticación

```http
POST /api/auth/login
Content-Type: application/json

{"celular": "987654321", "pin": "4826"}
```

Opcionalmente se envía `"dispositivo_id"` (identificador de un dispositivo de confianza, ver G6). La respuesta incluye `access_token` y `sesion_id`. Envíen el token en cada solicitud protegida:

```http
Authorization: Bearer <access_token>
```

- Cada inicio de sesión crea una **sesión**; el token vence a los **30 minutos**.
- `POST /api/auth/logout` cierra la sesión. Las sesiones activas se consultan y cierran en `/api/seguridad/sesiones`.
- Tras **3 intentos fallidos** consecutivos, la cuenta se bloquea 15 minutos (`423`).

### Convenciones de la API

- **Montos:** se envían como número o texto decimal (`100`, `"100.50"`) y se devuelven como texto con 2 decimales (`"100.50"`).
- **Fechas:** hora de Lima, formato `AAAA-MM-DDTHH:MM:SS`.
- **Errores:** todos responden con un código estable y un mensaje:

```json
{"codigo": "SALDO_INSUFICIENTE", "detail": "Saldo insuficiente para realizar la operación"}
```

| HTTP | Significado | Ejemplos de `codigo` |
|---|---|---|
| 204 | Eliminación o cierre correcto, sin contenido | |
| 401 | Sin token, token inválido, vencido o de una sesión cerrada, o credenciales incorrectas | `NO_AUTENTICADO`, `CREDENCIALES_INVALIDAS`, `CUENTA_CERRADA` |
| 404 | Recurso inexistente **o de otro usuario** | `DESTINO_NO_REGISTRADO`, `CONTACTO_NO_ENCONTRADO`, `SIN_DEUDA_PENDIENTE` |
| 409 | Conflicto con el estado actual | `CELULAR_REGISTRADO`, `ALIAS_DUPLICADO`, `DEUDA_YA_PAGADA`, `ESTADO_INVALIDO` |
| 422 | Regla de negocio o datos inválidos | `MONTO_INVALIDO`, `SALDO_INSUFICIENTE`, `LIMITE_DIARIO_EXCEDIDO`, `FILTRO_INVALIDO`, `SOLICITUD_INVALIDA` |
| 423 | Cuenta bloqueada | `CUENTA_BLOQUEADA` |

El contrato completo está en `/docs` (Swagger) y en `/openapi.json`. Cada operación indica su historia de usuario, los esquemas de entrada y salida con sus restricciones, y todos los códigos de error que puede devolver, con un ejemplo por código.

---

## Datos de prueba

Se restauran con `POST /api/pruebas/reiniciar`. Las fechas de las deudas y algunos movimientos se calculan **respecto del día actual** del reloj de la app.

### Usuarios

| Usuario | Celular | PIN | Correo | Saldo | Notas |
|---|---|---|---|---|---|
| Ana Torres Quispe | 987654321 | 4826 | ana.torres@correo.pe | S/ 1,500.00 | Usuario principal de ejemplo (ver abajo). Ha usado otros PIN antes |
| Bruno Díaz Mendoza | 912345678 | 7391 | bruno.diaz@correo.pe | S/ 800.00 | Tiene a Ana como contacto |
| Carla Ramos Huamán | 956781234 | 5917 | carla.ramos@correo.pe | S/ 50.00 | Saldo bajo. Tiene a Ana como contacto |
| Diego Salas Paredes | 998877665 | 3604 | diego.salas@correo.pe | S/ 2,500.00 | Límite diario configurado en S/ 1,000. Tiene a Fabián como contacto |
| Elena Vargas Ccori | 923456789 | 8152 | elena.vargas@correo.pe | S/ 300.00 | **Cuenta bloqueada** al reiniciar (para probar el desbloqueo) |
| Fabián Rojas Núñez | 934567812 | 6029 | fabian.rojas@correo.pe | S/ 0.00 | **Cuenta cerrada** |

### Datos de Ana por módulo

| Módulo | Datos |
|---|---|
| G1 | Programada "Mamá" (987111222, S/ 20, día 15, ACTIVA) y "Trabajo" (999000111, S/ 10, día 5, PAUSADA). Una recarga de hoy al 999000111 |
| G2 | Afiliaciones "Luz casa" (ELECTRO 10000001), "Agua depa" (AGUA 2000000008, **débito automático activo**) e "Internet casa" (INTERNET 300000000007) |
| G3 | Historial de unos 60 días. Categorías Comida, Familia y Servicios, con movimientos asignados y una nota |
| G4 | Contactos "Bruno" (favorito) y "Prima Carla". Solicitudes: Bruno le pide S/ 45.00 (pendiente), Carla le pidió S/ 30.00 hace más de 48 horas, y Ana le pide S/ 20.00 a Bruno (pendiente) |
| G5 | Alerta de TRANSFERENCIAS con umbral S/ 300 |
| G6 | Dispositivo de confianza "Celular de Ana" con identificador `a1b2c3d4e5f60718` |

### Usuarios de carga (pruebas de rendimiento)

- Celulares **900000001** a **900000200**, todos con PIN **2580**.
- Saldo S/ 10,000.00 y unos 1,000 movimientos de los últimos 120 días cada uno.

### Deudas de servicios

| Empresa | Suministro | Vencimiento (respecto de hoy) |
|---|---|---|
| ELECTRO | 10000001 | Vence en 10 días |
| ELECTRO | 10000002 | Vence hoy |
| ELECTRO | 10000003 | Venció ayer |
| ELECTRO | 100000009 | Dos periodos: uno venció hace 5 días y otro vence en 25 |
| AGUA | 20000004 | Venció hace 10 días |
| AGUA | 20000005 | Venció hace 30 días |
| AGUA | 2000000008 | Vence en 3 días |
| INTERNET | 300000000006 | Venció hace 60 días |
| INTERNET | 300000000007 | Venció hace 61 días |
| AGUA | 4000000001 a 4000000200 | Venció hace 5 días (para pruebas de carga) |

### Transferencias interbancarias

Usen cualquier CCI de 20 dígitos, por ejemplo `00219300123456789012`.

---

## API de soporte para pruebas

Disponible solo con `QOLQE_MODO_PRUEBA=1`. **No forma parte del producto**: existe para que las pruebas automatizadas sean repetibles.

| Endpoint | Para qué |
|---|---|
| `POST /api/pruebas/reiniciar` | Restaura todos los datos semilla |
| `GET /api/pruebas/reloj` | Ver la fecha y hora de la app |
| `PUT /api/pruebas/reloj` | Fijar (`{"ahora": "2026-11-15T10:00:00"}`) o adelantar (`{"avanzar_minutos": 60}`) el reloj |
| `DELETE /api/pruebas/reloj` | Volver a la hora real |
| `GET /api/pruebas/notificaciones?celular=...` | Ver los SMS simulados enviados a un celular (por ejemplo, el código de desbloqueo) |
| `PUT /api/pruebas/saldo` | Fijar el saldo de un usuario: `{"celular": "...", "saldo": "100.00"}` |
| `POST /api/pruebas/procesar-diario` | Ejecutar el proceso diario (recargas programadas y débitos automáticos) con la fecha del reloj de la app |

> 💡 Para probar el proceso diario: fijen o adelanten el reloj al día que necesiten y luego llamen a `POST /api/pruebas/procesar-diario`.
>
> 💡 Si sus pruebas modifican datos (transferencias, bloqueos, límites), reinicien los datos antes de cada prueba o diseñen datos independientes. Así cumplen la propiedad *Independent* de FIRST.
