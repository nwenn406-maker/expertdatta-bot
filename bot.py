from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import io

TOKEN = '8382109200:AAEkp8XpzsvoD6JJ_MemxJwb27EULR1y2EM'

KEYBOARD_OPTIONS = [
    ["📈 Ejemplo SQL", "🧮 Calculadora"],
    ["ℹ️ Ayuda"]
]
REPLY_KEYBOARD = ReplyKeyboardMarkup(KEYBOARD_OPTIONS, resize_keyboard=True, one_time_keyboard=False)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🖥️ *Hola, soy expertdatta_bot*\n\n"
        "Puedo ayudarte con:\n"
        "• 📈 **Ejemplo SQL**: Consultas de ejemplo\n"
        "• 🧮 **Calculadora**: Operaciones matemáticas\n\n"
        "Usa los botones o /help."
    )
    await update.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=REPLY_KEYBOARD)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📖 *Comandos:*\n"
        "/start - Inicia el bot\n"
        "/help - Ayuda\n"
        "/sql - Ejemplo SQL\n\n"
        "También los botones del menú."
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
    await update.message.reply_text(f"📌 *Ejemplo SQL:*\n{example}", parse_mode='Markdown')

async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "📈 Ejemplo SQL":
        await sql_command(update, context)
    elif text == "🧮 Calculadora":
        await update.message.reply_text("🔢 Escribe operación. Ej: `2+3*4`", parse_mode='Markdown')
    elif text == "ℹ️ Ayuda":
        await help_command(update, context)
    else:
        await handle_calculation(update, context)

async def handle_calculation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        expr = update.message.text
        expr = expr.replace('sqrt', '**0.5').replace('^', '**')
        result = eval(expr, {"__builtins__": {}})
        await update.message.reply_text(f"🧮 Resultado: `{result}`", parse_mode='Markdown')
    except:
        await update.message.reply_text("❌ No pude procesar. Usa: 2+2, 3*5, 2**8")

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("sql", sql_command))
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu))
    
    print("🤖 expertdatta_bot encendido")
    app.run_polling()

if __name__ == '__main__':
    main()
