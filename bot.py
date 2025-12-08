from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import requests
from bs4 import BeautifulSoup
import json
import sqlite3
from datetime import datetime
import re
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io

TOKEN = '8382109200:AAEkp8XpzsvoD6JJ_MemxJwb27EULR1y2EM'
DB_NAME = 'data_extraction.db'

def init_database():
    """Inicializa la base de datos SQLite"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS extracted_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            data_type TEXT,
            content TEXT,
            extraction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def create_pdf_report(data):
    """Crea un PDF con los resultados del análisis"""
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    
    # Título
    pdf.setTitle("Reporte de Análisis Web")
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, 750, "📊 REPORTE DE ANÁLISIS WEB")
    
    # Línea separadora
    pdf.line(50, 740, 550, 740)
    
    # Información básica
    pdf.setFont("Helvetica", 10)
    y_position = 720
    
    pdf.drawString(50, y_position, f"Fecha/Hora: {data['fecha_hora']}")
    y_position -= 20
    pdf.drawString(50, y_position, f"Dominio Web: {data['url']}")
    y_position -= 20
    pdf.drawString(50, y_position, f"Total de Hits: {data['total_hits']} caracteres")
    y_position -= 30
    
    # Estadísticas
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y_position, "ESTADÍSTICAS:")
    y_position -= 20
    pdf.setFont("Helvetica", 10)
    
    stats = [
        f"• Título: {data['titulo'][:50]}...",
        f"• Descripción: {data['descripcion'][:80]}...",
        f"• Enlaces encontrados: {data['enlaces']}",
        f"• Imágenes: {data['imagenes']}",
        f"• Formularios: {data['formularios']}",
        f"• Emails detectados: {data['emails_encontrados']}"
    ]
    
    for stat in stats:
        pdf.drawString(70, y_position, stat)
        y_position -= 18
    
    # Emails encontrados
    if data['emails_detectados']:
        y_position -= 20
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(50, y_position, "CORREOS ELECTRÓNICOS DETECTADOS:")
        y_position -= 20
        pdf.setFont("Helvetica", 10)
        
        for email in data['emails_detectados'][:20]:  # Máximo 20 emails
            pdf.drawString(70, y_position, f"• {email}")
            y_position -= 15
            if y_position < 50:  # Nueva página si se acaba el espacio
                pdf.showPage()
                y_position = 750
    
    # Pie de página
    pdf.setFont("Helvetica-Oblique", 8)
    pdf.drawString(50, 30, f"Reporte generado por expertdatta_bot - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    pdf.save()
    buffer.seek(0)
    return buffer

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    menu_text = (
        "🤖 *BOT DE EXTRACCIÓN DE DATOS*\n\n"
        "Comandos disponibles:\n"
        "/start - Muestra este menú\n"
        "/url [enlace] - Extrae datos y genera PDF\n"
        "/myid - Muestra tu ID de usuario\n"
        "/stats - Muestra estadísticas\n\n"
        "Ejemplo: /url https://ejemplo.com"
    )
    await update.message.reply_text(menu_text, parse_mode='Markdown')

async def url_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /url - Extrae datos y genera PDF"""
    if not context.args:
        await update.message.reply_text(
            "❌ Debes proporcionar una URL.\n"
            "Ejemplo: /url https://ejemplo.com"
        )
        return
    
    url = context.args[0]
    
    # Verificar formato de URL
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    await update.message.reply_text(f"🔍 Analizando: {url}")
    
    try:
        # Extraer datos de la URL
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraer diferentes tipos de datos
            page_title = soup.title.string if soup.title else 'Sin título'
            meta_description = soup.find('meta', attrs={'name': 'description'})
            description = meta_description['content'] if meta_description else 'Sin descripción'
            
            # Contar elementos
            total_links = len(soup.find_all('a'))
            total_images = len(soup.find_all('img'))
            total_forms = len(soup.find_all('form'))
            
            # Extraer emails
            emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', response.text)
            unique_emails = list(set(emails))
            
            # Guardar en base de datos
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO extracted_data (url, data_type, content)
                VALUES (?, ?, ?)
            ''', (url, 'page_analysis', json.dumps({
                'title': page_title,
                'description': description,
                'links': total_links,
                'images': total_images,
                'forms': total_forms,
                'emails_found': len(unique_emails)
            })))
            conn.commit()
            conn.close()
            
            # Preparar datos para PDF
            data_for_pdf = {
                'fecha_hora': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'url': url,
                'total_hits': len(response.text),
                'titulo': page_title,
                'descripcion': description,
                'enlaces': total_links,
                'imagenes': total_images,
                'formularios': total_forms,
                'emails_encontrados': len(unique_emails),
                'emails_detectados': unique_emails
            }
            
            # Crear PDF
            pdf_buffer = create_pdf_report(data_for_pdf)
            
            # Preparar mensaje de resumen
            summary_text = (
                f"📊 *ANÁLISIS COMPLETADO*\n"
                f"Fecha/Hora: {data_for_pdf['fecha_hora']}\n"
                f"Dominio Web: {url}\n"
                f"Total de Hits: {data_for_pdf['total_hits']} caracteres\n\n"
                f"*ESTADÍSTICAS:*\n"
                f"• Título: {page_title[:50]}...\n"
                f"• Descripción: {description[:80]}...\n"
                f"• Enlaces encontrados: {total_links}\n"
                f"• Imágenes: {total_images}\n"
                f"• Formularios: {total_forms}\n"
                f"• Emails detectados: {len(unique_emails)}\n\n"
                f"📄 *Generando PDF...*"
            )
            
            await update.message.reply_text(summary_text, parse_mode='Markdown')
            
            # Enviar PDF
            pdf_filename = f"analisis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            await update.message.reply_document(
                document=pdf_buffer,
                filename=pdf_filename,
                caption=f"📄 Reporte PDF - {url}"
            )
            
        else:
            await update.message.reply_text(f"❌ Error al acceder a la URL. Código: {response.status_code}")
            
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def myid_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /myid - Muestra ID de usuario"""
    user = update.message.from_user
    user_info = (
        f"👤 *INFORMACIÓN DE USUARIO*\n\n"
        f"• ID: `{user.id}`\n"
        f"• Nombre: {user.first_name or 'No disponible'}\n"
        f"• Apellido: {user.last_name or 'No disponible'}\n"
        f"• Username: @{user.username or 'Sin username'}\n"
        f"• Idioma: {user.language_code or 'No disponible'}\n\n"
        f"Guarda este ID para identificarte."
    )
    await update.message.reply_text(user_info, parse_mode='Markdown')

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /stats - Muestra estadísticas"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM extracted_data')
        total_extracciones = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT url) FROM extracted_data')
        urls_unicas = cursor.fetchone()[0]
        
        cursor.execute('SELECT url, extraction_date FROM extracted_data ORDER BY extraction_date DESC LIMIT 5')
        ultimas = cursor.fetchall()
        
        conn.close()
        
        stats_text = (
            f"📈 *ESTADÍSTICAS DE EXTRACCIÓN*\n\n"
            f"• Extracciones totales: {total_extracciones}\n"
            f"• URLs únicas analizadas: {urls_unicas}\n\n"
            f"*ÚLTIMAS 5 EXTRACCIONES:*\n"
        )
        
        for url, fecha in ultimas:
            stats_text += f"• {url[:30]}... ({fecha})\n"
        
        await update.message.reply_text(stats_text, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error al obtener estadísticas: {str(e)}")

def main():
    """Función principal"""
    # Inicializar base de datos
    init_database()
    
    # Crear aplicación
    app = Application.builder().token(TOKEN).build()
    
    # Añadir handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("url", url_command))
    app.add_handler(CommandHandler("myid", myid_command))
    app.add_handler(CommandHandler("stats", stats_command))
    
    print("🤖 Bot de Extracción de Datos con PDF iniciado")
    print("✅ Comandos disponibles: /start, /url, /myid, /stats")
    
    app.run_polling()

if __name__ == '__main__':
    main()
