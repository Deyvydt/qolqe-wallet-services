# Validación del agente de triaje · 2026-11-20

Casos etiquetados: 10 (`tests/triaje/casos_etiquetados.json`). Modelo: `claude-haiku-5-5` (Claude API (Anthropic)).

| Clasificador | Categoría correcta | DEF correcto |
|---|---:|---:|
| Línea base (reglas) | 9/10 (90%) | 10/10 (100%) |
| Agente IA | 10/10 (100%) | 10/10 (100%) |

## Caso por caso

| Caso | Esperado | Reglas | IA | Herramientas usadas por el agente | Confianza IA |
|---|---|---|---|---|---:|
| C01 | defecto_real / DEF-01 | defecto_real ✅ / DEF-01 ✅ | defecto_real ✅ / DEF-01 ✅ | leer_defectos, leer_fragmento_codigo | 0.95 |
| C02 | defecto_real / DEF-02 | defecto_real ✅ / DEF-02 ✅ | defecto_real ✅ / DEF-02 ✅ | leer_defectos, leer_fragmento_codigo | 0.95 |
| C03 | defecto_real / DEF-03 | defecto_real ✅ / DEF-03 ✅ | defecto_real ✅ / DEF-03 ✅ | leer_defectos, leer_fragmento_codigo | 0.93 |
| C04 | defecto_real / DEF-04 | defecto_real ✅ / DEF-04 ✅ | defecto_real ✅ / DEF-04 ✅ | leer_defectos, leer_fragmento_codigo | 0.95 |
| C05 | defecto_real / DEF-05 | defecto_real ✅ / DEF-05 ✅ | defecto_real ✅ / DEF-05 ✅ | leer_defectos | 0.90 |
| C06 | entorno / — | entorno ✅ / — ✅ | entorno ✅ / — ✅ | ninguna | 0.90 |
| C07 | entorno / — | entorno ✅ / — ✅ | entorno ✅ / — ✅ | leer_defectos | 0.85 |
| C08 | prueba_fragil / — | prueba_fragil ✅ / — ✅ | prueba_fragil ✅ / — ✅ | leer_defectos | 0.90 |
| C09 | prueba_fragil / — | defecto_real ❌ / — ✅ | prueba_fragil ✅ / — ✅ | leer_defectos | 0.85 |
| C10 | defecto_real / — | defecto_real ✅ / — ✅ | defecto_real ✅ / — ✅ | leer_defectos, leer_fragmento_codigo | 0.60 |

> Las tablas de arriba las genera `python .github/scripts/validar_triaje.py --destino docs`.
> Lo que sigue es el análisis.

## Resultado de la validación con el modelo

Se ejecutó el agente con **Claude (`claude-haiku-5-5`, API de Anthropic)** sobre los 10 casos etiquetados el 20/11/2026.
El mismo script corre en el pipeline (job `triaje-ia`, secret `ANTHROPIC_API_KEY`) y deja su propia tabla en el
artefacto `triaje-ia/validacion.md`.

| Clasificador | Categoría | DEF |
|---|---:|---:|
| Reglas (línea base) | 9/10 | 10/10 |
| **Agente con Claude** | **10/10** | **10/10** |

- El agente consultó herramientas en los 10 casos (`leer_defectos` en todos; `leer_fragmento_codigo` en 7) antes de responder.
- Corrigió el único error de las reglas: **C09** (timing de animación), que las reglas clasificaban como defecto real y el modelo reconoció como prueba frágil.
- **Lectura honesta del resultado:** 10 casos son pocos y 5 de ellos son defectos que el agente puede leer en `docs/defectos.md`,
  así que el 100 % mide bien «reconoce lo ya documentado» y no prueba generalización a fallas nuevas. Por eso el triaje **sugiere y una persona confirma**.
- Proveedor: con `ANTHROPIC_API_KEY` se usa Claude; sin ella, GitHub Models; sin ninguno, solo reglas (el pipeline nunca se bloquea).
  Se probó GitHub Models primero, pero su servicio respondió `OK` en texto plano a todas las llamadas (incluido su catálogo), tanto desde el equipo local como desde el runner.

## Qué aporta

- Cada falla **nueva** del run llega con una hipótesis: categoría (`defecto_real`, `prueba_fragil`,
  `entorno`), si coincide con un defecto ya reportado (DEF-01…05, y DEF-06…14 en el listado vivo de `docs/defectos.md`), causa probable y siguiente paso.
- Es un **agente**: antes de responder puede leer `docs/defectos.md`, ver qué cambió el último
  commit y leer el código del repo (p. ej. `qolqe/reglas/servicios.py`). La tabla «Herramientas
  usadas» muestra qué consultó en cada caso.
- Frente a las reglas, el modelo puede reconocer trazas con otra redacción y explicar la causa
  mirando el código. Las reglas solo reconocen las palabras que tienen escritas.

## Cómo se valida

- 10 fallas etiquetadas a mano (`tests/triaje/casos_etiquetados.json`): los 5 defectos reales
  (DEF-01…05, con trazas como las que dan pytest y k6) y 5 sintéticas con respuesta conocida
  (2 de entorno, 2 de prueba frágil y 1 defecto nuevo sin DEF).
- Métricas: exactitud de la categoría y del DEF asignado, comparadas con la línea base por reglas.
- Pruebas unitarias sin red (`tests/triaje/test_triaje.py`): lectura de JUnit/Robot, reglas, filtro
  de secretos, herramienta de código que no sale del repo, bucle del agente con un modelo simulado,
  rechazo de DEF inventados y degradación sin token o con 429.

## Límites

- **La línea base sale optimista.** Sus reglas se escribieron a partir de las huellas de
  `docs/defectos.md`, que son las mismas que aparecen en los casos. Por eso saca 9/10 en categoría
  (solo falla C09, un timing de animación) y no sirve como medida de generalización. Un DEF-02 con
  otra redacción, sin «mora» ni «días de atraso», ya no lo reconocería.
- 10 casos son pocos para dar cifras estables, así que el resultado es orientativo.
- C05 (DEF-05) mezcla timeouts con un defecto real. Es el caso más difícil de separar de «entorno».

## Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Alucinación (inventa un DEF o una categoría) | Salida **JSON estricta** y validada. La categoría solo puede ser uno de 3 valores, si no se descarta la respuesta. El DEF se acepta **solo si existe** en `docs/defectos.md` (si no, queda `null`). La confianza se recorta a [0, 1]. |
| Decisiones automáticas equivocadas | **Humano en el bucle**: el triaje solo sugiere. No marca xfail, no abre ni cierra defectos y no cambia el resultado del run. |
| Bloquear el pipeline | `continue-on-error: true` y `exit 0` siempre. Sin token, con error o con límite de uso, se usan las reglas y se avisa. |
| Fuga de información | Solo se envían el nombre de la prueba y su traza (recortada a 3 000 caracteres), quitando lo que parezca token o contraseña. `leer_fragmento_codigo` no sale del repo ni lee `.git` ni `.env`. |
| Bucles largos o costo | Máximo 6 pasos por falla. Ante el primer error del modelo deja de llamarlo en ese run. |
