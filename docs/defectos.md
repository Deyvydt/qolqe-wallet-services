<!-- QUÉ ES: reporte de los defectos encontrados por las pruebas (plantilla del curso, llenada).
     Cada DEF tiene regla rota, severidad, pasos para reproducir, esperado vs obtenido y la
     prueba que lo detecta. Al final están las observaciones de Schemathesis (OBS). -->

# Reporte de defectos · Módulo G2 Pago de servicios

Entorno común: Qolqe Wallet 1.0.0 (FastAPI), Python 3.12, Windows 11, `QOLQE_MODO_PRUEBA=1`. Pruebas de API con pytest-bdd + httpx (TestClient). Datos semilla restaurados con `POST /api/pruebas/reiniciar`.

| ID | Título | Regla | Severidad | Prioridad | Pruebas que fallan |
|---|---|---|---|---|---|
| DEF-01 | Se acepta un suministro de 13 dígitos | R-G2-01 | Baja | Media | 1 |
| DEF-02 | Los días de atraso se cuentan con un día de más, así que se cobra mora el mismo día del vencimiento | R-G2-03 | **Alta** | **Alta** | 5 |
| DEF-03 | Una deuda con 60 días de atraso pasa a cobranza y no se puede pagar | R-G2-04 | **Alta** | **Alta** | 2 |
| DEF-04 | El débito automático paga deudas ya vencidas antes de activarlo, y sin mora | HU-G2-05 CA4 | Media | Media | 1 |
| DEF-05 | Con ~1 200 usuarios simultáneos el servicio colapsa y no se recupera sin reinicio (rendimiento) | Requerimiento «Quincena Qolqe» | **Alta** | Media | estrés |
| DEF-06 | La API responde antes de guardar los cambios: tras un login correcto la 1.ª petición puede dar 401 y las listas se repintan con datos viejos | Consistencia (login, afiliar, desafiliar, pagar) | **Alta** | **Alta** | 3 web (intermitente) |
| DEF-07 | Cerrar sesión no invalida el token | HU-N-03 CA1 | **Alta** | **Alta** | 1 |
| DEF-08 | Se acepta un PIN en secuencia descendente (`4321`) | RN-03 | Media | Media | 1 |
| DEF-09 | Un login exitoso no reinicia el conteo de intentos fallidos | RN-04 | Media | Media | 1 |
| DEF-10 | Se puede transferir a una cuenta cerrada | RN-07 · HU-N-06 CA4 | **Alta** | **Alta** | 1 |
| DEF-11 | La comisión interbancaria redondea "al par" y no con redondeo comercial | RN-09 | Baja | Baja | 1 |
| DEF-12 | El saldo puede quedar negativo: no se valida que cubra la comisión interbancaria | RN-08 | **Alta** | **Alta** | 1 |
| DEF-13 | Las transferencias interbancarias no cuentan para el límite diario | RN-06 | **Alta** | **Alta** | 1 |
| DEF-14 | Transferencias simultáneas superan el límite diario | RN-06 · HU-N-07 CA5 | **Alta** | **Alta** | 1 |

---

## DEF-01: Se acepta un código de suministro de 13 dígitos

| Campo | Valor |
|---|---|
| Módulo / regla | G2 · HU-G2-01 CA1 · HU-G2-03 CA1 · R-G2-01 (8 a 12 dígitos) |
| Severidad | Baja |
| Prioridad | Media |
| Entorno | Ver arriba |
| Pruebas que lo detectan | `tests/api/test_g2_pago_servicios.py::test_longitud_del_código_de_suministro_rg201_8_a_12_dígitos[13 digitos (invalido)...]` (E2) y `test_el_suministro_de_la_afiliación_cumple_rg201[13 digitos (invalido)...]` (E7: `POST /api/servicios/afiliaciones` con 13 dígitos responde 404 `SUMINISTRO_NO_ENCONTRADO` en vez de 422 `AFILIACION_INVALIDA`; misma causa: `validar_suministro` permite 12 + 1) |

