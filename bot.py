import os
import sqlite3
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ========== CONFIGURACIÓN ==========
# ⚠️ ADVERTENCIA: No pongas tokens en el código en producción
# ⚠️ WARNING: Don't put tokens in code for production
TOKEN = "8382109200:AAFxY94tHyyRDD5VKn1FXskwaGffmpwxy-Q"  # Tu token aquí
PORT = int(os.environ.get("PORT", 8080))

# Validar token
if not TOKEN:
    print("❌ ERROR: Token no configurado")
    exit(1)

print(f"✅ Token configurado: {TOKEN[:15]}...")

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== BASE DE DATOS ==========
def init_db():
    """Inicializar base de datos SQLite"""
    conn = sqlite3.connect('expert_data.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY,
                  username TEXT,
                  first_name TEXT,
                  join_date TEXT)''')
    
    conn.commit()
    conn.close()
    logger.info("Base de datos lista")

# ========== COMANDOS ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start - Iniciar bot"""
    user = update.effective_user
    
    # Registrar en BD
    conn = sqlite3.connect('expert_data.db')
    c = conn.cursor()
    c.execute('''INSERT OR IGNORE INTO users 
                 (user_id, username, first_name, join_date)
                 VALUES (?, ?, ?, ?)''',
              (user.id, user.username, user.first_name,
               datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
    
    await update.message.reply_text(
        f"🤖 **ExpertDataBot Activado**\n\n"
        f"👋 Hola {user.first_name}\n"
        f"🆔 Tu ID: `{user.id}`\n\n"
        f"📋 **Comandos:**\n"
        f"/start - Iniciar bot\n"
        f"/myid - Mostrar tu ID\n"
        f"/url - Extraer base de datos\n\n"
        f"⚡ _Hosteado en Railway_",
        parse_mode='Markdown'
    )

async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /myid - Mostrar ID de usuario"""
    user = update.effective_user
    
    await update.message.reply_text(
        f"📋 **INFORMACIÓN DE USUARIO**\n\n"
        f"🆔 **ID:** `{user.id}`\n"
        f"👤 **Nombre:** {user.first_name}\n"
        f"📛 **Usuario:** @{user.username if user.username else 'N/A'}\n\n"
        f"⚠️ _Este ID es único y permanente_",
        parse_mode='Markdown'
    )

async def url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /url - Extraer base de datos"""
    user = update.effective_user
    
    try:
        with open('expert_data.db', 'rb') as db_file:
            await update.message.reply_document(
                document=db_file,
                filename=f"expert_data_{datetime.now().strftime('%Y%m%d')}.db",
                caption=f"📦 Backup: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
        logger.info(f"Base de datos enviada a {user.id}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

# ========== INICIAR BOT ==========
def main():
    """Función principal - NUEVA forma en versión 20.x"""
    
    # Inicializar BD
    init_db()
    
    try:
        # 1. CREAR APLICACIÓN (NUEVA FORMA - NO Updater)
        print("🔄 Creando Application...")
        application = Application.builder().token(TOKEN).build()
        
        # 2. AÑADIR COMANDOS
        print("📝 Configurando comandos...")
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("myid", myid))
        application.add_handler(CommandHandler("url", url))
        
        # 3. OBTENER CONFIGURACIÓN RAILWAY
        railway_url = os.environ.get("RAILWAY_STATIC_URL", "")
        
        if railway_url:
            # MODO WEBHOOK (Para Railway)
            print(f"🌐 Configurando webhook: {railway_url}")
            
            application.run_webhook(
                listen="0.0.0.0",
                port=PORT,
                url_path=TOKEN,
                webhook_url=f"{railway_url}/{TOKEN}",
                drop_pending_updates=True
            )
        else:
            # MODO POLLING (Para desarrollo/local)
            print("🔍 Iniciando en modo polling...")
            application.run_polling(
                drop_pending_updates=True,
                allowed_updates=Update.ALL_TYPES
            )
            
        print("✅ Bot iniciado correctamente")
        
    except Exception as e:
        print(f"❌ Error al iniciar bot: {type(e).__name__}")
        print(f"📄 Detalle: {e}")
        print("\n🔧 SOLUCIONES:")
        print("1. Verifica que el token sea correcto")
        print("2. Usa python-telegram-bot==20.7 en requirements.txt")
        print("3. No uses 'Updater' en el código")

if __name__ == "__main__":
    main()
