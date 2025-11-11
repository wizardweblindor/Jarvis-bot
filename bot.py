import openai
import os

openai.api_key = os.environ["OPENAI_API_KEY"]

def chat_with_gpt(update, context):
    user_message = update.message.text

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are Jarvis, a helpful AI assistant that gives clear, friendly answers."},
                {"role": "user", "content": user_message}
            ],
        )

        reply = response["choices"][0]["message"]["content"]
        update.message.reply_text(reply)

    except Exception as e:
        update.message.reply_text("⚠️ Sorry, I had trouble thinking just now.")

# Replace echo handler line with this:
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, chat_with_gpt))
