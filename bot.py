import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, filters
import openai

# ==========================
# CONFIG
# ==========================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # Telegram Bot Token
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # OpenAI API Key

openai.api_key = OPENAI_API_KEY

# ==========================
# FLASK APP
# ==========================
app = Flask(__name__)

bot = Bot(token=TELEGRAM_TOKEN)
dispatcher = Dispatcher(bot, None, use_context=True)

# ==========================
# BOT HANDLERS
# ==========================
def start(update: Update, context):
    update.message.reply_text("Hello! I am your AI assistant. Send me a message and I will respond.")

def chat(update: Update, context):
    user_message = update.message.text

    try:
        # New OpenAI API usage
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": user_message}]
        )
        answer = response.choices[0].message.content
        update.message.reply_text(answer)

    except Exception as e:
        update.message.reply_text(f"Error: {str(e)}")

# Add handlers to dispatcher
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

# ==========================
# FLASK WEBHOOK
# ==========================
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, bot)
    dispatcher.process_update(update)
    return "ok"

@app.route("/")
def index():
    return "Bot is running!"

# ==========================
# RUN
# ==========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
