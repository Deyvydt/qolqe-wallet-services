"""Llena la plantilla Template_Informe_Rendimiento.docx con el diseño y los resultados de tests/performance/resultados.

Uso: python docs/rendimiento/generar_informe.py <ruta plantilla.docx>
Salida: docs/rendimiento/Informe_Rendimiento_G2.docx
"""
import copy
import json
import sys
from pathlib import Path

import docx
from docx.shared import Cm, Pt

RAIZ = Path(__file__).resolve().parents[2]
RES = RAIZ / "tests" / "performance" / "resultados"
sys.path.insert(0, str(Path(__file__).parent))
from contenido import SECCIONES, TABLA_HERRAMIENTAS, TABLA_TIPOS, TABLA_MODELO, TABLA_CRITERIOS, PRUEBAS, ANALISIS  # noqa: E402


def despues(ancla, texto="", estilo=None, negrita_hasta=None):
    """Inserta un párrafo después de `ancla` y lo devuelve (para encadenar)."""
    nuevo = copy.deepcopy(ancla._p)
    for hijo in list(nuevo):
        if hijo.tag.endswith("}r") or hijo.tag.endswith("}hyperlink"):
            nuevo.remove(hijo)
    ancla._p.addnext(nuevo)
    p = docx.text.paragraph.Paragraph(nuevo, ancla._parent)
    p.style = estilo or "Normal"
    if negrita_hasta and texto.startswith(negrita_hasta):
        p.add_run(negrita_hasta).bold = True
        texto = texto[len(negrita_hasta):]
    p.add_run(texto)
    return p


def bloque(ancla, lineas):
    """Escribe varias líneas; las que empiezan con '- ' van como viñetas, '**x**' en negrita al inicio."""
    for linea in lineas:
        if linea == "@TABLA_HERRAMIENTAS":
            ancla = tabla_despues(ancla, TABLA_HERRAMIENTAS)
        elif linea.startswith("- "):
            ancla = despues(ancla, linea[2:], "List Bullet" if "List Bullet" in estilos else "List Paragraph")
        elif linea.startswith("**") and "**" in linea[2:]:
            fin = linea.index("**", 2)
            ancla = despues(ancla, linea[2:fin] + linea[fin + 2:], negrita_hasta=linea[2:fin])
        else:
            ancla = despues(ancla, linea)
    return ancla


def tabla_despues(ancla, filas, anchos=None):
    t = documento.add_table(rows=len(filas), cols=len(filas[0]))
    t.style = ESTILO_TABLA
    for i, fila in enumerate(filas):
        for j, valor in enumerate(fila):
            celda = t.cell(i, j)
            celda.text = str(valor)
            for r in celda.paragraphs[0].runs:
                r.font.size = Pt(9)
                r.bold = i == 0
    if anchos:
        for fila in t.rows:
            for celda, ancho in zip(fila.cells, anchos):
                celda.width = Cm(ancho)
    ancla._p.addnext(t._tbl)
    return despues_de_tabla(t)


def despues_de_tabla(t):
    p = documento.add_paragraph()
    t._tbl.addnext(p._p)
    return p


def imagen_despues(ancla, ruta, ancho_cm=16):
    p = despues(ancla)
    p.add_run().add_picture(str(ruta), width=Cm(ancho_cm))
    return p


def llenar_tabla(t, filas):
    for i, fila in enumerate(filas, start=1):
        while len(t.rows) <= i:
            t.add_row()
        for j, valor in enumerate(fila):
            t.cell(i, j).text = str(valor)
            for r in t.cell(i, j).paragraphs[0].runs:
                r.font.size = Pt(9)


plantilla = sys.argv[1]
documento = docx.Document(plantilla)
estilos = {s.name for s in documento.styles}
P = documento.paragraphs  # índices fijos de la plantilla (se toman antes de insertar nada)
T = list(documento.tables)  # 0 = tipos, 1 = modelo, 2 = criterios (antes de insertar la tabla de herramientas)
ESTILO_TABLA = T[0].style

P[2].text = "Grupo: G2 (Pago de servicios)   Fecha: 13/11/2026"
P[3].text = "Aplicación bajo prueba: Qolqe Wallet API 1.0.0 (FastAPI + SQLite)   Herramienta: Grafana k6 v2.1.0"
P[12].text = "☒  API"
anclas = {7: "contexto", 9: "flujos", 15: "capa", 19: "herramienta", 27: "origen", 31: "supuestos",
          34: "entorno", 35: "medicion", 36: "limitaciones", 37: "diferencias"}
for i, clave in anclas.items():
    bloque(P[i], SECCIONES[clave])

# Tablas de la plantilla: 0 = tipos, 1 = modelo, 2 = criterios
llenar_tabla(T[0], TABLA_TIPOS)
# La plantilla trae columnas para 2 tipos y ejecutamos 4: se reemplaza por una tabla del mismo estilo.
nueva = documento.add_table(rows=len(TABLA_MODELO), cols=len(TABLA_MODELO[0]))
nueva.style = ESTILO_TABLA
for i, fila in enumerate(TABLA_MODELO):
    for j, valor in enumerate(fila):
        nueva.cell(i, j).text = str(valor)
        for r in nueva.cell(i, j).paragraphs[0].runs:
            r.font.size = Pt(9)
            r.bold = i == 0 or j == 0
T[1]._tbl.addnext(nueva._tbl)
T[1]._tbl.getparent().remove(T[1]._tbl)
llenar_tabla(T[2], TABLA_CRITERIOS)

# 7. Resultados: la plantilla trae "Prueba 1" y "Prueba 2"; se usan para las dos primeras y se agregan las demás.
ultimo = P[49]
for k, prueba in enumerate(PRUEBAS):
    if k < 2:
        cab, resumen, rec, graf = (P[40], P[41], P[42], P[43]) if k == 0 else (P[45], P[46], P[47], P[48])
        cab.text = f"Prueba {k + 1}: {prueba['titulo']}"
    else:
        cab = despues(ultimo, f"Prueba {k + 1}: {prueba['titulo']}")
        resumen = despues(cab)
        rec = despues(resumen, "Recursos (CPU y memoria de Qolqe y de la herramienta):", "List Paragraph")
        graf = despues(rec, "Gráficos (tiempo de respuesta, errores, throughput y recursos a lo largo de la prueba):",
                       "List Paragraph")
    a = bloque(resumen, prueba["resumen"])
    tabla_despues(a, prueba["tabla"])
    bloque(rec, prueba["recursos"])
    ultimo = imagen_despues(graf, RES / prueba["carpeta"] / "graficos.png")
    if prueba.get("extra"):
        ultimo = bloque(ultimo, prueba["extra"])

for i, clave in zip(range(52, 57), ["cumplimiento", "cuello", "capacidad", "riesgos", "acciones"]):
    bloque(P[i], ANALISIS[clave])

salida = Path(__file__).parent / "Informe_Rendimiento_G2.docx"
documento.save(salida)
print(salida)
