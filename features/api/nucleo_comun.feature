# language: es
# ─────────────────────────────────────────────────────────────────────────
# QUÉ ES: escenarios de API del NÚCLEO COMÚN (HU-N-01 a HU-N-09, reglas RN-01 a RN-10).
# PARA QUÉ: cobertura funcional (reglas de negocio, caminos feliz y negativos) y técnica
#   (401 sin token, 422 de validación, contrato de la respuesta, límites, concurrencia)
#   de cada endpoint del núcleo. Los códigos de error son los que devuelve qolqe/api/*.py.
# ETIQUETAS: @funcional / @tecnico = tipo · @N1..@N9 = endpoint · @HU-N/@CA/@RN = trazabilidad.
#   N1 POST /api/usuarios · N2 POST /api/auth/login · N3 POST /api/auth/logout
#   N4 GET /api/cuentas/me · N5 PUT /api/cuentas/me · N6 GET /api/cuentas/me/saldo
#   N7 POST /api/cuentas/me/cierre · N8 POST /api/transferencias · N9 GET /api/transferencias/comision
# DATOS SEMILLA: Ana 987654321/4826 (S/ 1,500.00) · Bruno 912345678/7391 (S/ 800.00)
#   Diego 998877665/3604 (S/ 2,500.00, límite diario S/ 1,000.00) · Elena 923456789 (bloqueada)
#   Fabián 934567812/6029 (cuenta CERRADA).
# ─────────────────────────────────────────────────────────────────────────
@nucleo
Característica: Núcleo común por API (registro, sesión, cuenta y transferencias)
  Como cliente de Qolqe
  quiero registrarme, ingresar, administrar mi cuenta y transferir dinero
  para usar mi billetera de forma segura

  Antecedentes:
    Dado que los datos de Qolqe están reiniciados
    Y que inicié sesión como "987654321" con PIN "4826"

  # ═══════════════════════════════ N1 · POST /api/usuarios · HU-N-01
  @N1 @HU-N-01 @funcional @CA1 @CA6 @camino-feliz
  Escenario: Registro exitoso con saldo cero y SMS de bienvenida
    Cuando envío "POST" a "/api/usuarios" sin token con el cuerpo {"dni": "61234567", "nombres": "Lucía Mamani Flores", "celular": "911222333", "pin": "5173", "correo": "lucia.mamani@correo.pe"}
    Entonces la respuesta tiene estado 201
    Y el campo "celular" de la respuesta es "911222333"
    Y el saldo de "911222333" con PIN "5173" es "0.00"
    Y el celular "911222333" recibió un SMS que dice "Bienvenido a Qolqe"

  @N1 @HU-N-01 @funcional @CA2 @RN-01 @valor-limite
  Esquema del escenario: Registro con DNI que no cumple RN-01 (<caso>)
    Cuando envío "POST" a "/api/usuarios" sin token con el cuerpo {"dni": "<dni>", "nombres": "Lucía Mamani", "celular": "911222333", "pin": "5173"}
    Entonces la respuesta tiene estado 422 y código "DNI_INVALIDO"

    Ejemplos:
      | caso         | dni       |
      | 7 digitos    | 6123456   |
      | 9 digitos    | 612345678 |
      | con letras   | 6123456A  |

  @N1 @HU-N-01 @funcional @CA3 @RN-02 @particion
  Esquema del escenario: Registro con celular que no cumple RN-02 (<caso>)
    Cuando envío "POST" a "/api/usuarios" sin token con el cuerpo {"dni": "61234567", "nombres": "Lucía Mamani", "celular": "<celular>", "pin": "5173"}
    Entonces la respuesta tiene estado 422 y código "CELULAR_INVALIDO"

    Ejemplos:
      | caso              | celular    |
      | 8 digitos         | 91122233   |
      | 10 digitos        | 9112223334 |
      | no empieza con 9  | 811222333  |

  @N1 @HU-N-01 @funcional @CA3 @RN-02 @particion
  Esquema del escenario: Registro con un celular ya registrado (<caso>)
    Cuando envío "POST" a "/api/usuarios" sin token con el cuerpo {"dni": "61234567", "nombres": "Lucía Mamani", "celular": "<celular>", "pin": "5173"}
    Entonces la respuesta tiene estado 409 y código "CELULAR_REGISTRADO"

    Ejemplos:
      | caso           | celular   |
      | cuenta activa  | 987654321 |
      | cuenta cerrada | 934567812 |

  @N1 @HU-N-01 @funcional @CA4 @RN-03 @particion
  Esquema del escenario: Registro con PIN que no cumple RN-03 (<caso>)
    Cuando envío "POST" a "/api/usuarios" sin token con el cuerpo {"dni": "61234567", "nombres": "Lucía Mamani", "celular": "911222333", "pin": "<pin>"}
    Entonces la respuesta tiene estado 422 y código "PIN_INVALIDO"

    Ejemplos:
      | caso                    | pin   |
      | 3 digitos               | 517   |
      | 5 digitos               | 51734 |
      | todos iguales           | 1111  |
      | secuencia ascendente    | 1234  |
      | secuencia descendente   | 4321  |

  @N1 @HU-N-01 @funcional @CA5 @particion
  Esquema del escenario: Registro con correo inválido o ya usado (<caso>)
    Cuando envío "POST" a "/api/usuarios" sin token con el cuerpo {"dni": "61234567", "nombres": "Lucía Mamani", "celular": "911222333", "pin": "5173", "correo": "<correo>"}
    Entonces la respuesta tiene estado <estado> y código "<codigo>"

    Ejemplos:
      | caso                    | correo               | estado | codigo            |
      | sin arroba              | lucia.correo.pe      | 422    | CORREO_INVALIDO   |
      | sin dominio             | lucia@               | 422    | CORREO_INVALIDO   |
      | usado, otras mayusculas | ANA.TORRES@correo.pe | 409    | CORREO_REGISTRADO |

  @N1 @HU-N-01 @tecnico @contrato
  Escenario: La respuesta del registro cumple el contrato y no expone el PIN ni el DNI
    Cuando envío "POST" a "/api/usuarios" sin token con el cuerpo {"dni": "61234567", "nombres": "  Lucía Mamani  ", "celular": "911222333", "pin": "5173"}
    Entonces la respuesta tiene estado 201
    Y la respuesta tiene los campos "id, nombres, celular, correo, creado_en"
    Y la respuesta no tiene los campos "pin, pin_hash, dni"
    Y el campo "nombres" de la respuesta es "Lucía Mamani"

  @N1 @HU-N-01 @tecnico @particion
  Esquema del escenario: Registro con cuerpo inválido según el contrato (<caso>)
    Cuando envío "POST" a "/api/usuarios" sin token con el cuerpo <cuerpo>
    Entonces la respuesta tiene estado 422 y código "SOLICITUD_INVALIDA"

    Ejemplos:
      | caso              | cuerpo                                                                          |
      | sin campos        | {}                                                                              |
      | nombres de 1 letra | {"dni": "61234567", "nombres": "L", "celular": "911222333", "pin": "5173"}     |
      | JSON mal formado  | {"dni": "61234567",                                                             |

  # ═══════════════════════════════ N2 · POST /api/auth/login · HU-N-02
  @N2 @HU-N-02 @funcional @CA1 @camino-feliz
  Escenario: Login correcto entrega un token de 30 minutos y una sesión
    Cuando envío "POST" a "/api/auth/login" sin token con el cuerpo {"celular": "987654321", "pin": "4826"}
    Entonces la respuesta tiene estado 200
    Y el campo "token_type" de la respuesta es "bearer"
    Y el campo "expires_in" de la respuesta es "1800"
    Y el campo "usuario.celular" de la respuesta es "987654321"

  @N2 @HU-N-02 @funcional @CA2 @seguridad
  Esquema del escenario: Credenciales erróneas dan un mensaje genérico (<caso>)
    Cuando envío "POST" a "/api/auth/login" sin token con el cuerpo {"celular": "<celular>", "pin": "<pin>"}
    Entonces la respuesta tiene estado 401 y código "CREDENCIALES_INVALIDAS"
    Y el mensaje de error es "Celular o PIN incorrectos"

    Ejemplos:
      | caso                | celular   | pin  |
      | celular inexistente | 911999999 | 4826 |
      | PIN incorrecto      | 987654321 | 9999 |

  @N2 @HU-N-02 @funcional @CA3 @RN-04 @valor-limite
  Escenario: El tercer intento fallido consecutivo bloquea la cuenta y avisa por SMS
    Dado que intenté iniciar sesión 2 veces con celular "912345678" y PIN "0000"
    Cuando envío "POST" a "/api/auth/login" sin token con el cuerpo {"celular": "912345678", "pin": "0000"}
    Entonces la respuesta tiene estado 423 y código "CUENTA_BLOQUEADA"
    Y el celular "912345678" recibió un SMS que dice "fue bloqueada por intentos fallidos"

  @N2 @HU-N-02 @funcional @CA3 @RN-04 @valor-limite
  Escenario: Dos intentos fallidos todavía no bloquean la cuenta
    Dado que intenté iniciar sesión 2 veces con celular "912345678" y PIN "0000"
    Cuando envío "POST" a "/api/auth/login" sin token con el cuerpo {"celular": "912345678", "pin": "7391"}
    Entonces la respuesta tiene estado 200

  @N2 @HU-N-02 @funcional @CA3 @RN-04 @particion
  Escenario: Un login exitoso reinicia el conteo de intentos fallidos
    Dado que intenté iniciar sesión 2 veces con celular "912345678" y PIN "0000"
    Y que intenté iniciar sesión 1 veces con celular "912345678" y PIN "7391"
    Cuando envío "POST" a "/api/auth/login" sin token con el cuerpo {"celular": "912345678", "pin": "0000"}
    Entonces la respuesta tiene estado 401 y código "CREDENCIALES_INVALIDAS"

  @N2 @HU-N-02 @funcional @CA4 @RN-04
  Escenario: Durante el bloqueo ni el PIN correcto permite ingresar
    Cuando envío "POST" a "/api/auth/login" sin token con el cuerpo {"celular": "923456789", "pin": "8152"}
    Entonces la respuesta tiene estado 423 y código "CUENTA_BLOQUEADA"

  @N2 @HU-N-02 @funcional @CA4 @RN-04 @valor-limite
  Escenario: Pasados los 15 minutos de bloqueo se puede ingresar
    Dado que pasaron 16 minutos
    Cuando envío "POST" a "/api/auth/login" sin token con el cuerpo {"celular": "923456789", "pin": "8152"}
    Entonces la respuesta tiene estado 200

  @N2 @HU-N-02 @funcional @CA5
  Escenario: Una cuenta cerrada no puede iniciar sesión
    Cuando envío "POST" a "/api/auth/login" sin token con el cuerpo {"celular": "934567812", "pin": "6029"}
    Entonces la respuesta tiene estado 401 y código "CUENTA_CERRADA"

  @N2 @HU-N-02 @funcional @CA6 @efecto
  Escenario: Ingresar desde un dispositivo desconocido envía un SMS de alerta
    Cuando envío "POST" a "/api/auth/login" sin token con el cuerpo {"celular": "987654321", "pin": "4826", "dispositivo_id": "equipo-nuevo-01"}
    Entonces la respuesta tiene estado 200
    Y el celular "987654321" recibió un SMS que dice "nuevo dispositivo"

  @N2 @HU-N-02 @tecnico @contrato
  Escenario: La respuesta del login cumple el contrato
    Cuando envío "POST" a "/api/auth/login" sin token con el cuerpo {"celular": "987654321", "pin": "4826"}
    Entonces la respuesta tiene los campos "access_token, token_type, expires_in, sesion_id, usuario"
    Y la respuesta no tiene los campos "pin, pin_hash"

  @N2 @HU-N-02 @tecnico @particion
  Esquema del escenario: Login con cuerpo inválido según el contrato (<caso>)
    Cuando envío "POST" a "/api/auth/login" sin token con el cuerpo <cuerpo>
    Entonces la respuesta tiene estado 422 y código "SOLICITUD_INVALIDA"

    Ejemplos:
      | caso         | cuerpo                     |
      | sin PIN      | {"celular": "987654321"}   |
      | sin celular  | {"pin": "4826"}            |
      | PIN numérico | {"celular": "987654321", "pin": 4826} |

  @N2 @HU-N-02 @tecnico @particion
  Escenario: Método HTTP no permitido en el login
    Cuando envío "GET" a "/api/auth/login" sin token
    Entonces la respuesta tiene estado 405

  # ═══════════════════════════════ N3 · POST /api/auth/logout · HU-N-03
  @N3 @HU-N-03 @funcional @CA1 @camino-feliz
  Escenario: Cerrar sesión responde 204
    Cuando cierro sesión con mi token
    Entonces la respuesta tiene estado 204

  @N3 @HU-N-03 @funcional @CA1 @seguridad
  Escenario: Después de cerrar sesión el token ya no es válido
    Cuando cierro sesión con mi token
    Y envío "GET" a "/api/cuentas/me" con el token guardado
    Entonces la respuesta tiene estado 401 y código "NO_AUTENTICADO"

  @N3 @HU-N-03 @funcional @CA2
  Escenario: Cerrar una sesión no afecta mis otras sesiones activas
    Dado que guardé mi token y pasaron 0 minutos
    Cuando cierro otra sesión
    Y envío "GET" a "/api/cuentas/me" con el token guardado
    Entonces la respuesta tiene estado 200

  @N3 @HU-N-03 @tecnico @seguridad
  Esquema del escenario: Cerrar sesión exige un token válido (<caso>)
    Cuando envío "POST" a "/api/auth/logout" con el token "<token>"
    Entonces la respuesta tiene estado 401 y código "NO_AUTENTICADO"

    Ejemplos:
      | caso          | token          |
      | token basura  | abc.def.ghi    |
      | token vacio   |                |

  # ═══════════════════════════════ N4 · GET /api/cuentas/me · HU-N-04
  @N4 @HU-N-04 @funcional @CA2 @camino-feliz
  Escenario: Veo mi perfil con el DNI enmascarado
    Cuando envío "GET" a "/api/cuentas/me"
    Entonces la respuesta tiene estado 200
    Y el campo "nombres" de la respuesta es "Ana Torres Quispe"
    Y el campo "celular" de la respuesta es "987654321"
    Y el campo "correo" de la respuesta es "ana.torres@correo.pe"
    Y el campo "dni" de la respuesta es "****8912"

  @N4 @HU-N-04 @tecnico @contrato
  Escenario: El perfil cumple el contrato y no expone el PIN
    Cuando envío "GET" a "/api/cuentas/me"
    Entonces la respuesta tiene los campos "id, nombres, celular, correo, dni, estado, creado_en"
    Y la respuesta no tiene los campos "pin, pin_hash"
    Y el campo "estado" de la respuesta es "ACTIVA"

  @N4 @HU-N-04 @tecnico @CA3 @seguridad
  Escenario: El perfil sin token responde 401
    Cuando envío "GET" a "/api/cuentas/me" sin token
    Entonces la respuesta tiene estado 401 y código "NO_AUTENTICADO"

  @N4 @HU-N-04 @tecnico @CA3 @seguridad
  Escenario: El perfil con un token inválido responde 401
    Cuando envío "GET" a "/api/cuentas/me" con el token "eyJhbGciOiJIUzI1NiJ9.e30.firma-falsa"
    Entonces la respuesta tiene estado 401 y código "NO_AUTENTICADO"

  @N4 @HU-N-04 @tecnico @CA3 @seguridad @valor-limite
  Escenario: El perfil con un token vencido (31 minutos) responde 401
    Dado que guardé mi token y pasaron 31 minutos
    Cuando envío "GET" a "/api/cuentas/me" con el token guardado
    Entonces la respuesta tiene estado 401 y código "NO_AUTENTICADO"

  # ═══════════════════════════════ N5 · PUT /api/cuentas/me · HU-N-05
  @N5 @HU-N-05 @funcional @CA1 @CA3 @camino-feliz
  Escenario: Edito mis nombres y mi correo y recibo un SMS de aviso
    Cuando envío "PUT" a "/api/cuentas/me" con el cuerpo {"nombres": "Ana Lucía Torres Quispe", "correo": "Ana.Lucia@Correo.pe"}
    Entonces la respuesta tiene estado 200
    Y el campo "nombres" de la respuesta es "Ana Lucía Torres Quispe"
    Y el campo "correo" de la respuesta es "ana.lucia@correo.pe"
    Y el celular "987654321" recibió un SMS que dice "se cambió a ana.lucia@correo.pe"

  @N5 @HU-N-05 @funcional @CA2 @seguridad
  Escenario: El DNI y el celular enviados al editar se ignoran
    Cuando envío "PUT" a "/api/cuentas/me" con el cuerpo {"dni": "11111111", "celular": "911111111", "nombres": "Ana Torres"}
    Entonces la respuesta tiene estado 200
    Y el campo "dni" de la respuesta es "****8912"
    Y el campo "celular" de la respuesta es "987654321"
    Y el campo "nombres" de la respuesta es "Ana Torres"

  @N5 @HU-N-05 @funcional @CA1 @valor-limite
  Esquema del escenario: Editar con datos inválidos (<caso>)
    Cuando envío "PUT" a "/api/cuentas/me" con el cuerpo <cuerpo>
    Entonces la respuesta tiene estado <estado> y código "<codigo>"

    Ejemplos:
      | caso                          | cuerpo                                     | estado | codigo            |
      | nombres de 1 caracter         | {"nombres": "A"}                           | 422    | PERFIL_INVALIDO   |
      | nombres solo espacios         | {"nombres": "     "}                       | 422    | PERFIL_INVALIDO   |
      | correo sin dominio            | {"correo": "ana@"}                         | 422    | CORREO_INVALIDO   |
      | correo de otra cuenta activa  | {"correo": "BRUNO.DIAZ@correo.pe"}         | 409    | CORREO_REGISTRADO |

  @N5 @HU-N-05 @funcional @CA1 @valor-limite
  Esquema del escenario: Longitud de los nombres de 2 a 80 caracteres (<caso>)
    Cuando envío "PUT" a "/api/cuentas/me" con el cuerpo {"nombres": "<nombres>"}
    Entonces la respuesta tiene estado <estado> y código "<codigo>"

    Ejemplos:
      | caso          | nombres | estado | codigo          |
      | 2 (limite)    | Al      | 200    | -               |
      | 80 (limite)   | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa | 200    | -               |
      | 81 (invalido) | aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa | 422    | PERFIL_INVALIDO |

  @N5 @HU-N-05 @funcional @CA1
  Escenario: Puedo quitar mi correo enviándolo vacío
    Cuando envío "PUT" a "/api/cuentas/me" con el cuerpo {"correo": ""}
    Entonces la respuesta tiene estado 200
    Y el campo "correo" de la respuesta es nulo

  @N5 @HU-N-05 @tecnico @seguridad
  Escenario: Editar el perfil sin token responde 401
    Cuando envío "PUT" a "/api/cuentas/me" sin token
    Entonces la respuesta tiene estado 401 y código "NO_AUTENTICADO"

  @N5 @HU-N-05 @tecnico @particion
  Escenario: Editar el perfil con un tipo de dato inválido responde 422
    Cuando envío "PUT" a "/api/cuentas/me" con el cuerpo {"nombres": 123}
    Entonces la respuesta tiene estado 422 y código "SOLICITUD_INVALIDA"

  # ═══════════════════════════════ N6 · GET /api/cuentas/me/saldo · HU-N-04
  @N6 @HU-N-04 @funcional @CA1 @camino-feliz
  Escenario: Veo mi saldo disponible en soles
    Cuando envío "GET" a "/api/cuentas/me/saldo"
    Entonces la respuesta tiene estado 200
    Y el campo "saldo" de la respuesta es "1500.00"
    Y el campo "moneda" de la respuesta es "PEN"

  @N6 @HU-N-04 @tecnico @contrato
  Escenario: El saldo cumple el contrato
    Cuando envío "GET" a "/api/cuentas/me/saldo"
    Entonces la respuesta tiene los campos "saldo, moneda, actualizado_en"

  @N6 @HU-N-04 @tecnico @CA3 @seguridad
  Escenario: El saldo sin token responde 401
    Cuando envío "GET" a "/api/cuentas/me/saldo" sin token
    Entonces la respuesta tiene estado 401 y código "NO_AUTENTICADO"

  # ═══════════════════════════════ N7 · POST /api/cuentas/me/cierre · HU-N-06
  @N7 @HU-N-06 @funcional @CA1 @CA4 @camino-feliz
  Escenario: Cierro mi cuenta con saldo cero y ya no puedo usarla
    Dado que inicié sesión como "998877665" con PIN "3604"
    Y que mi saldo es "0.00"
    Y que guardé mi token y pasaron 0 minutos
    Cuando envío "POST" a "/api/cuentas/me/cierre" con el cuerpo {"pin": "3604"}
    Entonces la respuesta tiene estado 204
    Y al usar el token guardado en "/api/cuentas/me" responde 401
    Y al iniciar sesión con celular "998877665" y PIN "3604" responde 401 "CUENTA_CERRADA"

  @N7 @HU-N-06 @funcional @CA1
  Escenario: Cerrar la cuenta con un PIN incorrecto
    Cuando envío "POST" a "/api/cuentas/me/cierre" con el cuerpo {"pin": "9999"}
    Entonces la respuesta tiene estado 422 y código "PIN_INCORRECTO"

  @N7 @HU-N-06 @funcional @CA2 @valor-limite
  Esquema del escenario: Solo se cierra con saldo exactamente S/ 0.00 (<saldo>)
    Dado que inicié sesión como "998877665" con PIN "3604"
    Y que mi saldo es "<saldo>"
    Cuando envío "POST" a "/api/cuentas/me/cierre" con el cuerpo {"pin": "3604"}
    Entonces la respuesta tiene estado 422 y código "SALDO_PENDIENTE"

    Ejemplos:
      | saldo   |
      | 0.01    |
      | 1500.00 |

  @N7 @HU-N-06 @funcional @CA3
  Escenario: No se cierra la cuenta con solicitudes de dinero pendientes
    Dado que mi saldo es "0.00"
    Cuando envío "POST" a "/api/cuentas/me/cierre" con el cuerpo {"pin": "4826"}
    Entonces la respuesta tiene estado 409 y código "SOLICITUDES_PENDIENTES"

  @N7 @HU-N-06 @tecnico @seguridad
  Escenario: Cerrar la cuenta sin token responde 401
    Cuando envío "POST" a "/api/cuentas/me/cierre" sin token
    Entonces la respuesta tiene estado 401 y código "NO_AUTENTICADO"

  @N7 @HU-N-06 @tecnico @particion
  Escenario: Cerrar la cuenta sin PIN responde 422
    Cuando envío "POST" a "/api/cuentas/me/cierre" con el cuerpo {}
    Entonces la respuesta tiene estado 422 y código "SOLICITUD_INVALIDA"

  # ═══════════════════════════════ N8 · POST /api/transferencias · HU-N-07 (a Qolqe)
  @N8 @HU-N-07 @funcional @CA3 @CA4 @RN-10 @camino-feliz
  Escenario: Transferencia a otro usuario Qolqe sin comisión
    Cuando envío "POST" a "/api/transferencias" con el cuerpo {"celular_destino": "912345678", "monto": "100.00", "descripcion": "Almuerzo"}
    Entonces la respuesta tiene estado 201
    Y el campo "comision" de la respuesta es "0.00"
    Y el campo "total" de la respuesta es "100.00"
    Y el campo "saldo" de la respuesta es "1400.00"
    Y el campo "destinatario.nombre" de la respuesta es "Bruno D."
    Y el saldo de "912345678" con PIN "7391" es "900.00"
    Y el movimiento de la transferencia aparece para "912345678" con PIN "7391"
    Y el celular "912345678" recibió un SMS que dice "Recibiste S/ 100.00"

  @N8 @HU-N-07 @funcional @CA1
  Escenario: Transferencia eligiendo un contacto frecuente
    Cuando envío "POST" a "/api/transferencias" con el cuerpo {"contacto_id": 1, "monto": "10.00"}
    Entonces la respuesta tiene estado 201
    Y el campo "destinatario.celular" de la respuesta es "912345678"

  @N8 @HU-N-07 @funcional @CA2 @RN-05 @valor-limite
  Esquema del escenario: Monto de la transferencia según RN-05 (<caso>)
    Cuando envío "POST" a "/api/transferencias" con el cuerpo {"celular_destino": "912345678", "monto": "<monto>"}
    Entonces la respuesta tiene estado <estado> y código "<codigo>"

    Ejemplos:
      | caso                  | monto  | estado | codigo         |
      | cero                  | 0.00   | 422    | MONTO_INVALIDO |
      | negativo              | -5.00  | 422    | MONTO_INVALIDO |
      | minimo 0.01           | 0.01   | 201    | -              |
      | 3 decimales           | 10.001 | 422    | MONTO_INVALIDO |
      | maximo 500.00         | 500.00 | 201    | -              |
      | sobre el maximo       | 500.01 | 422    | MONTO_INVALIDO |

  @N8 @HU-N-07 @funcional @CA2 @RN-07 @particion
  Esquema del escenario: Destino no permitido según RN-07 (<caso>)
    Cuando envío "POST" a "/api/transferencias" con el cuerpo {"celular_destino": "<celular>", "monto": "10.00"}
    Entonces la respuesta tiene estado <estado> y código "<codigo>"

    Ejemplos:
      | caso                 | celular   | estado | codigo                   |
      | a mi mismo           | 987654321 | 422    | TRANSFERENCIA_A_SI_MISMO |
      | celular no registrado | 911999999 | 404    | DESTINO_NO_REGISTRADO    |
      | celular invalido     | 812345678 | 422    | CELULAR_INVALIDO         |

  @N8 @HU-N-07 @funcional @CA2 @RN-07 @particion
  Escenario: No se puede transferir a una cuenta cerrada
    Cuando envío "POST" a "/api/transferencias" con el cuerpo {"celular_destino": "934567812", "monto": "10.00"}
    Entonces la respuesta tiene estado 422 y código "DESTINO_INACTIVO"
    Y mi saldo es "1500.00"

  @N8 @HU-N-07 @funcional @CA2 @RN-08 @valor-limite
  Esquema del escenario: El saldo debe cubrir el monto (<caso>)
    Dado que mi saldo es "50.00"
    Cuando envío "POST" a "/api/transferencias" con el cuerpo {"celular_destino": "912345678", "monto": "<monto>"}
    Entonces la respuesta tiene estado <estado> y código "<codigo>"

    Ejemplos:
      | caso               | monto | estado | codigo             |
      | igual al saldo     | 50.00 | 201    | -                  |
      | supera por 0.01    | 50.01 | 422    | SALDO_INSUFICIENTE |

  @N8 @HU-N-07 @funcional @CA2 @RN-06 @valor-limite
  Escenario: La suma del día no puede superar el límite diario
    Dado que inicié sesión como "998877665" con PIN "3604"
    Y que transferí con el cuerpo {"celular_destino": "912345678", "monto": "500.00"}
    Y que transferí con el cuerpo {"celular_destino": "912345678", "monto": "500.00"}
    Cuando envío "POST" a "/api/transferencias" con el cuerpo {"celular_destino": "912345678", "monto": "0.01"}
    Entonces la respuesta tiene estado 422 y código "LIMITE_DIARIO_EXCEDIDO"
    Y mi saldo es "1500.00"

  @N8 @HU-N-07 @funcional @CA5 @RN-06 @concurrencia
  Escenario: Transferencias simultáneas no superan el límite diario
    Dado que inicié sesión como "998877665" con PIN "3604"
    Cuando envío 3 transferencias simultáneas con el cuerpo {"celular_destino": "912345678", "monto": "500.00"}
    Entonces 2 transferencias son exitosas y 1 responden "LIMITE_DIARIO_EXCEDIDO"
    Y mi saldo es "1500.00"

  @N8 @HU-N-07 @tecnico @seguridad
  Escenario: No puedo transferir usando un contacto de otro usuario
    Cuando envío "POST" a "/api/transferencias" con el cuerpo {"contacto_id": 3, "monto": "10.00"}
    Entonces la respuesta tiene estado 404 y código "CONTACTO_NO_ENCONTRADO"

  @N8 @HU-N-07 @tecnico @seguridad
  Escenario: Transferir sin token responde 401
    Cuando envío "POST" a "/api/transferencias" sin token
    Entonces la respuesta tiene estado 401 y código "NO_AUTENTICADO"

  @N8 @HU-N-07 @tecnico @contrato
  Escenario: El comprobante de la transferencia cumple el contrato
    Cuando envío "POST" a "/api/transferencias" con el cuerpo {"celular_destino": "912345678", "monto": "25.00"}
    Entonces la respuesta tiene estado 201
    Y la respuesta tiene los campos "codigo_operacion, tipo, monto, comision, total, destinatario, saldo, fecha"
    Y el campo "tipo" de la respuesta es "QOLQE"

  @N8 @HU-N-07 @tecnico @particion
  Esquema del escenario: Transferencia con cuerpo inválido (<caso>)
    Cuando envío "POST" a "/api/transferencias" con el cuerpo <cuerpo>
    Entonces la respuesta tiene estado 422 y código "<codigo>"

    Ejemplos:
      | caso                    | cuerpo                                                                                                       | codigo             |
      | sin destino             | {"monto": "10.00"}                                                                                           | DESTINO_REQUERIDO  |
      | sin monto               | {"celular_destino": "912345678"}                                                                             | SOLICITUD_INVALIDA |
      | monto no numerico       | {"celular_destino": "912345678", "monto": "diez"}                                                            | SOLICITUD_INVALIDA |
      | tipo desconocido        | {"tipo": "OTRO", "celular_destino": "912345678", "monto": "10.00"}                                           | SOLICITUD_INVALIDA |
      | descripcion de 61       | {"celular_destino": "912345678", "monto": "10.00", "descripcion": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"} | SOLICITUD_INVALIDA |

  # ═══════════════════════════════ N8 · POST /api/transferencias · HU-N-08 (interbancaria)
  @N8 @HU-N-08 @funcional @CA2 @CA3 @RN-09 @camino-feliz
  Escenario: Transferencia interbancaria con comisión y CCI enmascarado
    Cuando envío "POST" a "/api/transferencias" con el cuerpo {"tipo": "INTERBANCARIA", "cci": "00219100123456789012", "monto": "100.00"}
    Entonces la respuesta tiene estado 201
    Y el campo "comision" de la respuesta es "1.50"
    Y el campo "total" de la respuesta es "101.50"
    Y el campo "saldo" de la respuesta es "1398.50"
    Y el campo "destinatario.cci" de la respuesta es "****************9012"

  @N8 @HU-N-08 @funcional @CA2 @RN-09 @valor-limite
  Esquema del escenario: Comisión interbancaria con mínimo y máximo (<caso>)
    Cuando envío "POST" a "/api/transferencias" con el cuerpo {"tipo": "INTERBANCARIA", "cci": "00219100123456789012", "monto": "<monto>"}
    Entonces la respuesta tiene estado 201
    Y el campo "comision" de la respuesta es "<comision>"

    Ejemplos:
      | caso           | monto  | comision |
      | bajo el minimo | 20.00  | 1.00     |
      | sobre el maximo | 400.00 | 5.00    |

  @N8 @HU-N-08 @funcional @CA1 @particion
  Esquema del escenario: CCI que no tiene 20 dígitos (<caso>)
    Cuando envío "POST" a "/api/transferencias" con el cuerpo {"tipo": "INTERBANCARIA", "cci": "<cci>", "monto": "10.00"}
    Entonces la respuesta tiene estado 422 y código "CCI_INVALIDO"

    Ejemplos:
      | caso        | cci                   |
      | 19 digitos  | 0021910012345678901   |
      | 21 digitos  | 002191001234567890123 |
      | con letras  | 0021910012345678901A  |

  @N8 @HU-N-08 @funcional @CA1
  Escenario: Transferencia interbancaria sin CCI
    Cuando envío "POST" a "/api/transferencias" con el cuerpo {"tipo": "INTERBANCARIA", "monto": "10.00"}
    Entonces la respuesta tiene estado 422 y código "DESTINO_REQUERIDO"

  @N8 @HU-N-08 @funcional @CA2 @RN-08 @valor-limite
  Escenario: El saldo debe cubrir el monto más la comisión interbancaria
    Dado que mi saldo es "100.00"
    Cuando envío "POST" a "/api/transferencias" con el cuerpo {"tipo": "INTERBANCARIA", "cci": "00219100123456789012", "monto": "100.00"}
    Entonces la respuesta tiene estado 422 y código "SALDO_INSUFICIENTE"
    Y mi saldo es "100.00"

  @N8 @HU-N-08 @funcional @CA2 @RN-06
  Escenario: Las transferencias interbancarias cuentan para el límite diario
    Dado que inicié sesión como "998877665" con PIN "3604"
    Y que transferí con el cuerpo {"tipo": "INTERBANCARIA", "cci": "00219100123456789012", "monto": "500.00"}
    Y que transferí con el cuerpo {"tipo": "INTERBANCARIA", "cci": "00219100123456789012", "monto": "500.00"}
    Cuando envío "POST" a "/api/transferencias" con el cuerpo {"celular_destino": "912345678", "monto": "1.00"}
    Entonces la respuesta tiene estado 422 y código "LIMITE_DIARIO_EXCEDIDO"

  # ═══════════════════════════════ N9 · GET /api/transferencias/comision · HU-N-09
  @N9 @HU-N-09 @funcional @CA1 @camino-feliz
  Escenario: Simular una transferencia Qolqe no tiene comisión ni mueve el saldo
    Cuando envío "GET" a "/api/transferencias/comision?monto=150&tipo=QOLQE"
    Entonces la respuesta tiene estado 200
    Y el campo "monto" de la respuesta es "150.00"
    Y el campo "comision" de la respuesta es "0.00"
    Y el campo "total" de la respuesta es "150.00"
    Y mi saldo es "1500.00"

  @N9 @HU-N-09 @funcional @CA1 @RN-09 @valor-limite
  Esquema del escenario: Simular la comisión interbancaria (<caso>)
    Cuando envío "GET" a "/api/transferencias/comision?monto=<monto>&tipo=INTERBANCARIA"
    Entonces la respuesta tiene estado 200
    Y el campo "comision" de la respuesta es "<comision>"
    Y el campo "total" de la respuesta es "<total>"
    Y mi saldo es "1500.00"

    Ejemplos:
      | caso                     | monto  | comision | total  |
      | minimo S/ 1.00           | 20.00  | 1.00     | 21.00  |
      | justo en el minimo       | 66.67  | 1.00     | 67.67  |
      | 1.5 %                    | 100.00 | 1.50     | 101.50 |
      | justo en el maximo       | 333.33 | 5.00     | 338.33 |
      | maximo S/ 5.00           | 500.00 | 5.00     | 505.00 |
      | redondeo comercial 0.005 | 71.00  | 1.07     | 72.07  |

  @N9 @HU-N-09 @funcional @CA1 @RN-05 @valor-limite
  Esquema del escenario: Simular con un monto inválido (<caso>)
    Cuando envío "GET" a "/api/transferencias/comision?monto=<monto>&tipo=INTERBANCARIA"
    Entonces la respuesta tiene estado 422 y código "MONTO_INVALIDO"

    Ejemplos:
      | caso            | monto  |
      | cero            | 0      |
      | sobre el maximo | 500.01 |
      | 3 decimales     | 10.005 |

  @N9 @HU-N-09 @tecnico @particion
  Esquema del escenario: Simular con parámetros inválidos según el contrato (<caso>)
    Cuando envío "GET" a "/api/transferencias/comision?<parametros>"
    Entonces la respuesta tiene estado 422 y código "SOLICITUD_INVALIDA"

    Ejemplos:
      | caso             | parametros             |
      | sin monto        | tipo=QOLQE             |
      | monto no numero  | monto=diez             |
      | tipo desconocido | monto=10&tipo=OTRO     |

  @N9 @HU-N-09 @tecnico @seguridad
  Escenario: Simular la comisión sin token responde 401
    Cuando envío "GET" a "/api/transferencias/comision?monto=10" sin token
    Entonces la respuesta tiene estado 401 y código "NO_AUTENTICADO"

  @N9 @HU-N-09 @tecnico @contrato
  Escenario: La simulación cumple el contrato
    Cuando envío "GET" a "/api/transferencias/comision?monto=10"
    Entonces la respuesta tiene los campos "monto, comision, total"
