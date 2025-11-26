import os

# Tokens del bot y de Gemini
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# URL completa de conexión a PostgreSQL (Supabase)
DATABASE_URL = os.getenv("DATABASE_URL")



# # Si estoy en Render → uso /opt/render/project/src/data
# if os.getenv("RENDER"):
#     DB_DIR = "/opt/render/project/src/data"
# else:
#     DB_DIR = "data"   # Carpeta local en computadora

# # Crear carpeta si no existe
# os.makedirs(DB_DIR, exist_ok=True)

# DATABASE_PATH = os.path.join(DB_DIR, "botania.db")
