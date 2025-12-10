import os
import csv
import io
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Token de Railway Variables
TOKEN = os.environ.get('TELEGRAM_TOKEN', '8382109200:AAFXY94thyyRDDSVKnIFXskwa6ffmpwxy-Q')

# Teclado personalizado
KEYBOARD = [
    ["📊 Analizar CSV", "📈 Ejemplo SQL"],
    ["🧮 Calculadora", "ℹ️ Ayuda"],
    ["🌐 Render", "💻 GitHub"]
]
REPLY_KEYBOARD = ReplyKeyboardMarkup(KEYBOARD, resize_keyboard=True, one_time_keyboard=False)

# ===== COMANDO /start =====
async def start_command(update: Update, context):
    """Maneja el comando /start"""
    user = update.effective_user
    await update.message.reply_text(
        f"👋 *Hola {user.first_name}!*\n\n"
        "🚀 *@experttdata_bot - Expert Data Assistant*\n\n"
        "✅ *Funciones disponibles:*\n"
        "• 📊 **Analizar CSV**: Envíame un archivo .csv\n"
        "• 📈 **Ejemplo SQL**: Consultas SQL de ejemplo\n"
        "• 🧮 **Calculadora**: Operaciones matemáticas\n"
        "• 🌐 **Render**: Info de Render.com\n"
        "• 💻 **GitHub**: Info de GitHub.com\n\n"
        "🔧 *Hosting:* Railway.app 🚄",
        parse_mode='Markdown',
        reply_markup=REPLY_KEYBOARD
    )

# ===== ANÁLISIS CSV =====
async def handle_csv(update: Update, context):
    """Procesa archivos CSV usando csv nativo"""
    try:
        # Obtener archivo
        file = await update.message.document.get_file()
        file_bytes = io.BytesIO()
        await file.download_to_memory(file_bytes)
        file_bytes.seek(0)
        
        # Leer y analizar con CSV nativo
        content = file_bytes.read().decode('utf-8', errors='ignore')
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)
        
        if not rows:
            await update.message.reply_text("❌ El archivo CSV está vacío.")
            return
        
        header = rows[0]
        row_count = len(rows) - 1
        
        # Construir respuesta
        response = (
            f"📊 *CSV Analizado (Railway)* 🚄\n\n"
            f"✅ **Resultados:**\n"
            f"• 📈 Filas de datos: {row_count}\n"
            f"• 📉 Columnas: {len(header)}\n"
            f"• 📦 Tamaño: {len(content)/1024:.1f} KB\n\n"
            f"🏷️ **Primeras columnas:**\n"
        )
        
        # Mostrar primeras 5 columnas
        for i, col in enumerate(header[:5]):
            response += f"{i+1}. `{col}`\n"
        
        if len(header) > 5:
            response += f"... y {len(header)-5} más\n"
        
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error procesando CSV: {e}")
        await update.message.reply_text(
            f"❌ *Error al procesar el CSV*\n\n"
            f"`{str(e)[:100]}`\n\n"
            "**Soluciones:**\n"
            "1. Verifica que sea .csv válido\n"
            "2. Revisa la codificación (UTF-8)\n"
            "3. Prueba con archivo más pequeño",
            parse_mode='Markdown'
        )

# ===== EJEMPLO SQL =====
async def sql_example(update: Update, context):
    """Muestra ejemplo de consulta SQL"""
    example = (
        "```sql\n"
        "SELECT \n"
        "    departamento,\n"
        "    COUNT(*) AS empleados,\n"
        "    AVG(salario) AS salario_promedio\n"
        "FROM empleados\n"
        "WHERE activo = 1\n"
        "GROUP BY departamento\n"
        "ORDER BY salario_promedio DESC;\n"
        "```"
    )
    await update.message.reply_text(f"📌 *Ejemplo SQL:*\n{example}", parse_mode='Markdown')