**Pasos para reproducir**
1. Iniciar sesión como Ana (987654321 / 4826).
2. `GET /api/servicios/deudas?empresa=ELECTRO&suministro=1000000010000` (13 dígitos).

**Resultado esperado:** 422 `SUMINISTRO_INVALIDO`.

**Resultado obtenido:** 404 `SIN_DEUDA_PENDIENTE`. El dato inválido pasa la validación. Lo mismo ocurre al afiliar un servicio.

**Evidencia:** `{"codigo":"SIN_DEUDA_PENDIENTE","detail":"El suministro no tiene deudas pendientes"}`. Causa probable: el límite superior se compara contra `12 + 1` en `validar_suministro` (`qolqe/reglas/servicios.py`). Se detectó con **análisis de valores límite** (12 válido, 13 inválido).

---

## DEF-02: Se cobra mora el mismo día del vencimiento (los días de atraso se cuentan con +1)

| Campo | Valor |
|---|---|
| Módulo / regla | G2 · HU-G2-02 CA1 · HU-G2-01 CA2 · R-G2-03 |
| Severidad | **Alta**: se le cobra de más al cliente |
| Prioridad | **Alta** |
| Entorno | Ver arriba |
| Pruebas que lo detectan | `test_mora_de_05__diario...[el mismo dia del vencimiento]`, `[un dia de atraso]`, `[19 dias, bajo el tope]`, `test_conteo_de_días_de_atraso_alrededor_del_vencimiento[el mismo dia]`, `[un dia despues]` |

**Pasos para reproducir**
1. Reiniciar los datos e iniciar sesión como Ana.
2. `GET /api/servicios/deudas?empresa=ELECTRO&suministro=10000002` (deuda de S/ 85.50 que **vence hoy**).
3. `POST /api/servicios/pagos {"deuda_id": 2}`.

**Resultado esperado:** `dias_atraso = 0`, `mora = "0.00"` y `total = "85.50"`. R-G2-03 dice: "Pagar el mismo día del vencimiento no genera mora".

**Resultado obtenido:** `dias_atraso = 1`, `mora = "0.43"` y `total = "85.93"`. Todos los atrasos se cuentan con un día de más: con 1 día cobra 1.20 en lugar de 0.60, y con 19 días ya aplica el tope de 12.00 en lugar de 11.40.

**Evidencia:** comprobante `{"monto":"85.50","mora":"0.43","total":"85.93",...}`. Causa probable: `dias_de_atraso` suma `+ 1` (`qolqe/reglas/servicios.py`).

---

## DEF-03: Una deuda con 60 días de atraso se envía a cobranza y no se puede pagar

| Campo | Valor |
|---|---|
| Módulo / regla | G2 · HU-G2-01 CA2 · HU-G2-02 CA2 · R-G2-04 |
| Severidad | **Alta**: bloquea un pago que el cliente sí tiene derecho a hacer |
| Prioridad | **Alta** |
| Entorno | Ver arriba |
| Pruebas que lo detectan | `test_estado_de_la_deuda_según_los_días_de_atraso_límite_de_60_días[60-PENDIENTE]`, `test_mora_de_05__diario...[60 dias, aun se puede pagar]` |

**Pasos para reproducir**
1. Reiniciar los datos e iniciar sesión como Ana.
2. `GET /api/servicios/deudas?empresa=INTERNET&suministro=300000000006` (venció hace exactamente 60 días).

**Resultado esperado:** `estado = "PENDIENTE"`, con mora del 10 % y pagable. R-G2-04 dice: "con 60 días todavía se puede".

**Resultado obtenido:** `estado = "EN_COBRANZA"`, `dias_atraso = 61` y `mora = null`. El pago responde 422 `DEUDA_EN_COBRANZA`.

**Evidencia:** `{"id":6,"dias_atraso":61,"mora":null,"total":null,"estado":"EN_COBRANZA"}`. Tiene la misma causa raíz que DEF-02, pero rompe otra regla de negocio y tiene otro impacto, por eso se reporta por separado.

