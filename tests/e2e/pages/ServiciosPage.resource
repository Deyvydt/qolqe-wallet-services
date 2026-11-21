*** Settings ***
Documentation     PAGE OBJECT de la pantalla /servicios (módulo G2: pago de servicios).
Library           Browser


*** Variables ***
${SERV_EMPRESA}             css=[data-testid="select-empresa"]
${SERV_SUMINISTRO}          css=[data-testid="input-suministro"]
${SERV_BOTON_CONSULTAR}     css=[data-testid="boton-consultar"]
${SERV_DEUDA}               css=[data-testid="deuda"]
${SERV_BOTON_PAGAR}         css=[data-testid="boton-pagar-deuda"]
${SERV_DIALOGO}             css=[data-testid="dialogo-pago"]
${SERV_DIALOGO_TOTAL}       css=[data-testid="pago-total"]
${SERV_BOTON_CONFIRMAR}     css=[data-testid="boton-confirmar-pago"]
${SERV_COMPROBANTE}         css=[data-testid="comprobante"]
${COMP_CODIGO}              css=[data-testid="comprobante-codigo"]
${COMP_EMPRESA}             css=[data-testid="comprobante-empresa"]
${COMP_SUMINISTRO}          css=[data-testid="comprobante-suministro"]
${COMP_TOTAL}               css=[data-testid="comprobante-total"]
${COMP_SALDO}               css=[data-testid="comprobante-saldo"]
${COMP_MORA}                css=[data-testid="comprobante-mora"]
${SERV_ERROR}               css=[data-testid="servicios-error"]
${SERV_CONTADOR}            css=[data-testid="contador-afiliaciones"]
${AFI_EMPRESA}              css=[data-testid="select-afiliacion-empresa"]
${AFI_SUMINISTRO}           css=[data-testid="input-afiliacion-suministro"]
${AFI_ALIAS}                css=[data-testid="input-afiliacion-alias"]
${AFI_BOTON}                css=[data-testid="boton-afiliar"]
${AFI_ERROR}                css=[data-testid="afiliacion-error"]
${AFI_LISTA}                css=[data-testid="lista-afiliaciones"]
${PAGOS_FILTRO}             css=[data-testid="select-filtro-pagos"]
${PAGOS_ITEM}               css=[data-testid="lista-pagos"] >> css=[data-testid="pago"]
# Diálogos que crea app.js: confirmación (confirmar) y formulario (dialogoFormulario)
${DLG_CONFIRMAR}            css=[data-testid="dialogo-confirmar"]
${DLG_BOTON_CONFIRMAR}      css=[data-testid="boton-confirmar-accion"]
${DLG_FORM}                 css=[data-testid="dialogo-formulario"]
${DLG_ALIAS}                css=[data-testid="input-editar-alias"]
${DLG_GUARDAR}              css=[data-testid="boton-guardar-dialogo"]
${TOAST}                    css=[data-testid="toast"]


*** Keywords ***
Ir A Pagar Servicios
    Click    css=[data-testid="nav-servicios"]
    Get Url    contains    /servicios
    # Esperar a que la pantalla TERMINE de cargar (sus datos llegan por API).
    # Sin esto la prueba era frágil: escribía antes de que la página estuviera lista.
    Get Text    ${SERV_CONTADOR}    contains    de 8

Consultar Deuda
    [Documentation]    Elige la empresa, escribe el suministro y consulta.
    [Arguments]    ${empresa}    ${suministro}
    Select Options By    ${SERV_EMPRESA}    value    ${empresa}
    Fill Text            ${SERV_SUMINISTRO}    ${suministro}
    Click                ${SERV_BOTON_CONSULTAR}
    # Espera por CONDICIÓN (no sleep): que aparezca al menos una deuda
    Wait For Elements State    ${SERV_DEUDA} >> nth=0    visible

Pagar Primera Deuda
    [Documentation]    Pulsa "Pagar" en la primera deuda y confirma en el diálogo.
    [Arguments]    ${total_esperado}
    Click    ${SERV_DEUDA} >> nth=0 >> ${SERV_BOTON_PAGAR}
    Wait For Elements State    ${SERV_DIALOGO}    visible
    Get Text    ${SERV_DIALOGO_TOTAL}    ==    ${total_esperado}
    Click    ${SERV_BOTON_CONFIRMAR}

El Comprobante Deberia Mostrar
    [Documentation]    Verifica el comprobante (HU-G2-02, CA4).
    [Arguments]    ${empresa}    ${suministro}    ${total}    ${saldo}
    Wait For Elements State    ${SERV_COMPROBANTE}    visible
    Get Text    ${COMP_CODIGO}        !=    ${EMPTY}
    Get Text    ${COMP_EMPRESA}       ==    ${empresa}
    Get Text    ${COMP_SUMINISTRO}    ==    ${suministro}
    Get Text    ${COMP_TOTAL}         ==    ${total}
    Get Text    ${COMP_SALDO}         ==    ${saldo}

