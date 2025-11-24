import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Si estoy en Render → uso /opt/render/project/src/data
if os.getenv("RENDER"):
    DB_DIR = "/opt/render/project/src/data"
else:
    DB_DIR = "data"   # Carpeta local en computadora

# Crear carpeta si no existe
os.makedirs(DB_DIR, exist_ok=True)

DATABASE_PATH = os.path.join(DB_DIR, "botania.db")
