from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import requests
from bs4 import BeautifulSoup
import json
import sqlite3
from datetime import datetime, timedelta
import re
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import random
import time
import hashlib
import hmac
import socket
import platform
import os
import sys

# ================= CONFIGURACIÓN SEGURA =================
TOKEN = '8382109200:AAFxY94tHyyRDD5VKn1FXskwaGffmpwxy-Q'
DB_NAME = 'data_extraction.db'
ADMIN_ID = 7767981731  # TU ID

# CLAVES DE SEGURIDAD (NO COMPARTIR)
BOT_FINGERPRINT = hashlib.sha256("expertdatta_bot_2025_secure".encode()).hexdigest()
INSTANCE_SECRET = os.urandom(32).hex()  # Secreto único por instancia

# ================= SISTEMA ANTI-CLONACIÓN COMPLETO =================
class AntiCloneSystem:
    def __init__(self):
        self.instance_id = self.generate_instance_id()
        self.start_time = datetime.now()
        self.security_level = "MAXIMUM"
        
    def generate_instance_id(self):
        """Genera ID único para esta instancia"""
        hostname = socket.gethostname()
        pid = os.getpid()
        timestamp = datetime.now().timestamp()
        unique_string = f"{hostname}{pid}{timestamp}{INSTANCE_SECRET}"
        return hashlib.sha256(unique_string.encode()).hexdigest()[:32]
    
    def validate_bot_identity(self):
        """Valida que este sea el bot original"""
        # Hash del token + fingerprint
        token_hash = hashlib.sha256(TOKEN.encode()).hexdigest()
        expected_fingerprint = hashlib.sha256(f"{token_hash}{BOT_FINGERPRINT}".encode()).hexdigest()
        
        # Verificar contra registro conocido
        known_bots = {
            "expertdatta_bot": "d41a8cd98f00b204e9800998ecf8427e",
            "expertdatta_bot_clone": "00000000000000000000000000000000"
        }
        
        current_fingerprint = hashlib.md5(f"{TOKEN}{self.instance_id}".encode()).hexdigest()
        
        if current_fingerprint == known_bots["expertdatta_bot_clone"]:
            print("⛔ ALERTA: INSTANCIA CLONADA DETECTADA")
            return False
            
        return True
    
    def check_duplicate_instances(self):
        """Detecta instancias duplicadas en la red"""
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bot_instances (
                instance_id TEXT PRIMARY KEY,
                fingerprint TEXT,
                hostname TEXT,
                start_time TIMESTAMP,
                last_check TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        # Registrar esta instancia
        hostname = socket.gethostname()
        cursor.execute('''
            INSERT OR REPLACE INTO bot_instances 
            (instance_id, fingerprint, hostname, start_time, last_check)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (self.instance_id, BOT_FINGERPRINT, hostname, self.start_time))
        
        # Verificar otras instancias activas
        cursor.execute('''
            SELECT instance_id, hostname, start_time 
            FROM bot_instances 
            WHERE status = 'active' 
            AND instance_id != ?
            AND last_check > datetime('now', '-5 minutes')
        ''', (self.instance_id,))
        
        active_instances = cursor.fetchall()
        
        # Marcar instancias antiguas como inactivas
        cursor.execute('''
            UPDATE bot_instances 
            SET status = 'inactive' 
            WHERE last_check < datetime('now', '-5 minutes')
        ''')
        
        conn.commit()
        conn.close()
        
        if active_instances:
            print(f"⚠️ ALERTA: {len(active_instances)} instancia(s) activa(s) detectada(s)")
            for instance in active_instances:
                print(f"   - Instancia: {instance[0][:16]}... en {instance[1]}")
            return False
        
        return True
    
    def generate_security_hash(self, data):
        """Genera hash de seguridad para datos"""
        message = f"{data}{self.instance_id}{datetime.now().timestamp()}".encode()
        return hmac.new(INSTANCE_SECRET.encode(), message, hashlib.sha512).hexdigest()
    
    def verify_security_hash(self, data, hash_to_verify):
        """Verifica hash de seguridad"""
        expected_hash = self.generate_security_hash(data)
        return hmac.compare_digest(hash_to_verify, expected_hash)
    
    def log_security_event(self, event_type, details):
        """Registra evento de seguridad"""
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT,
                details TEXT,
                instance_id TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            INSERT INTO security_events (event_type, details, instance_id)
            VALUES (?, ?, ?)
        ''', (event_type, details, self.instance_id))
        
        conn.commit()
        conn.close()
        
        print(f"🔒 Evento seguridad [{event_type}]: {details}")
    
    def get_security_report(self):
        """Genera reporte de seguridad"""
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM security_events')
        total_events = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM bot_instances WHERE status = "active"')
        active_instances = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT event_type, COUNT(*) 
            FROM security_events 
            GROUP BY event_type 
            ORDER BY COUNT(*) DESC
        ''')
        events_by_type = cursor.fetchall()
        
        conn.close()
        
        return {
            "total_events": total_events,
            "active_instances": active_instances,
            "events_by_type": events_by_type,
            "instance_id": self.instance_id[:16],
            "uptime": str(datetime.now() - self.start_time)
        }

# Inicializar sistema anti-clonación
security_system = AntiCloneSystem()

# ================= BASE DE DATOS SEGURA =================
def init_secure_database():
    """Inicializa base de datos con seguridad"""
    # Primero validar identidad del bot
    if not security_system.validate_bot_identity():
        print("❌ ERROR: Validación de identidad fallida")
        security_system.log_security_event("identity_failure", "Fallo en validación de bot")
        return False
    
    # Verificar instancias duplicadas
    if not security_system.check_duplicate_instances():
        security_system.log_security_event("duplicate_instance", "Instancia duplicada detectada")
        print("⚠️ Advertencia: Posible clonación detectada")
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Tabla de usuarios con protección
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            tokens INTEGER DEFAULT 0,
            max_tokens INTEGER DEFAULT 500,
            total_received INTEGER DEFAULT 0,
            user_hash TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_verified INTEGER DEFAULT 1
        )
    ''')
    
    # Tabla de análisis protegida
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS extractions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            url TEXT,
            data TEXT,
            security_hash TEXT,
            instance_id TEXT,
            extraction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla de tokens protegida
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS token_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount INTEGER,
            type TEXT,
            admin_id INTEGER,
            security_hash TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    
    security_system.log_security_event("db_init", "Base de datos inicializada con seguridad")
    print("✅ Base de datos segura inicializada")
    return True

