import os
import asyncio
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN missing in environment variables.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Jarvis online and ready to chat!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text(f"You said: {text}")

@app.route("/")
def home():
    return "Jarvis bot is live ✅"

async def run_telegram():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    await application.run_polling()

def start_asyncio_thread():
    asyncio.run(run_telegram())

if __name__ == "__main__":
    threading.Thread(target=start_asyncio_thread).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
