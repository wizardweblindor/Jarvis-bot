import os
import asyncio
from fastapi import FastAPI
import uvicorn
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)
from openai import OpenAI

# -------------------------------
# Environment variables
# -------------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_KEY)

# -------------------------------
# Memory storage
# -------------------------------
USER_MEMORY = {}

# -------------------------------
# FastAPI server for Render
# -------------------------------
app = FastAPI()

@app.get("/")
def home():
    return {"status": "Jarvis Advanced Bot Running"}

# -------------------------------
# Telegram Bot Handlers
# -------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💬 Chat", callback_data="chat")],
        [InlineKeyboardButton("🖼 Image Gen", callback_data="image")],
        [InlineKeyboardButton("🎤 Voice-to-Text", callback_data="v2t")],
        [InlineKeyboardButton("🧠 Memory", callback_data="memory")],
        [InlineKeyboardButton("📊 Tools", callback_data="tools")],
    ]
    await update.message.reply_text(
        "🤖 Jarvis Advanced is online! Choose an option:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "chat":
        await query.edit_message_text("💬 Chat mode activated. Send a message.")
    elif query.data == "image":
        await query.edit_message_text("🖼 Send me a description and I will generate an image.")
    elif query.data == "v2t":
        await query.edit_message_text("🎤 Send a voice message and I'll convert it to text.")
    elif query.data == "memory":
        await query.edit_message_text("🧠 Memory commands:\n/addmemory <text>\n/clearmemory")
    elif query.data == "tools":
        await query.edit_message_text("📊 Tools available:\n/calc 5+5\n/trade BTC 100 to USD")

# -------------------------------
# ChatGPT text response
# -------------------------------
async def chatgpt_text(message: str, user_id: int):
    memory = USER_MEMORY.get(user_id, "")
    prompt = f"User memory: {memory}\n\nUser says: {message}"

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    # Access content properly for the new SDK
    return resp.choices[0].message.content

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.message.from_user.id
    response = await chatgpt_text(text, user_id)
    await update.message.reply_text(response)

# -------------------------------
# Image generation
# -------------------------------
async def generate_image(prompt: str):
    img = client.images.generate(
        model="gpt-image-1",
        prompt=prompt
    )
    return img.data[0].url

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text
    url = await generate_image(prompt)
    await update.message.reply_text(f"🖼 Image generated: {url}")

# -------------------------------
# Memory management
# -------------------------------
async def add_memory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = " ".join(context.args)
    USER_MEMORY[user_id] = USER_MEMORY.get(user_id, "") + " " + text
    await update.message.reply_text("🧠 Memory updated.")

async def clear_memory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    USER_MEMORY[user_id] = ""
    await update.message.reply_text("🧠 Memory cleared.")

# -------------------------------
# Voice-to-text
# -------------------------------
async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.voice.get_file()
    path = f"voice_{update.message.from_user.id}.ogg"
    await file.download_to_drive(path)

    with open(path, "rb") as f:
        text_response = client.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",
            file=f
        )

    await update.message.reply_text(f"🎤 Transcribed text: {text_response.text}")

# -------------------------------
# Telegram Bot Startup
# -------------------------------
async def start_telegram_bot():
    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()

    # Handlers
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CallbackQueryHandler(menu_handler))
    app_bot.add_handler(CommandHandler("addmemory", add_memory))
    app_bot.add_handler(CommandHandler("clearmemory", clear_memory))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app_bot.add_handler(MessageHandler(filters.VOICE, voice_handler))

    # Start polling
    await app_bot.run_polling(stop_signals=None)

# -------------------------------
# Run both Telegram + FastAPI
# -------------------------------
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(start_telegram_bot())

    port = int(os.getenv("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
