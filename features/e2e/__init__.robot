*** Settings ***
Documentation     BDD E2E: escenarios Gherkin (.feature) ejecutados por Robot Framework
...               con robotframework-gherkin-parser + Browser Library.
...               Cada frase Dado/Cuando/Entonces es una keyword de pasos/*.resource,
...               que llama a los Page Objects de tests/e2e/pages/.
...               Este archivo da a TODOS los escenarios el mismo fixture que los .robot:
...               reiniciar datos + abrir navegador antes, captura (EVIDENCIA) + cerrar después.
Resource          ../../tests/e2e/resources/Comun.resource
Test Setup        Abrir Navegador Con Datos Limpios
Test Teardown     Cerrar Navegador
