import os
import asyncio
from threading import Thread
from flask import Flask, request
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from openai import OpenAI

# -------------------------
# Flask setup
# -------------------------
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Jarvis AI Bot is live and ready!"

# -------------------------
# Environment variables
# -------------------------
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# -------------------------
# Initialize clients
# -------------------------
client = OpenAI(api_key=OPENAI_API_KEY)
app_tg = ApplicationBuilder().token(BOT_TOKEN).build()

# -------------------------
# Telegram command: /start
# -------------------------
async def start(update, context):
    await update.message.reply_text("Hey there 👋 I'm Jarvis — your AI assistant! Send me a message and I’ll reply intelligently.")

# -------------------------
# Telegram message handler
# -------------------------
async def chat_with_gpt(update, context):
    user_message = update.message.text

    try:
        # Call OpenAI ChatGPT
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # or "gpt-4o" if you prefer the full model
            messages=[
                {"role": "system", "content": "You are Jarvis, a helpful AI assistant."},
                {"role": "user", "content": user_message},
            ],
        )

        reply = response.choices[0].message.content
        await update.message.reply_text(reply)

    except Exception as e:
        await update.message.reply_text("⚠️ Sorry, something went wrong.\n" + str(e))

# -------------------------
# Register handlers
# -------------------------
app_tg.add_handler(CommandHandler("start", start))
app_tg.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_with_gpt))

# -------------------------
# Run Telegram bot safely in a thread
# -------------------------
def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(
        app_tg.run_polling(
            stop_signals=None,
            close_loop=False,
            drop_pending_updates=True  # ✅ Clears old polling sessions
        )
    )
# -------------------------
# Run Flask + Bot
# -------------------------
if __name__ == "__main__":
    print("🚀 Starting Jarvis AI Bot (Flask + Telegram)...")
    Thread(target=run_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=10000, use_reloader=False)
