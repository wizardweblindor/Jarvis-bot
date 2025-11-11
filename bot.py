import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import openai

# ---------- CONFIG ----------
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set!")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set!")

# Set OpenAI API key (no need to create OpenAI() client)
openai.api_key = OPENAI_API_KEY

# ---------- LOGGING ----------
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# ---------- OPENAI CHAT FUNCTION ----------
def ask_openai(messages):
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        return "Sorry, I couldn't process that."

# ---------- TELEGRAM COMMANDS ----------
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hello! I am your AI assistant. Ask me anything.")

def help_command(update: Update, context: CallbackContext):
    update.message.reply_text("You can just type a message, and I'll reply!")

def chat(update: Update, context: CallbackContext):
    user_text = update.message.text
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": user_text}
    ]
    reply = ask_openai(messages)
    update.message.reply_text(reply)

# ---------- MAIN FUNCTION ----------
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Command handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))

    # Chat handler
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, chat))

    # Start the bot
    updater.start_polling()
    logger.info("Bot started!")
    updater.idle()

if __name__ == "__main__":
    main()
