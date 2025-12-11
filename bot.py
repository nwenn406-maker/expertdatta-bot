#!/usr/bin/env python3
"""
🤖 OSINT-BOT - Versión 4.0 Estable
Bot de Inteligencia de Fuentes Abiertas
🔒 Token OCULTADO para Railway/GitHub
"""

import os
import sys
import json
import re
import time
import threading
from datetime import datetime
from urllib.parse import urljoin, urlparse, quote

# ==================== CONFIGURACIÓN SEGURA ====================
# ⚠️ NUNCA pongas tokens directamente en el código
# Leer de variable de entorno (Railway/GitHub Secrets)

# 1. Primero intenta leer de variable de entorno (Railway/GitHub)
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

# 2. Si no existe, para desarrollo local puedes usar un archivo .env
if not TOKEN:
    try:
        from dotenv import load_dotenv
        load_dotenv()
        TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
    except ImportError:
        pass

# 3. Si sigue sin existir, usar valor por defecto SOLO PARA PRUEBAS LOCALES
# ⚠️ ESTA LÍNEA DEBE ELIMINARSE EN PRODUCCIÓN ⚠️
if not TOKEN:
    TOKEN = "8382109200:AAFxY94tHyyRDD5VKn1FXskwaGffmpwxy-Q"  # ⚠️ TEMPORAL - REVOCAR ESTE TOKEN
    print("⚠️  ADVERTENCIA: Usando token por defecto - REVOCAR inmediatamente después de pruebas")

BOT_VERSION = "4.0-Secure"
PORT = int(os.environ.get('PORT', 8080))  # Puerto para Railway

# ==================== ARCHIVO .env (crear en tu máquina local) ====================
"""
# Archivo: .env (NO SUBIR A GITHUB)
TELEGRAM_BOT_TOKEN=8382109200:AAFxY94tHyyRDD5VKn1FXskwaGffmpwxy-Q
"""

# ==================== ARCHIVO .gitignore (AGREGAR) ====================
"""
# Secretos
.env
.env.local
*.env
secrets/
config.json
token.txt
credentials.json
bot_log.txt
temp/
"""

# ==================== IMPORTAR MÓDULOS ====================
try:
    import telebot
    from telebot import types
    import requests
    from bs4 import BeautifulSoup
    import whois
    import dns.resolver
    import concurrent.futures
    print("✅ Módulos importados correctamente")
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    print("\n📦 Instala las dependencias con:")
    print("pip install pyTelegramBotAPI requests beautifulsoup4 python-whois dnspython python-dotenv")
    sys.exit(1)

# ==================== INICIALIZAR BOT ====================
bot = telebot.TeleBot(TOKEN, parse_mode='HTML')

# ==================== VARIABLES GLOBALES ====================
user_data = {}
search_history = {}

# ==================== FUNCIONES UTILITARIAS ====================

def log_action(user_id, action, details=""):
    """Registrar acciones"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] User:{user_id} | Action:{action} | {details}"
    print(log_msg)
    
    # Guardar en archivo (solo si no estamos en Railway)
    try:
        with open("bot_log.txt", "a", encoding="utf-8") as f:
            f.write(log_msg + "\n")
    except:
        pass  # En Railway puede fallar si no hay filesystem

def validate_url(url):
    """Validar URL"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def normalize_url(url):
    """Normalizar URL"""
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url.rstrip('/')

def get_headers():
    """Headers para requests"""
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9',
        'Connection': 'keep-alive',
    }

# ==================== HERRAMIENTAS OSINT ====================

