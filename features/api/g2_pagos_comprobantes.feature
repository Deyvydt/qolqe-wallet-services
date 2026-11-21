# language: es
# ─────────────────────────────────────────────────────────────────────────
# QUÉ ES: escenarios de HU-G2-07 (ver mis pagos y comprobantes):
#   E4 GET /api/servicios/pagos (lista, orden y filtro ?afiliacion_id)
#   E5 GET /api/servicios/pagos/{codigo_operacion} (comprobante)
# ETIQUETAS: @funcional / @tecnico = tipo de caso · @E4/@E5 = endpoint · @HU/@CA = trazabilidad.
# ─────────────────────────────────────────────────────────────────────────
@G2 @HU-G2-07
Característica: HU-G2-07 Ver mis pagos y comprobantes (Prioridad Media)
  Como cliente
  quiero ver mis pagos de servicios y sus comprobantes
  para tener constancia de lo que pagué

  Antecedentes:
    Dado que los datos de Qolqe están reiniciados
    Y que inicié sesión como "987654321" con PIN "4826"

  # ------------------------------------------------------------- E4 GET /api/servicios/pagos

  @funcional @CA1 @camino-feliz @E4
  Escenario: Mis pagos se listan del más reciente al más antiguo
    Dado que pagué la deuda "ELECTRO" "10000001"
    Y que pagué la deuda "AGUA" "2000000008"
    Cuando envío "GET" a "/api/servicios/pagos"
    Entonces la respuesta tiene estado 200
    Y mis pagos son "AGUA 2000000008, ELECTRO 10000001" en ese orden

  @funcional @CA1 @particion @E4
  Escenario: Filtrar mis pagos por afiliación muestra solo los de ese suministro
    Dado que pagué la deuda "ELECTRO" "10000001"
    Y que pagué la deuda "AGUA" "2000000008"
    Cuando consulto mis pagos de la afiliación "Luz casa"
    Entonces la respuesta tiene estado 200
    Y mis pagos son "ELECTRO 10000001" en ese orden

  @funcional @CA1 @particion @E4
  Escenario: Sin pagos realizados la lista está vacía
    Cuando envío "GET" a "/api/servicios/pagos"
    Entonces la respuesta tiene estado 200
    Y la lista está vacía

  @funcional @CA1 @E4
  Escenario: Filtrar por una afiliación inexistente
    Cuando envío "GET" a "/api/servicios/pagos?afiliacion_id=999999"
    Entonces la respuesta tiene estado 404 y código "AFILIACION_NO_ENCONTRADA"

  @tecnico @seguridad @E4
  Escenario: Filtrar por la afiliación de otro usuario responde 404
    Dado que anoté el id de mi afiliación "Luz casa"
    Y que inicié sesión como "912345678" con PIN "7391"
    Cuando consulto mis pagos de la afiliación anotada
    Entonces la respuesta tiene estado 404 y código "AFILIACION_NO_ENCONTRADA"

  @tecnico @seguridad @E4
  Escenario: Ver mis pagos sin token
    Cuando envío "GET" a "/api/servicios/pagos" sin token
    Entonces la respuesta tiene estado 401 y código "NO_AUTENTICADO"

  @tecnico @particion @E4
  Esquema del escenario: afiliacion_id con tipo de dato inválido
    Cuando envío "GET" a "/api/servicios/pagos?afiliacion_id=<valor>"
    Entonces la respuesta tiene estado 422 y código "SOLICITUD_INVALIDA"

    Ejemplos:
      | valor |
      | abc   |
      | 1.5   |

  # ------------------------------------------------------------- E5 GET /api/servicios/pagos/{codigo}

  @funcional @CA2 @camino-feliz @E5
  Escenario: El dueño ve el comprobante de su pago
    Dado que pagué la deuda "ELECTRO" "10000001"
    Cuando consulto el comprobante de ese pago
    Entonces la respuesta tiene estado 200
    Y el comprobante muestra monto "120.00", mora "0.00" y total "120.00"
    Y el comprobante tiene el mismo código de operación del pago

  @funcional @CA2 @E5
  Escenario: Comprobante de un código de operación inexistente
    Cuando envío "GET" a "/api/servicios/pagos/PAG00000000000000000"
    Entonces la respuesta tiene estado 404 y código "PAGO_NO_ENCONTRADO"

  @tecnico @contrato @E5
  Escenario: El comprobante tiene todos sus campos
    Dado que pagué la deuda "ELECTRO" "10000001"
    Cuando consulto el comprobante de ese pago
    Entonces la respuesta tiene estado 200
    Y el comprobante tiene los campos "codigo_operacion, empresa, suministro, periodo, monto, mora, total, origen, fecha"

  @tecnico @seguridad @E5
  Escenario: Ver un comprobante sin token
    Dado que pagué la deuda "ELECTRO" "10000001"
    Cuando consulto el comprobante de ese pago sin token
    Entonces la respuesta tiene estado 401 y código "NO_AUTENTICADO"
