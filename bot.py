#!/usr/bin/env python3
"""
TELEGRAM BOT v3.0 - SIMPLIFIED
No necesita GitHub workflows - Solo 3 archivos
"""
import os
import sys
import json
import time
import sqlite3
import requests
import threading
from datetime import datetime

# ============================
# CONFIGURACIÓN
# ============================
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8382109200:AAF6Gu8Fi39lLBiMoMngufNSjNEZhz9DuY8")
API_URL = f"https://api.telegram.org/bot{TOKEN}"

class SimpleTelegramBot:
    """Bot simplificado sin dependencias complejas"""
    
    def __init__(self):
        self.token = TOKEN
        self.api_url = API_URL
        self.session = requests.Session()
        self.running = True
        self.last_update_id = 0
        
        print("🤖 TELEGRAM BOT v3.0 - SIMPLIFIED")
        print(f"🔑 Token: {TOKEN[:10]}...{TOKEN[-5:]}")
        print("🚀 Listo para usar!")
    
    def test_token(self):
        """Verificar token"""
        try:
            response = self.session.get(f"{self.api_url}/getMe", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    bot_info = data["result"]
                    print(f"✅ Token VÁLIDO!")
                    print(f"   Bot: {bot_info['first_name']}")
                    print(f"   Username: @{bot_info.get('username', 'N/A')}")
                    return True
            print("❌ Token inválido")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def send_message(self, chat_id, text):
        """Enviar mensaje simple"""
        try:
            data = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': 'HTML'
            }
            
            response = self.session.post(
                f"{self.api_url}/sendMessage",
                json=data,
                timeout=30
            )
            
            result = response.json()
            if result.get('ok'):
                return {'success': True}
            
            return {'success': False, 'error': result.get('description')}
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return {'success': False, 'error': str(e)}
    
    def send_bulk(self, chat_ids, messages, delay=1):
        """Envío masivo simple"""
        results = []
        for chat_id in chat_ids:
            for message in messages:
                result = self.send_message(chat_id, message)
                results.append(result)
                time.sleep(delay)
        return results
    
    def get_updates(self):
        """Obtener mensajes nuevos (POLLING)"""
        try:
            params = {
                'offset': self.last_update_id + 1,
                'timeout': 25,
                'allowed_updates': ['message']
            }
            
            response = self.session.get(
                f"{self.api_url}/getUpdates",
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    return data.get('result', [])
            return []
        except Exception as e:
            print(f"⚠️ Error getUpdates: {e}")
            return []
    
    def process_updates(self, updates):
        """Procesar mensajes recibidos"""
        for update in updates:
            update_id = update.get('update_id', 0)
            if update_id > self.last_update_id:
                self.last_update_id = update_id
            
            message = update.get('message', {})
            chat_id = message.get('chat', {}).get('id')
            text = message.get('text', '').strip()
            
            if chat_id and text:
                print(f"📥 Recibido: {text}")
                
                # RESPUESTA A /START
                if text == '/start':
                    response_text = f"""🤖 <b>TELEGRAM BOT v3.0</b>

✅ Bot activo y funcionando
🚀 Hosteado en Railway
🕐 {datetime.now().strftime('%H:%M:%S')}

🔹 Usa /help para ayuda
🔹 Tu ID: <code>{chat_id}</code>"""
                    self.send_message(chat_id, response_text)
                    print(f"✅ Respondido /start a {chat_id}")
                
                # RESPUESTA A /HELP
                elif text == '/help':
                    help_text = """📚 <b>COMANDOS DISPONIBLES</b>

/start - Iniciar bot
/help - Mostrar ayuda
/status - Estado del sistema
/id - Mostrar tu ID
/ping - Probar conexión

💡 <b>Funciones avanzadas:</b>
• Envío masivo
• Monitoreo
• Alertas automáticas"""
                    self.send_message(chat_id, help_text)
                
                # RESPUESTA A /ID
                elif text == '/id':
                    self.send_message(chat_id, f"🆔 <b>Tu ID:</b> <code>{chat_id}</code>")
                
                # RESPUESTA A /PING
                elif text == '/ping':
                    self.send_message(chat_id, f"🏓 <b>PONG!</b>\n✅ Bot activo\n🕐 {datetime.now()}")
                
                # RESPUESTA A /STATUS
                elif text == '/status':
                    status_text = f"""📊 <b>ESTADO DEL SISTEMA</b>

🤖 Bot: Activo
🚀 Railway: Funcionando
⏰ Hora: {datetime.now()}
📡 Modo: Polling activo
🔐 Token: {self.token[:8]}...{self.token[-4:]}

✅ Todo operativo"""
                    self.send_message(chat_id, status_text)
                
                # RESPUESTA A CUALQUIER OTRO MENSAJE
                else:
                    echo_text = f"📝 <b>Recibido:</b>\n<code>{text[:100]}</code>"
                    if len(text) > 100:
                        echo_text += "..."
                    self.send_message(chat_id, echo_text)
    
    def start_listening(self):
        """Iniciar escucha de mensajes"""
        print("📡 Iniciando escucha de mensajes...")
        print("👉 Envía /start a tu bot en Telegram")
        
        while self.running:
            try:
                # Obtener mensajes nuevos
                updates = self.get_updates()
                
                # Procesarlos si hay
                if updates:
                    self.process_updates(updates)
                
                # Pequeña pausa para no saturar
                time.sleep(0.5)
                
            except Exception as e:
                print(f"⚠️ Error: {e}")
                time.sleep(2)
    
    def stop(self):
        """Detener bot"""
        self.running = False
        print("👋 Bot detenido")

# ============================
# FUNCIÓN PRINCIPAL
# ============================
def main():
    """Función principal para ejecutar el bot"""
    print("=" * 50)
    print("🚀 INICIANDO TELEGRAM BOT v3.0")
    print("=" * 50)
    
    # Crear instancia del bot
    bot = SimpleTelegramBot()
    
    # Verificar token
    if not bot.test_token():
        print("❌ No se puede continuar con token inválido")
        return
    
    # Iniciar escucha en segundo plano
    listener_thread = threading.Thread(target=bot.start_listening)
    listener_thread.daemon = True
    listener_thread.start()
    
    print("✅ Bot completamente operativo")
    print("💡 Usa Ctrl+C para detener")
    
    # Mantener proceso principal activo para Railway
    try:
        while True:
            time.sleep(60)
            print("📊 Sistema activo...")
    except KeyboardInterrupt:
        bot.stop()
        print("\n🛑 Programa finalizado")

if __name__ == "__main__":
    main()
