import os
import logging
import openai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

Logging setup

logging.basicConfig(
format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
level=logging.INFO
)
logger = logging.getLogger(name)

Load environment variables

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

Start command

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text("Hello! I'm your Jarvis bot 🤖 — how can I help?")

Chat handler

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
logger.error(f"Error processing message: {e}")
await update.message.reply_text(f"Error: {str(e)}")

Main function

def main():
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

logger.info("Bot is running...")  
app.run_polling()  

if name == "main":
main()
