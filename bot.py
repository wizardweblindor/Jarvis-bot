import os
import asyncio
from flask import Flask
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from openai import OpenAI

# === ENVIRONMENT VARIABLES ===
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# === INITIALIZE CLIENTS ===
client = OpenAI(api_key=OPENAI_API_KEY)

# === FLASK APP (for Render keep-alive and health check) ===
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "🤖 Jarvis Bot is live and running on Render!"

# === TELEGRAM BOT ===
app_tg = ApplicationBuilder().token(BOT_TOKEN).build()

# --- Command: /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! Jarvis Bot is online and ready to help!")

# --- Command: /help ---
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💡 Just send me a message and I'll reply intelligently using OpenAI!")

# --- Message Handler ---
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are Jarvis, a helpful AI assistant."},
                {"role": "user", "content": user_message}
            ]
        )

        bot_reply = completion.choices[0].message.content
        await update.message.reply_text(bot_reply)

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {e}")

# === ADD HANDLERS ===
app_tg.add_handler(CommandHandler("start", start))
app_tg.add_handler(CommandHandler("help", help_command))
app_tg.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

# === RUN BOT (polling) ===
def run_bot():
    print("🚀 Starting Jarvis AI Bot (Flask + Telegram)...")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(
        app_tg.run_polling(
            stop_signals=None,
            close_loop=False,
            drop_pending_updates=True  # ✅ Avoids duplicate polling conflicts
        )
    )

# === ENTRY POINT ===
if __name__ == "__main__":
    # Run both Flask and Telegram together
    from threading import Thread

    Thread(target=run_bot, daemon=True).start()
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
