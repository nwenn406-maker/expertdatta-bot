import os
import sqlite3
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ========== CONFIGURACIÓN ==========
TOKEN = os.environ.get("BOT_TOKEN", "").strip()
PORT = int(os.environ.get("PORT", 8080))

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== BASE DE DATOS ==========
def init_db():
    """Inicializar base de datos SQLite"""
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY,
                  username TEXT,
                  first_name TEXT,
                  created_at TEXT)''')
    conn.commit()
    conn.close()
    logger.info("✅ Base de datos inicializada")

# ========== COMANDOS ==========
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejar comando /start"""
    user = update.effective_user
    
    # Guardar en BD
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?)',
              (user.id, user.username, user.first_name, 
               datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
    
    await update.message.reply_text(
        f"✅ *Bot ExpertData activado*\n\n"
        f"👋 Hola {user.first_name}\n"
        f"🆔 Tu ID: `{user.id}`\n\n"
        f"📋 *Comandos:*\n"
        f"• /start - Iniciar bot\n"
        f"• /myid - Ver tu ID\n"
        f"• /url - Descargar base de datos\n\n"
        f"⚡ _Hosteado en Railway_",
        parse_mode='Markdown'
    )

async def myid_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejar comando /myid"""
    user = update.effective_user
    await update.message.reply_text(
        f"🆔 *TU ID:* `{user.id}`\n"
        f"👤 *Nombre:* {user.first_name}\n"
        f"📛 *Usuario:* @{user.username if user.username else 'N/A'}",
        parse_mode='Markdown'
    )

async def url_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejar comando /url"""
    try:
        init_db()  # Asegurar que existe
        with open('bot_data.db', 'rb') as f:
            await update.message.reply_document(
                document=f,
                filename=f"database_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db",
                caption=f"📦 Backup: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

# ========== INICIAR BOT ==========
def main():
    """Función principal"""
    # Verificar token
    if not TOKEN:
        logger.error("❌ ERROR: BOT_TOKEN no configurado")
        print("Configura BOT_TOKEN en Railway Variables")
        return
    
    logger.info(f"🚀 Iniciando bot con token: {TOKEN[:15]}...")
    
    # Inicializar BD
    init_db()
    
    # Crear aplicación (NUEVA forma en versión 20.x)
    application = Application.builder().token(TOKEN).build()
    
    # Añadir handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("myid", myid_command))
    application.add_handler(CommandHandler("url", url_command))
    
    # Verificar si estamos en Railway
    railway_url = os.environ.get("RAILWAY_STATIC_URL")
    
    if railway_url:
        # Modo webhook para Railway
        logger.info(f"🌐 Usando webhook: {railway_url}")
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN,
            webhook_url=f"{railway_url}/{TOKEN}",
            drop_pending_updates=True
        )
    else:
        # Modo polling (para desarrollo)
        logger.info("🔍 Usando polling")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
