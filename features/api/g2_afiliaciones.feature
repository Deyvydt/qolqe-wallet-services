# language: es
# ─────────────────────────────────────────────────────────────────────────
# QUÉ ES: escenarios de las afiliaciones (HU-G2-03 a HU-G2-06):
#   E6 GET    /api/servicios/afiliaciones        (HU-G2-04: lista y situación)
#   E7 POST   /api/servicios/afiliaciones        (HU-G2-03: afiliar)
#   E8 PUT    /api/servicios/afiliaciones/{id}   (HU-G2-05 CA1: alias y débito automático)
#   E9 DELETE /api/servicios/afiliaciones/{id}   (HU-G2-06: desafiliar)
# DATOS SEMILLA de Ana (987654321): "Agua depa" (AGUA 2000000008, débito activo, vence en 3 días),
#   "Internet casa" (INTERNET 300000000007, en cobranza) y "Luz casa" (ELECTRO 10000001, vence en 10 días).
# ETIQUETAS: @funcional / @tecnico = tipo de caso · @E6..@E9 = endpoint · @HU/@CA = trazabilidad.
# ─────────────────────────────────────────────────────────────────────────
@G2
Característica: Afiliaciones de servicios (HU-G2-03 a HU-G2-06)
  Como cliente
  quiero guardar, ver, editar y quitar mis servicios frecuentes
  para pagarlos sin escribir el suministro cada vez

  Antecedentes:
    Dado que los datos de Qolqe están reiniciados
    Y que inicié sesión como "987654321" con PIN "4826"

  # ------------------------------------------------------------- E6 GET /api/servicios/afiliaciones

  @funcional @HU-G2-04 @CA1 @camino-feliz @E6
  Escenario: Mis afiliaciones se listan ordenadas por alias
    Cuando envío "GET" a "/api/servicios/afiliaciones"
    Entonces la respuesta tiene estado 200
    Y la lista tiene los alias "Agua depa, Internet casa, Luz casa" en ese orden

  @funcional @HU-G2-04 @CA1 @particion @E6
  Esquema del escenario: Situación de cada afiliación según sus deudas
    Dado que <precondicion>
    Cuando envío "GET" a "/api/servicios/afiliaciones"
    Entonces la afiliación "<alias>" tiene situación "<situacion>" y total pendiente "<total>"

    Ejemplos:
      | caso         | precondicion                            | alias         | situacion   | total  |
      | sin deudas   | pagué la deuda "ELECTRO" "10000001"     | Luz casa      | AL_DIA      | 0.00   |
      | con deuda    | no hice nada                            | Luz casa      | CON_DEUDA   | 120.00 |
      | en cobranza  | no hice nada                            | Internet casa | EN_COBRANZA | 0.00   |

  @funcional @HU-G2-04 @CA1 @E6
  Escenario: El próximo vencimiento solo existe si hay deuda pendiente
    Dado que pagué la deuda "ELECTRO" "10000001"
    Cuando envío "GET" a "/api/servicios/afiliaciones"
    Entonces la afiliación "Luz casa" no tiene próximo vencimiento
    Y la afiliación "Agua depa" tiene próximo vencimiento

  @funcional @HU-G2-04 @CA1 @particion @E6
  Escenario: Un usuario sin afiliaciones recibe una lista vacía
    Dado que inicié sesión como "912345678" con PIN "7391"
    Cuando envío "GET" a "/api/servicios/afiliaciones"
    Entonces la respuesta tiene estado 200
    Y la lista está vacía

  @tecnico @HU-G2-04 @contrato @E6
  Escenario: Cada afiliación tiene todos sus campos
    Cuando envío "GET" a "/api/servicios/afiliaciones"
    Entonces la respuesta tiene estado 200
    Y cada elemento de la lista tiene los campos "id, alias, empresa, empresa_nombre, suministro, total_pendiente, proximo_vencimiento, debito_automatico, situacion, creada_en"

  @tecnico @HU-G2-04 @seguridad @E6
  Escenario: Ver mis afiliaciones sin token
    Cuando envío "GET" a "/api/servicios/afiliaciones" sin token
    Entonces la respuesta tiene estado 401 y código "NO_AUTENTICADO"

  # ------------------------------------------------------------- E7 POST /api/servicios/afiliaciones

  @funcional @HU-G2-03 @CA1 @CA4 @camino-feliz @E7
  Escenario: Afiliar un servicio: se crea con el débito automático desactivado
    Cuando afilio "ELECTRO" "10000002" con alias "Luz oficina"
    Entonces la respuesta tiene estado 201
    Y la afiliación creada tiene alias "Luz oficina", situación "CON_DEUDA" y débito automático desactivado
    Y la afiliación "Luz oficina" aparece en mi lista

  @funcional @HU-G2-03 @CA1 @valor-limite @E7
  Esquema del escenario: Longitud del alias (3 a 20 caracteres)
    Cuando afilio "ELECTRO" "10000002" con alias "<alias>"
    Entonces la respuesta tiene estado <estado> y código "<codigo>"

    Ejemplos:
      | caso                     | alias                 | estado | codigo              |
      | 2 caracteres (invalido)  | ab                    | 422    | AFILIACION_INVALIDA |
      | 3 caracteres (limite)    | abc                   | 201    | -                   |
      | 20 caracteres (limite)   | Luz de la casa grand  | 201    | -                   |
      | 21 caracteres (invalido) | Luz de la casa grande | 422    | AFILIACION_INVALIDA |

  @funcional @HU-G2-03 @CA1 @valor-limite @E7
  Escenario: Los espacios alrededor del alias no cuentan para su longitud
    Cuando envío "POST" a "/api/servicios/afiliaciones" con el cuerpo {"empresa": "ELECTRO", "suministro": "10000002", "alias": "   ab   "}
    Entonces la respuesta tiene estado 422 y código "AFILIACION_INVALIDA"

  @funcional @HU-G2-03 @CA1 @R-G2-01 @valor-limite @E7
  Esquema del escenario: El suministro de la afiliación cumple R-G2-01
    Cuando afilio "ELECTRO" "<suministro>" con alias "Luz prueba"
    Entonces la respuesta tiene estado 422 y código "AFILIACION_INVALIDA"

    Ejemplos:
      | caso                  | suministro    |
      | 7 digitos (invalido)  | 1000000       |
      | con letras (invalido) | 1000000A      |
      | 13 digitos (invalido) | 1000000010000 |

  @funcional @HU-G2-03 @CA1 @E7
  Escenario: Afiliar una empresa inexistente
    Cuando afilio "NOEXISTE" "10000002" con alias "Luz prueba"
    Entonces la respuesta tiene estado 404 y código "EMPRESA_NO_ENCONTRADA"

  @funcional @HU-G2-03 @CA2 @E7
  Escenario: El suministro debe tener al menos un recibo en la empresa
    Cuando afilio "ELECTRO" "99999999" con alias "Luz prueba"
    Entonces la respuesta tiene estado 404 y código "SUMINISTRO_NO_ENCONTRADO"

  @funcional @HU-G2-03 @CA3 @R-G2-05 @E7
  Escenario: No se puede afiliar dos veces el mismo suministro
    Cuando afilio "ELECTRO" "10000001" con alias "Luz otra vez"
    Entonces la respuesta tiene estado 409 y código "AFILIACION_DUPLICADA"

  @funcional @HU-G2-03 @CA3 @R-G2-05 @valor-limite @E7
  Esquema del escenario: Máximo 8 servicios afiliados por usuario
    Dado que tengo <previas> afiliaciones
    Cuando afilio "ELECTRO" "100000009" con alias "Luz Diego"
    Entonces la respuesta tiene estado <estado> y código "<codigo>"

    Ejemplos:
      | caso                    | previas | estado | codigo              |
      | la octava (limite)      | 7       | 201    | -                   |
      | la novena (sobre limite)| 8       | 422    | LIMITE_AFILIACIONES |

  @tecnico @HU-G2-03 @seguridad @E7
  Escenario: Afiliar sin token
    Cuando envío "POST" a "/api/servicios/afiliaciones" sin token
    Entonces la respuesta tiene estado 401 y código "NO_AUTENTICADO"

  @tecnico @HU-G2-03 @particion @E7
  Esquema del escenario: Cuerpo de afiliación con campos faltantes o de tipo inválido
    Cuando envío "POST" a "/api/servicios/afiliaciones" con el cuerpo <cuerpo>
    Entonces la respuesta tiene estado 422 y código "SOLICITUD_INVALIDA"

    Ejemplos:
      | cuerpo                                                       |
      | {}                                                           |
      | {"empresa": "ELECTRO", "suministro": "10000002"}             |
      | {"empresa": "ELECTRO", "suministro": 10000002, "alias": "Luz"} |
      | []                                                           |

  # ------------------------------------------------------------- E8 PUT /api/servicios/afiliaciones/{id}

  @funcional @HU-G2-05 @CA1 @camino-feliz @E8
  Escenario: Cambiar el alias de una afiliación
    Cuando cambio la afiliación "Luz casa" con el cuerpo {"alias": "Luz depa"}
    Entonces la respuesta tiene estado 200
    Y la afiliación "Luz depa" aparece en mi lista

  @funcional @HU-G2-05 @CA1 @efecto @E8
  Escenario: Activar el débito automático envía un SMS al titular
    Cuando cambio la afiliación "Luz casa" con el cuerpo {"debito_automatico": true}
    Entonces la respuesta tiene estado 200
    Y la afiliación devuelta tiene el débito automático activo
    Y recibí un SMS que dice "Débito automático activado para Luz casa"

  @funcional @HU-G2-05 @CA1 @valor-limite @E8
  Escenario: Cambiar el alias por uno demasiado corto
    Cuando cambio la afiliación "Luz casa" con el cuerpo {"alias": "ab"}
    Entonces la respuesta tiene estado 422 y código "AFILIACION_INVALIDA"

  @funcional @HU-G2-05 @CA1 @E8
  Escenario: Editar una afiliación inexistente
    Cuando envío "PUT" a "/api/servicios/afiliaciones/999999" con el cuerpo {"alias": "Luz depa"}
    Entonces la respuesta tiene estado 404 y código "AFILIACION_NO_ENCONTRADA"

  @tecnico @HU-G2-05 @seguridad @E8
  Escenario: Editar la afiliación de otro usuario responde 404
    Dado que anoté el id de mi afiliación "Luz casa"
    Y que inicié sesión como "912345678" con PIN "7391"
    Cuando envío "PUT" a la afiliación anotada con el cuerpo {"alias": "Mía ahora"}
    Entonces la respuesta tiene estado 404 y código "AFILIACION_NO_ENCONTRADA"

  @tecnico @HU-G2-05 @seguridad @E8
  Escenario: Editar una afiliación sin token
    Cuando envío "PUT" a "/api/servicios/afiliaciones/1" sin token
    Entonces la respuesta tiene estado 401 y código "NO_AUTENTICADO"

  @tecnico @HU-G2-05 @particion @E8
  Esquema del escenario: Edición con id o cuerpo de tipo inválido
    Cuando envío "PUT" a "<ruta>" con el cuerpo <cuerpo>
    Entonces la respuesta tiene estado 422 y código "SOLICITUD_INVALIDA"

    Ejemplos:
      | ruta                               | cuerpo                           |
      | /api/servicios/afiliaciones/abc    | {"alias": "Luz depa"}            |
      | /api/servicios/afiliaciones/1      | {"debito_automatico": "talvez"}  |
      | /api/servicios/afiliaciones/1      | {"alias": 123}                   |

  # ------------------------------------------------------------- E9 DELETE /api/servicios/afiliaciones/{id}

  @funcional @HU-G2-06 @CA1 @camino-feliz @E9
  Escenario: Desafiliar un servicio no modifica los pagos realizados
    Dado que pagué la deuda "ELECTRO" "10000001"
    Cuando desafilio "Luz casa"
    Entonces la respuesta tiene estado 204
    Y la afiliación "Luz casa" ya no aparece en mi lista
    Y mis pagos son "ELECTRO 10000001" en ese orden

  @funcional @HU-G2-06 @CA2 @E9
  Escenario: No se puede desafiliar con el débito automático activo
    Cuando desafilio "Agua depa"
    Entonces la respuesta tiene estado 409 y código "DEBITO_ACTIVO"
    Y la afiliación "Agua depa" aparece en mi lista

  @funcional @HU-G2-06 @CA2 @efecto @E9
  Escenario: Después de desactivar el débito automático sí se puede desafiliar
    Dado que cambié la afiliación "Agua depa" con el cuerpo {"debito_automatico": false}
    Cuando desafilio "Agua depa"
    Entonces la respuesta tiene estado 204
    Y la afiliación "Agua depa" ya no aparece en mi lista

  @funcional @HU-G2-06 @CA1 @E9
  Escenario: Desafiliar una afiliación inexistente
    Cuando envío "DELETE" a "/api/servicios/afiliaciones/999999"
    Entonces la respuesta tiene estado 404 y código "AFILIACION_NO_ENCONTRADA"

  @tecnico @HU-G2-06 @seguridad @E9
  Escenario: Desafiliar la afiliación de otro usuario responde 404 y no la borra
    Dado que anoté el id de mi afiliación "Luz casa"
    Y que inicié sesión como "912345678" con PIN "7391"
    Cuando envío "DELETE" a la afiliación anotada
    Entonces la respuesta tiene estado 404 y código "AFILIACION_NO_ENCONTRADA"
    Y la afiliación anotada sigue existiendo para "987654321" con PIN "4826"

  @tecnico @HU-G2-06 @seguridad @E9
  Escenario: Desafiliar sin token
    Cuando envío "DELETE" a "/api/servicios/afiliaciones/1" sin token
    Entonces la respuesta tiene estado 401 y código "NO_AUTENTICADO"

  @tecnico @HU-G2-06 @particion @E9
  Escenario: Desafiliar con un id que no es entero
    Cuando envío "DELETE" a "/api/servicios/afiliaciones/abc"
    Entonces la respuesta tiene estado 422 y código "SOLICITUD_INVALIDA"
