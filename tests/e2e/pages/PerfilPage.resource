*** Settings ***
Documentation     PAGE OBJECT de la pantalla /perfil (HU-N-04, HU-N-05 y HU-N-06).
Library           Browser


*** Variables ***
${PER_NOMBRES}           css=[data-testid="perfil-nombres"]
${PER_CELULAR}           css=[data-testid="perfil-celular"]
${PER_DNI}               css=[data-testid="perfil-dni"]
${PER_CORREO}            css=[data-testid="perfil-correo"]
${PER_INPUT_NOMBRES}     css=[data-testid="input-nombres"]
${PER_INPUT_CORREO}      css=[data-testid="input-correo"]
${PER_BOTON_GUARDAR}     css=[data-testid="boton-guardar-perfil"]
${PER_MENSAJE}           css=[data-testid="perfil-mensaje"]
${PER_BOTON_CERRAR}      css=[data-testid="boton-cerrar-cuenta"]
# Diálogo genérico con formulario que crea app.js (dialogoFormulario)
${DIALOGO_FORM}          css=[data-testid="dialogo-formulario"]
${DIALOGO_PIN_CIERRE}    css=[data-testid="input-pin-cierre"]
${DIALOGO_GUARDAR}       css=[data-testid="boton-guardar-dialogo"]
${DIALOGO_ERROR}         css=[data-testid="dialogo-error"]


*** Keywords ***
Ir A Mi Perfil
    Click    css=[data-testid="nav-perfil"]
    Get Url    contains    /perfil
    # Los datos llegan por API: esperar a que se pinten antes de leer o escribir
    Get Text    ${PER_CELULAR}    !=    ${EMPTY}

El Perfil Deberia Mostrar
    [Arguments]    ${nombres}    ${celular}    ${dni}    ${correo}
    Get Text    ${PER_NOMBRES}    ==    ${nombres}
    Get Text    ${PER_CELULAR}    ==    ${celular}
    Get Text    ${PER_DNI}        ==    ${dni}
    Get Text    ${PER_CORREO}     ==    ${correo}

Editar Perfil
    [Arguments]    ${nombres}    ${correo}
    Fill Text    ${PER_INPUT_NOMBRES}    ${nombres}
    Fill Text    ${PER_INPUT_CORREO}     ${correo}
    Click        ${PER_BOTON_GUARDAR}

El Mensaje De Perfil Deberia Ser
    [Arguments]    ${texto}
    Get Text    ${PER_MENSAJE}    ==    ${texto}

Solicitar Cierre De Cuenta
    [Documentation]    Pulsa "Cerrar mi cuenta" y confirma con el PIN en el diálogo.
    [Arguments]    ${pin}
    Click    ${PER_BOTON_CERRAR}
    Wait For Elements State    ${DIALOGO_FORM}    visible
    Fill Secret    ${DIALOGO_PIN_CIERRE}    $pin
    Click    ${DIALOGO_GUARDAR}

El Error Del Dialogo Deberia Contener
    [Arguments]    ${texto}
    Wait For Elements State    ${DIALOGO_ERROR}    visible
    Get Text    ${DIALOGO_ERROR}    contains    ${texto}
