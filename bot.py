import os
import sqlite3
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ========== CONFIGURACIÓN ==========
TOKEN = "8382109200:AAFxY94tHyyRDD5VKn1FXskwaGffmpwxy-Q"
PORT = 8080

print("=" * 50)
print("🤖 BOT INICIANDO - VERSIÓN 20.x")
print("=" * 50)

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== BASE DE DATOS ==========
def crear_db():
    conn = sqlite3.connect('datos.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, user_id INTEGER, nombre TEXT)')
    conn.commit()
    conn.close()
    print("✅ Base de datos lista")

# ========== COMANDOS ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f"✅ Bot activo! Hola {user.first_name}")

async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f"🆔 Tu ID: {user.id}")

async def url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📦 Base de datos (próximamente)")

# ========== FUNCIÓN PRINCIPAL ==========
def main():
    print("🚀 Iniciando bot...")
    crear_db()
    
    try:
        # ✅ CORRECTO: Application (NUEVA forma)
        app = Application.builder().token(TOKEN).build()
        
        # Añadir comandos
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("myid", myid))
        app.add_handler(CommandHandler("url", url))
        
        print("✅ Application creada correctamente")
        
        # Iniciar
        railway_url = os.environ.get("RAILWAY_STATIC_URL", "")
        
        if railway_url:
            print(f"🌐 Usando webhook: {railway_url}")
            app.run_webhook(
                listen="0.0.0.0",
                port=PORT,
                url_path=TOKEN,
                webhook_url=f"{railway_url}/{TOKEN}"
            )
        else:
            print("🔍 Usando polling...")
            app.run_polling()
            
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}")
        print(f"📄 Mensaje: {e}")
        
        # Si el error menciona 'Updater', tu código todavía lo usa
        if "Updater" in str(e):
            print("\n⚠️  ¡TU CÓDIGO TODAVÍA USA 'UPDATER'!")
            print("   Busca y elimina 'Updater' de tu código")

if __name__ == "__main__":
    main()
