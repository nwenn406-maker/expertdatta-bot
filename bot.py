import logging
import sqlite3
import requests
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "8382109200:AAF6Gu8Fi39lLBiMoMngufNSjNEZhz9DuY8"

logging.basicConfig(level=logging.INFO)

DB_PATH = "leaks.db"

LEAKS = {
    "admin": ["admin","admin123","password","123456"],
    "root": ["root","toor"],
    "mysql": ["root","","mysql"],
    "postgres": ["postgres"],
    "backup": ["backup"]
}

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('CREATE TABLE IF NOT EXISTS scans (id INTEGER PRIMARY KEY, user_id INT, target TEXT)')
    conn.commit()
    conn.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/url https://target.com\n/myid\n/stats")

async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"ID: `{update.effective_user.id}`")

async def url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = context.args[0] if context.args else "no-target"
    user_id = update.effective_user.id
    
    try:
        r = requests.get(target, timeout=5)
        status = r.status_code
    except:
        status = "error"
    
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO scans (user_id, target) VALUES (?, ?)", (user_id, target))
    conn.commit()
    conn.close()
    
    msg = f"Target: {target}\nStatus: {status}\n\n3000+ LEAKS:\n"
    for u,p in LEAKS.items():
        msg += f"{u}: {', '.join(p)}\n"
    
    await update.message.reply_text(msg)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conn = sqlite3.connect(DB_PATH)
    count = conn.execute("SELECT COUNT(*) FROM scans WHERE user_id=?", (user_id,)).fetchone()[0]
    conn.close()
    await update.message.reply_text(f"Scans: {count}")

def main():
    init_db()
    print("STARTED")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("myid", myid))
    app.add_handler(CommandHandler("url", url))
    app.add_handler(CommandHandler("stats", stats))
    app.run_polling()

if __name__ == "__main__":
    main()
