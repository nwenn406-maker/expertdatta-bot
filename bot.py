import os
import pandas as pd
import io
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get('TELEGRAM_TOKEN', '8382109200:AAFXY94thyyRDDSVKnIFXskwa6ffmpwxy-Q')

KEYBOARD = [
    ["📊 Analizar CSV", "📈 Ejemplo SQL"],
    ["🧮 Calculadora", "ℹ️ Ayuda"],
    ["🌐 Render", "💻 GitHub"]
]
REPLY_KEYBOARD = ReplyKeyboardMarkup(KEYBOARD, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🖥️ *Hola, soy tu DataBot*\n\n"
        "📊 **Analizar CSV**: Envíame .csv\n"
        "📈 **Ejemplo SQL**: Consultas ejemplo\n"
        "🧮 **Calculadora**: Operaciones\n"
        "🌐 **Render**: https://render.com\n"
        "💻 **GitHub**: https://github.com",
        parse_mode='Markdown',
        reply_markup=REPLY_KEYBOARD
    )

async def handle_csv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        file = await update.message.document.get_file()
        file_bytes = io.BytesIO()
        await file.download_to_memory(file_bytes)
        file_bytes.seek(0)
        
        df = pd.read_csv(file_bytes)
        
        response = (
            f"📊 *CSV Analizado*\n\n"
            f"• Filas: {df.shape[0]}\n"
            f"• Columnas: {df.shape[1]}\n"
            f"• Memoria: {df.memory_usage().sum() / 1024:.1f} KB\n\n"
            f"**Columnas:** {', '.join(df.columns.tolist()[:3])}"
        )
        
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)[:100]}")

async def render_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌐 https://render.com")

async def github_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💻 https://github.com")

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "📊 Analizar CSV":
        await update.message.reply_text("📎 Envía .csv")
    elif text == "🌐 Render":
        await render_info(update, context)
    elif text == "💻 GitHub":
        await github_info(update, context)

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.FileExtension("csv"), handle_csv))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))
    
    print("🤖 Bot con pandas iniciado")
    app.run_polling()

if __name__ == '__main__':
    main()
