import os
import time
import threading
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters
import requests
import random

# ------------------------
# Config
# ------------------------
TOKEN = os.environ.get("BOT_TOKEN")
APP_URL = os.environ.get("APP_URL")
bot = Bot(token=TOKEN)
app = Flask(__name__)
dispatcher = Dispatcher(bot, None, workers=0)

# In-memory storage
tracked_stocks = {}  # {ticker: {'qty': int, 'target': float}}
tracked_bets = []    # list of {'stake': float, 'odds': float, 'goal': float}

# ------------------------
# Fun commands
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
# Stock commands
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
        target = float(context.args[2]) if len(context.args) > 2 else None
        tracked_stocks[ticker] = {'qty': tracked_stocks.get(ticker, {}).get('qty',0) + qty, 'target': target}
        update.message.reply_text(f"Added {qty} shares of {ticker}. Target: {target if target else 'None'}")
    except:
        update.message.reply_text("Usage: /addstock <ticker> <quantity> [target_price]")
dispatcher.add_handler(CommandHandler("addstock", add_stock))

def portfolio(update, context):
    if not tracked_stocks:
        update.message.reply_text("No stocks tracked yet.")
        return
    msg = "📊 Stock Portfolio:\n"
    for ticker, data in tracked_stocks.items():
        try:
            r = requests.get(f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={ticker}").json()
            price_now = r["quoteResponse"]["result"][0]["regularMarketPrice"]
            msg += f"{ticker}: {data['qty']} shares @ ${price_now} → Total ${price_now*data['qty']}"
            if data.get('target'):
                msg += f" (Target: ${data['target']})"
            msg += "\n"
        except:
            msg += f"{ticker}: {data['qty']} shares → Price not found\n"
    update.message.reply_text(msg)
dispatcher.add_handler(CommandHandler("portfolio", portfolio))

# ------------------------
# Betting commands
# ------------------------
def add_bet(update, context):
    try:
        stake = float(context.args[0])
        odds = float(context.args[1])
        goal = float(context.args[2]) if len(context.args) > 2 else None
        tracked_bets.append({'stake': stake, 'odds': odds, 'goal': goal})
        update.message.reply_text(f"Added bet: ${stake} @ {odds} Goal: {goal if goal else 'None'}")
    except:
        update.message.reply_text("Usage: /addbet <stake> <decimal_odds> [goal]")
dispatcher.add_handler(CommandHandler("addbet", add_bet))

def total_bets(update, context):
    if not tracked_bets:
        update.message.reply_text("No bets tracked yet.")
        return
    total_stake = sum(b['stake'] for b in tracked_bets)
    total_payout = sum(b['stake'] * b['odds'] for b in tracked_bets)
    msg = "🎲 Betting Summary:\n"
    for i, b in enumerate(tracked_bets,1):
        msg += f"Bet {i}: ${b['stake']} @ {b['odds']} → ${b['stake']*b['odds']} (Goal: {b['goal']})\n"
    msg += f"\nTotal Stake: ${total_stake}\nTotal Potential Payout: ${total_payout}"
    update.message.reply_text(msg)
dispatcher.add_handler(CommandHandler("totalbets", total_bets))

# ------------------------
# Background monitor
# ------------------------
def monitor():
    while True:
        # Check stocks
        for ticker, data in tracked_stocks.items():
            try:
                r = requests.get(f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={ticker}").json()
                price_now = r["quoteResponse"]["result"][0]["regularMarketPrice"]
                target = data.get('target')
                if target and price_now >= target:
                    bot.send_message(chat_id=os.environ.get("TELEGRAM_CHAT_ID"),
                                     text=f"🚨 {ticker} reached target price ${target}! Current: ${price_now}")
                    tracked_stocks[ticker]['target'] = None  # alert once
            except:
                continue
        
        # Check bets
        for b in tracked_bets:
            payout = b['stake'] * b['odds']
            if b.get('goal') and payout >= b['goal']:
                bot.send_message(chat_id=os.environ.get("TELEGRAM_CHAT_ID"),
                                 text=f"🎯 Bet reached goal! Stake ${b['stake']} @ {b['odds']} → ${payout}")
                b['goal'] = None
        time.sleep(60)  # check every 60 seconds

# Start monitor in background
threading.Thread(target=monitor, daemon=True).start()

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
