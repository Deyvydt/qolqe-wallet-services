# E2E · Pruebas web con Robot Framework + Browser Library (Gherkin `.feature`)

Cobertura web de Qolqe por la interfaz (navegador real, Playwright):

- **Escenarios BDD en Gherkin** (`features/e2e/*.feature`, obligatorio): núcleo común (HU-N-01 a HU-N-09) y G2 (HU-G2-01 a HU-G2-07).
- **Casos `.robot`** de la entrega anterior (`tests/e2e/*.robot`): CP-W01 (pagar luz), CP-W02 (pagar agua) y CP-W03 (afiliar).

## Herramienta: `robotframework-gherkin-parser`

Robot Framework **no lee `.feature` por sí solo**. Elegimos el parser oficial de la comunidad
[`robotframework-gherkin-parser`](https://github.com/d-biehl/robotframework-gherkin-parser) porque:

1. Mantiene **una sola herramienta web** (Robot + Browser) y reutiliza los Page Objects, fixtures, reportes y el pipeline que ya teníamos (no hubo que reescribir nada en pytest-playwright).
2. El `.feature` es el caso de prueba real: cada frase `Dado/Cuando/Entonces/Y` se ejecuta como una keyword (no es documentación aparte).
3. Funcionó al primer intento con Robot 7.5 y Gherkin en español (`# language: es`).

Cómo encaja: el parser convierte cada escenario en un test de Robot e **importa solo** los `.resource` de la carpeta del `.feature` (`features/e2e/pasos/`). Esos pasos llaman a los Page Objects de `tests/e2e/pages/`. Con `--language es` Robot quita los prefijos `Dado/Cuando/Entonces/Y/Pero` antes de buscar la keyword. Las etiquetas `@HU-…`, `@CA…`, `@e2e` pasan a ser *tags* de Robot (trazabilidad y filtros con `--include`).

## Estructura (patrón Page Object + Fixtures)

```
features/e2e/                       BDD E2E (lo que se prueba, en Gherkin)
├── __init__.robot                  Fixture de TODOS los escenarios: reiniciar datos + navegador / captura + cerrar
├── nucleo_comun.feature            13 escenarios: HU-N-01..09
├── g2_servicios.feature            14 escenarios: HU-G2-01..07 (incluye CP-W01..03)
└── pasos/
    ├── nucleo.resource             Frase Gherkin → acciones de los Page Objects (núcleo)
    └── g2.resource                 Frase Gherkin → acciones de ServiciosPage
tests/e2e/
├── pago_servicios.robot            CP-W01 en estilo Given/When/Then (.robot)
├── afiliacion.robot                CP-W03 afiliar un servicio (localizadores en ServiciosPage)
├── pago_agua.robot                 CP-W02 pagar un recibo de agua
├── pages/                          ¿CÓMO se usa cada pantalla? (localizadores data-testid + acciones)
│   ├── LoginPage.resource          /login (+ login por API para precondiciones)
│   ├── RegistroPage.resource       /registro
│   ├── InicioPage.resource         /inicio y menú lateral (cerrar sesión)
│   ├── PerfilPage.resource         /perfil (ver, editar, cerrar cuenta)
│   ├── TransferirPage.resource     /transferir (Qolqe e interbancaria, diálogo de comisión, comprobante)
│   └── ServiciosPage.resource      /servicios (consultar, pagar, afiliar, editar, débito, desafiliar, pagos)
└── resources/
    └── Comun.resource              Variables (URL, HEADLESS, SLOWMO, EVIDENCIA) y fixtures
```

Flujo: **escenario `.feature` → paso (`pasos/*.resource`) → Page Object → Browser Library → Playwright → navegador**.

## Requisitos e instalación (una sola vez)

| Herramienta | Versión | Para qué |
|---|---|---|
| Python | 3.11+ | Qolqe y Robot Framework |
| Node.js | 20 o 22 LTS | Browser Library usa Playwright, que corre en Node |

```bash
python -m venv .venv
source .venv/bin/activate              # Windows: .venv\Scripts\activate
pip install -r requirements.txt -r requirements-e2e.txt   # incluye robotframework-gherkin-parser
rfbrowser init chromium                # descarga Playwright + Chromium
```

## Ejecución

**Terminal 1** – levantar Qolqe:

```bash
uvicorn qolqe.main:app --port 8000
```

**Terminal 2** – correr TODA la suite web (`.robot` + `.feature`), igual que el pipeline:

```bash
robot --name "Web E2E" --parser GherkinParser --language es --skiponfailure defecto \
      --outputdir reportes/web -v URL:http://127.0.0.1:8000 tests/e2e features/e2e
```

Variantes útiles (se agregan antes de las carpetas):

| Opción | Efecto |
|---|---|
| `-v HEADLESS:False` | Ver el navegador (demo) |
| `-v SLOWMO:1s` | Demo en cámara lenta |
| `-v EVIDENCIA:sin` | No tomar capturas al final de cada prueba (más rápido); por defecto `con` |
| `--include HU-G2-02` | Solo los escenarios de una historia (cualquier tag sirve: `CP-W01`, `nucleo`, `G2`…) |
| solo `features/e2e` | Solo los escenarios Gherkin |

Resultado esperado: `30 tests, 28 passed, 0 failed, 2 skipped` (los 2 *skipped* son el defecto conocido DEF-02; si en esa corrida se manifiesta el defecto intermitente DEF-06 puede haber alguno más, ver abajo).

> **Windows:** usa `127.0.0.1` en la URL (no `localhost`). Si Robot falla con `RecursionError` o `LookupError: unknown encoding: utf-8:surrogateescape` (terminal de VS Code), ejecuta antes en PowerShell: `$env:PYTHONIOENCODING='utf-8'`.

## Evidencia

Con `EVIDENCIA=con` (por defecto) el teardown toma una captura de página completa al terminar cada prueba. Con `EVIDENCIA=sin` no se toma ninguna, ni siquiera la automática de Browser al fallar un paso (cualquier otro valor hace fallar el teardown, para no equivocarse en silencio). En local, la traza de Playwright se guarda si una prueba falla; en el pipeline, con `sin` también se borra para que el reporte quede sin imágenes.

| Archivo | Qué contiene |
|---|---|
| `reportes/web/report.html` | Resumen: qué pasó, qué falló y qué se omitió (por tag) |
| `reportes/web/log.html` | Cada paso Gherkin y sus keywords, con la captura final (TEST → Teardown → `Take Screenshot`) |
| `reportes/web/browser/screenshot/` | Una captura `.png` por prueba (solo con `EVIDENCIA=con`) |
| `reportes/web/browser/traces/` | Traza Playwright (solo si falla): `npx playwright show-trace <archivo.zip>` |

## Defectos que destapan los escenarios web (`@defecto`)

Los escenarios con `@defecto @DEF-0X` esperan el comportamiento **correcto** según los requisitos. Si fallan por el defecto, `--skiponfailure defecto` los reporta como **SKIP** con el fallo original en el mensaje (no se ocultan: se ven en `report.html`). Si el defecto se corrige, pasan solos.

| Defecto | Escenario | Qué se ve en la web |
|---|---|---|
| DEF-02 (ya reportado) | *La mora del comprobante respeta R-G2-03* (2 ejemplos) | Recibo que vence hoy: total S/ 85.93 (esperado S/ 85.50). Vencido hace 5 días: S/ 80.65 (esperado S/ 80.26) |
| **DEF-06 (nuevo)** | *Ana inicia sesión…*, *Un visitante crea su cuenta…*, *La lista de afiliaciones se actualiza al instante…* | La API responde **antes** de guardar (commit) los cambios. Justo después de un login, la primera petición puede recibir 401 y la app expulsa al usuario a `/login?motivo=sesion`; tras desafiliar o pagar, la lista se repinta con datos viejos. Es intermitente |

Para que el resto de escenarios sea estable sin esconder DEF-06: las **precondiciones** (`Dado que Ana inició sesión`) inician sesión por API y esperan a que la sesión exista (`LoginPage.Iniciar Sesion Por API`), y lo guardado tras una acción se verifica **recargando la página** (`Comun.Comprobar`: hasta 5 recargas, porque el commit llega después de la respuesta). Los escenarios cuyo objetivo es el login o el refresco inmediato siguen haciéndolo por la pantalla y llevan `@DEF-06`.

## Decisiones de diseño

- **Localizadores `data-testid`**: Qolqe los expone en todos los elementos; no dependen del texto ni del estilo. Los textos esperados se tomaron de `qolqe/web/*.html`, `static/app.js` y `qolqe/contrato.py`.
- **Sin `Sleep`**: las aserciones de Browser (`Get Text … ==`, `Get Element Count … ==`) reintentan solas hasta 15 s; se espera por condición (diálogo visible, contador cargado, contactos cargados).
- **Datos independientes (FIRST)**: cada escenario reinicia los datos con `POST /api/pruebas/reiniciar` (fixture en `features/e2e/__init__.robot` y en cada `.robot`). Los montos con mora dependen de "hoy", y la semilla también: son deterministas.
- **Cerrar cuenta (HU-N-06)**: se automatiza con un usuario recién registrado (saldo S/ 0.00, sin solicitudes), así no depende de datos previos.