class OSINTTools:
    """Clase con herramientas OSINT"""
    
    @staticmethod
    def extract_urls(target_url, max_urls=100):
        """Extraer URLs de una página"""
        urls = []
        try:
            headers = get_headers()
            response = requests.get(target_url, headers=headers, timeout=15, verify=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Enlaces <a>
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href and not href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                    absolute_url = urljoin(target_url, href)
                    if validate_url(absolute_url):
                        urls.append(absolute_url)
            
            # Recursos
            tags = soup.find_all(['img', 'script', 'link', 'source', 'iframe'])
            for tag in tags:
                for attr in ['src', 'href', 'data-src']:
                    if tag.has_attr(attr):
                        value = tag[attr]
                        if value and not value.startswith(('#', 'javascript:', 'data:')):
                            absolute_url = urljoin(target_url, value)
                            if validate_url(absolute_url):
                                urls.append(absolute_url)
            
            return list(set(urls))[:max_urls]
            
        except Exception as e:
            return [f"Error: {str(e)}"]
    
    @staticmethod
    def extract_emails(target_url):
        """Extraer emails"""
        emails = set()
        try:
            headers = get_headers()
            response = requests.get(target_url, headers=headers, timeout=15)
            
            # Buscar en texto
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
            found_emails = re.findall(email_pattern, response.text)
            emails.update(found_emails)
            
            # Buscar en mailto links
            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.startswith('mailto:'):
                    email = href.replace('mailto:', '').split('?')[0]
                    if '@' in email:
                        emails.add(email)
            
            return list(emails)[:50]
        except:
            return []
    
    @staticmethod
    def extract_phones(target_url):
        """Extraer números de teléfono"""
        phones = set()
        try:
            headers = get_headers()
            response = requests.get(target_url, headers=headers, timeout=15)
            
            patterns = [
                r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]',  # Internacional
                r'\b\d{3}[-.\s]??\d{3}[-.\s]??\d{4}\b',  # US/CA
                r'\(\d{3}\)\s*\d{3}[-.\s]??\d{4}',  # Con paréntesis
                r'\b\d{4}[-.\s]??\d{3}[-.\s]??\d{3}\b',  # Otro formato
            ]
            
            for pattern in patterns:
                found = re.findall(pattern, response.text)
                phones.update(found)
            
            return list(phones)[:20]
        except:
            return []
    
    @staticmethod
    def get_whois_info(domain):
        """Información WHOIS"""
        try:
            w = whois.whois(domain)
            info = {
                'domain_name': w.domain_name,
                'registrar': w.registrar,
                'creation_date': str(w.creation_date),
                'expiration_date': str(w.expiration_date),
                'name_servers': list(w.name_servers)[:5] if w.name_servers else [],
                'status': w.status,
                'emails': w.emails,
            }
            return info
        except:
            return {"error": "No se pudo obtener información"}
    
    @staticmethod
    def get_dns_info(domain):
        """Información DNS"""
        info = {}
        try:
            resolver = dns.resolver.Resolver()
            resolver.timeout = 5
            
            # Registros A
            try:
                a_records = []
                answers = resolver.resolve(domain, 'A')
                for rdata in answers:
                    a_records.append(str(rdata))
                info['A'] = a_records
            except:
                info['A'] = []
            
            # Registros MX
            try:
                mx_records = []
                answers = resolver.resolve(domain, 'MX')
                for rdata in answers:
                    mx_records.append(str(rdata))
                info['MX'] = mx_records
            except:
                info['MX'] = []
            
            # Registros TXT
            try:
                txt_records = []
                answers = resolver.resolve(domain, 'TXT')
                for rdata in answers:
                    txt_records.append(str(rdata))
                info['TXT'] = txt_records
            except:
                info['TXT'] = []
            
            # Registros NS
            try:
                ns_records = []
                answers = resolver.resolve(domain, 'NS')
                for rdata in answers:
                    ns_records.append(str(rdata))
                info['NS'] = ns_records
            except:
                info['NS'] = []
            
            return info
            
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def google_dork_search(dork):
        """Generar enlace de Google Dorks"""
        encoded_dork = quote(dork)
        return f"https://www.google.com/search?q={encoded_dork}"
    
    @staticmethod
    def search_username(username):
        """Buscar username en redes"""
        platforms = {
            "GitHub": f"https://github.com/{username}",
            "Twitter": f"https://twitter.com/{username}",
            "Instagram": f"https://instagram.com/{username}",
            "Facebook": f"https://facebook.com/{username}",
            "LinkedIn": f"https://linkedin.com/in/{username}",
            "YouTube": f"https://youtube.com/@{username}",
            "Reddit": f"https://reddit.com/user/{username}",
            "Telegram": f"https://t.me/{username}",
            "TikTok": f"https://tiktok.com/@{username}",
        }
        return platforms

# ==================== HANDLERS DEL BOT ====================

