from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse
from openpyxl.styles import Border, Side
from openpyxl.utils import get_column_letter
from app.database import db
from typing import List
import io
import pandas as pd
import unicodedata

app = FastAPI()

# Configuración de templates
templates = Jinja2Templates(directory="app/templates")

# Mostrar el menú principal
@app.get("/", response_class=HTMLResponse)
async def mostrar_menu(request: Request):
    return templates.TemplateResponse("menu.html", {"request": request})

# Crear un alumno (Formulario)
@app.get("/crear", response_class=HTMLResponse)
async def crear_alumno(request: Request):
    return templates.TemplateResponse("crear.html", {"request": request})

@app.post("/crear")
async def agregar_alumno(
    request: Request,
    name: str = Form(...),
    subjects: List[str] = Form(...),
    scores: List[str] = Form(...),  # Recibimos como str para validar y convertir
    salon: str = Form(...)
):
    print(f"Recibido nombre: {name}")
    print(f"Materias recibidas: {subjects}")
    print(f"Notas recibidas: {scores}")
    print(f"Recibido salón: {salon}")

    if len(subjects) != len(scores):
        return templates.TemplateResponse("menu.html", {
            "request": request,
            "message": "Error: El número de materias y notas no coincide."
        })

    grades_list = []
    for subject, score_str in zip(subjects, scores):
        subject = subject.strip()
        if not subject:
            return templates.TemplateResponse("menu.html", {
                "request": request,
                "message": "Error: Hay materias vacías."
            })
        try:
            score = float(score_str)
            if score < 0 or score > 20:
                return templates.TemplateResponse("menu.html", {
                    "request": request,
                    "message": f"Error: La nota de {subject} debe estar entre 0 y 20."
                })
        except ValueError:
            return templates.TemplateResponse("menu.html", {
                "request": request,
                "message": f"Error: La nota de {subject} no es válida."
            })
        grades_list.append({"subject": subject, "score": score})

    if not grades_list:
        return templates.TemplateResponse("menu.html", {
            "request": request,
            "message": "Error: No se recibieron notas válidas."
        })

    alumno = db.students.find_one({"name": name})

    if alumno:
        alumno['grades'] = grades_list
        alumno['salon'] = salon
        resultado = db.students.update_one({"name": name}, {"$set": {"grades": grades_list, "salon": salon}})
        message = f"Alumno {name} actualizado con las notas."
    else:
        nuevo_alumno = {
            "name": name,
            "salon": salon,
            "grades": grades_list
        }
        resultado = db.students.insert_one(nuevo_alumno)
        message = f"Alumno {name} agregado con ID {resultado.inserted_id}."

    return templates.TemplateResponse("menu.html", {"request": request, "message": message})

# Listar todos los alumnos
# Listar alumnos por salón

@app.get("/listar", response_class=HTMLResponse)
async def listar_alumnos(
    request: Request,
    salon: str = None,
    page: int = 1,
    limit: int = 5
):
    # Salones únicos para el filtro
    all_salons = db.students.distinct("salon")

    # Filtro dinámico
    filtro = {"salon": salon} if salon else {}

    # Cálculo para paginación
    total_alumnos = db.students.count_documents(filtro)
    total_pages = (total_alumnos + limit - 1) // limit
    skip = (page - 1) * limit

    # Obtener los alumnos paginados
    alumnos_cursor = db.students.find(filtro).skip(skip).limit(limit)
    alumnos = list(alumnos_cursor)

    return templates.TemplateResponse("listar.html", {
        "request": request,
        "alumnos": alumnos,
        "salons": all_salons,
        "salon": salon,
        "page": page,
        "total_pages": total_pages,
        "limit": limit
    })


# Actualizar alumno (Formulario)
@app.get("/actualizar", response_class=HTMLResponse)
async def actualizar_alumno(request: Request):
    return templates.TemplateResponse("actualizar.html", {"request": request})

