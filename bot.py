import os
import logging
import pandas as pd
import io
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configuración
logging.basicConfig(level=logging.INFO)
TOKEN = os.environ.get('TELEGRAM_TOKEN', '8382109200:AAFXY94thyyRDDSVKnIFXskwa6ffmpwxy-Q')

# Teclado como ExpertDatabot
KEYBOARD = [
    ["📊 Analizar CSV", "📈 Ejemplo SQL"],
    ["🧮 Calculadora", "ℹ️ Ayuda"],
    ["🌐 Render", "💻 GitHub"]  # Tus enlaces agregados
]
REPLY_KEYBOARD = ReplyKeyboardMarkup(KEYBOARD, resize_keyboard=True, one_time_keyboard=False)

# ===== COMANDO /start =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mensaje de bienvenida como ExpertDatabot"""
    welcome = (
        "🖥️ *Hola, soy tu DataBot personalizado*\n\n"
        "Puedo ayudarte con:\n"
        "• 📊 **Analizar CSV**: Envíame un archivo .csv\n"
        "• 📈 **Ejemplo SQL**: Te muestro consultas SQL\n"
        "• 🧮 **Calculadora**: Operaciones matemáticas\n"
        "• 🌐 **Render**: Info de hosting\n"
        "• 💻 **GitHub**: Control de versiones\n\n"
        "Usa los botones o escribe /help."
    )
    await update.message.reply_text(welcome, parse_mode='Markdown', reply_markup=REPLY_KEYBOARD)

# ===== ANÁLISIS CSV (como ExpertDatabot) =====
async def handle_csv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa archivos CSV"""
    try:
        file = await update.message.document.get_file()
        file_bytes = io.BytesIO()
        await file.download_to_memory(file_bytes)
        file_bytes.seek(0)
        
        # Leer solo las primeras 1000 filas para ahorrar memoria
        df = pd.read_csv(file_bytes, nrows=1000)
        
        response = (
            f"📊 *Resumen del CSV:*\n"
            f"• Filas: {df.shape[0]}\n"
            f"• Columnas: {df.shape[1]}\n"
            f"• Columnas: {', '.join(df.columns.tolist()[:3])}"
            f"{'...' if len(df.columns) > 3 else ''}\n\n"
            f"📈 *Estadísticas (numéricas):*\n"
        )
        
        # Solo columnas numéricas
        numeric_df = df.select_dtypes(include='number')
        if not numeric_df.empty:
            stats = numeric_df.describe().round(2)
            for col in numeric_df.columns[:2]:  # Máximo 2 columnas
                response += f"\n*{col}:* μ={stats[col]['mean']}, σ={stats[col]['std']}"
        else:
            response += "\nNo hay columnas numéricas."
        
        await update.message.reply_text(response, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)[:100]}")

# ===== EJEMPLO SQL =====
async def sql_example(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra ejemplo SQL"""
    sql = (
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
    await update.message.reply_text(f"📌 *Ejemplo SQL:*\n{sql}", parse_mode='Markdown')

# ===== CALCULADORA =====
async def calculator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Calculadora básica"""
    try:
        expr = update.message.text.replace('sqrt', '**0.5').replace('^', '**')
        result = eval(expr, {"__builtins__": {}}, {})
        await update.message.reply_text(f"🧮 `{expr} = {result}`", parse_mode='Markdown')
    except:
        await update.message.reply_text("❌ Usa: 2+2, 3*4, sqrt(16)")

# ===== TUS ENLACES =====
async def render_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌐 *Render.com*\n🔗 https://render.com", parse_mode='Markdown')

async def github_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💻 *GitHub*\n🔗 https://github.com", parse_mode='Markdown')

# ===== MANEJADOR DE BOTONES =====
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "📊 Analizar CSV":
        await update.message.reply_text("📎 Envíame un archivo **.csv**", parse_mode='Markdown')
    elif text == "📈 Ejemplo SQL":
        await sql_example(update, context)
    elif text == "🧮 Calculadora":
        await update.message.reply_text("🔢 Escribe: `2+3*4` o `sqrt(25)`", parse_mode='Markdown')
    elif text == "ℹ️ Ayuda":
        await update.message.reply_text("Usa /start para ver opciones", parse_mode='Markdown')
    elif text == "🌐 Render":
        await render_info(update, context)
    elif text == "💻 GitHub":
        await github_info(update, context)
    else:
        # Si no es botón, intenta calcular
        await calculator(update, context)

# ===== CONFIGURACIÓN PRINCIPAL =====
def main():
    app = Application.builder().token(TOKEN).build()
    
    # Comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("render", render_info))
    app.add_handler(CommandHandler("github", github_info))
    app.add_handler(CommandHandler("sql", sql_example))
    app.add_handler(CommandHandler("help", start))  # Mismo que /start
    
    # Mensajes de texto (botones)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))
    
    # Archivos CSV
    app.add_handler(MessageHandler(filters.Document.FileExtension("csv"), handle_csv))
    
    print("=" * 50)
    print("🤖 @experttdata_bot - Como ExpertDatabot")
    print("📊 Con pandas para análisis CSV")
    print("🌐 + Render y GitHub")
    print("=" * 50)
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
