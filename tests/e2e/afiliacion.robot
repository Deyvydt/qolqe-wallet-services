*** Settings ***
Documentation     CP-W03 · Afiliar un servicio (HU-G2-03).
Resource          resources/Comun.resource
Resource          pages/LoginPage.resource
Resource          pages/ServiciosPage.resource
Test Setup        Abrir Navegador Con Datos Limpios
Test Teardown     Cerrar Navegador


*** Test Cases ***
Ana afilia un servicio de agua
    [Documentation]    HU-G2-03: Ana afilia AGUA con suministro 20000004 y la ve en su lista.
    [Tags]    G2    e2e    HU-G2-03    CA1    CP-W03
    Abrir Pagina De Login
    Iniciar Sesion Por API    987654321    4826
    Ir A Pagar Servicios
    # Localizadores movidos al Page Object ServiciosPage (antes estaban crudos aquí).
    Afiliar Servicio    AGUA    20000004    Agua mamá
    Marcar Para Recargar
    Comprobar    La Lista De Afiliaciones Deberia Contener    Agua mamá
    Comprobar    El Contador De Afiliaciones Deberia Ser    4 de 8
