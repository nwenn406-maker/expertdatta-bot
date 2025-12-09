import csv
import io

async def handle_csv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        file = await update.message.document.get_file()
        file_bytes = io.BytesIO()
        await file.download_to_memory(file_bytes)
        file_bytes.seek(0)
        
        # Leer como texto
        content = file_bytes.read().decode('utf-8')
        reader = csv.reader(io.StringIO(content))
        
        rows = list(reader)
        if not rows:
            await update.message.reply_text("❌ CSV vacío")
            return
        
        header = rows[0]
        row_count = len(rows) - 1
        
        response = (
            f"📊 *CSV Analizado (sin pandas)*\n\n"
            f"• **Filas:** {row_count}\n"
            f"• **Columnas:** {len(header)}\n"
            f"• **Primeras columnas:**\n"
        )
        
        for i, col in enumerate(header[:5]):
            response += f"  {i+1}. `{col}`\n"
        
        if len(header) > 5:
            response += f"  ... y {len(header)-5} más\n"
        
        # Mostrar primeras filas de datos
        if row_count > 0:
            response += f"\n**Primera fila de datos:**\n"
            first_row = rows[1][:3]  # Primeras 3 columnas
            response += " | ".join(first_row)
        
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)[:100]}", parse_mode='Markdown')
