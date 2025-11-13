import os
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Jarvis Bot is online 🚀")

async def main():
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )
    app.add_handler(CommandHandler("start", start))

    print("🚀 BOT IS RUNNING USING POLLING")
    await app.run_polling(stop_signals=None)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
