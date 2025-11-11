import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters
import requests
import random

# ------------------------
# Config
# ------------------------
TOKEN = os.environ.get("TELEGRAM_TOKEN")
APP_URL = os.environ.get("APP_URL")
bot = Bot(token=TOKEN)
app = Flask(__name__)
dispatcher = Dispatcher(bot, None, workers=0)

# In-memory storage for simplicity
tracked_stocks = {}   # {ticker: quantity}
tracked_bets = []     # list of (stake, odds)

# ------------------------
# Fun Commands
# ------------------------
def ping(update, context):
    update.message.reply_text("Pong 🏓")
dispatcher.add_handler(CommandHandler("ping", ping))

jokes = [
    "Why did the stock trader cross the road? To get to the green side!",
    "I asked my broker for a loan. He said, 'Stocks only!'"
]
def joke(update, context):
    update.message.reply_text(random.choice(jokes))
dispatcher.add_handler(CommandHandler("joke", joke))

def flip(update, context):
    update.message.reply_text(random.choice(["Heads", "Tails"]))
dispatcher.add_handler(CommandHandler("flip", flip))

def roll(update, context):
    try:
        sides = int(context.args[0])
        update.message.reply_text(f"🎲 You rolled: {random.randint(1, sides)}")
    except:
        update.message.reply_text("Usage: /roll <number_of_sides>")
dispatcher.add_handler(CommandHandler("roll", roll))

# ------------------------
# Stock Commands
# ------------------------
def price(update, context):
    try:
        ticker = context.args[0].upper()
        r = requests.get(f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={ticker}").json()
        current_price = r["quoteResponse"]["result"][0]["regularMarketPrice"]
        update.message.reply_text(f"{ticker} current price: ${current_price}")
    except:
        update.message.reply_text("Usage: /price <ticker> or ticker not found.")
dispatcher.add_handler(CommandHandler("price", price))

def add_stock(update, context):
    try:
        ticker = context.args[0].upper()
        qty = int(context.args[1])
        tracked_stocks[ticker] = tracked_stocks.get(ticker, 0) + qty
        update.message.reply_text(f"Added {qty} shares of {ticker}. Total: {tracked_stocks[ticker]}")
    except:
        update.message.reply_text("Usage: /addstock <ticker> <quantity>")
dispatcher.add_handler(CommandHandler("addstock", add_stock))

def portfolio(update, context):
    if not tracked_stocks:
        update.message.reply_text("No stocks tracked yet.")
        return
    msg = "📊 Stock Portfolio:\n"
    for ticker, qty in tracked_stocks.items():
        try:
            r = requests.get(f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={ticker}").json()
            price_now = r["quoteResponse"]["result"][0]["regularMarketPrice"]
            msg += f"{ticker}: {qty} shares @ ${price_now} → Total ${price_now * qty}\n"
        except:
            msg += f"{ticker}: {qty} shares → Price not found\n"
    update.message.reply_text(msg)
dispatcher.add_handler(CommandHandler("portfolio", portfolio))

# ------------------------
# Betting Commands
# ------------------------
def add_bet(update, context):
    try:
        stake = float(context.args[0])
        odds = float(context.args[1])
        tracked_bets.append((stake, odds))
        update.message.reply_text(f"Added bet: ${stake} at odds {odds}")
    except:
        update.message.reply_text("Usage: /addbet <stake> <decimal_odds>")
dispatcher.add_handler(CommandHandler("addbet", add_bet))

def total_bets(update, context):
    if not tracked_bets:
        update.message.reply_text("No bets tracked yet.")
        return
    total_stake = sum(stake for stake, _ in tracked_bets)
    total_payout = sum(stake * odds for stake, odds in tracked_bets)
    msg = "🎲 Betting Summary:\n"
    for i, (stake, odds) in enumerate(tracked_bets, 1):
        msg += f"Bet {i}: ${stake} @ {odds} → ${stake*odds}\n"
    msg += f"\nTotal Stake: ${total_stake}\nTotal Potential Payout: ${total_payout}"
    update.message.reply_text(msg)
dispatcher.add_handler(CommandHandler("totalbets", total_bets))

# ------------------------
# Echo fallback
# ------------------------
def echo(update, context):
    update.message.reply_text(update.message.text)
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

# ------------------------
# Flask webhook
# ------------------------
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"

@app.before_first_request
def setup_webhook():
    bot.set_webhook(f"{APP_URL}/{TOKEN}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
