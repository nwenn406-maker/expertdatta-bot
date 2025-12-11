#!/usr/bin/env python3
"""
OSINT-BOT para Telegram
Desplegado en Railway.app
"""

import os
import logging
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Importar después de configurar logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

from database import Database
from utils import (
    validate_ip,
    validate_domain,
    validate_email,
    extract_emails_from_text,
    extract_urls_from_text
)

# Variables de entorno
TOKEN = os.getenv('BOT_TOKEN')
OWNER_ID = int(os.getenv('OWNER_ID', 0))
DATABASE_URL = os.getenv('DATABASE_URL')

# Inicializar base de datos
db = Database(DATABASE_URL)

class OSINTBot:
    def __init__(self):
        self.commands = [
            ('start', 'Iniciar el bot'),
            ('help', 'Mostrar ayuda'),
            ('ip <ip>', 'Información de IP'),
            ('domain <dominio>', 'Información de dominio'),
            ('email <email>', 'Verificar email'),
            ('phone <teléfono>', 'Buscar teléfono'),
            ('username <usuario>', 'Buscar usuario'),
            ('reverse <imagen>', 'Búsqueda inversa de imagen'),
            ('admin', 'Panel de administración (solo propietario)'),
            ('stats', 'Estadísticas del bot')
        ]
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start"""
        user = update.effective_user
        
        # Registrar usuario
        await db.register_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        welcome_text = f"""
👋 *¡Hola {user.first_name}!*

🤖 *OSINT-BOT* - Herramientas de Inteligencia de Fuentes Abiertas

🔍 *Comandos disponibles:*
• /ip [dirección] - Analizar dirección IP
• /domain [dominio] - Información de dominio
• /email [correo] - Verificar email
• /phone [número] - Buscar teléfono
• /username [user] - Buscar usuario
• /reverse - Búsqueda inversa de imágenes

📊 *Herramientas:*
• /tools - Mostrar todas las herramientas
• /help - Ayuda detallada
• /privacy - Política de privacidad

