import os
import threading
from fastapi import FastAPI
import uvicorn

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)
from openai import OpenAI
from telegram import Update

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_KEY)

# -------------------------------------------------
# 1. Tiny Web Server (keeps Render Web Service alive)
# -------------------------------------------------

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Bot is running", "service": "Jarvis"}

def start_web_server():
    port = int(os.getenv("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)

# -------------------------------------------------
# 2. Telegram ChatGPT Bot
# -------------------------------------------------

async def start(update: Update, context):
    await update.message.reply_text("🤖 ChatGPT Telegram Bot is ONLINE!")


async def chatgpt_reply(update: Update, context):
    user_msg = update.message.text

    # OpenAI ChatGPT Request
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": user_msg}]
    )

    ai_reply = response.choices[0].message["content"]

    await update.message.reply_text(ai_reply)


def start_telegram_bot():
    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, chatgpt_reply)
    )

    application.run_polling(stop_signals=None)


# -------------------------------------------------
# 3. Run BOTH: the web server + the Telegram bot
# -------------------------------------------------

if __name__ == "__main__":
    # Start web server in background thread
    web_thread = threading.Thread(target=start_web_server)
    web_thread.daemon = True
    web_thread.start()

    # Start Telegram bot
    start_telegram_bot()
