from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from bson import ObjectId
from app.database import db

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
async def agregar_alumno(request: Request, name: str = Form(...), grades: str = Form(...), salon: str = Form(...)):
    print(f"Recibido nombre: {name}")
    print(f"Recibidas notas: {grades}")
    print(f"Recibido salón: {salon}")
    
    grades_list = []
    
    # Intentar separar materias y notas de manera segura
    grades_split = grades.split(",")
    
    # Verificamos que el número de elementos sea par (materia, nota, materia, nota...)
    if len(grades_split) % 2 != 0:
        return templates.TemplateResponse("menu.html", {"request": request, "message": "Error: Asegúrese de que haya el mismo número de materias y notas."})
    
    # Procesar las materias y notas
    for i in range(0, len(grades_split), 2):
        subject = grades_split[i].strip()  # Materia
        try:
            score = float(grades_split[i+1].strip())  # Nota
        except ValueError:
            return templates.TemplateResponse("menu.html", {"request": request, "message": f"Error: La nota de {subject} no es válida. Debe ser un número."})
        
        grades_list.append({"subject": subject, "score": score})

    print(f"Datos procesados para el alumno: {name}, Notas: {grades_list}, Salón: {salon}")
    
    # Verificar si las notas están correctas
    if not grades_list:
        return templates.TemplateResponse("menu.html", {"request": request, "message": "Error: No se recibieron notas válidas."})
    
    # Crear el alumno en la base de datos
    alumno = db.students.find_one({"name": name})
    
    if alumno:
        # Si ya existe el alumno, actualizamos las notas
        alumno['grades'] = grades_list
        resultado = db.students.update_one({"name": name}, {"$set": {"grades": alumno['grades']}})
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
async def listar_alumnos(request: Request, salon: str = None):
    # Obtener todos los salones únicos de la base de datos
    all_salons = db.students.distinct("salon")
    
    # Si se especifica un salón, filtramos por el campo "salon"
    if salon:
        alumnos = db.students.find({"salon": salon})
    else:
        alumnos = db.students.find()
    
    # Convertir el cursor a una lista
    alumnos = list(alumnos)
    
    return templates.TemplateResponse("listar.html", {"request": request, "alumnos": alumnos, "salons": all_salons, "salon": salon})

# Actualizar alumno (Formulario)
@app.get("/actualizar", response_class=HTMLResponse)
async def actualizar_alumno(request: Request):
    return templates.TemplateResponse("actualizar.html", {"request": request})

@app.post("/actualizar")
async def actualizar_datos(request: Request, new_name: str = Form(...), grades: str = Form(...), salon: str = Form(...)):
    print(f"Nuevo nombre: {new_name}")
    print(f"Recibidas notas: {grades}")
    print(f"Nuevo salón: {salon}")
    
    grades_list = []
    
    # Intentar separar materias y notas de manera segura
    grades_split = grades.split(",")
    
    # Verificamos que el número de elementos sea par (materia, nota, materia, nota...)
    if len(grades_split) % 2 != 0:
        return templates.TemplateResponse("menu.html", {"request": request, "message": "Error: Asegúrese de que haya el mismo número de materias y notas."})
    
    # Procesar las materias y notas
    for i in range(0, len(grades_split), 2):
        subject = grades_split[i].strip()  # Materia
        try:
            score = float(grades_split[i+1].strip())  # Nota
        except ValueError:
            return templates.TemplateResponse("menu.html", {"request": request, "message": f"Error: La nota de {subject} no es válida."})
        
        grades_list.append({"subject": subject, "score": score})

    print(f"Datos procesados para el alumno: {new_name}, Notas: {grades_list}, Salón: {salon}")
    
    # Verificar si las notas están correctas
    if not grades_list:
        return templates.TemplateResponse("menu.html", {"request": request, "message": "Error: No se recibieron notas válidas."})
    
    # Actualizar el alumno por nombre
    resultado = db.students.update_one(
        {"name": new_name},  # Buscamos por nombre
        {"$set": {"grades": grades_list, "salon": salon}}  # Actualizamos las notas (cursos) y el salón
    )

    if resultado.modified_count:
        message = f"Alumno {new_name} actualizado correctamente."
    else:
        message = "No se encontró el alumno o no se modificó nada."

    return templates.TemplateResponse("menu.html", {"request": request, "message": message})

# Eliminar alumno (Formulario)
@app.get("/eliminar", response_class=HTMLResponse)
async def eliminar_alumno(request: Request):
    return templates.TemplateResponse("eliminar.html", {"request": request})

@app.post("/eliminar")
async def eliminar_datos(request: Request, nombre_alumno: str = Form(...)):
    # Eliminar el alumno por nombre
    resultado = db.students.delete_one({"name": nombre_alumno})

    if resultado.deleted_count:
        message = f"Alumno con nombre {nombre_alumno} eliminado."
    else:
        message = "No se encontró el alumno."

    return templates.TemplateResponse("menu.html", {"request": request, "message": message})