@app.post("/actualizar", response_class=HTMLResponse)
async def actualizar_datos(
    request: Request,
    new_name: str = Form(...),
    subjects: List[str] = Form(...),
    scores: List[float] = Form(...),
    salon: str = Form(...)
):
    print(f"Nuevo nombre: {new_name}")
    print(f"Materias recibidas: {subjects}")
    print(f"Notas recibidas: {scores}")
    print(f"Nuevo salón: {salon}")

    if len(subjects) != len(scores):
        return templates.TemplateResponse("menu.html", {
            "request": request,
            "message": "Error: El número de materias y notas no coincide."
        })

    grades_list = []

    for subject, score in zip(subjects, scores):
        subject = subject.strip()
        try:
            score = float(score)
            grades_list.append({"subject": subject, "score": score})
        except ValueError:
            return templates.TemplateResponse("menu.html", {
                "request": request,
                "message": f"Error: La nota para {subject} no es válida."
            })

    if not grades_list:
        return templates.TemplateResponse("menu.html", {
            "request": request,
            "message": "Error: No se recibieron datos válidos para cursos y notas."
        })

    # Actualizar el alumno nombre
    resultado = db.students.update_one(
        {"name": new_name},
        {"$set": {"grades": grades_list, "salon": salon}}
    )

    if resultado.modified_count:
        message = f"Alumno {new_name} actualizado correctamente."
    else:
        message = "No se encontró el alumno o no se modificó nada."

    return templates.TemplateResponse("menu.html", {"request": request, "message": message})

# Eliminar alumno (Formulario)
@app.get("/eliminar", response_class=HTMLResponse)
async def eliminar_alumno(request: Request):
    # Obtener todos los alumnos nombre
    alumnos = list(db.students.find({}, {"name": 1, "_id": 0}))
    return templates.TemplateResponse("eliminar.html", {
        "request": request,
        "alumnos": alumnos
    })

@app.post("/eliminar")
async def eliminar_datos(request: Request, nombre_alumno: str = Form(...)):
    # Eliminar alum
    resultado = db.students.delete_one({"name": nombre_alumno})

    if resultado.deleted_count:
        message = f"Alumno con nombre {nombre_alumno} eliminado."
    else:
        message = "No se encontró el alumno."

    return templates.TemplateResponse("menu.html", {"request": request, "message": message})

@app.get("/editar", response_class=HTMLResponse)
async def editar_alumno(request: Request, name: str):
    alumno = db.students.find_one({"name": name})
    if not alumno:
        return templates.TemplateResponse("menu.html", {"request": request, "message": "Alumno no encontrado."})
    
    grades_str = ", ".join(f"{g['subject']}, {g['score']}" for g in alumno["grades"])

    return templates.TemplateResponse("actualizar.html", {
        "request": request,
        "name": alumno["name"],
        "grades": grades_str,
        "salon": alumno["salon"],
        "modo_edicion": True
    })

@app.get("/exportar_excel", response_class=HTMLResponse)
async def mostrar_formulario_exportacion(request: Request):
    salones = db.students.distinct("salon")  # Sin await
    return templates.TemplateResponse("exportar_excel.html", {
        "request": request,
        "salones": salones
    })

def normalizar_texto(texto: str) -> str:
    texto = texto.strip().lower()
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')  # elimina tildes
    return texto 

@app.get("/exportar_excel_salon")
async def exportar_excel_salon(salon: str):
    if not salon:
        return {"error": "Debes especificar un salón con el parámetro ?salon=SALON"}

    alumnos = list(db.students.find({"salon": salon}))
    if not alumnos:
        return {"error": f"No se encontraron alumnos en el salón {salon}"}

    # Paso 1: Normalizar y mapear cursos
    cursos_unicos = {}
    for alumno in alumnos:
        for grade in alumno.get("grades", []):
            key = normalizar_texto(grade["subject"])
            if key not in cursos_unicos:
                cursos_unicos[key] = grade["subject"].strip().title()

    # Paso 2: Construir filas con nombres amigables
    data = []
    for alumno in alumnos:
        fila = {"Apellidos y Nombres": alumno.get("name", "").strip().title()}
        for key in cursos_unicos:
            fila[cursos_unicos[key]] = ""
        for grade in alumno.get("grades", []):
            curso_key = normalizar_texto(grade["subject"])
            nombre_curso = cursos_unicos[curso_key]
            fila[nombre_curso] = grade["score"]
        data.append(fila)

    # Paso 3: Exportar a Excel
    columnas = ["Apellidos y Nombres"] + list(cursos_unicos.values())
    df = pd.DataFrame(data, columns=columnas)

    stream = io.BytesIO()
    with pd.ExcelWriter(stream, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Alumnas")
        ws = writer.book["Alumnas"]

        border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
        for row in ws.iter_rows():
            for cell in row:
                cell.border = border

        for col in ws.columns:
            max_length = max(len(str(cell.value)) if cell.value else 0 for cell in col)
            ws.column_dimensions[col[0].column_letter].width = max_length + 2

    stream.seek(0)
    filename = f"Alumnas_{salon}.xlsx"
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename=\"{filename}\"'}
    )