@bot.message_handler(commands=['start', 'help', 'menu'])
def send_main_menu(message):
    """Menú principal"""
    user_id = message.from_user.id
    log_action(user_id, "START")
    
    # Información de seguridad
    env_info = "🔒" if os.environ.get('RAILWAY_ENVIRONMENT') else "🔧"
    
    menu_text = f"""
<b>🔍 OSINT-BOT v{BOT_VERSION}</b>
<i>{env_info} Token protegido • Herramientas de Inteligencia de Fuentes Abiertas</i>

<u>🛠️ HERRAMIENTAS PRINCIPALES:</u>

<code>/scrape URL</code> - Extraer todas las URLs
<code>/emails URL</code> - Extraer correos electrónicos
<code>/phones URL</code> - Extraer números telefónicos
<code>/domain DOMINIO</code> - Información WHOIS/DNS
<code>/dork QUERY</code> - Búsqueda con Google Dorks
<code>/user USERNAME</code> - Buscar usuario en redes

<u>📊 ANÁLISIS AVANZADO:</u>
<code>/analyze URL</code> - Análisis completo del sitio
<code>/deep URL</code> - Crawleo profundo (lento)
<code>/metadata URL</code> - Metadatos del sitio

<u>⚙️ UTILIDADES:</u>
<code>/export</code> - Exportar últimos resultados
<code>/history</code> - Ver historial de búsquedas
<code>/clear</code> - Limpiar datos
<code>/status</code> - Estado del bot

<u>⚠️ USO ÉTICO:</u>
• Solo para investigación autorizada
• Respeta robots.txt y términos de servicio
• No sobrecargues servidores
    """
    
    # Crear teclado
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("🔍 Scrape URL"),
        types.KeyboardButton("📧 Extraer Emails"),
        types.KeyboardButton("🌐 Info Dominio"),
        types.KeyboardButton("🔎 Google Dorks"),
        types.KeyboardButton("📊 Análisis Completo"),
        types.KeyboardButton("🗑️ Limpiar Datos")
    )
    
    bot.send_message(message.chat.id, menu_text, reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "🔍 Scrape URL")
def ask_scrape_url(message):
    """Pedir URL para scrape"""
    msg = bot.send_message(message.chat.id, "📥 <b>Envía la URL a analizar:</b>\n\nEjemplo: <code>https://ejemplo.com</code>")
    bot.register_next_step_handler(msg, process_scrape)

def process_scrape(message):
    """Procesar scrape de URL"""
    user_id = message.from_user.id
    url = message.text.strip()
    
    if not validate_url(url):
        bot.reply_to(message, "❌ <b>URL inválida</b>\nFormato: https://ejemplo.com")
        return
    
    log_action(user_id, "SCRAPE", url)
    
    # Enviar mensaje de procesamiento
    processing_msg = bot.send_message(message.chat.id, f"🔍 <b>Analizando:</b>\n<code>{url}</code>\n⏳ <i>Extrayendo URLs...</i>")
    
    # Ejecutar en segundo plano
    def do_scrape():
        try:
            urls = OSINTTools.extract_urls(url, max_urls=100)
            
            if not urls or (len(urls) == 1 and urls[0].startswith("Error:")):
                bot.edit_message_text(f"❌ <b>No se pudieron extraer URLs</b>\n{urls[0] if urls else 'Error desconocido'}", 
                                     message.chat.id, processing_msg.message_id)
                return
            
            # Guardar en historial
            if user_id not in search_history:
                search_history[user_id] = []
            search_history[user_id].append({
                'type': 'scrape',
                'url': url,
                'results': len(urls),
                'timestamp': datetime.now().isoformat()
            })
            
            # Formatear respuesta
            response = f"✅ <b>Extracción completada</b>\n\n"
            response += f"🔗 <b>URL analizada:</b> <code>{url}</code>\n"
            response += f"📊 <b>URLs encontradas:</b> {len(urls)}\n\n"
            response += "<b>Primeros 15 resultados:</b>\n"
            
            for i, found_url in enumerate(urls[:15], 1):
                response += f"{i}. <code>{found_url}</code>\n"
            
            if len(urls) > 15:
                response += f"\n📋 <i>... y {len(urls)-15} más</i>"
            
            # Botones de acción
            markup = types.InlineKeyboardMarkup()
            markup.row(
                types.InlineKeyboardButton("📥 Exportar TXT", callback_data=f"export_scrape_{user_id}"),
                types.InlineKeyboardButton("📧 Extraer Emails", callback_data=f"get_emails_{url}")
            )
            markup.row(
                types.InlineKeyboardButton("📞 Extraer Teléfonos", callback_data=f"get_phones_{url}"),
                types.InlineKeyboardButton("🔄 Crawlear Profundo", callback_data=f"deep_crawl_{url}")
            )
            
            bot.edit_message_text(response, message.chat.id, processing_msg.message_id, reply_markup=markup)
            
            # Guardar datos
            user_data[user_id] = {'urls': urls, 'type': 'scrape'}
            
        except Exception as e:
            bot.edit_message_text(f"❌ <b>Error:</b> {str(e)[:200]}", 
                                 message.chat.id, processing_msg.message_id)
    
    threading.Thread(target=do_scrape).start()

@bot.message_handler(commands=['emails'])
def handle_emails_command(message):
    """Comando /emails"""
    try:
        url = message.text.split()[1]
        process_emails(message, url)
    except IndexError:
        msg = bot.send_message(message.chat.id, "📧 <b>Envía la URL para extraer emails:</b>")
        bot.register_next_step_handler(msg, lambda m: process_emails(m, m.text))

