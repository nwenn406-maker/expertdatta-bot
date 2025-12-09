from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

TOKEN = os.environ.get('TELEGRAM_TOKEN', '8382109200:AAFXY94thyyRDDSVKnIFXskwa6ffmpwxy-Q')

KEYBOARD_OPTIONS = [
    ["🌐 Render", "💻 GitHub"],
    ["📊 Analizar CSV", "📈 Ejemplo SQL"],
    ["🧮 Calculadora", "ℹ️ Ayuda"],
    ["📄 Generar PDF", "🔍 Web Scraping"]
]
REPLY_KEYBOARD = ReplyKeyboardMarkup(KEYBOARD_OPTIONS, resize_keyboard=True)

# ----- COMANDO /start -----
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"👋 *Hola {user.first_name}!*\n\n"
        "🚀 *@experttdata_bot - Versión Completa*\n\n"
        "✅ *Todas las funciones activas:*\n"
        "• 📊 Análisis CSV (pandas)\n"
        "• 🌐 Info Render/GitHub\n"
        "• 📄 Generación PDF (reportlab)\n"
        "• 🔍 Web Scraping (BeautifulSoup)\n"
        "• 📈 Ejemplos SQL\n"
        "• 🧮 Calculadora\n\n"
        "🔧 *Dependencias instaladas:*\n"
        "• python-telegram-bot 20.7\n"
        "• pandas 2.2.0\n"
        "• beautifulsoup4 4.12.2\n"
        "• reportlab 4.1.0\n\n"
        "🤖 *Hosting:* Render.com",
        parse_mode='Markdown',
        reply_markup=REPLY_KEYBOARD
    )

# ----- ANÁLISIS CSV -----
async def handle_csv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        file = await update.message.document.get_file()
        file_bytes = io.BytesIO()
        await file.download_to_memory(file_bytes)
        file_bytes.seek(0)
        
        df = pd.read_csv(file_bytes, nrows=1000)
        
        summary = (
            f"📊 *CSV Analizado*\n\n"
            f"• **Filas:** {len(df)}\n"
            f"• **Columnas:** {len(df.columns)}\n"
            f"• **Memoria:** {df.memory_usage(deep=True).sum() / 1024:.1f} KB\n\n"
            f"**Primeras 5 columnas:**\n"
        )
        
        for i, col in enumerate(df.columns[:5]):
            summary += f"{i+1}. `{col}`\n"
        
        numeric = df.select_dtypes(include='number').columns
        if len(numeric) > 0:
            summary += f"\n**{len(numeric)} columnas numéricas**"
        
        await update.message.reply_text(summary, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)[:100]}", parse_mode='Markdown')

# ----- GENERAR PDF -----
async def handle_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        
        c.setFont("Helvetica", 16)
        c.drawString(100, 750, f"Reporte de @experttdata_bot")
        
        c.setFont("Helvetica", 12)
        c.drawString(100, 700, f"Usuario: {update.effective_user.first_name}")
        c.drawString(100, 680, f"Fecha: {update.message.date}")
        c.drawString(100, 660, "Funciones disponibles:")
        c.drawString(120, 640, "• Análisis CSV con pandas")
        c.drawString(120, 620, "• Web scraping con BeautifulSoup")
        c.drawString(120, 600, "• Generación de PDF con reportlab")
        c.drawString(120, 580, "• Consultas SQL de ejemplo")
        
        c.save()
        
        buffer.seek(0)
        await update.message.reply_document(
            document=buffer,
            filename=f"reporte_{update.effective_user.id}.pdf",
            caption="📄 PDF generado con reportlab"
        )
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error PDF: {str(e)[:100]}", parse_mode='Markdown')

# ----- WEB SCRAPING -----
async def handle_scraping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        url = "https://render.com"
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.title.string if soup.title else "Sin título"
        meta_desc = soup.find("meta", attrs={"name": "description"})
        desc = meta_desc["content"] if meta_desc else "No description"
        
        await update.message.reply_text(
            f"🔍 *Scraping de {url}*\n\n"
            f"**Título:** {title[:100]}\n"
            f"**Descripción:** {desc[:150]}\n\n"
            f"✅ BeautifulSoup funcionando correctamente",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error scraping: {str(e)[:100]}", parse_mode='Markdown')

# ----- RENDER Y GITHUB -----
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

# ----- MANEJADOR MENÚ -----
async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "🌐 Render":
        await render_command(update, context)
    elif text == "💻 GitHub":
        await github_command(update, context)
    elif text == "📊 Analizar CSV":
        await handle_csv(update, context)
    elif text == "📄 Generar PDF":
        await handle_pdf(update, context)
    elif text == "🔍 Web Scraping":
        await handle_scraping(update, context)
    elif text == "📈 Ejemplo SQL":
        await update.message.reply_text(
            "```sql\nSELECT * FROM usuarios WHERE activo = 1;\n```",
            parse_mode='Markdown'
        )
    elif text == "🧮 Calculadora":
        await update.message.reply_text("🔢 Escribe: 2+2, sqrt(16), 3*4")
    elif text == "ℹ️ Ayuda":
        await update.message.reply_text(
            "📖 *Funciones:*\n"
            "• CSV: Sube archivo .csv\n"
            "• PDF: Genera reporte\n"
            "• Scraping: Info de páginas\n"
            "• Render/GitHub: Info servicios",
            parse_mode='Markdown'
        )

# ----- CONFIGURACIÓN -----
def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("render", render_command))
    app.add_handler(CommandHandler("github", github_command))
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu))
    app.add_handler(MessageHandler(filters.Document.FileExtension("csv"), handle_csv))
    
    print("=" * 50)
    print("🤖 @experttdata_bot - VERSIÓN COMPLETA")
    print("📊 pandas, BeautifulSoup, reportlab ACTIVOS")
    print("=" * 50)
    
    app.run_polling()

if __name__ == '__main__':
    main()
