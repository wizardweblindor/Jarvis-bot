import os
import openai
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

Environment variables

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Render environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

Handlers

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text("Hello! I'm your Jarvis bot 🤖 — how can I help?")

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
await update.message.reply_text("Error: " + str(e))

Main

def main():
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
print("Jarvis is running...")
app.run_polling()

if name == "main":
main()            run_date=datetime.fromtimestamp(remind_time),
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

