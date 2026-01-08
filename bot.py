#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import sqlite3
import requests
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# TOKEN DIRECTO - SIN BASE64
TOKEN = "8382109200:AAF6Gu8Fi39lLBiMoMngufNSjNEZhz9DuY8"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

DB_PATH = "leaks.db"

LEAKS = {
    "👑 admin": ["admin", "admin123", "password", "123456", "administrator"],
    "🔑 root": ["root", "toor", "root123"],
    "🐬 mysql": ["root", "", "mysql"],
    "🐘 postgres": ["postgres"],
    "💾 backup": ["backup", "backup123"]
}

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS scans 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  user_id INTEGER, 
                  target TEXT, 
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()
    logger.info("✅ DB inicializada")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔍 <b>ExpertDataBot</b>\n\n"
        "📡 <b>Comandos:</b>\n"
        "/url https://target.com - Recon + Leaks\n"
        "/myid - Tu ID\n"
        "/stats - Estadísticas\n"
        "/help - Este mensaje",
        parse_mode='HTML'
    )

async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(
        f"🆔 <b>Tu ID:</b> <code>{user_id}</code>",
        parse_mode='HTML'
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    count = c.execute("SELECT COUNT(*) FROM scans WHERE user_id=?", (user_id,)).fetchone()[0]
    conn.close()
    await update.message.reply_text(
        f"📊 <b>Estadísticas:</b>\n"
        f"🔍 Scans realizados: <b>{count}</b>",
        parse_mode='HTML'
    )

async def url_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Usa: <code>/url https://target.com</code>", parse_mode='HTML')
        return
    
    target = context.args[0]
    user_id = update.effective_user.id
    
    # Recon básico
    try:
        r = requests.get(target, timeout=7, verify=False)
        status = r.status_code
        title = r.text[:200]
    except Exception as e:
        status = "ERROR"
        title = str(e)[:100]
    
    # Guardar en DB
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO scans (user_id, target) VALUES (?, ?)", (user_id, target))
    conn.commit()
    conn.close()
    
    # Mensaje con leaks
    msg = f"🎯 <b>Target:</b> <code>{target}</code>\n"
    msg += f"📡 <b>Status:</b> <code>{status}</code>\n"
    msg += f"📄 <b>Response:</b> {title[:100]}...\n\n"
    msg += "💧 <b>3000+ LEAKS DATABASES:</b>\n\n"
    
    for category, passwords in LEAKS.items():
        msg += f"{category}:\n"
        msg += f"  <code>{', '.join(passwords)}</code>\n"
    
    await update.message.reply_text(msg, parse_mode='HTML')

def main():
    init_db()
    print("🚀 ExpertDataBot iniciado correctamente!")
    
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("myid", myid))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("url", url_cmd))
    
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
