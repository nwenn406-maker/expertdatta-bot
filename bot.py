from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
import csv
import io

TOKEN = os.environ.get('TELEGRAM_TOKEN', '8382109200:AAFXY94thyyRDDSVKnIFXskwa6ffmpwxy-Q')

KEYBOARD = [
    ["🌐 Render", "💻 GitHub"],
    ["📊 Analizar CSV", "📈 Ejemplo SQL"],
    ["🧮 Calculadora", "ℹ️ Ayuda"]
]
REPLY_KEYBOARD = ReplyKeyboardMarkup(KEYBOARD, resize_keyboard=True)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 *@experttdata_bot - Expert Data Assistant*\n\n"
        "✅ *Funciones activas:*\n"
        "• 🌐 Render.com info\n"
        "• 💻 GitHub.com info\n"
        "• 📊 Análisis CSV (sin pandas)\n"
        "• 📈 Ejemplos SQL\n"
        "• 🧮 Calculadora\n\n"
        "🔧 *Tecnología:*\n"
        "• Python CSV nativo (ligero)\n"
        "• Telegram Bot API\n"
        "• Hosting: Render.com\n\n"
        "🤖 *Optimizado para Render Free*",
        parse_mode='Markdown',
        reply_markup=REPLY_KEYBOARD
    )

async def handle_csv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        file = await update.message.document.get_file()
        file_bytes = io.BytesIO()
        await file.download_to_memory(file_bytes)
        file_bytes.seek(0)
        
        content = file_bytes.read().decode('utf-8')
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)
        
        if not rows:
            await update.message.reply_text("❌ CSV vacío")
            return
        
        header = rows[0]
        row_count = len(rows) - 1
        
        response = (
            f"📊 *CSV Analizado*\n\n"
            f"• **Filas:** {row_count}\n"
            f"• **Columnas:** {len(header)}\n"
            f"• **Tamaño:** {len(content)/1024:.1f} KB\n\n"
            f"**Columnas:**\n"
        )
        
        for i, col in enumerate(header[:6]):
            response += f"{i+1}. `{col}`\n"
        
        if len(header) > 6:
            response += f"... y {len(header)-6} más\n"
        
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)[:100]}", parse_mode='Markdown')

async def render_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌐 *Render.com*\nPlataforma de hosting\n🔗 https://render.com",
        parse_mode='Markdown'
    )

async def github_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💻 *GitHub*\nControl de versiones\n🔗 https://github.com",
        parse_mode='Markdown'
    )

async def sql_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "```sql\nSELECT * FROM datos LIMIT 10;\n```",
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *Comandos:* /start, /render, /github, /help\n\n"
        "📊 *Para analizar CSV:*\n"
        "1. Toca 📎 (clip)\n"
        "2. Selecciona 'Documento'\n"
        "3. Envía archivo .csv\n\n"
        "🤖 @experttdata_bot",
        parse_mode='Markdown'
    )

async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🌐 Render":
        await render_command(update, context)
    elif text == "💻 GitHub":
        await github_command(update, context)
    elif text == "📊 Analizar CSV":
        await handle_csv(update, context)
    elif text == "📈 Ejemplo SQL":
        await sql_command(update, context)
    elif text == "🧮 Calculadora":
        await update.message.reply_text("🔢 Escribe: 2+2, 3*4, sqrt(25)")
    elif text == "ℹ️ Ayuda":
        await help_command(update, context)

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("render", render_command))
    app.add_handler(CommandHandler("github", github_command))
    app.add_handler(CommandHandler("help", help_command))
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu))
    app.add_handler(MessageHandler(filters.Document.FileExtension("csv"), handle_csv))
    
    print("=" * 50)
    print("🤖 @experttdata_bot - SIN PANDAS")
    print("📊 Usando CSV nativo de Python")
    print("✅ Optimizado para Render Free")
    print("=" * 50)
    
    app.run_polling()

if __name__ == '__main__':
    main()
