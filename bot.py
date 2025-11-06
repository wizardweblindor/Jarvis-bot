import os
import openai
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

Load tokens from environment variables

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

Start command

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text("Hello! I'm your Jarvis bot 🤖 — how can I help?")

Chat messages

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

Main function

def main():
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

print("Bot is running...")  
app.run_polling()  

if name == "main":
main()
