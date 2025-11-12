import logging
import os
import openai
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# OpenAI setup
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Start command
def start(update: Update, context: CallbackContext):
    update.message.reply_text("🤖 Hello! Jarvis AI bot is online and ready to chat!")

# Handle messages
def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are Jarvis, a smart helpful assistant."},
                {"role": "user", "content": user_message}
            ]
        )

        bot_reply = response.choices[0].message.content.strip()
        update.message.reply_text(bot_reply)

    except Exception as e:
        logger.error(f"Error: {e}")
        update.message.reply_text("⚠️ Sorry, there was an error with my AI response.")

def main():
    """Start the bot."""
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN not found in environment variables.")

    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    logger.info("Jarvis AI Bot is running...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
