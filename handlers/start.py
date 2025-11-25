from bot.bot_instance import bot
from handlers.ui import main_keyboard
from handlers.plants import ver_plantas, pedir_planta_a_eliminar
from handlers.reminders_manager import pedir_planta_recordatorio, pedir_recordatorio_a_eliminar

@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(
        msg.chat.id,
        "🌱 ¡Hola! Soy Botania, tu asistente personal de plantas.\n¿Qué necesitás?",
        reply_markup=main_keyboard()
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_menu(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id

    if call.data == "identificar":
        bot.send_message(chat_id, "Enviame la foto de la planta.")

    elif call.data == "mis_plantas":
        ver_plantas(user_id, chat_id)

    elif call.data == "crear_recordatorio":
        pedir_planta_recordatorio(user_id, chat_id)

    elif call.data == "eliminar_planta":
        pedir_planta_a_eliminar(user_id, chat_id)

    elif call.data == "eliminar_recordatorio":
        pedir_recordatorio_a_eliminar(user_id, chat_id)

    elif call.data == "ayuda":
        ayuda(chat_id)


def ayuda(chat_id):
    bot.send_message(
        chat_id,
        "📘 *Ayuda*\n\n"
        "• 📸 Identificar planta → Enviás una foto.\n"
        "• 🌿 Mis plantas → Lista tus plantas.\n"
        "• ⏰ Crear recordatorio → Te aviso cuándo regar.\n"
        "• 🗑 Eliminar planta → Borra plantas.\n"
        "• 🗑 Eliminar recordatorio → Borra recordatorios.\n",
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )
