from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import pandas as pd
import io
import os

# ⚠️ TOKEN REAL DE TU BOT
TOKEN = os.environ.get('TELEGRAM_TOKEN', '8382109200:AAFXY94thyyRDDSVKnIFXskwa6ffmpwxy-Q')

# Menú de teclado principal
KEYBOARD_OPTIONS = [
    ["📊 Analizar CSV", "📈 Ejemplo SQL"],
    ["🧮 Calculadora", "ℹ️ Ayuda"],
    ["🌐 Render", "💻 GitHub"]  # Añadí estos botones
]
REPLY_KEYBOARD = ReplyKeyboardMarkup(KEYBOARD_OPTIONS, resize_keyboard=True, one_time_keyboard=False)

# ----- COMANDOS BÁSICOS -----
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🚀 *@experttdata_bot - Expert Data Bot*\n\n"
        "🤖 *Funciones disponibles:*\n"
        "• 📊 **Analizar CSV**: Envíame un .csv para análisis\n"
        "• 📈 **Ejemplo SQL**: Consultas SQL de ejemplo\n"
        "• 🧮 **Calculadora**: Operaciones matemáticas\n"
        "• 🌐 **Render**: Info de Render.com\n"
        "• 💻 **GitHub**: Info de GitHub.com\n\n"
        "📅 *Servicios conectados:*\n"
        "✅ Render: https://render.com\n"
        "✅ GitHub: https://github.com\n\n"
        "Usa los botones o escribe /help."
    )
    await update.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=REPLY_KEYBOARD)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📖 *Comandos disponibles:*\n"
        "/start - Inicia el bot\n"
        "/help - Esta ayuda\n"
        "/sql - Ejemplo SQL\n"
        "/render - Info de Render.com\n"
        "/github - Info de GitHub.com\n\n"
        "📊 *Funciones por botones:*\n"
        "• Analizar CSV: Sube archivo .csv\n"
        "• Ejemplo SQL: Muestra consulta SQL\n"
        "• Calculadora: Opera 2+2, sqrt(16)\n"
        "• Render/GitHub: Info servicios\n\n"
        "🤖 @experttdata_bot"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def sql_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    await update.message.reply_text(f"📌 *Ejemplo de consulta SQL:*\n{example}", parse_mode='Markdown')

# ----- COMANDOS NUEVOS PARA RENDER/GITHUB -----
async def render_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    render_text = (
        "🌐 *Render.com*\n\n"
        "*Descripción:* Plataforma cloud para desplegar aplicaciones web, APIs, bases de datos y workers.\n\n"
        "*Características principales:*\n"
        "• 🚀 Web Services (aplicaciones web)\n"
        "• ⚡ Static Sites (sitios estáticos)\n"
        "• 🔄 Background Workers (procesos)\n"
        "• 🗄️ Databases (PostgreSQL, Redis)\n"
        "• ⏰ Cron Jobs (tareas programadas)\n\n"
        "*Plan Free:* Sí, con límites generosos\n"
        "*Documentación:* https://render.com/docs\n"
        "*Status:* https://status.render.com\n\n"
        "🔗 https://render.com"
    )
    await update.message.reply_text(render_text, parse_mode='Markdown')

async def github_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    github_text = (
        "💻 *GitHub*\n\n"
        "*Descripción:* Plataforma de desarrollo y control de versiones usando Git.\n\n"
        "*Características principales:*\n"
        "• 📂 Repositorios Git\n"
        "• ⚙️ GitHub Actions (CI/CD)\n"
        "• 🌐 GitHub Pages (hosting estático)\n"
        "• 📋 Proyectos y Issues\n"
        "• 🤖 GitHub Copilot (IA)\n"
        "• 🛡️ Security scanning\n\n"
        "*Para estudiantes:* https://education.github.com\n"
        "*Documentación:* https://docs.github.com\n\n"
        "🔗 https://github.com"
    )
    await update.message.reply_text(github_text, parse_mode='Markdown')

