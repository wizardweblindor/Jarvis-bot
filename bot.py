import os
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Jarvis Bot is online 🚀")

async def main():
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    application.add_handler(CommandHandler("start", start))

    print("🚀 Telegram bot running on polling...")
    await application.run_polling(stop_signals=None)

# ---------------------------------------------------------------
# IMPORTANT: DO NOT USE asyncio.run() ON RENDER
# ---------------------------------------------------------------
if __name__ == "__main__":
    import asyncio

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop already running (Render), run inside it
            loop.create_task(main())
        else:
            loop.run_until_complete(main())
    except RuntimeError:
        # fallback
        asyncio.run(main())
