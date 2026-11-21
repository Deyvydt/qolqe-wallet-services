*** Settings ***
Documentation     Configuración común y FIXTURES (preparar antes / limpiar después).
...               La usan los .robot de tests/e2e y los .feature de features/e2e.
Library           Browser


*** Variables ***
${URL}         http://localhost:8000
${BROWSER}     chromium
${HEADLESS}    True
# Pausa entre cada acción del navegador. Para la demo: -v SLOWMO:1s
${SLOWMO}      0s
# Evidencia: "con" toma una captura al terminar cada prueba (y al fallar un paso); "sin" no
# toma ninguna captura (más rápido). La traza de Playwright se guarda siempre que una prueba falla.
${EVIDENCIA}   con


*** Keywords ***
Abrir Navegador Con Datos Limpios
    [Documentation]    Fixture de PREPARACIÓN: abre el navegador y reinicia los datos semilla
    ...                de Qolqe por API (así cada prueba es independiente: FIRST).
    New Browser    ${BROWSER}    headless=${HEADLESS}    slowMo=${SLOWMO}
    New Context    viewport={'width': 1280, 'height': 800}    tracing=retain-on-failure
    # 15 s: en una máquina cargada la app tarda más en pintar los datos que llegan por API.
    Set Browser Timeout    15s
    # Con EVIDENCIA=sin tampoco se toma la captura automática al fallar (queda la traza).
    IF    $EVIDENCIA == 'sin'    Register Keyword To Run On Failure    NONE
    New Page       ${URL}/login
    &{respuesta}=    Http    ${URL}/api/pruebas/reiniciar    method=POST
    Should Be Equal As Integers    ${respuesta.status}    200

Marcar Para Recargar
    [Documentation]    Desde aquí, las verificaciones de Comprobar leen lo GUARDADO recargando la página.
    Set Test Variable    ${RECARGAR}    ${True}

Comprobar
    [Documentation]    Ejecuta una verificación. Si la prueba pidió recargar (Marcar Para Recargar),
    ...                recarga y reintenta hasta 5 veces: la API confirma (commit) los cambios
    ...                DESPUÉS de responder (DEF-06), así que la primera recarga puede llegar antes.
    [Arguments]    ${keyword}    @{args}
    ${recargar}=    Get Variable Value    ${RECARGAR}    ${False}
    IF    ${recargar}
        Wait Until Keyword Succeeds    5x    1s    Recargar Y Comprobar    ${keyword}    @{args}
    ELSE
        Run Keyword    ${keyword}    @{args}
    END

Recargar Y Comprobar
    [Arguments]    ${keyword}    @{args}
    Reload
    ${anterior}=    Set Browser Timeout    3s
    TRY
        Run Keyword    ${keyword}    @{args}
    FINALLY
        Set Browser Timeout    ${anterior}
    END

Cerrar Navegador
    [Documentation]    Fixture de LIMPIEZA: toma la captura final (si EVIDENCIA=con) y cierra todo.
    Should Be True    $EVIDENCIA in ('con', 'sin')    EVIDENCIA debe ser "con" o "sin" (vino "${EVIDENCIA}")
    IF    $EVIDENCIA == 'con'    Take Screenshot    fullPage=True
    Close Browser    ALL
