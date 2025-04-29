from app.database import db

# Lista de 3 alumnos nuevos
alumnos = [
    {
        "name": "Carlos Ruiz",
        "grades": [
            {"subject": "Matemáticas", "score": 18.0},
            {"subject": "Historia", "score": 16.5}
        ]
    },
    {
        "name": "Lucía Fernández",
        "grades": [
            {"subject": "Ciencias", "score": 19.2},
            {"subject": "Arte", "score": 17.8}
        ]
    },
    {
        "name": "Miguel Torres",
        "grades": [
            {"subject": "Inglés", "score": 14.5},
            {"subject": "Matemáticas", "score": 15.0}
        ]
    }
]

# Insertar todos los alumnos de una vez
resultado = db.students.insert_many(alumnos)

# Mostrar los IDs insertados
print("✅ Alumnos agregados con IDs:")
for id in resultado.inserted_ids:
    print(f"- {id}")
