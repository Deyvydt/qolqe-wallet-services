# Validación del agente de triaje · 2026-11-20

Casos etiquetados: 10 (`tests/triaje/casos_etiquetados.json`). Modelo: `openai/gpt-4.1-mini` (GitHub Models), temperatura 0.

> ⚠️ El modelo no estuvo disponible (no hay GITHUB_TOKEN); solo se evaluó la línea base por reglas.

| Clasificador | Categoría correcta | DEF correcto |
|---|---:|---:|
| Línea base (reglas) | 9/10 (90%) | 10/10 (100%) |

## Caso por caso

| Caso | Esperado | Reglas | IA | Herramientas usadas por el agente | Confianza IA |
|---|---|---|---|---|---:|
| C01 | defecto_real / DEF-01 | defecto_real ✅ / DEF-01 ✅ | no evaluado | — | — |
| C02 | defecto_real / DEF-02 | defecto_real ✅ / DEF-02 ✅ | no evaluado | — | — |
| C03 | defecto_real / DEF-03 | defecto_real ✅ / DEF-03 ✅ | no evaluado | — | — |
| C04 | defecto_real / DEF-04 | defecto_real ✅ / DEF-04 ✅ | no evaluado | — | — |
| C05 | defecto_real / DEF-05 | defecto_real ✅ / DEF-05 ✅ | no evaluado | — | — |
| C06 | entorno / — | entorno ✅ / — ✅ | no evaluado | — | — |
| C07 | entorno / — | entorno ✅ / — ✅ | no evaluado | — | — |
| C08 | prueba_fragil / — | prueba_fragil ✅ / — ✅ | no evaluado | — | — |
| C09 | prueba_fragil / — | defecto_real ❌ / — ✅ | no evaluado | — | — |
| C10 | defecto_real / — | defecto_real ✅ / — ✅ | no evaluado | — | — |

> Las tablas de arriba las genera `python .github/scripts/validar_triaje.py --salida docs/ia/validacion_triaje.md`.
> Lo que sigue es el análisis.

## Estado de la validación con el modelo

La corrida con el modelo **todavía no se hizo**: desde la máquina local la llamada a
`models.github.ai` no llegó al servicio (la red local devolvió `200 OK` en texto plano, sin el JSON
del modelo). El agente lo detectó, avisó «triaje IA no disponible» y usó las reglas, que es justo la
degradación esperada. Las cifras del agente IA se completan corriendo el mismo script en el pipeline
(job `triaje-ia`, con `models: read`) o en una máquina con acceso:

```bash
GITHUB_TOKEN=$(gh auth token) python .github/scripts/validar_triaje.py --salida docs/ia/validacion_triaje.md
```

## Qué aporta

- Cada falla **nueva** del run llega con una hipótesis: categoría (`defecto_real`, `prueba_fragil`,
  `entorno`), si coincide con un defecto ya reportado (DEF-01…05), causa probable y siguiente paso.
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
| Alucinación (inventa un DEF o una categoría) | Salida **JSON estricta** y validada. La categoría solo puede ser uno de 3 valores, si no se descarta la respuesta. El DEF se acepta **solo si existe** en `docs/defectos.md` (si no, queda `null`). La confianza se recorta a [0, 1]. Temperatura 0. |
| Decisiones automáticas equivocadas | **Humano en el bucle**: el triaje solo sugiere. No marca xfail, no abre ni cierra defectos y no cambia el resultado del run. |
| Bloquear el pipeline | `continue-on-error: true` y `exit 0` siempre. Sin token, con error o con límite de uso, se usan las reglas y se avisa. |
| Fuga de información | Solo se envían el nombre de la prueba y su traza (recortada a 3 000 caracteres), quitando lo que parezca token o contraseña. `leer_fragmento_codigo` no sale del repo ni lee `.git` ni `.env`. |
| Bucles largos o costo | Máximo 6 pasos por falla. Ante el primer error del modelo deja de llamarlo en ese run. |
