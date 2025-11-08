from flask import Flask
import os
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Jarvis Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def main():
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    application = Application.builder().token(BOT_TOKEN).build()

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Hello! I’m Jarvis 🤖")

    application.add_handler(CommandHandler("start", start))

    # Start Telegram bot in a thread
    threading.Thread(target=application.run_polling, daemon=True).start()

    # Run Flask web server to keep Render alive
    run_flask()

if __name__ == "__main__":
    main()
