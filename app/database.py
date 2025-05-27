from pymongo import MongoClient

try:
    # Conexión MongoDB 
    client = MongoClient("mongodb://localhost:27017/")

    # Selección de la base de datos
    db = client["schoolgrades"]


    print("✅ Conexión exitosa a MongoDB.")
    
except Exception as e:
    print(f"❌ Error al conectar a MongoDB: {e}")
