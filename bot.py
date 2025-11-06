import os
import openai
import yfinance as yf
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

# ---------------------- Environment ----------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Make sure this is set in Render’s Environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

# ---------------------- Memory & Storage ----------------------
user_memory = {}
scheduler = BackgroundScheduler()
scheduler.start()

# ---------------------- Helper Functions ----------------------
def remember(user_id, key, value):
    if user_id not in user_memory:
        user_memory[user_id] = {}
    user_memory[user_id][key] = value

def recall(user_id, key):
    return user_memory.get(user_id, {}).get(key, "I don’t remember that yet.")

# ---------------------- Commands ----------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm Jarvis 🤖 — your smart money assistant!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💡 Commands:\n"
        "/stock <symbol> — Get stock price (e.g., /stock AAPL)\n"
        "/remember <key> <value> — Store a note\n"
        "/recall <key> — Retrieve a stored note\n"
        "/remind <minutes> <message> — Set a reminder\n"
        "Or just chat with me naturally!"
    )

async def stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("Please provide a stock symbol, e.g., /stock AAPL")
        return
    symbol = context.args[0].upper()
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d")
        price = data["Close"].iloc[-1]
        await update.message.reply_text(f"💰 {symbol} is currently at ${price:.2f}")
    except Exception as e:
        await update.message.reply_text(f"Error fetching stock: {e}")

async def remember_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /remember <key> <value>")
        return
    key = context.args[0]
    value = " ".join(context.args[1:])
    remember(user_id, key, value)
    await update.message.reply_text(f"Got it! I’ll remember {key} = {value}")

async def recall_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /recall <key>")
        return
    key = context.args[0]
    value = recall(user_id, key)
    await update.message.reply_text(f"{key}: {value}")

async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /remind <minutes> <message>")
        return

    try:
        minutes = int(context.args[0])
        message = " ".join(context.args[1:])
        remind_time = datetime.now().timestamp() + (minutes * 60)
        scheduler.add_job(
            send_reminder,
            'date',
            run_date=datetime.fromtimestamp(remind_time),
            args=[update, message]
        )
        await update.message.reply_text(f"⏰ Reminder set for {minutes} minutes from now.")
    except Exception as e:
        await update.message.reply_text(f"Error setting reminder: {e}")

async def send_reminder(update: Update, message: str):
    await update.message.reply_text(f"🔔 Reminder: {message}")

# ---------------------- Chat Function ----------------------
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user_id = update.effective_user.id
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are Jarvis, a friendly financial assistant who helps with investing, planning, and small talk."},
                {"role": "user", "content": user_message}
            ]
        )
        reply = response.choices[0].message.content.strip()
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text("Error: " + str(e))

# ---------------------- Main ----------------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stock", stock))
    app.add_handler(CommandHandler("remember", remember_command))
    app.add_handler(CommandHandler("recall", recall_command))
    app.add_handler(CommandHandler("remind", remind))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("✅ Jarvis Money Assistant is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
