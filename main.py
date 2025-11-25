from bot.bot_instance import bot
import telebot
import handlers.start
import handlers.plants
import handlers.reminders_manager
import handlers.ai_chat
from config import TELEGRAM_TOKEN

# ----------------EN RENDER IMPLEMENTANDO WEBHOOKS-----------------------------------

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


@app.route("/", methods=["GET"])
def home():
    return "Botania Bot está funcionando 🌱"



# # ----------------EN local-----------------------------------

# if __name__ == "__main__":
#     bot.infinity_polling()



