# bot.py
import os
import logging
from typing import Dict
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Optional OpenAI integration
try:
    import openai
    OPENAI_AVAILABLE = True
except Exception:
    OPENAI_AVAILABLE = False

# Get tokens from environment variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if OPENAI_AVAILABLE and OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

if not BOT_TOKEN:
    raise SystemExit("❌ BOT_TOKEN environment variable is not set. Please set it before running the bot.")

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Simple per-user memory (not persistent)
sessions: Dict[int, Dict] = {}

def get_session(user_id: int) -> Dict:
    """Get or create a session for a specific user."""
    if user_id not in sessions:
        sessions[user_id] = {"messages": []}
    return sessions[user_id]

# --- COMMAND HANDLERS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    await update.message.reply_text(
        f"👋 Hi {user.first_name or 'there'}! I’m your Telegram bot.\n"
        "Type /help to see what I can do!"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    await update.message.reply_text(
        "🤖 *Bot Commands:*\n"
        "/start - Start the bot\n"
        "/help - Show this message\n"
        "/ping - Test if I’m online\n\n"
        "💬 *Chat:*\n"
        "Just send me a message — I’ll echo it back.\n"
        "If you type `ai: your question`, I’ll reply using AI (if OpenAI is set up).",
        parse_mode="Markdown",
    )

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ping command"""
    await update.message.reply_text("🏓 Pong!")

# --- MESSAGE HANDLERS ---

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle normal text messages"""
    user_id = update.effective_user.id
    text = (update.message.text or "").strip()
    session = get_session(user_id)

    # AI mode
    if text.lower().startswith("ai:") and OPENAI_AVAILABLE and OPENAI_API_KEY:
        prompt = text[3:].strip()
        session["messages"].append({"role": "user", "content": prompt})
        ai_reply = ai_reply_openai(session["messages"])
        session["messages"].append({"role": "assistant", "content": ai_reply})
        await update.message.reply_text(ai_reply)
        return

    # Default echo
    session["messages"].append({"role": "user", "content": text})
    await update.message.reply_text(f"You said: {text}")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle received photos"""
    user_id = update.effective_user.id
    photos = update.message.photo

    if not photos:
        await update.message.reply_text("No photo detected.")
        return

    # Get largest photo
    photo = photos[-1]
    file = await context.bot.get_file(photo.file_id)

    os.makedirs("downloads", exist_ok=True)
    local_path = f"downloads/{photo.file_id}.jpg"
    await file.download_to_drive(local_path)

    session = get_session(user_id)
    session.setdefault("files", []).append(local_path)

    await update.message.reply_text(f"📸 Saved your photo to: {local_path}")

# --- OPTIONAL: AI FUNCTION ---

def ai_reply_openai(messages):
    """Generate an AI response using OpenAI"""
    if not OPENAI_AVAILABLE or not OPENAI_API_KEY:
        return "⚠️ OpenAI not configured."
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are a helpful assistant."}] + messages[-8:],
            max_tokens=300,
            temperature=0.7,
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.exception("OpenAI error")
        return f"⚠️ AI error: {e}"

# --- MAIN ENTRY POINT ---

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🤖 Bot is starting...")
    app.run_polling(poll_interval=1.0)

if __name__ == "__main__":
    main()


