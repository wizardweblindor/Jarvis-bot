import os
import json
import openai
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import yfinance as yf
from apscheduler.schedulers.asyncio import AsyncIOScheduler

---------------------- Environment ----------------------

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

---------------------- Memory & Storage ----------------------

user_memory = {}  # Conversation memory per user
portfolio_file = "portfolio.json"  # Save trades/bets
scheduler = AsyncIOScheduler()
scheduler.start()

---------------------- Helper Functions ----------------------

def save_trade(user_id, trade):
try:
with open(portfolio_file, "r") as f:
portfolio = json.load(f)
except FileNotFoundError:
portfolio = {}
if str(user_id) not in portfolio:
portfolio[str(user_id)] = []
portfolio[str(user_id)].append(trade)
with open(portfolio_file, "w") as f:
json.dump(portfolio, f)

def load_portfolio(user_id):
try:
with open(portfolio_file, "r") as f:
portfolio = json.load(f)
return portfolio.get(str(user_id), [])
except FileNotFoundError:
return []

def save_message(user
