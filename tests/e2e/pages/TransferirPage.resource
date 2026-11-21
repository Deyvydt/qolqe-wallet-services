*** Settings ***
Documentation     PAGE OBJECT de la pantalla /transferir (HU-N-07, HU-N-08 y HU-N-09).
Library           Browser


*** Variables ***
${TRF_PESTANA_QOLQE}       css=[data-testid="pestana-qolqe"]
${TRF_PESTANA_BANCO}       css=[data-testid="pestana-interbancaria"]
${TRF_CELULAR}             css=[data-testid="input-celular-destino"]
${TRF_CCI}                 css=[data-testid="input-cci"]
${TRF_MONTO}               css=[data-testid="input-monto"]
${TRF_CONTINUAR}           css=[data-testid="boton-continuar"]
${TRF_ERROR}               css=[data-testid="transferencia-error"]
${TRF_DIALOGO}             css=[data-testid="dialogo-confirmacion"]
${TRF_CONF_MONTO}          css=[data-testid="confirmar-monto"]
${TRF_CONF_COMISION}       css=[data-testid="confirmar-comision"]
${TRF_CONF_TOTAL}          css=[data-testid="confirmar-total"]
${TRF_CONFIRMAR}           css=[data-testid="boton-confirmar"]
${TRF_COMPROBANTE}         css=[data-testid="comprobante"]
${TRF_COMP_CODIGO}         css=[data-testid="comprobante-codigo"]
${TRF_COMP_DESTINO}        css=[data-testid="comprobante-destino"]
${TRF_COMP_COMISION}       css=[data-testid="comprobante-comision"]
${TRF_COMP_TOTAL}          css=[data-testid="comprobante-total"]
${TRF_COMP_SALDO}          css=[data-testid="comprobante-saldo"]


*** Keywords ***
Ir A Transferir
    Click    css=[data-testid="nav-transferir"]
    Get Url    contains    /transferir
    # app.js conecta el formulario DESPUÉS de cargar los contactos (Ana tiene 2):
    # si se pulsa "Continuar" antes, el navegador recarga la página.
    Get Element Count    css=[data-testid="select-contacto"] option    >    1

Preparar Transferencia Qolqe
    [Documentation]    Llena celular y monto y pulsa "Continuar": abre el diálogo con la comisión simulada.
    [Arguments]    ${celular}    ${monto}
    Click        ${TRF_PESTANA_QOLQE}
    Fill Text    ${TRF_CELULAR}    ${celular}
    Fill Text    ${TRF_MONTO}      ${monto}
    Click        ${TRF_CONTINUAR}

Preparar Transferencia Interbancaria
    [Arguments]    ${cci}    ${monto}
    Click        ${TRF_PESTANA_BANCO}
    Fill Text    ${TRF_CCI}      ${cci}
    Fill Text    ${TRF_MONTO}    ${monto}
    Click        ${TRF_CONTINUAR}

El Dialogo De Confirmacion Deberia Mostrar
    [Arguments]    ${monto}    ${comision}    ${total}
    Wait For Elements State    ${TRF_DIALOGO}    visible
    Get Text    ${TRF_CONF_MONTO}       ==    ${monto}
    Get Text    ${TRF_CONF_COMISION}    ==    ${comision}
    Get Text    ${TRF_CONF_TOTAL}       ==    ${total}

Confirmar Transferencia
    Click    ${TRF_CONFIRMAR}

El Comprobante De Transferencia Deberia Mostrar
    [Arguments]    ${destino}    ${comision}    ${total}    ${saldo}
    Wait For Elements State    ${TRF_COMPROBANTE}    visible
    Get Text    ${TRF_COMP_CODIGO}      !=          ${EMPTY}
    Get Text    ${TRF_COMP_DESTINO}     contains    ${destino}
    Get Text    ${TRF_COMP_COMISION}    ==          ${comision}
    Get Text    ${TRF_COMP_TOTAL}       ==          ${total}
    Get Text    ${TRF_COMP_SALDO}       ==          ${saldo}

El Error De Transferencia Deberia Contener
    [Arguments]    ${texto}
    Wait For Elements State    ${TRF_ERROR}    visible
    Get Text    ${TRF_ERROR}    contains    ${texto}
