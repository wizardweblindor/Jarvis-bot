import os
import logging
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, MessageHandler, Filters
from openai import OpenAI

# Telegram bot token and OpenAI key
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize Flask
app = Flask(__name__)

# Initialize clients
bot = Bot(token=BOT_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Handle incoming Telegram messages
def handle_message(update, context):
    user_message = update.message.text
    chat_id = update.message.chat_id

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are Jarvis, a helpful assistant."},
                {"role": "user", "content": user_message}
            ]
        )
        reply = response.choices[0].message.content
        bot.send_message(chat_id=chat_id, text=reply)
    except Exception as e:
        logger.error(f"Error: {e}")
        bot.send_message(chat_id=chat_id, text="⚠️ Sorry, an error occurred.")

# Set up dispatcher
from telegram.ext import CallbackContext
dispatcher = Dispatcher(bot, None, use_context=True)
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

# Flask webhook route
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok", 200

# Root test route
@app.route("/")
def home():
    return "Bot is running!", 200

# Run app (for Render)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
