*** Settings ***
Documentation     PASOS (step definitions) de nucleo_comun.feature.
...               El parser Gherkin importa solo los .resource de features/e2e/; aquí se
...               traduce cada frase a acciones de los Page Objects (tests/e2e/pages/).
...               Robot quita el prefijo Dado/Cuando/Entonces/Y (opción --language es).
Resource          ../../../tests/e2e/resources/Comun.resource
Resource          ../../../tests/e2e/pages/LoginPage.resource
Resource          ../../../tests/e2e/pages/RegistroPage.resource
Resource          ../../../tests/e2e/pages/InicioPage.resource
Resource          ../../../tests/e2e/pages/PerfilPage.resource
Resource          ../../../tests/e2e/pages/TransferirPage.resource


*** Variables ***
# Datos semilla de Qolqe (README, sección 4)
${CELULAR_ANA}    987654321
${PIN_ANA}        4826


*** Keywords ***
# ---------- Sesión (HU-N-01, HU-N-02, HU-N-03) ----------
que Ana inició sesión
    [Documentation]    Precondición: login por API (motivo: DEF-06, ver LoginPage.Iniciar Sesion Por API).
    Iniciar Sesion Por API    ${CELULAR_ANA}    ${PIN_ANA}

que estoy en la página de login
    Abrir Pagina De Login

que estoy en la página de registro
    Abrir Pagina De Registro

me registro con DNI "${dni}", nombres "${nombres}", celular "${celular}" y PIN "${pin}"
    Registrarse    ${dni}    ${nombres}    ${celular}    ${pin}

que me registré con DNI "${dni}", nombres "${nombres}", celular "${celular}" y PIN "${pin}"
    Abrir Pagina De Registro
    Registrarse    ${dni}    ${nombres}    ${celular}    ${pin}
    El Aviso De Login Deberia Ser    Tu cuenta fue creada. Ya puedes ingresar.

ingreso con celular "${celular}" y PIN "${pin}"
    Iniciar Sesion    ${celular}    ${pin}

que inicié sesión con celular "${celular}" y PIN "${pin}"
    Iniciar Sesion Por API    ${celular}    ${pin}

ingreso ${veces} veces con celular "${celular}" y PIN "${pin}"
    [Documentation]    Cada intento espera la respuesta (el mensaje de error) antes del siguiente.
    FOR    ${_}    IN RANGE    ${veces}
        Iniciar Sesion    ${celular}    ${pin}
        Wait For Elements State    ${LOGIN_ERROR}    visible
    END

estoy en la página de inicio
    [Documentation]    Solo la firma exacta de DEF-06 (401 tras un login correcto) da SKIP; cualquier otro fallo es FAIL.
    ${ok}=    Run Keyword And Return Status    Deberia Estar En Inicio
    IF    not ${ok}
        ${url}=    Get Url
        Skip If    'motivo=sesion' in $url    DEF-06: 401 justo después de un login correcto
        Fail    Login roto, sin la firma de DEF-06: ${url}
    END

sigo en la página de login
    Deberia Estar En Login

veo el saludo "${texto}"
    El Saludo Deberia Ser    ${texto}

veo el error de login "${texto}"
    El Error De Login Deberia Contener    ${texto}

veo el aviso de inicio de sesión "${texto}"
    El Aviso De Login Deberia Ser    ${texto}

cierro sesión
    Cerrar Sesion

al abrir la página de inicio vuelvo al login
    Abrir Pagina De Inicio
    Deberia Estar En Login

# ---------- Saldo y perfil (HU-N-04, HU-N-05, HU-N-06) ----------
veo mi saldo "${saldo}"
    El Saldo Deberia Ser    ${saldo}

abro mi perfil
    Ir A Mi Perfil

mi perfil muestra nombres "${nombres}", celular "${celular}", DNI "${dni}" y correo "${correo}"
    Comprobar    El Perfil Deberia Mostrar    ${nombres}    ${celular}    ${dni}    ${correo}

cambio mis nombres a "${nombres}" y mi correo a "${correo}"
    Editar Perfil    ${nombres}    ${correo}

recargo mi perfil
    Marcar Para Recargar

veo el mensaje de perfil "${texto}"
    El Mensaje De Perfil Deberia Ser    ${texto}

cierro mi cuenta con PIN "${pin}"
    Solicitar Cierre De Cuenta    ${pin}

el diálogo de cierre muestra el error "${texto}"
    El Error Del Dialogo Deberia Contener    ${texto}

# ---------- Transferencias (HU-N-07, HU-N-08, HU-N-09) ----------
abro la página de transferir
    Ir A Transferir

preparo una transferencia Qolqe de "${monto}" al celular "${celular}"
    Preparar Transferencia Qolqe    ${celular}    ${monto}

preparo una transferencia a otro banco de "${monto}" al CCI "${cci}"
    Preparar Transferencia Interbancaria    ${cci}    ${monto}

el diálogo de confirmación muestra monto "${monto}", comisión "${comision}" y total "${total}"
    El Dialogo De Confirmacion Deberia Mostrar    ${monto}    ${comision}    ${total}

confirmo la transferencia
    Confirmar Transferencia

el comprobante de transferencia muestra destino "${destino}", comisión "${comision}", total "${total}" y saldo "${saldo}"
    El Comprobante De Transferencia Deberia Mostrar    ${destino}    ${comision}    ${total}    ${saldo}

veo el error de transferencia "${texto}"
    El Error De Transferencia Deberia Contener    ${texto}
