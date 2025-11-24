# main.py
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import TELEGRAM_TOKEN
from utils.ai import chat_with_ai, identify_plant   # tu lógica NO se toca
from db import PlantRepository
from services.reminders import ReminderService


bot = telebot.TeleBot(TELEGRAM_TOKEN)
repo = PlantRepository()
reminders = ReminderService(bot, repo)
reminders.start()

# ---------------------------------------------------
# MENÚ PRINCIPAL INLINE (Siempre visible)
# ---------------------------------------------------
def main_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📸 Identificar planta", callback_data="identificar"))
    kb.add(InlineKeyboardButton("🌿 Mis plantas", callback_data="mis_plantas"))
    kb.add(InlineKeyboardButton("⏰ Crear recordatorio", callback_data="crear_recordatorio"))
    kb.add(InlineKeyboardButton("🌑 Eliminar planta", callback_data="eliminar_planta"))
    kb.add(InlineKeyboardButton("🗑 Eliminar recordatorio", callback_data="eliminar_recordatorio"))
    kb.add(InlineKeyboardButton("❓ Ayuda", callback_data="ayuda"))
    return kb

# ---------------------------------------------------
#  START
# ---------------------------------------------------
@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(
        msg.chat.id,
        "🌱 ¡Hola! Soy Botania.",
        reply_markup=main_keyboard()
    )

# ---------------------------------------------------
#  CALLBACK DEL MENÚ PRINCIPAL INLINE
# ---------------------------------------------------
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


# ---------------------------------------------------
#  MIS PLANTAS
# ---------------------------------------------------
def ver_plantas(user_id, chat_id):
    plants = repo.get_plants(user_id)

    if not plants:
        return bot.send_message(chat_id, "No tenés plantas registradas.", reply_markup=main_keyboard())

    text = "🌿 *Tus plantas:*\n\n" + "\n".join(f"• {p['name']}" for p in plants)

    bot.send_message(
        chat_id,
        text,
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )

def pedir_planta_a_eliminar(user_id, chat_id):
    plants = repo.get_plants(user_id)

    if not plants:
        return bot.send_message(chat_id, "No tenés plantas registradas.", reply_markup=main_keyboard())

    texto = "🌑 *Plantas registradas*\nElegí cuál querés eliminar:\n\n"
    texto += "\n".join(f"• {p['name']}" for p in plants)

    bot.send_message(chat_id, texto, parse_mode="Markdown")
    msg = bot.send_message(chat_id, "Escribí el *nombre exacto* de la planta a eliminar.")
    bot.register_next_step_handler(msg, step_eliminar_planta)


def step_eliminar_planta(msg):
    planta = msg.text.strip().lower()
    user = msg.from_user.id

    data = repo.get_plant(user, planta)
    if not data:
        return bot.send_message(msg.chat.id, "No encontré esa planta.", reply_markup=main_keyboard())

    repo.remove_plant(user, planta)

    bot.send_message(
        msg.chat.id,
        f"🌑 Listo, eliminé *{planta}* de tus plantas.",
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )

# ---------------------------------------------------
#  CREAR RECORDATORIO
# ---------------------------------------------------
def pedir_planta_recordatorio(user_id, chat_id):
    msg = bot.send_message(chat_id, "Decime el nombre de la planta para recordar.")
    bot.register_next_step_handler(msg, step_recordatorio_1)


def step_recordatorio_1(msg):
    planta = msg.text.strip().lower()
    data = repo.get_plant(msg.from_user.id, planta)

    if not data:
        return bot.send_message(msg.chat.id, "No encontré esa planta.", reply_markup=main_keyboard())

    bot.send_message(msg.chat.id, "¿Cada cuántos días querés que te recuerde?")
    bot.register_next_step_handler(msg, lambda m: step_recordatorio_2(m, planta))


def step_recordatorio_2(msg, planta):
    try:
        days = int(msg.text)
    except:
        return bot.send_message(msg.chat.id, "Número inválido.", reply_markup=main_keyboard())

    user = msg.from_user.id
    reminders.schedule_plant(user, planta, days)

    bot.send_message(
        msg.chat.id,
        f"⏰ Listo, te recuerdo cada {days} días.",
        reply_markup=main_keyboard()
    )

# ---------------------------------------------------
#  ELIMINAR RECORDATORIO
# ---------------------------------------------------
def pedir_recordatorio_a_eliminar(user_id, chat_id):
    reminders_list = repo.get_reminders(user_id)

    if not reminders_list:
        return bot.send_message(chat_id, "No tenés recordatorios creados.", reply_markup=main_keyboard())

    texto = "🗑 *Recordatorios disponibles*\nElegí cuál querés eliminar:\n\n"
    texto += "\n".join(f"• {r['plant_name']}" for r in reminders_list)

    bot.send_message(chat_id, texto, parse_mode="Markdown")
    msg = bot.send_message(chat_id, "Escribí el *nombre exacto* de la planta.")
    bot.register_next_step_handler(msg, step_eliminar_recordatorio)