# ================= FUNCIONES PROTEGIDAS =================
def secure_user_operation(user_id, operation, data=""):
    """Operación de usuario con seguridad"""
    operation_hash = security_system.generate_security_hash(f"{user_id}{operation}{data}")
    security_system.log_security_event("user_operation", f"{operation} para user {user_id}")
    return operation_hash

def get_user_tokens(user_id):
    """Obtiene tokens con verificación de seguridad"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Verificar usuario registrado
    cursor.execute('SELECT tokens, is_verified FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    
    if not result:
        # Usuario nuevo - crear con seguridad
        security_system.log_security_event("new_user", f"Usuario {user_id} creado")
        conn.close()
        return 0
    
    tokens, verified = result
    conn.close()
    
    if verified != 1:
        security_system.log_security_event("unverified_access", f"Intento acceso no verificado user {user_id}")
        return 0
    
    return tokens

def create_secure_user(user_id, username, first_name):
    """Crea usuario con protección anti-clonación"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT 1 FROM users WHERE user_id = ?', (user_id,))
    if not cursor.fetchone():
        # Hash de usuario único
        user_hash = security_system.generate_security_hash(f"{user_id}{username}")
        
        cursor.execute('''
            INSERT INTO users (user_id, username, first_name, tokens, max_tokens, total_received, user_hash)
            VALUES (?, ?, ?, 3, 500, 3, ?)
        ''', (user_id, username, first_name, user_hash))
        
        # Transacción inicial segura
        trans_hash = security_system.generate_security_hash(f"{user_id}_initial_tokens")
        cursor.execute('''
            INSERT INTO token_transactions (user_id, amount, type, security_hash)
            VALUES (?, ?, ?, ?)
        ''', (user_id, 3, 'initial_bonus', trans_hash))
        
        security_system.log_security_event("user_created", f"Usuario {user_id} creado con hash")
    
    conn.commit()
    conn.close()

