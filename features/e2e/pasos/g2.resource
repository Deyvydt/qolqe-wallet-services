*** Settings ***
Documentation     PASOS (step definitions) de g2_servicios.feature (G2: pago de servicios y afiliaciones).
...               "que Ana inició sesión" vive en nucleo.resource (el parser importa ambos).
Resource          ../../../tests/e2e/resources/Comun.resource
Resource          ../../../tests/e2e/pages/ServiciosPage.resource


*** Keywords ***
voy a pagar servicios
    Ir A Pagar Servicios

recargo la página
    Marcar Para Recargar

# ---------- Consultar y pagar (HU-G2-01, HU-G2-02) ----------
consulto la deuda de "${empresa}" con suministro "${suministro}"
    Consultar Deuda    ${empresa}    ${suministro}

consulto el suministro "${suministro}" de "${empresa}"
    Consultar Deuda Sin Resultado    ${empresa}    ${suministro}

pago la primera deuda confirmando el total "${total}"
    Pagar Primera Deuda    ${total}

el comprobante muestra empresa "${empresa}", suministro "${suministro}", total "${total}" y saldo "${saldo}"
    El Comprobante Deberia Mostrar    ${empresa}    ${suministro}    ${total}    ${saldo}

la mora del comprobante es "${mora}"
    La Mora Del Comprobante Deberia Ser    ${mora}

veo el mensaje "${texto}" en la consulta
    El Mensaje De Servicios Deberia Ser    ${texto}

# ---------- Afiliaciones (HU-G2-03 a HU-G2-06) ----------
afilio "${empresa}" con suministro "${suministro}" y alias "${alias}"
    Afiliar Servicio    ${empresa}    ${suministro}    ${alias}

mis afiliaciones incluyen "${alias}"
    Comprobar    La Lista De Afiliaciones Deberia Contener    ${alias}

mis afiliaciones no incluyen "${alias}"
    Comprobar    La Lista De Afiliaciones No Deberia Contener    ${alias}

el contador de afiliaciones es "${texto}"
    Comprobar    El Contador De Afiliaciones Deberia Ser    ${texto}

veo el error de afiliación "${texto}"
    El Error De Afiliacion Deberia Ser    ${texto}

cambio el alias de "${alias}" a "${nuevo}"
    Editar Alias De Afiliacion    ${alias}    ${nuevo}

activo el débito automático de "${alias}"
    Cambiar Debito De Afiliacion    ${alias}

el débito automático de "${alias}" está "${estado}"
    Comprobar    El Debito De La Afiliacion Deberia Estar    ${alias}    ${estado}

desafilio "${alias}"
    Desafiliar Servicio    ${alias}

veo el aviso "${texto}"
    El Aviso Deberia Ser    ${texto}

# ---------- Mis pagos (HU-G2-07) ----------
que pagué la deuda de "${empresa}" con suministro "${suministro}" por "${total}"
    Consultar Deuda    ${empresa}    ${suministro}
    Pagar Primera Deuda    ${total}
    Wait For Elements State    ${SERV_COMPROBANTE}    visible

filtro mis pagos por "${opcion}"
    # Ya se comprobó lo guardado; recargar ahora perdería el filtro elegido.
    Set Test Variable    ${RECARGAR}    ${False}
    Filtrar Pagos Por    ${opcion}

la lista de pagos tiene ${cantidad} pago(s)
    Comprobar    La Lista De Pagos Deberia Tener    ${cantidad}

la lista de pagos incluye "${texto}"
    Comprobar    El Pago Deberia Aparecer En La Lista    ${texto}
