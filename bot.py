import os
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import threading

BOT_TOKEN = os.environ.get("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 10000))

# Flask dummy server
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

# Telegram bot handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm your bot.")

def run_bot():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.run_polling()

# Start Telegram bot in a separate thread
threading.Thread(target=run_bot).start()

# Run Flask server to satisfy Render
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Load your bot token from environment (Render dashboard)
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Telegram command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Jarvis is online and running on Render!")

# Create Telegram bot application
bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
bot_app.add_handler(CommandHandler("start", start))

# Function to run the Telegram bot
def run_bot():
    bot_app.run_polling()

# Start the Telegram bot in a separate thread
threading.Thread(target=run_bot).start()

# Create a simple Flask web server (Render requires a web port)
server = Flask(__name__)

@server.route("/")
def home():
    return "✅ Jarvis bot is alive and running on Render!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    server.run(host="0.0.0.0", port=port)
