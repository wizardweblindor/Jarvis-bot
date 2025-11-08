from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, filters
import os

# ---------- CONFIG ----------
TOKEN = os.environ.get("TELEGRAM_TOKEN")  # Set this in Render as an environment variable
PORT = int(os.environ.get("PORT", 10000))  # Render assigns a port automatically

bot = Bot(token=TOKEN)
app = Flask(__name__)
dispatcher = Dispatcher(bot, None, workers=0)  # Workers=0 for webhook mode

# ---------- HANDLERS ----------
def start(update: Update, context):
    update.message.reply_text("Hello! Jarvis AI Bot is live 🚀")

def echo(update: Update, context):
    update.message.reply_text(f"You said: {update.message.text}")

# Add handlers to dispatcher
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# ---------- FLASK ROUTES ----------
@app.route("/")
def home():
    return "Jarvis AI Bot is live and running!"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

# ---------- MAIN ----------
if __name__ == "__main__":
    # Set the webhook URL for Telegram
    HEROKU_URL = os.environ.get("APP_URL") or "https://jarvis-bot-2-zp0b.onrender.com"
    bot.set_webhook(url=f"{HEROKU_URL}/{TOKEN}")
    
    app.run(host="0.0.0.0", port=PORT)
