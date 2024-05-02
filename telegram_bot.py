import os
import yaml
from dotenv import load_dotenv
from groq import Groq
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Load environment variables from .env file
load_dotenv()

# Load configuration from config.yaml
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Load Groq API key from environment variable
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    print("GROQ_API_KEY environment variable not found. Please set it in the .env file.")
    exit()

client = Groq(api_key=GROQ_API_KEY)

# Define model details
model_option = "llama3-70b-8192"
model_info = config["models"][model_option]
max_tokens_range = model_info["tokens"]
default_max_tokens = config["default_max_tokens"]

# Initialize chat history
chat_history = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hi there! I'm a Telegram chatbot powered by Groq's language model. How can I assist you today?")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    chat_history.append({"role": "user", "content": user_input})

    try:
        chat_completion = client.chat.completions.create(
            model=model_option,
            messages=chat_history,
            max_tokens=default_max_tokens,
            stream=True
        )

        response = ""
        for chunk in chat_completion:
            if chunk.choices[0].delta.content:
                response += chunk.choices[0].delta.content
                await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
                await context.bot.send_message(chat_id=update.effective_chat.id, text=chunk.choices[0].delta.content)

        chat_history.append({"role": "assistant", "content": response})

    except Exception as e:
        error_message = f"Error: {e}"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=error_message)

def run_telegram_bot():
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    app.run_polling()

if __name__ == "__main__":
    run_telegram_bot()
