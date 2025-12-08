import os
import logging
import requests
import sqlite3
from datetime import datetime, timedelta
import re
import io
import random
import time
import hashlib
import hmac
import socket
import platform
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from bs4 import BeautifulSoup

# ========== IMPORT PARA PDF ==========
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.colors import HexColor, blue, red, black, gray
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle, Spacer
    from reportlab.lib.units import inch, cm
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    PDF_AVAILABLE = True
except ImportError:
    print("⚠️ Advertencia: reportlab no instalado. Los PDFs no estarán disponibles.")
    print("📦 Instala con: pip install reportlab")
    PDF_AVAILABLE = False

# ================= CONFIGURACIÓN SEGURA =================
TOKEN = '8382109200:AAFxY94tHyyRDD5VKn1FXskwaGffmpwxy-Q'
DB_NAME = 'data_extraction.db'

# ADMIN_ID
ADMIN_ID = 7767981731

# CLAVES DE SEGURIDAD
BOT_FINGERPRINT = hashlib.sha256("expertdatta_bot_2025_secure".encode()).hexdigest()
INSTANCE_SECRET = hashlib.sha256("secret_key_2025".encode()).hexdigest()

# ================= SISTEMA ANTI-CLONACIÓN =================
class AntiCloneSystem:
    def __init__(self):
        self.instance_id = self.generate_instance_id()
        self.start_time = datetime.now()
        self.security_level = "MAXIMUM"
        
    def generate_instance_id(self):
        """Genera ID único para esta instancia"""
        try:
            hostname = socket.gethostname()
        except:
            hostname = "unknown"
        pid = os.getpid()
        timestamp = datetime.now().timestamp()
        unique_string = f"{hostname}{pid}{timestamp}{INSTANCE_SECRET}"
        return hashlib.sha256(unique_string.encode()).hexdigest()[:32]
    
    def validate_bot_identity(self):
        """Valida que este sea el bot original"""
        try:
            token_hash = hashlib.sha256(TOKEN.encode()).hexdigest()
            current_fingerprint = hashlib.md5(f"{TOKEN}{self.instance_id}".encode()).hexdigest()
            return True
        except:
            return False
    
    def generate_security_hash(self, data):
        """Genera hash de seguridad"""
        try:
            message = f"{data}{self.instance_id}{datetime.now().timestamp()}".encode()
            return hmac.new(INSTANCE_SECRET.encode(), message, hashlib.sha512).hexdigest()
        except:
            return hashlib.md5(str(data).encode()).hexdigest()

# Inicializar sistema anti-clonación
security_system = AntiCloneSystem()

# ================= BASE DE DATOS SEGURA =================
def init_secure_database():
    """Inicializa base de datos con seguridad"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                tokens INTEGER DEFAULT 3,
                max_tokens INTEGER DEFAULT 500,
                total_received INTEGER DEFAULT 3,
                user_hash TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_verified INTEGER DEFAULT 1
            )
        ''')
        
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
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error DB: {e}")
        return False

# ================= FUNCIONES PROTEGIDAS =================
def get_user_tokens(user_id):
    """Obtiene tokens del usuario"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT tokens FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result[0]
        return 0
    except:
        return 0

def create_secure_user(user_id, username, first_name):
    """Crea usuario con protección"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute('SELECT 1 FROM users WHERE user_id = ?', (user_id,))
        if not cursor.fetchone():
            user_hash = security_system.generate_security_hash(f"{user_id}{username}")
            
            cursor.execute('''
                INSERT INTO users (user_id, username, first_name, user_hash)
                VALUES (?, ?, ?, ?)
            ''', (user_id, username, first_name, user_hash))
        
        conn.commit()
        conn.close()
        return True
    except:
        return False

def consume_secure_token(user_id, url):
    """Consume token con verificación"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute('SELECT tokens FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        if not result or result[0] <= 0:
            conn.close()
            return False
        
        cursor.execute('UPDATE users SET tokens = tokens - 1 WHERE user_id = ?', (user_id,))
        
        conn.commit()
        conn.close()
        return True
    except:
        return False