---

## DEF-04: El débito automático paga deudas que ya estaban vencidas (y sin mora)

| Campo | Valor |
|---|---|
| Módulo / regla | G2 · HU-G2-05 CA2 y CA4 (prioridad Media, alcance extra) |
| Severidad | Media: hay un cobro no autorizado al cliente y la empresa pierde la mora |
| Prioridad | Media |
| Entorno | Ver arriba |
| Prueba que lo detecta | `test_las_deudas_ya_vencidas_antes_de_activar_el_débito_no_se_pagan_automáticamente` |

**Pasos para reproducir**
1. Reiniciar los datos e iniciar sesión como Ana.
2. `POST /api/servicios/afiliaciones {"empresa":"ELECTRO","suministro":"10000003","alias":"Luz vencida"}` (deuda vencida ayer).
3. `PUT /api/servicios/afiliaciones/{id} {"debito_automatico": true}`.
4. `POST /api/pruebas/procesar-diario`.

**Resultado esperado:** `debitos_pagados = 0`. Solo se pagan las deudas que vencen **ese día**, y las vencidas antes de activar el débito no se pagan.

**Resultado obtenido:** `debitos_pagados = 1`. Se pagó la deuda vencida, con origen `DEBITO_AUTOMATICO`, `mora = 0.00` y `total = 200.00`, aunque la consulta mostraba un total de 202.00.

**Evidencia:** `{"debitos_pagados":1,...}` y `GET /api/servicios/pagos` muestra el pago. Causa probable: el proceso diario filtra `vencimiento <= hoy` en lugar de `= hoy`.

---

## DEF-05 (rendimiento): Con ~1 200 usuarios simultáneos el servicio colapsa y no se recupera sin reinicio

| Campo | Valor |
|---|---|
| Módulo / requisito | Toda la API · requerimiento de rendimiento «Quincena Qolqe» («opera de 6:00 a 24:00 sin reinicios») |
| Severidad | **Alta**: caída total y permanente del servicio |
| Prioridad | Media: ocurre a 4× la carga de la campaña (300 VUs) |
| Entorno | Local: i5-11400H, 32 GB, Windows 11, uvicorn 1 proceso, SQLite. k6 v2.1.0 |
| Prueba que lo detecta | `python tests/performance/ejecutar.py estres` (escalón de 1 200 VUs) |

**Pasos para reproducir**
1. Levantar Qolqe: `uvicorn qolqe.main:app --port 8000 --no-access-log`.
2. `python tests/performance/ejecutar.py estres` (escalones de +200 VUs con la mezcla de operaciones del requerimiento).
3. Al llegar a 1 200 VUs (~100 req/s), y al terminar la prueba, consultar `GET /api/salud`.

**Resultado esperado:** con exceso de carga, degradación controlada (respuestas más lentas o 503) y recuperación al bajar la carga.

**Resultado obtenido:** p95 = 60 s (timeout), errores técnicos 42–100 %, throughput de ~100 a ~20 req/s. 13 minutos después de terminar la prueba, `/api/salud` seguía sin responder, la memoria en ~1.2 GB y `BEGIN IMMEDIATE` sobre la BD devolvía «database is locked». Hubo que reiniciar el proceso. La integridad del dinero se mantuvo (0 descuadres).

**Evidencia:** `tests/performance/resultados/estres/` → `graficos.png`, `analisis.json`, `hilos_py-spy.txt` (los 40 hilos de trabajo detenidos en un INSERT/UPDATE esperando el lock; ninguno en commit/rollback), `recuperacion.log`. Causa probable: una transacción de escritura queda abierta sin dueño (posiblemente una petición interrumpida por desconexión del cliente entre su escritura y su commit), y como SQLite admite un solo escritor, todas las demás escrituras esperan el `busy_timeout` de 10 s y ocupan los 40 hilos. Falta además un límite de concurrencia que rechace el exceso con 503.

---

