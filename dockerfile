FROM python:3.10-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código
COPY . .

# Crear directorio para la base de datos
RUN mkdir -p /app/data

# Puerto expuesto (Railway lo asignará automáticamente)
EXPOSE 8443

# Comando para ejecutar
CMD ["python", "bot.py"]
