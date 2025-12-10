import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters

logging.basicConfig(level=logging.INFO)
TOKEN = os.environ.get('TELEGRAM_TOKEN', '8382109200:AAFXY94thyyRDDSVKnIFXskwa6ffmpwxy-Q')

KEYBOARD = [["🌐 Render", "💻 GitHub"]]
REPLY_KEYBOARD = ReplyKeyboardMarkup(KEYBOARD, resize_keyboard=True)

async def start(update: Update, context):
    await update.message.reply_text(
        "🤖 @experttdata_bot en Railway\n\n"
        "🌐 Render: https://render.com\n"
        "💻 GitHub: https://github.com",
        reply_markup=REPLY_KEYBOARD
    )

async def render(update: Update, context):
    await update.message.reply_text("🌐 https://render.com")

async def github(update: Update, context):
    await update.message.reply_text("💻 https://github.com")

async def handle_buttons(update: Update, context):
    text = update.message.text
    if text == "🌐 Render":
        await render(update, context)
    elif text == "💻 GitHub":
        await github(update, context)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))
    print("🤖 Bot en Railway iniciado")
    app.run_polling()

if __name__ == '__main__':
    main()