La Mora Del Comprobante Deberia Ser
    [Arguments]    ${mora}
    Get Text    ${COMP_MORA}    ==    ${mora}

Consultar Deuda Sin Resultado
    [Documentation]    Consulta un suministro que no devuelve deudas (error o sin deuda pendiente).
    [Arguments]    ${empresa}    ${suministro}
    Select Options By    ${SERV_EMPRESA}    value    ${empresa}
    Fill Text            ${SERV_SUMINISTRO}    ${suministro}
    Click                ${SERV_BOTON_CONSULTAR}

El Mensaje De Servicios Deberia Ser
    [Arguments]    ${texto}
    Wait For Elements State    ${SERV_ERROR}    visible
    Get Text    ${SERV_ERROR}    ==    ${texto}

Afiliar Servicio
    [Documentation]    HU-G2-03: llena empresa, suministro y alias, y pulsa "Afiliar servicio".
    [Arguments]    ${empresa}    ${suministro}    ${alias}
    Select Options By    ${AFI_EMPRESA}    value    ${empresa}
    Fill Text            ${AFI_SUMINISTRO}    ${suministro}
    Fill Text            ${AFI_ALIAS}         ${alias}
    Click                ${AFI_BOTON}

La Lista De Afiliaciones Deberia Contener
    [Arguments]    ${alias}
    Get Text    ${AFI_LISTA}    contains    ${alias}

La Lista De Afiliaciones No Deberia Contener
    [Arguments]    ${alias}
    Get Text    ${SERV_CONTADOR}    contains    de 8    # espera a que la lista cargue
    Get Text    ${AFI_LISTA}    not contains    ${alias}

El Contador De Afiliaciones Deberia Ser
    [Arguments]    ${texto}
    Get Text    ${SERV_CONTADOR}    ==    ${texto}

El Error De Afiliacion Deberia Ser
    [Arguments]    ${texto}
    Wait For Elements State    ${AFI_ERROR}    visible
    Get Text    ${AFI_ERROR}    ==    ${texto}

Afiliacion
    [Documentation]    Localizador de la tarjeta de una afiliación según su alias exacto.
    [Arguments]    ${alias}
    RETURN    css=[data-testid="afiliacion"]:has([data-testid="afiliacion-alias"]:text-is("${alias}"))

Editar Alias De Afiliacion
    [Arguments]    ${alias}    ${nuevo_alias}
    ${tarjeta}=    Afiliacion    ${alias}
    Click    ${tarjeta} >> css=[data-testid="boton-editar-afiliacion"]
    Wait For Elements State    ${DLG_FORM}    visible
    Fill Text    ${DLG_ALIAS}    ${nuevo_alias}
    Click    ${DLG_GUARDAR}
    Wait For Elements State    ${DLG_FORM}    detached

Cambiar Debito De Afiliacion
    [Documentation]    Pulsa "Activar/Desactivar débito" y confirma en el diálogo.
    [Arguments]    ${alias}
    ${tarjeta}=    Afiliacion    ${alias}
    Click    ${tarjeta} >> css=[data-testid="boton-debito-afiliacion"]
    Wait For Elements State    ${DLG_CONFIRMAR}    visible
    Click    ${DLG_BOTON_CONFIRMAR}

El Debito De La Afiliacion Deberia Estar
    [Documentation]    estado: activado | desactivado
    [Arguments]    ${alias}    ${estado}
    ${tarjeta}=    Afiliacion    ${alias}
    Get Text    ${tarjeta} >> css=[data-testid="afiliacion-debito"]    ==    Débito automático: ${estado}

Desafiliar Servicio
    [Arguments]    ${alias}
    ${tarjeta}=    Afiliacion    ${alias}
    Click    ${tarjeta} >> css=[data-testid="boton-desafiliar"]
    Wait For Elements State    ${DLG_CONFIRMAR}    visible
    Click    ${DLG_BOTON_CONFIRMAR}

El Aviso Deberia Ser
    [Documentation]    Mensaje emergente (toast) que muestra la app tras una acción.
    [Arguments]    ${texto}
    Get Text    ${TOAST}    ==    ${texto}

Filtrar Pagos Por
    [Documentation]    Elige una opción del filtro "Filtrar por servicio afiliado" por su texto.
    [Arguments]    ${opcion}
    Select Options By    ${PAGOS_FILTRO}    label    ${opcion}

La Lista De Pagos Deberia Tener
    [Arguments]    ${cantidad}
    Get Element Count    ${PAGOS_ITEM}    ==    ${cantidad}

El Pago Deberia Aparecer En La Lista
    [Arguments]    ${texto}
    Get Text    css=[data-testid="lista-pagos"]    contains    ${texto}
