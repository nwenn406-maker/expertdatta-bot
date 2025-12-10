import os
import sqlite3
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ========== CONFIGURACIÓN ==========
# ⚠️ Token directamente en código (solo para pruebas)
TOKEN = "8382109200:AAFxY94tHyyRDD5VKn1FXskwaGffmpwxy-Q"
PORT = 8080

print("=" * 50)
print("🚀 EXPERTDATABOT INICIANDO")
print("=" * 50)
print(f"🔑 Token: {TOKEN[:20]}...")
print(f"🐍 Python: {os.sys.version[:20]}...")

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),  # Para ver logs en Railway
        logging.FileHandler('bot.log')  # Para guardar logs
    ]
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
                      join_date TEXT)''')
        conn.commit()
        conn.close()
        logger.info("✅ Base de datos lista")
        return True
    except Exception as e:
        logger.error(f"❌ Error BD: {e}")
        return False

# ========== COMANDOS ==========
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    try:
        user = update.effective_user
        logger.info(f"Usuario /start: {user.id} - {user.first_name}")
        
        # Guardar en BD
        conn = sqlite3.connect('bot_data.db')
        c = conn.cursor()
        c.execute('INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?)',
                  (user.id, user.username or "", user.first_name or "",
                   datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
        
        await update.message.reply_text(
            f"🤖 *ExpertDataBot*\n\n"
            f"👋 Hola {user.first_name or 'Usuario'}\n"
            f"🆔 ID: `{user.id}`\n\n"
            f"📋 *Comandos:*\n"
            f"/start - Iniciar\n"
            f"/myid - Ver ID\n"
            f"/url - Descargar DB\n\n"
            f"⚡ Railway",
            parse_mode='Markdown'
        )
        return True
    except Exception as e:
        logger.error(f"Error /start: {e}")
        return False

async def myid_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /myid"""
    try:
        user = update.effective_user
        await update.message.reply_text(
            f"🆔 *TU ID:* `{user.id}`\n"
            f"👤 *Nombre:* {user.first_name or 'N/A'}\n"
            f"📛 *Usuario:* @{user.username or 'N/A'}\n\n"
            f"⚠️ Guarda este ID",
            parse_mode='Markdown'
        )
        return True
    except Exception as e:
        logger.error(f"Error /myid: {e}")
        return False

async def url_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /url"""
    try:
        # Asegurar que existe la BD
        init_db()
        
        filename = f"expert_db_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        
        with open('bot_data.db', 'rb') as f:
            await update.message.reply_document(
                document=f,
                filename=filename,
                caption=f"📦 Backup: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
        logger.info(f"✅ DB enviada a {update.effective_user.id}")
        return True
    except Exception as e:
        logger.error(f"❌ Error /url: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")
        return False

# ========== INICIAR BOT ==========
def main():
    """Función principal"""
    logger.info("=" * 50)
    logger.info("🚀 INICIANDO BOT EXPERTDATA")
    logger.info("=" * 50)
    
    # 1. Inicializar BD
    if not init_db():
        logger.error("❌ No se pudo inicializar BD")
        return
    
    # 2. Verificar importaciones
    try:
        # Forzar import para verificar
        from telegram import __version__ as tg_version
        logger.info(f"📦 python-telegram-bot: {tg_version}")
    except ImportError as e:
        logger.error(f"❌ No se puede importar telegram: {e}")
        logger.error("   Verifica requirements.txt: python-telegram-bot==20.7")
        return
    
    # 3. Crear aplicación
    try:
        logger.info("🔄 Creando Application...")
        app = Application.builder().token(TOKEN).build()
        logger.info("✅ Application creada")
        
        # 4. Añadir comandos
        app.add_handler(CommandHandler("start", start_cmd))
        app.add_handler(CommandHandler("myid", myid_cmd))
        app.add_handler(CommandHandler("url", url_cmd))
        logger.info("✅ Comandos configurados")
        
        # 5. Verificar Railway
        railway_url = os.environ.get("RAILWAY_STATIC_URL", "")
        
        if railway_url:
            # Modo webhook
            logger.info(f"🌐 Webhook URL: {railway_url}")
            logger.info(f"🔌 Puerto: {PORT}")
            
            app.run_webhook(
                listen="0.0.0.0",
                port=PORT,
                url_path=TOKEN,
                webhook_url=f"{railway_url}/{TOKEN}",
                drop_pending_updates=True,
                allowed_updates=Update.ALL_TYPES
            )
        else:
            # Modo polling
            logger.info("🔍 Usando modo polling...")
            app.run_polling(
                drop_pending_updates=True,
                allowed_updates=Update.ALL_TYPES,
                poll_interval=1.0,
                timeout=30
            )
            
    except Exception as e:
        logger.error(f"❌ ERROR CRÍTICO: {type(e).__name__}")
        logger.error(f"📄 Detalle: {e}")
        logger.error("\n🔧 SOLUCIÓN:")
        logger.error("1. Verifica el token")
        logger.error("2. requirements.txt debe tener: python-telegram-bot==20.7")
        logger.error("3. No uses 'Updater' en el código")

if __name__ == "__main__":
    main()
