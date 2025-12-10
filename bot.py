import os
import sqlite3
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Configuración
TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")
PORT = int(os.environ.get("PORT", 8000))

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Base de datos
def init_db():
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY,
                  username TEXT,
                  first_name TEXT,
                  date_added TEXT)''')
    conn.commit()
    conn.close()

# COMANDOS
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        f"✅ *Bot activado*\n\n"
        f"👋 Hola {user.first_name}\n"
        f"🆔 Tu ID: `{user.id}`\n\n"
        f"📋 **Comandos:**\n"
        f"/start - Iniciar bot\n"
        f"/url - Descargar base de datos\n"
        f"/myid - Ver tu ID\n\n"
        f"⚡ _Hosteado en Railway_",
        parse_mode='Markdown'
    )

async def url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open('bot_data.db', 'rb') as f:
            await update.message.reply_document(
                document=f,
                filename=f"database_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db",
                caption=f"📦 Backup: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"🆔 *TU ID:* `{user.id}`\n"
        f"👤 *Nombre:* {user.first_name}\n"
        f"📛 *Usuario:* @{user.username if user.username else 'N/A'}",
        parse_mode='Markdown'
    )

def main():
    init_db()
    
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("url", url))
    app.add_handler(CommandHandler("myid", myid))
    
    if WEBHOOK_URL:
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN,
            webhook_url=f"{WEBHOOK_URL}/{TOKEN}"
        )
        print("🚀 Bot en modo WEBHOOK")
    else:
        app.run_polling()
        print("🔍 Bot en modo POLLING")

if __name__ == '__main__':
    main()
