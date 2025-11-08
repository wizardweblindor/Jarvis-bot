import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters

# Environment variables
TOKEN = os.environ.get("TELEGRAM_TOKEN")  # Set your bot token in Render secrets
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # Set your deployed URL in Render secrets

# Flask app
app = Flask(__name__)
bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot, None, workers=0)  # Dispatcher without polling

# Handlers
def start(update, context):
    update.message.reply_text("Hello! Jarvis AI Bot is online.")

def echo(update, context):
    update.message.reply_text(update.message.text)

# Add handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

# Flask routes
@app.route("/")
def index():
    return "Bot is running!"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"

# Set webhook on start
if __name__ == "__main__":
    # Set Telegram webhook
    bot.set_webhook(f"{WEBHOOK_URL}/{TOKEN}")
    # Use Render's assigned port
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
