"""QUÉ ES: el archivo que pytest encuentra y ejecuta (empieza con test_).

PARA QUÉ: con scenarios() convierte CADA escenario de los .feature de features/api/ en una
prueba de pytest. Es corto porque la lógica está en tests/api/conftest.py (los pasos)
y los casos están en features/api/ (el Gherkin, un archivo por HU o grupo de endpoints).
"""
from pytest_bdd import scenarios

scenarios("api")
