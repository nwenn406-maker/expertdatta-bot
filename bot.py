import os
import sqlite3
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ========== CONFIGURACIÓN ==========
TOKEN = os.environ.get("BOT_TOKEN", "").strip()

# Validar token
if not TOKEN:
    print("❌ ERROR: BOT_TOKEN no configurado")
    print("Configura en Railway: BOT_TOKEN = tu_token")
    exit(1)

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== BASE DE DATOS ==========
def init_db():
    """Inicializar base de datos"""
    try:
        conn = sqlite3.connect('bot_data.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (user_id INTEGER PRIMARY KEY,
                      username TEXT,
                      first_name TEXT,
                      created_at TEXT)''')
        conn.commit()
        conn.close()
        logger.info("✅ Base de datos lista")
    except Exception as e:
        logger.error(f"❌ Error BD: {e}")

# ========== COMANDOS ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    try:
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
            f"✅ *Bot ExpertData*\n\n"
            f"👋 Hola {user.first_name}\n"
            f"🆔 ID: `{user.id}`\n\n"
            f"📋 Comandos:\n"
            f"/start - Iniciar\n"
            f"/myid - Ver ID\n"
            f"/url - Descargar DB\n\n"
            f"⚡ Railway Hosting",
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error en /start: {e}")

async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /myid"""
    try:
        user = update.effective_user
        await update.message.reply_text(
            f"🆔 *TU ID:* `{user.id}`\n"
            f"👤 *Nombre:* {user.first_name}\n"
            f"📛 *Usuario:* @{user.username if user.username else 'N/A'}",
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error en /myid: {e}")

async def url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /url"""
    try:
        # Crear archivo si no existe
        init_db()
        
        with open('bot_data.db', 'rb') as f:
            await update.message.reply_document(
                document=f,
                filename=f"database_{datetime.now().strftime('%Y%m%d')}.db",
                caption=f"📦 Backup: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

# ========== MAIN ==========
def main():
    """Función principal"""
    logger.info("🚀 Iniciando bot...")
    
    # Inicializar BD
    init_db()
    
    try:
        # Crear aplicación
        application = Application.builder().token(TOKEN).build()
        
        # Handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("myid", myid))
        application.add_handler(CommandHandler("url", url))
        
        # Obtener URL de Railway
        railway_url = os.environ.get("RAILWAY_STATIC_URL", "")
        
        if railway_url:
            # Modo webhook (Railway)
            logger.info(f"🌐 Webhook: {railway_url}")
            port = int(os.environ.get("PORT", 8080))
            
            application.run_webhook(
                listen="0.0.0.0",
                port=port,
                url_path=TOKEN,
                webhook_url=f"{railway_url}/{TOKEN}",
                drop_pending_updates=True
            )
        else:
            # Modo polling (local)
            logger.info("🔍 Modo polling")
            application.run_polling(
                drop_pending_updates=True,
                allowed_updates=Update.ALL_TYPES
            )
            
    except Exception as e:
        logger.error(f"❌ Error fatal: {e}")
        print(f"\n🔧 SOLUCIÓN: Verifica que:")
        print("1. El token es válido")
        print("2. requirements.txt tiene: python-telegram-bot==20.7")
        print("3. No hay errores de sintaxis")

if __name__ == "__main__":
    main()
