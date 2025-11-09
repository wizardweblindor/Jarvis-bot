import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters

# Get environment variables
TOKEN = os.environ.get("TELEGRAM_TOKEN")
APP_URL = os.environ.get("APP_URL")  # e.g. https://jarvis-bot-2-zp0b.onrender.com

bot = Bot(token=TOKEN)
app = Flask(__name__)

# Create dispatcher for handling updates
dispatcher = Dispatcher(bot, None, workers=0)

# ------------------------
# Handlers
# ------------------------
def start(update, context):
    update.message.reply_text("Hello! Jarvis is online and ready to assist.")

def echo(update, context):
    update.message.reply_text(update.message.text)

# Add handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

# ------------------------
# Flask route for Telegram webhook
# ------------------------
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"

# ------------------------
# Set webhook when app starts
# ------------------------
@app.before_first_request
def setup_webhook():
    bot.set_webhook(f"{APP_URL}/{TOKEN}")

# ------------------------
# Run the Flask app
# ------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
