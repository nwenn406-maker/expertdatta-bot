import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Configurar
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get('TELEGRAM_TOKEN', '8382109200:AAFXY94thyyRDDSVKnIFXskwa6ffmpwxy-Q')

# Teclado
KEYBOARD = [
    ["🌐 Render", "💻 GitHub"],
    ["📊 Analizar CSV", "📈 Ejemplo SQL"],
    ["🧮 Calculadora", "ℹ️ Ayuda"]
]
REPLY_KEYBOARD = ReplyKeyboardMarkup(KEYBOARD, resize_keyboard=True)

# ===== COMANDOS =====
async def start(update: Update, context):
    """Maneja /start"""
    user = update.effective_user
    await update.message.reply_text(
        f"👋 Hola {user.first_name}!\n\n"
        "🚀 *@experttdata_bot - Expert Data Assistant*\n\n"
        "✅ *Servicios conectados:*\n"
        "• 🌐 **Render**: https://render.com\n"
        "• 💻 **GitHub**: https://github.com\n\n"
        "🔧 *Usa los botones:*",
        parse_mode='Markdown',
        reply_markup=REPLY_KEYBOARD
    )

async def render_cmd(update: Update, context):
    await update.message.reply_text(
        "🌐 *Render.com*\nPlataforma de hosting\n🔗 https://render.com",
        parse_mode='Markdown'
    )

async def github_cmd(update: Update, context):
    await update.message.reply_text(
        "💻 *GitHub*\nControl de versiones\n🔗 https://github.com",
        parse_mode='Markdown'
    )

async def help_cmd(update: Update, context):
    await update.message.reply_text(
        "📖 *Comandos:* /start, /render, /github, /help",
        parse_mode='Markdown'
    )

# ===== MANEJADOR DE BOTONES =====
async def handle_buttons(update: Update, context):
    text = update.message.text
    
    if text == "🌐 Render":
        await render_cmd(update, context)
    elif text == "💻 GitHub":
        await github_cmd(update, context)
    elif text == "📊 Analizar CSV":
        await update.message.reply_text("📎 Envía un archivo .csv", parse_mode='Markdown')
    elif text == "📈 Ejemplo SQL":
        await update.message.reply_text("```sql\nSELECT * FROM data;\n```", parse_mode='Markdown')
    elif text == "🧮 Calculadora":
        await update.message.reply_text("🔢 Escribe: 2+2, 3*4, sqrt(16)", parse_mode='Markdown')
    elif text == "ℹ️ Ayuda":
        await help_cmd(update, context)

# ===== PRINCIPAL =====
def main():
    """Inicia el bot con polling"""
    app = Application.builder().token(TOKEN).build()
    
    # Comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("render", render_cmd))
    app.add_handler(CommandHandler("github", github_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    
    # Mensajes de texto (botones)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))
    
    # Archivos CSV
    app.add_handler(MessageHandler(filters.Document.FileExtension("csv"), 
        lambda u,c: u.message.reply_text("📊 Función CSV activa")))
    
    logger.info("🤖 @experttdata_bot iniciando...")
    print("=" * 50)
    print("🚀 Bot con POLLING (no webhook)")
    print(f"🔑 Token: {TOKEN[:10]}...")
    print("📡 Esperando mensajes de Telegram...")
    print("=" * 50)
    
    # Iniciar polling
    app.run_polling(allowed_updates="", drop_pending_updates=True)

if __name__ == '__main__':
    main()
