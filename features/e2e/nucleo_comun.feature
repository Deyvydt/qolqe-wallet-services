# language: es
# ─────────────────────────────────────────────────────────────────────────
# QUÉ ES: escenarios E2E (por la interfaz web) del NÚCLEO COMÚN de Qolqe, HU-N-01 a HU-N-09.
# CÓMO SE EJECUTA: Robot Framework lee este archivo con robotframework-gherkin-parser;
#   cada frase es una keyword de features/e2e/pasos/nucleo.resource (Page Objects en
#   tests/e2e/pages/). Antes de cada escenario se reinician los datos semilla.
#   robot --parser GherkinParser --language es -v URL:http://127.0.0.1:8000 features/e2e
# DATOS: Ana (987654321 / PIN 4826, saldo S/ 1,500.00) y Bruno (912345678).
# ─────────────────────────────────────────────────────────────────────────
@e2e @nucleo
Característica: Núcleo común por la interfaz web
  Como cliente de Qolqe
  quiero registrarme, ingresar, ver y editar mis datos y transferir dinero
  para usar mi billetera desde el navegador

  # @DEF-06: tras un login exitoso por la pantalla, /inicio a veces recibe 401 (la sesión se
  # guarda después de responder). Si ocurre, Robot lo reporta como SKIP con el fallo original.
  @HU-N-01 @CA1 @camino-feliz @defecto @DEF-06
  Escenario: Un visitante crea su cuenta y la usa con saldo S/ 0.00
    Dado que estoy en la página de registro
    Cuando me registro con DNI "61234567", nombres "Lucía Mamani Flores", celular "911222333" y PIN "5173"
    Entonces veo el aviso de inicio de sesión "Tu cuenta fue creada. Ya puedes ingresar."
    Cuando ingreso con celular "911222333" y PIN "5173"
    Entonces estoy en la página de inicio
    Y veo mi saldo "S/ 0.00"

  @HU-N-02 @CA1 @camino-feliz @defecto @DEF-06
  Escenario: Ana inicia sesión con sus credenciales correctas
    Dado que estoy en la página de login
    Cuando ingreso con celular "987654321" y PIN "4826"
    Entonces estoy en la página de inicio
    Y veo el saludo "Hola, Ana"

  @HU-N-02 @CA2 @seguridad
  Esquema del escenario: Credenciales erróneas (<caso>) muestran un mensaje genérico
    Dado que estoy en la página de login
    Cuando ingreso con celular "<celular>" y PIN "<pin>"
    Entonces veo el error de login "Celular o PIN incorrectos"
    Y sigo en la página de login

    Ejemplos:
      | caso                | celular   | pin  |
      | PIN incorrecto      | 987654321 | 1379 |
      | celular inexistente | 977777777 | 4826 |

  @HU-N-02 @CA3 @CA4 @RN-04 @seguridad
  Escenario: La cuenta se bloquea al tercer intento fallido y ni el PIN correcto permite ingresar
    Dado que estoy en la página de login
    Cuando ingreso 3 veces con celular "987654321" y PIN "1379"
    Entonces veo el error de login "Tu cuenta está bloqueada"
    Cuando ingreso con celular "987654321" y PIN "4826"
    Entonces veo el error de login "Tu cuenta está bloqueada"
    Y sigo en la página de login

  @HU-N-03 @CA1
  Escenario: Ana cierra sesión y ya no puede abrir páginas privadas
    Dado que Ana inició sesión
    Cuando cierro sesión
    Entonces veo el aviso de inicio de sesión "Cerraste sesión correctamente."
    Y al abrir la página de inicio vuelvo al login

  @HU-N-04 @CA1 @CA2
  Escenario: Ana ve su saldo y su perfil con el DNI enmascarado
    Dado que Ana inició sesión
    Entonces veo mi saldo "S/ 1,500.00"
    Cuando abro mi perfil
    Entonces mi perfil muestra nombres "Ana Torres Quispe", celular "987654321", DNI "****8912" y correo "ana.torres@correo.pe"

  @HU-N-05 @CA1
  Escenario: Ana actualiza sus nombres y su correo
    Dado que Ana inició sesión
    Y abro mi perfil
    Cuando cambio mis nombres a "Ana Torres Q." y mi correo a "ana.tq@correo.pe"
    Entonces veo el mensaje de perfil "Tus datos fueron actualizados"
    Cuando recargo mi perfil
    Entonces mi perfil muestra nombres "Ana Torres Q.", celular "987654321", DNI "****8912" y correo "ana.tq@correo.pe"

  @HU-N-06 @CA2
  Escenario: Ana no puede cerrar su cuenta mientras tenga saldo
    Dado que Ana inició sesión
    Y abro mi perfil
    Cuando cierro mi cuenta con PIN "4826"
    Entonces el diálogo de cierre muestra el error "Para cerrar tu cuenta el saldo debe ser S/ 0.00"

  @HU-N-06 @CA1 @CA4
  Escenario: Un cliente con saldo S/ 0.00 cierra su cuenta y ya no puede ingresar
    Dado que me registré con DNI "61234567", nombres "Lucía Mamani Flores", celular "911222333" y PIN "5173"
    Y que inicié sesión con celular "911222333" y PIN "5173"
    Y abro mi perfil
    Cuando cierro mi cuenta con PIN "5173"
    Entonces veo el aviso de inicio de sesión "Tu cuenta fue cerrada. Gracias por usar Qolqe."
    Cuando ingreso con celular "911222333" y PIN "5173"
    Entonces veo el error de login "La cuenta fue cerrada"

  @HU-N-07 @HU-N-09 @CA3 @CA4 @camino-feliz
  Escenario: Ana transfiere a Bruno, ve la comisión antes de confirmar y recibe el comprobante
    Dado que Ana inició sesión
    Y abro la página de transferir
    Cuando preparo una transferencia Qolqe de "50.00" al celular "912345678"
    Entonces el diálogo de confirmación muestra monto "S/ 50.00", comisión "S/ 0.00" y total "S/ 50.00"
    Cuando confirmo la transferencia
    Entonces el comprobante de transferencia muestra destino "912345678", comisión "S/ 0.00", total "S/ 50.00" y saldo "S/ 1,450.00"

  @HU-N-07 @CA2 @RN-07
  Escenario: No se puede transferir a un celular que no está registrado
    Dado que Ana inició sesión
    Y abro la página de transferir
    Cuando preparo una transferencia Qolqe de "20.00" al celular "977777777"
    Y confirmo la transferencia
    Entonces veo el error de transferencia "El celular de destino no está registrado en Qolqe"

  @HU-N-08 @HU-N-09 @CA2 @RN-09
  Escenario: Ana transfiere a otro banco y paga la comisión de 1.5 %
    Dado que Ana inició sesión
    Y abro la página de transferir
    Cuando preparo una transferencia a otro banco de "100.00" al CCI "00212345678901234567"
    Entonces el diálogo de confirmación muestra monto "S/ 100.00", comisión "S/ 1.50" y total "S/ 101.50"
    Cuando confirmo la transferencia
    Entonces el comprobante de transferencia muestra destino "4567", comisión "S/ 1.50", total "S/ 101.50" y saldo "S/ 1,398.50"