def process_emails(message, url):
    """Procesar extracción de emails"""
    user_id = message.from_user.id
    url = url.strip()
    
    if not validate_url(url):
        bot.reply_to(message, "❌ URL inválida")
        return
    
    log_action(user_id, "EMAILS", url)
    
    msg = bot.send_message(message.chat.id, f"📧 <b>Buscando emails en:</b>\n<code>{url}</code>")
    
    def do_email_extraction():
        emails = OSINTTools.extract_emails(url)
        
        if not emails:
            bot.edit_message_text("❌ <b>No se encontraron emails</b>", 
                                 message.chat.id, msg.message_id)
            return
        
        # Guardar historial
        if user_id not in search_history:
            search_history[user_id] = []
        search_history[user_id].append({
            'type': 'emails',
            'url': url,
            'results': len(emails),
            'timestamp': datetime.now().isoformat()
        })
        
        response = f"✅ <b>Emails encontrados ({len(emails)}):</b>\n\n"
        for email in emails:
            response += f"• <code>{email}</code>\n"
        
        user_data[user_id] = {'emails': emails, 'type': 'emails'}
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📥 Exportar", callback_data=f"export_emails_{user_id}"))
        
        bot.edit_message_text(response, message.chat.id, msg.message_id, reply_markup=markup)
    
    threading.Thread(target=do_email_extraction).start()

@bot.message_handler(commands=['domain'])
def handle_domain_command(message):
    """Comando /domain"""
    try:
        domain = message.text.split()[1]
        process_domain(message, domain)
    except IndexError:
        msg = bot.send_message(message.chat.id, "🌐 <b>Envía el dominio a analizar:</b>\nEjemplo: ejemplo.com")
        bot.register_next_step_handler(msg, lambda m: process_domain(m, m.text))

def process_domain(message, domain):
    """Procesar análisis de dominio"""
    user_id = message.from_user.id
    domain = domain.strip().lower()
    
    if '.' not in domain:
        bot.reply_to(message, "❌ Dominio inválido")
        return
    
    log_action(user_id, "DOMAIN", domain)
    
    msg = bot.send_message(message.chat.id, f"🌐 <b>Analizando dominio:</b>\n<code>{domain}</code>\n⏳ <i>Obteniendo información...</i>")
    
    def do_domain_analysis():
        try:
            # Obtener información en paralelo
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_whois = executor.submit(OSINTTools.get_whois_info, domain)
                future_dns = executor.submit(OSINTTools.get_dns_info, domain)
                
                whois_info = future_whois.result()
                dns_info = future_dns.result()
            
            response = f"📊 <b>INFORMACIÓN DEL DOMINIO</b>\n\n"
            response += f"🔗 <b>Dominio:</b> <code>{domain}</code>\n\n"
            
            response += "<u>📋 WHOIS Information:</u>\n"
            if 'error' not in whois_info:
                response += f"• <b>Registrador:</b> {whois_info.get('registrar', 'N/A')}\n"
                response += f"• <b>Fecha creación:</b> {whois_info.get('creation_date', 'N/A')}\n"
                response += f"• <b>Fecha expiración:</b> {whois_info.get('expiration_date', 'N/A')}\n"
                response += f"• <b>Name Servers:</b> {len(whois_info.get('name_servers', []))}\n"
            else:
                response += "• No disponible\n"
            
            response += "\n<u>🌐 DNS Records:</u>\n"
            if 'error' not in dns_info:
                response += f"• <b>A Records:</b> {len(dns_info.get('A', []))}\n"
                response += f"• <b>MX Records:</b> {len(dns_info.get('MX', []))}\n"
                response += f"• <b>TXT Records:</b> {len(dns_info.get('TXT', []))}\n"
                response += f"• <b>NS Records:</b> {len(dns_info.get('NS', []))}\n"
            else:
                response += "• No disponible\n"
            
            # Guardar datos
            user_data[user_id] = {
                'domain_info': {'whois': whois_info, 'dns': dns_info},
                'type': 'domain'
            }
            
            # Botones
            markup = types.InlineKeyboardMarkup()
            markup.row(
                types.InlineKeyboardButton("📥 Exportar JSON", callback_data=f"export_domain_{user_id}"),
                types.InlineKeyboardButton("🔍 Scrapear Sitio", callback_data=f"scrape_domain_{domain}")
            )
            
            bot.edit_message_text(response, message.chat.id, msg.message_id, reply_markup=markup)
            
        except Exception as e:
            bot.edit_message_text(f"❌ <b>Error:</b> {str(e)}", 
                                 message.chat.id, msg.message_id)
    
    threading.Thread(target=do_domain_analysis).start()