def step_eliminar_recordatorio(msg):
    planta = msg.text.strip().lower()

    reminders_list = repo.get_reminders(msg.from_user.id)
    recordatorios = [r["plant_name"].lower() for r in reminders_list]

    if planta not in recordatorios:
        return bot.send_message(msg.chat.id, "No encontré un recordatorio con ese nombre.", reply_markup=main_keyboard())

    ok = reminders.remove_plant_reminder(msg.from_user.id, planta)

    if ok:
        bot.send_message(
            msg.chat.id,
            f"🗑 Listo, eliminé el recordatorio de *{planta}*.",
            parse_mode="Markdown",
            reply_markup=main_keyboard()
        )
    else:
        bot.send_message(msg.chat.id, "Hubo un error eliminando el recordatorio.", reply_markup=main_keyboard())

# ---------------------------------------------------
#  IDENTIFICAR PLANTA (FOTO)
# ---------------------------------------------------
@bot.message_handler(content_types=['photo'])
def foto_handler(msg):
    photo = msg.photo[-1]
    file = bot.get_file(photo.file_id)
    img = bot.download_file(file.file_path)

    try:
        result = identify_plant(img)
        name = result.get("nombre", "Planta desconocida")
        care = result.get("cuidados", "Sin datos")
        riego = result.get("riego", 7)

        repo.add_or_update_plant(msg.from_user.id, name, care, riego)

        bot.send_message(
            msg.chat.id,
            f"🌿 *{name}*\n\n💧 Regar cada {riego} días\n\n{care}",
            parse_mode="Markdown",
            reply_markup=main_keyboard()
        )
    except Exception as e:
        bot.send_message(msg.chat.id, f"Error procesando la imagen: {e}", reply_markup=main_keyboard())

# ---------------------------------------------------
#  AYUDA
# ---------------------------------------------------
def ayuda(chat_id):
    bot.send_message(
        chat_id,
        "📘 *Ayuda*\n\n"
        "• 📸 Identificar planta → Enviás una foto y te digo qué planta es.\n"
        "• 🌿 Mis plantas → Lista tus plantas guardadas.\n"
        "• ⏰ Crear recordatorio → Te aviso cuándo regar.\n"
        "• 🗑 Eliminar recordatorio → Borra avisos anteriores.\n",
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )


# ---------------------------------------------------
#  TEST RECORDATORIO
# ---------------------------------------------------
@bot.message_handler(commands=['test'])
def test_recordatorio(msg):
    try:
        partes = msg.text.split()
        if len(partes) < 2:
            return bot.send_message(msg.chat.id, "Usá: /test <minutos>\nEjemplo: /test 3", reply_markup=main_keyboard())

        minutos = int(partes[1])
        if minutos <= 0:
            return bot.send_message(msg.chat.id, "El número debe ser mayor a 0.", reply_markup=main_keyboard())

        reminders.schedule_test_reminder(msg.from_user.id, minutos)
        bot.send_message(msg.chat.id, f"⏰ Listo, recibirás un recordatorio en {minutos} minutos.", reply_markup=main_keyboard())

    except ValueError:
        bot.send_message(msg.chat.id, "Ingresá un número válido. Ejemplo: /test 2", reply_markup=main_keyboard())

@bot.message_handler(commands=['delete_test'])
def borrar_test(msg):
    ok = reminders.remove_test_reminder(msg.from_user.id)

    if ok:
        bot.send_message(msg.chat.id, "🗑 Eliminé el test reminder.", reply_markup=main_keyboard())
    else:
        bot.send_message(msg.chat.id, "No había recordatorio de test activo.", reply_markup=main_keyboard())

# ---------------------------------------------------
#  CHAT LIBRE (IA)
# ---------------------------------------------------
@bot.message_handler(func=lambda m: True)
def chat_libre(msg):
    respuesta = chat_with_ai(msg.text)
    bot.reply_to(msg, respuesta, parse_mode="HTML", reply_markup=main_keyboard())

# ---------------------------------------------------
# bot.infinity_polling()


from flask import Flask, request

app = Flask(__name__)

@app.post(f"/bot{TELEGRAM_TOKEN}")
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "ok", 200


if __name__ == "__main__":
    import os

    bot.remove_webhook()

    
    WEBHOOK_URL = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/bot{TELEGRAM_TOKEN}"

    bot.set_webhook(url=WEBHOOK_URL)

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
