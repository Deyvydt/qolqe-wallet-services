*** Settings ***
Documentation     PAGE OBJECT de la pantalla /inicio y del MENÚ lateral (común a las páginas privadas).
Library           Browser


*** Variables ***
${INI_SALUDO}            css=[data-testid="saludo"]
${INI_SALDO}             css=[data-testid="saldo-valor"]
${MENU_CERRAR_SESION}    css=[data-testid="boton-cerrar-sesion"]


*** Keywords ***
Abrir Pagina De Inicio
    Go To    ${URL}/inicio

El Saludo Deberia Ser
    [Arguments]    ${texto}
    Get Text    ${INI_SALUDO}    ==    ${texto}

El Saldo Deberia Ser
    [Documentation]    El saldo llega por API: la aserción reintenta hasta que aparece.
    [Arguments]    ${saldo}
    Get Text    ${INI_SALDO}    ==    ${saldo}

Ir A La Opcion Del Menu
    [Documentation]    Opciones: inicio, transferir, servicios, perfil, ... (data-testid="nav-<ruta>").
    [Arguments]    ${ruta}
    Click    css=[data-testid="nav-${ruta}"]
    Get Url    contains    /${ruta}

Cerrar Sesion
    Click    ${MENU_CERRAR_SESION}
