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

---------------------- Helper Functions ----------------
