bot.py

import os
import logging
import openai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load tokens from environment
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm your Jarvis bot 🤖 — how can I help?")

# Chat handler
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": user_message}]
        )
        reply = response.choices[0].message.content.strip()
        await update.message.reply_text(reply)
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await update.message.reply_text(f"Error: {str(e)}")

# Main function
def main():
    try:
        app = ApplicationBuilder().token(BOT_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

        logger.info("Bot is starting...")
        app.run_polling()
    except Exception as e:
        logger.critical(f"Bot failed to start: {e}")

if __name__ == "__main__":
    main()

requirements.txt

python-telegram-bot[asyncio]==20.7
openai==2.7.1
pandas==2.3.3
numpy==2.3.4
beautifulsoup4==4.14.2
websockets==15.0.1
httpx==0.25.2
anyio==4.11.0
typing-extensions==4.15.0
pydantic==2.12.4
pydantic-core==2.41.5
tzdata==2025.2
pytz==2025.2
requests==2.32.5
cffi==2.0.0
