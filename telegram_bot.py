#!/usr/bin/env python3
"""
TELEGRAM HACK TOOL v3.0 - SIMPLIFIED
No necesita GitHub workflows - Solo 3 archivos
Token: 8382109200:AAF6Gu8Fi39lLBiMoMngufNSjNEZhz9DuY8
"""

import os
import sys
import json
import time
import sqlite3
import requests
from datetime import datetime

# ============================
# CONFIGURACIÓN
# ============================
TOKEN = "8382109200:AAF6Gu8Fi39lLBiMoMngufNSjNEZhz9DuY8"
API_URL = f"https://api.telegram.org/bot{TOKEN}"

class SimpleTelegramBot:
    """Bot simplificado sin dependencias complejas"""
    
    def __init__(self):
        self.token = TOKEN
        self.api_url = API_URL
        self.session = requests.Session()
        
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
                print(f"✅ Mensaje enviado a {chat_id}")
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
                results.append({
                    'chat_id': chat_id,
                    'success': result['success']
                })
                time.sleep(delay)
        
        print(f"✅ Enviados {len(results)} mensajes")
        return results
    
    def get_chat_info(self, chat_id):
        """Obtener info del chat"""
        try:
            response = self.session.post(
                f"{self.api_url}/getChat",
                json={'chat_id': chat_id},
                timeout=10
            )
            return response.json()
        except Exception as e:
            return {'ok': False, 'error': str(e)}
    
    def auto_reply_simple(self, chat_id, responses):
        """Auto-respuesta simple"""
        print(f"🤖 Auto-respuesta activada para chat {chat_id}")
        
        last_update = 0
        while True:
            try:
                response = self.session.post(
                    f"{self.api_url}/getUpdates",
                    json={'offset': last_update + 1, 'timeout': 10},
                    timeout=15
                )
                
                updates = response.json().get('result', [])
                
                for update in updates:
                    last_update = update['update_id']
                    
                    if 'message' in update:
                        msg = update['message']
                        if str(msg['chat']['id']) == str(chat_id) and 'text' in msg:
                            text = msg['text'].lower()
                            
                            for trigger, reply in responses.items():
                                if trigger.lower() in text:
                                    self.send_message(chat_id, reply)
                                    print(f"💬 Respondido: {trigger}")
                                    break
                
                time.sleep(1)
                
            except KeyboardInterrupt:
                print("⏹️ Auto-respuesta detenida")
                break
            except:
                time.sleep(5)

def simple_menu():
    """Menú simple"""
    bot = SimpleTelegramBot()
    
    while True:
        print("""
╔══════════════════════════════╗
║     🤖 MENÚ PRINCIPAL        ║
╚══════════════════════════════╝

[1] Verificar token
[2] Enviar mensaje
[3] Envío masivo
[4] Info de chat
[5] Auto-respuesta
[6] Salir

Selección: """, end="")
        
        try:
            choice = input().strip()
            
            if choice == '1':
                bot.test_token()
            
            elif choice == '2':
                chat_id = input("Chat ID: ")
                message = input("Mensaje: ")
                bot.send_message(chat_id, message)
            
            elif choice == '3':
                chat_ids = input("Chat IDs (separados por coma): ").split(',')
                messages = input("Mensajes (separados por |): ").split('|')
                bot.send_bulk([c.strip() for c in chat_ids], [m.strip() for m in messages])
            
            elif choice == '4':
                chat_id = input("Chat ID: ")
                info = bot.get_chat_info(chat_id)
                print(json.dumps(info, indent=2))
            
            elif choice == '5':
                chat_id = input("Chat ID para auto-respuesta: ")
                print("Configura respuestas (formato: palabra:respuesta)")
                print("Escribe 'listo' para terminar")
                
                responses = {}
                while True:
                    entry = input("> ").strip()
                    if entry.lower() == 'listo':
                        break
                    if ':' in entry:
                        key, value = entry.split(':', 1)
                        responses[key.strip()] = value.strip()
                
                import threading
                thread = threading.Thread(target=bot.auto_reply_simple, args=(chat_id, responses), daemon=True)
                thread.start()
                print("✅ Auto-respuesta activada. Presiona Ctrl+C para detener.")
                thread.join()
            
            elif choice == '6':
                print("👋 Hasta luego!")
                break
            
            else:
                print("❌ Opción inválida")
            
            input("\nPresiona Enter para continuar...")
            
        except KeyboardInterrupt:
            print("\n👋 Operación cancelada")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    simple_menu()
