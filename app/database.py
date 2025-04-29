from pymongo import MongoClient

try:
    # Conexión a MongoDB local
    client = MongoClient("mongodb://localhost:27017/")

    # Selección de la base de datos
    db = client["schoolgrades"]

    # Si la colección 'students' no existe, MongoDB la crea automáticamente
    print("✅ Conexión exitosa a MongoDB.")
    
except Exception as e:
    print(f"❌ Error al conectar a MongoDB: {e}")
