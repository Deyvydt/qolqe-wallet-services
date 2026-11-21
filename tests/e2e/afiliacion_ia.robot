*** Settings ***
Documentation     Caso generado con IA a partir de HU-G2-03 y revisado por el equipo.
Resource          resources/Comun.resource
Resource          pages/LoginPage.resource
Resource          pages/ServiciosPage.resource
Test Setup        Abrir Navegador Con Datos Limpios
Test Teardown     Cerrar Navegador


*** Test Cases ***
Ana afilia un servicio de agua
    [Documentation]    HU-G2-03. Generado con IA; corregido por el equipo (ver README).
    [Tags]    G2    e2e    ia    HU-G2-03    CA1    CP-W03    defecto    DEF-06
    Abrir Pagina De Login
    Iniciar Sesion    987654321    4826
    Deberia Estar En Inicio
    Ir A Pagar Servicios
    # Localizadores movidos al Page Object ServiciosPage (antes estaban crudos aquí).
    Afiliar Servicio    AGUA    20000004    Agua mamá
    La Lista De Afiliaciones Deberia Contener    Agua mamá
    El Contador De Afiliaciones Deberia Ser    4 de 8
