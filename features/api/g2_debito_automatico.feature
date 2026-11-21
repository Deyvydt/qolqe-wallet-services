# language: es
# ─────────────────────────────────────────────────────────────────────────
# QUÉ ES: escenarios de prueba en Gherkin (lenguaje natural) de HU-G2-05 (débito automático, extra).
# PARA QUÉ: verificar que el proceso diario solo pague, sin mora, las deudas que vencen
#   ese día y no las que ya estaban vencidas.
# CÓMO SE USA: no se ejecuta solo. pytest-bdd lee este archivo y conecta cada
#   frase (Dado/Cuando/Entonces) con una función de tests/api/conftest.py.
#   Ejecutar: pytest -v   ·   solo esta HU: pytest -v -m "HU-G2-05"
# ETIQUETAS (@...): trazabilidad HU → criterio de aceptación (CA) → técnica.
# ─────────────────────────────────────────────────────────────────────────
@G2 @HU-G2-05 @E10
Característica: HU-G2-05 Débito automático (Prioridad Media, extra)
  Como cliente
  quiero que mis servicios afiliados se paguen solos el día de su vencimiento
  para no olvidar pagarlos

  Antecedentes:
    Dado que los datos de Qolqe están reiniciados
    Y que inicié sesión como "987654321" con PIN "4826"

  @funcional @CA2 @actor-sistema
  Escenario: El proceso diario paga, sin mora, la deuda que vence hoy
    Dado que afilié "ELECTRO" "10000002" con alias "Luz hoy" y débito automático activo
    Cuando se ejecuta el proceso diario
    Entonces se registró 1 pago por débito automático de "ELECTRO" "10000002" con mora "0.00"

  @funcional @CA4 @actor-sistema
  Escenario: Las deudas ya vencidas antes de activar el débito NO se pagan automáticamente
    Dado que afilié "ELECTRO" "10000003" con alias "Luz vencida" y débito automático activo
    Cuando se ejecuta el proceso diario
    Entonces se registraron 0 pagos por débito automático de "ELECTRO" "10000003"

  @funcional @CA3 @actor-sistema @efecto
  Escenario: Sin saldo, la deuda queda pendiente y el titular recibe un SMS
    Dado que mi saldo es "0.00"
    Y que afilié "ELECTRO" "10000002" con alias "Luz hoy" y débito automático activo
    Cuando se ejecuta el proceso diario
    Entonces el proceso diario reporta 0 débitos pagados y 1 fallidos
    Y se registraron 0 pagos por débito automático de "ELECTRO" "10000002"
    Y la deuda "ELECTRO" "10000002" sigue pendiente
    Y recibí un SMS que dice "No pudimos pagar con débito automático Luz hoy"

  @funcional @CA2 @actor-sistema @particion
  Escenario: Una afiliación sin débito automático no se paga en el proceso diario
    Dado que afilié "ELECTRO" "10000002" con alias "Luz hoy"
    Cuando se ejecuta el proceso diario
    Entonces el proceso diario reporta 0 débitos pagados y 0 fallidos
    Y la deuda "ELECTRO" "10000002" sigue pendiente

  @tecnico @actor-sistema @efecto
  Escenario: Ejecutar dos veces el proceso diario no cobra dos veces la misma deuda
    Dado que afilié "ELECTRO" "10000002" con alias "Luz hoy" y débito automático activo
    Cuando se ejecuta el proceso diario
    Y se ejecuta el proceso diario
    Entonces el proceso diario reporta 0 débitos pagados y 0 fallidos
    Y se registró 1 pago por débito automático de "ELECTRO" "10000002" con mora "0.00"

  @tecnico @contrato
  Escenario: La respuesta del proceso diario tiene todos sus campos y usa la fecha del reloj
    Cuando se ejecuta el proceso diario
    Entonces la respuesta tiene estado 200
    Y la respuesta tiene los campos "fecha, recargas_exitosas, recargas_fallidas, debitos_pagados, debitos_fallidos"
    Y la fecha del proceso diario es la fecha del reloj