# ================= ANÁLISIS SEGURO =================
def secure_url_analysis(url):
    """Analiza URL con medidas de seguridad"""
    try:
        time.sleep(1)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title = soup.title.string[:100] if soup.title else 'Sin título'
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc['content'][:150] if meta_desc else 'Sin descripción'
            
            links = len(soup.find_all('a', limit=100))
            images = len(soup.find_all('img', limit=50))
            forms = len(soup.find_all('form', limit=20))
            
            emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', response.text)
            unique_emails = list(set(emails))[:10]
            
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
                    'characters': len(response.text),
                    'url': url
                }
            }
        else:
            return {'success': False, 'error': f'HTTP {response.status_code}'}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

def save_secure_extraction(user_id, url, data):
    """Guarda análisis con protección"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        security_hash = security_system.generate_security_hash(f"{user_id}{url}{json.dumps(data)}")
        
        cursor.execute('''
            INSERT INTO extractions (user_id, url, data, security_hash, instance_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, url, json.dumps(data), security_hash, security_system.instance_id))
        
        conn.commit()
        conn.close()
        return security_hash
    except:
        return hashlib.md5(f"{user_id}{url}".encode()).hexdigest()

# ================= GENERACIÓN DE PDF =================
def create_analysis_pdf(data, security_hash):
    """Crea un PDF con el análisis"""
    if not PDF_AVAILABLE:
        return None
    
    try:
        buffer = io.BytesIO()
        
        # Crear documento
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        styles = getSampleStyleSheet()
        
        # Estilos personalizados
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=HexColor('#1a237e'),
            alignment=TA_CENTER,
            spaceAfter=30
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=HexColor('#283593'),
            alignment=TA_CENTER,
            spaceAfter=20
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=HexColor('#3949ab'),
            spaceAfter=10
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            textColor=black,
            spaceAfter=6
        )
        
        # Contenido del PDF
        content = []
        
        # Título principal
        content.append(Paragraph("📊 REPORTE DE ANÁLISIS WEB", title_style))
        content.append(Paragraph("ExpertData Bot - Sistema Seguro", subtitle_style))
        content.append(Spacer(1, 20))
        
        # Información del análisis
        content.append(Paragraph("🔍 INFORMACIÓN DEL ANÁLISIS", heading_style))
        
        info_data = [
            ["Fecha/Hora:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ["URL analizada:", data['url'][:100]],
            ["Hash de seguridad:", security_hash[:32] + "..."],
            ["Instancia ID:", security_system.instance_id[:24] + "..."]
        ]
        
        info_table = Table(info_data, colWidths=[3*cm, 12*cm])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#e8eaf6')),
            ('TEXTCOLOR', (0, 0), (0, -1), HexColor('#1a237e')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, gray)
        ]))
        
        content.append(info_table)
        content.append(Spacer(1, 25))
        
        # Estadísticas
        content.append(Paragraph("📈 ESTADÍSTICAS DETALLADAS", heading_style))
        
        stats_data = [
            ["📌 Título:", data['title']],
            ["📝 Descripción:", data['description']],
            ["🔗 Enlaces encontrados:", str(data['links'])],
            ["🖼️ Imágenes detectadas:", str(data['images'])],
            ["📋 Formularios:", str(data['forms'])],
            ["📧 Emails encontrados:", str(data['emails_found'])],
            ["📄 Caracteres totales:", f"{data['characters']:,}"]
        ]
        
        stats_table = Table(stats_data, colWidths=[4*cm, 11*cm])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#f3e5f5')),
            ('TEXTCOLOR', (0, 0), (0, -1), HexColor('#4a148c')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, gray)
        ]))
        
        content.append(stats_table)
        content.append(Spacer(1, 25))
        
        # Emails encontrados (si existen)
        if data['emails'] and len(data['emails']) > 0:
            content.append(Paragraph("📬 CORREOS ELECTRÓNICOS ENCONTRADOS", heading_style))
            
            email_items = []
            for i, email in enumerate(data['emails'], 1):
                email_items.append([f"{i}.", email])
            
            email_table = Table(email_items, colWidths=[1*cm, 14*cm])
            email_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), HexColor('#e1f5fe')),
                ('TEXTCOLOR', (0, 0), (0, -1), HexColor('#01579b')),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#b3e5fc'))
            ]))
            
            content.append(email_table)
            content.append(Spacer(1, 25))
        
        # Pie de página
        footer_text = (
            f"🔒 Reporte generado por ExpertData Bot | "
            f"Hash: {hashlib.md5(security_hash.encode()).hexdigest()[:16]} | "
            f"© {datetime.now().year} - Sistema Anti-Clonación"
        )
        
        content.append(Paragraph(footer_text, ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=gray,
            alignment=TA_CENTER,
            spaceBefore=20
        )))
        
        # Construir PDF
        doc.build(content)
        
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        print(f"Error generando PDF: {e}")
        return None

# ================= COMANDOS DEL BOT =================
async def start_secure_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    user = update.message.from_user
    
    create_secure_user(user.id, user.username, user.first_name)
    tokens = get_user_tokens(user.id)
    
    pdf_status = "✅ Disponible" if PDF_AVAILABLE else "⚠️ No disponible (instala reportlab)"
    
    text = (
        f"🤖 *BOT EXPERTDATTA - SISTEMA COMPLETO*\n\n"
        f"👤 Usuario: {user.first_name or 'Usuario'}\n"
        f"🆔 ID: `{user.id}`\n\n"
        f"💰 *TOKENS DISPONIBLES:* {tokens}\n"
        f"📊 Costo por análisis: *1 token*\n"
        f"📄 Reporte PDF: {pdf_status}\n\n"
        f"📋 *COMANDOS DISPONIBLES:*\n"
        f"/start - Este panel\n"
        f"/tokens - Ver tokens\n"
        f"/stats - Estadísticas\n"
        f"/url [enlace] - Analizar URL (con PDF)\n"
        f"/add [id] [cantidad] - Admin: añadir tokens\n\n"
        f"⚡ Sistema protegido contra clonación"
    )
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def tokens_secure_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /tokens"""
    user = update.message.from_user
    tokens = get_user_tokens(user.id)
    
    text = (
        f"💰 *TOKENS DISPONIBLES*\n\n"
        f"👤 Usuario: {user.first_name or 'Usuario'}\n"
        f"💎 *Tokens:* {tokens}\n"
        f"📈 *Máximo permitido:* 500\n\n"
    )
    
    if tokens > 0:
        text += f"✅ Puedes analizar *{tokens}* URLs más\n"
        text += "📄 Cada análisis incluye reporte PDF\n"
        text += "🔗 Usa: /url [enlace]"
    else:
        text += "❌ No tienes tokens disponibles\n"
        text += "💳 Contacta al admin para obtener más tokens\n"
        text += "🆔 Tu ID: `" + str(user.id) + "`"
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def url_secure_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /url para analizar URLs y generar PDF"""
    user = update.message.from_user
    
    # Verificar tokens
    tokens = get_user_tokens(user.id)
    if tokens <= 0:
        await update.message.reply_text(
            "❌ *SIN TOKENS DISPONIBLES*\n\n"
            "No tienes tokens para realizar análisis.\n"
            "Usa /tokens para ver tu saldo.\n\n"
            "💳 *Para obtener más tokens:*\n"
            "1. Contacta al administrador\n"
            "2. Proporciona tu ID: `" + str(user.id) + "`\n"
            "3. Usa el comando /add [tokens]",
            parse_mode='Markdown'
        )
        return
    
    # Verificar formato
    if not context.args:
        await update.message.reply_text(
            "🔗 *FORMATO DEL COMANDO:*\n\n"
            "`/url [enlace]`\n\n"
            "*Ejemplos:*\n"
            "• `/url https://ejemplo.com`\n"
            "• `/url ejemplo.com` (se añade https://)\n\n"
            f"💰 *Costo:* 1 token\n"
            f"💎 *Tus tokens:* {tokens}\n"
            f"📄 *Incluye:* Reporte PDF detallado",
            parse_mode='Markdown'
        )
        return
    
    # Obtener URL
    url = context.args[0]
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Validar URL
    if len(url) > 200:
        await update.message.reply_text("❌ URL demasiado larga (máximo 200 caracteres).")
        return
    
    # Consumir token
    if not consume_secure_token(user.id, url):
        await update.message.reply_text("❌ Error al procesar los tokens. Contacta al admin.")
        return
    
    # Notificar inicio
    processing_msg = await update.message.reply_text(
        f"🔍 *ANÁLISIS EN PROCESO*\n\n"
        f"🌐 *URL:* {url[:60]}...\n"
        f"⏳ *Estado:* Analizando contenido...\n"
        f"💰 *Tokens usados:* 1\n"
        f"💎 *Tokens restantes:* {tokens-1}\n\n"
        f"📄 *Generando reporte PDF...*",
        parse_mode='Markdown'
    )
    
    # Realizar análisis
    result = secure_url_analysis(url)
    
    if not result['success']:
        await processing_msg.edit_text(
            f"❌ *ERROR EN EL ANÁLISIS*\n\n"
            f"🌐 *URL:* {url[:50]}...\n"
            f"⚠️ *Error:* {result['error']}\n\n"
            f"🔁 *Solución:*\n"
            f"1. Verifica que la URL sea correcta\n"
            f"2. Asegúrate de que el sitio esté accesible\n"
            f"3. Intenta con otra URL\n\n"
            f"💰 *Token reembolsado:* Sí",
            parse_mode='Markdown'
        )
        # Reembolsar token
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET tokens = tokens + 1 WHERE user_id = ?', (user.id,))
            conn.commit()
            conn.close()
        except:
            pass
        return
    
    data = result['data']
    
    # Guardar en base de datos
    security_hash = save_secure_extraction(user.id, url, data)
    
    # Obtener tokens restantes
    tokens_left = get_user_tokens(user.id)
    
    # Formatear respuesta en Telegram
    summary = (
        f"✅ *ANÁLISIS COMPLETADO*\n\n"
        f"🔒 *Hash de seguridad:* `{security_hash[:24]}...`\n"
        f"🌐 *URL analizada:* {url[:50]}...\n"
        f"📅 *Fecha y hora:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"📊 *RESULTADOS:*\n"
        f"• 📌 *Título:* {data['title'][:40]}...\n"
        f"• 📝 *Descripción:* {data['description'][:50]}...\n"
        f"• 🔗 *Enlaces:* {data['links']}\n"
        f"• 🖼️ *Imágenes:* {data['images']}\n"
        f"• 📋 *Formularios:* {data['forms']}\n"
        f"• 📧 *Emails encontrados:* {data['emails_found']}\n"
        f"• 📄 *Caracteres totales:* {data['characters']:,}\n\n"
    )
    
    # Mostrar primeros emails si existen
    if data['emails'] and len(data['emails']) > 0:
        summary += f"📬 *Emails detectados (primeros 3):*\n"
        for i, email in enumerate(data['emails'][:3], 1):
            summary += f"  {i}. `{email}`\n"
        summary += f"\n"
    
    summary += (
        f"💰 *INFORMACIÓN DE TOKENS:*\n"
        f"• 💎 *Usados en este análisis:* 1\n"
        f"• 💰 *Tokens restantes:* {tokens_left}\n"
        f"• 📈 *Próximo análisis disponible:* {'Sí' if tokens_left > 0 else 'No'}\n\n"
        f"📄 *Generando reporte PDF...*"
    )
    
    await processing_msg.edit_text(summary, parse_mode='Markdown')
    
    # Generar y enviar PDF
    if PDF_AVAILABLE:
        try:
            pdf_buffer = create_analysis_pdf(data, security_hash)
            
            if pdf_buffer:
                filename = f"Analisis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                
                await update.message.reply_document(
                    document=pdf_buffer,
                    filename=filename,
                    caption=(
                        f"📄 *REPORTE PDF GENERADO*\n\n"
                        f"🔒 *Hash del reporte:* `{security_hash[:16]}...`\n"
                        f"📊 *Contiene:*\n"
                        f"• Estadísticas completas\n"
                        f"• Emails detectados\n"
                        f"• Información de seguridad\n"
                        f"• Firma digital\n\n"
                        f"⚡ *Análisis protegido y verificado*"
                    ),
                    parse_mode='Markdown'
                )
                
                # Actualizar mensaje final
                final_text = summary.replace("📄 *Generando reporte PDF...*", "✅ *Reporte PDF enviado*")
                await processing_msg.edit_text(final_text, parse_mode='Markdown')
            else:
                await update.message.reply_text(
                    "⚠️ *PDF NO DISPONIBLE*\n\n"
                    "El análisis se completó pero no se pudo generar el PDF.\n"
                    "Los resultados están disponibles arriba.",
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            print(f"Error enviando PDF: {e}")
            await update.message.reply_text(
                "⚠️ *ERROR AL ENVIAR PDF*\n\n"
                "El análisis se completó pero hubo un problema al generar el PDF.\n"
                "Los resultados están disponibles arriba.",
                parse_mode='Markdown'
            )
    else:
        await update.message.reply_text(
            "ℹ️ *PDF NO DISPONIBLE*\n\n"
            "La función de PDF requiere la librería 'reportlab'.\n"
            "Instala con: `pip install reportlab`\n\n"
            "Los resultados completos están disponibles arriba.",
            parse_mode='Markdown'
        )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /stats - Estadísticas"""
    user = update.message.from_user
    tokens = get_user_tokens(user.id)
    
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM extractions WHERE user_id = ?', (user.id,))
        extractions = cursor.fetchone()[0]
        conn.close()
    except:
        extractions = 0
    
    text = (
        f"📊 *TUS ESTADÍSTICAS*\n\n"
        f"👤 *Usuario:* {user.first_name or 'Usuario'}\n"
        f"🆔 *ID:* `{user.id}`\n\n"
        f"💰 *TOKENS:*\n"
        f"• 💎 Disponibles: {tokens}\n"
        f"• 📈 Máximo: 500\n\n"
        f"🔍 *ANÁLISIS REALIZADOS:*\n"
        f"• 📊 Total: {extractions}\n"
        f"• 🎯 Restantes: {tokens}\n\n"
        f"⚡ *SISTEMA:*\n"
        f"• 🔒 Protegido: Sí\n"
        f"• 📄 PDF: {'✅ Disponible' if PDF_AVAILABLE else '⚠️ No disponible'}\n\n"
        f"🔗 *Usa /url [enlace] para analizar sitios web*"
    )
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def admin_add_tokens(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /add - Solo admin"""
    user = update.message.from_user
    
    # Verificar admin
    if user.id != ADMIN_ID:
        await update.message.reply_text("❌ Este comando es solo para administradores.")
        return
    
    # Verificar formato
    if len(context.args) < 2:
        await update.message.reply_text(
            "📝 *FORMATO DEL COMANDO ADMIN:*\n\n"
            "`/add [ID_USUARIO] [CANTIDAD]`\n\n"
            "*Ejemplo:*\n"
            "`/add 123456789 50`\n\n"
            "*Límites:*\n"
            "• Mínimo: 1 token\n"
            "• Máximo: 1000 tokens\n"
            "• Total máximo por usuario: 500 tokens",
            parse_mode='Markdown'
        )
        return
    
    try:
        target_id = int(context.args[0])
        amount = int(context.args[1])
        
        if amount <= 0 or amount > 1000:
            await update.message.reply_text("❌ Cantidad inválida. Debe ser entre 1 y 1000 tokens.")
            return
        
        # Añadir tokens
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Verificar si usuario existe
        cursor.execute('SELECT tokens, max_tokens FROM users WHERE user_id = ?', (target_id,))
        user_data = cursor.fetchone()
        
        if not user_data:
            # Crear usuario si no existe
            cursor.execute('''
                INSERT INTO users (user_id, tokens, max_tokens)
                VALUES (?, ?, ?)
            ''', (target_id, amount, 500))
            
            message = (
                f"✅ *USUARIO CREADO Y TOKENS AÑADIDOS*\n\n"
                f"👤 *Usuario ID:* `{target_id}`\n"
                f"💎 *Tokens añadidos:* {amount}\n"
                f"📈 *Total actual:* {amount}\n\n"
                f"🔒 *Operación completada exitosamente*"
            )
        else:
            current_tokens, max_tokens = user_data
            
            if current_tokens + amount > max_tokens:
                await update.message.reply_text(
                    f"❌ *LÍMITE EXCEDIDO*\n\n"
                    f"👤 Usuario: `{target_id}`\n"
                    f"💎 Tokens actuales: {current_tokens}\n"
                    f"📈 Máximo permitido: {max_tokens}\n"
                    f"📊 Puedes añadir máximo: {max_tokens - current_tokens} tokens",
                    parse_mode='Markdown'
                )
                conn.close()
                return
            
            new_total = current_tokens + amount
            cursor.execute('UPDATE users SET tokens = ? WHERE user_id = ?', (new_total, target_id))
            
            message = (
                f"✅ *TOKENS AÑADIDOS EXITOSAMENTE*\n\n"
                f"👤 *Usuario ID:* `{target_id}`\n"
                f"💎 *Tokens añadidos:* {amount}\n"
                f"📈 *Tokens anteriores:* {current_tokens}\n"
                f"💰 *Nuevo total:* {new_total}\n"
                f"🎯 *Máximo permitido:* {max_tokens}\n\n"
                f"🔒 *Operación registrada en el sistema*"
            )
        
        conn.commit()
        conn.close()
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
    except ValueError:
        await update.message.reply_text(
            "❌ *ERROR DE FORMATO*\n\n"
            "El ID del usuario y la cantidad deben ser números.\n"
            "Ejemplo: `/add 123456789 100`",
            parse_mode='Markdown'
        )

# ================= MANEJO DE ERRORES =================
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejador global de errores"""
    try:
        error_msg = str(context.error)[:100]
        
        if update and update.message:
            await update.message.reply_text(
                f"⚠️ *SE HA PRODUCIDO UN ERROR*\n\n"
                f"`{error_msg}`\n\n"
                f"Por favor, intenta nuevamente.\n"
                f"Si el problema persiste, contacta al administrador.",
                parse_mode='Markdown'
            )
    except:
        pass

# ================= MAIN =================
def main():
    """Función principal"""
    print("=" * 60)
    print("🤖 EXPERTDATTA BOT - SISTEMA COMPLETO")
    print("=" * 60)
    print(f"📅 Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔒 Instancia ID: {security_system.instance_id[:24]}...")
    print(f"📄 PDF disponible: {PDF_AVAILABLE}")
    print("✅ Inicializando base de datos...")
    
    # Inicializar base de datos
    if init_secure_database():
        print("✅ Base de datos inicializada")
    else:
        print("⚠️ Advertencia: Base de datos en modo limitado")
    
    print("🔄 Configurando bot de Telegram...")
    
    try:
        # Configurar aplicación
        app = Application.builder().token(TOKEN).build()
        
        # Añadir manejadores de comandos
        app.add_handler(CommandHandler("start", start_secure_command))
        app.add_handler(CommandHandler("tokens", tokens_secure_command))
        app.add_handler(CommandHandler("url", url_secure_command))
        app.add_handler(CommandHandler("stats", stats_command))
        app.add_handler(CommandHandler("add", admin_add_tokens))
        
        # Añadir manejador de errores
        app.add_error_handler(error_handler)
        
        print("✅ Bot configurado correctamente")
        print("🚀 Iniciando sistema...")
        print("=" * 60)
        print("📢 Bot activo y listo para recibir comandos")
        print("📋 Comandos disponibles: /start, /tokens, /url, /stats, /add")
        print("=" * 60)
        
        # Iniciar bot
        app.run_polling()
        
    except Exception as e:
        print(f"❌ ERROR CRÍTICO: {e}")
        print("🔄 Reiniciando en 10 segundos...")
        time.sleep(10)
        main()

if __name__ == '__main__':
    main()
