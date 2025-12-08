import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Token de tu bot
TOKEN = os.environ.get('TELEGRAM_TOKEN', '8382109200:AAFXY94thyyRDDSVKnIFXskwa6ffmpwxy-Q')

@app.route('/')
def home():
    """Página principal - solo para verificar"""
    return jsonify({
        "status": "online",
        "service": "Telegram Bot Webhook",
        "message": "✅ Servicio funcionando",
        "webhook": "/webhook",
        "commands": ["/start", "/render", "/github"]
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """Recibe mensajes de Telegram via webhook"""
    try:
        data = request.json
        
        if 'message' in data:
            chat_id = data['message']['chat']['id']
            text = data['message'].get('text', '').lower()
            
            # Comando /start
            if text == '/start':
                # Enviar mensaje simple
                requests.post(
                    f'https://api.telegram.org/bot{TOKEN}/sendMessage',
                    json={
                        'chat_id': chat_id,
                        'text': '🚀 *Bot en Render activo*\n\n'
                               '✅ *Conectado a:*\n'
                               '• 🌐 **Render**: https://render.com\n'
                               '• 💻 **GitHub**: https://github.com\n\n'
                               'Usa /render o /github',
                        'parse_mode': 'Markdown'
                    }
                )
            
            # Comando /render
            elif text == '/render':
                requests.post(
                    f'https://api.telegram.org/bot{TOKEN}/sendMessage',
                    json={
                        'chat_id': chat_id,
                        'text': '🌐 *Render.com*\nPlataforma de hosting\n\n🔗 https://render.com',
                        'parse_mode': 'Markdown'
                    }
                )
            
            # Comando /github
            elif text == '/github':
                requests.post(
                    f'https://api.telegram.org/bot{TOKEN}/sendMessage',
                    json={
                        'chat_id': chat_id,
                        'text': '💻 *GitHub*\nPlataforma de desarrollo\n\n🔗 https://github.com',
                        'parse_mode': 'Markdown'
                    }
                )
        
        return jsonify({'ok': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Configuración para Render
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print(f"✅ Servidor iniciando en puerto {port}")
    app.run(host='0.0.0.0', port=port)
