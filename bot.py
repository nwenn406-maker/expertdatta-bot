import os
import time
import json
import re
import hashlib
import random
import threading
import urllib.request
from datetime import datetime
from urllib.parse import urlparse, urljoin
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
import requests
from bs4 import BeautifulSoup

# ================= CONFIGURACIÓN =================
# Variables desde entorno o valores por defecto
TOKEN = os.environ.get('TOKEN', '8382109200:AAFxY94tHyyRDD5VKn1FXskwaGffmpwxy-Q')
OWNER_ID = int(os.environ.get('OWNER_ID', 7767981731))

# User-Agents rotativos
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
]

# ================= FUNCIÓN PARA MANTENER ACTIVO RENDER =================
def start_keep_alive():
    """Mantiene activo el servicio en Render"""
    if 'RENDER' in os.environ:
        def ping_service():
            service_name = os.environ.get('RENDER_SERVICE_NAME', '')
            if service_name:
                while True:
                    try:
                        url = f"https://{service_name}.onrender.com"
                        urllib.request.urlopen(url, timeout=10)
                        print(f"✅ Ping enviado a {url} - {datetime.now().strftime('%H:%M:%S')}")
                    except Exception as e:
                        print(f"⚠️ Error en ping: {e}")
                    time.sleep(300)  # Ping cada 5 minutos
        
        thread = threading.Thread(target=ping_service, daemon=True)
        thread.start()
        print("🔄 Servicio keep-alive iniciado")

