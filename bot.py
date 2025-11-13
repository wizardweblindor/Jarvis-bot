import os
import threading
import asyncio
from flask import Flask
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Jarvis Bot is running on Render!"

# Telegram command
async def start(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Jarvis Bot is online 🚀")

# Telegram bot runner
async def run_telegram():
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )
    application.add_handler(CommandHandler("start", start))

    # Disable signal handling for background thread
    await application.run_polling(
        stop_signals=None,  # 👈 prevents wakeup_fd / signal errors
        close_loop=False
    )

# Background thread starter
def start_bot_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_telegram())

if __name__ == "__main__":
    threading.Thread(target=start_bot_thread, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
