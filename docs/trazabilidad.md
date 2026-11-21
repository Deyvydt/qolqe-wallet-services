<!-- QUÉ ES: matriz de trazabilidad generada automáticamente por .github/scripts/trazabilidad.py.
     No editar a mano: se vuelve a generar en cada ejecución del pipeline. -->

# Matriz de trazabilidad · G2 Pago de servicios

Run [#10](https://github.com/Deyvydt/qolqe-wallet-services/actions/runs/44845599753) · commit [`201791d`](https://github.com/Deyvydt/qolqe-wallet-services/commit/201791dc6556318665d9e3785f2e63637b1493f0) · rama `entrega-final` · 20/11/2026 21:25 (hora de Lima)

Cada fila une una **historia de usuario (HU)** con el **caso de prueba** que la verifica, el **nivel** donde se prueba y el **resultado de esta ejecución**.

**Totales:** ✅ 142 pasan · ⚠️ 10 fallos esperados (defectos conocidos) · ❌ 0 fallan · ⏭️ 2 omitidas

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
| Otros (humo, métodos no declarados) | 0 | 0 | 0 | 0 | 2 | 2 | 0 | 0 | 2 |
| Web E2E | 30 | 28 | 0 | 0 | 0 | 0 | 0 | 0 | 30 |
| **TOTAL** | 102 | 90 | 10 | 0 | 52 | 52 | 0 | 0 | 154 |

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
| HU-N-01 | 1 | web 1 | 1 | 0 | 0 | 0 | — | ✅ OK |
| HU-N-02 | 4 | web 4 | 4 | 0 | 0 | 0 | — | ✅ OK |
| HU-N-03 | 1 | web 1 | 1 | 0 | 0 | 0 | — | ✅ OK |
| HU-N-04 | 1 | web 1 | 1 | 0 | 0 | 0 | — | ✅ OK |
| HU-N-05 | 1 | web 1 | 1 | 0 | 0 | 0 | — | ✅ OK |
| HU-N-06 | 2 | web 2 | 2 | 0 | 0 | 0 | — | ✅ OK |
| HU-N-07 | 2 | web 2 | 2 | 0 | 0 | 0 | — | ✅ OK |
| HU-N-08 | 1 | web 1 | 1 | 0 | 0 | 0 | — | ✅ OK |
| HU-N-09 | 2 | web 2 | 2 | 0 | 0 | 0 | — | ✅ OK |
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
| HU-G2-01 | CP-W01 · Ana paga su recibo de luz y ve el comprobante | CA1, CA4 | Web E2E | funcional | web | ✅ passed |
| HU-G2-01 | CP-W01 · Ana paga su recibo de luz y ve el comprobante | CA1, CA4 | Web E2E | funcional | web | ✅ passed |
| HU-G2-01 | CP-W02 · Ana paga su recibo de agua | CA1, CA4 | Web E2E | funcional | web | ✅ passed |
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
| HU-G2-02 | CP-W01 · Ana paga su recibo de luz y ve el comprobante | CA1, CA4 | Web E2E | funcional | web | ✅ passed |
| HU-G2-02 | CP-W01 · Ana paga su recibo de luz y ve el comprobante | CA1, CA4 | Web E2E | funcional | web | ✅ passed |
| HU-G2-02 | CP-W02 · Ana paga su recibo de agua | CA1, CA4 | Web E2E | funcional | web | ✅ passed |
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
| HU-N-01 | Un visitante crea su cuenta y la usa con saldo S/ 0.00 | CA1 | Web E2E | funcional | web | ✅ passed |
| HU-N-02 | Ana inicia sesión con sus credenciales correctas | CA1 | Web E2E | funcional | web | ✅ passed |
| HU-N-02 | Credenciales erróneas (PIN incorrecto) muestran un mensaje genérico | CA2 | Web E2E | funcional | web | ✅ passed |
| HU-N-02 | Credenciales erróneas (celular inexistente) muestran un mensaje genérico | CA2 | Web E2E | funcional | web | ✅ passed |
| HU-N-02 | La cuenta se bloquea al tercer intento fallido y ni el PIN correcto permite ingresar | CA3, CA4 | Web E2E | funcional | web | ✅ passed |
| HU-N-03 | Ana cierra sesión y ya no puede abrir páginas privadas | CA1 | Web E2E | funcional | web | ✅ passed |
| HU-N-04 | Ana ve su saldo y su perfil con el DNI enmascarado | CA1, CA2 | Web E2E | funcional | web | ✅ passed |
| HU-N-05 | Ana actualiza sus nombres y su correo | CA1 | Web E2E | funcional | web | ✅ passed |
| HU-N-06 | Ana no puede cerrar su cuenta mientras tenga saldo | CA2 | Web E2E | funcional | web | ✅ passed |
| HU-N-06 | Un cliente con saldo S/ 0.00 cierra su cuenta y ya no puede ingresar | CA1, CA4 | Web E2E | funcional | web | ✅ passed |
| HU-N-07 | Ana transfiere a Bruno, ve la comisión antes de confirmar y recibe el comprobante | CA3, CA4 | Web E2E | funcional | web | ✅ passed |
| HU-N-07 | No se puede transferir a un celular que no está registrado | CA2 | Web E2E | funcional | web | ✅ passed |
| HU-N-08 | Ana transfiere a otro banco y paga la comisión de 1.5 % | CA2 | Web E2E | funcional | web | ✅ passed |
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
