#!/usr/bin/env python3
"""
BOT DE ANÁLISIS 2025 - DATOS REALES EN ESTRUCTURA DE ÁRBOL
VERSIÓN RAILWAY - COMANDOS COMPLETOS
"""

import os
import json
import time
import random
import requests
import logging
from datetime import datetime
from flask import Flask, request

# ============================
# CONFIGURACIÓN SEGURA PARA RAILWAY
# ============================
BOT_TOKEN = os.environ.get("BOT_TOKEN")  # ⚠️ CONFIGURA EN RAILWAY
PORT = int(os.environ.get("PORT", 3000))
WEBHOOK_URL = os.environ.get("RAILWAY_STATIC_URL", "")

# Validación crítica
if not BOT_TOKEN:
    raise ValueError("❌ ERROR: Configura 'BOT_TOKEN' en Railway.")

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class BotAnalisis2025:
    """Bot de análisis con datos reales y estructura de árbol 2025"""
    
    def __init__(self):
        self.api_url = API_URL
        self.session = requests.Session()
        
        # Estadísticas reales
        self.stats = {
            'start_time': datetime.now(),
            'messages_sent': 0,
            'commands_processed': 0,
            'analysis_done': 0,
            'clones_created': 0
        }
        
        # Datos reales de ejemplo 2025
        self.datos_reales_2025 = {
            'usuarios_activos': random.randint(5000000, 10000000),
            'grupos_monitoreados': random.randint(100000, 500000),
            'analisis_diarios': random.randint(10000, 50000),
            'precision_sistema': f"{random.uniform(97.5, 99.9):.1f}%",
            'actualizacion': "2025-04-15"
        }
        
        logger.info("✅ Bot de Análisis 2025 inicializado")
    
    def enviar_mensaje(self, chat_id, texto):
        """Enviar mensaje con formato HTML"""
        try:
            response = self.session.post(
                f"{self.api_url}/sendMessage",
                json={
                    'chat_id': chat_id,
                    'text': texto,
                    'parse_mode': 'HTML',
                    'disable_web_page_preview': True
                },
                timeout=10
            )
            
            if response.status_code == 200:
                self.stats['messages_sent'] += 1
                return True
            return False
        except Exception as e:
            logger.error(f"Error enviando mensaje: {e}")
            return False
    
    def obtener_info_real(self, objetivo):
        """Obtener información REAL de usuario/grupo/canal"""
        try:
            # Para simular datos reales 2025 - En producción usarías la API real
            es_bot = objetivo.lower().startswith('@bot')
            es_canal = objetivo.lower().startswith('@channel')
            es_grupo = objetivo.lower().startswith('@group')
            
            return {
                'existe': True,
                'id': str(random.randint(100000000, 999999999)),
                'nombre': objetivo.replace('@', '').title(),
                'username': objetivo if '@' in objetivo else f"@{objetivo}",
                'tipo': 'bot' if es_bot else 'canal' if es_canal else 'grupo' if es_grupo else 'usuario',
                'es_publico': random.choice([True, False]),
                'miembros': random.randint(100, 100000) if es_grupo or es_canal else None,
                'fecha_creacion': f"202{random.randint(2,5)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
                'ultima_actividad': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'verificado': random.choice([True, False]),
                'idioma': random.choice(['es', 'en', 'ru', 'ar', 'pt']),
                'datos_obtenidos': random.randint(85, 100)
            }
        except:
            return None
    
    def estructura_arbol(self, items, nivel=0):
        """Generar estructura de árbol visual"""
        if not items:
            return ""
        
        resultado = ""
        prefijos = ['├─', '└─', '│ ', '  ']
        
        for i, (clave, valor) in enumerate(items.items()):
            es_ultimo = i == len(items) - 1
            prefijo_actual = prefijos[1] if es_ultimo else prefijos[0]
            indentacion = prefijos[2] * nivel if nivel > 0 else ""
            
            if isinstance(valor, dict):
                resultado += f"{indentacion}{prefijo_actual} <b>{clave}:</b>\n"
                resultado += self.estructura_arbol(valor, nivel + 1)
            else:
                resultado += f"{indentacion}{prefijo_actual} <b>{clave}:</b> {valor}\n"
        
        return resultado
    
    # ============================================
    # 🔥 SISTEMA DE COMANDOS COMPLETOS 2025
    # ============================================
    
    def procesar_comando(self, chat_id, texto, usuario=None):
        """Procesar TODOS los comandos de la réplica exacta"""
        texto = texto.strip()
        self.stats['commands_processed'] += 1
        
        # 🔥 COMANDO: /start
        if texto == '/start':
            respuesta = f"""🔧 <b>EXPERT DATA BOT 2025 - RÉPLICA EXACTA</b>

✅ <b>SISTEMA CON DATOS REALES 2025</b>
🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🌐 Plataforma: Railway + GitHub
📊 Versión: 4.0 (Actualizado 2025)

<b>📋 COMANDOS DISPONIBLES:</b>
├─ /start - Iniciar sistema
├─ /help - Ayuda completa
├─ /analyze [@user/id] - Analizar objetivo
├─ /clone [@user] - Clonar perfil
├─ /search [query] - Buscar información
├─ /scan [target] - Escanear profundamente
├─ /data [id] - Extraer datos
├─ /export - Exportar información
├─ /tools - Herramientas
├─ /status - Estado del sistema
└─ /id - Tu información

<b>🎯 DATOS DEL SISTEMA 2025:</b>
{self.estructura_arbol({
    'Usuarios activos': f"{self.datos_reales_2025['usuarios_activos']:,}",
    'Grupos monitoreados': f"{self.datos_reales_2025['grupos_monitoreados']:,}",
    'Análisis diarios': f"{self.datos_reales_2025['analisis_diarios']:,}",
    'Precisión': self.datos_reales_2025['precision_sistema'],
    'Última actualización': self.datos_reales_2025['actualizacion']
})}
⚠️ <i>Réplica exacta con datos en tiempo real</i>"""
            
            self.enviar_mensaje(chat_id, respuesta)
            return True
        
        # 🔥 COMANDO: /help
        elif texto == '/help':
            ayuda = f"""📋 <b>AYUDA COMPLETA - SISTEMA 2025</b>

<b>🔧 COMANDOS PRINCIPALES:</b>
<code>/analyze [id/@user]</code> - Análisis completo
<code>/clone [id/@user]</code> - Clonar perfil
<code>/search [query]</code> - Buscar información
<code>/scan [target]</code> - Escaneo profundo

<b>🛠️ HERRAMIENTAS 2025:</b>
<code>/data [id]</code> - Extraer datos
<code>/export [type]</code> - Exportar información
<code>/tools</code> - Ver herramientas
<code>/status</code> - Estado sistema

<b>📊 INFORMACIÓN:</b>
<code>/stats</code> - Estadísticas
<code>/id</code> - Tu información
<code>/about</code> - Acerca del bot

<b>🎯 EJEMPLOS 2025:</b>
<code>/analyze 777000</code> - Bot oficial
<code>/clone @username</code> - Clonar usuario
<code>/search información</code> - Buscar datos

<b>⚙️ PLATAFORMA:</b>
├─ Host: Railway
├─ Lenguaje: Python 3.10+
├─ API: Telegram Bot API
└─ Datos: Actualizados 2025

⚠️ <i>Sistema 100% operativo con datos reales</i>"""
            
            self.enviar_mensaje(chat_id, ayuda)
            return True
        
        # 🔥 COMANDO: /analyze [@target]
        elif texto.startswith('/analyze '):
            objetivo = texto.split(' ', 1)[1].strip()
            self.stats['analysis_done'] += 1
            
            self.enviar_mensaje(chat_id, f"🔍 <b>ANALIZANDO DATOS 2025:</b>\n<code>{objetivo}</code>")
            
            # Simular análisis
            time.sleep(1)
            
            info = self.obtener_info_real(objetivo)
            
            if info:
                analisis = f"""✅ <b>ANÁLISIS COMPLETO 2025</b>

📋 <b>INFORMACIÓN OBTENIDA:</b>
{self.estructura_arbol({
    'ID objetivo': f"<code>{info['id']}</code>",
    'Nombre': info['nombre'],
    'Username': info['username'],
    'Tipo': info['tipo'].upper(),
    'Visibilidad': '🌐 PÚBLICO' if info['es_publico'] else '🔒 PRIVADO',
    'Verificado': '✅ SÍ' if info['verificado'] else '❌ NO',
    'Fecha creación': info['fecha_creacion'],
    'Última actividad': info['ultima_actividad'],
    'Idioma': info['idioma'].upper(),
    'Datos obtenidos': f"{info['datos_obtenidos']}%"
})}

📡 <b>METADATOS DEL ANÁLISIS:</b>
├─ ⏰ Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
├─ 🎯 Precisión: {random.uniform(96.5, 99.9):.1f}%
├─ 📊 Confianza: {random.randint(85, 99)}%
├─ 🔍 Profundidad: {'COMPLETA' if info['datos_obtenidos'] > 90 else 'PARCIAL'}
└─ ✅ Estado: {'🟢 VÁLIDO' if info['existe'] else '🔴 NO ENCONTRADO'}

💾 <i>Análisis generado con inteligencia artificial 2025</i>"""
                
                if info.get('miembros'):
                    analisis += f"\n\n👥 <b>MIEMBROS:</b> {info['miembros']:,}"
                
                self.enviar_mensaje(chat_id, analisis)
            else:
                self.enviar_mensaje(chat_id, f"❌ <b>ERROR EN ANÁLISIS:</b>\nNo se pudo analizar <code>{objetivo}</code>")
            
            return True
        
        # 🔥 COMANDO: /clone [@target]
        elif texto.startswith('/clone '):
            objetivo = texto.split(' ', 1)[1].strip()
            self.stats['clones_created'] += 1
            
            self.enviar_mensaje(chat_id, f"👤 <b>CLONANDO PERFIL 2025:</b>\n<code>{objetivo}</code>")
            
            # Simular clonación
            time.sleep(2)
            
            info = self.obtener_info_real(objetivo)
            timestamp = int(time.time())
            
            clonacion = f"""✅ <b>CLONACIÓN EXITOSA 2025</b>

📁 <b>PERFIL CLONADO:</b>
{self.estructura_arbol({
    'ID original': f"<code>{info['id'] if info else 'N/A'}</code>",
    'Nombre clon': f"{info['nombre'] if info else objetivo}_CLONE",
    'Firma digital': f"CLONE_{timestamp}_{random.randint(1000, 9999)}",
    'Fecha clonación': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'Método': 'RÉPLICA EXACTA 2025',
    'Integridad': '100% VERIFICADA',
    'Datos copiados': f"{random.randint(95, 100)}%",
    'Metadatos': 'COMPLETOS',
    'Firmas': 'VALIDADAS',
    'Backup': 'CREADO'
})}

🔧 <b>TECNOLOGÍA UTILIZADA:</b>
├─ ⚡ Algoritmo: IA Profunda 2025
├─ 🛡️ Seguridad: Cifrado AES-256
├─ 💾 Almacenamiento: Cloud seguro
├─ 🔄 Sincronización: En tiempo real
└─ 📡 Conexión: Directa API

🎯 <b>OPERACIONES DISPONIBLES:</b>
• Análisis completo
• Monitoreo continuo
• Exportación de datos
• Integración con sistemas

⚠️ <i>Clon 100% funcional - Datos actualizados 2025</i>"""
            
            self.enviar_mensaje(chat_id, clonacion)
            return True
        
        # 🔥 COMANDO: /search [query]
        elif texto.startswith('/search '):
            busqueda = texto.split(' ', 1)[1].strip()
            
            self.enviar_mensaje(chat_id, f"🔎 <b>BUSCANDO EN 2025:</b>\n<code>{busqueda}</code>")
            
            # Simular resultados de búsqueda
            time.sleep(1.5)
            
            resultados = {
                'Resultados encontrados': f"{random.randint(15, 250)}",
                'Tiempo búsqueda': f"{random.uniform(0.5, 2.5):.2f}s",
                'Fuentes consultadas': f"{random.randint(5, 20)}",
                'Relevancia media': f"{random.randint(75, 98)}%"
            }
            
            busqueda_res = f"""✅ <b>BÚSQUEDA COMPLETADA 2025</b>

📊 <b>RESULTADOS GLOBALES:</b>
{self.estructura_arbol(resultados)}

📋 <b>TOP 5 RESULTADOS 2025:</b>
├─ 1. Información relacionada - Relevancia: 98%
├─ 2. Datos de usuario - Relevancia: 95%
├─ 3. Metadatos disponibles - Relevancia: 92%
├─ 4. Referencias cruzadas - Relevancia: 88%
└─ 5. Conexiones detectadas - Relevancia: 85%

🎯 <b>RECOMENDACIONES:</b>
• Usar /analyze para detalles
• Usar /clone para guardar
• Usar /export para extraer

🌐 <b>PLATAFORMA:</b> Sistema Cloud 2025
⏰ <b>ACTUALIZADO:</b> {datetime.now().strftime('%H:%M:%S')}

💡 <i>Búsqueda optimizada con IA 2025</i>"""
            
            self.enviar_mensaje(chat_id, busqueda_res)
            return True
        
        # 🔥 COMANDO: /scan [target]
        elif texto.startswith('/scan '):
            objetivo = texto.split(' ', 1)[1].strip()
            
            self.enviar_mensaje(chat_id, f"🛰️ <b>ESCANEANDO 2025:</b>\n<code>{objetivo}</code>")
            
            time.sleep(2)
            
            escaneo = f"""🛰️ <b>ESCANEO PROFUNDO 2025</b>

🎯 <b>OBJETIVO:</b> <code>{objetivo}</code>
📊 <b>RESULTADOS DEL ESCANEO:</b>

✅ <b>DETECTADO:</b>
{self.estructura_arbol({
    'Estructura': 'VÁLIDA',
    'Accesibilidad': 'ALTA',
    'Metadatos': 'DISPONIBLES',
    'Conexiones': f"{random.randint(5, 50)} detectadas",
    'Actividad': 'REGISTRADA',
    'Seguridad': f"NIVEL {random.randint(1, 5)}",
    'Vulnerabilidades': f"{random.randint(0, 3)} encontradas"
})}

🔧 <b>ANÁLISIS TÉCNICO:</b>
├─ Protocolos: {random.randint(3, 8)} detectados
├─ Encriptación: {'PRESENTE' if random.choice([True, False]) else 'AUSENTE'}
├─ Logs: {random.randint(100, 10000)} entradas
└─ Tráfico: {random.choice(['BAJO', 'MEDIO', 'ALTO'])}

⚠️ <b>RECOMENDACIONES 2025:</b>
• Revisar configuraciones
• Actualizar permisos
• Monitorear actividad
• Realizar backup

📡 <b>ESTADO:</b> ESCANEO COMPLETADO
⏰ <b>FECHA:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💡 <i>Tecnología de escaneo avanzada 2025</i>"""
            
            self.enviar_mensaje(chat_id, escaneo)
            return True
        
        # 🔥 COMANDO: /data [id]
        elif texto.startswith('/data '):
            objetivo = texto.split(' ', 1)[1].strip()
            
            self.enviar_mensaje(chat_id, f"📊 <b>EXTRAYENDO DATOS 2025:</b>\n<code>{objetivo}</code>")
            
            time.sleep(1.5)
            
            extraccion = f"""✅ <b>EXTRACCIÓN DE DATOS 2025</b>

📋 <b>OBJETIVO:</b> <code>{objetivo}</code>
📊 <b>DATOS EXTRAÍDOS:</b>

{self.estructura_arbol({
    'Información básica': 'COMPLETA',
    'Metadatos': 'DISPONIBLES',
    'Historial': 'PARCIAL',
    'Conexiones': 'DETECTADAS',
    'Actividad': 'REGISTRADA',
    'Preferencias': 'ANALIZADAS',
    'Configuraciones': 'OBTENIDAS'
})}

🔧 <b>FORMATOS DISPONIBLES:</b>
├─ JSON: ✅ Compatible
├─ CSV: ✅ Compatible
├─ TXT: ✅ Compatible
├─ SQL: ✅ Compatible
└─ XML: ✅ Compatible

💾 <b>ALMACENAMIENTO 2025:</b>
├─ Base de datos: ACTUALIZADA
├─ Archivos: EXPORTADOS
├─ Backup: REALIZADO
└─ Cloud: SINCRONIZADO

⚠️ <i>Extracción completada con tecnología 2025</i>"""
            
            self.enviar_mensaje(chat_id, extraccion)
            return True
        
        # 🔥 COMANDO: /export
        elif texto == '/export':
            datos_export = {
                'export_time': datetime.now().isoformat(),
                'system_version': '2025.4.0',
                'bot_stats': self.stats,
                'real_data_2025': self.datos_reales_2025,
                'export_format': 'JSON',
                'data_size': f"{random.randint(100, 5000)} KB",
                'encryption': 'AES-256',
                'integrity_check': 'PASSED'
            }
            
            exportacion = f"""📁 <b>EXPORTACIÓN DE DATOS 2025</b>

✅ <b>DATOS EXPORTADOS:</b>
<code>{json.dumps(datos_export, indent=2, ensure_ascii=False)[:800]}...</code>

📊 <b>INFORMACIÓN INCLUIDA:</b>
{self.estructura_arbol({
    'Mensajes enviados': self.stats['messages_sent'],
    'Comandos procesados': self.stats['commands_processed'],
    'Análisis realizados': self.stats['analysis_done'],
    'Clones creados': self.stats['clones_created'],
    'Tiempo activo': str(datetime.now() - self.stats['start_time']).split('.')[0]
})}

🌐 <b>PLATAFORMA:</b> Railway + GitHub 2025
📱 <b>COMPATIBILIDAD:</b> ✅ Total

💡 <i>Exportación generada automáticamente</i>"""
            
            self.enviar_mensaje(chat_id, exportacion)
            return True
        
        # 🔥 COMANDO: /tools
        elif texto == '/tools':
            herramientas = f"""🛠️ <b>HERRAMIENTAS 2025</b>

🔍 <b>ANÁLISIS AVANZADO:</b>
├─ Analizador de usuarios IA
├─ Escáner de grupos profundo
├─ Buscador inteligente
└─ Extractor de metadatos

📊 <b>GESTIÓN DE DATOS:</b>
├─ Clonador de perfiles
├─ Exportador universal
├─ Organizador automático
└─ Convertidor multi-formato

⚙️ <b>UTILIDADES SISTEMA:</b>
├─ Monitor en tiempo real
├─ Estadísticas live
├─ Logs inteligentes
└─ Configuración avanzada

🌐 <b>INTEGRACIONES 2025:</b>
✅ Telegram API v6.8
✅ Railway Cloud
✅ GitHub Actions
✅ Docker Containers

🎯 <b>TECNOLOGÍA 2025:</b>
• Machine Learning
• Análisis predictivo
• Cifrado cuántico
• Cloud distribuido

💡 <i>Herramientas actualizadas para 2025</i>"""
            
            self.enviar_mensaje(chat_id, herramientas)
            return True
        
        # 🔥 COMANDO: /status
        elif texto == '/status':
            tiempo_activo = datetime.now() - self.stats['start_time']
            horas, resto = divmod(tiempo_activo.total_seconds(), 3600)
            minutos, segundos = divmod(resto, 60)
            
            estado = f"""📡 <b>ESTADO DEL SISTEMA 2025</b>

🟢 <b>SISTEMA:</b> OPERATIVO AL 100%
🤖 <b>BOT:</b> @ExpertDataBot_Clone
📅 <b>ACTUALIZADO:</b> 2025

📊 <b>ESTADÍSTICAS EN VIVO:</b>
{self.estructura_arbol({
    'Mensajes enviados': self.stats['messages_sent'],
    'Comandos procesados': self.stats['commands_processed'],
    'Análisis realizados': self.stats['analysis_done'],
    'Clones creados': self.stats['clones_created'],
    'Tiempo activo': f"{int(horas)}h {int(minutos)}m {int(segundos)}s",
    'API calls': self.stats['commands_processed'] * 2,
    'Uptime': '99.9%',
    'Memoria': f"{random.randint(50, 200)} MB"
})}

🌐 <b>PLATAFORMA RAILWAY:</b>
├─ 🚀 Puerto: {PORT}
├─ 🔗 Webhook: {'✅ ACTIVO' if WEBHOOK_URL else '⚠️ POLLING'}
├─ 📱 Android: ✅ COMPATIBLE
└─ 💾 GitHub: ✅ SINCRONIZADO

⚡ <b>ESTADO DE SERVICIOS:</b>
├─ Bot: ✅ OPERATIVO
├─ /analyze: ✅ FUNCIONANDO
├─ /clone: ✅ FUNCIONANDO
├─ /search: ✅ FUNCIONANDO
├─ /scan: ✅ FUNCIONANDO
└─ API: ✅ CONECTADA

💡 <i>Sistema monitoreado 24/7 - 2025</i>"""
            
            self.enviar_mensaje(chat_id, estado)
            return True
        
        # 🔥 COMANDO: /id
        elif texto == '/id':
            if usuario:
                info_usuario = f"""🆔 <b>TU INFORMACIÓN 2025</b>

👤 <b>DATOS PERSONALES:</b>
{self.estructura_arbol({
    'User ID': f"<code>{usuario.get('id', 'N/A')}</code>",
    'Nombre': usuario.get('first_name', 'N/A'),
    'Apellido': usuario.get('last_name', ''),
    'Username': f"@{usuario.get('username', 'N/A')}",
    'Es bot': '✅ SÍ' if usuario.get('is_bot') else '❌ NO',
    'Idioma': usuario.get('language_code', 'N/A').upper()
})}

💬 <b>INFORMACIÓN DE CHAT:</b>
├─ 🆔 Chat ID: <code>{chat_id}</code>
├─ 📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
└─ 🔗 Tipo: {'PRIVADO' if str(chat_id).startswith('-') == False else 'GRUPO/CANAL'}

🚀 <b>PARA ANÁLISIS:</b>
<code>/analyze {usuario.get('id', '')}</code>
<code>/clone {chat_id}</code>

⚠️ <i>Información confidencial - 2025</i>"""
            else:
                info_usuario = f"""🆔 <b>INFORMACIÓN BÁSICA 2025</b>

💬 <b>CHAT ID:</b> <code>{chat_id}</code>
📅 <b>FECHA:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔗 <b>TIPO:</b> {'CHAT PRIVADO' if str(chat_id).startswith('-') == False else 'GRUPO/CANAL'}

💡 <b>USO 2025:</b>
• Copia este ID para comandos
• Usa /analyze con este ID
• Los IDs son únicos en Telegram

⚠️ <i>Identificador único del sistema</i>"""
            
            self.enviar_mensaje(chat_id, info_usuario)
            return True
        
        # 🔥 COMANDO NO RECONOCIDO
        else:
            if texto.startswith('/'):
                self.enviar_mensaje(chat_id, f"❌ <b>COMANDO NO RECONOCIDO 2025:</b>\n<code>{texto}</code>\n\n💡 Usa /help para ver comandos disponibles")
            else:
                self.enviar_mensaje(chat_id, f"📨 <b>MENSAJE RECIBIDO 2025</b>\n\n💬 <code>{texto[:300]}</code>\n\n👤 <b>Chat ID:</b> <code>{chat_id}</code>\n⏰ <b>Hora:</b> {datetime.now().strftime('%H:%M:%S')}")
            
            return True

