import os
import logging
import sqlite3
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)

# Configuración de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Token desde variables de entorno
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Base de datos
def init_database():
    """Inicializa la base de datos SQLite"""
    conn = sqlite3.connect('expert_data.db')
    c = conn.cursor()
    
    # Tabla de usuarios
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            join_date TIMESTAMP,
            queries_count INTEGER DEFAULT 0
        )
    ''')
    
    # Tabla de consultas
    c.execute('''
        CREATE TABLE IF NOT EXISTS queries (
            query_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            query_type TEXT,
            query_data TEXT,
            response_data TEXT,
            timestamp TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Base de datos lista")

def register_user(user_id, username, first_name, last_name):
    """Registra un usuario en la base de datos"""
    conn = sqlite3.connect('expert_data.db')
    c = conn.cursor()
    
    c.execute('''
        INSERT OR IGNORE INTO users (user_id, username, first_name, last_name, join_date)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, username, first_name, last_name, datetime.now()))
    
    conn.commit()
    conn.close()

# Comandos del bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start - Menú principal"""
    user = update.effective_user
    
    # Registrar usuario
    register_user(
        user.id,
        user.username,
        user.first_name,
        user.last_name
    )
    
    # Teclado inline
    keyboard = [
        [InlineKeyboardButton("📊 Consultar Datos", callback_data='query_data')],
        [InlineKeyboardButton("📈 Estadísticas", callback_data='stats')],
        [InlineKeyboardButton("❓ Ayuda", callback_data='help'),
         InlineKeyboardButton("ℹ️ Información", callback_data='info')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = f"""
👋 ¡Hola {user.first_name}!

🤖 *Bienvenido a Expert Data Bot*
Tu asistente especializado en análisis de datos.

*Comandos disponibles:*
/start - Menú principal
/data - Consultar información
/stats - Ver estadísticas
/help - Ayuda y soporte
/about - Información del bot

Selecciona una opción del menú:
    """
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def data_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /data - Consulta de datos"""
    keyboard = [
        [InlineKeyboardButton("📈 Datos en Tiempo Real", callback_data='realtime_data')],
        [InlineKeyboardButton("📊 Reportes Diarios", callback_data='daily_reports')],
        [InlineKeyboardButton("📉 Análisis Histórico", callback_data='historical')],
        [InlineKeyboardButton("🔍 Búsqueda Personalizada", callback_data='custom_search')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📊 *Selecciona el tipo de datos que deseas consultar:*",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /help"""
    help_text = """
🆘 *Centro de Ayuda - Expert Data Bot*

*Comandos principales:*
• /start - Inicia el bot y muestra el menú
• /data - Accede a las opciones de consulta de datos
• /stats - Muestra estadísticas del bot
• /help - Muestra este mensaje de ayuda
• /about - Información sobre el bot

*¿Cómo consultar datos?*
1. Usa /data o haz clic en "Consultar Datos"
2. Selecciona el tipo de datos que necesitas
3. Sigue las instrucciones en pantalla

*Soporte técnico:*
Si encuentras problemas, contacta al desarrollador.

📌 *Consejo:* Usa los botones del menú para una mejor experiencia.
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /stats - Estadísticas"""
    conn = sqlite3.connect('expert_data.db')
    c = conn.cursor()
    
    # Obtener estadísticas
    c.execute('SELECT COUNT(*) FROM users')
    total_users = c.fetchone()[0]
    
    c.execute('SELECT COUNT(*) FROM queries')
    total_queries = c.fetchone()[0]
    
    conn.close()
    
    stats_text = f"""
📈 *ESTADÍSTICAS DEL BOT*

👥 *Usuarios totales:* {total_users}
📊 *Consultas realizadas:* {total_queries}
🔄 *Versión del bot:* 2.0
⚙️ *Estado:* Operativo ✅

*Uso reciente:*
• Consultas hoy: En desarrollo
• Usuarios activos: En desarrollo
• Tiempo activo: 24/7

*Próximas funciones:*
✓ Exportación de datos
✓ Gráficos interactivos
✓ Alertas personalizadas
    """
    
    await update.message.reply_text(stats_text, parse_mode='Markdown')

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /about"""
    about_text = """
🤖 *Expert Data Bot v2.0*

*Descripción:*
Bot especializado en análisis y consulta de datos en tiempo real. 
Desarrollado para proporcionar información precisa y actualizada.

*Características:*
• Consultas de datos en tiempo real
• Análisis histórico
• Reportes personalizados
• Base de datos local
• Interfaz intuitiva

*Tecnologías:*
• Python 3.10+
• python-telegram-bot v20
• SQLite3
• Railway (hosting)

*Desarrollador:* @ExpertDataDev
*Soporte:* @ExpertDataSupport

*Versión actual:* 2.0 (Migrado sin Updater)
*Última actualización:* Diciembre 2025
    """
    
    await update.message.reply_text(about_text, parse_mode='Markdown')

# Handlers para botones inline
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja los botones inline"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == 'query_data':
        await data_command_callback(query)
    elif data == 'stats':
        await stats_command_callback(query)
    elif data == 'help':
        await help_command_callback(query)
    elif data == 'info':
        await about_command_callback(query)
    elif data == 'realtime_data':
        await realtime_data_callback(query)
    elif data == 'daily_reports':
        await daily_reports_callback(query)
    elif data == 'historical':
        await historical_callback(query)
    elif data == 'custom_search':
        await custom_search_callback(query)

async def data_command_callback(query):
    """Callback para consulta de datos"""
    await query.edit_message_text(
        "📊 *Consulta de Datos*\n\nSelecciona el tipo de análisis:",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Tiempo Real", callback_data='realtime_data')],
            [InlineKeyboardButton("📅 Histórico", callback_data='historical')],
            [InlineKeyboardButton("📋 Reportes", callback_data='daily_reports')],
            [InlineKeyboardButton("🔙 Volver", callback_data='back_to_main')]
        ])
    )

async def realtime_data_callback(query):
    """Datos en tiempo real"""
    await query.edit_message_text(
        "🔄 *Datos en Tiempo Real*\n\n"
        "Esta función está en desarrollo activo.\n"
        "Próximamente podrás consultar:\n"
        "• Precios de criptomonedas\n"
        "• Indicadores económicos\n"
        "• Datos bursátiles\n"
        "• Métricas en tiempo real\n\n"
        "¡Muy pronto disponible! 🚀",
        parse_mode='Markdown'
    )

async def daily_reports_callback(query):
    """Reportes diarios"""
    await query.edit_message_text(
        "📋 *Reportes Diarios*\n\n"
        "Generando reporte del día...\n\n"
        "📅 *Fecha:* " + datetime.now().strftime("%d/%m/%Y") + "\n"
        "📊 *Consultas hoy:* 0\n"
        "👥 *Usuarios activos:* 0\n"
        "✅ *Estado del sistema:* Operativo\n\n"
        "*Próximamente:*\n"
        "✓ Reportes personalizados\n"
        "✓ Exportación PDF/Excel\n"
        "✓ Programación automática",
        parse_mode='Markdown'
    )

async def historical_callback(query):
    """Análisis histórico"""
    await query.edit_message_text(
        "📉 *Análisis Histórico*\n\n"
        "Funcionalidad en desarrollo.\n\n"
        "Podrás consultar:\n"
        "• Series temporales\n"
        "• Tendencia histórica\n"
        "• Comparativas\n"
        "• Proyecciones\n\n"
        "Disponible en la próxima actualización.",
        parse_mode='Markdown'
    )

async def custom_search_callback(query):
    """Búsqueda personalizada"""
    await query.edit_message_text(
        "🔍 *Búsqueda Personalizada*\n\n"
        "Escribe lo que quieres buscar:\n\n"
        "*Ejemplos:*\n"
        "• \"precio BTC últimos 7 días\"\n"
        "• \"indicador económico argentina\"\n"
        "• \"tendencia mercado hoy\"\n\n"
        "Envía tu consulta directamente en el chat.",
        parse_mode='Markdown'
    )

async def stats_command_callback(query):
    """Callback para estadísticas"""
    await query.edit_message_text(
        "📈 *Cargando estadísticas...*\n\n"
        "Consulta completa disponible con /stats",
        parse_mode='Markdown'
    )

async def help_command_callback(query):
    """Callback para ayuda"""
    await query.edit_message_text(
        "❓ *Ayuda*\n\n"
        "Comandos disponibles:\n"
        "/start - Menú principal\n"
        "/data - Consultar datos\n"
        "/stats - Estadísticas\n"
        "/help - Esta ayuda\n"
        "/about - Información\n\n"
        "Para más detalles, usa /help en el chat.",
        parse_mode='Markdown'
    )

async def about_command_callback(query):
    """Callback para información"""
    await query.edit_message_text(
        "ℹ️ *Información del Bot*\n\n"
        "🤖 Expert Data Bot v2.0\n"
        "🔧 Reconstruido sin Updater\n"
        "🚀 Alojado en Railway\n"
        "📊 Especializado en datos\n\n"
        "Usa /about para más información.",
        parse_mode='Markdown'
    )

# Manejador de mensajes
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja mensajes de texto"""
    text = update.message.text.lower()
    
    if any(word in text for word in ['hola', 'hello', 'hi']):
        await update.message.reply_text("¡Hola! ¿En qué puedo ayudarte? Usa /start para ver las opciones.")
    elif any(word in text for word in ['gracias', 'thanks']):
        await update.message.reply_text("¡De nada! 😊 ¿Necesitas algo más?")
    elif 'datos' in text or 'información' in text:
        await data_command(update, context)
    else:
        await update.message.reply_text(
            "🤖 No entiendo tu mensaje.\n\n"
            "Usa /start para ver el menú principal o /help para ayuda."
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja errores"""
    logger.error(f"Error: {context.error}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ Ocurrió un error. Por favor, intenta de nuevo.\n"
            "Si el problema persiste, contacta al soporte."
        )

def main():
    """Función principal"""
    print("=" * 50)
    print("🤖 EXPERT DATA BOT - INICIANDO")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Verificar token
    if not BOT_TOKEN:
        print("❌ ERROR: BOT_TOKEN no configurado")
        print("Configura la variable de entorno BOT_TOKEN")
        return
    
    print(f"✅ Token encontrado: {BOT_TOKEN[:10]}...")
    
    # Inicializar base de datos
    init_database()
    print("✅ Base de datos inicializada")
    
    # Crear Application (SIN UPDATER)
    application = Application.builder().token(BOT_TOKEN).build()
    print("✅ Application creada")
    
    # Añadir handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("data", data_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    
    # Handler para botones inline
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Handler para mensajes de texto
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Handler de errores
    application.add_error_handler(error_handler)
    
    print("✅ Todos los handlers configurados")
    print("🚀 Iniciando bot...")
    print("=" * 50)
    
    # Iniciar polling
    application.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES
    )

if __name__ == '__main__':
    main()