# ===== CALCULADORA =====
async def calculator(update: Update, context):
    """Calculadora básica"""
    try:
        expr = update.message.text
        # Reemplazar funciones
        expr = expr.replace('sqrt', '**0.5').replace('^', '**').replace(',', '.')
        result = eval(expr, {"__builtins__": {}}, {})
        await update.message.reply_text(f"🧮 `{expr} = {result}`", parse_mode='Markdown')
    except:
        await update.message.reply_text(
            "❌ *No pude calcular*\n\n"
            "Ejemplos válidos:\n"
            "• `2 + 3`\n"
            "• `10 * 5`\n"
            "• `100 / 4`\n"
            "• `sqrt(16)`\n"
            "• `2 ** 8` (2⁸)",
            parse_mode='Markdown'
        )

# ===== INFO RENDER Y GITHUB =====
async def render_info(update: Update, context):
    await update.message.reply_text(
        "🌐 *Render.com*\n\n"
        "Plataforma de hosting cloud\n"
        "🔗 https://render.com\n\n"
        "*Características:*\n"
        "• Web Services\n"
        "• Static Sites\n"
        "• Background Workers\n"
        "• Databases\n"
        "• Cron Jobs",
        parse_mode='Markdown'
    )

async def github_info(update: Update, context):
    await update.message.reply_text(
        "💻 *GitHub*\n\n"
        "Plataforma de desarrollo\n"
        "🔗 https://github.com\n\n"
        "*Características:*\n"
        "• Repositorios Git\n"
        "• GitHub Actions\n"
        "• GitHub Pages\n"
        "• Proyectos\n"
        "• GitHub Copilot",
        parse_mode='Markdown'
    )

# ===== MANEJADOR DE BOTONES =====
async def handle_buttons(update: Update, context):
    """Procesa los botones del teclado"""
    text = update.message.text
    
    if text == "📊 Analizar CSV":
        await update.message.reply_text(
            "📎 *Envía un archivo .csv*\n\n"
            "1. Toca el 📎 (clip)\n"
            "2. Selecciona 'Documento'\n"
            "3. Elige tu archivo .csv\n\n"
            "✅ Usando CSV nativo de Python",
            parse_mode='Markdown'
        )
    elif text == "📈 Ejemplo SQL":
        await sql_example(update, context)
    elif text == "🧮 Calculadora":
        await update.message.reply_text(
            "🔢 *Calculadora*\n\n"
            "Escribe una operación:\n"
            "• `2 + 3`\n"
            "• `10 * 5`\n"
            "• `100 / 4`\n"
            "• `sqrt(16)`\n"
            "• `2 ** 8` (2⁸)",
            parse_mode='Markdown'
        )
    elif text == "ℹ️ Ayuda":
        await update.message.reply_text(
            "📖 *Comandos disponibles:*\n\n"
            "`/start` - Menú principal\n"
            "`/render` - Info Render.com\n"
            "`/github` - Info GitHub\n"
            "`/sql` - Ejemplo SQL\n"
            "`/help` - Esta ayuda\n\n"
            "🤖 @experttdata_bot",
            parse_mode='Markdown'
        )
    elif text == "🌐 Render":
        await render_info(update, context)
    elif text == "💻 GitHub":
        await github_info(update, context)
    else:
        # Intentar calcular si no es un botón conocido
        await calculator(update, context)

# ===== CONFIGURACIÓN PRINCIPAL =====
def main():
    """Función principal"""
    # Crear aplicación
    app = Application.builder().token(TOKEN).build()
    
    # Comandos
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", start_command))
    app.add_handler(CommandHandler("render", render_info))
    app.add_handler(CommandHandler("github", github_info))
    app.add_handler(CommandHandler("sql", sql_example))
    
    # Mensajes de texto (botones)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))
    
    # Archivos CSV
    app.add_handler(MessageHandler(filters.Document.FileExtension("csv"), handle_csv))
    
    # Log de inicio
    logger.info("=" * 50)
    logger.info("🚀 @experttdata_bot INICIADO EN RAILWAY")
    logger.info(f"🔑 Token: {TOKEN[:10]}...")
    logger.info("📊 Funciones: CSV, SQL, Calculadora, Render, GitHub")
    logger.info("🚄 Hosting: Railway.app")
    logger.info("=" * 50)
    
    # Iniciar bot
    app.run_polling(
        allowed_updates="",
        drop_pending_updates=True
    )

if __name__ == '__main__':
    main()