@bot.message_handler(commands=['dork'])
def handle_dork(message):
    """Comando Google Dorks"""
    try:
        dork = message.text[6:].strip()
        if not dork:
            bot.reply_to(message, "❌ <b>Uso:</b> <code>/dork site:example.com filetype:pdf</code>")
            return
        
        log_action(message.from_user.id, "DORK", dork)
        
        google_url = OSINTTools.google_dork_search(dork)
        
        response = f"🔍 <b>Google Dork Generado</b>\n\n"
        response += f"<b>Query:</b> <code>{dork}</code>\n\n"
        response += f"<b>Enlace de búsqueda:</b>\n<code>{google_url}</code>\n\n"
        response += "<i>⚠️ Usa de forma responsable</i>"
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔗 Abrir en Google", url=google_url))
        
        bot.reply_to(message, response, reply_markup=markup)
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['user'])
def handle_user_search(message):
    """Buscar usuario en redes"""
    try:
        username = message.text.split()[1]
        search_username(message, username)
    except IndexError:
        msg = bot.send_message(message.chat.id, "👤 <b>Envía el username a buscar:</b>")
        bot.register_next_step_handler(msg, lambda m: search_username(m, m.text))

def search_username(message, username):
    """Buscar username"""
    user_id = message.from_user.id
    username = username.strip()
    
    log_action(user_id, "USER_SEARCH", username)
    
    platforms = OSINTTools.search_username(username)
    
    response = f"🔍 <b>Búsqueda de usuario:</b> <code>{username}</code>\n\n"
    response += "<b>Enlaces de búsqueda:</b>\n\n"
    
    for platform_name, url in platforms.items():
        response += f"• {platform_name}: {url}\n"
    
    response += "\n⚠️ <i>Puede que el usuario no exista en todas las plataformas</i>"
    
    # Crear botones inline
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for platform_name, url in list(platforms.items())[:8]:  # Primeras 8 plataformas
        buttons.append(types.InlineKeyboardButton(platform_name, url=url))
    
    # Agregar botones en filas de 2
    for i in range(0, len(buttons), 2):
        if i + 1 < len(buttons):
            markup.row(buttons[i], buttons[i + 1])
        else:
            markup.row(buttons[i])
    
    bot.send_message(message.chat.id, response, reply_markup=markup)

@bot.message_handler(commands=['analyze'])
def handle_analyze(message):
    """Análisis completo"""
    try:
        url = message.text.split()[1]
        full_analysis(message, url)
    except IndexError:
        msg = bot.send_message(message.chat.id, "📊 <b>Envía la URL para análisis completo:</b>")
        bot.register_next_step_handler(msg, lambda m: full_analysis(m, m.text))

def full_analysis(message, url):
    """Análisis completo de URL"""
    user_id = message.from_user.id
    url = url.strip()
    
    if not validate_url(url):
        bot.reply_to(message, "❌ URL inválida")
        return
    
    log_action(user_id, "FULL_ANALYSIS", url)
    
    msg = bot.send_message(message.chat.id, f"🔬 <b>Análisis completo iniciado:</b>\n<code>{url}</code>\n⏳ <i>Esto tomará unos segundos...</i>")
    
    def do_full_analysis():
        try:
            # Ejecutar todas las herramientas en paralelo
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                future_urls = executor.submit(OSINTTools.extract_urls, url, 50)
                future_emails = executor.submit(OSINTTools.extract_emails, url)
                future_phones = executor.submit(OSINTTools.extract_phones, url)
                
                urls = future_urls.result()
                emails = future_emails.result()
                phones = future_phones.result()
            
            # Obtener dominio
            domain = urlparse(url).netloc
            domain_info = OSINTTools.get_whois_info(domain)
            
            # Construir reporte
            report = f"📈 <b>REPORTE DE ANÁLISIS COMPLETO</b>\n\n"
            report += f"🔗 <b>URL analizada:</b> <code>{url}</code>\n"
            report += f"🌐 <b>Dominio:</b> <code>{domain}</code>\n\n"
            
            report += "<u>📊 ESTADÍSTICAS:</u>\n"
            report += f"• URLs encontradas: {len(urls)}\n"
            report += f"• Emails encontrados: {len(emails)}\n"
            report += f"• Teléfonos encontrados: {len(phones)}\n\n"
            
            report += "<u>📧 EMAILS (primeros 5):</u>\n"
            if emails:
                for i, email in enumerate(emails[:5], 1):
                    report += f"{i}. <code>{email}</code>\n"
            else:
                report += "• Ninguno encontrado\n"
            
            report += "\n<u>📞 TELÉFONOS (primeros 3):</u>\n"
            if phones:
                for i, phone in enumerate(phones[:3], 1):
                    report += f"{i}. <code>{phone}</code>\n"
            else:
                report += "• Ninguno encontrado\n"
            
            report += f"\n<u>🌐 INFO DOMINIO:</u>\n"
            if 'error' not in domain_info:
                report += f"• Registrador: {domain_info.get('registrar', 'N/A')}\n"
                report += f"• Creado: {domain_info.get('creation_date', 'N/A')[:10]}\n"
            else:
                report += "• Información no disponible\n"
            
            # Guardar datos
            user_data[user_id] = {
                'analysis': {
                    'url': url,
                    'domain': domain,
                    'urls_count': len(urls),
                    'emails': emails,
                    'phones': phones,
                    'domain_info': domain_info
                },
                'type': 'full_analysis'
            }
            
            # Botones de acción
            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                types.InlineKeyboardButton("📥 Exportar Reporte", callback_data=f"export_report_{user_id}"),
                types.InlineKeyboardButton("🔍 Ver Todas URLs", callback_data=f"show_urls_{user_id}"),
                types.InlineKeyboardButton("📧 Ver Todos Emails", callback_data=f"show_emails_{user_id}"),
                types.InlineKeyboardButton("📞 Ver Todos Teléfonos", callback_data=f"show_phones_{user_id}")
            )
            
            bot.edit_message_text(report, message.chat.id, msg.message_id, reply_markup=markup)
            
        except Exception as e:
            bot.edit_message_text(f"❌ <b>Error en análisis:</b> {str(e)[:200]}", 
                                 message.chat.id, msg.message_id)
    
    threading.Thread(target=do_full_analysis).start()

