import os
from flask import Flask, jsonify
import requests
import time

app = Flask(__name__)

# Info del bot
BOT_NAME = "ExpertData Bot"
VERSION = "1.0"

@app.route('/')
def home():
    """Página principal del bot"""
    return jsonify({
        "bot": BOT_NAME,
        "version": VERSION,
        "status": "online",
        "description": "Bot que muestra información de Render y GitHub",
        "endpoints": {
            "info": "/info",
            "render": "/render-info",
            "github": "/github-info",
            "status": "/status"
        },
        "connected_services": ["Render", "GitHub"]
    })

@app.route('/info')
def info():
    """Información sobre el bot"""
    return jsonify({
        "name": BOT_NAME,
        "purpose": "Mostrar información y enlaces de Render y GitHub",
        "how_to_use": "Visita /render-info o /github-info",
        "services": {
            "render": {
                "name": "Render",
                "url": "https://render.com",
                "description": "Plataforma de hosting y deployment"
            },
            "github": {
                "name": "GitHub",
                "url": "https://github.com",
                "description": "Plataforma de desarrollo y control de versiones"
            }
        }
    })

@app.route('/render-info')
def render_info():
    """Información específica de Render"""
    return jsonify({
        "service": "Render",
        "official_url": "https://render.com",
        "documentation": "https://render.com/docs",
        "status_page": "https://status.render.com",
        "pricing": "https://render.com/pricing",
        "features": [
            "Web Services",
            "Background Workers",
            "Static Sites",
            "Databases",
            "Cron Jobs"
        ],
        "free_tier": "Sí, con límites generosos",
        "your_project": "expertidata-bot",
        "deployment_url": os.environ.get('RENDER_EXTERNAL_URL', 'https://expertidata-bot.onrender.com')
    })

@app.route('/github-info')
def github_info():
    """Información específica de GitHub"""
    return jsonify({
        "service": "GitHub",
        "official_url": "https://github.com",
        "documentation": "https://docs.github.com",
        "education": "https://education.github.com",
        "features": [
            "Repositorios Git",
            "GitHub Actions (CI/CD)",
            "GitHub Pages",
            "GitHub Copilot",
            "Proyectos y Issues"
        ],
        "your_repository": "expertdata-bot",
        "repository_url": "https://github.com/tu-usuario/expertdata-bot"
    })

@app.route('/status')
def status():
    """Estado del servicio"""
    return jsonify({
        "status": "online",
        "timestamp": time.time(),
        "uptime": "Activo",
        "memory_usage": "Normal",
        "service": "expertidata-bot",
        "deployed_on": "Render"
    })

# Configuración para Render
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print(f"🚀 {BOT_NAME} iniciado en puerto {port}")
    print(f"🌐 Render: https://render.com")
    print(f"💻 GitHub: https://github.com")
    print(f"🔗 URL: https://expertidata-bot.onrender.com")
    
    app.run(host='0.0.0.0', port=port)
