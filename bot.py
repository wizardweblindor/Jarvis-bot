import os
import openai
from telegram import Update
from telegram.ext import (
ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
)
import yfinance as yf

Environment variables (set these in Render)

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

---------------------- Commands ----------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text(
"Hello! I'm Jarvis 🤖 — your AI assistant for finance, stocks, crypto, and betting insights.\n"
"Use /help to see commands."
)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
commands = (
"/start - Start Jarvis\n"
"/help - Show commands\n"
"/price <symbol> - Stock/Crypto price lookup\n"
"/bet <team/event> - Betting/odds insights\n"
"/advice <question> - Ask Jarvis anything about finance or betting"
)
await update.message.reply_text(commands)

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not context.args:
await update.message.reply_text("Please provide a stock or crypto symbol, e.g. /price TSLA")
return
symbol = context.args[0].upper()
try:
stock = yf.Ticker(symbol)
info = stock.info
response = (
f"{info.get('shortName', symbol)} ({symbol})\n"
f"Price: ${info.get('regularMarketPrice', 'N/A')}\n"
f"Change: {info.get('regularMarketChangePercent', 0):.2f}%"
)
await update.message.reply_text(response)
except Exception as e:
await update.message.reply_text(f"Error fetching data: {e}")

async def bet(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not context.args:
await update.message.reply_text("Please provide a team or event, e.g. /bet Arsenal")
return
query = " ".join(context.args)
# Using GPT to provide betting insights
try:
response = openai.chat.completions.create(
model="gpt-4o-mini",
messages=[{"role": "user", "content": f"Analyze betting odds and trends for {query}."}]
)
reply = response.choices[0].message.content.strip()
await update.message.reply_text(reply)
except Exception as e:
await update.message.reply_text(f"Error: {e}")

async def advice(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not context.args:
await update.message.reply_text("Please ask a question, e.g. /advice How is Tesla doing today?")
return
question = " ".join(context.args)
try:
response = openai.chat.completions.create(
model="gpt-4o-mini",
messages=[{"role": "user", "content": question}]
)
reply = response.choices[0].message.content.strip()
await update.message.reply_text(reply)
except Exception as e:
await update.message.reply_text(f"Error: {e}")

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

---------------------- Main ----------------------

def main():
app = ApplicationBuilder().token(BOT_TOKEN).build()

# Command handlers  
app.add_handler(CommandHandler("start", start))  
app.add_handler(CommandHandler("help", help_command))  
app.add_handler(CommandHandler("price", price))  
app.add_handler(CommandHandler("bet", bet))  
app.add_handler(CommandHandler("advice", advice))  

# Catch-all for general chat  
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))  

print("Jarvis Money Assistant is running...")  
app.run_polling()  

if name == "main":
main()