@bot.message_handler(commands=['export'])
def handle_export(message):
    """Exportar últimos resultados"""
    user_id = message.from_user.id
    
    if user_id not in user_data:
        bot.reply_to(message, "❌ No hay datos para exportar")
        return
    
    data = user_data[user_id]
    export_type = data.get('type', 'data')
    
    try:
        if export_type == 'scrape':
            content = "\n".join(data.get('urls', []))
            filename = f"urls_{user_id}_{int(time.time())}.txt"
            send_as_file(message.chat.id, content, filename, "📄 URLs exportadas")
            
        elif export_type == 'emails':
            content = "\n".join(data.get('emails', []))
            filename = f"emails_{user_id}_{int(time.time())}.txt"
            send_as_file(message.chat.id, content, filename, "📧 Emails exportados")
            
        elif export_type == 'domain':
            content = json.dumps(data.get('domain_info', {}), indent=2, ensure_ascii=False)
            filename = f"domain_{user_id}_{int(time.time())}.json"
            send_as_file(message.chat.id, content, filename, "🌐 Info dominio exportada")
            
        elif export_type == 'full_analysis':
            content = json.dumps(data.get('analysis', {}), indent=2, ensure_ascii=False)
            filename = f"analysis_{user_id}_{int(time.time())}.json"
            send_as_file(message.chat.id, content, filename, "📊 Análisis exportado")
            
        else:
            bot.reply_to(message, "❌ Tipo de exportación no soportado")
            
    except Exception as e:
        bot.reply_to(message, f"❌ Error exportando: {str(e)}")

