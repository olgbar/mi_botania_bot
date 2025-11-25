from bot.bot_instance import bot, reminders, repo
from handlers.ui import main_keyboard
from utils.ai import identify_plant


# ---------- VER PLANTAS ----------
def ver_plantas(user_id, chat_id):
    plants = repo.get_plants(user_id)

    if not plants:
        return bot.send_message(chat_id, "No tenés plantas registradas.", reply_markup=main_keyboard())

    plant_list = "\n".join([
        # f"• *{p['name']}* — {p['water_every_days']} días" 
        f"• {p['name']}" 
        for p in plants
    ])

    text = "🌿 Tus plantas:\n\n" + plant_list
    # text = "🌿 *Tus plantas:*\n\n" + "\n".join(f"• {p['name']}" for p in plants)
    bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=main_keyboard())

# ---------- ELIMINAR PLANTA ----------
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
        f"Listo! Eliminé *{planta}* de tus plantas.",
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )

# ---------- IDENTIFICAR PLANTA (FOTO) ----------
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
        
        # Actualizar contexto
        repo.set_last_plant(msg.from_user.id, name)

        bot.send_message(
            msg.chat.id,
            f"🌿 *{name}*\n\n💧 Recomiendo regar cada {riego} días\n\n{care}",
            parse_mode="Markdown",
            reply_markup=main_keyboard()
        )
    except Exception as e:
        bot.send_message(msg.chat.id, f"Error procesando la imagen: {e}", reply_markup=main_keyboard())
