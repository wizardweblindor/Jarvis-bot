import os
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

# Combined async runner
async def main():
    print("🚀 Starting Jarvis Telegram bot...")

    # Create Telegram bot application
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )
    application.add_handler(CommandHandler("start", start))

    # Flask server (using Hypercorn)
    async def run_flask():
        from hypercorn.asyncio import serve
        from hypercorn.config import Config
        config = Config()
        config.bind = ["0.0.0.0:" + os.environ.get("PORT", "10000")]
        await serve(app, config)

    # Run Telegram polling + Flask at same time
    await asyncio.gather(
        application.run_polling(stop_signals=None, close_loop=False),
        run_flask()
    )


if __name__ == "__main__":
    asyncio.run(main())