## Observaciones de las pruebas técnicas (Schemathesis): no son defectos funcionales

| ID | Hallazgo | Clasificación |
|---|---|---|
| OBS-01 | `GET /api/servicios/pagos?afiliacion_id=-1072...` (entero muy grande) responde **422**, pero el contrato declara `integer` sin rango. | Defecto **del contrato**: falta documentar el rango (`minimum`/`maximum`). Severidad baja. |
| OBS-02 | `OPTIONS /api/servicios/pagos` responde `Allow: POST`, aunque la ruta también acepta `GET` (Schemathesis lo marca en 3 rutas de `/api/servicios/*` con dos métodos). | Convención HTTP (cabecera `Allow` incompleta). Observación de baja severidad, la produce el framework. |
| OBS-03 | "API rejected schema-compliant request": `POST /api/servicios/pagos {"deuda_id": 7}` responde 422 `DEUDA_EN_COBRANZA`. | **No es defecto**: es la regla R-G2-04 (deuda con más de 60 días). El contrato no puede expresar reglas de negocio; el clasificador lo cuenta como "Válido según el contrato" con respuesta correcta. |

Resultado positivo: desde que Schemathesis cubre las 9 operaciones `/api/servicios/*` (E1..E9) genera ~900–1 200 solicitudes por ejecución y **no hubo ningún 500**.

---

## DEF-06: La API responde antes de confirmar la transacción (carrera lectura tras escritura)

| Campo | Valor |
|---|---|
| Módulo / requisito | Toda la API · `qolqe/dependencias.py` (`obtener_bd`) |
| Severidad | **Alta**: el usuario ve datos viejos o es expulsado de la sesión |
| Prioridad | **Alta** |
| Entorno | Local: Windows 11, FastAPI 0.143, SQLite |
| Pruebas que lo detectan | Web E2E con etiqueta `@DEF-06` (login por pantalla, refresco tras afiliar/pagar) |

**Resultado esperado:** al recibir la respuesta de una escritura, un GET inmediato ya ve el cambio.
**Resultado actual:** el commit se hace al cerrar la dependencia con `yield`, y FastAPI lo ejecuta *después* de enviar la respuesta. Reproducción por API (login y enseguida `GET /api/cuentas/me`): 109 de 200 respuestas fueron 401.
**Efecto en la web:** tras un login correcto la primera petición puede dar 401 y la app manda a `/login?motivo=sesion`; tras afiliar, desafiliar o pagar, la lista se repinta con datos viejos.
**Tratamiento en las pruebas:** los escenarios que lo exponen llevan `@defecto @DEF-06` y se marcan SKIP si fallan (`--skiponfailure defecto`); el resto verifica recargando la página.

---

# Núcleo común (HU-N-01 a HU-N-09) · pruebas de API

Detectados por `features/api/nucleo_comun.feature` (pytest-bdd, mismas condiciones del entorno común). Cada prueba está marcada como fallo esperado (`xfail strict`) con su ID en `tests/conftest.py`. Usuarios semilla: Ana 987654321/4826, Bruno 912345678/7391, Diego 998877665/3604 (límite diario S/ 1,000.00), Fabián 934567812 (cuenta cerrada).

---

## DEF-07: Cerrar sesión no invalida el token

| Campo | Valor |
|---|---|
| Módulo / regla | Núcleo · HU-N-03 CA1 |
| Severidad | **Alta**: un token "cerrado" sigue dando acceso a la cuenta |
| Prioridad | **Alta** |
| Prueba que lo detecta | `test_después_de_cerrar_sesión_el_token_ya_no_es_válido` (N3) |

**Pasos para reproducir**
1. `POST /api/auth/login {"celular":"987654321","pin":"4826"}` y guardar el token.
2. `POST /api/auth/logout` con ese token → 204.
3. `GET /api/cuentas/me` con el mismo token.

**Resultado esperado:** 401 `NO_AUTENTICADO`.

**Resultado obtenido:** 200 con el perfil de Ana.

