 import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===== OBTENER TOKEN =====
# 1. Intenta desde variable de entorno (Railway usa TELEGRAM_TOKEN)
TOKEN = os.environ.get('TELEGRAM_TOKEN')  # <-- CAMBIÉ BOT_TOKEN por TELEGRAM_TOKEN

# 2. Si no está, usa fallback
if not TOKEN:
    TOKEN = os.environ.get('BOT_TOKEN')
    
if not TOKEN:
    print("❌ ERROR: No se encontró TELEGRAM_TOKEN en variables de entorno")
    exit(1)

print(f"✅ Token cargado ({len(TOKEN)} caracteres)")

# Teclado
KEYBOARD = [
    ["🌐 Render", "💻 GitHub"],
    ["📊 Analizar CSV", "📈 Ejemplo SQL"],
    ["🧮 Calculadora", "ℹ️ Ayuda"]
]
REPLY_KEYBOARD = ReplyKeyboardMarkup(KEYBOARD, resize_keyboard=True)

# ===== COMANDOS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

async def render_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌐 *Render.com*\nPlataforma de hosting\n🔗 https://render.com",
        parse_mode='Markdown'
    )

async def github_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💻 *GitHub*\nControl de versiones\n🔗 https://github.com",
        parse_mode='Markdown'
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *Comandos:* /start, /render, /github, /help",
        parse_mode='Markdown'
    )

# ===== MANEJADOR DE BOTONES =====
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    
    # Handler para botones (mensajes de texto)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))
    
    # Iniciar el bot
    print("🤖 Bot iniciando...")
    app.run_polling()

if __name__ == '__main__':
    main()
