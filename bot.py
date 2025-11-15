import os
import asyncio
from fastapi import FastAPI
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)
from openai import OpenAI
from uvicorn import Config, Server

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_KEY)

USER_MEMORY = {}
USER_MODE = {}

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Jarvis Advanced Bot Running"}

# ------------------ Telegram Handlers ------------------
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
    user_id = query.from_user.id

    USER_MODE[user_id] = query.data
    await query.edit_message_text(f"Mode set to {query.data}. Send a message.")

async def chatgpt_text(message: str, user_id: int):
    memory = USER_MEMORY.get(user_id, "")
    prompt = f"User memory: {memory}\n\nUser says: {message}"
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.choices[0].message["content"]

async def generate_image(prompt: str):
    img = client.images.generate(model="gpt-image-1", prompt=prompt)
    return img.data[0].url

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    mode = USER_MODE.get(user_id)
    text = update.message.text

    if mode == "chat":
        response = await chatgpt_text(text, user_id)
        await update.message.reply_text(response)
    elif mode == "image":
        url = await generate_image(text)
        await update.message.reply_text(f"🖼 Image generated: {url}")
    else:
        await update.message.reply_text("Select a mode from /start first!")

async def add_memory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    USER_MEMORY[user_id] = USER_MEMORY.get(user_id, "") + " " + " ".join(context.args)
    await update.message.reply_text("🧠 Memory updated.")

async def clear_memory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    USER_MEMORY[update.message.from_user.id] = ""
    await update.message.reply_text("🧠 Memory cleared.")

async def start_telegram_bot():
    app_telegram = ApplicationBuilder().token(BOT_TOKEN).build()
    app_telegram.add_handler(CommandHandler("start", start))
    app_telegram.add_handler(CallbackQueryHandler(menu_handler))
    app_telegram.add_handler(CommandHandler("addmemory", add_memory))
    app_telegram.add_handler(CommandHandler("clearmemory", clear_memory))
    app_telegram.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    await app_telegram.initialize()
    await app_telegram.start()
    await app_telegram.updater.start_polling()  # safe polling
    return app_telegram

async def main():
    bot_task = asyncio.create_task(start_telegram_bot())
    config = Config(app=app, host="0.0.0.0", port=int(os.getenv("PORT", 10000)), log_level="info")
    server = Server(config)
    api_task = asyncio.create_task(server.serve())
    await asyncio.gather(bot_task, api_task)

if __name__ == "__main__":
    asyncio.run(main())
