#!/usr/bin/env python3
"""
TELEGRAM UTILITY BOT v3.0 - FULL FEATURES
No necesita GitHub workflows - Solo 3 archivos
VERSION: 3.0 COMPLETE
AUTHOR: [SYSTEM_ADMIN]
"""

import os
import sys
import json
import time
import sqlite3
import requests
import logging
import hashlib
import threading
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple

# ============================
# CONFIGURACIÓN SEGURA
# ============================
# ⚠️ CONFIGURA ESTO EN RAILWAY VARIABLES:
# Settings → Variables → TELEGRAM_BOT_TOKEN
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
if not TOKEN:
    print("❌ ERROR CRÍTICO: TELEGRAM_BOT_TOKEN no configurado")
    print("   Configura en Railway: Settings → Variables → Add New")
    print("   NAME: TELEGRAM_BOT_TOKEN")
    print("   VALUE: tu_token_completo")
    sys.exit(1)

API_URL = f"https://api.telegram.org/bot{TOKEN}"

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class TelegramUtilityBot:
    """BOT DE UTILIDAD TELEGRAM - VERSIÓN COMPLETA"""
    
    def __init__(self, bot_token: str = TOKEN):
        self.token = bot_token
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9'
        })
        
        # Estadísticas
        self.stats = {
            'messages_sent': 0,
            'users_analyzed': 0,
            'chats_monitored': 0,
            'files_processed': 0,
            'api_calls': 0
        }
        
        # Base de datos
        self.setup_database()
        
        self.print_banner()
        self.test_token()
    
    def print_banner(self):
        """Mostrar banner del sistema"""
        banner = f"""
╔══════════════════════════════════════════════════════════════════╗
║                TELEGRAM UTILITY BOT v3.0                         ║
║                     VERSIÓN COMPLETA                             ║
║                Sistema de gestión automatizada                   ║
╚══════════════════════════════════════════════════════════════════╝

[*] Token: {self.token[:12]}...{self.token[-8:]}
[*] API URL: {self.api_url}
[+] Sistema cargado y operativo
[!] Uso exclusivo para gestión y automatización
"""
        print(banner)
    
    def test_token(self):
        """Verificar que el token funcione"""
        print("[*] Verificando token...")
        try:
            response = self.session.get(f"{self.api_url}/getMe", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    bot_info = data["result"]
                    print("[+] ✅ Token VÁLIDO!")
                    print(f"    Bot ID: {bot_info['id']}")
                    print(f"    Nombre: {bot_info['first_name']}")
                    print(f"    Username: @{bot_info.get('username', 'N/A')}")
                    return True
            print("[!] Token inválido o error")
            return False
        except Exception as e:
            print(f"[!] Error verificando token: {e}")
            return False
    
    def setup_database(self):
        """Configurar base de datos para almacenamiento"""
        self.conn = sqlite3.connect('telegram_data.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        
        # Tabla de mensajes
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER,
                chat_id TEXT,
                user_id TEXT,
                text TEXT,
                timestamp DATETIME,
                is_bot BOOLEAN,
                metadata TEXT
            )
        ''')
        
        # Tabla de usuarios
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                is_bot BOOLEAN,
                language_code TEXT,
                last_seen DATETIME,
                analysis_data TEXT
            )
        ''')
        
        # Tabla de chats
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS chats (
                chat_id TEXT PRIMARY KEY,
                chat_type TEXT,
                title TEXT,
                username TEXT,
                member_count INTEGER,
                admin_count INTEGER,
                last_activity DATETIME
            )
        ''')
        
        # Tabla de archivos
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                file_id TEXT PRIMARY KEY,
                file_unique_id TEXT,
                file_size INTEGER,
                file_path TEXT,
                mime_type TEXT,
                download_path TEXT,
                download_date DATETIME
            )
        ''')
        
        self.conn.commit()
        print("[+] Base de datos configurada")
    
    # ============================================
    # 1. SISTEMA DE MENSAJERÍA
    # ============================================
    
    def send_message(self, chat_id: str, text: str, **kwargs) -> Dict:
        """Enviar mensaje a un chat"""
        self.stats['api_calls'] += 1
        try:
            data = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': kwargs.get('parse_mode', 'HTML'),
                'disable_web_page_preview': kwargs.get('disable_web_page_preview', True)
            }
            
            if 'reply_markup' in kwargs:
                data['reply_markup'] = json.dumps(kwargs['reply_markup'])
            
            response = self.session.post(
                f"{self.api_url}/sendMessage",
                json=data,
                timeout=30
            )
            
            result = response.json()
            if result.get('ok'):
                self.stats['messages_sent'] += 1
                msg_id = result['result']['message_id']
                
                # Guardar en base de datos
                self.cursor.execute('''
                    INSERT INTO messages (message_id, chat_id, text, timestamp)
                    VALUES (?, ?, ?, ?)
                ''', (msg_id, chat_id, text, datetime.now().isoformat()))
                self.conn.commit()
                
                print(f"[+] Mensaje enviado a {chat_id}: {text[:50]}...")
                return {'success': True, 'message_id': msg_id}
            
            return {'success': False, 'error': result.get('description')}
            
        except Exception as e:
            print(f"[!] Error enviando mensaje: {e}")
            return {'success': False, 'error': str(e)}
    
    def send_bulk_messages(self, chat_ids: List[str], messages: List[str], delay: float = 0.5):
        """Envío masivo de mensajes"""
        print(f"[*] Iniciando envío masivo a {len(chat_ids)} chats...")
        
        results = []
        for i, chat_id in enumerate(chat_ids):
            for message in messages:
                result = self.send_message(chat_id, message)
                results.append({
                    'chat_id': chat_id,
                    'message': message[:50],
                    'success': result['success'],
                    'timestamp': datetime.now().isoformat()
                })
                
                # Rate limiting
                time.sleep(delay)
                
                # Mostrar progreso
                if i % 10 == 0:
                    print(f"[*] Progreso: {i+1}/{len(chat_ids)} chats")
        
        print(f"[+] Envío masivo completado: {len(results)} mensajes enviados")
        return results
    
    def auto_reply_system(self, chat_id: str, trigger_words: Dict[str, str]):
        """Sistema de auto-respuesta inteligente"""
        print(f"[*] Configurando auto-respuesta para chat {chat_id}")
        
        def reply_worker():
            last_update_id = 0
            while True:
                try:
                    # Obtener mensajes nuevos
                    response = self.session.post(
                        f"{self.api_url}/getUpdates",
                        json={'offset': last_update_id + 1, 'timeout': 10},
                        timeout=15
                    )
                    
                    updates = response.json().get('result', [])
                    
                    for update in updates:
                        last_update_id = update['update_id']
                        
                        if 'message' in update:
                            msg = update['message']
                            if str(msg['chat']['id']) == chat_id and 'text' in msg:
                                text = msg['text'].lower()
                                
                                # Buscar palabra clave
                                for trigger, response_text in trigger_words.items():
                                    if trigger.lower() in text:
                                        self.send_message(chat_id, response_text)
                                        print(f"[+] Auto-respuesta enviada por trigger: {trigger}")
                                        break
                    
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"[!] Error en auto-reply: {e}")
                    time.sleep(5)
        
        # Iniciar en hilo separado
        thread = threading.Thread(target=reply_worker, daemon=True)
        thread.start()
        print(f"[+] Sistema de auto-respuesta activado")
        return thread
    
    # ============================================
    # 2. ANÁLISIS DE USUARIOS
    # ============================================
    
    def analyze_user(self, user_id: str) -> Dict:
        """Analizar usuario"""
        print(f"[*] Analizando usuario {user_id}...")
        
        try:
            # Obtener información del chat (que funciona para usuarios también)
            response = self.session.post(
                f"{self.api_url}/getChat",
                json={'chat_id': user_id},
                timeout=10
            )
            
            user_data = response.json()
            
            if user_data.get('ok'):
                user_info = user_data['result']
                
                # Análisis completo
                analysis = {
                    'basic_info': {
                        'id': user_info.get('id'),
                        'username': user_info.get('username', 'N/A'),
                        'first_name': user_info.get('first_name', 'N/A'),
                        'last_name': user_info.get('last_name', ''),
                        'is_bot': user_info.get('is_bot', False)
                    },
                    'privacy_analysis': {
                        'has_username': bool(user_info.get('username')),
                        'has_photo': 'photo' in user_info,
                        'language': user_info.get('language_code', 'N/A'),
                        'is_premium': user_info.get('is_premium', False),
                        'is_verified': user_info.get('is_verified', False)
                    },
                    'security_score': self.calculate_security_score(user_info),
                    'detected_patterns': self.analyze_user_patterns(user_info),
                    'vulnerabilities': self.find_vulnerabilities(user_info),
                    'analysis_timestamp': datetime.now().isoformat()
                }
                
                # Guardar en base de datos
                self.cursor.execute('''
                    INSERT OR REPLACE INTO users 
                    (user_id, username, first_name, last_name, is_bot, language_code, last_seen, analysis_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_info.get('id'),
                    user_info.get('username'),
                    user_info.get('first_name'),
                    user_info.get('last_name'),
                    user_info.get('is_bot', False),
                    user_info.get('language_code'),
                    datetime.now().isoformat(),
                    json.dumps(analysis)
                ))
                self.conn.commit()
                
                print(f"[+] Análisis completado para usuario {user_id}")
                return analysis
            
            return {'error': 'No se pudo obtener información del usuario'}
            
        except Exception as e:
            print(f"[!] Error analizando usuario: {e}")
            return {'error': str(e)}
    
    def calculate_security_score(self, user_info: Dict) -> int:
        """Calcular puntuación de seguridad (0-100)"""
        score = 100
        
        # Restar por vulnerabilidades
        if not user_info.get('username'):
            score -= 20  # Sin username
        
        if user_info.get('is_bot', False):
            score -= 30  # Es un bot
        
        if user_info.get('is_premium', False):
            score += 10  # Premium suele ser más seguro
        
        if user_info.get('is_verified', False):
            score += 20  # Verificado es más seguro
        
        return max(0, min(100, score))
    
    def analyze_user_patterns(self, user_info: Dict) -> List[str]:
        """Analizar patrones de comportamiento"""
        patterns = []
        
        # Patrones basados en username
        username = user_info.get('username', '')
        if username:
            if username.startswith('bot'):
                patterns.append('Probable bot account')
            if any(num in username for num in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']):
                patterns.append('Username contains numbers')
        
        # Patrones basados en nombre
        first_name = user_info.get('first_name', '')
        if len(first_name) < 3:
            patterns.append('Very short first name')
        
        return patterns
    
    def find_vulnerabilities(self, user_info: Dict) -> List[str]:
        """Buscar vulnerabilidades"""
        vulnerabilities = []
        
        # Sin username
        if not user_info.get('username'):
            vulnerabilities.append('No username set (harder to identify)')
        
        # Cuenta muy nueva (simulado)
        vulnerabilities.append('Account age unknown (needs further investigation)')
        
        # Es bot
        if user_info.get('is_bot', False):
            vulnerabilities.append('Bot account (may have limited functionality)')
        
        return vulnerabilities
    
    def clone_user_profile(self, user_id: str) -> Dict:
        """Clonar perfil de usuario (para análisis)"""
        print(f"[*] Clonando perfil de usuario {user_id}...")
        
        # Obtener datos del usuario
        user_analysis = self.analyze_user(user_id)
        
        if 'error' not in user_analysis:
            # Crear clon para análisis
            clone_data = {
                'original_user_id': user_id,
                'clone_timestamp': datetime.now().isoformat(),
                'cloned_data': {
                    'username': f"clone_{user_analysis['basic_info'].get('username', 'user')}",
                    'first_name': f"{user_analysis['basic_info'].get('first_name', 'User')}_CLONE",
                    'analysis_purpose': 'System analysis',
                    'security_analysis': user_analysis['security_score'],
                    'detected_patterns': user_analysis['detected_patterns']
                },
                'analysis_notes': 'Clon creado para análisis de sistema'
            }
            
            print(f"[+] Perfil clonado para análisis")
            return clone_data
        
        return {'error': 'Failed to clone profile'}
    
    # ============================================
    # 3. RECOLECCIÓN DE DATOS
    # ============================================
    
    def collect_chat_metadata(self, chat_id: str) -> Dict:
        """Recolectar metadatos del chat"""
        print(f"[*] Recolectando metadatos del chat {chat_id}...")
        
        metadata = {
            'collection_time': datetime.now().isoformat(),
            'chat_id': chat_id,
            'basic_info': {},
            'members_info': {},
            'admin_info': {},
            'activity_data': {},
            'file_metadata': []
        }
        
        try:
            # 1. Información básica del chat
            response = self.session.post(
                f"{self.api_url}/getChat",
                json={'chat_id': chat_id},
                timeout=10
            )
            
            if response.json().get('ok'):
                chat_info = response.json()['result']
                metadata['basic_info'] = chat_info
            
            # 2. Administradores
            response = self.session.post(
                f"{self.api_url}/getChatAdministrators",
                json={'chat_id': chat_id},
                timeout=10
            )
            
            if response.json().get('ok'):
                admins = response.json()['result']
                metadata['admin_info'] = {
                    'count': len(admins),
                    'admins': admins
                }
            
            # 3. Cantidad de miembros
            response = self.session.post(
                f"{self.api_url}/getChatMembersCount",
                json={'chat_id': chat_id},
                timeout=10
            )
            
            if response.json().get('ok'):
                metadata['members_info']['total'] = response.json()['result']
            
            # Guardar en base de datos
            self.cursor.execute('''
                INSERT OR REPLACE INTO chats 
                (chat_id, chat_type, title, username, member_count, admin_count, last_activity)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                chat_id,
                metadata['basic_info'].get('type', ''),
                metadata['basic_info'].get('title', ''),
                metadata['basic_info'].get('username', ''),
                metadata['members_info'].get('total', 0),
                metadata['admin_info'].get('count', 0),
                datetime.now().isoformat()
            ))
            self.conn.commit()
            
            self.stats['chats_monitored'] += 1
            print(f"[+] Metadatos recolectados para chat {chat_id}")
            
            return metadata
            
        except Exception as e:
            print(f"[!] Error recolectando metadatos: {e}")
            return {'error': str(e)}
    
    # ============================================
    # 4. EXPLORACIÓN DE API
    # ============================================
    
    def explore_api_methods(self):
        """Explorar métodos de la API"""
        print(f"[*] Explorando métodos de la API de Telegram...")
        
        methods = [
            ('getMe', 'Obtener información del bot'),
            ('getUpdates', 'Obtener actualizaciones'),
            ('sendMessage', 'Enviar mensaje'),
            ('sendPhoto', 'Enviar foto'),
            ('sendDocument', 'Enviar documento'),
            ('sendVideo', 'Enviar video'),
            ('sendAudio', 'Enviar audio'),
            ('sendChatAction', 'Enviar acción'),
            ('getFile', 'Obtener archivo'),
            ('getChat', 'Obtener chat'),
            ('getChatAdministrators', 'Obtener administradores'),
            ('getChatMembersCount', 'Obtener conteo'),
            ('setWebhook', 'Establecer webhook'),
            ('deleteWebhook', 'Eliminar webhook'),
            ('getWebhookInfo', 'Obtener info webhook'),
        ]
        
        results = []
        for method, description in methods:
            try:
                # Probar método simple
                if method in ['getMe', 'getWebhookInfo']:
                    response = self.session.get(f"{self.api_url}/{method}", timeout=5)
                    status = '✅' if response.status_code == 200 else '❌'
                    results.append({
                        'method': method,
                        'description': description,
                        'status': status,
                        'code': response.status_code
                    })
                    print(f"[{'✅' if response.status_code == 200 else '❌'}] {method} - {description}")
                    
                time.sleep(0.1)  # Rate limiting
                
            except Exception as e:
                results.append({
                    'method': method,
                    'description': description,
                    'status': '❌',
                    'error': str(e)[:50]
                })
                print(f"[❌] {method} - Error: {str(e)[:50]}")
        
        print(f"[+] Exploración completada: {len([r for r in results if r['status'] == '✅'])}/{len(results)} métodos disponibles")
        return results
    
    # ============================================
    # 5. SISTEMA DE MONITOREO
    # ============================================
    
    def system_health_check(self, chat_id: str):
        """Chequeo de salud del sistema"""
        print(f"[*] Realizando chequeo de salud del sistema...")
        
        health_report = {
            'timestamp': datetime.now().isoformat(),
            'chat_id': chat_id,
            'checks': []
        }
        
        # Check 1: Token válido
        token_valid = self.test_token()
        health_report['checks'].append({
            'check': 'Token Validation',
            'status': 'PASS' if token_valid else 'FAIL',
            'details': 'Bot token is valid' if token_valid else 'Invalid token'
        })
        
        # Check 2: Conexión API
        try:
            response = self.session.get(f"{self.api_url}/getMe", timeout=5)
            api_status = response.status_code == 200
            health_report['checks'].append({
                'check': 'API Connection',
                'status': 'PASS' if api_status else 'FAIL',
                'details': f'API responded with status {response.status_code}'
            })
        except:
            health_report['checks'].append({
                'check': 'API Connection',
                'status': 'FAIL',
                'details': 'Could not connect to Telegram API'
            })
        
        # Check 3: Base de datos
        try:
            self.cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            table_count = self.cursor.fetchone()[0]
            health_report['checks'].append({
                'check': 'Database',
                'status': 'PASS' if table_count >= 4 else 'WARN',
                'details': f'{table_count} tables found'
            })
        except:
            health_report['checks'].append({
                'check': 'Database',
                'status': 'FAIL',
                'details': 'Database connection failed'
            })
        
        # Check 4: Estadísticas
        health_report['checks'].append({
            'check': 'System Statistics',
            'status': 'PASS',
            'details': f"Messages: {self.stats['messages_sent']}, API Calls: {self.stats['api_calls']}"
        })
        
        # Enviar reporte
        report_text = f"""📊 <b>REPORTE DE SALUD DEL SISTEMA</b>

🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🤖 Bot: Telegram Utility System

<b>Resultados:</b>
"""
        
        for check in health_report['checks']:
            status_icon = '✅' if check['status'] == 'PASS' else '⚠️' if check['status'] == 'WARN' else '❌'
            report_text += f"{status_icon} {check['check']}: {check['details']}\n"
        
        report_text += f"\n📈 <b>Estadísticas:</b>\n"
        report_text += f"• Mensajes enviados: {self.stats['messages_sent']}\n"
        report_text += f"• Llamadas API: {self.stats['api_calls']}\n"
        report_text += f"• Chats monitoreados: {self.stats['chats_monitored']}\n"
        report_text += f"• Usuarios analizados: {self.stats['users_analyzed']}"
        
        self.send_message(chat_id, report_text)
        print(f"[+] Reporte de salud enviado a {chat_id}")
        
        return health_report
    
    # ============================================
    # 6. SISTEMA DE COMANDOS OCULTOS
    # ============================================
    
    def setup_command_system(self):
        """Configurar sistema de comandos"""
        self.running = True
        self.last_update_id = 0
        
        def command_listener():
            """Escuchar y procesar comandos"""
            print("[*] Sistema de comandos activado")
            
            while self.running:
                try:
                    # Obtener updates
                    params = {
                        'offset': self.last_update_id + 1,
                        'timeout': 20,
                        'allowed_updates': ['message']
                    }
                    
                    response = self.session.get(
                        f"{self.api_url}/getUpdates",
                        params=params,
                        timeout=25
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('ok'):
                            updates = data.get('result', [])
                            
                            for update in updates:
                                update_id = update.get('update_id', 0)
                                if update_id > self.last_update_id:
                                    self.last_update_id = update_id
                                
                                # Procesar mensaje
                                if 'message' in update:
                                    self.process_hidden_command(update['message'])
                    
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"[!] Error en command listener: {e}")
                    time.sleep(3)
        
        # Iniciar listener
        listener_thread = threading.Thread(target=command_listener, daemon=True)
        listener_thread.start()
        print("[+] Sistema de comandos iniciado")
        return listener_thread
    
    def process_hidden_command(self, message: Dict):
        """Procesar comandos ocultos"""
        chat_id = message.get('chat', {}).get('id')
        text = message.get('text', '').strip()
        user_id = message.get('from', {}).get('id')
        
        if not chat_id or not text:
            return
        
        print(f"[📨] Comando recibido de {user_id}: {text}")
        
        # COMANDO: /start (público)
        if text == '/start':
            response = f"""🔧 <b>SISTEMA DE UTILIDAD TELEGRAM</b>

✅ Sistema activo y operativo
🕐 {datetime.now().strftime('%H:%M:%S')}

<b>Funciones disponibles:</b>
• Análisis de usuarios
• Monitoreo de chats
• Envío programado
• Gestión de datos

💡 Sistema en funcionamiento normal"""
            self.send_message(chat_id, response)
        
        # COMANDO OCULTO: /system_status
        elif text == '/system_status' or text == '/status':
            stats = self.get_stats()
            status_text = f"""📡 <b>ESTADO DEL SISTEMA</b>

🟢 Sistema: OPERATIVO
🤖 Bot: {self.token[:8]}...{self.token[-4:]}
📊 Mensajes: {stats['messages_sent']}
👥 Usuarios: {stats['users_analyzed']}
💾 DB Entries: {sum(stats['database_entries'].values())}
⏰ Uptime: {stats.get('uptime', 'Active')}

✅ Todos los sistemas funcionando"""
            self.send_message(chat_id, status_text)
        
        # COMANDO OCULTO: /analyze [id]
        elif text.startswith('/analyze '):
            target = text.split(' ', 1)[1]
            if target.isdigit() or target.startswith('@'):
                analysis = self.analyze_user(target)
                if 'error' not in analysis:
                    summary = f"""🔍 <b>ANÁLISIS DE USUARIO</b>

🆔 ID: {analysis['basic_info']['id']}
👤 Nombre: {analysis['basic_info']['first_name']}
📛 Username: @{analysis['basic_info']['username']}
🛡️ Score: {analysis['security_score']}/100

📋 Patrones: {', '.join(analysis['detected_patterns'][:3])}
⚠️ Vulnerabilidades: {len(analysis['vulnerabilities'])}"""
                    self.send_message(chat_id, summary)
                else:
                    self.send_message(chat_id, f"❌ Error: {analysis['error']}")
        
        # COMANDO OCULTO: /bulk [chats] [mensaje]
        elif text.startswith('/bulk '):
            parts = text.split(' ', 2)
            if len(parts) == 3:
                chats = parts[1].split(',')
                message = parts[2]
                results = self.send_bulk_messages(chats, [message], delay=1)
                success = sum(1 for r in results if r['success'])
                self.send_message(chat_id, f"✅ Envío masivo completado: {success}/{len(results)} exitosos")
        
        # COMANDO OCULTO: /monitor [chat_id]
        elif text.startswith('/monitor '):
            chat_to_monitor = text.split(' ', 1)[1]
            metadata = self.collect_chat_metadata(chat_to_monitor)
            if 'error' not in metadata:
                info_text = f"""📊 <b>MONITOREO DE CHAT</b>

🆔 Chat: {metadata['chat_id']}
📛 Tipo: {metadata['basic_info'].get('type', 'N/A')}
🏷️ Título: {metadata['basic_info'].get('title', 'N/A')}
👥 Miembros: {metadata['members_info'].get('total', 0)}
👮 Admins: {metadata['admin_info'].get('count', 0)}

✅ Monitoreo activado"""
                self.send_message(chat_id, info_text)
        
        # COMANDO OCULTO: /health
        elif text == '/health':
            self.system_health_check(chat_id)
        
        # COMANDO OCULTO: /export
        elif text == '/export':
            export_data = self.export_data('summary')
            self.send_message(chat_id, f"📁 Export completado:\n{export_data}")
        
        # COMANDO OCULTO: /methods
        elif text == '/methods':
            methods = self.explore_api_methods()
            available = sum(1 for m in methods if m['status'] == '✅')
            self.send_message(chat_id, f"🛠️ Métodos API: {available}/{len(methods)} disponibles")
        
        # COMANDO OCULTO: /clone [user_id]
        elif text.startswith('/clone '):
            user_to_clone = text.split(' ', 1)[1]
            clone = self.clone_user_profile(user_to_clone)
            if 'error' not in clone:
                self.send_message(chat_id, f"👤 Perfil clonado para análisis: {user_to_clone}")
        
        # COMANDO OCULTO: /stop
        elif text == '/stop':
            self.send_message(chat_id, "🛑 Sistema detenido")
            self.running = False
        
        # Mensaje normal
        else:
            # Respuesta automática para mensajes no comandos
            if len(text) > 3:  # Ignorar mensajes muy cortos
                self.send_message(chat_id, f"📨 Mensaje recibido: {text[:100]}...")
    
    # ============================================
    # UTILIDADES
    # ============================================
    
    def get_stats(self):
        """Obtener estadísticas de uso"""
        return {
            'messages_sent': self.stats['messages_sent'],
            'users_analyzed': self.stats['users_analyzed'],
            'chats_monitored': self.stats['chats_monitored'],
            'files_processed': self.stats['files_processed'],
            'api_calls': self.stats['api_calls'],
            'database_entries': self.get_db_stats(),
            'uptime': self.get_uptime()
        }
    
    def get_db_stats(self):
        """Obtener estadísticas de la base de datos"""
        try:
            tables = ['messages', 'users', 'chats', 'files']
            stats = {}
            for table in tables:
                self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = self.cursor.fetchone()[0]
                stats[table] = count
            return stats
        except:
            return {}
    
    def get_uptime(self):
        """Obtener tiempo de actividad"""
        if hasattr(self, 'start_time'):
            return str(datetime.now() - self.start_time)
        return "Unknown"
    
    def export_data(self, format: str = 'summary'):
        """Exportar datos"""
        print(f"[*] Exportando datos...")
        
        data = {
            'export_time': datetime.now().isoformat(),
            'stats': self.get_stats(),
            'summary': f"Messages: {self.stats['messages_sent']}, Users: {self.stats['users_analyzed']}"
        }
        
        return json.dumps(data, indent=2)
    
    def stop_system(self):
        """Detener sistema completo"""
        self.running = False
        if hasattr(self, 'conn'):
            self.conn.close()
        print("[🛑] Sistema detenido")

# ============================================
# EJECUCIÓN PRINCIPAL
# ============================================

def main():
    """Función principal del sistema"""
    print("[🚀] Iniciando Telegram Utility Bot v3.0...")
    
    # Registrar tiempo de inicio
    start_time = datetime.now()
    
    try:
        # Crear instancia del bot
        bot = TelegramUtilityBot()
        bot.start_time = start_time
        
        # Verificar token
        if not bot.test_token():
            print("[❌] Error: Token inválido. Verifica TELEGRAM_BOT_TOKEN en Railway Variables")
            return
        
        # Iniciar sistema de comandos
        listener = bot.setup_command_system()
        
        print("[✅] Sistema completamente operativo")
        print("[📡] Escuchando comandos...")
        print("[💡] Comandos disponibles: /start, /system_status, /analyze, /bulk, /monitor, /health, /methods, /clone, /stop")
        
        # Mantener proceso principal vivo para Railway
        while bot.running:
            time.sleep(60)
            print("[💚] Sistema activo...")
        
        print("[👋] Sistema finalizado")
        
    except KeyboardInterrupt:
        print("\n[🛑] Interrupción por usuario")
        if 'bot' in locals():
            bot.stop_system()
    except Exception as e:
        print(f"[❌] Error crítico: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
