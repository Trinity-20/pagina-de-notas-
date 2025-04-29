from app.database import db
from bson import ObjectId

def crear_alumnos():
    cantidad = int(input("¿Cuántos alumnos deseas agregar?: "))
    alumnos = []
    for _ in range(cantidad):
        nombre = input("Nombre del alumno: ").strip()
        notas = []
        agregar_materias = True
        while agregar_materias:
            materia = input("Materia: ").strip()
            nota = float(input(f"Nota de {materia}: "))
            notas.append({"subject": materia, "score": nota})
            otra = input("¿Agregar otra materia? (s/n): ").strip().lower()
            if otra != "s":
                agregar_materias = False
        alumnos.append({"name": nombre, "grades": notas})
    resultado = db.students.insert_many(alumnos)
    print(f"✅ {len(resultado.inserted_ids)} alumno(s) agregado(s) correctamente.")

def listar_alumnos():
    alumnos = db.students.find()
    print("\n📚 Lista de alumnos:\n")
    for alumno in alumnos:
        print(f"ID: {alumno['_id']}")
        print(f"Nombre: {alumno['name']}")
        for grade in alumno.get("grades", []):
            print(f"  - {grade['subject']}: {grade['score']}")
        print("-" * 20)

def actualizar_alumno():
    id_alumno = input("Ingrese el ID del alumno a actualizar: ").strip()
    nuevo_nombre = input("Nuevo nombre: ").strip()
    resultado = db.students.update_one(
        {"_id": ObjectId(id_alumno)},
        {"$set": {"name": nuevo_nombre}}
    )
    if resultado.modified_count:
        print("✅ Alumno actualizado correctamente.")
    else:
        print("⚠️ No se encontró el alumno o no se modificó nada.")

def eliminar_alumno():
    id_alumno = input("Ingrese el ID del alumno a eliminar: ").strip()
    resultado = db.students.delete_one({"_id": ObjectId(id_alumno)})
    if resultado.deleted_count:
        print("✅ Alumno eliminado correctamente.")
    else:
        print("⚠️ No se encontró el alumno.")

def menu():
    while True:
        print("\n📚 Menú de Gestión de Alumnos")
        print("1. Agregar alumnos")
        print("2. Listar alumnos")
        print("3. Actualizar alumno")
        print("4. Eliminar alumno")
        print("5. Salir")

        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            crear_alumnos()
        elif opcion == "2":
            listar_alumnos()
        elif opcion == "3":
            actualizar_alumno()
        elif opcion == "4":
            eliminar_alumno()
        elif opcion == "5":
            print("👋 Saliendo del programa...")
            break
        else:
            print("⚠️ Opción inválida. Intente de nuevo.")

if __name__ == "__main__":
    menu()
