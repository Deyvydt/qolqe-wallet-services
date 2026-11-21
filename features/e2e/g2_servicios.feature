# language: es
# ─────────────────────────────────────────────────────────────────────────
# QUÉ ES: escenarios E2E (por la interfaz web) del módulo G2: pago de servicios y afiliaciones.
# CÓMO SE EJECUTA: Robot Framework lee este archivo con robotframework-gherkin-parser;
#   cada frase es una keyword de features/e2e/pasos/g2.resource (Page Object ServiciosPage).
#   robot --parser GherkinParser --language es -v URL:http://127.0.0.1:8000 features/e2e
# DATOS (semilla, relativos a HOY): ELECTRO 10000001 S/ 120.00 vence en 10 días;
#   AGUA 2000000008 S/ 45.00 vence en 3 días; ELECTRO 100000009 S/ 78.30 venció hace 5 días.
#   Afiliaciones de Ana: "Luz casa" (débito off), "Agua depa" (débito ON), "Internet casa".
# ─────────────────────────────────────────────────────────────────────────
@e2e @G2
Característica: G2 Pago de servicios y afiliaciones por la interfaz web
  Como cliente de Qolqe
  quiero pagar mis recibos y guardar mis servicios frecuentes
  para no acudir a una agencia

  Antecedentes:
    Dado que Ana inició sesión
    Y voy a pagar servicios

  @HU-G2-01 @HU-G2-02 @CA1 @CA4 @camino-feliz @CP-W01
  Escenario: Ana paga su recibo de luz y ve el comprobante
    Cuando consulto la deuda de "ELECTRO" con suministro "10000001"
    Y pago la primera deuda confirmando el total "S/ 120.00"
    Entonces el comprobante muestra empresa "ELECTRO", suministro "10000001", total "S/ 120.00" y saldo "S/ 1,380.00"
    Y la mora del comprobante es "S/ 0.00"

  @HU-G2-01 @HU-G2-02 @CA1 @CA4 @camino-feliz @CP-W02
  Escenario: Ana paga su recibo de agua y ve el comprobante
    Cuando consulto la deuda de "AGUA" con suministro "2000000008"
    Y pago la primera deuda confirmando el total "S/ 45.00"
    Entonces el comprobante muestra empresa "AGUA", suministro "2000000008", total "S/ 45.00" y saldo "S/ 1,455.00"

  # DEFECTO CONOCIDO DEF-02 (docs/defectos.md): los días de atraso se cuentan con +1.
  # Los valores esperados son los de la REGLA; el escenario falla por el defecto y Robot lo
  # reporta como SKIP ("fallo esperado") gracias a --skiponfailure defecto. Si se corrige, pasa.
  @HU-G2-02 @CA1 @R-G2-03 @valor-limite @defecto @DEF-02
  Esquema del escenario: La mora del comprobante respeta R-G2-03 (<caso>)
    Cuando consulto la deuda de "ELECTRO" con suministro "<suministro>"
    Y pago la primera deuda confirmando el total "<total>"
    Entonces el comprobante muestra empresa "ELECTRO", suministro "<suministro>", total "<total>" y saldo "<saldo>"
    Y la mora del comprobante es "<mora>"

    Ejemplos:
      | caso                                 | suministro | mora    | total    | saldo       |
      | vence hoy, sin mora                  | 10000002   | S/ 0.00 | S/ 85.50 | S/ 1,414.50 |
      | vencida hace 5 días, 2.5 % de mora   | 100000009  | S/ 1.96 | S/ 80.26 | S/ 1,419.74 |

  @HU-G2-01 @CA3
  Escenario: Un suministro sin deudas pendientes muestra un aviso
    Cuando consulto el suministro "99999999" de "ELECTRO"
    Entonces veo el mensaje "El suministro no tiene deudas pendientes" en la consulta

  @HU-G2-01 @CA1 @R-G2-01 @valor-limite
  Escenario: Un suministro de menos de 8 dígitos es rechazado
    Cuando consulto el suministro "1234567" de "ELECTRO"
    Entonces veo el mensaje "El código de suministro debe tener entre 8 y 12 dígitos" en la consulta

  # Tras una acción (afiliar, editar, desafiliar, pagar) se verifica el aviso de la respuesta y,
  # luego de RECARGAR la página, lo que quedó guardado. La lista que la app repinta al instante
  # puede salir desactualizada (DEF-06); eso lo cubre el último escenario de este archivo.
  @HU-G2-03 @CA1 @CA4 @CP-W03
  Escenario: Ana afilia su servicio de agua
    Cuando afilio "AGUA" con suministro "20000004" y alias "Agua mamá"
    Entonces veo el aviso "Servicio "Agua mamá" afiliado"
    Cuando recargo la página
    Entonces mis afiliaciones incluyen "Agua mamá"
    Y el contador de afiliaciones es "4 de 8"
    Y el débito automático de "Agua mamá" está "desactivado"

  @HU-G2-03 @CA2
  Escenario: No se puede afiliar un suministro que no existe en la empresa
    Cuando afilio "AGUA" con suministro "29999999" y alias "No existe"
    Entonces veo el error de afiliación "El suministro no existe en la empresa"
    Y el contador de afiliaciones es "3 de 8"

  @HU-G2-05 @CA1
  Escenario: Ana cambia el alias de un servicio afiliado
    Cuando cambio el alias de "Luz casa" a "Luz departamento"
    Entonces veo el aviso "Servicio actualizado"
    Cuando recargo la página
    Entonces mis afiliaciones incluyen "Luz departamento"
    Y mis afiliaciones no incluyen "Luz casa"

  @HU-G2-05 @CA1
  Escenario: Ana activa el débito automático de su servicio de luz
    Cuando activo el débito automático de "Luz casa"
    Entonces veo el aviso "Débito automático activado"
    Cuando recargo la página
    Entonces el débito automático de "Luz casa" está "activado"

  @HU-G2-06 @CA1
  Escenario: Ana desafilia un servicio sin débito automático
    Cuando desafilio "Luz casa"
    Entonces veo el aviso "Servicio desafiliado"
    Cuando recargo la página
    Entonces mis afiliaciones no incluyen "Luz casa"
    Y el contador de afiliaciones es "2 de 8"

  @HU-G2-06 @CA2
  Escenario: No se puede desafiliar un servicio con el débito automático activo
    Cuando desafilio "Agua depa"
    Entonces veo el aviso "Desactiva el débito automático antes de desafiliar el servicio"
    Y mis afiliaciones incluyen "Agua depa"
    Y el contador de afiliaciones es "3 de 8"

  @HU-G2-07 @CA1
  Escenario: Ana filtra sus pagos por servicio afiliado
    Dado que pagué la deuda de "ELECTRO" con suministro "10000001" por "S/ 120.00"
    Y que pagué la deuda de "AGUA" con suministro "2000000008" por "S/ 45.00"
    Cuando recargo la página
    Entonces la lista de pagos tiene 2 pago(s)
    Cuando filtro mis pagos por "Luz casa"
    Entonces la lista de pagos tiene 1 pago(s)
    Y la lista de pagos incluye "ELECTRO · 10000001"

  # DEFECTO DEF-06: la API responde ANTES de guardar (commit) los cambios. La app vuelve a pedir
  # la lista apenas recibe la respuesta y a veces recibe los datos viejos: el usuario sigue viendo
  # el servicio que acaba de desafiliar. Falla de forma intermitente; si falla, Robot lo reporta
  # como SKIP con el fallo original (--skiponfailure defecto).
  @HU-G2-06 @HU-G2-04 @CA1 @defecto @DEF-06
  Escenario: La lista de afiliaciones se actualiza al instante al desafiliar
    Cuando desafilio "Luz casa"
    Entonces veo el aviso "Servicio desafiliado"
    Y mis afiliaciones no incluyen "Luz casa"
    Y el contador de afiliaciones es "2 de 8"