**Evidencia / causa probable:** el logout guarda el `jti` en `tokens_revocados`, pero `usuario_actual` (`qolqe/dependencias.py`) busca el **token completo** (`credenciales.credentials`) en esa tabla, y el logout tampoco marca `sesiones.cerrada_en`. Ninguna de las dos verificaciones lo rechaza.

---

## DEF-08: Se acepta un PIN en secuencia descendente

| Campo | Valor |
|---|---|
| Módulo / regla | Núcleo · HU-N-01 CA4 · RN-03 |
| Severidad | Media: PIN débil permitido |
| Prioridad | Media |
| Prueba que lo detecta | `test_registro_con_pin_que_no_cumple_rn03_caso[secuencia descendente-4321]` (N1) |

**Pasos para reproducir:** `POST /api/usuarios {"dni":"61234567","nombres":"Lucía Mamani","celular":"911222333","pin":"4321"}`.

**Resultado esperado:** 422 `PIN_INVALIDO` (RN-03: ni ascendente ni descendente).

**Resultado obtenido:** 201, la cuenta se crea.

**Causa probable:** `validar_pin` (`qolqe/reglas/nucleo.py`) solo busca el PIN dentro de `"0123456789"` (ascendente). `1234` sí se rechaza.

---

## DEF-09: Un login exitoso no reinicia el conteo de intentos fallidos

| Campo | Valor |
|---|---|
| Módulo / regla | Núcleo · HU-N-02 CA3 · RN-04 |
| Severidad | Media: se bloquea a un usuario legítimo |
| Prioridad | Media |
| Prueba que lo detecta | `test_un_login_exitoso_reinicia_el_conteo_de_intentos_fallidos` (N2) |

**Pasos para reproducir**
1. Dos logins de Bruno con PIN `0000` → 401 y 401.
2. Login de Bruno con su PIN correcto `7391` → 200.
3. Un login con PIN `0000`.

**Resultado esperado:** 401 `CREDENCIALES_INVALIDAS` (RN-04: el login exitoso reinicia el conteo; es el 1.er fallo consecutivo).

**Resultado obtenido:** 423 `CUENTA_BLOQUEADA`.

**Causa probable:** en `iniciar_sesion` (`qolqe/api/autenticacion.py`) el camino exitoso no pone `intentos_fallidos = 0`.

---

## DEF-10: Se puede transferir a una cuenta cerrada

| Campo | Valor |
|---|---|
| Módulo / regla | Núcleo · HU-N-07 CA2 · HU-N-06 CA4 · RN-07 |
| Severidad | **Alta**: el dinero queda en una cuenta que nadie puede usar |
| Prioridad | **Alta** |
| Prueba que lo detecta | `test_no_se_puede_transferir_a_una_cuenta_cerrada` (N8) |

**Pasos para reproducir:** como Ana, `POST /api/transferencias {"celular_destino":"934567812","monto":"10.00"}` (Fabián, cuenta CERRADA).

**Resultado esperado:** 422 `DESTINO_INACTIVO` y el saldo de Ana sin cambios.

**Resultado obtenido:** 201, se debitan S/ 10.00 a Ana y se acreditan a Fabián.

**Causa probable:** `_resolver_destino_qolqe` (`qolqe/api/transferencias.py`) busca el destino solo por celular, sin revisar `estado`. El código `DESTINO_INACTIVO` no existe en la API.

---

## DEF-11: La comisión interbancaria no usa redondeo comercial

| Campo | Valor |
|---|---|
| Módulo / regla | Núcleo · HU-N-09 CA1 · HU-N-08 CA2 · RN-09 |
| Severidad | Baja: diferencia de S/ 0.01 en ciertos montos |
| Prioridad | Baja |
| Prueba que lo detecta | `test_simular_la_comisión_interbancaria_caso[redondeo comercial 0.005-...]` (N9) |

**Pasos para reproducir:** `GET /api/transferencias/comision?monto=71.00&tipo=INTERBANCARIA` (1.5 % = 1.065).

