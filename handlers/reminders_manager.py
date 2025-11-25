from bot.bot_instance import bot, repo, reminders as reminder_manager
from handlers.ui import main_keyboard
from services import reminders

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
    reminder_manager.schedule_plant(user, planta, days)

    bot.send_message(msg.chat.id, f"⏰ Listo, te recuerdo cada {days} días.", reply_markup=main_keyboard())

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
        return bot.send_message(msg.chat.id, "No encontré ese recordatorio.", reply_markup=main_keyboard())

    ok = reminder_manager.remove_plant_reminder(msg.from_user.id, planta)

    repo.remove_reminder(msg.from_user.id, planta)
    if ok:
        repo.set_last_plant(msg.from_user.id, '')
        bot.send_message(msg.chat.id, f"🗑 Listo, eliminé *{planta}*.", parse_mode="Markdown", reply_markup=main_keyboard())
    else:
        bot.send_message(msg.chat.id, "Error eliminando el recordatorio.", reply_markup=main_keyboard())