# ----- MANEJADOR DE MENÚ (Botones) -----
async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "📊 Analizar CSV":
        await update.message.reply_text("📎 Envíame un archivo **.csv** y te daré un resumen estadístico.", parse_mode='Markdown')
    
    elif text == "📈 Ejemplo SQL":
        await sql_command(update, context)
    
    elif text == "🧮 Calculadora":
        await update.message.reply_text("🔢 Escribe una operación. Ejemplos:\n`2+3*4`\n`sqrt(25)`\n`10/2`\n`2**8` (2^8)", parse_mode='Markdown')
    
    elif text == "ℹ️ Ayuda":
        await help_command(update, context)
    
    elif text == "🌐 Render":
        await render_command(update, context)
    
    elif text == "💻 GitHub":
        await github_command(update, context)
    
    else:
        # Si no es un botón, intenta calcular
        await handle_calculation(update, context)

# ----- MANEJADOR DE ARCHIVOS CSV -----
async def handle_csv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        file = await update.message.document.get_file()
        file_bytes = io.BytesIO()
        await file.download_to_memory(file_bytes)
        file_bytes.seek(0)
        
        df = pd.read_csv(file_bytes)
        summary = (
            f"📊 *Resumen del CSV:*\n"
            f"• 📈 Filas: {df.shape[0]}\n"
            f"• 📉 Columnas: {df.shape[1]}\n"
            f"• 🏷️ Columnas: {', '.join(df.columns.tolist()[:5])}"
            f"{'...' if len(df.columns) > 5 else ''}\n\n"
            f"📈 *Estadísticas (columnas numéricas):*\n"
        )
        
        numeric_df = df.select_dtypes(include='number')
        if not numeric_df.empty:
            stats = numeric_df.describe().round(2)
            for col in numeric_df.columns[:3]:  # Muestra máximo 3 columnas
                summary += f"\n*{col}:*\n"
                summary += f"  Media (μ) = {stats[col]['mean']}\n"
                summary += f"  Desv. (σ) = {stats[col]['std']}\n"
                summary += f"  Min = {stats[col]['min']}, Max = {stats[col]['max']}"
        else:
            summary += "\nNo se encontraron columnas numéricas."
        
        await update.message.reply_text(summary, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Error al procesar el CSV:\n`{str(e)[:100]}`", parse_mode='Markdown')

# ----- MANEJADOR DE CÁLCULOS -----
async def handle_calculation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        expr = update.message.text
        # Limpiar y reemplazar funciones
        expr = expr.replace('sqrt', '**0.5').replace('^', '**').replace(',', '.')
        # Evaluar de forma segura
        result = eval(expr, {"__builtins__": {}}, {})
        await update.message.reply_text(f"🧮 *Resultado:*\n`{expr} = {result}`", parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ No pude procesar:\n`{str(e)[:50]}`\n\nEjemplos: 2+2, 3*5, sqrt(16), 10/2", parse_mode='Markdown')

# ----- CONFIGURACIÓN PRINCIPAL -----
def main():
    # Crear aplicación
    app = Application.builder().token(TOKEN).build()
    
    # Comandos
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("sql", sql_command))
    app.add_handler(CommandHandler("render", render_command))
    app.add_handler(CommandHandler("github", github_command))
    
    # Mensajes de texto (botones y cálculos)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu))
    
    # Archivos CSV
    app.add_handler(MessageHandler(filters.Document.FileExtension("csv"), handle_csv))
    
    print("=" * 50)
    print("🚀 @experttdata_bot iniciado")
    print(f"🤖 Token: {TOKEN[:10]}...")
    print("📊 Funciones: CSV, SQL, Calculadora, Render, GitHub")
    print("⚡ Usando: python-telegram-bot")
    print("🌐 Host: Render.com")
    print("=" * 50)
    
    # Iniciar polling
    app.run_polling()

if __name__ == '__main__':
    main()
