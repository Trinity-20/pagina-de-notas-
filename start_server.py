import uvicorn
import sys
import os

# Asegurarse de que la carpeta "app" esté en sys.path para que pueda encontrar main
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000)
