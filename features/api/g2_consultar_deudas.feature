# language: es
# ─────────────────────────────────────────────────────────────────────────
# QUÉ ES: escenarios de prueba en Gherkin (lenguaje natural) de HU-G2-01 (consultar deudas).
# PARA QUÉ: verificar la consulta de deudas: empresa válida, longitud del suministro
#   (8 a 12 dígitos), orden, datos mostrados, estado EN_COBRANZA y seguridad.
# CÓMO SE USA: no se ejecuta solo. pytest-bdd lee este archivo y conecta cada
#   frase (Dado/Cuando/Entonces) con una función de tests/api/conftest.py.
#   Ejecutar: pytest -v   ·   solo esta HU: pytest -v -m "HU-G2-01"
# ETIQUETAS (@...): trazabilidad HU → criterio de aceptación (CA) → técnica.
# ─────────────────────────────────────────────────────────────────────────
@G2 @HU-G2-01 @E2
Característica: HU-G2-01 Consultar deudas de un suministro (Prioridad Alta)
  Como cliente
  quiero consultar las deudas pendientes de un suministro
  para saber cuánto debo pagar y hasta cuándo

  Antecedentes:
    Dado que los datos de Qolqe están reiniciados
    Y que inicié sesión como "987654321" con PIN "4826"

  @funcional @CA1 @particion
  Escenario: Empresa inexistente
    Cuando consulto las deudas de la empresa "NOEXISTE" y suministro "10000001"
    Entonces la respuesta tiene estado 404 y código "EMPRESA_NO_ENCONTRADA"

  @funcional @CA1 @R-G2-01 @valor-limite
  Esquema del escenario: Longitud del código de suministro (R-G2-01: 8 a 12 dígitos)
    Cuando consulto las deudas de la empresa "<empresa>" y suministro "<suministro>"
    Entonces la respuesta tiene estado <estado> y código "<codigo>"

    Ejemplos:
      | caso                     | empresa  | suministro    | estado | codigo              |
      | 7 digitos (invalido)     | ELECTRO  | 1234567       | 422    | SUMINISTRO_INVALIDO |
      | 8 digitos (limite min)   | ELECTRO  | 10000001      | 200    | -                   |
      | 12 digitos (limite max)  | INTERNET | 300000000007  | 200    | -                   |
      | 13 digitos (invalido)    | ELECTRO  | 1000000010000 | 422    | SUMINISTRO_INVALIDO |

  @funcional @CA1 @R-G2-01 @particion
  Esquema del escenario: Suministro con caracteres no numéricos
    Cuando consulto las deudas de la empresa "ELECTRO" y suministro "<suministro>"
    Entonces la respuesta tiene estado 422 y código "SUMINISTRO_INVALIDO"

    Ejemplos:
      | suministro |
      | 1000000A   |
      | 1000 0001  |
      | -10000001  |

  @funcional @CA2
  Escenario: Deudas ordenadas de la más antigua a la más reciente
    Cuando consulto las deudas de la empresa "ELECTRO" y suministro "100000009"
    Entonces la respuesta tiene estado 200
    Y recibo 2 deudas ordenadas por vencimiento ascendente

  @tecnico @CA2 @contrato
  Escenario: Cada deuda muestra todos sus datos y el titular enmascarado
    Cuando consulto las deudas de la empresa "ELECTRO" y suministro "100000009"
    Entonces la respuesta tiene estado 200
    Y cada deuda tiene los campos "id, empresa, suministro, titular, periodo, monto, vencimiento, dias_atraso, mora, total, estado"
    Y el titular de cada deuda está enmascarado como "Diego S."

  @funcional @CA2 @R-G2-04 @valor-limite
  Esquema del escenario: Estado de la deuda según los días de atraso (límite de 60 días)
    Dado que el reloj está <dias> días después del vencimiento de la deuda "ELECTRO" "10000001"
    Cuando consulto las deudas de la empresa "ELECTRO" y suministro "10000001"
    Entonces la respuesta tiene estado 200
    Y la deuda tiene estado "<estado>"

    Ejemplos:
      | dias | estado      |
      | 59   | PENDIENTE   |
      | 60   | PENDIENTE   |
      | 61   | EN_COBRANZA |

  @funcional @CA2 @R-G2-03 @valor-limite
  Esquema del escenario: Conteo de días de atraso alrededor del vencimiento
    Dado que el reloj está <dias> días después del vencimiento de la deuda "ELECTRO" "10000001"
    Cuando consulto las deudas de la empresa "ELECTRO" y suministro "10000001"
    Entonces la respuesta tiene estado 200
    Y la deuda tiene <atraso> días de atraso

    Ejemplos:
      | caso                 | dias | atraso |
      | un dia antes         | -1   | 0      |
      | el mismo dia         | 0    | 0      |
      | un dia despues       | 1    | 1      |

  @funcional @CA3
  Escenario: Suministro sin deudas pendientes
    Cuando consulto las deudas de la empresa "ELECTRO" y suministro "99999999"
    Entonces la respuesta tiene estado 404 y código "SIN_DEUDA_PENDIENTE"

  @funcional @CA3 @efecto
  Escenario: Después de pagar la única deuda, el suministro queda sin deudas pendientes
    Dado que pagué la deuda "ELECTRO" "10000001"
    Cuando consulto las deudas de la empresa "ELECTRO" y suministro "10000001"
    Entonces la respuesta tiene estado 404 y código "SIN_DEUDA_PENDIENTE"

  @tecnico @seguridad
  Escenario: Consultar deudas sin token
    Cuando consulto las deudas de la empresa "ELECTRO" y suministro "10000001" sin token
    Entonces la respuesta tiene estado 401 y código "NO_AUTENTICADO"

  @tecnico @seguridad @particion
  Esquema del escenario: Consultar deudas con un token inválido
    Cuando envío "GET" a "/api/servicios/deudas?empresa=ELECTRO&suministro=10000001" con el token "<token>"
    Entonces la respuesta tiene estado 401 y código "NO_AUTENTICADO"

    Ejemplos:
      | caso             | token                                  |
      | texto cualquiera | abc123                                 |
      | JWT mal firmado  | eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0.x |

  @tecnico @seguridad @valor-limite
  Esquema del escenario: El token vence a los 30 minutos de iniciar sesión
    Dado que guardé mi token y pasaron <minutos> minutos
    Cuando envío "GET" a "/api/servicios/deudas?empresa=ELECTRO&suministro=10000001" con el token guardado
    Entonces la respuesta tiene estado <estado>

    Ejemplos:
      | minutos | estado |
      | 29      | 200    |
      | 30      | 401    |

  @tecnico @particion
  Esquema del escenario: Faltan parámetros obligatorios de la consulta
    Cuando envío "GET" a "/api/servicios/deudas<query>"
    Entonces la respuesta tiene estado 422 y código "SOLICITUD_INVALIDA"

    Ejemplos:
      | caso             | query                |
      | sin parametros   |                      |
      | falta suministro | ?empresa=ELECTRO     |
      | falta empresa    | ?suministro=10000001 |

  @tecnico
  Escenario: Método HTTP no permitido en la consulta de deudas
    Cuando envío "DELETE" a "/api/servicios/deudas"
    Entonces la respuesta tiene estado 405
