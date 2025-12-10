import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import pandas as pd
import io

# ⚠️ TOKEN REAL
TOKEN = os.environ.get('TELEGRAM_TOKEN', '8382109200:AAFXY94thyyRDDSVKnIFXskwa6ffmpwxy-Q')

# Menú de teclado principal
KEYBOARD_OPTIONS = [
    ["📊 Analizar CSV", "📈 Ejemplo SQL"],
    ["🧮 Calculadora", "ℹ️ Ayuda"],
    ["🌐 Render", "💻 GitHub"]  # Tus enlaces añadidos
]
REPLY_KEYBOARD = ReplyKeyboardMarkup(KEYBOARD_OPTIONS, resize_keyboard=True, one_time_keyboard=False)

# ----- COMANDOS -----
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🖥️ *Hola, soy tu DataBot personalizado*\n\n"
        "Puedo ayudarte con:\n"
        "• 📊 **Analizar CSV**: Envíame un archivo .csv y te daré estadísticas básicas.\n"
        "• 📈 **Ejemplo SQL**: Te mostraré una consulta SQL de ejemplo.\n"
        "• 🧮 **Calculadora**: Escribe una operación como '2+2' o 'sqrt(16)'.\n"
        "• 🌐 **Render**: Info de Render.com\n"
        "• 💻 **GitHub**: Info de GitHub.com\n\n"
        "Usa los botones del menú o escribe /help."
    )
    await update.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=REPLY_KEYBOARD)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📖 *Comandos disponibles:*\n"
        "/start - Inicia el bot y muestra el menú\n"
        "/help - Muestra esta ayuda\n"
        "/sql - Muestra un ejemplo de consulta SQL\n"
        "/render - Info de Render.com\n"
        "/github - Info de GitHub.com\n\n"
        "También puedes usar los *botones del menú* o enviarme un *archivo .csv* directamente."
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

# ----- TUS ENLACES AÑADIDOS -----
async def render_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌐 *Render.com*\nPlataforma de hosting\n🔗 https://render.com",
        parse_mode='Markdown'
    )

async def github_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💻 *GitHub*\nControl de versiones\n🔗 https://github.com",
        parse_mode='Markdown'
    )

# ----- MANEJADOR DE MENÚ (Botones) -----
async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "📊 Analizar CSV":
        await update.message.reply_text("📎 Envíame un archivo **.csv** y te daré un resumen estadístico.", parse_mode='Markdown')
    elif text == "📈 Ejemplo SQL":
        await sql_command(update, context)
    elif text == "🧮 Calculadora":
        await update.message.reply_text("🔢 Escribe una operación. Ej: `2+3*4` o `sqrt(25)`", parse_mode='Markdown')
    elif text == "ℹ️ Ayuda":
        await help_command(update, context)
    elif text == "🌐 Render":
        await render_command(update, context)
    elif text == "💻 GitHub":
        await github_command(update, context)
    else:
        # Si no es un botón, asumimos que es una operación matemática
        await handle_calculation(update, context)

# ----- MANEJADOR DE ARCHIVOS CSV -----
async def handle_csv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        file = await update.message.document.get_file()
        file_bytes = io.BytesIO()
        await file.download_to_memory(file_bytes)
        file_bytes.seek(0)
        
        df = pd.read_csv(file_bytes, nrows=1000)  # Limitar a 1000 filas para Railway
        
        summary = (
            f"📊 *Resumen del CSV:*\n"
            f"• Filas: {df.shape[0]}\n"
            f"• Columnas: {df.shape[1]}\n"
            f"• Columnas: {', '.join(df.columns.tolist()[:3])}"
            f"{'...' if len(df.columns) > 3 else ''}\n\n"
            f"📈 *Estadísticas (numéricas):*\n"
        )
        
        # Agrega estadísticas básicas solo para columnas numéricas
        numeric_df = df.select_dtypes(include='number')
        if not numeric_df.empty:
            stats = numeric_df.describe().round(2)
            for col in numeric_df.columns[:3]:  # Mostrar solo 3 columnas
                summary += f"\n*{col}:* μ={stats[col]['mean']}, σ={stats[col]['std']}"
        else:
            summary += "\nNo se encontraron columnas numéricas."
        
        await update.message.reply_text(summary, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Error al procesar el CSV: {str(e)[:100]}", parse_mode='Markdown')

# ----- MANEJADOR DE CÁLCULOS SIMPLES -----
async def handle_calculation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        expr = update.message.text
        # Reemplaza funciones comunes
        expr = expr.replace('sqrt', '**0.5').replace('^', '**').replace(',', '.')
        result = eval(expr, {"__builtins__": {}}, {})
        await update.message.reply_text(f"🧮 Resultado: `{result}`", parse_mode='Markdown')
    except:
        await update.message.reply_text("❌ No pude procesar la operación. Usa formato como: 2+2, 3*5, 2**8, sqrt(16)")

# ----- CONFIGURACIÓN PRINCIPAL -----
def main():
    app = Application.builder().token(TOKEN).build()
    
    # Comandos
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("sql", sql_command))
    app.add_handler(CommandHandler("render", render_command))
    app.add_handler(CommandHandler("github", github_command))
    
    # Mensajes (botones del menú y cálculos)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu))
    
    # Archivos CSV
    app.add_handler(MessageHandler(filters.Document.FileExtension("csv"), handle_csv))
    
    print("=" * 50)
    print("🤖 DataBot @experttdata_bot")
    print(f"🔑 Token: {TOKEN[:10]}...")
    print("📊 Con pandas para análisis CSV")
    print("🌐 + Render y GitHub")
    print("🚀 Hosting: Railway.app")
    print("=" * 50)
    
    print("🤖 DataBot encendido. Presiona Ctrl+C para apagar.")
    app.run_polling(allowed_updates="")

if __name__ == '__main__':
    main()
