import os
import threading
import asyncio
from flask import Flask
from telegram.ext import Application, CommandHandler, ContextTypes

# Load bot token from Render environment
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Flask app for Render web service
app = Flask(__name__)

@app.route("/")
def home():
    return "Jarvis Bot is running and connected!"

# Telegram command
async def start(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Jarvis Bot is online 🚀")

# Function to run the Telegram bot
async def run_telegram():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    await application.run_polling(close_loop=False)

# Start the bot in a safe background thread
def start_bot_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_telegram())

if __name__ == "__main__":
    # Start Telegram bot in its own event loop (no main-thread conflict)
    threading.Thread(target=start_bot_thread, daemon=True).start()

    # Start Flask server on Render port
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