**Resultado esperado:** comisión `1.07`, total `72.07` (RN-09: "0.005 sube").

**Resultado obtenido:** comisión `1.06`, total `72.06`.

**Causa probable:** `calcular_comision` (`qolqe/reglas/nucleo.py`) hace `quantize` sin `rounding=ROUND_HALF_UP`, así que usa el redondeo por defecto de `Decimal` (al par). La mora de G2 sí usa `ROUND_HALF_UP`.

---

## DEF-12: El saldo puede quedar negativo en una transferencia interbancaria

| Campo | Valor |
|---|---|
| Módulo / regla | Núcleo · HU-N-08 CA2 · RN-08 |
| Severidad | **Alta**: saldo negativo |
| Prioridad | **Alta** |
| Prueba que lo detecta | `test_el_saldo_debe_cubrir_el_monto_más_la_comisión_interbancaria` (N8) |

**Pasos para reproducir:** fijar el saldo de Ana en S/ 100.00 (`PUT /api/pruebas/saldo`) y `POST /api/transferencias {"tipo":"INTERBANCARIA","cci":"00219100123456789012","monto":"100.00"}`.

**Resultado esperado:** 422 `SALDO_INSUFICIENTE` (el saldo debe cubrir 100.00 + 1.50).

**Resultado obtenido:** 201 con `"saldo":"-1.50"`.

**Causa probable:** `realizar_transferencia` (`qolqe/transacciones.py`) compara el saldo con `monto_cent` y no con `monto_cent + comision_cent`.

---

## DEF-13: Las transferencias interbancarias no cuentan para el límite diario

| Campo | Valor |
|---|---|
| Módulo / regla | Núcleo · HU-N-08 CA2 · RN-06 |
| Severidad | **Alta**: se puede enviar fuera del banco más que el límite diario |
| Prioridad | **Alta** |
| Prueba que lo detecta | `test_las_transferencias_interbancarias_cuentan_para_el_límite_diario` (N8) |

**Pasos para reproducir:** como Diego (límite S/ 1,000.00), dos interbancarias de S/ 500.00 → 201 y 201; después una transferencia Qolqe de S/ 1.00 a Bruno.

**Resultado esperado:** 422 `LIMITE_DIARIO_EXCEDIDO` (RN-06: suman las transferencias a Qolqe **e interbancarias**).

**Resultado obtenido:** 201. Lo enviado al otro banco no se cuenta (con interbancarias se puede seguir sin límite).

**Causa probable:** `transferido_hoy_centimos` (`qolqe/operaciones.py`) filtra `tipo = 'QOLQE'`.

---

## DEF-14: Transferencias simultáneas superan el límite diario

| Campo | Valor |
|---|---|
| Módulo / regla | Núcleo · HU-N-07 CA5 · RN-06 |
| Severidad | **Alta**: el límite diario se salta enviando pedidos a la vez |
| Prioridad | **Alta** |
| Prueba que lo detecta | `test_transferencias_simultáneas_no_superan_el_límite_diario` (N8, `@concurrencia`; falló en 5 de 5 ejecuciones) |

**Pasos para reproducir:** como Diego (límite S/ 1,000.00, saldo S/ 2,500.00), enviar **3 a la vez** `POST /api/transferencias {"celular_destino":"912345678","monto":"500.00"}`.

**Resultado esperado:** 2 responden 201 y 1 responde 422 `LIMITE_DIARIO_EXCEDIDO`; saldo final S/ 1,500.00.

**Resultado obtenido:** las 3 responden 201 (S/ 1,500.00 en el día con límite de S/ 1,000.00).

**Causa probable:** la verificación del límite (`transferido_hoy_centimos`) y el débito no se hacen en la misma transacción con bloqueo; entre ambos está la consulta antifraude (40–120 ms), y las 3 solicitudes leen el mismo total del día antes de que ninguna escriba. En G2 el pago doble se evita con `UPDATE ... WHERE estado = 'PENDIENTE'`; aquí no hay un control equivalente.
