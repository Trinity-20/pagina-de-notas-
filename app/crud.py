from app.database import db
from app.models import StudentModel
from bson import ObjectId

# Obtener todos los estudiantes
def get_students():
    students = list(db.students.find())
    for student in students:
        student["_id"] = str(student["_id"])  # Convertir ObjectId a string
    return students

# Crear un estudiante
def create_student(student: StudentModel):
    student_dict = student.dict()
    result = db.students.insert_one(student_dict)
    return str(result.inserted_id)

# Actualizar un estudiante
def update_student(student_id: str, student: StudentModel):
    result = db.students.update_one(
        {"_id": ObjectId(student_id)},
        {"$set": student.dict()}
    )
    return result.modified_count

# Eliminar un estudiante
def delete_student(student_id: str):
    result = db.students.delete_one({"_id": ObjectId(student_id)})
    return result.deleted_count