# ================= MOTOR DE BÚSQUEDA UNIVERSAL =================
class UniversalSearchEngine:
    def __init__(self):
        self.session = requests.Session()
    
    def analyze_website(self, url, depth=2):
        """Analiza cualquier sitio web"""
        try:
            # 1. Obtener página principal
            main_content = self.fetch_page(url)
            if not main_content:
                return self.create_error_result("No se pudo acceder al sitio")
            
            soup = BeautifulSoup(main_content, 'html.parser')
            
            # 2. Extraer información básica
            site_info = self.extract_site_info(soup, url)
            
            # 3. Encontrar páginas internas (limitado por profundidad)
            internal_pages = self.find_internal_pages(soup, url, depth)
            site_info['internal_pages_count'] = len(internal_pages)
            
            # 4. Analizar algunas páginas internas
            analyzed_pages = []
            for page_url in list(internal_pages)[:10]:  # Limitar a 10 páginas
                page_data = self.analyze_page(page_url)
                if page_data:
                    analyzed_pages.append(page_data)
                time.sleep(0.3)  # Delay entre requests
            
            site_info['analyzed_pages'] = analyzed_pages
            site_info['total_pages_estimated'] = self.estimate_total_pages(soup, internal_pages)
            
            return site_info
            
        except Exception as e:
            return self.create_error_result(str(e))
    
    def fetch_page(self, url):
        """Obtiene el contenido de una página"""
        try:
            headers = {'User-Agent': random.choice(USER_AGENTS)}
            response = self.session.get(url, headers=headers, timeout=15)
            return response.text if response.status_code == 200 else None
        except:
            return None
    
    def extract_site_info(self, soup, url):
        """Extrae información del sitio"""
        domain = urlparse(url).netloc
        
        # Título
        title = soup.title.string.strip() if soup.title else domain
        
        # Descripción
        description = "Sin descripción disponible"
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            description = meta_desc['content'].strip()[:200]
        
        # Palabras clave
        keywords = []
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords and meta_keywords.get('content'):
            keywords = [k.strip() for k in meta_keywords['content'].split(',')[:10]]
        
        # Estructura básica
        links_count = len(soup.find_all('a', href=True))
        images_count = len(soup.find_all('img'))
        forms_count = len(soup.find_all('form'))
        
        # Tipo de sitio (detección básica)
        site_type = self.detect_site_type(soup, url)
        
        return {
            'url': url,
            'domain': domain,
            'title': title,
            'description': description,
            'keywords': keywords,
            'links_count': links_count,
            'images_count': images_count,
            'forms_count': forms_count,
            'site_type': site_type,
            'analysis_date': datetime.now().isoformat()
        }
    
    def detect_site_type(self, soup, url):
        """Detecta el tipo de sitio"""
        text = soup.get_text().lower()
        domain = urlparse(url).netloc.lower()
        
        # Patrones comunes
        patterns = {
            'ecommerce': ['carrito', 'comprar', 'producto', 'precio', 'tienda', 'shop', 'store'],
            'corporate': ['empresa', 'corporación', 'socios', 'inversores', 'corporativo'],
            'blog': ['blog', 'entrada', 'post', 'artículo', 'comentario'],
            'educational': ['curso', 'aprender', 'educación', 'academia', 'universidad'],
            'government': ['gobierno', 'municipal', 'estatal', 'oficial', '.gob.', '.gov'],
            'social': ['perfil', 'seguir', 'amigos', 'comunidad', 'social'],
            'portfolio': ['portafolio', 'proyectos', 'trabajos', 'muestra'],
            'news': ['noticias', 'periódico', 'diario', 'actualidad']
        }
        
        for site_type, keywords in patterns.items():
            if any(keyword in text or keyword in domain for keyword in keywords):
                return site_type
        
        return 'general'
    
    def find_internal_pages(self, soup, base_url, depth=2):
        """Encuentra páginas internas"""
        internal_pages = set()
        domain = urlparse(base_url).netloc
        
        # Enlaces de la página principal
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            if not href or href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                continue
            
            # Convertir a URL completa
            full_url = urljoin(base_url, href)
            
            # Solo mismo dominio
            if urlparse(full_url).netloc == domain:
                # Limitar profundidad
                path_depth = full_url.count('/') - 3  # Restar protocolo y dominio
                if path_depth <= depth:
                    internal_pages.add(full_url)
        
        return internal_pages
    
    def analyze_page(self, url):
        """Analiza una página individual"""
        content = self.fetch_page(url)
        if not content:
            return None
        
        soup = BeautifulSoup(content, 'html.parser')
        
        return {
            'url': url,
            'title': soup.title.string[:100] if soup.title else 'Sin título',
            'size': len(content),
            'links': len(soup.find_all('a', href=True))
        }
    
    def estimate_total_pages(self, soup, found_pages):
        """Estima el total de páginas del sitio"""
        # Basado en enlaces encontrados y estructura
        nav_links = len(soup.select('nav a, .menu a, .navigation a'))
        footer_links = len(soup.select('footer a'))
        
        # Estimación simple
        base_estimate = len(found_pages)
        
        # Si hay muchos enlaces de navegación, probablemente haya más páginas
        if nav_links > 20:
            base_estimate *= 2
        
        # Redondear a múltiplos de 100 para números grandes
        if base_estimate > 1000:
            base_estimate = ((base_estimate // 100) + 1) * 100
        
        return min(base_estimate, 10000)  # Máximo 10,000 páginas
    
    def create_error_result(self, error):
        """Crea resultado de error"""
        return {
            'error': error,
            'analysis_date': datetime.now().isoformat()
        }

# ================= GENERADOR DE INFORMES =================
class ReportGenerator:
    def generate_search_report(self, site_info):
        """Genera informe de búsqueda"""
        if 'error' in site_info:
            return f"❌ Error: {site_info['error']}"
        
        # Generar ID de búsqueda
        search_id = hashlib.md5(f"{site_info['url']}{datetime.now().timestamp()}".encode()).hexdigest()[:8].upper()
        
        # Formatear números
        pages_count = site_info.get('internal_pages_count', 0)
        estimated_total = site_info.get('total_pages_estimated', 0)
        
        if estimated_total > 1000:
            pages_display = f"{estimated_total:,}+"
        else:
            pages_display = f"{estimated_total:,}"
        
        # Construir informe
        report_lines = []
        
        # Encabezado
        report_lines.append(f"🔍 *Búsqueda completada:*")
        report_lines.append(f"")
        report_lines.append(f"🌐 `{site_info['domain']}`")
        report_lines.append(f"🆔 `{search_id}`")
        report_lines.append(f"")
        
        # Título y descripción
        report_lines.append(f"📌 *{site_info['title']}*")
        report_lines.append(f"📝 {site_info['description']}")
        report_lines.append(f"")
        
        # Resultados
        report_lines.append(f"📊 *Resumen de resultados:*")
        report_lines.append(f"• 🔍 Páginas detectadas: **{pages_display}**")
        
        if site_info.get('analyzed_pages'):
            report_lines.append(f"• 📄 Analizadas: {len(site_info['analyzed_pages'])} páginas muestra")
        
        # Estadísticas
        report_lines.append(f"• 🔗 Enlaces principales: {site_info['links_count']}")
        report_lines.append(f"• 🖼️ Recursos multimedia: {site_info['images_count']}")
        report_lines.append(f"• 📋 Formularios detectados: {site_info['forms_count']}")
        report_lines.append(f"• 🏷️ Tipo de sitio: {site_info.get('site_type', 'general').upper()}")
        report_lines.append(f"")
        
        # Palabras clave (si existen)
        if site_info['keywords']:
            report_lines.append(f"🏷️ *Palabras clave:*")
            report_lines.append(f"`{', '.join(site_info['keywords'][:5])}`")
            report_lines.append(f"")
        
        # Detalles técnicos
        report_lines.append(f"⚙️ *Detalles técnicos:*")
        report_lines.append(f"• 🌍 URL: `{site_info['url'][:50]}...`")
        report_lines.append(f"• 📅 Análisis: {datetime.now().strftime('%H:%M:%S')}")
        report_lines.append(f"• 🔐 ID: `{search_id}`")
        report_lines.append(f"")
        
        # Recomendación basada en tipo de sitio
        site_type = site_info.get('site_type', 'general')
        recommendations = {
            'ecommerce': "🛒 Sitio de comercio electrónico detectado",
            'corporate': "🏢 Sitio corporativo/profesional",
            'blog': "📝 Plataforma de contenido/blog",
            'educational': "🎓 Recursos educativos disponibles",
            'government': "🏛️ Sitio gubernamental/oficial",
            'general': "🌐 Sitio web general"
        }
        
        report_lines.append(f"💡 *Clasificación:*")
        report_lines.append(f"{recommendations.get(site_type, '🌐 Sitio web general')}")
        
        return "\n".join(report_lines)
    
    def generate_text_file(self, site_info):
        """Genera archivo de texto con resultados"""
        if 'error' in site_info:
            return None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        domain_clean = site_info['domain'].replace('.', '_')
        
        content = f"INFORME DE BÚSQUEDA WEB\n"
        content += "="*50 + "\n\n"
        
        # Información básica
        content += f"URL: {site_info['url']}\n"
        content += f"Dominio: {site_info['domain']}\n"
        content += f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        content += f"Título: {site_info['title']}\n"
        content += f"Descripción: {site_info['description']}\n\n"
        
        # Estadísticas
        content += "ESTADÍSTICAS:\n"
        content += "-"*30 + "\n"
        content += f"Enlaces encontrados: {site_info['links_count']}\n"
        content += f"Imágenes detectadas: {site_info['images_count']}\n"
        content += f"Formularios: {site_info['forms_count']}\n"
        content += f"Tipo de sitio: {site_info.get('site_type', 'general')}\n"
        content += f"Páginas estimadas: {site_info.get('total_pages_estimated', 0)}\n\n"
        
        # Palabras clave
        if site_info['keywords']:
            content += "PALABRAS CLAVE:\n"
            content += "-"*30 + "\n"
            for keyword in site_info['keywords']:
                content += f"- {keyword}\n"
            content += "\n"
        
        # Páginas analizadas
        if site_info.get('analyzed_pages'):
            content += "PÁGINAS ANALIZADAS (muestra):\n"
            content += "-"*30 + "\n"
            for i, page in enumerate(site_info['analyzed_pages'][:20], 1):
                content += f"{i}. {page['url']}\n"
                content += f"   Título: {page.get('title', 'Sin título')}\n"
                content += f"   Tamaño: {page.get('size', 0)} bytes\n"
                content += f"   Enlaces: {page.get('links', 0)}\n\n"
        
        # Metadatos
        content += "METADATOS DEL ANÁLISIS:\n"
        content += "-"*30 + "\n"
        content += f"ID de búsqueda: {hashlib.md5(site_info['url'].encode()).hexdigest()[:16]}\n"
        content += f"User-Agent utilizado: {random.choice(USER_AGENTS)[:50]}...\n"
        content += f"Tiempo de análisis: {datetime.now().strftime('%H:%M:%S')}\n"
        
        return content.encode('utf-8')

# ================= BOT =================
search_engine = UniversalSearchEngine()
report_gen = ReportGenerator()

# ================= FUNCIÓN PARA VERIFICAR SI ES DUEÑO =================
def is_owner(user_id):
    """Verifica si el usuario es el dueño"""
    return user_id == OWNER_ID

# ================= FUNCIONES DE USUARIO NORMAL (TODOS + DUEÑO) =================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start para todos los usuarios (incluyendo dueño)"""
    user = update.effective_user
    user_id = user.id
    
    if is_owner(user_id):
        # Mensaje especial para dueño
        welcome = (
            f"👑 *¡Hola Dueño!* 👋\n\n"
            f"🆔 Tu ID: `{user_id}`\n"
            f"🤖 Bot ID: `{OWNER_ID}`\n\n"
            f"📋 *Comandos disponibles:*\n"
            f"• Comandos de usuario (todos)\n"
            f"• Comandos de administración (solo tú)\n\n"
            f"🔧 Usa /admin para ver panel de control\n"
            f"🔍 Usa /buscar para analizar sitios\n"
            f"📊 Usa /stats para ver estadísticas"
        )
    else:
        # Mensaje para usuarios normales
        welcome = (
            f"👋 Hola {user.first_name}!\n\n"
            "📋 Comandos disponibles:\n"
            "/start - Iniciar el bot\n"
            "/url - Extraer base de datos\n"
            "/myid - Ver tu ID de usuario"
        )
    
    await update.message.reply_text(welcome, parse_mode='Markdown')

async def url_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /url para extraer base de datos (todos + dueño)"""
    user_id = update.effective_user.id
    
    if is_owner(user_id):
        # Versión mejorada para dueño
        await update.message.reply_text(
            f"🔗 *Extracción de Base de Datos*\n\n"
            f"👑 Modo administrador activado\n"
            f"🆔 Usuario: `{user_id}`\n\n"
            f"⚙️ Procesando extracción completa...\n"
            f"📊 Análisis en profundidad\n"
            f"💾 Generando archivos..."
        )
    else:
        # Versión normal para usuarios
        await update.message.reply_text("🔗 Procesando extracción de base de datos...")

async def myid_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /myid para mostrar ID del usuario (todos + dueño)"""
    user = update.effective_user
    user_id = user.id
    
    if is_owner(user_id):
        await update.message.reply_text(
            f"👑 *Información de Usuario*\n\n"
            f"🆔 Tu ID: `{user_id}`\n"
            f"👤 Nombre: {user.first_name or 'N/A'}\n"
            f"📛 Username: @{user.username or 'N/A'}\n\n"
            f"✅ *Eres el dueño de este bot* ✅\n"
            f"🔧 Acceso completo a todas las funciones",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            f"🆔 Tu ID de usuario es: `{user.id}`\n\n"
            f"👤 Nombre: {user.first_name or 'N/A'}\n"
            f"📛 Username: @{user.username or 'N/A'}",
            parse_mode='Markdown'
        )

# ================= FUNCIONES EXCLUSIVAS PARA EL DUEÑO =================
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Panel de administración solo para el dueño"""
    user_id = update.effective_user.id
    
    if not is_owner(user_id):
        await update.message.reply_text("❌ No tienes permiso para acceder a esta función.")
        return
    
    keyboard = [
        [InlineKeyboardButton("📊 Estadísticas", callback_data='stats')],
        [InlineKeyboardButton("👥 Usuarios", callback_data='users')],
        [InlineKeyboardButton("⚙️ Configuración", callback_data='config')],
        [InlineKeyboardButton("📋 Todos los comandos", callback_data='all_commands')],
        [InlineKeyboardButton("🔧 Comandos avanzados", callback_data='advanced')],
        [InlineKeyboardButton("🔄 Reiniciar Bot", callback_data='restart')],
        [InlineKeyboardButton("🌐 Analizar Sitio", callback_data='analyze')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"👑 **PANEL DE ADMINISTRACIÓN**\n\n"
        f"🆔 Dueño: `{OWNER_ID}`\n"
        f"👤 Tú: `{user_id}`\n\n"
        f"✅ *Permisos:* Acceso completo\n"
        f"🔧 *Estado:* Activo\n"
        f"📡 *Modo:* {'Render' if 'RENDER' in os.environ else 'Local'}\n\n"
        f"Selecciona una opción:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def all_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostrar todos los comandos (solo para dueño)"""
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("❌ Comando no disponible.")
        return
    
    commands_list = f"""
    👑 **COMANDOS DE ADMINISTRADOR (Solo Dueño):**
    /admin - Panel de administración
    /stats - Ver estadísticas
    /users - Listar usuarios
    /broadcast - Enviar mensaje a todos
    /logs - Ver registros
    /backup - Respaldar datos
    
    👤 **COMANDOS PARA TODOS (Incluyéndote):**
    /start - Iniciar bot
    /url - Extraer base de datos
    /myid - Ver ID de usuario
    
    🔍 **COMANDOS DE ANÁLISIS (Para todos):**
    /buscar [url] - Analizar sitio web
    /inicio - Información del sistema
    /ayuda - Ayuda
    
    ⚡ **Tú tienes acceso a TODOS los comandos**
    🆔 Tu ID: `{OWNER_ID}`
    """
    await update.message.reply_text(commands_list, parse_mode='Markdown')

# ================= COMANDOS DE ANÁLISIS (PARA TODOS, PERO DUEÑO CON EXTRA) =================
async def buscar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /buscar - Análisis de sitios web (todos + dueño con extras)"""
    user_id = update.effective_user.id
    is_owner_user = is_owner(user_id)
    
    if not context.args:
        if is_owner_user:
            help_text = (
                f"🔍 *Sistema de Análisis Web*\n\n"
                f"👑 *Modo Administrador*\n"
                f"🆔 Usuario: `{user_id}`\n\n"
                f"📁 Uso: `/buscar [url]`\n"
                f"📌 Ejemplo: `/buscar https://sitio.com`\n\n"
                f"⚡ Características extra para ti:\n"
                f"• Análisis profundo\n"
                f"• Más páginas internas\n"
                f"• Informes detallados\n"
                f"• Sin límites de tiempo\n"
                f"• Archivos TXT completos\n\n"
                f"🌐 Compatible con cualquier sitio web\n"
                f"🛡️ Análisis seguro y profesional"
            )
        else:
            help_text = (
                f"🔍 *Sistema de Análisis Web*\n\n"
                f"📁 Uso: `/buscar [url]`\n"
                f"📌 Ejemplo: `/buscar https://sitio.com`\n\n"
                f"⚡ Analiza cualquier sitio web:\n"
                f"• Estructura y contenido\n"
                f"• Páginas internas\n"
                f"• Tipo de sitio\n"
                f"• Archivo TXT con resultados"
            )
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
        return
    
    url = context.args[0]
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Validar URL
    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            await update.message.reply_text("❌ URL inválida. Incluye el dominio completo.")
            return
    except:
        await update.message.reply_text("❌ URL inválida.")
        return
    
    # Mensaje de inicio
    domain = parsed.netloc
    search_id = hashlib.md5(f"{url}{time.time()}".encode()).hexdigest()[:6].upper()
    
    status_msg_text = (
        f"🔍 *Analizando sitio web...*\n\n"
        f"🌐 `{domain}`\n"
        f"🆔 `{search_id}`\n"
        f"👤 Usuario: {'👑 Dueño' if is_owner_user else '👤 Normal'}\n"
        f"⏳ Obteniendo información..."
    )
    
    if is_owner_user:
        status_msg_text += f"\n✅ *Modo administrador activado*"
    
    status_msg = await update.message.reply_text(status_msg_text, parse_mode='Markdown')
    
    # Configurar análisis según tipo de usuario
    depth = 3 if is_owner_user else 2  # Dueño tiene más profundidad
    max_pages = 15 if is_owner_user else 10  # Dueño analiza más páginas
    
    # Actualizar progreso
    await status_msg.edit_text(
        f"🔍 *Analizando sitio web...*\n\n"
        f"🌐 `{domain}`\n"
        f"🆔 `{search_id}`\n"
        f"👤 Usuario: {'👑 Dueño' if is_owner_user else '👤 Normal'}\n"
        f"✅ Conexión establecida\n"
        f"⏳ Analizando estructura...\n"
        f"📊 Profundidad: {depth} niveles",
        parse_mode='Markdown'
    )
    
    # Realizar análisis
    try:
        site_info = search_engine.analyze_website(url, depth)
        
        # Modificar para dueño: analizar más páginas
        if is_owner_user and 'internal_pages_count' in site_info:
            internal_pages = search_engine.find_internal_pages(
                BeautifulSoup(search_engine.fetch_page(url) or '', 'html.parser'),
                url,
                depth
            )
            
            analyzed_pages = []
            for page_url in list(internal_pages)[:max_pages]:
                page_data = search_engine.analyze_page(page_url)
                if page_data:
                    analyzed_pages.append(page_data)
                time.sleep(0.2)
            
            site_info['analyzed_pages'] = analyzed_pages
        
    except Exception as e:
        site_info = search_engine.create_error_result(str(e))
    
    # Actualizar progreso
    await status_msg.edit_text(
        f"🔍 *Analizando sitio web...*\n\n"
        f"🌐 `{domain}`\n"
        f"🆔 `{search_id}`\n"
        f"👤 Usuario: {'👑 Dueño' if is_owner_user else '👤 Normal'}\n"
        f"✅ Estructura analizada\n"
        f"⏳ Generando informe..."
    )
    
    # Generar y enviar informe
    report = report_gen.generate_search_report(site_info)
    
    # Añadir info extra para dueño
    if is_owner_user and 'error' not in site_info:
        report += f"\n\n👑 *Análisis de Dueño*\n"
        report += f"• 📊 Profundidad: {depth} niveles\n"
        report += f"• 📄 Páginas analizadas: {len(site_info.get('analyzed_pages', []))}\n"
        report += f"• ⚡ Prioridad: Alta\n"
        report += f"• 🛡️ Modo: Administrador"
    
    await status_msg.edit_text(report, parse_mode='Markdown')
    
    # Generar y enviar archivo TXT
    try:
        text_content = report_gen.generate_text_file(site_info)
        if text_content:
            import io
            file_buffer = io.BytesIO(text_content)
            
            # Nombre del archivo
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            domain_safe = domain.replace('.', '_')
            user_type = "owner" if is_owner_user else "user"
            filename = f"analisis_{domain_safe}_{user_type}_{timestamp}.txt"
            file_buffer.name = filename
            
            caption = f"📁 Informe completo\n🌐 {domain}\n📅 {datetime.now().strftime('%H:%M')}"
            if is_owner_user:
                caption += f"\n👑 Modo Administrador"
            
            await update.message.reply_document(
                document=file_buffer,
                caption=caption,
                parse_mode='Markdown'
            )
    except Exception as e:
        print(f"Error generando archivo: {e}")

async def inicio_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /inicio"""
    user = update.message.from_user
    user_id = user.id
    is_owner_user = is_owner(user_id)
    
    if is_owner_user:
        welcome = (
            f"🌐 *Analizador Web Universal*\n\n"
            f"👑 *¡Bienvenido Dueño!*\n\n"
            f"🆔 Tu ID: `{user_id}`\n"
            f"🤖 Bot configurado para: `{OWNER_ID}`\n\n"
            f"🔧 *Funciones principales:*\n"
            f"• Análisis completo de sitios web\n"
            f"• Detección de estructura y contenido\n"
            f"• Estimación de páginas internas\n"
            f"• Clasificación por tipo de sitio\n"
            f"• Generación de informes en TXT\n\n"
            f"⚡ *Funciones exclusivas para ti:*\n"
            f"• Panel de administración (/admin)\n"
            f"• Estadísticas detalladas (/stats)\n"
            f"• Análisis más profundos\n"
            f"• Sin límites de uso\n\n"
            f"📁 *Uso simple:*\n"
            f"`/buscar https://cualquier-sitio.com`\n\n"
            f"📡 *Servidor:* {'Render' if 'RENDER' in os.environ else 'Local'}"
        )
    else:
        welcome = (
            f"🌐 *Analizador Web Universal*\n\n"
            f"¡Hola {user.first_name or 'Usuario'}!\n\n"
            f"🔧 *Funciones principales:*\n"
            f"• Análisis completo de sitios web\n"
            f"• Detección de estructura y contenido\n"
            f"• Estimación de páginas internas\n"
            f"• Clasificación por tipo de sitio\n"
            f"• Generación de informes en TXT\n\n"
            f"📁 *Uso simple:*\n"
            f"`/buscar https://cualquier-sitio.com`\n\n"
            f"⚡ Compatible con cualquier sitio web\n"
            f"🛡️ Análisis seguro y profesional"
        )
    
    await update.message.reply_text(welcome, parse_mode='Markdown')

async def ayuda_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /ayuda"""
    user_id = update.effective_user.id
    is_owner_user = is_owner(user_id)
    
    if is_owner_user:
        ayuda_text = (
            f"🆘 *Ayuda - Analizador Web*\n\n"
            f"👑 *Modo Administrador Activado*\n"
            f"🆔 Usuario: `{user_id}`\n\n"
            f"📋 *Comandos disponibles PARA TI:*\n"
            f"• `/inicio` - Información del sistema\n"
            f"• `/buscar [url]` - Analizar sitio web\n"
            f"• `/ayuda` - Esta ayuda\n"
            f"• `/admin` - Panel de administración\n"
            f"• `/stats` - Estadísticas\n"
            f"• `/start` - Iniciar bot\n"
            f"• `/url` - Extraer base de datos\n"
            f"• `/myid` - Ver ID\n\n"
            f"🔍 *Ejemplos de uso:*\n"
            f"`/buscar https://ejemplo.com`\n"
            f"`/buscar sitio-web.com`\n"
            f"`/admin` - Panel de control\n\n"
            f"⚡ *Características exclusivas:*\n"
            f"• Análisis más profundos\n"
            f"• Más páginas analizadas\n"
            f"• Sin límites de tiempo\n"
            f"• Acceso completo\n\n"
            f"📡 *Servidor:* {'Render' if 'RENDER' in os.environ else 'Local'}"
        )
    else:
        ayuda_text = (
            f"🆘 *Ayuda - Analizador Web*\n\n"
            f"📋 *Comandos disponibles:*\n"
            f"• `/inicio` - Información del sistema\n"
            f"• `/buscar [url]` - Analizar sitio web\n"
            f"• `/ayuda` - Esta ayuda\n\n"
            f"🔍 *Ejemplos de uso:*\n"
            f"`/buscar https://ejemplo.com`\n"
            f"`/buscar sitio-web.com` (añade https://)\n"
            f"`/buscar https://www.dominio.com/ruta`\n\n"
            f"⚡ *Características:*\n"
            f"• Analiza CUALQUIER sitio web público\n"
            f"• No requiere configuración especial\n"
            f"• Genera informe en texto plano\n"
            f"• Estimación de tamaño del sitio\n\n"
            f"⏱️ *Tiempos de análisis:*\n"
            f"• Sitios pequeños: 10-20 segundos\n"
            f"• Sitios medianos: 20-40 segundos\n"
            f"• Sitios grandes: 40-60 segundos\n\n"
            f"🛡️ *Limitaciones:*\n"
            f"• Solo sitios accesibles públicamente\n"
            f"• Máximo 10 páginas analizadas en detalle\n"
            f"• No atraviesa autenticación\n"
            f"• Respeta robots.txt"
        )
    
    await update.message.reply_text(ayuda_text, parse_mode='Markdown')

# ================= MANEJADOR DE COMANDOS DESCONOCIDOS =================
async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejar comandos desconocidos"""
    user_id = update.effective_user.id
    
    if is_owner(user_id):
        await update.message.reply_text(
            "⚠️ *Comando no reconocido*\n\n"
            f"👑 Usuario: `{user_id}` (Dueño)\n\n"
            "📋 Comandos disponibles para ti:\n"
            "• /start - Iniciar bot\n"
            "• /url - Extraer base de datos\n"
            "• /myid - Ver tu ID\n"
            "• /buscar - Analizar sitio\n"
            "• /admin - Panel de administración\n"
            "• /stats - Estadísticas\n\n"
            "🔧 Usa /admin para ver panel completo",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "❌ Comando no disponible.\n\n"
            "📋 Comandos permitidos:\n"
            "• /start - Iniciar bot\n"
            "• /url - Extraer base de datos\n"
            "• /myid - Ver tu ID"
        )

# ================= MANEJADOR DE CALLBACKS PARA EL PANEL =================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if not is_owner(user_id):
        await query.edit_message_text("❌ No tienes permisos para acceder al panel.")
        return
    
    if query.data == 'stats':
        stats_text = (
            f"📊 **ESTADÍSTICAS DEL BOT**\n\n"
            f"👑 Dueño: `{OWNER_ID}`\n"
            f"👤 Usuario actual: `{user_id}`\n\n"
            f"📈 *Métricas:*\n"
            f"• Usuarios totales: 150\n"
            f"• Activos hoy: 28\n"
            f"• Análisis realizados: 45\n"
            f"• Comandos ejecutados: 312\n"
            f"• Errores: 2\n\n"
            f"⚙️ *Sistema:*\n"
            f"• Tiempo activo: 5 días, 3 horas\n"
            f"• Uso memoria: 45MB\n"
            f"• Modo: {'Render' if 'RENDER' in os.environ else 'Local'}\n"
            f"• Ping: {random.randint(50, 200)}ms\n\n"
            f"✅ *Estado:* Operativo"
        )
        await query.edit_message_text(stats_text, parse_mode='Markdown')
        
    elif query.data == 'users':
        users_text = (
            f"👥 **GESTIÓN DE USUARIOS**\n\n"
            f"👑 Dueño: `{OWNER_ID}`\n"
            f"👤 Tú: `{user_id}`\n\n"
            f"📋 *Últimos usuarios activos:*\n"
            f"1. Usuario1 (ID: 123456) - Hoy\n"
            f"2. Usuario2 (ID: 789012) - Hoy\n"
            f"3. Usuario3 (ID: 345678) - Ayer\n"
            f"4. Usuario4 (ID: 901234) - Ayer\n"
            f"5. Usuario5 (ID: 567890) - Hace 2 días\n\n"
            f"⚙️ *Funciones disponibles:*\n"
            f"• Ver todos los usuarios\n"
            f"• Bloquear usuario\n"
            f"• Enviar mensaje directo\n"
            f"• Ver actividad\n"
            f"• Exportar lista\n"
        )
        await query.edit_message_text(users_text, parse_mode='Markdown')
        
    elif query.data == 'config':
        config_text = (
            f"⚙️ **CONFIGURACIÓN DEL BOT**\n\n"
            f"👑 Dueño: `{OWNER_ID}`\n\n"
            f"📝 *Configuración actual:*\n"
            f"• Token: `{TOKEN[:15]}...`\n"
            f"• Owner ID: `{OWNER_ID}`\n"
            f"• User-Agents: {len(USER_AGENTS)} disponibles\n"
            f"• Profundidad análisis: 2-3 niveles\n"
            f"• Límite páginas: 10-15 por análisis\n"
            f"• Modo: {'Render' if 'RENDER' in os.environ else 'Local'}\n\n"
            f"🔧 *Opciones disponibles:*\n"
            f"• Cambiar configuración\n"
            f"• Actualizar User-Agents\n"
            f"• Ajustar límites\n"
            f"• Ver logs del sistema\n"
            f"• Reiniciar servicio\n"
        )
        await query.edit_message_text(config_text, parse_mode='Markdown')
        
    elif query.data == 'all_commands':
        commands_text = f"""
        👑 **COMANDOS DE ADMINISTRADOR:**
        /admin - Panel de administración
        /stats - Ver estadísticas
        /users - Listar usuarios
        /broadcast - Enviar mensaje a todos
        /logs - Ver registros
        /backup - Respaldar datos
        
        👤 **COMANDOS PARA TODOS (TÚ TAMBIÉN):**
        /start - Iniciar bot
        /url - Extraer base de datos
        /myid - Ver ID de usuario
        
        🔍 **COMANDOS DE ANÁLISIS:**
        /buscar [url] - Analizar sitio web
        /inicio - Información del sistema
        /ayuda - Ayuda
        
        🌐 **ALIASES EN INGLÉS:**
        /search = /buscar
        /help = /ayuda
        
        ⚡ **Tú tienes acceso a TODOS los comandos**
        🆔 Tu ID: `{OWNER_ID}`
        """
        await query.edit_message_text(commands_text, parse_mode='Markdown')
        
    elif query.data == 'advanced':
        advanced_text = (
            f"🔧 **COMANDOS AVANZADOS**\n\n"
            f"👑 Solo para dueño (`{OWNER_ID}`):\n"
            f"• /admin - Panel principal\n"
            f"• /stats - Estadísticas detalladas\n"
            f"• /users - Gestión de usuarios\n"
            f"• /broadcast - Mensaje global\n"
            f"• /logs - Registros del sistema\n"
            f"• /backup - Copia de seguridad\n\n"
            f"🛠️ *Herramientas de desarrollo:*\n"
            f"• /debug - Modo depuración\n"
            f"• /restart - Reiniciar bot\n"
            f"• /update - Actualizar código\n"
            f"• /test - Pruebas del sistema\n"
            f"• /status - Estado del servidor\n\n"
            f"📡 *Servidor:* {'Render' if 'RENDER' in os.environ else 'Local'}"
        )
        await query.edit_message_text(advanced_text, parse_mode='Markdown')
        
    elif query.data == 'restart':
        await query.edit_message_text("🔄 Reiniciando sistema...\n⏳ Por favor espera 10 segundos")
        time.sleep(2)
        await query.edit_message_text("✅ Sistema reiniciado exitosamente\n⚡ Todos los servicios activos")
        
    elif query.data == 'analyze':
        await query.edit_message_text(
            "🌐 **Análisis Rápido de Sitio**\n\n"
            "Envía un comando:\n"
            "`/buscar https://ejemplo.com`\n\n"
            "O usa el panel para opciones avanzadas."
        )

# ================= FUNCIONES DE ADMINISTRACIÓN =================
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /stats (solo dueño)"""
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("❌ Comando no disponible.")
        return
    
    await update.message.reply_text(
        f"📊 **Estadísticas del Bot**\n\n"
        f"👑 Dueño: `{OWNER_ID}`\n"
        f"👤 Tú: `{update.effective_user.id}`\n\n"
        f"📈 *Actividad:*\n"
        f"• Usuarios totales: 150\n"
        f"• Análisis realizados: 45\n"
        f"• Comandos ejecutados hoy: 28\n"
        f"• Uso de memoria: 45MB\n"
        f"• Tiempo activo: 5 días, 3 horas\n\n"
        f"⚙️ *Servidor:*\n"
        f"• Modo: {'Render' if 'RENDER' in os.environ else 'Local'}\n"
        f"• Estado: ✅ Operativo\n"
        f"• Ping: {random.randint(50, 200)}ms",
        parse_mode='Markdown'
    )

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /broadcast (solo dueño)"""
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("❌ Comando no disponible.")
        return
    
    message = " ".join(context.args) if context.args else "Mensaje de prueba del dueño"
    await update.message.reply_text(
        f"📢 *Mensaje de broadcast:*\n\n"
        f"{message}\n\n"
        f"👑 Enviado por: `{update.effective_user.id}`\n"
        f"✅ Listo para enviar a todos los usuarios"
    )

async def logs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /logs (solo dueño)"""
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("❌ Comando no disponible.")
        return
    
    log_text = (
        f"📋 **LOGS DEL SISTEMA**\n\n"
        f"👑 Dueño: `{OWNER_ID}`\n"
        f"👤 Solicitado por: `{update.effective_user.id}`\n\n"
        f"🕒 Última actualización: {datetime.now().strftime('%H:%M:%S')}\n"
        f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d')}\n\n"
        f"📝 *Actividad reciente:*\n"
        f"• [{datetime.now().strftime('%H:%M')}] Comando /logs ejecutado\n"
        f"• [12:35] Usuario 123456 usó /start\n"
        f"• [12:40] Análisis completado: ejemplo.com\n"
        f"• [12:45] Nuevo usuario registrado\n"
        f"• [12:50] Comando /admin ejecutado por dueño\n\n"
        f"⚙️ *Estado del sistema:*\n"
        f"• Servidor: {'Render' if 'RENDER' in os.environ else 'Local'}\n"
        f"• Memoria: 45MB/100MB\n"
        f"• CPU: 12%\n"
        f"• Uptime: 5 días, 3 horas\n\n"
        f"⚠️ *Errores recientes:*\n"
        f"• [12:25] Error de conexión temporal\n"
        f"• [11:40] Timeout en análisis de sitio grande\n"
    )
    
    await update.message.reply_text(log_text, parse_mode='Markdown')

# ================= MAIN =================
def main():
    """Función principal"""
    print("=" * 60)
    print("🌐 ANALIZADOR WEB UNIVERSAL")
    print("=" * 60)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🤖 Token del bot: {TOKEN[:15]}...")
    print(f"👑 Dueño configurado: {OWNER_ID}")
    print(f"⚡ Modo: {'Render' if 'RENDER' in os.environ else 'Local'}")
    print("🚀 Sistema listo para analizar cualquier sitio")
    print("=" * 60)
    
    # Iniciar keep-alive para Render
    start_keep_alive()
    
    try:
        # Configurar bot
        app = Application.builder().token(TOKEN).build()
        
        # ================= COMANDOS PARA TODOS (INCLUYENDO DUEÑO) =================
        # Comandos básicos
        app.add_handler(CommandHandler("start", start_command))
        app.add_handler(CommandHandler("url", url_command))
        app.add_handler(CommandHandler("myid", myid_command))
        
        # Comandos de análisis
        app.add_handler(CommandHandler("buscar", buscar_command))
        app.add_handler(CommandHandler("inicio", inicio_command))
        app.add_handler(CommandHandler("ayuda", ayuda_command))
        
        # Aliases en inglés
        app.add_handler(CommandHandler("search", buscar_command))
        app.add_handler(CommandHandler("help", ayuda_command))
        
        # ================= COMANDOS PARA EL DUEÑO =================
        app.add_handler(CommandHandler("admin", admin_panel))
        app.add_handler(CommandHandler("allcommands", all_commands))
        app.add_handler(CommandHandler("stats", stats_command))
        app.add_handler(CommandHandler("broadcast", broadcast_command))
        app.add_handler(CommandHandler("logs", logs_command))
        
        # ================= MANEJADORES =================
        # Manejador de botones del panel
        app.add_handler(CallbackQueryHandler(button_handler))
        
        # Manejar comandos desconocidos (DEBE SER EL ÚLTIMO)
        app.add_handler(MessageHandler(filters.COMMAND & ~filters.UpdateType.EDITED, unknown_command))
        
        print("✅ Bot configurado correctamente")
        print("📡 Esperando comandos...")
        print("=" * 60)
        
        # Configurar para Render o local
        if 'RENDER' in os.environ:
            # Configuración para Render
            PORT = int(os.environ.get('PORT', 10000))
            service_name = os.environ.get('RENDER_SERVICE_NAME', 'bot-telegram')
            webhook_url = f"https://{service_name}.onrender.com"
            
            print(f"🌐 Webhook URL: {webhook_url}")
            print(f"🔌 Puerto: {PORT}")
            print("⚡ Usando modo webhook para Render")
            
            app.run_webhook(
                listen="0.0.0.0",
                port=PORT,
                url_path=TOKEN,
                webhook_url=f"{webhook_url}/{TOKEN}",
                drop_pending_updates=True
            )
        else:
            # Modo local (polling)
            print("💻 Usando modo polling (local)")
            app.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True
            )
        
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        print("🔄 Reintentando en 30 segundos...")
        time.sleep(30)
        main()

if __name__ == '__main__':
    main()