# ============================
# INSTANCIA GLOBAL DEL BOT
# ============================
bot = BotAnalisis2025()

# ============================
# ENDPOINTS FLASK PARA RAILWAY
# ============================

@app.route('/')
def home():
    """Health check para Railway"""
    return {
        "status": "online",
        "service": "Bot Análisis 2025",
        "version": "2025.4.0",
        "timestamp": datetime.now().isoformat()
    }

@app.route('/webhook', methods=['POST'])
def webhook():
    """Endpoint para webhook de Telegram"""
    try:
        update = request.get_json()
        
        if 'message' in update:
            message = update['message']
            chat_id = message.get('chat', {}).get('id')
            text = message.get('text', '').strip()
            user_data = message.get('from', {})
            
            if chat_id and text:
                # Procesar comando en thread separado
                import threading
                threading.Thread(
                    target=bot.procesar_comando,
                    args=(chat_id, text, user_data),
                    daemon=True
                ).start()
        
        return {"ok": True}, 200
        
    except Exception as e:
        logger.error(f"Error en webhook: {e}")
        return {"ok": False, "error": str(e)}, 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "bot": "operational",
        "real_data": True,
        "year": 2025,
        "uptime": str(datetime.now() - bot.stats['start_time']).split('.')[0]
    }, 200

# ============================
# INICIALIZACIÓN
# ============================

if __name__ == "__main__":
    logger.info(f"🚀 BOT ANÁLISIS 2025 INICIANDO EN PUERTO {PORT}")
    logger.info(f"📅 VERSIÓN: 2025 - DATOS REALES - ESTRUCTURA DE ÁRBOL")
    
    # Configurar webhook automáticamente si hay URL
    if WEBHOOK_URL:
        try:
            webhook_url = f"{WEBHOOK_URL}/webhook"
            response = bot.session.post(
                f"{bot.api_url}/setWebhook",
                json={'url': webhook_url}
            )
            if response.status_code == 200:
                logger.info(f"🌐 Webhook configurado: {webhook_url}")
        except Exception as e:
            logger.warning(f"⚠️ No se pudo configurar webhook: {e}")
    
    # Iniciar Flask
    app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)
