*** Settings ***
Documentation     Configuración común y FIXTURES (preparar antes / limpiar después).
Library           Browser


*** Variables ***
${URL}         http://localhost:8000
${BROWSER}     chromium
${HEADLESS}    True


*** Keywords ***
Abrir Navegador Con Datos Limpios
    [Documentation]    Fixture de PREPARACIÓN: abre el navegador y reinicia los datos semilla
    ...                de Qolqe por API (así cada prueba es independiente: FIRST).
    New Browser    ${BROWSER}    headless=${HEADLESS}
    New Context    viewport={'width': 1280, 'height': 800}    tracing=retain-on-failure
    Set Browser Timeout    10s
    New Page       ${URL}/login
    &{respuesta}=    Http    ${URL}/api/pruebas/reiniciar    method=POST
    Should Be Equal As Integers    ${respuesta.status}    200

Cerrar Navegador
    [Documentation]    Fixture de LIMPIEZA: toma captura final y cierra todo.
    Take Screenshot    fullPage=True
    Close Browser    ALL