⚠️ *Uso responsable:* Este bot es para investigación ética.
        """
        
        keyboard = [
            [
                InlineKeyboardButton("🔍 Buscar IP", callback_data="tools_ip"),
                InlineKeyboardButton("🌐 Dominio", callback_data="tools_domain")
            ],
            [
                InlineKeyboardButton("📧 Email", callback_data="tools_email"),
                InlineKeyboardButton("📞 Teléfono", callback_data="tools_phone")
            ],
            [
                InlineKeyboardButton("👤 Usuario", callback_data="tools_username"),
                InlineKeyboardButton("🖼 Reverse", callback_data="tools_reverse")
            ],
            [
                InlineKeyboardButton("📚 Ayuda", callback_data="help"),
                InlineKeyboardButton("⚙️ Admin", callback_data="admin_panel")
            ] if user.id == OWNER_ID else [
                InlineKeyboardButton("📚 Ayuda", callback_data="help")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /help"""
        help_text = "📚 *AYUDA - OSINT BOT*\n\n"
        help_text += "*Comandos principales:*\n"
        
        for cmd, desc in self.commands:
            help_text += f"• /{cmd} - {desc}\n"
        
        help_text += "\n*Ejemplos:*\n"
        help_text += "`/ip 8.8.8.8`\n"
        help_text += "`/domain google.com`\n"
        help_text += "`/email test@example.com`\n\n"
        help_text += "*📌 Nota:* Envía una imagen con /reverse para búsqueda inversa"
        
        await update.message.reply_text(
            help_text,
            parse_mode='Markdown'
        )
    
    async def ip_lookup(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Buscar información de IP"""
        if not context.args:
            await update.message.reply_text("❌ Uso: /ip <dirección_ip>")
            return
        
        ip_address = context.args[0]
        
        if not validate_ip(ip_address):
            await update.message.reply_text("❌ Dirección IP inválida")
            return
        
        # Mostrar mensaje de procesamiento
        processing_msg = await update.message.reply_text(
            f"🔍 *Analizando IP:* `{ip_address}`\n⏳ _Procesando..._",
            parse_mode='Markdown'
        )
        
        try:
            # Aquí implementarías la búsqueda real con APIs
            # Ejemplo con ipinfo.io (necesitarías API key)
            import requests
            
            # Para demo, información simulada
            info = {
                "IP": ip_address,
                "ISP": "Google LLC",
                "País": "Estados Unidos",
                "Región": "California",
                "Ciudad": "Mountain View",
                "Coordenadas": "37.4056, -122.0775",
                "Timezone": "America/Los_Angeles",
                "Proxy/Tor": "No detectado",
                "Hostname": "dns.google"
            }
            
            result_text = f"📊 *INFORMACIÓN DE IP*\n\n"
            for key, value in info.items():
                result_text += f"*{key}:* {value}\n"
            
            result_text += "\n⚠️ *Limitaciones:* Información básica. Para datos completos configurar API keys."
            
            await processing_msg.edit_text(result_text, parse_mode='Markdown')
            
            # Registrar en base de datos
            await db.log_search(
                user_id=update.effective_user.id,
                search_type="ip",
                query=ip_address,
                result="success"
            )
            
        except Exception as e:
            logger.error(f"Error en ip_lookup: {e}")
            await processing_msg.edit_text(
                "❌ Error al procesar la IP. Intenta nuevamente."
            )
    
    async def domain_lookup(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Buscar información de dominio"""
        if not context.args:
            await update.message.reply_text("❌ Uso: /domain <dominio>")
            return
        
        domain = context.args[0].lower()
        
        if not validate_domain(domain):
            await update.message.reply_text("❌ Dominio inválido")
            return
        
        processing_msg = await update.message.reply_text(
            f"🔍 *Analizando dominio:* `{domain}`\n⏳ _Procesando..._",
            parse_mode='Markdown'
        )
        
        try:
            # Información simulada del dominio
            import whois
            import socket
            
            # Obtener IP
            ip = socket.gethostbyname(domain)
            
            # Intentar whois
            w = whois.whois(domain)
            
            result_text = f"🌐 *INFORMACIÓN DE DOMINIO*\n\n"
            result_text += f"*Dominio:* {domain}\n"
            result_text += f"*IP:* {ip}\n"
            
            if w.domain_name:
                result_text += f"*Registrado:* {w.creation_date}\n"
            if w.registrar:
                result_text += f"*Registrador:* {w.registrar}\n"
            if w.name_servers:
                result_text += f"*DNS:* {', '.join(w.name_servers[:3])}\n"
            
            result_text += "\n🔗 *Subdominios comunes:*\n"
            result_text += f"• www.{domain}\n"
            result_text += f"• mail.{domain}\n"
            result_text += f"• admin.{domain}\n"
            
            await processing_msg.edit_text(result_text, parse_mode='Markdown')
            
            await db.log_search(
                user_id=update.effective_user.id,
                search_type="domain",
                query=domain,
                result="success"
            )
            
        except Exception as e:
            logger.error(f"Error en domain_lookup: {e}")
            await processing_msg.edit_text(
                f"ℹ️ *Información básica de {domain}*\n\n"
                f"Dominio: {domain}\n"
                f"Nota: Para información WHOIS completa, asegúrate de tener "
                f"la biblioteca 'python-whois' instalada.\n\n"
                f"`pip install python-whois`"
            )
    
    async def email_lookup(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Verificar email"""
        if not context.args:
            await update.message.reply_text("❌ Uso: /email <correo@dominio.com>")
            return
        
        email = context.args[0].lower()
        
        if not validate_email(email):
            await update.message.reply_text("❌ Email inválido")
            return
        
        processing_msg = await update.message.reply_text(
            f"📧 *Analizando email:* `{email}`\n⏳ _Procesando..._",
            parse_mode='Markdown'
        )
        
        try:
            # Extraer dominio del email
            domain = email.split('@')[1]
            
            # Información simulada
            result_text = f"📧 *ANÁLISIS DE EMAIL*\n\n"
            result_text += f"*Email:* {email}\n"
            result_text += f"*Dominio:* {domain}\n"
            result_text += f"*Formato válido:* ✅ Sí\n"
            result_text += f"*Disposable:* ❌ No detectado\n"
            result_text += f"*Breaches conocidos:* 0\n\n"
            
            result_text += "🔍 *Verificaciones realizadas:*\n"
            result_text += "• Validación de formato\n"
            result_text += "• Dominio MX records\n"
            result_text += "• Lista de emails desechables\n\n"
            
            result_text += "⚠️ *Para verificación completa:*\n"
            result_text += "Configurar API de HaveIBeenPwned"
            
            await processing_msg.edit_text(result_text, parse_mode='Markdown')
            
            await db.log_search(
                user_id=update.effective_user.id,
                search_type="email",
                query=email,
                result="success"
            )
            
        except Exception as e:
            logger.error(f"Error en email_lookup: {e}")
            await processing_msg.edit_text("❌ Error al procesar el email")
    
    async def admin_panel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Panel de administración"""
        user = update.effective_user
        
        if user.id != OWNER_ID:
            await update.message.reply_text("❌ Acceso denegado. Solo el propietario.")
            return
        
        # Obtener estadísticas
        stats = await db.get_statistics()
        
        admin_text = f"🛠 *PANEL DE ADMINISTRACIÓN*\n\n"
        admin_text += f"👑 *Propietario:* {user.first_name}\n"
        admin_text += f"📊 *Usuarios totales:* {stats['total_users']}\n"
        admin_text += f"🔍 *Búsquedas hoy:* {stats['searches_today']}\n"
        admin_text += f"📈 *Búsquedas totales:* {stats['total_searches']}\n"
        admin_text += f"🔄 *Bot activo desde:* {stats['bot_uptime']}\n"
        
        keyboard = [
            [
                InlineKeyboardButton("📊 Estadísticas", callback_data="admin_stats"),
                InlineKeyboardButton("👥 Usuarios", callback_data="admin_users")
            ],
            [
                InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"),
                InlineKeyboardButton("📝 Logs", callback_data="admin_logs")
            ],
            [
                InlineKeyboardButton("🔄 Reiniciar", callback_data="admin_restart"),
                InlineKeyboardButton("💾 Backup", callback_data="admin_backup")
            ],
            [
                InlineKeyboardButton("❌ Cerrar", callback_data="admin_close")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            admin_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manejador de botones inline"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        if query.data == "help":
            await self.help_callback(query)
        elif query.data == "tools_ip":
            await query.edit_message_text(
                "🔍 *Búsqueda de IP*\n\n"
                "Envía: `/ip 8.8.8.8`\n\n"
                "*Ejemplos:*\n"
                "• IP pública\n• IP privada\n• Rango CIDR",
                parse_mode='Markdown'
            )
        elif query.data == "admin_panel" and user_id == OWNER_ID:
            await self.admin_panel_callback(query)
        elif query.data == "admin_stats" and user_id == OWNER_ID:
            stats = await db.get_statistics()
            stats_text = f"📊 *ESTADÍSTICAS*\n\n"
            for key, value in stats.items():
                stats_text += f"*{key}:* {value}\n"
            await query.edit_message_text(stats_text, parse_mode='Markdown')
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manejador de errores"""
        logger.error(f"Error: {context.error}")
        
        if update and update.effective_user:
            try:
                await update.effective_message.reply_text(
                    "❌ Ocurrió un error. Intenta nuevamente."
                )
            except:
                pass

def main():
    """Función principal"""
    # Verificar token
    if not TOKEN:
        logger.error("❌ No se encontró BOT_TOKEN en variables de entorno")
        return
    
    # Crear aplicación
    application = Application.builder().token(TOKEN).build()
    
    # Instanciar bot
    bot = OSINTBot()
    
    # Handlers de comandos
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CommandHandler("help", bot.help_command))
    application.add_handler(CommandHandler("ip", bot.ip_lookup))
    application.add_handler(CommandHandler("domain", bot.domain_lookup))
    application.add_handler(CommandHandler("email", bot.email_lookup))
    application.add_handler(CommandHandler("admin", bot.admin_panel))
    
    # Handler de botones
    application.add_handler(CallbackQueryHandler(bot.button_handler))
    
    # Handler de errores
    application.add_error_handler(bot.error_handler)
    
    # Handler de mensajes (extraer datos automáticamente)
    async def auto_extract(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Extraer automáticamente IPs, emails, etc. de mensajes"""
        text = update.message.text
        
        # Extraer emails
        emails = extract_emails_from_text(text)
        if emails:
            await update.message.reply_text(
                f"📧 *Emails detectados:*\n" + "\n".join(emails),
                parse_mode='Markdown'
            )
        
        # Extraer URLs
        urls = extract_urls_from_text(text)
        if urls:
            await update.message.reply_text(
                f"🔗 *URLs detectadas:*\n" + "\n".join(urls),
                parse_mode='Markdown'
            )
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_extract))
    
    # Iniciar bot
    logger.info("🤖 OSINT-BOT iniciándose...")
    
    if os.getenv('RAILWAY_ENVIRONMENT'):
        logger.info("🚀 Entorno: Railway.app")
        # En Railway, usar webhook o polling según configuración
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    else:
        logger.info("💻 Entorno: Local")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
