#!/usr/bin/env python3
"""
ExpertDataBot - Clon de @ExpertDatabot
Comandos: /start, /myid, /url
"""

import os
import sys
import sqlite3
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ========== CONFIGURACIÓN ==========
# TOKEN FIJO PARA PRUEBAS (luego muévelo a variables)
TOKEN = "8382109200:AAFxY94tHyyRDD5VKn1FXskwaGffmpwxy-Q"
PORT = 8080

# ========== DIAGNÓSTICO INICIAL ==========
print("=" * 60)
print("🤖 EXPERTDATABOT - DIAGNÓSTICO")
print("=" * 60)

# 1. Verificar Python y imports
print(f"🐍 Python: {sys.version.split()[0]}")

try:
    import telegram
    print(f"📦 python-telegram-bot: {telegram.__version__}")
    
    # Verificar que NO estamos usando Updater
    try:
        from telegram.ext import Updater
        print("❌ PELIGRO: 'Updater' está disponible")
        print("   Tu código probablemente usa Updater")
        print("   REEMPLÁZALO por 'Application'")
    except ImportError:
        print("✅ Correcto: 'Updater' NO disponible")
        
    from telegram.ext import Application
    print("✅ 'Application' disponible")
    
except ImportError as e:
    print(f"❌ Error import: {e}")
    print("   Ejecuta: pip install python-telegram-bot==20.7")
    sys.exit(1)

print("=" * 60)

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('expertbot.log')
    ]
)
logger = logging.getLogger(__name__)

# ========== BASE DE DATOS ==========
def init_database():
    """Crear base de datos SQLite"""
    try:
        conn = sqlite3.connect('expert_data.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                username TEXT,
                first_name TEXT,
                join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Base de datos creada: expert_data.db")
        return True
    except Exception as e:
        print(f"❌ Error BD: {e}")
        return False

# ========== COMANDOS ==========
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejar /start"""
    try:
        user = update.effective_user
        
        # Guardar en BD
        conn = sqlite3.connect('expert_data.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO users (user_id, username, first_name)
            VALUES (?, ?, ?)
        ''', (user.id, user.username, user.first_name))
        conn.commit()
        conn.close()
        
        # Mensaje de respuesta
        response = (
            f"✅ *ExpertDataBot Activado*\n\n"
            f"👋 Hola {user.first_name or 'Usuario'}\n"
            f"🆔 Tu ID: `{user.id}`\n\n"
            f"📋 *Comandos disponibles:*\n"
            f"• /start - Iniciar bot\n"
            f"• /myid - Ver tu ID\n"
            f"• /url - Descargar base de datos\n\n"
            f"⚡ _Versión 2.0 - Railway Hosting_"
        )
        
        await update.message.reply_text(response, parse_mode='Markdown')
        print(f"✅ /start respondido a {user.id}")
        
    except Exception as e:
        print(f"❌ Error en /start: {e}")
        await update.message.reply_text("❌ Error interno")

async def cmd_myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejar /myid"""
    try:
        user = update.effective_user
        
        response = (
            f"📋 *INFORMACIÓN DE USUARIO*\n\n"
            f"🆔 *ID:* `{user.id}`\n"
            f"👤 *Nombre:* {user.first_name or 'No disponible'}\n"
            f"📛 *Usuario:* @{user.username or 'No disponible'}\n\n"
            f"⚠️ *Este ID es único e intransferible*"
        )
        
        await update.message.reply_text(response, parse_mode='Markdown')
        print(f"✅ /myid respondido a {user.id}")
        
    except Exception as e:
        print(f"❌ Error en /myid: {e}")
        await update.message.reply_text("❌ Error interno")

async def cmd_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejar /url"""
    try:
        # Asegurar que existe el archivo
        init_database()
        
        filename = f"expert_data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        
        with open('expert_data.db', 'rb') as file:
            await update.message.reply_document(
                document=file,
                filename=filename,
                caption=f"📦 Backup de datos | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
        
        print(f"✅ /url enviado a {update.effective_user.id}")
        
    except Exception as e:
        print(f"❌ Error en /url: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)[:100]}")

# ========== INICIAR BOT ==========
def main():
    """Función principal - VERSIÓN 20.x"""
    print("\n" + "=" * 60)
    print("🚀 INICIANDO BOT EXPERTDATA")
    print("=" * 60)
    
    # 1. Inicializar BD
    print("1. Inicializando base de datos...")
    if not init_database():
        print("❌ No se pudo crear BD")
        return
    
    # 2. Construir aplicación (NUEVA FORMA)
    print("2. Construyendo Application...")
    try:
        # ESTA ES LA PARTE CLAVE - NO USAR Updater
        application = Application.builder().token(TOKEN).build()
        print("   ✅ Application construida")
        
        # 3. Registrar comandos
        print("3. Registrando comandos...")
        application.add_handler(CommandHandler("start", cmd_start))
        application.add_handler(CommandHandler("myid", cmd_myid))
        application.add_handler(CommandHandler("url", cmd_url))
        print("   ✅ Comandos registrados")
        
        # 4. Verificar modo (Railway o local)
        print("4. Configurando modo de ejecución...")
        railway_url = os.environ.get("RAILWAY_STATIC_URL", "")
        
        if railway_url and railway_url.startswith("http"):
            # Modo Railway con webhook
            print(f"   🌐 Modo Railway: {railway_url}")
            
            application.run_webhook(
                listen="0.0.0.0",
                port=PORT,
                url_path=TOKEN,
                webhook_url=f"{railway_url}/{TOKEN}",
                drop_pending_updates=True,
                allowed_updates=Update.ALL_TYPES
            )
        else:
            # Modo local con polling
            print("   🔍 Modo local (polling)")
            
            application.run_polling(
                drop_pending_updates=True,
                allowed_updates=Update.ALL_TYPES,
                poll_interval=1.0,
                timeout=30
            )
        
        print("✅ Bot iniciado correctamente")
        
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO AL INICIAR:")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Mensaje: {str(e)}")
        
        # Diagnóstico específico
        if "Updater" in str(e):
            print("\n🔴 PROBLEMA IDENTIFICADO:")
            print("   Tu código usa 'Updater' que es obsoleto.")
            print("   REEMPLAZA en tu código:")
            print("   - 'Updater' → 'Application'")
            print("   - 'updater.start_polling()' → 'app.run_polling()'")
            print("   - 'updater.idle()' → (eliminar)")
            
        elif "token" in str(e).lower() or "401" in str(e):
            print("\n🔴 PROBLEMA CON TOKEN:")
            print("   Token inválido o expirado.")
            print("   Crea nuevo bot con @BotFather")
            
        elif "import" in str(e).lower():
            print("\n🔴 PROBLEMA CON INSTALACIÓN:")
            print("   requirements.txt debe tener:")
            print("   python-telegram-bot==20.7")

# ========== EJECUCIÓN ==========
if __name__ == "__main__":
    main()
