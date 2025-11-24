import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

DATABASE_PATH = os.getenv("DATABASE_PATH", "botania.db")