def send_as_file(chat_id, content, filename, caption):
    """Enviar contenido como archivo"""
    # En Railway, usar directorio temporal
    temp_dir = os.environ.get('TEMP', 'temp')
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir, exist_ok=True)
    
    filepath = os.path.join(temp_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    with open(filepath, 'rb') as f:
        bot.send_document(chat_id, f, caption=caption)
    
    # Limpiar archivo temporal
    try:
        os.remove(filepath)
    except:
        pass

@bot.message_handler(commands=['history'])
def handle_history(message):
    """Mostrar historial"""
    user_id = message.from_user.id
    
    if user_id not in search_history or not search_history[user_id]:
        bot.reply_to(message, "📭 <b>No hay historial de búsquedas</b>")
        return
    
    history = search_history[user_id][-10:]  # Últimas 10 búsquedas
    
    response = "📜 <b>HISTORIAL DE BÚSQUEDAS</b>\n\n"
    
    for i, entry in enumerate(reversed(history), 1):
        date = entry['timestamp'].split('T')[0]
        time_str = entry['timestamp'].split('T')[1][:8]
        
        response += f"<b>{i}. {entry['type'].upper()}</b>\n"
        response += f"   📅 {date} ⏰ {time_str}\n"
        response += f"   🔗 {entry['url'][:50]}...\n"
        response += f"   📊 Resultados: {entry['results']}\n\n"
    
    response += f"<i>Mostrando {len(history)} de {len(search_history[user_id])} búsquedas</i>"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🗑️ Limpiar Historial", callback_data=f"clear_history_{user_id}"))
    
    bot.send_message(message.chat.id, response, reply_markup=markup)

@bot.message_handler(commands=['clear'])
def handle_clear(message):
    """Limpiar datos"""
    user_id = message.from_user.id
    
    if user_id in user_data:
        del user_data[user_id]
    
    if user_id in search_history:
        del search_history[user_id]
    
    bot.reply_to(message, "✅ <b>Datos limpiados correctamente</b>")
    log_action(user_id, "CLEAR_DATA")

@bot.message_handler(commands=['status'])
def handle_status(message):
    """Estado del bot"""
    # Detectar entorno
    environment = "Railway" if os.environ.get('RAILWAY_ENVIRONMENT') else "Local"
    token_status = "🔒 Oculto" if os.environ.get('TELEGRAM_BOT_TOKEN') else "⚠️ Por defecto"
    
    status_text = f"""
<b>🤖 OSINT-BOT Status v{BOT_VERSION}</b>

<u>📊 ESTADÍSTICAS:</u>
• <b>Versión:</b> {BOT_VERSION}
• <b>Entorno:</b> {environment}
• <b>Token:</b> {token_status}
• <b>Usuarios activos:</b> {len(user_data)}
• <b>Búsquedas totales:</b> {sum(len(v) for v in search_history.values())}
• <b>Hora servidor:</b> {datetime.now().strftime('%H:%M:%S')}

<u>🛠️ Funciones activas:</u>
• Extracción URLs
• Extracción emails/teléfonos
• Análisis WHOIS/DNS
• Google Dorks
• Búsqueda usuarios

<u>⚠️ Recordatorio:</u>
Este bot es para investigación ética.
Respeta siempre los términos de servicio.
    """
    bot.reply_to(message, status_text)

# ==================== HANDLERS DE CALLBACK ====================

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    """Manejar botones inline"""
    user_id = call.from_user.id
    data = call.data
    
    try:
        if data.startswith("export_"):
            # export_scrape_123456
            parts = data.split("_")
            if len(parts) >= 3:
                user_str = parts[2]
                if user_str.isdigit() and int(user_str) == user_id:
                    # Simular mensaje para exportar
                    class FakeMessage:
                        def __init__(self, chat_id, user_id):
                            self.chat = type('obj', (object,), {'id': chat_id})
                            self.from_user = type('obj', (object,), {'id': user_id})
                    
                    fake_msg = FakeMessage(call.message.chat.id, user_id)
                    handle_export(fake_msg)
                    bot.answer_callback_query(call.id, "✅ Exportando...")
                else:
                    bot.answer_callback_query(call.id, "❌ No autorizado")
            
        elif data.startswith("get_emails_"):
            url = data[11:]
            # Crear mensaje simulado
            class FakeMessage:
                def __init__(self, text, user_id, chat_id):
                    self.text = text
                    self.from_user = type('obj', (object,), {'id': user_id})
                    self.chat = type('obj', (object,), {'id': chat_id})
            
            fake_msg = FakeMessage(url, user_id, call.message.chat.id)
            process_emails(fake_msg, url)
            bot.answer_callback_query(call.id, "📧 Buscando emails...")
            
        elif data.startswith("get_phones_"):
            bot.answer_callback_query(call.id, "📞 Función en desarrollo")
            
        elif data.startswith("deep_crawl_"):
            bot.answer_callback_query(call.id, "🔄 Crawleo profundo iniciado")
            
        elif data.startswith("scrape_domain_"):
            domain = data[14:]
            url = f"https://{domain}"
            # Crear mensaje simulado
            class FakeMessage:
                def __init__(self, text, user_id, chat_id):
                    self.text = text
                    self.from_user = type('obj', (object,), {'id': user_id})
                    self.chat = type('obj', (object,), {'id': chat_id})
            
            fake_msg = FakeMessage(url, user_id, call.message.chat.id)
            process_scrape(fake_msg)
            
        elif data.startswith("show_urls_"):
            parts = data.split("_")
            if len(parts) >= 3:
                uid = int(parts[2])
                if uid == user_id and user_id in user_data:
                    urls = user_data[user_id].get('urls', [])
                    response = "🔗 <b>Todas las URLs:</b>\n\n"
                    for url in urls[:30]:
                        response += f"• {url}\n"
                    bot.send_message(call.message.chat.id, response[:4000])
            
        elif data.startswith("clear_history_"):
            parts = data.split("_")
            if len(parts) >= 3:
                uid = int(parts[2])
                if uid == user_id:
                    if user_id in search_history:
                        del search_history[user_id]
                    bot.answer_callback_query(call.id, "✅ Historial limpiado")
                    bot.edit_message_text("🗑️ <b>Historial limpiado</b>", 
                                         call.message.chat.id, call.message.message_id)
        
        else:
            bot.answer_callback_query(call.id, "⚙️ Función no implementada")
            
    except Exception as e:
        bot.answer_callback_query(call.id, f"❌ Error: {str(e)[:50]}")
        print(f"Callback error: {e}")

# ==================== MANEJO DE MENSAJES NO RECONOCIDOS ====================

@bot.message_handler(func=lambda message: True)
def handle_unknown(message):
    """Manejar mensajes no reconocidos"""
    if message.text in ["🔍 Scrape URL", "📧 Extraer Emails", "🌐 Info Dominio", 
                       "🔎 Google Dorks", "📊 Análisis Completo", "🗑️ Limpiar Datos"]:
        # Los botones del teclado ya tienen handlers
        pass
    elif message.text.startswith('http'):
        # Si es una URL, hacer scrape automático
        process_scrape(message)
    else:
        bot.reply_to(message, "❌ <b>Comando no reconocido</b>\n\nUsa /help para ver comandos disponibles")

# ==================== INICIAR BOT (MODIFICADO PARA RAILWAY) ====================

def check_token():
    """Verificar token"""
    try:
        bot_info = bot.get_me()
        print(f"✅ Token válido")
        print(f"🤖 Bot: @{bot_info.username}")
        print(f"🆔 ID: {bot_info.id}")
        print(f"📛 Nombre: {bot_info.first_name}")
        
        # Verificar si estamos usando token por defecto (peligroso)
        if not os.environ.get('TELEGRAM_BOT_TOKEN') and TOKEN == "8382109200:AAFxY94tHyyRDD5VKn1FXskwaGffmpwxy-Q":
            print("\n⚠️  ⚠️  ⚠️  ADVERTENCIA CRÍTICA ⚠️  ⚠️  ⚠️")
            print("Estás usando el token por defecto que fue EXPUESTO PÚBLICAMENTE")
            print("REVÓCALO INMEDIATAMENTE en @BotFather y configura uno nuevo en Railway")
            print("Pasos: Railway Dashboard → Variables → TELEGRAM_BOT_TOKEN = [NUEVO_TOKEN]")
        
        return True
    except Exception as e:
        print(f"❌ Token inválido: {e}")
        print("\n🔧 SOLUCIÓN:")
        print("1. Obtén token nuevo en @BotFather (/mybots → API Token)")
        print("2. En Railway: Settings → Variables → TELEGRAM_BOT_TOKEN = [nuevo_token]")
        print("3. Para local: crea archivo .env con TELEGRAM_BOT_TOKEN=tu_token")
        return False

def run_railway_server():
    """Ejecutar servidor para Railway"""
    try:
        from flask import Flask, request
        app = Flask(__name__)
        
        @app.route(f'/{TOKEN}', methods=['POST'])
        def webhook():
            if request.headers.get('content-type') == 'application/json':
                json_string = request.get_data().decode('utf-8')
                update = telebot.types.Update.de_json(json_string)
                bot.process_new_updates([update])
                return ''
            return 'Bad Request', 400
        
        @app.route('/')
        def index():
            return f'<h1>OSINT-BOT v{BOT_VERSION}</h1><p>Bot activo en Railway</p>'
        
        @app.route('/health')
        def health():
            return {'status': 'ok', 'version': BOT_VERSION}
        
        print(f"🌐 Iniciando servidor Railway en puerto {PORT}")
        app.run(host='0.0.0.0', port=PORT)
        
    except ImportError:
        print("⚠️ Flask no instalado. Usando polling...")
        bot.infinity_polling(timeout=60, long_polling_timeout=60)

def main():
    """Función principal"""
    print("=" * 60)
    print(f"🤖 OSINT-BOT v{BOT_VERSION}")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Verificar token
    if not check_token():
        sys.exit(1)
    
    print("\n🔧 Configuración detectada:")
    print(f"   • Entorno: {'Railway' if os.environ.get('RAILWAY_ENVIRONMENT') else 'Local'}")
    print(f"   • Token: {'🔒 Oculto' if os.environ.get('TELEGRAM_BOT_TOKEN') else '⚠️ Por defecto'}")
    print(f"   • Puerto: {PORT}")
    
    print("\n✅ Características activas:")
    print("   • Extracción de URLs")
    print("   • Extracción emails/teléfonos")
    print("   • Análisis WHOIS/DNS")
    print("   • Google Dorks")
    print("   • Búsqueda de usuarios")
    
    # Ejecutar según entorno
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        print("\n🌐 Modo: Railway (Webhook)")
        print("✅ Bot iniciado en Railway")
        run_railway_server()
    else:
        print("\n🔧 Modo: Local (Polling)")
        print("✅ Bot iniciado. Presiona Ctrl+C para detener.")
        print("=" * 60)
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except KeyboardInterrupt:
            print("\n👋 Bot detenido por el usuario")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
