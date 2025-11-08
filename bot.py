import os
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- Environment Variables ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")  # Set this in Render
PORT = int(os.environ.get("PORT", 10000))  # Default Render port
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # e.g., https://your-app.onrender.com/webhook

# --- Flask app ---
app = Flask(__name__)

# --- Telegram bot app ---
bot_app = ApplicationBuilder().token(BOT_TOKEN).build()

# Example command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Jarvis bot is live 🚀")

bot_app.add_handler(CommandHandler("start", start))

# --- Webhook route for Telegram ---
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(), bot_app.bot)
    bot_app.update_queue.put_nowait(update)
    return "OK"

# --- Setup webhook when starting ---
async def set_webhook():
    await bot_app.bot.set_webhook(WEBHOOK_URL)

if __name__ == "__main__":
    import asyncio
    # Set webhook before starting Flask server
    asyncio.run(set_webhook())
    app.run(host="0.0.0.0", port=PORT)
