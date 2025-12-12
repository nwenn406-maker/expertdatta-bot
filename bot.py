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
