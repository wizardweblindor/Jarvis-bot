import os
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN")


async def start(update, context):
    await update.message.reply_text("Bot is live and running on Render 🚀")


async def echo(update, context):
    text = update.message.text
    await update.message.reply_text(f"You said: {text}")


def main():
    application = (
        ApplicationBuilder()
        .token(TOKEN)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # IMPORTANT: Do NOT use asyncio.run() on Render
    application.run_polling(stop_signals=None)


if __name__ == "__main__":
    main()
