*** Settings ***
Documentation     PAGE OBJECT de la pantalla /registro (HU-N-01).
Library           Browser


*** Variables ***
${REG_DNI}              css=[data-testid="input-dni"]
${REG_NOMBRES}          css=[data-testid="input-nombres"]
${REG_CELULAR}          css=[data-testid="input-celular"]
${REG_CORREO}           css=[data-testid="input-correo"]
${REG_PIN}              css=[data-testid="input-pin"]
${REG_PIN_CONFIRMA}     css=[data-testid="input-pin-confirmacion"]
${REG_BOTON}            css=[data-testid="boton-registrar"]
${REG_ERROR}            css=[data-testid="registro-error"]


*** Keywords ***
Abrir Pagina De Registro
    Go To    ${URL}/registro
    Wait For Elements State    ${REG_BOTON}    visible

Registrarse
    [Documentation]    Llena el formulario (sin correo, es opcional) y pulsa "Crear cuenta".
    [Arguments]    ${dni}    ${nombres}    ${celular}    ${pin}
    Fill Text      ${REG_DNI}             ${dni}
    Fill Text      ${REG_NOMBRES}         ${nombres}
    Fill Text      ${REG_CELULAR}         ${celular}
    Fill Secret    ${REG_PIN}             $pin
    Fill Secret    ${REG_PIN_CONFIRMA}    $pin
    Click          ${REG_BOTON}

El Error De Registro Deberia Contener
    [Arguments]    ${texto}
    Wait For Elements State    ${REG_ERROR}    visible
    Get Text    ${REG_ERROR}    contains    ${texto}