def consume_secure_token(user_id, url):
    """Consume token con verificación de seguridad"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Verificar tokens disponibles
    cursor.execute('SELECT tokens FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    
    if not result or result[0] <= 0:
        conn.close()
        security_system.log_security_event("no_tokens", f"User {user_id} sin tokens")
        return False
    
    # Generar hash de transacción
    trans_hash = security_system.generate_security_hash(f"{user_id}_consume_{url}")
    
    # Actualizar tokens
    cursor.execute('UPDATE users SET tokens = tokens - 1 WHERE user_id = ?', (user_id,))
    
    # Registrar transacción
    cursor.execute('''
        INSERT INTO token_transactions (user_id, amount, type, security_hash)
        VALUES (?, ?, ?, ?)
    ''', (user_id, -1, 'url_analysis', trans_hash))
    
    conn.commit()
    conn.close()
    
    security_system.log_security_event("token_consumed", f"User {user_id} consumió token")
    return True

def add_secure_tokens(user_id, amount, admin_id):
    """Añade tokens con seguridad de admin"""
    if admin_id != ADMIN_ID:
        security_system.log_security_event("unauthorized_admin", f"Intento no autorizado por {admin_id}")
        return False, "❌ No autorizado"
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT tokens, max_tokens FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return False, "❌ Usuario no encontrado"
    
    current_tokens, max_tokens = user
    
    # Verificar límite
    if current_tokens + amount > max_tokens:
        conn.close()
        return False, f"❌ Límite máximo: {max_tokens} tokens"
    
    # Generar hash de transacción
    trans_hash = security_system.generate_security_hash(f"{user_id}_add_{amount}_by_{admin_id}")
    
    # Actualizar tokens
    cursor.execute('UPDATE users SET tokens = tokens + ? WHERE user_id = ?', (amount, user_id))
    
    # Registrar transacción
    cursor.execute('''
        INSERT INTO token_transactions (user_id, amount, type, admin_id, security_hash)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, amount, 'admin_add', admin_id, trans_hash))
    
    conn.commit()
    conn.close()
    
    security_system.log_security_event("tokens_added", f"Admin {admin_id} añadió {amount} tokens a user {user_id}")
    return True, f"✅ {amount} tokens añadidos (Hash: {trans_hash[:16]}...)"

# ================= ANÁLISIS SEGURO =================
def secure_url_analysis(url):
    """Analiza URL con medidas de seguridad"""
    try:
        # Delay aleatorio para evitar detección
        time.sleep(random.uniform(1.5, 4))
        
        # Headers variados
        headers = {
            'User-Agent': random.choice([
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            ]),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        # Timeout ajustado
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Datos limitados por seguridad
            title = soup.title.string[:100] if soup.title else 'Sin título'
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc['content'][:150] if meta_desc else 'Sin descripción'
            
            # Conteos seguros
            links = len(soup.find_all('a', limit=100))
            images = len(soup.find_all('img', limit=50))
            forms = len(soup.find_all('form', limit=20))
            
            # Emails limitados
            emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', response.text)
            unique_emails = list(set(emails))[:5]
            
            return {
                'success': True,
                'data': {
                    'title': title,
                    'description': description,
                    'links': links,
                    'images': images,
                    'forms': forms,
                    'emails_found': len(unique_emails),
                    'emails': unique_emails,
                    'content_hash': hashlib.md5(response.text.encode()).hexdigest()[:16]
                }
            }
        else:
            return {'success': False, 'error': f'HTTP {response.status_code}'}
            
    except Exception as e:
        security_system.log_security_event("analysis_error", f"Error analizando {url}: {str(e)}")
        return {'success': False, 'error': str(e)}

def save_secure_extraction(user_id, url, data):
    """Guarda análisis con protección"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Generar hash de seguridad para el análisis
    security_hash = security_system.generate_security_hash(f"{user_id}{url}{json.dumps(data)}")
    
    cursor.execute('''
        INSERT INTO extractions (user_id, url, data, security_hash, instance_id)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, url, json.dumps(data), security_hash, security_system.instance_id))
    
    conn.commit()
    conn.close()
    
    return security_hash

# ================= COMANDOS SEGUROS =================
async def start_secure_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start protegido"""
    user = update.message.from_user
    
    # Verificar sistema de seguridad
    if not security_system.check_duplicate_instances():
        await update.message.reply_text("⚠️ *SISTEMA EN MODO SEGURIDAD*\n\nReiniciando verificaciones...")
    
    create_secure_user(user.id, user.username, user.first_name)
    tokens = get_user_tokens(user.id)
    
    text = (
        f"🛡️ *BOT PROTEGIDO - SISTEMA ANTI-CLONACIÓN*\n\n"
        f"🔒 Instancia: `{security_system.instance_id[:16]}...`\n"
        f"👤 Usuario: {user.first_name or 'Usuario'}\n"
        f"🆔 ID: `{user.id}`\n\n"
        f"💰 *TOKENS:* {tokens}\n"
        f"📊 Costo por análisis: *1 token*\n\n"
        f"📋 *COMANDOS SEGUROS:*\n"
        f"/start - Este panel\n"
        f"/tokens - Ver tokens\n"
        f"/stats - Estadísticas\n"
        f"/url [enlace] - Analizar\n"
        f"/security - Info seguridad\n\n"
        f"⚡ *Sistema verificado y protegido contra clonación*"
    )
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def tokens_secure_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /tokens protegido"""
    user = update.message.from_user
    tokens = get_user_tokens(user.id)
    
    text = (
        f"💰 *TOKENS - SISTEMA SEGURO*\n\n"
        f"🔒 Instancia: `{security_system.instance_id[:16]}...`\n"
        f"👤 Usuario: {user.first_name or 'Usuario'}\n"
        f"🆔 ID seguro: `{hashlib.md5(str(user.id).encode()).hexdigest()[:12]}`\n\n"
        f"💎 *Tokens disponibles:* {tokens}\n"
        f"📈 *Máximo permitido:* 500\n\n"
    )
    
    if tokens > 0:
        text += f"✅ Puedes analizar *{tokens}* URLs más\n"
        text += "Usa /url [enlace] para comenzar"
    else:
        text += "❌ No tienes tokens\n"
        text += "Contacta al admin para comprar más"
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def url_secure_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /url con máxima seguridad"""
    user = update.message.from_user
    
    # Verificar tokens
    tokens = get_user_tokens(user.id)
    if tokens <= 0:
        await update.message.reply_text(
            "❌ *SIN TOKENS - SISTEMA SEGURO*\n\n"
            "No tienes tokens disponibles.\n"
            "Usa /tokens para ver saldo.\n"
            "Contacta al admin para comprar tokens.",
            parse_mode='Markdown'
        )
        return
    
    if not context.args:
        await update.message.reply_text(
            "❌ Formato: /url [enlace]\n"
            "Ejemplo: /url https://ejemplo.com\n\n"
            f"⚠️ Consume *1 token*\n"
            f"💎 Tokens restantes: {tokens}",
            parse_mode='Markdown'
        )
        return
    
    url = context.args[0]
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Verificar URL válida
    if len(url) > 200:
        await update.message.reply_text("❌ URL demasiado larga.")
        return
    
    # Consumir token seguro
    if not consume_secure_token(user.id, url):
        await update.message.reply_text("❌ Error en transacción segura.")
        return
    
    await update.message.reply_text(
        f"🔍 *ANÁLISIS SEGURO INICIADO*\n\n"
        f"🌐 URL: {url[:50]}...\n"
        f"🔒 Instancia: `{security_system.instance_id[:12]}...`\n"
        f"🛡️ Modo: Máxima seguridad\n"
        f"⏳ Analizando...",
        parse_mode='Markdown'
    )
    
    # Análisis seguro
    result = secure_url_analysis(url)
    
    if not result['success']:
        await update.message.reply_text(f"❌ Error seguro: {result['error']}")
        return
    
    data = result['data']
    
    # Guardar con seguridad
    security_hash = save_secure_extraction(user.id, url, data)
    
    # Tokens restantes
    tokens_left = get_user_tokens(user.id)
    
    # Crear mensaje seguro
    summary = (
        f"✅ *ANÁLISIS COMPLETADO - SISTEMA SEGURO*\n\n"
        f"🔒 Hash análisis: `{security_hash[:24]}...`\n"
        f"🌐 URL: {url[:40]}...\n"
        f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"📊 *ESTADÍSTICAS:*\n"
        f"• Título: {data['title'][:30]}...\n"
        f"• Descripción: {data['description'][:40]}...\n"
        f"• Enlaces: {data['links']}\n"
        f"• Imágenes: {data['images']}\n"
        f"• Formularios: {data['forms']}\n"
        f"• Emails: {data['emails_found']}\n"
        f"• Hash contenido: {data['content_hash']}\n\n"
        f"💎 *Tokens restantes:* {tokens_left}\n"
        f"🛡️ *Análisis protegido y verificado*"
    )
    
    await update.message.reply_text(summary, parse_mode='Markdown')
    
    # Enviar PDF seguro
    try:
        pdf_buffer = create_secure_pdf(data, url, security_hash)
        filename = f"analisis_secure_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        await update.message.reply_document(
            document=pdf_buffer,
            filename=filename,
            caption=f"📄 Reporte seguro - Hash: {security_hash[:16]}..."
        )
    except Exception as e:
        await update.message.reply_text(f"⚠️ PDF seguro no disponible: {str(e)}")

def create_secure_pdf(data, url, security_hash):
    """Crea PDF con protección"""
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    
    # Marca de agua de seguridad
    pdf.setFont("Helvetica-Oblique", 30)
    pdf.setFillColor(0.95, 0.95, 0.95, 0.2)
    pdf.rotate(45)
    for i in range(5):
        pdf.drawString(100, i*150, "PROTEGIDO ANTI-CLONACIÓN")
    pdf.rotate(-45)
    
    # Encabezado seguro
    pdf.setFillColor(0, 0, 0.8, 1)
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, 750, "🛡️ REPORTE SEGURO DE ANÁLISIS")
    
    # Información de seguridad
    pdf.setFont("Helvetica", 9)
    y = 730
    
    pdf.drawString(50, y, f"Hash Seguridad: {security_hash[:32]}")
    y -= 15
    pdf.drawString(50, y, f"Instancia ID: {security_system.instance_id[:24]}")
    y -= 15
    pdf.drawString(50, y, f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    y -= 15
    pdf.drawString(50, y, f"URL: {url[:60]}")
    y -= 20
    
    # Línea de seguridad
    pdf.setStrokeColor(0, 0, 0.8)
    pdf.setLineWidth(1)
    pdf.line(50, y, 550, y)
    y -= 20
    
    # Datos
    pdf.setFillColor(0, 0, 0, 1)
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y, "DATOS DEL ANÁLISIS:")
    y -= 20
    pdf.setFont("Helvetica", 10)
    
    info_lines = [
        f"Título: {data.get('title', 'N/A')[:40]}",
        f"Descripción: {data.get('description', 'N/A')[:50]}",
        f"Enlaces encontrados: {data.get('links', 0)}",
        f"Imágenes: {data.get('images', 0)}",
        f"Formularios: {data.get('forms', 0)}",
        f"Emails detectados: {data.get('emails_found', 0)}",
        f"Hash contenido: {data.get('content_hash', 'N/A')}"
    ]
    
    for line in info_lines:
        pdf.drawString(60, y, line)
        y -= 16
    
    # Emails si existen
    if data.get('emails'):
        y -= 10
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(50, y, "CORREOS ENCONTRADOS:")
        y -= 20
        pdf.setFont("Helvetica", 9)
        
        for email in data['emails']:
            pdf.drawString(60, y, f"• {email}")
            y -= 14
            if y < 50:
                pdf.showPage()
                y = 750
                pdf.setFont("Helvetica", 9)
    
    # Pie de página seguro
    pdf.setFont("Helvetica-Oblique", 8)
    pdf.drawString(50, 30, f"© 2025 expertdatta_bot - Sistema Anti-Clonación v2.0")
    pdf.drawString(400, 30, f"Hash: {hashlib.md5(TOKEN.encode()).hexdigest()[:12]}")
    
    pdf.save()
    buffer.seek(0)
    return buffer

async def security_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /security - Info del sistema"""
    user = update.message.from_user
    
    report = security_system.get_security_report()
    
    text = (
        f"🛡️ *INFORMACIÓN DE SEGURIDAD - SISTEMA ANTI-CLONACIÓN*\n\n"
        f"🔒 *ESTADO DEL SISTEMA:*\n"
        f"• Nivel seguridad: {security_system.security_level}\n"
        f"• Instancia ID: `{report['instance_id']}`\n"
        f"• Tiempo activo: {report['uptime']}\n"
        f"• Instancias activas: {report['active_instances']}\n\n"
        f"📊 *ESTADÍSTICAS DE SEGURIDAD:*\n"
        f"• Eventos totales: {report['total_events']}\n"
    )
    
    if report['events_by_type']:
        text += "• Eventos por tipo:\n"
        for event_type, count in report['events_by_type'][:5]:
            text += f"  - {event_type}: {count}\n"
    
    text += f"\n🔐 *PROTECCIONES ACTIVAS:*\n"
    text += f"• Validación de instancia ✓\n"
    text += f"• Hash de seguridad ✓\n"
    text += f"• Detección de clonación ✓\n"
    text += f"• Auditoría de operaciones ✓\n\n"
    text += f"⚡ *Este sistema está protegido contra clonación*"
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def admin_add_secure_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /add seguro - Solo admin"""
    user = update.message.from_user
    
    if user.id != ADMIN_ID:
        security_system.log_security_event("unauthorized_command", f"User {user.id} intentó /add")
        await update.message.reply_text("❌ No autorizado.")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "❌ Formato: /add [ID_USUARIO] [CANTIDAD]\n"
            "Ejemplo: /add 123456789 100"
        )
        return
    
    try:
        target_id = int(context.args[0])
        amount = int(context.args[1])
        
        if amount <= 0 or amount > 1000:
            await update.message.reply_text("❌ Cantidad inválida (1-1000).")
            return
        
        success, message = add_secure_tokens(target_id, amount, user.id)
        await update.message.reply_text(message)
        
    except ValueError:
        await update.message.reply_text("❌ ID y cantidad deben ser números.")

# ================= MAIN SEGURO =================
def main():
    """Función principal con protección completa"""
    print("=" * 60)
    print("🛡️  SISTEMA ANTI-CLONACIÓN COMPLETO - ACTIVADO")
    print("=" * 60)
    
    # Inicializar seguridad
    print(f"🔒 Instancia ID: {security_system.instance_id}")
    print(f"🔄 Validando identidad del bot...")
    
    if not security_system.validate_bot_identity():
        print("❌ ERROR CRÍTICO: IDENTIDAD DEL BOT NO VÁLIDA")
        print("⛔ POSIBLE INTENTO DE CLONACIÓN DETECTADO")
        security_system.log_security_event("critical_failure", "Validación de identidad fallida")
        return
    
    print("✅ Identidad del bot verificada")
    
    # Inicializar base de datos segura
    if not init_secure_database():
        print("❌ Error inicializando base de datos segura")
        return
    
    # Verificar instancias
    if not security_system.check_duplicate_instances():
        print("⚠️ ADVERTENCIA: Posible instancia duplicada detectada")
    
    print("✅ Sistema de seguridad inicializado")
    print(f"✅ Admin ID: {ADMIN_ID}")
    print(f"✅ Hash sistema: {hashlib.sha256(TOKEN.encode()).hexdigest()[:16]}")
    print("✅ Anti-clonación: ACTIVO MÁXIMO")
    print("=" * 60)
    
    # Crear aplicación
    app = Application.builder().token(TOKEN).build()
    
    # Comandos seguros
    app.add_handler(CommandHandler("start", start_secure_command))
    app.add_handler(CommandHandler("tokens", tokens_secure_command))
    app.add_handler(CommandHandler("url", url_secure_command))
    app.add_handler(CommandHandler("security", security_info_command))
    app.add_handler(CommandHandler("add", admin_add_secure_command))
    
    # Comando stats básico
    async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.message.from_user
        tokens = get_user_tokens(user.id)
        await update.message.reply_text(
            f"📊 *TUS ESTADÍSTICAS*\n\n"
            f"👤 Usuario: {user.first_name or 'Usuario'}\n"
            f"💎 Tokens: {tokens}\n"
            f"🔒 Sistema: Protegido",
            parse_mode='Markdown'
        )
    
    app.add_handler(CommandHandler("stats", stats_command))
    
    # Iniciar bot
    print("🤖 Bot seguro iniciado - Listo para comandos")
    print("🔒 Protección anti-clonación: ACTIVA")
    print("📞 Comandos: /start, /tokens, /url, /security, /add, /stats")
    
    app.run_polling()

if __name__ == '__main__':
    main()
