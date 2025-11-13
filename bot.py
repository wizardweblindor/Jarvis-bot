import os
import asyncio
from flask import Flask
from telegram.ext import Application, CommandHandler

# Load your Telegram bot token
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Flask app
app = Flask(__name__)

@app.route("/")
def home():
    return "Jarvis Bot is running!"

# Telegram bot commands
async def start(update, context):
    await update.message.reply_text("Hello! I am Jarvis Bot.")

async def run_telegram_bot():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    # Run polling in main thread (Render requires this)
    await application.run_polling()

if __name__ == "__main__":
    # Start Flask in a separate process via Gunicorn on Render
    # and run the Telegram bot in the main thread
    asyncio.run(run_telegram_bot())
