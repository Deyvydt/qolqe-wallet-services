*** Settings ***
Documentation     PAGE OBJECT de la pantalla /login.
...               Aquí viven los LOCALIZADORES (cómo encontrar cada elemento)
...               y las ACCIONES (qué puede hacer el usuario).
...               Si la pantalla cambia, solo se corrige ESTE archivo.
Library           Browser


*** Variables ***
# Localizadores: usamos data-testid (atributo pensado para pruebas, estable)
${LOGIN_CELULAR}      css=[data-testid="input-celular"]
${LOGIN_PIN}          css=[data-testid="input-pin"]
${LOGIN_BOTON}        css=[data-testid="boton-ingresar"]
${LOGIN_ERROR}        css=[data-testid="login-error"]
${LOGIN_AVISO}        css=[data-testid="login-aviso"]
${INICIO_SALDO}       css=[data-testid="saldo-valor"]


*** Keywords ***
Abrir Pagina De Login
    Go To    ${URL}/login

Iniciar Sesion
    [Documentation]    Llena celular y PIN, y pulsa "Ingresar".
    [Arguments]    ${celular}    ${pin}
    Fill Text      ${LOGIN_CELULAR}    ${celular}
    Fill Secret    ${LOGIN_PIN}        $pin
    Click          ${LOGIN_BOTON}

Iniciar Sesion Por API
    [Documentation]    Atajo para PRECONDICIONES ("Dado que Ana inició sesión"): obtiene el token por
    ...                API, espera a que la sesión quede guardada en la BD y lo deja en el navegador.
    ...                Por qué: DEF-06, la API responde el login ANTES de guardar la sesión, y la
    ...                primera petición de /inicio a veces recibe 401 (la app expulsa al usuario).
    ...                Los escenarios cuyo objetivo es el login lo siguen haciendo por la pantalla.
    ...                También reintenta el login: un usuario recién registrado puede no estar guardado aún.
    [Arguments]    ${celular}    ${pin}
    ${login}=    Wait Until Keyword Succeeds    10x    500ms
    ...    Obtener Sesion Activa Por API    ${celular}    ${pin}
    Evaluate JavaScript    ${None}
    ...    (datos) => sessionStorage.setItem("qolqe.sesion", JSON.stringify(datos))    arg=${login.body}
    Go To    ${URL}/inicio
    Deberia Estar En Inicio

Obtener Sesion Activa Por API
    [Documentation]    Login por API y comprobación de que el token ya sirve (la sesión quedó guardada).
    [Arguments]    ${celular}    ${pin}
    &{login}=    Http    ${URL}/api/auth/login    method=POST
    ...    body={"celular": "${celular}", "pin": "${pin}"}    headers={"Content-Type": "application/json"}
    Should Be Equal As Integers    ${login.status}    200    Login por API: ${login.body}
    Wait Until Keyword Succeeds    10x    300ms
    ...    La Sesion Deberia Estar Activa    ${login.body}[access_token]
    RETURN    ${login}

La Sesion Deberia Estar Activa
    [Arguments]    ${token}
    &{r}=    Http    ${URL}/api/cuentas/me    headers={"Authorization": "Bearer ${token}"}
    Should Be Equal As Integers    ${r.status}    200

Deberia Estar En Inicio
    [Documentation]    Las aserciones de Browser REINTENTAN solas hasta el timeout (espera automática).
    Get Url    contains    /inicio
    Get Text    ${INICIO_SALDO}    contains    S/

Deberia Estar En Login
    Get Url    contains    /login
    Wait For Elements State    ${LOGIN_BOTON}    visible

El Error De Login Deberia Contener
    [Documentation]    Al pulsar "Ingresar" la app oculta el error anterior; esperamos al nuevo.
    [Arguments]    ${texto}
    Wait For Elements State    ${LOGIN_ERROR}    visible
    Get Text    ${LOGIN_ERROR}    contains    ${texto}

El Aviso De Login Deberia Ser
    [Arguments]    ${texto}
    Get Url    contains    /login
    Get Text    ${LOGIN_AVISO}    ==    ${texto}
