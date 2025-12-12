#!/usr/bin/env python3
"""
WEBHOOK SIMPLE PARA RAILWAY
"""

from flask import Flask, request
import requests

app = Flask(__name__)
TOKEN = "8382109200:AAF6Gu8Fi39lLBiMoMngufNSjNEZhz9DuY8"

@app.route('/')
def home():
    return "🤖 Bot Activo - Token: " + TOKEN[:10] + "..."

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.json:
        update = request.json
        if 'message' in update:
            msg = update['message']
            chat_id = msg['chat']['id']
            text = msg.get('text', '')
            
            # Responder automáticamente
            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                json={
                    'chat_id': chat_id,
                    'text': f'✅ Recibido: {text}'
                }
            )
    
    return 'OK'

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
