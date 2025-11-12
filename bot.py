import os
import logging
from threading import Thread
from flask import Flask
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from openai import OpenAI

# ---------- CONFIG ----------
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# ---------- LOGGING ----------
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ---------- FLASK SERVER ----------
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Jarvis AI bot is live and running on Render!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# ---------- OPENAI CHAT FUNCTION ----------
def ask_openai(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are Jarvis, a helpful and clever AI assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"OpenAI error: {e}")
        return "⚠️ Sorry, I had trouble processing that request."

# ---------- TELEGRAM HANDLERS ----------
def start(update, context):
    update.message.reply_text("🤖 Hello, I'm Jarvis! Ask me anything or tell me a task to do.")

def help_command(update, context):
    update.message.reply_text("Just type a message and I'll use AI to respond helpfully!")

def chat(update, context):
    user_text = update.message.text
    reply = ask_openai(user_text)
    update.message.reply_text(reply)

# ---------- MAIN ----------
def main():
    # Start Flask web server in background
    Thread(target=run_flask).start()

    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not found in environment variables.")
        return

    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, chat))

    logger.info("🚀 Jarvis AI bot started successfully!")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
