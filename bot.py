import os
import csv
import io
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters

TOKEN = os.environ.get('TELEGRAM_TOKEN', '8382109200:AAFXY94thyyRDDSVKnIFXskwa6ffmpwxy-Q')

KEYBOARD = [
    ["📊 CSV Básico", "📈 SQL"],
    ["🧮 Calculadora", "ℹ️ Ayuda"],
    ["🌐 Render", "💻 GitHub"]
]
REPLY_KEYBOARD = ReplyKeyboardMarkup(KEYBOARD, resize_keyboard=True)

async def start(update: Update, context):
    await update.message.reply_text(
        "🤖 @experttdata_bot - Fase 1\n\n"
        "✅ *Funciones básicas:*\n"
        "• 📊 CSV básico (sin pandas)\n"
        "• 📈 Ejemplos SQL\n"
        "• 🧮 Calculadora\n"
        "• 🌐 Render: https://render.com\n"
        "• 💻 GitHub: https://github.com\n\n"
        "🔧 *Próximamente:* Análisis CSV avanzado",
        parse_mode='Markdown',
        reply_markup=REPLY_KEYBOARD
    )

async def handle_csv(update: Update, context):
    try:
        file = await update.message.document.get_file()
        file_bytes = io.BytesIO()
        await file.download_to_memory(file_bytes)
        file_bytes.seek(0)
        
        content = file_bytes.read().decode('utf-8')
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)
        
        await update.message.reply_text(
            f"📊 CSV básico: {len(rows)-1} filas, {len(rows[0])} columnas",
            parse_mode='Markdown'
        )
    except:
        await update.message.reply_text("❌ Error con CSV")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.FileExtension("csv"), handle_csv))
    print("🤖 Bot Fase 1 iniciado")
    app.run_polling()

if __name__ == '__main__':
    main()
