# bot/bot_instance.py

import dotenv
dotenv.load_dotenv()

import telebot

from config import TELEGRAM_TOKEN, DATABASE_PATH
from db import PlantRepository
from services.reminders import ReminderService

# Crear instancia de bot
bot = telebot.TeleBot(TELEGRAM_TOKEN, parse_mode=None, threaded=True)

# Base de datos
repo = PlantRepository()

# Recordatorios
reminders = ReminderService(bot, repo)
reminders.start()  # muy importante

print("USANDO BASE DE DATOS EN:", DATABASE_PATH)

# Exportar instancias
__all__ = ["bot", "repo", "reminders"]
