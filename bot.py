import os
import logging
import requests
import json
import io
import datetime
from urllib.parse import urlparse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from PIL import Image
import dns.resolver
import whois
import psutil

# Configuración
TOKEN = os.getenv("8382109200:AAE83AVpz5NyoglrPlMvW3SwGmvXR5ki9VU")
ADMIN_ID = os.getenv("7767981731", "")

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============= COMANDOS PRINCIPALES =============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manejador del comando /start"""
    user = update.effective_user
    welcome_text = f"""
🕵️‍♂️ *Bienvenido {user.first_name} al OSINT Bot*

*Comandos disponibles:*

🔍 *Investigación Digital:*
/ip [dirección] - Información de IP
/domain [url] - Análisis de dominio
/whois [dominio] - Consulta WHOIS

👤 *Personas:*
/user [username] - Búsqueda de usuario
/email [email] - Verificar email
/phone [número] - Información telefónica

📊 *Multimedia:*
/exif - Analizar metadatos (envía imagen)

📍 *Geolocalización:*
/geo [IP/dominio] - Geolocalización

⚙️ *Otros:*
/help - Mostrar ayuda completa
/status - Estado del bot
/report [texto] - Reportar problema

⚠️ *Uso Ético:* Este bot es para investigación legítima.
    """
    
    keyboard = [
        [InlineKeyboardButton("🔍 Analizar IP", callback_data='ip_help'),
         InlineKeyboardButton("🌐 Analizar Dominio", callback_data='domain_help')],
        [InlineKeyboardButton("👤 Buscar Usuario", callback_data='user_help'),
         InlineKeyboardButton("📸 Analizar EXIF", callback_data='exif_help')],
        [InlineKeyboardButton("ℹ️ Ayuda Completa", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manejador del comando /help"""
    help_text = """
🕵️‍♂️ *OSINT Bot - Ayuda Completa*

*🔍 Herramientas de Investigación Digital:*
• `/ip 8.8.8.8` - Información detallada de IP
• `/domain google.com` - Análisis completo de dominio
• `/whois ejemplo.com` - Consulta WHOIS

*👤 Investigación de Personas:*
• `/user usuario123` - Búsqueda en redes sociales
• `/email prueba@ejemplo.com` - Verificación de email
• `/phone +521234567890` - Información telefónica

*📊 Herramientas Multimedia:*
• `/exif` - Analizar metadatos (luego envía imagen)
• Solo envía una imagen - Análisis EXIF automático

*📍 Geolocalización:*
• `/geo 8.8.8.8` - Ubicación geográfica

*⚙️ Comandos del Sistema:*
• `/status` - Estado del bot y estadísticas
• `/report [problema]` - Reportar error o sugerencia

*🛡️ Uso Responsable:*
Este bot debe usarse solo para:
- Investigación de seguridad
- Verificación de información
- Análisis legítimo
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def ip_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Análisis de dirección IP"""
    if not context.args:
        await update.message.reply_text("⚠️ Uso: `/ip 8.8.8.8`", parse_mode='Markdown')
        return
    
    ip = context.args[0]
    await update.message.reply_text(f"🔍 Analizando IP: `{ip}`...", parse_mode='Markdown')
    
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}?fields=66846719&lang=es")
        data = response.json()
        
        if data['status'] == 'success':
            info_text = f"""
🔍 *Información de IP:* `{ip}`
📍 *Ubicación:* {data.get('city', 'N/A')}, {data.get('regionName', 'N/A')}, {data.get('country', 'N/A')}
🌐 *ISP:* {data.get('isp', 'N/A')}
🏢 *Organización:* {data.get('org', 'N/A')}
📡 *ASN:* {data.get('as', 'N/A')}
📊 *Zona Horaria:* {data.get('timezone', 'N/A')}
🗺️ *Coordenadas:* {data.get('lat', 'N/A')}, {data.get('lon', 'N/A')}
🛡️ *Proxy:* {'✅ Sí' if data.get('proxy') else '❌ No'}
🌍 *Continente:* {data.get('continent', 'N/A')}
            """
            
            if data.get('lat') and data.get('lon'):
                map_url = f"https://maps.google.com/?q={data['lat']},{data['lon']}"
                info_text += f"\n🗺️ [Ver en Google Maps]({map_url})"
                
        else:
            info_text = f"❌ IP `{ip}` no válida o no encontrada"
            
        await update.message.reply_text(info_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error en ip_lookup: {e}")
        await update.message.reply_text("❌ Error al consultar la IP")

async def domain_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Análisis de dominio"""
    if not context.args:
        await update.message.reply_text("⚠️ Uso: `/domain google.com`", parse_mode='Markdown')
        return
    
    domain = context.args[0].replace('https://', '').replace('http://', '').split('/')[0]
    await update.message.reply_text(f"🌐 Analizando dominio: `{domain}`...", parse_mode='Markdown')
    
    try:
        info_text = f"🌐 *Análisis de Dominio:* `{domain}`\n\n"
        
        try:
            answers = dns.resolver.resolve(domain, 'A')
            ips = [str(rdata) for rdata in answers]
            info_text += f"📡 *IPs:* {', '.join(ips)}\n"
        except:
            info_text += "📡 *IPs:* No resuelto\n"
        
        try:
            w = whois.whois(domain)
            info_text += f"📅 *Creado:* {w.creation_date if w.creation_date else 'N/A'}\n"
            info_text += f"🔄 *Actualizado:* {w.updated_date if w.updated_date else 'N/A'}\n"
            info_text += f"⏰ *Expira:* {w.expiration_date if w.expiration_date else 'N/A'}\n"
            info_text += f"🏢 *Registrador:* {w.registrar if w.registrar else 'N/A'}\n"
        except:
            info_text += "ℹ️ *WHOIS:* Información limitada\n"
        
        try:
            headers_response = requests.get(f"https://{domain}", timeout=5)
            server = headers_response.headers.get('Server', 'N/A')
            info_text += f"🖥️ *Servidor:* {server}\n"
            
            if headers_response.url.startswith('https'):
                info_text += "🔐 *HTTPS:* ✅ Activo\n"
            else:
                info_text += "🔐 *HTTPS:* ❌ Inactivo\n"
                
        except:
            info_text += "⚠️ *HTTP:* No accesible\n"
        
        info_text += f"\n🔗 *URL completa:* https://{domain}"
        
        await update.message.reply_text(info_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error en domain_analysis: {e}")
        await update.message.reply_text("❌ Error al analizar el dominio")

async def user_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Búsqueda de usuario en redes sociales"""
    if not context.args:
        await update.message.reply_text("⚠️ Uso: `/user nombreusuario`", parse_mode='Markdown')
        return
    
    username = context.args[0]
    await update.message.reply_text(f"👤 Buscando usuario: `{username}`...", parse_mode='Markdown')
    
    platforms = [
        {"name": "GitHub", "url": f"https://github.com/{username}", "icon": "💻"},
        {"name": "Twitter", "url": f"https://twitter.com/{username}", "icon": "🐦"},
        {"name": "Instagram", "url": f"https://instagram.com/{username}", "icon": "📸"},
        {"name": "LinkedIn", "url": f"https://linkedin.com/in/{username}", "icon": "💼"},
        {"name": "Reddit", "url": f"https://reddit.com/user/{username}", "icon": "👤"},
        {"name": "Telegram", "url": f"https://t.me/{username}", "icon": "📱"},
        {"name": "Facebook", "url": f"https://facebook.com/{username}", "icon": "📘"},
        {"name": "YouTube", "url": f"https://youtube.com/@{username}", "icon": "📺"},
    ]
    
    results_text = f"👤 *Búsqueda de Usuario:* @{username}\n\n"
    found_count = 0
    
    for platform in platforms:
        try:
            response = requests.head(platform["url"], timeout=3)
            if response.status_code in [200, 301, 302]:
                results_text += f"{platform['icon']} *{platform['name']}:* [Enlace]({platform['url']})\n"
                found_count += 1
            else:
                results_text += f"❌ *{platform['name']}:* No encontrado\n"
        except:
            results_text += f"⚪ *{platform['name']}:* No verificado\n"
    
    results_text += f"\n📊 *Resumen:* {found_count}/{len(platforms)} plataformas encontradas"
    
    keyboard = [
        [InlineKeyboardButton("🔍 Buscar en Google", 
         url=f"https://www.google.com/search?q=%22{username}%22+site%3Agithub.com+OR+site%3Atwitter.com")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(results_text, parse_mode='Markdown', reply_markup=reply_markup)

async def exif_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Solicitar imagen para análisis EXIF"""
    await update.message.reply_text(
        "📸 *Envía una imagen para analizar sus metadatos EXIF.*\n\n"
        "Los metadatos pueden incluir:\n"
        "• 📷 Modelo de cámara\n• 📅 Fecha y hora\n• 📍 Ubicación GPS\n• ⚙️ Configuración de exposición",
        parse_mode='Markdown'
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manejador de imágenes para análisis EXIF"""
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    
    await update.message.reply_text("🔍 Analizando metadatos de la imagen...")
    
    try:
        image_data = io.BytesIO()
        await file.download_to_memory(image_data)
        image_data.seek(0)
        
        image = Image.open(image_data)
        exif_data = image._getexif()
        
        if exif_data:
            info_text = "📸 *Metadatos EXIF encontrados:*\n\n"
            
            exif_tags = {
                271: "📷 Fabricante",
                272: "📷 Modelo",
                306: "📅 Fecha y hora",
                34853: "📍 Información GPS",
                33434: "⏱️ Tiempo de exposición",
                33437: "📏 Apertura",
                34855: "📈 ISO",
                37378: "⚡ Flash",
                41987: "🎨 Modo de color"
            }
            
            for tag, value in exif_data.items():
                if tag in exif_tags:
                    info_text += f"{exif_tags[tag]}: `{value}`\n"
            
            info_text += f"\n📐 *Dimensiones:* {image.width} × {image.height} px"
            info_text += f"\n🎨 *Formato:* {image.format}"
            info_text += f"\n💾 *Modo de color:* {image.mode}"
            
        else:
            info_text = "ℹ️ No se encontraron metadatos EXIF en la imagen.\n\n"
            info_text += f"📐 *Dimensiones:* {image.width} × {image.height} px"
            info_text += f"\n🎨 *Formato:* {image.format}"
        
        await update.message.reply_text(info_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error en análisis EXIF: {e}")
        await update.message.reply_text("❌ Error al analizar la imagen")

async def geo_locate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Geolocalización de IP o dominio"""
    if not context.args:
        await update.message.reply_text("⚠️ Uso: `/geo 8.8.8.8` o `/geo google.com`", parse_mode='Markdown')
        return
    
    target = context.args[0]
    await update.message.reply_text(f"📍 Geolocalizando: `{target}`...", parse_mode='Markdown')
    
    try:
        if '.' in target and not target[0].isdigit():
            try:
                answers = dns.resolver.resolve(target, 'A')
                ip = str(answers[0])
            except:
                ip = target
        else:
            ip = target
        
        response = requests.get(f"http://ip-api.com/json/{ip}?fields=66846719&lang=es")
        data = response.json()
        
        if data['status'] == 'success':
            info_text = f"""
📍 *Geolocalización de:* `{target}`
🏙️ *Ciudad:* {data.get('city', 'N/A')}
🏛️ *Región:* {data.get('regionName', 'N/A')}
🇺🇸 *País:* {data.get('country', 'N/A')} ({data.get('countryCode', 'N/A')})
📮 *Código Postal:* {data.get('zip', 'N/A')}
🌐 *ISP:* {data.get('isp', 'N/A')}
🗺️ *Coordenadas:* {data.get('lat', 'N/A')}, {data.get('lon', 'N/A')}
            """
            
            if data.get('lat') and data.get('lon'):
                map_url = f"https://www.google.com/maps?q={data['lat']},{data['lon']}"
                keyboard = [[InlineKeyboardButton("🗺️ Ver en Google Maps", url=map_url)]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(info_text, parse_mode='Markdown', reply_markup=reply_markup)
                return
        
        else:
            info_text = f"❌ No se pudo geolocalizar `{target}`"
        
        await update.message.reply_text(info_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error en geo_locate: {e}")
        await update.message.reply_text("❌ Error en geolocalización")

async def bot_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Estado del bot"""
    cpu_percent = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    status_text = f"""
🤖 *Estado del Bot OSINT:*

✅ *Estado:* En línea
⏱️ *Uptime:* {datetime.datetime.now() - context.bot_data.get('start_time', datetime.datetime.now())}
👥 *Usuarios activos:* {len(context.application.user_data)}

💻 *Sistema:*
• 🖥️ CPU: {cpu_percent}%
• 💾 RAM: {memory.percent}% ({memory.used // (1024**2)}/{memory.total // (1024**2)} MB)
• 💿 Disco: {disk.percent}% usado

📊 *Estadísticas:*
• 📨 Comandos procesados: {context.bot_data.get('command_count', 0)}
• 🕐 Hora servidor: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

🔧 *Versión:* Python Telegram Bot
    """
    
    await update.message.reply_text(status_text, parse_mode='Markdown')

async def report_issue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Reportar un problema"""
    if not context.args:
        await update.message.reply_text("⚠️ Uso: `/report descripción del problema`", parse_mode='Markdown')
        return
    
    report_text = ' '.join(context.args)
    user = update.effective_user
    
    if ADMIN_ID:
        admin_message = f"""
🚨 *Nuevo Reporte:*

👤 *Usuario:* {user.first_name} (@{user.username or 'N/A'})
🆔 *ID:* {user.id}
📝 *Reporte:* {report_text}
📅 *Fecha:* {update.message.date}
        """
        
        try:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=admin_message,
                parse_mode='Markdown'
            )
        except:
            pass
    
    await update.message.reply_text(
        "✅ *Reporte enviado.*\n\n"
        "Gracias por tu feedback. Los problemas serán revisados lo antes posible.",
        parse_mode='Markdown'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manejador de botones inline"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == 'ip_help':
        await query.edit_message_text(
            "🔍 *Análisis de IP:*\n\n"
            "Envía: `/ip 8.8.8.8`\n\n"
            "Obtendrás:\n"
            "• 📍 Ubicación geográfica\n"
            "• 🌐 Proveedor de Internet\n"
            "• 🏢 Organización\n"
            "• 🗺️ Coordenadas GPS\n"
            "• 🛡️ Detección de Proxy/VPN",
            parse_mode='Markdown'
        )
    elif data == 'domain_help':
        await query.edit_message_text(
            "🌐 *Análisis de Dominio:*\n\n"
            "Envía: `/domain google.com`\n\n"
            "Obtendrás:\n"
            "• 📡 Direcciones IP\n"
            "• 📅 Fechas de registro\n"
            "• 🏢 Información del registrante\n"
            "• 🔐 Estado de HTTPS\n"
            "• 🖥️ Servidor web",
            parse_mode='Markdown'
        )
    elif data == 'user_help':
        await query.edit_message_text(
            "👤 *Búsqueda de Usuario:*\n\n"
            "Envía: `/user nombreusuario`\n\n"
            "Verificamos en:\n"
            "• 💻 GitHub\n• 🐦 Twitter\n• 📸 Instagram\n"
            "• 💼 LinkedIn\n• 👤 Reddit\n• 📱 Telegram\n"
            "• 📘 Facebook\n• 📺 YouTube",
            parse_mode='Markdown'
        )
    elif data == 'exif_help':
        await query.edit_message_text(
            "📸 *Análisis EXIF:*\n\n"
            "1. Envía el comando `/exif`\n"
            "2. O simplemente envía una imagen\n\n"
            "Analizamos:\n"
            "• 📷 Modelo de cámara\n• 📅 Fecha y hora\n"
            "• 📍 Coordenadas GPS\n• ⚙️ Configuración técnica",
            parse_mode='Markdown'
        )
    elif data == 'help':
        await help_command(update, context)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manejador de errores"""
    logger.error(f"Error: {context.error}")
    
    try:
        await update.message.reply_text(
            "❌ *Ocurrió un error inesperado.*\n\n"
            "Por favor, intenta nuevamente o usa `/report` para informar el problema.",
            parse_mode='Markdown'
        )
    except:
        pass

def count_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Contador de comandos"""
    if update.message and update.message.text and update.message.text.startswith('/'):
        context.application.bot_data['command_count'] = context.application.bot_data.get('command_count', 0) + 1

# ============= CONFIGURACIÓN PRINCIPAL =============

def main() -> None:
    """Función principal"""
    application = Application.builder().token(TOKEN).build()
    
    application.bot_data['start_time'] = datetime.datetime.now()
    application.bot_data['command_count'] = 0
    
    # Comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ip", ip_lookup))
    application.add_handler(CommandHandler("domain", domain_analysis))
    application.add_handler(CommandHandler("user", user_search))
    application.add_handler(CommandHandler("exif", exif_analysis))
    application.add_handler(CommandHandler("geo", geo_locate))
    application.add_handler(CommandHandler("whois", domain_analysis))
    application.add_handler(CommandHandler("status", bot_status))
    application.add_handler(CommandHandler("report", report_issue))
    
    # Botones inline
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Manejadores de mensajes
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    # Contador de comandos
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, count_commands), group=1)
    
    # Manejador de errores
    application.add_error_handler(error_handler)
    
    # Iniciar bot
    logger.info("🕵️‍♂️ Bot OSINT iniciado...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
