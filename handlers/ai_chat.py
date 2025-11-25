from bot.bot_instance import bot, repo, reminders
from handlers.start import main_keyboard
from utils.ai_functions import process_user_message
from utils.text import html_a_markdown
from handlers.ui import main_keyboard

@bot.message_handler(commands=['test'])
def test_handler(message):
    try:
        parts = message.text.split()
        minutes = int(parts[1]) if len(parts) > 1 else 1

        reminders.schedule_test_reminder(message.chat.id, minutes)

        bot.send_message(message.chat.id, f"⏰ Test programado cada {minutes} minutos.")
    except Exception as e:
        bot.send_message(message.chat.id, "Error en test.")


@bot.message_handler(commands=['delete_test', 'test_stop'])
def delete_test_handler(message):
    try:
        success = reminders.remove_test_reminder(message.chat.id)
        
        if success:
            bot.send_message(message.chat.id, "🛑 Recordatorio de muestra detenido correctamente.")
        else:
            bot.send_message(message.chat.id, "⚠️ No había ningún test activo.")
    
    except Exception as e:
        bot.send_message(message.chat.id, f"Error al detener test: {e}")


@bot.message_handler(func=lambda m: not m.text.startswith("/"))
def chat_libre(msg):
    try:
        respuesta_html = process_user_message(
            msg.text,
            msg.from_user.id,
            repo,
            reminders
        )
    except Exception as e:
        print(f"❌ ERROR CRÍTICO en chat_libre: {e}")
        print(f"❌ Tipo de error: {type(e).__name__}")
        import traceback
        traceback.print_exc()  # Mostrará la línea exacta del error
        
        respuesta_html = "<b>Ups, ocurrió un error procesando tu consulta.</b>"
    texto_md = html_a_markdown(respuesta_html)
    

    bot.reply_to(
        msg,
        texto_md,
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )

