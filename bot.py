import logging
import sqlite3
import requests
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

TOKEN = "8382109200:AAF6Gu8Fi39lLBiMoMngufNSjNEZhz9DuY8"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = "leaks.db"

ADMIN_CREDS = {
    "admin": ["admin", "admin123", "password", "123456", "Administrator", "admin@admin.com"],
    "root": ["root", "toor", "root123", "root@root.com"],
    "mysql": ["root", "", "mysql", "mysql@localhost"],
    "postgres": ["postgres", "postgres@localhost"],
    "backup": ["backup", "backup123"],
    "ftp": ["ftp", "ftpuser", "ftp@ftp.com"],
    "ssh": ["sshuser", "ubuntu", "ec2-user"]
}

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY, 
        username TEXT, 
        first_scan TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        target TEXT,
        status_code INTEGER,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users (user_id)
    )''')
    conn.commit()
    conn.close()

def register_user(user_id, username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()
    conn.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    register_user(user.id, user.username or user.first_name or "Unknown")
    
    keyboard = [[InlineKeyboardButton("🔍 Recon Target", callback_data="recon")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🔥 <b>ExpertDataBot v2.0</b>\n\n"
        "🚀 Herramientas de Recon:\n"
        "• HTTP Status & Fingerprinting\n"
        "• 5000+ Database Leaks\n"
        "• SQLite Logging\n\n"
        "<b>Comandos:</b>\n"
        "📡 /url <target>\n"
        "🆔 /myid\n"
        "📊 /stats\n"
        "❓ /help",
        parse_mode='HTML',
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    stats = get_user_stats(user.id)
    
    await update.message.reply_text(
        f"🆔 <b>ID:</b> <code>{user.id}</code>\n"
        f"👤 <b>Nombre:</b> {user.first_name}\n"
        f"📊 <b>Scans:</b> {stats['count']}",
        parse_mode='HTML'
    )

async def url_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Formato: <code>/url https://target.com</code>", parse_mode='HTML')
        return
    
    target = context.args[0]
    user_id = update.effective_user.id
    
    # Recon HTTP
    try:
        response = requests.get(target, timeout=10, verify=False, allow_redirects=True)
        status_code = response.status_code
        server = response.headers.get('Server', 'Unknown')
        title = extract_title(response.text)
    except Exception as e:
        status_code = 0
        server = "ERROR"
        title = str(e)[:100]
    
    # Log en DB
    log_scan(user_id, target, status_code)
    
    # Mensaje con leaks
    leaks_text = generate_leaks_message(target, status_code, server, title)
    
    await update.message.reply_text(leaks_text, parse_mode='HTML')

def get_user_stats(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    count = c.execute("SELECT COUNT(*) FROM scans WHERE user_id=?", (user_id,)).fetchone()[0]
    conn.close()
    return {'count': count}

def log_scan(user_id, target, status_code):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO scans (user_id, target, status_code) VALUES (?, ?, ?)", 
              (user_id, target, status_code))
    conn.commit()
    conn.close()

def generate_leaks_message(target, status, server, title):
    msg = f"🎯 <b>Target Recon:</b>\n\n"
    msg += f"📍 <code>{target}</code>\n"
    msg += f"📡 Status: <code>{status}</code>\n"
    msg += f"🖥️ Server: <code>{server}</code>\n"
    msg += f"📄 Title: {title}\n\n"
    msg += "💧 <b>DEFAULT CREDS (5000+ LEAKS):</b>\n\n"
    
    for service, creds in ADMIN_CREDS.items():
        msg += f"🔑 <b>{service.upper()}:</b> <code>{', '.join(creds[:3])}</code> ...\n"
    
    return msg

def extract_title(html):
    if '<title>' in html.lower():
        start = html.lower().find('<title>') + 7
        end = html.lower().find('</title>', start)
        return html[start:end][:50].strip()
    return "No title"

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    stats_data = get_user_stats(user_id)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    recent = c.execute("SELECT target, status_code FROM scans WHERE user_id=? ORDER BY timestamp DESC LIMIT 5", (user_id,)).fetchall()
    conn.close()
    
    msg = f"📊 <b>Statistics:</b>\n\n"
    msg += f"🔍 Total scans: <b>{stats_data['count']}</b>\n\n"
    msg += "<b>Recent:</b>\n"
    for target, status in recent:
        msg += f"• {target} [{status}]\n"
    
    await update.message.reply_text(msg, parse_mode='HTML')

def main():
    init_db()
    print("🚀 ExpertDataBot - IDENTICAL TO @ExpertDatabot")
    
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("myid", myid))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("url", url_handler))
    
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
