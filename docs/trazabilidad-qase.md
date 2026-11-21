# Trazabilidad con Qase: historial de ejecuciones múltiples

Las pruebas del proyecto se ejecutan muchas veces: en cada push y en cada pull request corre el
pipeline de GitHub Actions. La matriz de `docs/trazabilidad.md` muestra **una** ejecución; para ver
**todas** usamos una herramienta de gestión de casos de prueba: **Qase**.

## Qué es Qase

Qase (https://qase.io) es una herramienta web de gestión de pruebas (*test management*). Guarda:

- **Repositorio de casos**: cada prueba es un caso con ID (`QOLQE-12`), suite, descripción,
  etiquetas y campos propios (en nuestro proyecto: *Endpoint* e *Historia de usuario*).
- **Test runs**: cada ejecución del pipeline es un run con su fecha, commit y resultados.
- **Historial por caso**: en la ficha de un caso se ve en qué runs pasó, falló o se omitió.

## Por qué Qase

| Herramienta | Costo para el curso | Integración con CI | API | Curva de aprendizaje |
|---|---|---|---|---|
| **Qase** | Plan gratuito (hasta 3 usuarios) | Reportes nativos para pytest y Robot; API REST simple | REST v1 con token, bien documentada | Baja: interfaz moderna, sin instalar nada |
| TestRail | De pago (solo prueba de 14 días) | Por API o la CLI `trcli` | REST completa | Media |
| Xray | De pago, requiere Jira | Importa JUnit / Robot vía Jira | REST + GraphQL | Alta: hay que conocer Jira |
| Zephyr Scale | De pago, requiere Jira | Importa JUnit vía Jira | REST | Alta: depende de Jira |
| Kiwi TCMS | Gratis (código abierto) | Plugins para pytest y Robot | XML-RPC / JSON-RPC | Media: hay que instalarlo y mantener un servidor |

Elegimos Qase porque es **gratis**, **no requiere Jira ni servidor propio**, y su API REST permite
subir resultados desde el pipeline con un script de ~200 líneas sin dependencias nuevas.

## Cómo se conecta

```
pytest (JUnit) ─┐
                ├─> .github/scripts/qase_subir.py ──API REST v1 (header Token)──> Qase · proyecto QOLQE
Robot (XML) ────┘
```

1. En Qase: *Workspace → API tokens* → crear un token.
2. En GitHub: *Settings → Secrets and variables → Actions → New repository secret* con el
   nombre `QASE_API_TOKEN` y el token como valor. El token **nunca** se escribe en el repositorio.
3. El pipeline ejecuta, después de las pruebas:

   ```bash
   python .github/scripts/qase_subir.py \
     --junit reportes/api/junit.xml --robot reportes/web/output.xml \
     --proyecto QOLQE \
     --titulo-run "Pipeline #${GITHUB_RUN_NUMBER} · ${GITHUB_REF_NAME}" \
     --commit "${GITHUB_SHA::7}" \
     --url-run "${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}/actions/runs/${GITHUB_RUN_ID}"
   ```

   con `env: QASE_API_TOKEN: ${{ secrets.QASE_API_TOKEN }}`.

El script:

- Lee los resultados con las mismas funciones de la matriz (`trazabilidad.py`).
- Busca cada prueba por **título** en el repositorio de Qase y crea las que falten. El título es
  estable (`[nivel] nombre de la prueba`), por eso cada ejecución suma historial al **mismo** caso.
- Ubica cada caso en su suite: *API - Funcional* (1), *API - Técnico* (2: contrato/Schemathesis
  y escenarios `@tecnico`), *Web E2E - Núcleo común* (3), *Web E2E - G2 Servicios* (4).
- Crea el run (título, commit, enlace al run de GitHub), sube los resultados con su duración y
  lo cierra. Los estados se mapean así:

  | Resultado en el pipeline | En Qase |
  |---|---|
  | pasa | `passed` |
  | falla (fallo nuevo) | `failed`, con el mensaje de error |
  | omitida | `skipped` |
  | fallo esperado (xfail) | `skipped` con el comentario "Fallo esperado: defecto conocido DEF-0X" |

- Si falta el token o Qase no responde (reintenta ante 429 y errores 5xx), imprime
  `Qase no disponible` y termina con éxito: **la herramienta de gestión nunca rompe el pipeline**.
- `--dry-run` muestra qué casos y resultados enviaría, sin usar la red.

Las pruebas del script están en `tests/qase/test_qase_subir.py` (servidor HTTP falso, sin red).

## Cómo se ve el historial de ejecuciones múltiples

- **Test Runs**: una fila por ejecución del pipeline (`Pipeline #12 · main`, `Pipeline #13 · main`…),
  con el porcentaje de casos que pasan. Comparar runs muestra si una regresión apareció en un commit.
- **Ficha de un caso → pestaña *History* / *Runs***: la línea de tiempo de ese caso en todos los runs.
  Así se ve, por ejemplo, que el caso de DEF-02 se omite como "defecto conocido" en cada ejecución
  hasta que se corrija.
- **Dashboard del run**: el enlace `https://app.qase.io/run/QOLQE/dashboard/<id>` se imprime en el log
  y se agrega al resumen del run de GitHub.

## Pasos para verificar el primer run

1. Crear el secret `QASE_API_TOKEN` (ver arriba) y ejecutar el pipeline (push o *Re-run jobs*).
2. En el log del paso de Qase debe aparecer:
   `Qase: N casos en este run · N creados · 0 reutilizados` y `Qase: run #1 → https://app.qase.io/...`.
   Si aparece `Qase no disponible: ...`, el mensaje dice la causa (token, permisos, campo rechazado).
3. Abrir el enlace: el run debe estar **completado**, con los totales de pasan / fallan / omitidas
   iguales a los del resumen de GitHub.
4. En *Repository*, revisar que los casos estén en las 4 suites y que *Endpoint* e *Historia de
   usuario* tengan valor.
5. Volver a ejecutar el pipeline: ahora el log debe decir `0 creados · N reutilizados`, y en la ficha
   de cualquier caso deben verse **dos** ejecuciones en su historial.
