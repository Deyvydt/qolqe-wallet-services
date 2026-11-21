<!-- QUÉ ES: matriz de trazabilidad generada automáticamente por .github/scripts/trazabilidad.py.
     No editar a mano: se vuelve a generar en cada ejecución del pipeline. -->

# Matriz de trazabilidad · G2 Pago de servicios

Run [#25](https://github.com/Deyvydt/qolqe-wallet-services/actions/runs/44861371954) · commit [`b5e23a3`](https://github.com/Deyvydt/qolqe-wallet-services/commit/b5e23a3f2b5cdc59e7cc260dbbb8b68593173e8f) · rama `main` · 21/11/2026 11:01 (hora de Lima)

Cada fila une una **historia de usuario (HU)** con el **caso de prueba** que la verifica, el **nivel** donde se prueba y el **resultado de esta ejecución**.

**Totales:** ✅ 250 pasan · ⚠️ 18 fallos esperados (defectos conocidos) · ❌ 0 fallan · ⏭️ 2 omitidas

Fuentes: API ✔️ ejecutada · Web ✔️ ejecutada

## Cobertura de la especificación

| HU | Descripción | ¿Tiene casos en este run? | Casos |
|---|---|---|---:|
| HU-G2-01 | Consultar deudas | ✅ Sí | 38 |
| HU-G2-02 | Pagar una deuda | ✅ Sí | 26 |
| HU-G2-03 | Afiliar un servicio | ✅ Sí | 22 |
| HU-G2-04 | Ver servicios afiliados | ✅ Sí | 9 |
| HU-G2-05 | Editar afiliación y débito automático | ✅ Sí | 17 |
| HU-G2-06 | Desafiliar | ✅ Sí | 10 |
| HU-G2-07 | Ver pagos y comprobantes | ✅ Sí | 14 |

**7 de 7 HU** del módulo tienen casos en este run.

## Reporte total de escenarios · endpoint × tipo × resultado

Cada escenario está etiquetado con su endpoint (`@E1`..`@E10`) y su tipo (`@funcional` / `@tecnico`). ✅ pasa · ⚠️ fallo esperado (defecto conocido) · ❌ falla.

| Endpoint | Funcional | F ✅ | F ⚠️ | F ❌ | Técnico | T ✅ | T ⚠️ | T ❌ | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| E1 · GET /api/servicios/empresas | 2 | 2 | 0 | 0 | 4 | 4 | 0 | 0 | 6 |
| E2 · GET /api/servicios/deudas | 17 | 13 | 4 | 0 | 11 | 11 | 0 | 0 | 28 |
| E3 · POST /api/servicios/pagos | 15 | 11 | 4 | 0 | 5 | 5 | 0 | 0 | 20 |
| E4 · GET /api/servicios/pagos | 4 | 4 | 0 | 0 | 5 | 5 | 0 | 0 | 9 |
| E5 · GET /api/servicios/pagos/{codigo} | 2 | 2 | 0 | 0 | 4 | 4 | 0 | 0 | 6 |
| E6 · GET /api/servicios/afiliaciones | 6 | 6 | 0 | 0 | 3 | 3 | 0 | 0 | 9 |
| E7 · POST /api/servicios/afiliaciones | 14 | 13 | 1 | 0 | 6 | 6 | 0 | 0 | 20 |
| E8 · PUT /api/servicios/afiliaciones/{id} | 4 | 4 | 0 | 0 | 6 | 6 | 0 | 0 | 10 |
| E9 · DELETE /api/servicios/afiliaciones/{id} | 4 | 4 | 0 | 0 | 4 | 4 | 0 | 0 | 8 |
| E10 · POST /api/pruebas/procesar-diario | 4 | 3 | 1 | 0 | 2 | 2 | 0 | 0 | 6 |
| N1 · POST /api/usuarios | 17 | 16 | 1 | 0 | 4 | 4 | 0 | 0 | 21 |
| N2 · POST /api/auth/login | 10 | 9 | 1 | 0 | 5 | 5 | 0 | 0 | 15 |
| N3 · POST /api/auth/logout | 3 | 2 | 1 | 0 | 2 | 2 | 0 | 0 | 5 |
| N4 · GET /api/cuentas/me | 1 | 1 | 0 | 0 | 4 | 4 | 0 | 0 | 5 |
| N5 · PUT /api/cuentas/me | 10 | 10 | 0 | 0 | 2 | 2 | 0 | 0 | 12 |
| N6 · GET /api/cuentas/me/saldo | 1 | 1 | 0 | 0 | 2 | 2 | 0 | 0 | 3 |
| N7 · POST /api/cuentas/me/cierre | 5 | 5 | 0 | 0 | 2 | 2 | 0 | 0 | 7 |
| N8 · POST /api/transferencias | 25 | 21 | 4 | 0 | 8 | 8 | 0 | 0 | 33 |
| N9 · GET /api/transferencias/comision | 10 | 9 | 1 | 0 | 5 | 5 | 0 | 0 | 15 |
| Otros (humo, métodos no declarados) | 0 | 0 | 0 | 0 | 2 | 2 | 0 | 0 | 2 |
| Web E2E | 30 | 28 | 0 | 0 | 0 | 0 | 0 | 0 | 30 |
| **TOTAL** | 184 | 164 | 18 | 0 | 86 | 86 | 0 | 0 | 270 |

## Resumen por HU

| HU | Casos | Cobertura por nivel | ✅ | ⚠️ | ❌ | ⏭️ | Defectos | Estado |
|---|---:|---|---:|---:|---:|---:|---|---|
| HU-G2-01 | 38 | api 32 · web 6 | 34 | 4 | 0 | 0 | [DEF-01](defectos.md#def-01-se-acepta-un-código-de-suministro-de-13-dígitos), [DEF-02](defectos.md#def-02-se-cobra-mora-el-mismo-día-del-vencimiento-los-días-de-atraso-se-cuentan-con-1), [DEF-03](defectos.md#def-03-una-deuda-con-60-días-de-atraso-se-envía-a-cobranza-y-no-se-puede-pagar) | ✅ OK (con defectos conocidos) |
| HU-G2-02 | 26 | api 20 · web 6 | 20 | 4 | 0 | 2 | [DEF-02](defectos.md#def-02-se-cobra-mora-el-mismo-día-del-vencimiento-los-días-de-atraso-se-cuentan-con-1), [DEF-03](defectos.md#def-03-una-deuda-con-60-días-de-atraso-se-envía-a-cobranza-y-no-se-puede-pagar) | ✅ OK (con defectos conocidos) |
| HU-G2-03 | 22 | api 19 · web 3 | 21 | 1 | 0 | 0 | [DEF-01](defectos.md#def-01-se-acepta-un-código-de-suministro-de-13-dígitos) | ✅ OK (con defectos conocidos) |
| HU-G2-04 | 9 | api 8 · web 1 | 9 | 0 | 0 | 0 | — | ✅ OK |
| HU-G2-05 | 17 | api 15 · web 2 | 16 | 1 | 0 | 0 | [DEF-04](defectos.md#def-04-el-débito-automático-paga-deudas-que-ya-estaban-vencidas-y-sin-mora) | ✅ OK (con defectos conocidos) |
| HU-G2-06 | 10 | api 7 · web 3 | 10 | 0 | 0 | 0 | — | ✅ OK |
| HU-G2-07 | 14 | api 13 · web 1 | 14 | 0 | 0 | 0 | — | ✅ OK |
| HU-N-01 | 22 | api 21 · web 1 | 21 | 1 | 0 | 0 | [DEF-08](defectos.md#def-08-se-acepta-un-pin-en-secuencia-descendente) | ✅ OK (con defectos conocidos) |
| HU-N-02 | 19 | api 15 · web 4 | 18 | 1 | 0 | 0 | [DEF-09](defectos.md#def-09-un-login-exitoso-no-reinicia-el-conteo-de-intentos-fallidos) | ✅ OK (con defectos conocidos) |
| HU-N-03 | 6 | api 5 · web 1 | 5 | 1 | 0 | 0 | [DEF-07](defectos.md#def-07-cerrar-sesión-no-invalida-el-token) | ✅ OK (con defectos conocidos) |
| HU-N-04 | 9 | api 8 · web 1 | 9 | 0 | 0 | 0 | — | ✅ OK |
| HU-N-05 | 13 | api 12 · web 1 | 13 | 0 | 0 | 0 | — | ✅ OK |
| HU-N-06 | 9 | api 7 · web 2 | 9 | 0 | 0 | 0 | — | ✅ OK |
| HU-N-07 | 26 | api 24 · web 2 | 24 | 2 | 0 | 0 | [DEF-10](defectos.md#def-10-se-puede-transferir-a-una-cuenta-cerrada), [DEF-14](defectos.md#def-14-transferencias-simultáneas-superan-el-límite-diario) | ✅ OK (con defectos conocidos) |
| HU-N-08 | 10 | api 9 · web 1 | 8 | 2 | 0 | 0 | [DEF-12](defectos.md#def-12-el-saldo-puede-quedar-negativo-en-una-transferencia-interbancaria), [DEF-13](defectos.md#def-13-las-transferencias-interbancarias-no-cuentan-para-el-límite-diario) | ✅ OK (con defectos conocidos) |
| HU-N-09 | 17 | api 15 · web 2 | 16 | 1 | 0 | 0 | [DEF-11](defectos.md#def-11-la-comisión-interbancaria-no-usa-redondeo-comercial) | ✅ OK (con defectos conocidos) |
| (sin HU) | 11 | api 1 · contrato 10 | 11 | 0 | 0 | 0 | — | ✅ OK |

## Matriz HU → caso → nivel → resultado

| HU | Caso de prueba | CA | Endpoint | Tipo | Nivel | Resultado |
|---|---|---|---|---|---|---|
| HU-G2-01 | cada deuda muestra todos sus datos y el titular enmascarado | CA2 | E2 | tecnico | api | ✅ passed |
| HU-G2-01 | cada empresa tiene código nombre y rubro | — | E1 | tecnico | api | ✅ passed |
| HU-G2-01 | consultar deudas con un token inválido [JWT mal firmado-eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0.x] | — | E2 | tecnico | api | ✅ passed |
| HU-G2-01 | consultar deudas con un token inválido [texto cualquiera-abc123] | — | E2 | tecnico | api | ✅ passed |
| HU-G2-01 | consultar deudas sin token | — | E2 | tecnico | api | ✅ passed |
| HU-G2-01 | conteo de días de atraso alrededor del vencimiento [el mismo dia-0-0] | CA2 | E2 | funcional | api | ⚠️ xfailed → [DEF-02](defectos.md#def-02-se-cobra-mora-el-mismo-día-del-vencimiento-los-días-de-atraso-se-cuentan-con-1) |
| HU-G2-01 | conteo de días de atraso alrededor del vencimiento [un dia antes--1-0] | CA2 | E2 | funcional | api | ✅ passed |
| HU-G2-01 | conteo de días de atraso alrededor del vencimiento [un dia despues-1-1] | CA2 | E2 | funcional | api | ⚠️ xfailed → [DEF-02](defectos.md#def-02-se-cobra-mora-el-mismo-día-del-vencimiento-los-días-de-atraso-se-cuentan-con-1) |
| HU-G2-01 | después de pagar la única deuda el suministro queda sin deudas pendientes | CA3 | E2 | funcional | api | ✅ passed |
| HU-G2-01 | deudas ordenadas de la más antigua a la más reciente | CA2 | E2 | funcional | api | ✅ passed |
| HU-G2-01 | el catálogo es público y responde sin token | — | E1 | tecnico | api | ✅ passed |
| HU-G2-01 | el catálogo lista las empresas ordenadas por nombre | CA1 | E1 | funcional | api | ✅ passed |
| HU-G2-01 | el token vence a los 30 minutos de iniciar sesión [29-200] | — | E2 | tecnico | api | ✅ passed |
| HU-G2-01 | el token vence a los 30 minutos de iniciar sesión [30-401] | — | E2 | tecnico | api | ✅ passed |
| HU-G2-01 | empresa inexistente | CA1 | E2 | funcional | api | ✅ passed |
| HU-G2-01 | estado de la deuda según los días de atraso límite de 60 días [59-PENDIENTE] | CA2 | E2 | funcional | api | ✅ passed |
| HU-G2-01 | estado de la deuda según los días de atraso límite de 60 días [60-PENDIENTE] | CA2 | E2 | funcional | api | ⚠️ xfailed → [DEF-03](defectos.md#def-03-una-deuda-con-60-días-de-atraso-se-envía-a-cobranza-y-no-se-puede-pagar) |
| HU-G2-01 | estado de la deuda según los días de atraso límite de 60 días [61-EN_COBRANZA] | CA2 | E2 | funcional | api | ✅ passed |
| HU-G2-01 | faltan parámetros obligatorios de la consulta [falta empresa-?suministro=10000001] | — | E2 | tecnico | api | ✅ passed |
| HU-G2-01 | faltan parámetros obligatorios de la consulta [falta suministro-?empresa=ELECTRO] | — | E2 | tecnico | api | ✅ passed |
| HU-G2-01 | faltan parámetros obligatorios de la consulta [sin parametros-] | — | E2 | tecnico | api | ✅ passed |
| HU-G2-01 | longitud del código de suministro rg201 8 a 12 dígitos [12 digitos (limite max)-INTERNET-300000000007-200--] | CA1 | E2 | funcional | api | ✅ passed |
| HU-G2-01 | longitud del código de suministro rg201 8 a 12 dígitos [13 digitos (invalido)-ELECTRO-1000000010000-422-SUMINISTRO_INVALIDO] | CA1 | E2 | funcional | api | ⚠️ xfailed → [DEF-01](defectos.md#def-01-se-acepta-un-código-de-suministro-de-13-dígitos) |
| HU-G2-01 | longitud del código de suministro rg201 8 a 12 dígitos [7 digitos (invalido)-ELECTRO-1234567-422-SUMINISTRO_INVALIDO] | CA1 | E2 | funcional | api | ✅ passed |
| HU-G2-01 | longitud del código de suministro rg201 8 a 12 dígitos [8 digitos (limite min)-ELECTRO-10000001-200--] | CA1 | E2 | funcional | api | ✅ passed |
| HU-G2-01 | método http no permitido en el catálogo | — | E1 | tecnico | api | ✅ passed |
| HU-G2-01 | método http no permitido en la consulta de deudas | — | E2 | tecnico | api | ✅ passed |
| HU-G2-01 | suministro con caracteres no numéricos [-10000001] | CA1 | E2 | funcional | api | ✅ passed |
| HU-G2-01 | suministro con caracteres no numéricos [1000 0001] | CA1 | E2 | funcional | api | ✅ passed |
| HU-G2-01 | suministro con caracteres no numéricos [1000000A] | CA1 | E2 | funcional | api | ✅ passed |
| HU-G2-01 | suministro sin deudas pendientes | CA3 | E2 | funcional | api | ✅ passed |
| HU-G2-01 | una empresa que no está en el catálogo no tiene deudas consultables | CA1 | E1 | funcional | api | ✅ passed |
| HU-G2-01 | Un suministro de menos de 8 dígitos es rechazado | CA1 | Web E2E | funcional | web | ✅ passed |
| HU-G2-01 | Un suministro sin deudas pendientes muestra un aviso | CA3 | Web E2E | funcional | web | ✅ passed |
| HU-G2-01 | CP-W01 · Ana paga su recibo de luz (caso .robot) | CA1, CA4 | Web E2E | funcional | web | ✅ passed |
| HU-G2-01 | CP-W01 · Ana paga su recibo de luz y ve el comprobante | CA1, CA4 | Web E2E | funcional | web | ✅ passed |
| HU-G2-01 | CP-W02 · Ana paga su recibo de agua (caso .robot) | CA1, CA4 | Web E2E | funcional | web | ✅ passed |
| HU-G2-01 | CP-W02 · Ana paga su recibo de agua y ve el comprobante | CA1, CA4 | Web E2E | funcional | web | ✅ passed |
| HU-G2-02 | deuda en cobranza más de 60 días no se puede pagar | CA2 | E3 | funcional | api | ✅ passed |
| HU-G2-02 | deuda id con tipo de dato inválido [{"deuda_id": "abc"}] | — | E3 | tecnico | api | ✅ passed |
| HU-G2-02 | deuda id con tipo de dato inválido [{"deuda_id": null}] | — | E3 | tecnico | api | ✅ passed |
| HU-G2-02 | deuda id con tipo de dato inválido [{}] | — | E3 | tecnico | api | ✅ passed |
| HU-G2-02 | deuda inexistente | CA2 | E3 | funcional | api | ✅ passed |
| HU-G2-02 | deuda ya pagada no se cobra dos veces | CA2 | E3 | funcional | api | ✅ passed |
| HU-G2-02 | dos pagos simultáneos de la misma deuda solo uno es exitoso | CA3 | E3 | funcional | api | ✅ passed |
| HU-G2-02 | el comprobante de un pago de otro usuario responde 404 | CA2 | E5 | tecnico | api | ✅ passed |
| HU-G2-02 | el pago genera un movimiento con el mismo código de operación | CA4 | E3 | funcional | api | ✅ passed |
| HU-G2-02 | el saldo debe cubrir el total monto  mora [saldo exacto (pasa)-120.00-201---0.00] | CA1 | E3 | funcional | api | ✅ passed |
| HU-G2-02 | el saldo debe cubrir el total monto  mora [un centimo menos (falla)-119.99-422-SALDO_INSUFICIENTE-119.99] | CA1 | E3 | funcional | api | ✅ passed |
| HU-G2-02 | mora de 05  diario después del vencimiento con tope de 10 [19 dias, bajo el tope-19-11.40-131.40] | CA1 | E3 | funcional | api | ⚠️ xfailed → [DEF-02](defectos.md#def-02-se-cobra-mora-el-mismo-día-del-vencimiento-los-días-de-atraso-se-cuentan-con-1) |
| HU-G2-02 | mora de 05  diario después del vencimiento con tope de 10 [20 dias, justo en el tope 10 %-20-12.00-132.00] | CA1 | E3 | funcional | api | ✅ passed |
| HU-G2-02 | mora de 05  diario después del vencimiento con tope de 10 [21 dias, el tope no se supera-21-12.00-132.00] | CA1 | E3 | funcional | api | ✅ passed |
| HU-G2-02 | mora de 05  diario después del vencimiento con tope de 10 [60 dias, aun se puede pagar-60-12.00-132.00] | CA1 | E3 | funcional | api | ⚠️ xfailed → [DEF-03](defectos.md#def-03-una-deuda-con-60-días-de-atraso-se-envía-a-cobranza-y-no-se-puede-pagar) |
| HU-G2-02 | mora de 05  diario después del vencimiento con tope de 10 [el mismo dia del vencimiento-0-0.00-120.00] | CA1 | E3 | funcional | api | ⚠️ xfailed → [DEF-02](defectos.md#def-02-se-cobra-mora-el-mismo-día-del-vencimiento-los-días-de-atraso-se-cuentan-con-1) |
| HU-G2-02 | mora de 05  diario después del vencimiento con tope de 10 [un dia antes del vencimiento--1-0.00-120.00] | CA1 | E3 | funcional | api | ✅ passed |
| HU-G2-02 | mora de 05  diario después del vencimiento con tope de 10 [un dia de atraso-1-0.60-120.60] | CA1 | E3 | funcional | api | ⚠️ xfailed → [DEF-02](defectos.md#def-02-se-cobra-mora-el-mismo-día-del-vencimiento-los-días-de-atraso-se-cuentan-con-1) |
| HU-G2-02 | pagar sin token | — | E3 | tecnico | api | ✅ passed |
| HU-G2-02 | pago exitoso antes del vencimiento sin mora | CA1, CA4 | E3 | funcional | api | ✅ passed |
| HU-G2-02 | La mora del comprobante respeta R-G2-03 (vence hoy, sin mora) | CA1 | Web E2E | funcional | web | ⏭️ skipped |
| HU-G2-02 | La mora del comprobante respeta R-G2-03 (vencida hace 5 días, 2.5 % de mora) | CA1 | Web E2E | funcional | web | ⏭️ skipped |
| HU-G2-02 | CP-W01 · Ana paga su recibo de luz (caso .robot) | CA1, CA4 | Web E2E | funcional | web | ✅ passed |
| HU-G2-02 | CP-W01 · Ana paga su recibo de luz y ve el comprobante | CA1, CA4 | Web E2E | funcional | web | ✅ passed |
| HU-G2-02 | CP-W02 · Ana paga su recibo de agua (caso .robot) | CA1, CA4 | Web E2E | funcional | web | ✅ passed |
| HU-G2-02 | CP-W02 · Ana paga su recibo de agua y ve el comprobante | CA1, CA4 | Web E2E | funcional | web | ✅ passed |
| HU-G2-03 | afiliar sin token | — | E7 | tecnico | api | ✅ passed |
| HU-G2-03 | afiliar un servicio se crea con el débito automático desactivado | CA1, CA4 | E7 | funcional | api | ✅ passed |
| HU-G2-03 | afiliar una empresa inexistente | CA1 | E7 | funcional | api | ✅ passed |
| HU-G2-03 | cuerpo de afiliación con campos faltantes o de tipo inválido [[]] | — | E7 | tecnico | api | ✅ passed |
| HU-G2-03 | cuerpo de afiliación con campos faltantes o de tipo inválido [{"empresa": "ELECTRO", "suministro": "10000002"}] | — | E7 | tecnico | api | ✅ passed |
| HU-G2-03 | cuerpo de afiliación con campos faltantes o de tipo inválido [{"empresa": "ELECTRO", "suministro": 10000002, "alias": "Luz"}] | — | E7 | tecnico | api | ✅ passed |
| HU-G2-03 | cuerpo de afiliación con campos faltantes o de tipo inválido [{}] | — | E7 | tecnico | api | ✅ passed |
| HU-G2-03 | el suministro de la afiliación cumple rg201 [13 digitos (invalido)-1000000010000] | CA1 | E7 | funcional | api | ⚠️ xfailed → [DEF-01](defectos.md#def-01-se-acepta-un-código-de-suministro-de-13-dígitos) |
| HU-G2-03 | el suministro de la afiliación cumple rg201 [7 digitos (invalido)-1000000] | CA1 | E7 | funcional | api | ✅ passed |
| HU-G2-03 | el suministro de la afiliación cumple rg201 [con letras (invalido)-1000000A] | CA1 | E7 | funcional | api | ✅ passed |
| HU-G2-03 | el suministro debe tener al menos un recibo en la empresa | CA2 | E7 | funcional | api | ✅ passed |
| HU-G2-03 | longitud del alias 3 a 20 caracteres [2 caracteres (invalido)-ab-422-AFILIACION_INVALIDA] | CA1 | E7 | funcional | api | ✅ passed |
| HU-G2-03 | longitud del alias 3 a 20 caracteres [20 caracteres (limite)-Luz de la casa grand-201--] | CA1 | E7 | funcional | api | ✅ passed |
| HU-G2-03 | longitud del alias 3 a 20 caracteres [21 caracteres (invalido)-Luz de la casa grande-422-AFILIACION_INVALIDA] | CA1 | E7 | funcional | api | ✅ passed |
| HU-G2-03 | longitud del alias 3 a 20 caracteres [3 caracteres (limite)-abc-201--] | CA1 | E7 | funcional | api | ✅ passed |
| HU-G2-03 | los espacios alrededor del alias no cuentan para su longitud | CA1 | E7 | funcional | api | ✅ passed |
| HU-G2-03 | máximo 8 servicios afiliados por usuario [la novena (sobre limite)-8-422-LIMITE_AFILIACIONES] | CA3 | E7 | funcional | api | ✅ passed |
| HU-G2-03 | máximo 8 servicios afiliados por usuario [la octava (limite)-7-201--] | CA3 | E7 | funcional | api | ✅ passed |
| HU-G2-03 | no se puede afiliar dos veces el mismo suministro | CA3 | E7 | funcional | api | ✅ passed |
| HU-G2-03 | No se puede afiliar un suministro que no existe en la empresa | CA2 | Web E2E | funcional | web | ✅ passed |
| HU-G2-03 | CP-W03 · Ana afilia su servicio de agua | CA1, CA4 | Web E2E | funcional | web | ✅ passed |
| HU-G2-03 | CP-W03 · Ana afilia un servicio de agua | CA1 | Web E2E | funcional | web | ✅ passed |
| HU-G2-04 | cada afiliación tiene todos sus campos | — | E6 | tecnico | api | ✅ passed |
| HU-G2-04 | el próximo vencimiento solo existe si hay deuda pendiente | CA1 | E6 | funcional | api | ✅ passed |
| HU-G2-04 | mis afiliaciones se listan ordenadas por alias | CA1 | E6 | funcional | api | ✅ passed |
| HU-G2-04 | situación de cada afiliación según sus deudas [con deuda-no hice nada-Luz casa-CON_DEUDA-120.00] | CA1 | E6 | funcional | api | ✅ passed |
| HU-G2-04 | situación de cada afiliación según sus deudas [en cobranza-no hice nada-Internet casa-EN_COBRANZA-0.00] | CA1 | E6 | funcional | api | ✅ passed |
| HU-G2-04 | situación de cada afiliación según sus deudas [sin deudas-pagu\xe9 la deuda "ELECTRO" "10000001"-Luz casa-AL_DIA-0.00] | CA1 | E6 | funcional | api | ✅ passed |
| HU-G2-04 | un usuario sin afiliaciones recibe una lista vacía | CA1 | E6 | funcional | api | ✅ passed |
| HU-G2-04 | ver mis afiliaciones sin token | — | E6 | tecnico | api | ✅ passed |
| HU-G2-04 | La lista de afiliaciones se actualiza al instante al desafiliar | CA1 | Web E2E | funcional | web | ✅ passed |
| HU-G2-05 | activar el débito automático envía un sms al titular | CA1 | E8 | funcional | api | ✅ passed |
| HU-G2-05 | cambiar el alias de una afiliación | CA1 | E8 | funcional | api | ✅ passed |
| HU-G2-05 | cambiar el alias por uno demasiado corto | CA1 | E8 | funcional | api | ✅ passed |
| HU-G2-05 | edición con id o cuerpo de tipo inválido [/api/servicios/afiliaciones/1-{"alias": 123}] | — | E8 | tecnico | api | ✅ passed |
| HU-G2-05 | edición con id o cuerpo de tipo inválido [/api/servicios/afiliaciones/1-{"debito_automatico": "talvez"}] | — | E8 | tecnico | api | ✅ passed |
| HU-G2-05 | edición con id o cuerpo de tipo inválido [/api/servicios/afiliaciones/abc-{"alias": "Luz depa"}] | — | E8 | tecnico | api | ✅ passed |
| HU-G2-05 | editar la afiliación de otro usuario responde 404 | — | E8 | tecnico | api | ✅ passed |
| HU-G2-05 | editar una afiliación inexistente | CA1 | E8 | funcional | api | ✅ passed |
| HU-G2-05 | editar una afiliación sin token | — | E8 | tecnico | api | ✅ passed |
| HU-G2-05 | ejecutar dos veces el proceso diario no cobra dos veces la misma deuda | — | E10 | tecnico | api | ✅ passed |
| HU-G2-05 | el proceso diario paga sin mora la deuda que vence hoy | CA2 | E10 | funcional | api | ✅ passed |
| HU-G2-05 | la respuesta del proceso diario tiene todos sus campos y usa la fecha del reloj | — | E10 | tecnico | api | ✅ passed |
| HU-G2-05 | las deudas ya vencidas antes de activar el débito no se pagan automáticamente | CA4 | E10 | funcional | api | ⚠️ xfailed → [DEF-04](defectos.md#def-04-el-débito-automático-paga-deudas-que-ya-estaban-vencidas-y-sin-mora) |
| HU-G2-05 | sin saldo la deuda queda pendiente y el titular recibe un sms | CA3 | E10 | funcional | api | ✅ passed |
| HU-G2-05 | una afiliación sin débito automático no se paga en el proceso diario | CA2 | E10 | funcional | api | ✅ passed |
| HU-G2-05 | Ana activa el débito automático de su servicio de luz | CA1 | Web E2E | funcional | web | ✅ passed |
| HU-G2-05 | Ana cambia el alias de un servicio afiliado | CA1 | Web E2E | funcional | web | ✅ passed |
| HU-G2-06 | desafiliar con un id que no es entero | — | E9 | tecnico | api | ✅ passed |
| HU-G2-06 | desafiliar la afiliación de otro usuario responde 404 y no la borra | — | E9 | tecnico | api | ✅ passed |
| HU-G2-06 | desafiliar sin token | — | E9 | tecnico | api | ✅ passed |
| HU-G2-06 | desafiliar un servicio no modifica los pagos realizados | CA1 | E9 | funcional | api | ✅ passed |
| HU-G2-06 | desafiliar una afiliación inexistente | CA1 | E9 | funcional | api | ✅ passed |
| HU-G2-06 | después de desactivar el débito automático sí se puede desafiliar | CA2 | E9 | funcional | api | ✅ passed |
| HU-G2-06 | no se puede desafiliar con el débito automático activo | CA2 | E9 | funcional | api | ✅ passed |
| HU-G2-06 | Ana desafilia un servicio sin débito automático | CA1 | Web E2E | funcional | web | ✅ passed |
| HU-G2-06 | La lista de afiliaciones se actualiza al instante al desafiliar | CA1 | Web E2E | funcional | web | ✅ passed |
| HU-G2-06 | No se puede desafiliar un servicio con el débito automático activo | CA2 | Web E2E | funcional | web | ✅ passed |
| HU-G2-07 | afiliacion id con tipo de dato inválido [1.5] | — | E4 | tecnico | api | ✅ passed |
| HU-G2-07 | afiliacion id con tipo de dato inválido [abc] | — | E4 | tecnico | api | ✅ passed |
| HU-G2-07 | comprobante de un código de operación inexistente | CA2 | E5 | funcional | api | ✅ passed |
| HU-G2-07 | el comprobante de un pago de otro usuario responde 404 | CA2 | E5 | tecnico | api | ✅ passed |
| HU-G2-07 | el comprobante tiene todos sus campos | — | E5 | tecnico | api | ✅ passed |
| HU-G2-07 | el dueño ve el comprobante de su pago | CA2 | E5 | funcional | api | ✅ passed |
| HU-G2-07 | filtrar mis pagos por afiliación muestra solo los de ese suministro | CA1 | E4 | funcional | api | ✅ passed |
| HU-G2-07 | filtrar por la afiliación de otro usuario responde 404 | — | E4 | tecnico | api | ✅ passed |
| HU-G2-07 | filtrar por una afiliación inexistente | CA1 | E4 | funcional | api | ✅ passed |
| HU-G2-07 | mis pagos se listan del más reciente al más antiguo | CA1 | E4 | funcional | api | ✅ passed |
| HU-G2-07 | sin pagos realizados la lista está vacía | CA1 | E4 | funcional | api | ✅ passed |
| HU-G2-07 | ver mis pagos sin token | — | E4 | tecnico | api | ✅ passed |
| HU-G2-07 | ver un comprobante sin token | — | E5 | tecnico | api | ✅ passed |
| HU-G2-07 | Ana filtra sus pagos por servicio afiliado | CA1 | Web E2E | funcional | web | ✅ passed |
| HU-N-01 | la respuesta del registro cumple el contrato y no expone el pin ni el dni | — | N1 | tecnico | api | ✅ passed |
| HU-N-01 | registro con celular que no cumple rn02 caso [10 digitos-9112223334] | CA3 | N1 | funcional | api | ✅ passed |
| HU-N-01 | registro con celular que no cumple rn02 caso [8 digitos-91122233] | CA3 | N1 | funcional | api | ✅ passed |
| HU-N-01 | registro con celular que no cumple rn02 caso [no empieza con 9-811222333] | CA3 | N1 | funcional | api | ✅ passed |
| HU-N-01 | registro con correo inválido o ya usado caso [sin arroba-lucia.correo.pe-422-CORREO_INVALIDO] | CA5 | N1 | funcional | api | ✅ passed |
| HU-N-01 | registro con correo inválido o ya usado caso [sin dominio-lucia@-422-CORREO_INVALIDO] | CA5 | N1 | funcional | api | ✅ passed |
| HU-N-01 | registro con correo inválido o ya usado caso [usado, otras mayusculas-ANA.TORRES@correo.pe-409-CORREO_REGISTRADO] | CA5 | N1 | funcional | api | ✅ passed |
| HU-N-01 | registro con cuerpo inválido según el contrato caso [JSON mal formado-{"dni": "61234567",] | — | N1 | tecnico | api | ✅ passed |
| HU-N-01 | registro con cuerpo inválido según el contrato caso [nombres de 1 letra-{"dni": "61234567", "nombres": "L", "celular": "911222333", "pin": "5173"}] | — | N1 | tecnico | api | ✅ passed |
| HU-N-01 | registro con cuerpo inválido según el contrato caso [sin campos-{}] | — | N1 | tecnico | api | ✅ passed |
| HU-N-01 | registro con dni que no cumple rn01 caso [7 digitos-6123456] | CA2 | N1 | funcional | api | ✅ passed |
| HU-N-01 | registro con dni que no cumple rn01 caso [9 digitos-612345678] | CA2 | N1 | funcional | api | ✅ passed |
| HU-N-01 | registro con dni que no cumple rn01 caso [con letras-6123456A] | CA2 | N1 | funcional | api | ✅ passed |
| HU-N-01 | registro con pin que no cumple rn03 caso [3 digitos-517] | CA4 | N1 | funcional | api | ✅ passed |
| HU-N-01 | registro con pin que no cumple rn03 caso [5 digitos-51734] | CA4 | N1 | funcional | api | ✅ passed |
| HU-N-01 | registro con pin que no cumple rn03 caso [secuencia ascendente-1234] | CA4 | N1 | funcional | api | ✅ passed |
| HU-N-01 | registro con pin que no cumple rn03 caso [secuencia descendente-4321] | CA4 | N1 | funcional | api | ⚠️ xfailed → [DEF-08](defectos.md#def-08-se-acepta-un-pin-en-secuencia-descendente) |
| HU-N-01 | registro con pin que no cumple rn03 caso [todos iguales-1111] | CA4 | N1 | funcional | api | ✅ passed |
| HU-N-01 | registro con un celular ya registrado caso [cuenta activa-987654321] | CA3 | N1 | funcional | api | ✅ passed |
| HU-N-01 | registro con un celular ya registrado caso [cuenta cerrada-934567812] | CA3 | N1 | funcional | api | ✅ passed |
| HU-N-01 | registro exitoso con saldo cero y sms de bienvenida | CA1, CA6 | N1 | funcional | api | ✅ passed |
| HU-N-01 | Un visitante crea su cuenta y la usa con saldo S/ 0.00 | CA1 | Web E2E | funcional | web | ✅ passed |
| HU-N-02 | credenciales erróneas dan un mensaje genérico caso [PIN incorrecto-987654321-9999] | CA2 | N2 | funcional | api | ✅ passed |
| HU-N-02 | credenciales erróneas dan un mensaje genérico caso [celular inexistente-911999999-4826] | CA2 | N2 | funcional | api | ✅ passed |
| HU-N-02 | dos intentos fallidos todavía no bloquean la cuenta | CA3 | N2 | funcional | api | ✅ passed |
| HU-N-02 | durante el bloqueo ni el pin correcto permite ingresar | CA4 | N2 | funcional | api | ✅ passed |
| HU-N-02 | el tercer intento fallido consecutivo bloquea la cuenta y avisa por sms | CA3 | N2 | funcional | api | ✅ passed |
| HU-N-02 | ingresar desde un dispositivo desconocido envía un sms de alerta | CA6 | N2 | funcional | api | ✅ passed |
| HU-N-02 | la respuesta del login cumple el contrato | — | N2 | tecnico | api | ✅ passed |
| HU-N-02 | login con cuerpo inválido según el contrato caso [PIN num\xe9rico-{"celular": "987654321", "pin": 4826}] | — | N2 | tecnico | api | ✅ passed |
| HU-N-02 | login con cuerpo inválido según el contrato caso [sin PIN-{"celular": "987654321"}] | — | N2 | tecnico | api | ✅ passed |
| HU-N-02 | login con cuerpo inválido según el contrato caso [sin celular-{"pin": "4826"}] | — | N2 | tecnico | api | ✅ passed |
| HU-N-02 | login correcto entrega un token de 30 minutos y una sesión | CA1 | N2 | funcional | api | ✅ passed |
| HU-N-02 | método http no permitido en el login | — | N2 | tecnico | api | ✅ passed |
| HU-N-02 | pasados los 15 minutos de bloqueo se puede ingresar | CA4 | N2 | funcional | api | ✅ passed |
| HU-N-02 | un login exitoso reinicia el conteo de intentos fallidos | CA3 | N2 | funcional | api | ⚠️ xfailed → [DEF-09](defectos.md#def-09-un-login-exitoso-no-reinicia-el-conteo-de-intentos-fallidos) |
| HU-N-02 | una cuenta cerrada no puede iniciar sesión | CA5 | N2 | funcional | api | ✅ passed |
| HU-N-02 | Ana inicia sesión con sus credenciales correctas | CA1 | Web E2E | funcional | web | ✅ passed |
| HU-N-02 | Credenciales erróneas (PIN incorrecto) muestran un mensaje genérico | CA2 | Web E2E | funcional | web | ✅ passed |
| HU-N-02 | Credenciales erróneas (celular inexistente) muestran un mensaje genérico | CA2 | Web E2E | funcional | web | ✅ passed |
| HU-N-02 | La cuenta se bloquea al tercer intento fallido y ni el PIN correcto permite ingresar | CA3, CA4 | Web E2E | funcional | web | ✅ passed |
| HU-N-03 | cerrar sesión exige un token válido caso [token basura-abc.def.ghi] | — | N3 | tecnico | api | ✅ passed |
| HU-N-03 | cerrar sesión exige un token válido caso [token vacio-] | — | N3 | tecnico | api | ✅ passed |
| HU-N-03 | cerrar sesión responde 204 | CA1 | N3 | funcional | api | ✅ passed |
| HU-N-03 | cerrar una sesión no afecta mis otras sesiones activas | CA2 | N3 | funcional | api | ✅ passed |
| HU-N-03 | después de cerrar sesión el token ya no es válido | CA1 | N3 | funcional | api | ⚠️ xfailed → [DEF-07](defectos.md#def-07-cerrar-sesión-no-invalida-el-token) |
| HU-N-03 | Ana cierra sesión y ya no puede abrir páginas privadas | CA1 | Web E2E | funcional | web | ✅ passed |
| HU-N-04 | el perfil con un token inválido responde 401 | CA3 | N4 | tecnico | api | ✅ passed |
| HU-N-04 | el perfil con un token vencido 31 minutos responde 401 | CA3 | N4 | tecnico | api | ✅ passed |
| HU-N-04 | el perfil cumple el contrato y no expone el pin | — | N4 | tecnico | api | ✅ passed |
| HU-N-04 | el perfil sin token responde 401 | CA3 | N4 | tecnico | api | ✅ passed |
| HU-N-04 | el saldo cumple el contrato | — | N6 | tecnico | api | ✅ passed |
| HU-N-04 | el saldo sin token responde 401 | CA3 | N6 | tecnico | api | ✅ passed |
| HU-N-04 | veo mi perfil con el dni enmascarado | CA2 | N4 | funcional | api | ✅ passed |
| HU-N-04 | veo mi saldo disponible en soles | CA1 | N6 | funcional | api | ✅ passed |
| HU-N-04 | Ana ve su saldo y su perfil con el DNI enmascarado | CA1, CA2 | Web E2E | funcional | web | ✅ passed |
| HU-N-05 | editar con datos inválidos caso [correo de otra cuenta activa-{"correo": "BRUNO.DIAZ@correo.pe"}-409-CORREO_REGISTRADO] | CA1 | N5 | funcional | api | ✅ passed |
| HU-N-05 | editar con datos inválidos caso [correo sin dominio-{"correo": "ana@"}-422-CORREO_INVALIDO] | CA1 | N5 | funcional | api | ✅ passed |
| HU-N-05 | editar con datos inválidos caso [nombres de 1 caracter-{"nombres": "A"}-422-PERFIL_INVALIDO] | CA1 | N5 | funcional | api | ✅ passed |
| HU-N-05 | editar con datos inválidos caso [nombres solo espacios-{"nombres": "     "}-422-PERFIL_INVALIDO] | CA1 | N5 | funcional | api | ✅ passed |
| HU-N-05 | editar el perfil con un tipo de dato inválido responde 422 | — | N5 | tecnico | api | ✅ passed |
| HU-N-05 | editar el perfil sin token responde 401 | — | N5 | tecnico | api | ✅ passed |
| HU-N-05 | edito mis nombres y mi correo y recibo un sms de aviso | CA1, CA3 | N5 | funcional | api | ✅ passed |
| HU-N-05 | el dni y el celular enviados al editar se ignoran | CA2 | N5 | funcional | api | ✅ passed |
| HU-N-05 | longitud de los nombres de 2 a 80 caracteres caso [2 (limite)-Al-200--] | CA1 | N5 | funcional | api | ✅ passed |
| HU-N-05 | longitud de los nombres de 2 a 80 caracteres caso [80 (limite)-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa-200--] | CA1 | N5 | funcional | api | ✅ passed |
| HU-N-05 | longitud de los nombres de 2 a 80 caracteres caso [81 (invalido)-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa-422-PERFIL_INVALIDO] | CA1 | N5 | funcional | api | ✅ passed |
| HU-N-05 | puedo quitar mi correo enviándolo vacío | CA1 | N5 | funcional | api | ✅ passed |
| HU-N-05 | Ana actualiza sus nombres y su correo | CA1 | Web E2E | funcional | web | ✅ passed |
| HU-N-06 | cerrar la cuenta con un pin incorrecto | CA1 | N7 | funcional | api | ✅ passed |
| HU-N-06 | cerrar la cuenta sin pin responde 422 | — | N7 | tecnico | api | ✅ passed |
| HU-N-06 | cerrar la cuenta sin token responde 401 | — | N7 | tecnico | api | ✅ passed |
| HU-N-06 | cierro mi cuenta con saldo cero y ya no puedo usarla | CA1, CA4 | N7 | funcional | api | ✅ passed |
| HU-N-06 | no se cierra la cuenta con solicitudes de dinero pendientes | CA3 | N7 | funcional | api | ✅ passed |
| HU-N-06 | solo se cierra con saldo exactamente s 000 saldo [0.01] | CA2 | N7 | funcional | api | ✅ passed |
| HU-N-06 | solo se cierra con saldo exactamente s 000 saldo [1500.00] | CA2 | N7 | funcional | api | ✅ passed |
| HU-N-06 | Ana no puede cerrar su cuenta mientras tenga saldo | CA2 | Web E2E | funcional | web | ✅ passed |
| HU-N-06 | Un cliente con saldo S/ 0.00 cierra su cuenta y ya no puede ingresar | CA1, CA4 | Web E2E | funcional | web | ✅ passed |
| HU-N-07 | destino no permitido según rn07 caso [a mi mismo-987654321-422-TRANSFERENCIA_A_SI_MISMO] | CA2 | N8 | funcional | api | ✅ passed |
| HU-N-07 | destino no permitido según rn07 caso [celular invalido-812345678-422-CELULAR_INVALIDO] | CA2 | N8 | funcional | api | ✅ passed |
| HU-N-07 | destino no permitido según rn07 caso [celular no registrado-911999999-404-DESTINO_NO_REGISTRADO] | CA2 | N8 | funcional | api | ✅ passed |
| HU-N-07 | el comprobante de la transferencia cumple el contrato | — | N8 | tecnico | api | ✅ passed |
| HU-N-07 | el saldo debe cubrir el monto caso [igual al saldo-50.00-201--] | CA2 | N8 | funcional | api | ✅ passed |
| HU-N-07 | el saldo debe cubrir el monto caso [supera por 0.01-50.01-422-SALDO_INSUFICIENTE] | CA2 | N8 | funcional | api | ✅ passed |
| HU-N-07 | la suma del día no puede superar el límite diario | CA2 | N8 | funcional | api | ✅ passed |
| HU-N-07 | monto de la transferencia según rn05 caso [3 decimales-10.001-422-MONTO_INVALIDO] | CA2 | N8 | funcional | api | ✅ passed |
| HU-N-07 | monto de la transferencia según rn05 caso [cero-0.00-422-MONTO_INVALIDO] | CA2 | N8 | funcional | api | ✅ passed |
| HU-N-07 | monto de la transferencia según rn05 caso [maximo 500.00-500.00-201--] | CA2 | N8 | funcional | api | ✅ passed |
| HU-N-07 | monto de la transferencia según rn05 caso [minimo 0.01-0.01-201--] | CA2 | N8 | funcional | api | ✅ passed |
| HU-N-07 | monto de la transferencia según rn05 caso [negativo--5.00-422-MONTO_INVALIDO] | CA2 | N8 | funcional | api | ✅ passed |
| HU-N-07 | monto de la transferencia según rn05 caso [sobre el maximo-500.01-422-MONTO_INVALIDO] | CA2 | N8 | funcional | api | ✅ passed |
| HU-N-07 | no puedo transferir usando un contacto de otro usuario | — | N8 | tecnico | api | ✅ passed |
| HU-N-07 | no se puede transferir a una cuenta cerrada | CA2 | N8 | funcional | api | ⚠️ xfailed → [DEF-10](defectos.md#def-10-se-puede-transferir-a-una-cuenta-cerrada) |
| HU-N-07 | transferencia a otro usuario qolqe sin comisión | CA3, CA4 | N8 | funcional | api | ✅ passed |
| HU-N-07 | transferencia con cuerpo inválido caso [descripcion de 61-{"celular_destino": "912345678", "monto": "10.00", "descripcion": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"}-SOLICITUD_INVALIDA] | — | N8 | tecnico | api | ✅ passed |
| HU-N-07 | transferencia con cuerpo inválido caso [monto no numerico-{"celular_destino": "912345678", "monto": "diez"}-SOLICITUD_INVALIDA] | — | N8 | tecnico | api | ✅ passed |
| HU-N-07 | transferencia con cuerpo inválido caso [sin destino-{"monto": "10.00"}-DESTINO_REQUERIDO] | — | N8 | tecnico | api | ✅ passed |
| HU-N-07 | transferencia con cuerpo inválido caso [sin monto-{"celular_destino": "912345678"}-SOLICITUD_INVALIDA] | — | N8 | tecnico | api | ✅ passed |
| HU-N-07 | transferencia con cuerpo inválido caso [tipo desconocido-{"tipo": "OTRO", "celular_destino": "912345678", "monto": "10.00"}-SOLICITUD_INVALIDA] | — | N8 | tecnico | api | ✅ passed |
| HU-N-07 | transferencia eligiendo un contacto frecuente | CA1 | N8 | funcional | api | ✅ passed |
| HU-N-07 | transferencias simultáneas no superan el límite diario | CA5 | N8 | funcional | api | ⚠️ xfailed → [DEF-14](defectos.md#def-14-transferencias-simultáneas-superan-el-límite-diario) |
| HU-N-07 | transferir sin token responde 401 | — | N8 | tecnico | api | ✅ passed |
| HU-N-07 | Ana transfiere a Bruno, ve la comisión antes de confirmar y recibe el comprobante | CA3, CA4 | Web E2E | funcional | web | ✅ passed |
| HU-N-07 | No se puede transferir a un celular que no está registrado | CA2 | Web E2E | funcional | web | ✅ passed |
| HU-N-08 | cci que no tiene 20 dígitos caso [19 digitos-0021910012345678901] | CA1 | N8 | funcional | api | ✅ passed |
| HU-N-08 | cci que no tiene 20 dígitos caso [21 digitos-002191001234567890123] | CA1 | N8 | funcional | api | ✅ passed |
| HU-N-08 | cci que no tiene 20 dígitos caso [con letras-0021910012345678901A] | CA1 | N8 | funcional | api | ✅ passed |
| HU-N-08 | comisión interbancaria con mínimo y máximo caso [bajo el minimo-20.00-1.00] | CA2 | N8 | funcional | api | ✅ passed |
| HU-N-08 | comisión interbancaria con mínimo y máximo caso [sobre el maximo-400.00-5.00] | CA2 | N8 | funcional | api | ✅ passed |
| HU-N-08 | el saldo debe cubrir el monto más la comisión interbancaria | CA2 | N8 | funcional | api | ⚠️ xfailed → [DEF-12](defectos.md#def-12-el-saldo-puede-quedar-negativo-en-una-transferencia-interbancaria) |
| HU-N-08 | las transferencias interbancarias cuentan para el límite diario | CA2 | N8 | funcional | api | ⚠️ xfailed → [DEF-13](defectos.md#def-13-las-transferencias-interbancarias-no-cuentan-para-el-límite-diario) |
| HU-N-08 | transferencia interbancaria con comisión y cci enmascarado | CA2, CA3 | N8 | funcional | api | ✅ passed |
| HU-N-08 | transferencia interbancaria sin cci | CA1 | N8 | funcional | api | ✅ passed |
| HU-N-08 | Ana transfiere a otro banco y paga la comisión de 1.5 % | CA2 | Web E2E | funcional | web | ✅ passed |
| HU-N-09 | la simulación cumple el contrato | — | N9 | tecnico | api | ✅ passed |
| HU-N-09 | simular con parámetros inválidos según el contrato caso [monto no numero-monto=diez] | — | N9 | tecnico | api | ✅ passed |
| HU-N-09 | simular con parámetros inválidos según el contrato caso [sin monto-tipo=QOLQE] | — | N9 | tecnico | api | ✅ passed |
| HU-N-09 | simular con parámetros inválidos según el contrato caso [tipo desconocido-monto=10&tipo=OTRO] | — | N9 | tecnico | api | ✅ passed |
| HU-N-09 | simular con un monto inválido caso [3 decimales-10.005] | CA1 | N9 | funcional | api | ✅ passed |
| HU-N-09 | simular con un monto inválido caso [cero-0] | CA1 | N9 | funcional | api | ✅ passed |
| HU-N-09 | simular con un monto inválido caso [sobre el maximo-500.01] | CA1 | N9 | funcional | api | ✅ passed |
| HU-N-09 | simular la comisión interbancaria caso [1.5 %-100.00-1.50-101.50] | CA1 | N9 | funcional | api | ✅ passed |
| HU-N-09 | simular la comisión interbancaria caso [justo en el maximo-333.33-5.00-338.33] | CA1 | N9 | funcional | api | ✅ passed |
| HU-N-09 | simular la comisión interbancaria caso [justo en el minimo-66.67-1.00-67.67] | CA1 | N9 | funcional | api | ✅ passed |
| HU-N-09 | simular la comisión interbancaria caso [maximo S/ 5.00-500.00-5.00-505.00] | CA1 | N9 | funcional | api | ✅ passed |
| HU-N-09 | simular la comisión interbancaria caso [minimo S/ 1.00-20.00-1.00-21.00] | CA1 | N9 | funcional | api | ✅ passed |
| HU-N-09 | simular la comisión interbancaria caso [redondeo comercial 0.005-71.00-1.07-72.07] | CA1 | N9 | funcional | api | ⚠️ xfailed → [DEF-11](defectos.md#def-11-la-comisión-interbancaria-no-usa-redondeo-comercial) |
| HU-N-09 | simular la comisión sin token responde 401 | — | N9 | tecnico | api | ✅ passed |
| HU-N-09 | simular una transferencia qolqe no tiene comisión ni mueve el saldo | CA1 | N9 | funcional | api | ✅ passed |
| HU-N-09 | Ana transfiere a Bruno, ve la comisión antes de confirmar y recibe el comprobante | CA3, CA4 | Web E2E | funcional | web | ✅ passed |
| HU-N-09 | Ana transfiere a otro banco y paga la comisión de 1.5 % | CA2 | Web E2E | funcional | web | ✅ passed |
| (sin HU) | la app responde | — | Otros (humo, métodos no declarados) | tecnico | api | ✅ passed |
| (sin HU) | endpoint g2 cumple el contrato openapi [E1] | — | E1 | tecnico | contrato | ✅ passed |
| (sin HU) | endpoint g2 cumple el contrato openapi [E2] | — | E2 | tecnico | contrato | ✅ passed |
| (sin HU) | endpoint g2 cumple el contrato openapi [E3] | — | E3 | tecnico | contrato | ✅ passed |
| (sin HU) | endpoint g2 cumple el contrato openapi [E4] | — | E4 | tecnico | contrato | ✅ passed |
| (sin HU) | endpoint g2 cumple el contrato openapi [E5] | — | E5 | tecnico | contrato | ✅ passed |
| (sin HU) | endpoint g2 cumple el contrato openapi [E6] | — | E6 | tecnico | contrato | ✅ passed |
| (sin HU) | endpoint g2 cumple el contrato openapi [E7] | — | E7 | tecnico | contrato | ✅ passed |
| (sin HU) | endpoint g2 cumple el contrato openapi [E8] | — | E8 | tecnico | contrato | ✅ passed |
| (sin HU) | endpoint g2 cumple el contrato openapi [E9] | — | E9 | tecnico | contrato | ✅ passed |
| (sin HU) | endpoint g2 cumple el contrato openapi [metodo-no-declarado] | — | Otros (humo, métodos no declarados) | tecnico | contrato | ✅ passed |

Leyenda: ✅ pasa · ⚠️ fallo esperado: la prueba detecta un defecto ya reportado en [defectos.md](defectos.md) · ❌ falla (fallo nuevo, hay que analizarlo) · ⏭️ omitida.
