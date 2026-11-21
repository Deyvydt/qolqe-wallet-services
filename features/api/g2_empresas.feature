# language: es
# ─────────────────────────────────────────────────────────────────────────
# QUÉ ES: escenarios del endpoint E1 GET /api/servicios/empresas (catálogo de empresas, HU-G2-01 CA1).
# PARA QUÉ: verificar que el catálogo lista las empresas afiliadas, ordenadas por nombre,
#   con todos sus campos; que es público (no exige token, igual que /api/recargas/configuracion)
#   y que rechaza los métodos no declarados.
# ETIQUETAS: @funcional / @tecnico = tipo de caso · @E1 = endpoint · @HU/@CA = trazabilidad.
# ─────────────────────────────────────────────────────────────────────────
@G2 @HU-G2-01 @E1
Característica: E1 Catálogo de empresas de servicios
  Como cliente
  quiero ver qué empresas puedo pagar en Qolqe
  para elegir la empresa de mi recibo

  Antecedentes:
    Dado que los datos de Qolqe están reiniciados
    Y que inicié sesión como "987654321" con PIN "4826"

  @funcional @CA1 @camino-feliz
  Escenario: El catálogo lista las empresas ordenadas por nombre
    Cuando envío "GET" a "/api/servicios/empresas"
    Entonces la respuesta tiene estado 200
    Y la lista tiene los códigos "AGUA, ELECTRO, INTERNET" en ese orden

  @funcional @CA1 @particion
  Escenario: Una empresa que no está en el catálogo no tiene deudas consultables
    Cuando envío "GET" a "/api/servicios/empresas"
    Entonces la lista no tiene el código "NOEXISTE"
    Y al consultar las deudas de la empresa "NOEXISTE" y suministro "10000001" responde 404 "EMPRESA_NO_ENCONTRADA"

  @tecnico @contrato
  Escenario: Cada empresa tiene código, nombre y rubro
    Cuando envío "GET" a "/api/servicios/empresas"
    Entonces la respuesta tiene estado 200
    Y cada elemento de la lista tiene los campos "codigo, nombre, rubro"

  @tecnico @seguridad
  Escenario: El catálogo es público y responde sin token
    Cuando envío "GET" a "/api/servicios/empresas" sin token
    Entonces la respuesta tiene estado 200
    Y la lista tiene los códigos "AGUA, ELECTRO, INTERNET" en ese orden

  @tecnico @particion
  Escenario: Método HTTP no permitido en el catálogo
    Cuando envío "POST" a "/api/servicios/empresas" con el cuerpo {"codigo": "GAS"}
    Entonces la respuesta tiene estado 405
