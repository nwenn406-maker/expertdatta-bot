import os
import csv
import io
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Configurar
logging.basicConfig(level=logging.INFO)
TOKEN = os.environ.get('TELEGRAM_TOKEN', '8382109200:AAFXY94thyyRDDSVKnIFXskwa6ffmpwxy-Q')

# Teclado
KEYBOARD = [["🌐 Render", "💻 GitHub"], ["📊 Analizar CSV", "📈 SQL"]]
REPLY_KEYBOARD = ReplyKeyboardMarkup(KEYBOARD, resize_keyboard=True)

# Comandos
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🚀 @experttdata_bot activo\n"
        "🌐 Render: https://render.com\n"
        "💻 GitHub: https://github.com",
        reply_markup=REPLY_KEYBOARD
    )

def render(update: Update, context: CallbackContext):
    update.message.reply_text("🌐 Render.com\n🔗 https://render.com")

def github(update: Update, context: CallbackContext):
    update.message.reply_text("💻 GitHub\n🔗 https://github.com")

# CSV
def handle_csv(update: Update, context: CallbackContext):
    try:
        file = update.message.document.get_file()
        file_bytes = io.BytesIO()
        file.download(out=file_bytes)
        file_bytes.seek(0)
        
        content = file_bytes.read().decode('utf-8')
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)
        
        update.message.reply_text(
            f"📊 CSV: {len(rows)-1} filas, {len(rows[0])} columnas"
        )
    except:
        update.message.reply_text("❌ Error con CSV")

# Mensajes
def handle_text(update: Update, context: CallbackContext):
    text = update.message.text
    if text == "🌐 Render":
        render(update, context)
    elif text == "💻 GitHub":
        github(update, context)
    elif text == "📊 Analizar CSV":
        update.message.reply_text("📎 Envía un archivo .csv")
    elif text == "📈 SQL":
        update.message.reply_text("SELECT * FROM data;")

# Principal
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("render", render))
    dp.add_handler(CommandHandler("github", github))
    dp.add_handler(MessageHandler(Filters.document.file_extension("csv"), handle_csv))
    dp.add_handler(MessageHandler(Filters.text, handle_text))
    
    print("🤖 Bot iniciado")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
