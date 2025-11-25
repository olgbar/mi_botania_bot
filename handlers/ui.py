from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📸 Identificar planta", callback_data="identificar"))
    kb.add(InlineKeyboardButton("🌿 Mis plantas", callback_data="mis_plantas"))
    kb.add(InlineKeyboardButton("⏰ Crear recordatorio", callback_data="crear_recordatorio"))
    kb.add(InlineKeyboardButton("🗑 Eliminar planta", callback_data="eliminar_planta"))
    kb.add(InlineKeyboardButton("🗑 Eliminar recordatorio", callback_data="eliminar_recordatorio"))
    kb.add(InlineKeyboardButton("❓ Ayuda", callback_data="ayuda"))
    return kb
