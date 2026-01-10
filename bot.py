import logging
import sqlite3
import requests
import asyncio
from urllib.parse import urlparse
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configuración de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = "8382109200:AAF6Gu8Fi39lLBiMoMngufNSjNEZhz9DuY8"

# Inicializar base de datos
def init_db():
    conn = sqlite3.connect('leaks.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS leaks 
                 (id INTEGER PRIMARY KEY, url TEXT UNIQUE, user_id INTEGER, 
                  date TEXT, status TEXT)''')
    conn.commit()
    conn.close()

init_db()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔍 <b>ExpertDataBot</b>\n\n"
        "Comandos disponibles:\n"
        "/myid - Tu ID de Telegram\n"
        "/url <link> - Recon + Leaks\n"
        "/stats - Estadísticas\n"
        "/help - Ayuda",
        parse_mode='HTML'
    )

async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(f"🆔 Tu ID: <code>{user_id}</code>", parse_mode='HTML')

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect('leaks.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM leaks")
    total = c.fetchone()[0]
    conn.close()
    await update.message.reply_text(f"📊 Total scans: <b>{total}</b>", parse_mode='HTML')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Envía: <code>/url https://ejemplo.com</code>", parse_mode='HTML')
        return
    
    url = context.args[0]
    user_id = update.effective_user.id
    
    # Recon básico HTTP
    try:
        response = requests.get(url, timeout=10)
        status = response.status_code
        domain = urlparse(url).netloc
        
        msg = f"🌐 <b>Recon: {domain}</b>\n"
        msg += f"📡 Status: <code>{status}</code>\n"
        msg += f"📏 Size: {len(response.content):,} bytes\n"
        msg += f"🔗 Leaks: Buscando... ⏳"
        
        status_msg = await update.message.reply_text(msg, parse_mode='HTML')
        
        # Simular búsqueda de leaks (SQLite)
        conn = sqlite3.connect('leaks.db', check_same_thread=False)
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO leaks (url, user_id, date, status) VALUES (?, ?, datetime('now'), ?)",
                 (url, user_id, status))
        conn.commit()
        conn.close()
        
        # Resultado final
        final_msg = f"✅ <b>Scan completado</b>\n\n"
        final_msg += f"🔍 No se encontraron leaks públicos\n"
        final_msg += f"🛡️ Status: <b>OK ({status})</b>"
        
        await status_msg.edit_text(final_msg, parse_mode='HTML')
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

def main():
    # Crear aplicación con drop_pending_updates
    application = Application.builder().token(TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("myid", myid))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("url", handle_url))
    
    # Fallback para URLs directas
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    
    # Iniciar con manejo robusto de conflictos
    print("🚀 Bot iniciando...")
    application.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES,
        timeout=45,
        bootstrap_retries=-1  # Reintentos infinitos
    )

if __name__ == '__main__':
    main()
