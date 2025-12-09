import os
import csv
import io
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Configurar
logging.basicConfig(level=logging.INFO)
TOKEN = os.environ.get('TELEGRAM_TOKEN', '8382109200:AAFXY94thyyRDDSVKnIFXskwa6ffmpwxy-Q')

# Teclado
KEYBOARD = [["🌐 Render", "💻 GitHub"], ["📊 Analizar CSV", "ℹ️ Ayuda"]]
REPLY_KEYBOARD = ReplyKeyboardMarkup(KEYBOARD, resize_keyboard=True)

# Comandos
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "🚀 @experttdata_bot activo\n"
        "🌐 Render: https://render.com\n"
        "💻 GitHub: https://github.com",
        reply_markup=REPLY_KEYBOARD
    )

async def render(update: Update, context: CallbackContext):
    await update.message.reply_text("🌐 Render.com\n🔗 https://render.com")

async def github(update: Update, context: CallbackContext):
    await update.message.reply_text("💻 GitHub\n🔗 https://github.com")

async def help_cmd(update: Update, context: CallbackContext):
    await update.message.reply_text("/start /render /github")

# CSV
async def handle_csv(update: Update, context: CallbackContext):
    try:
        file = await update.message.document.get_file()
        file_bytes = io.BytesIO()
        await file.download_to_memory(file_bytes)
        file_bytes.seek(0)
        
        content = file_bytes.read().decode('utf-8')
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)
        
        await update.message.reply_text(
            f"📊 CSV: {len(rows)-1} filas, {len(rows[0])} columnas"
        )
    except:
        await update.message.reply_text("❌ Error con CSV")

# Mensajes
async def handle_text(update: Update, context: CallbackContext):
    text = update.message.text
    if text == "🌐 Render":
        await render(update, context)
    elif text == "💻 GitHub":
        await github(update, context)
    elif text == "📊 Analizar CSV":
        await update.message.reply_text("📎 Envía un archivo .csv")
    elif text == "ℹ️ Ayuda":
        await help_cmd(update, context)

# Principal
def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("render", render))
    app.add_handler(CommandHandler("github", github))
    app.add_handler(CommandHandler("help", help_cmd))
    
    app.add_handler(MessageHandler(filters.Document.FileExtension("csv"), handle_csv))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("🤖 Bot iniciado")
    app.run_polling()

if __name__ == '__main__':
    main()
