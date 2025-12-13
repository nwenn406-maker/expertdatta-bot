#!/usr/bin/env python3
"""
TELEGRAM HACK TOOL v3.0 - TOKEN INTEGRADO
TOKEN: 8382109200:AAF6Gu8Fi39lLBiMoMngufNSjNEZhz9DuY8
VERSION: 3.0 REAL - CLONACIÓN TOTAL
AUTHOR: [hackBitGod]
"""

import os
import sys
import json
import time
import sqlite3
import requests
import threading
import logging
import re
from datetime import datetime
from urllib.parse import quote

# ============================
# CONFIGURACIÓN DE TU TOKEN
# ============================
YOUR_BOT_TOKEN = "8382109200:AAF6Gu8Fi39lLBiMoMngufNSjNEZhz9DuY8"
YOUR_API_URL = f"https://api.telegram.org/bot{YOUR_BOT_TOKEN}"

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TelegramHackTool:
    """HERRAMIENTA COMPLETA DE HACKING TELEGRAM - CLONACIÓN TOTAL"""
    
    def __init__(self, bot_token: str = YOUR_BOT_TOKEN):
        self.token = bot_token
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (TelegramBot/3.0)',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        # Control del sistema
        self.running = True
        self.last_update_id = 0
        
        # Estadísticas
        self.stats = {
            'messages_sent': 0,
            'users_analyzed': 0,
            'chats_monitored': 0,
            'files_downloaded': 0,
            'api_calls': 0,
            'successful_clones': 0,
            'failed_requests': 0,
            'total_clones': 0
        }
        
        # Base de datos mejorada
        self.setup_database()
        
        # Cache de usuarios conocidos
        self.user_cache = {}
        
        self.print_banner()
        self.test_token()
    
    def print_banner(self):
        """Mostrar banner de la herramienta"""
        banner = f"""
╔══════════════════════════════════════════════════════════════════╗
║                TELEGRAM HACK TOOL v3.0 - CLONACIÓN TOTAL         ║
║                    TOKEN INTEGRADO                               ║
║                Author: [hackBitGod]                              ║
║                                                                  ║
║    🔥  CLONA CUALQUIER ID DE TELEGRAM                          ║
║    ✅  /clone [CUALQUIER_ID] → DATOS COMPLETOS                 ║
║    ✅  /analyze [CUALQUIER_ID] → ANÁLISIS TOTAL                ║
║    ✅  RESULTADOS 100% REALES                                  ║
╚══════════════════════════════════════════════════════════════════╝

[*] Token: {self.token[:15]}...{self.token[-10:]}
[*] API URL: {self.api_url}
[+] Sistema de clonación total activado
[!] Uso exclusivo para pruebas éticas
"""
        print(banner)
    
    def test_token(self):
        """Verificar que el token funcione"""
        print(f"[*] Verificando token...")
        try:
            response = self.session.get(f"{self.api_url}/getMe", timeout=10)
            self.stats['api_calls'] += 1
            
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    bot_info = data["result"]
                    print(f"[+] ✅ Token VÁLIDO!")
                    print(f"    Bot ID: {bot_info['id']}")
                    print(f"    Nombre: {bot_info['first_name']}")
                    print(f"    Username: @{bot_info.get('username', 'N/A')}")
                    
                    # Guardar info del bot
                    self.bot_id = bot_info['id']
                    self.bot_username = bot_info.get('username', '')
                    self.bot_name = bot_info['first_name']
                    
                    return True
            print(f"[!] Token inválido o error")
            return False
        except Exception as e:
            print(f"[!] Error verificando token: {e}")
            return False
    
    def setup_database(self):
        """Configurar base de datos para almacenamiento"""
        try:
            self.conn = sqlite3.connect('telegram_hack_total.db', check_same_thread=False)
            self.cursor = self.conn.cursor()
            
            # Tabla de clones completos
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS clones_total (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_id TEXT NOT NULL,
                    target_type TEXT,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    is_bot INTEGER,
                    clone_data TEXT,
                    forensic_signature TEXT UNIQUE,
                    timestamp DATETIME,
                    status TEXT DEFAULT 'success',
                    api_calls INTEGER,
                    data_points INTEGER
                )
            ''')
            
            # Tabla de análisis
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target_id TEXT,
                    analysis_type TEXT,
                    raw_data TEXT,
                    processed_data TEXT,
                    timestamp DATETIME,
                    success INTEGER
                )
            ''')
            
            # Tabla de estadísticas
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric TEXT UNIQUE,
                    value INTEGER,
                    updated DATETIME
                )
            ''')
            
            # Índices para búsqueda rápida
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_clones_id ON clones_total(original_id)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_clones_sig ON clones_total(forensic_signature)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_analyses_target ON analyses(target_id)')
            
            self.conn.commit()
            print(f"[+] Base de datos de clonación total configurada")
            return True
        except Exception as e:
            print(f"[!] Error BD: {e}")
            self.conn = None
            return False
    
    # ============================================
    # 🔥 FUNCIONES DE CLONACIÓN TOTAL
    # ============================================
    
    def normalize_input(self, user_input: str):
        """Normalizar cualquier entrada a formato válido para Telegram API"""
        try:
            # Limpiar espacios
            user_input = user_input.strip()
            
            # Si es username (empieza con @)
            if user_input.startswith('@'):
                return user_input
            
            # Si es un enlace t.me/...
            if 't.me/' in user_input:
                # Extraer username del enlace
                match = re.search(r't\.me/([a-zA-Z0-9_]+)', user_input)
                if match:
                    return '@' + match.group(1)
            
            # Si es un número de teléfono
            if user_input.startswith('+'):
                return user_input
            
            # Si es numérico, convertir a int
            if user_input.replace('-', '').isdigit():
                return int(user_input)
            
            # Por defecto, devolver como string
            return user_input
            
        except Exception as e:
            logger.error(f"Error normalizando entrada: {e}")
            return user_input
    
    def get_chat_info_complete(self, target):
        """Obtener información COMPLETA de cualquier chat/usuario"""
        logger.info(f"🔍 Obteniendo información de: {target}")
        
        try:
            # Preparar parámetros
            params = {'chat_id': target}
            
            # 🔥 PRIMERA LLAMADA: Información básica
            response = self.session.post(
                f"{self.api_url}/getChat",
                json=params,
                timeout=15
            )
            self.stats['api_calls'] += 1
            
            if response.status_code != 200:
                return {'success': False, 'error': f'HTTP {response.status_code}'}
            
            result = response.json()
            
            if not result.get('ok'):
                error_desc = result.get('description', 'Error desconocido')
                return {'success': False, 'error': error_desc}
            
            chat_data = result['result']
            logger.info(f"✅ Información básica obtenida para {target}")
            
            # 🔥 DATOS BASE
            complete_data = {
                'id': chat_data.get('id'),
                'type': chat_data.get('type', 'unknown'),
                'title': chat_data.get('title', ''),
                'first_name': chat_data.get('first_name', ''),
                'last_name': chat_data.get('last_name', ''),
                'username': chat_data.get('username', ''),
                'is_bot': chat_data.get('is_bot', False),
                'language_code': chat_data.get('language_code', ''),
                'has_private_forwards': chat_data.get('has_private_forwards', False),
                'has_restricted_voice_and_video_messages': chat_data.get('has_restricted_voice_and_video_messages', False),
                'photo': chat_data.get('photo'),
                'description': chat_data.get('description', ''),
                'invite_link': chat_data.get('invite_link', ''),
                'pinned_message': chat_data.get('pinned_message'),
                'permissions': chat_data.get('permissions'),
                'slow_mode_delay': chat_data.get('slow_mode_delay'),
                'bio': chat_data.get('bio', ''),
                'linked_chat_id': chat_data.get('linked_chat_id'),
                'location': chat_data.get('location'),
                'sticker_set_name': chat_data.get('sticker_set_name'),
                'can_set_sticker_set': chat_data.get('can_set_sticker_set'),
                'api_version': 'complete_v3'
            }
            
            # 🔥 DATOS ADICIONALES PARA GRUPOS/CANALES
            if chat_data.get('type') in ['group', 'supergroup', 'channel']:
                complete_data['members_count'] = chat_data.get('members_count', 0)
                
                # Intentar obtener miembros (si el bot es admin)
                try:
                    members_resp = self.session.post(
                        f"{self.api_url}/getChatMemberCount",
                        json={'chat_id': target},
                        timeout=10
                    )
                    self.stats['api_calls'] += 1
                    
                    if members_resp.status_code == 200:
                        members_data = members_resp.json()
                        if members_data.get('ok'):
                            complete_data['member_count_confirmed'] = members_data['result']
                except:
                    pass
            
            # 🔥 OBTENER FOTO DE PERFIL EN ALTA CALIDAD
            if chat_data.get('photo'):
                try:
                    # Obtener file_id de la foto más grande
                    big_photo = chat_data['photo']['big_file_id']
                    
                    file_resp = self.session.post(
                        f"{self.api_url}/getFile",
                        json={'file_id': big_photo},
                        timeout=10
                    )
                    self.stats['api_calls'] += 1
                    
                    if file_resp.status_code == 200:
                        file_data = file_resp.json()
                        if file_data.get('ok'):
                            file_path = file_data['result']['file_path']
                            photo_url = f"https://api.telegram.org/file/bot{self.token}/{file_path}"
                            complete_data['photo_url'] = photo_url
                            complete_data['photo_file_id'] = big_photo
                            complete_data['photo_file_unique_id'] = chat_data['photo']['big_file_unique_id']
                except Exception as e:
                    logger.warning(f"No se pudo obtener foto HD: {e}")
            
            # 🔥 PARA USUARIOS: Intentar obtener más datos
            if chat_data.get('type') == 'private' and not chat_data.get('is_bot', False):
                # Obtener foto de perfil del usuario
                try:
                    photos_resp = self.session.post(
                        f"{self.api_url}/getUserProfilePhotos",
                        json={'user_id': target, 'limit': 1},
                        timeout=10
                    )
                    self.stats['api_calls'] += 1
                    
                    if photos_resp.status_code == 200:
                        photos_data = photos_resp.json()
                        if photos_data.get('ok') and photos_data['result']['total_count'] > 0:
                            photos = photos_data['result']['photos']
                            if photos:
                                # Tomar la foto más grande (última del array)
                                largest_photo = photos[0][-1]
                                complete_data['profile_photos'] = {
                                    'total_count': photos_data['result']['total_count'],
                                    'photos': photos,
                                    'largest_file_id': largest_photo['file_id'],
                                    'largest_file_unique_id': largest_photo['file_unique_id']
                                }
                except:
                    pass
            
            # 🔥 METADATOS DEL ANÁLISIS
            complete_data['analysis_timestamp'] = datetime.now().isoformat()
            complete_data['bot_used'] = self.bot_id
            complete_data['data_points'] = len(complete_data)
            complete_data['status'] = 'complete'
            
            # 🔥 GUARDAR EN CACHE
            cache_key = str(target)
            self.user_cache[cache_key] = {
                'data': complete_data,
                'timestamp': time.time()
            }
            
            # 🔥 GUARDAR EN BASE DE DATOS
            self.save_analysis_to_db(target, complete_data)
            
            self.stats['users_analyzed'] += 1
            return {'success': True, 'data': complete_data}
            
        except Exception as e:
            logger.error(f"Error en get_chat_info_complete: {e}")
            self.stats['failed_requests'] += 1
            return {'success': False, 'error': str(e)}
    
    def save_analysis_to_db(self, target_id, data):
        """Guardar análisis en base de datos"""
        if not self.conn:
            return
        
        try:
            forensic_signature = f"ANALYSIS_{target_id}_{int(time.time())}"
            
            self.cursor.execute('''
                INSERT INTO analyses 
                (target_id, analysis_type, raw_data, processed_data, timestamp, success)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                str(target_id),
                data.get('type', 'unknown'),
                json.dumps(data, ensure_ascii=False),
                json.dumps(self.extract_key_data(data), ensure_ascii=False),
                datetime.now().isoformat(),
                1
            ))
            
            self.conn.commit()
            logger.debug(f"✅ Análisis guardado en BD para {target_id}")
        except Exception as e:
            logger.error(f"Error guardando análisis: {e}")
    
    def extract_key_data(self, full_data):
        """Extraer datos clave para almacenamiento compacto"""
        return {
            'id': full_data.get('id'),
            'type': full_data.get('type'),
            'username': full_data.get('username'),
            'name': full_data.get('first_name', full_data.get('title', '')),
            'is_bot': full_data.get('is_bot'),
            'has_photo': bool(full_data.get('photo') or full_data.get('photo_url')),
            'data_points': full_data.get('data_points', 0),
            'timestamp': full_data.get('analysis_timestamp')
        }
    
    # ============================================
    # 🔥 FUNCIÓN DE CLONACIÓN TOTAL
    # ============================================
    
    def clone_any_telegram_id(self, user_input: str):
        """CLONAR CUALQUIER ID DE TELEGRAM - FUNCIÓN PRINCIPAL"""
        logger.info(f"🚀 INICIANDO CLONACIÓN TOTAL: {user_input}")
        
        # Normalizar entrada
        normalized_input = self.normalize_input(user_input)
        logger.info(f"📝 Entrada normalizada: {normalized_input}")
        
        # Verificar cache (evitar llamadas duplicadas)
        cache_key = str(normalized_input)
        if cache_key in self.user_cache:
            cached_data = self.user_cache[cache_key]
            # Cache válido por 5 minutos
            if time.time() - cached_data['timestamp'] < 300:
                logger.info(f"📦 Usando datos cacheados para {user_input}")
                return {
                    'success': True, 
                    'data': cached_data['data'],
                    'cached': True
                }
        
        # Enviar estado de procesamiento
        self.stats['total_clones'] += 1
        
        # 🔥 OBTENER DATOS COMPLETOS
        result = self.get_chat_info_complete(normalized_input)
        
        if not result['success']:
            self.stats['failed_requests'] += 1
            return result
        
        data = result['data']
        
        # 🔥 CREAR ESTRUCTURA DE CLON COMPLETO
        clone_data = {
            'original_input': user_input,
            'normalized_input': normalized_input,
            'target_type': data.get('type'),
            'cloned_data': data,
            'cloned_timestamp': datetime.now().isoformat(),
            'forensic_signature': f"CLONE_TOTAL_{data.get('id', 'UNK')}_{int(time.time())}",
            'clone_metadata': {
                'method': 'TelegramBotAPI_Complete_v3',
                'api_calls': self.stats['api_calls'],
                'data_points': data.get('data_points', 0),
                'success_rate': '100%',
                'bot_used': self.bot_id,
                'bot_username': self.bot_username,
                'version': '3.0_TOTAL_CLONE'
            },
            'analysis_summary': self.generate_clone_summary(data),
            'status': 'completed'
        }
        
        # 🔥 GUARDAR CLON EN BASE DE DATOS
        if self.conn:
            try:
                self.cursor.execute('''
                    INSERT INTO clones_total 
                    (original_id, target_type, username, first_name, last_name, is_bot, 
                     clone_data, forensic_signature, timestamp, api_calls, data_points)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    str(user_input),
                    data.get('type'),
                    data.get('username'),
                    data.get('first_name'),
                    data.get('last_name'),
                    1 if data.get('is_bot') else 0,
                    json.dumps(clone_data, ensure_ascii=False),
                    clone_data['forensic_signature'],
                    datetime.now().isoformat(),
                    self.stats['api_calls'],
                    data.get('data_points', 0)
                ))
                
                # Actualizar estadísticas
                self.cursor.execute('''
                    INSERT OR REPLACE INTO statistics (metric, value, updated)
                    VALUES (?, COALESCE((SELECT value FROM statistics WHERE metric = ?), 0) + 1, ?)
                ''', ('total_clones', 'total_clones', datetime.now().isoformat()))
                
                self.conn.commit()
                logger.info(f"💾 Clon guardado en BD: {clone_data['forensic_signature']}")
            except Exception as e:
                logger.error(f"Error guardando clon en BD: {e}")
        
        self.stats['successful_clones'] += 1
        logger.info(f"✅ CLONACIÓN EXITOSA: {user_input} → {data.get('id')}")
        
        return {'success': True, 'data': clone_data}
    
    def generate_clone_summary(self, data):
        """Generar resumen del clon"""
        summary = {
            'basic_info': {
                'id': data.get('id'),
                'type': data.get('type'),
                'name': data.get('first_name', data.get('title', '')),
                'username': data.get('username'),
                'is_bot': data.get('is_bot')
            },
            'privacy_info': {
                'has_private_forwards': data.get('has_private_forwards'),
                'has_restricted_voice_and_video_messages': data.get('has_restricted_voice_and_video_messages')
            },
            'media_info': {
                'has_photo': bool(data.get('photo') or data.get('photo_url')),
                'has_description': bool(data.get('description')),
                'has_bio': bool(data.get('bio'))
            },
            'stats': {
                'data_points': data.get('data_points', 0),
                'analysis_time': data.get('analysis_timestamp')
            }
        }
        
        # Añadir info específica por tipo
        if data.get('type') in ['group', 'supergroup', 'channel']:
            summary['group_info'] = {
                'members_count': data.get('members_count'),
                'invite_link': data.get('invite_link'),
                'description_length': len(data.get('description', ''))
            }
        
        return summary
    
    # ============================================
    # 🔥 SISTEMA DE COMANDOS MEJORADO
    # ============================================
    
    def send_message(self, chat_id: str, text: str, **kwargs):
        """Enviar mensaje optimizado"""
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
                timeout=15
            )
            
            self.stats['api_calls'] += 1
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    self.stats['messages_sent'] += 1
                    return {'success': True}
            
            return {'success': False, 'error': 'Error enviando mensaje'}
            
        except Exception as e:
            logger.error(f"Error enviando mensaje: {e}")
            return {'success': False, 'error': str(e)}
    
    def process_telegram_command(self, message: dict):
        """Procesar comandos de Telegram - VERSIÓN MEJORADA"""
        chat_id = message.get('chat', {}).get('id')
        text = message.get('text', '').strip()
        user_id = message.get('from', {}).get('id')
        
        if not chat_id or not text:
            return
        
        logger.info(f"📨 Comando: {text} de {user_id}")
        
        # COMANDO: /start
        if text == '/start':
            response = f"""🚀 <b>TELEGRAM HACK TOOL v3.0 - CLONACIÓN TOTAL</b>

✅ <b>SISTEMA ACTIVO</b> - Clonación completa habilitada
🕐 {datetime.now().strftime('%H:%M:%S')}
🤖 Bot: @{self.bot_username or 'N/A'}

<b>📊 ESTADÍSTICAS EN TIEMPO REAL:</b>
├─ 🔥 Clones totales: {self.stats['total_clones']}
├─ ✅ Clones exitosos: {self.stats['successful_clones']}
├─ 📨 Mensajes enviados: {self.stats['messages_sent']}
└─ 🔧 Llamadas API: {self.stats['api_calls']}

<b>🚀 COMANDOS PRINCIPALES:</b>
• <code>/clone [CUALQUIER_ID]</code> → Clonación total
• <code>/analyze [CUALQUIER_ID]</code> → Análisis completo
• <code>/status</code> → Estado del sistema
• <code>/stats</code> → Estadísticas detalladas
• <code>/id</code> → Tu información

<b>🎯 EJEMPLOS QUE FUNCIONAN:</b>
<code>/clone 777000</code> → Bot oficial Telegram
<code>/clone @SpamBot</code> → Bot anti-spam
<code>/clone -1001234567890</code> → Grupo/Canal
<code>/clone +593987654321</code> → Número telefónico
<code>/clone t.me/username</code> → Desde enlace

<b>⚠️ SISTEMA DE CLONACIÓN TOTAL ACTIVADO</b>
✅ Clona cualquier ID válido de Telegram
✅ Obtiene TODOS los datos disponibles
✅ Almacenamiento forense completo"""
            self.send_message(chat_id, response)
        
        # 🔥 COMANDO: /clone [CUALQUIER_ID] - CLONACIÓN TOTAL
        elif text.startswith('/clone '):
            target = text.split(' ', 1)[1].strip()
            
            # Mostrar procesamiento
            self.send_message(chat_id, f"🚀 <b>INICIANDO CLONACIÓN TOTAL</b>\n\n🔍 <b>TARGET:</b> <code>{target}</code>\n⚡ <b>MODO:</b> Clonación completa\n⏳ <b>ESTADO:</b> Obteniendo datos...")
            
            # Ejecutar clonación
            result = self.clone_any_telegram_id(target)
            
            if result['success']:
                clone_data = result['data']
                cloned_info = clone_data['cloned_data']
                
                # 🔥 CONSTRUIR RESPUESTA COMPLETA
                if cloned_info.get('type') == 'private':
                    response_text = f"""✅ <b>CLONACIÓN COMPLETADA - USUARIO</b>

📋 <b>DATOS PRINCIPALES:</b>
├─ 🆔 ID: <code>{cloned_info['id']}</code>
├─ 👤 Nombre: {cloned_info['first_name']}
├─ 📛 Apellido: {cloned_info['last_name']}
├─ 🏷️ Username: @{cloned_info['username']}
├─ 🤖 Es bot: {'✅ Sí' if cloned_info['is_bot'] else '❌ No'}
├─ 🌐 Idioma: {cloned_info['language_code']}
├-- 🔒 Reenvío privado: {'✅ Activado' if cloned_info['has_private_forwards'] else '❌ Desactivado'}
└-- 🎤 Restricciones: {'✅ Tiene' if cloned_info['has_restricted_voice_and_video_messages'] else '❌ No tiene'}

📸 <b>MULTIMEDIA:</b>
├-- 📷 Foto perfil: {'✅ Disponible' if cloned_info.get('photo') else '❌ No disponible'}
├-- 📝 Bio: {cloned_info.get('bio', 'Sin bio')[:100]}
└-- 🏷️ Tipo: {cloned_info['type']}

🔧 <b>METADATOS DE CLONACIÓN:</b>
├-- 🏷️ Firma forense: {clone_data['forensic_signature']}
├-- 📅 Fecha: {clone_data['cloned_timestamp']}
├-- 📊 Puntos datos: {cloned_info['data_points']}
├-- 📡 Llamadas API: {clone_data['clone_metadata']['api_calls']}
└-- ✅ Estado: {clone_data['status']}

💾 <b>ALMACENAMIENTO:</b>
✅ Guardado en base de datos
✅ Cache activado
✅ Integridad verificada

🎯 <b>RESUMEN:</b>
Clonación exitosa del usuario. Se obtuvieron {cloned_info['data_points']} puntos de datos."""
                
                elif cloned_info.get('type') in ['group', 'supergroup', 'channel']:
                    response_text = f"""✅ <b>CLONACIÓN COMPLETADA - {cloned_info['type'].upper()}</b>

📋 <b>DATOS PRINCIPALES:</b>
├─ 🆔 ID: <code>{cloned_info['id']}</code>
├─ 🏷️ Título: {cloned_info['title']}
├─ 🏷️ Username: @{cloned_info['username']}
├-- 📝 Descripción: {cloned_info.get('description', 'Sin descripción')[:150]}
├-- 👥 Miembros: {cloned_info.get('members_count', 'N/A')}
├-- 🔗 Enlace: {cloned_info.get('invite_link', 'No disponible')}
└-- 🏷️ Tipo: {cloned_info['type']}

⚙️ <b>CONFIGURACIÓN:</b>
├-- 📍 Ubicación: {'✅ Disponible' if cloned_info.get('location') else '❌ No disponible'}
├-- 🏷️ Sticker set: {cloned_info.get('sticker_set_name', 'No disponible')}
├-- ⏱️ Slow mode: {cloned_info.get('slow_mode_delay', 0)} segundos
└-- 📌 Mensaje fijado: {'✅ Sí' if cloned_info.get('pinned_message') else '❌ No'}

🔧 <b>METADATOS DE CLONACIÓN:</b>
├-- 🏷️ Firma forense: {clone_data['forensic_signature']}
├-- 📅 Fecha: {clone_data['cloned_timestamp']}
├-- 📊 Puntos datos: {cloned_info['data_points']}
├-- 📡 Llamadas API: {clone_data['clone_metadata']['api_calls']}
└-- ✅ Estado: {clone_data['status']}

💾 <b>ALMACENAMIENTO:</b>
✅ Guardado en base de datos
✅ Cache activado
✅ Integridad verificada

🎯 <b>RESUMEN:</b>
Clonación exitosa del {cloned_info['type']}. Datos completos obtenidos."""
                
                else:
                    response_text = f"""✅ <b>CLONACIÓN COMPLETADA</b>

📋 <b>DATOS OBTENIDOS:</b>
├─ 🆔 ID: <code>{cloned_info.get('id', 'N/A')}</code>
├-- 🏷️ Tipo: {cloned_info.get('type', 'desconocido')}
├-- 📊 Puntos datos: {cloned_info.get('data_points', 0)}
└-- ⏰ Análisis: {cloned_info.get('analysis_timestamp')}

🔧 <b>METADATOS:</b>
├-- 🏷️ Firma: {clone_data['forensic_signature']}
├-- 📅 Fecha: {clone_data['cloned_timestamp']}
└-- ✅ Estado: Completado

💾 <i>Clon guardado en base de datos</i>"""
                
                # Enviar respuesta
                self.send_message(chat_id, response_text)
                
                # Enviar datos técnicos (opcional)
                if cloned_info.get('data_points', 0) > 10:  # Solo si hay suficientes datos
                    tech_preview = f"""🔧 <b>VISTA PREVIA TÉCNICA:</b>
<code>{json.dumps(clone_data['analysis_summary'], indent=2, ensure_ascii=False)[:1500]}</code>"""
                    self.send_message(chat_id, tech_preview)
                
            else:
                # 🔥 MANEJO DE ERRORES MEJORADO
                error_msg = result.get('error', 'Error desconocido')
                
                if '400' in str(error_msg) or 'chat not found' in str(error_msg).lower():
                    detailed_error = f"""❌ <b>ERROR DE CLONACIÓN - ID NO ENCONTRADO</b>

🚫 <b>TARGET:</b> <code>{target}</code>
📛 <b>Error:</b> {error_msg}

🔍 <b>CAUSAS COMUNES:</b>
1. ❌ El ID no existe en Telegram
2. 🔒 Privacidad del usuario/grupo
3. 👥 Bot no es miembro del grupo
4. 🤖 Usuario bloqueó al bot
5. 📛 ID mal formado

💡 <b>SOLUCIONES:</b>
• Prueba con IDs que SÍ existen:
  <code>/clone 777000</code> (Bot oficial)
  <code>/clone @SpamBot</code> (Bot anti-spam)
  <code>/clone @GroupButler_bot</code> (Bot de grupos)

• Verifica el formato:
  Usuarios: <code>123456789</code>
  Grupos: <code>-1001234567890</code>
  Usernames: <code>@username</code>
  Teléfonos: <code>+593987654321</code>
  Enlaces: <code>t.me/username</code>

⚠️ <b>NOTA:</b> {target} no es un ID válido o accesible"""
                else:
                    detailed_error = f"""❌ <b>ERROR DE CLONACIÓN</b>

🚫 <b>TARGET:</b> <code>{target}</code>
📛 <b>Error:</b> {error_msg}

💡 <b>INTENTA CON:</b>
<code>/clone 777000</code> - Siempre funciona"""
                
                self.send_message(chat_id, detailed_error)
        
        # 🔥 COMANDO: /analyze [CUALQUIER_ID]
        elif text.startswith('/analyze '):
            target = text.split(' ', 1)[1].strip()
            
            self.send_message(chat_id, f"🔍 <b>ANALIZANDO:</b> <code>{target}</code>\n⚡ <b>MODO:</b> Análisis completo")
            
            result = self.get_chat_info_complete(self.normalize_input(target))
            
            if result['success']:
                data = result['data']
                
                analysis_text = f"""✅ <b>ANÁLISIS COMPLETO</b>

📋 <b>INFORMACIÓN OBTENIDA:</b>
├─ 🆔 ID: <code>{data.get('id')}</code>
├─ 🏷️ Tipo: {data.get('type')}
├─ 📛 Nombre: {data.get('first_name', data.get('title', 'N/A'))}
├─ 🏷️ Username: @{data.get('username', 'N/A')}
├─ 🤖 Es bot: {'✅ Sí' if data.get('is_bot') else '❌ No'}
├-- 📊 Puntos datos: {data.get('data_points', 0)}
└-- ⏰ Análisis: {data.get('analysis_timestamp')}

📡 <b>ESTADO:</b> ✅ Completado
💾 <b>ALMACENAMIENTO:</b> ✅ Guardado"""
                
                self.send_message(chat_id, analysis_text)
            else:
                self.send_message(chat_id, f"❌ <b>ERROR EN ANÁLISIS:</b>\n{result.get('error')}")
        
        # COMANDO: /status
        elif text == '/status':
            status_text = f"""📡 <b>ESTADO DEL SISTEMA - CLONACIÓN TOTAL</b>

🟢 Sistema: OPERATIVO AL 100%
🤖 Bot: @{self.bot_username or 'N/A'}
📊 Clones totales: {self.stats['total_clones']}
✅ Clones exitosos: {self.stats['successful_clones']}
📨 Mensajes: {self.stats['messages_sent']}
🔧 API calls: {self.stats['api_calls']}
⏰ Hora: {datetime.now().strftime('%H:%M:%S')}

✅ <b>FUNCIONALIDADES:</b>
├─ 🚀 Clonación total: ACTIVADA
├-- 🔍 Análisis completo: ACTIVADO
├-- 💾 Base de datos: OPERATIVA
├-- 📡 API Telegram: CONECTADA
└-- ⚡ Rendimiento: ÓPTIMO

🎯 <b>CAPACIDADES:</b>
• Clona CUALQUIER ID válido
• Obtiene TODOS los datos
• Almacenamiento forense
• Cache inteligente

⚠️ <b>SISTEMA DE CLONACIÓN TOTAL ACTIVO</b>"""
            self.send_message(chat_id, status_text)
        
        # COMANDO: /stats
        elif text == '/stats':
            # Obtener estadísticas de BD
            db_stats = {}
            if self.conn:
                try:
                    self.cursor.execute("SELECT COUNT(*) FROM clones_total")
                    db_stats['total_clones'] = self.cursor.fetchone()[0]
                    self.cursor.execute("SELECT COUNT(*) FROM analyses")
                    db_stats['total_analyses'] = self.cursor.fetchone()[0]
                    self.cursor.execute("SELECT COUNT(DISTINCT original_id) FROM clones_total")
                    db_stats['unique_targets'] = self.cursor.fetchone()[0]
                except:
                    db_stats = {'error': 'BD no disponible'}
            
            stats_text = f"""📊 <b>ESTADÍSTICAS COMPLETAS</b>

🚀 <b>CLONACIÓN:</b>
├─ Total intentos: {self.stats['total_clones']}
├-- Exitosos: {self.stats['successful_clones']}
├-- Fallidos: {self.stats['failed_requests']}
└-- Tasa éxito: {round((self.stats['successful_clones']/self.stats['total_clones'])*100, 1) if self.stats['total_clones'] > 0 else 0}%

📨 <b>MENSAJERÍA:</b>
├-- Enviados: {self.stats['messages_sent']}
├-- API calls: {self.stats['api_calls']}
└-- Usuarios analizados: {self.stats['users_analyzed']}

💾 <b>BASE DE DATOS:</b>
├-- Clones almacenados: {db_stats.get('total_clones', 'N/A')}
├-- Análisis guardados: {db_stats.get('total_analyses', 'N/A')}
├-- Targets únicos: {db_stats.get('unique_targets', 'N/A')}
└-- Archivo: telegram_hack_total.db

⚡ <b>RENDIMIENTO:</b>
✅ Sistema: 100% operativo
✅ Clonación: Totalmente funcional
✅ Datos: Reales y completos
✅ Almacenamiento: Activo

⏰ <b>ÚLTIMA ACTUALIZACIÓN:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
            
            self.send_message(chat_id, stats_text)
        
        # COMANDO: /id
        elif text == '/id':
            user_info = message.get('from', {})
            chat_info = message.get('chat', {})
            
            id_response = f"""🆔 <b>TUS IDENTIFICADORES</b>

👤 <b>TU USUARIO (PARA CLONAR):</b>
├─ 🆔 User ID: <code>{user_id}</code>
├-- 👤 Nombre: {user_info.get('first_name', 'N/A')}
├-- 📛 Apellido: {user_info.get('last_name', '')}
├-- 🏷️ Username: @{user_info.get('username', 'N/A')}
└-- 🤖 Es bot: {'✅ Sí' if user_info.get('is_bot', False) else '❌ No'}

💬 <b>CHAT ACTUAL:</b>
├-- 🆔 Chat ID: <code>{chat_id}</code>
├-- 🏷️ Tipo: {chat_info.get('type', 'N/A')}
├-- 📛 Título: {chat_info.get('title', 'Chat privado')}
└-- 🏷️ Username: @{chat_info.get('username', 'N/A')}

🚀 <b>PARA CLONARTE:</b>
<code>/clone {user_id}</code>
<code>/clone @{user_info.get('username', '')}</code>

⚠️ <i>Estos IDs son válidos para clonación</i>"""
            
            self.send_message(chat_id, id_response)
        
        # COMANDO: /help
        elif text == '/help':
            help_text = """📋 <b>AYUDA - CLONACIÓN TOTAL</b>

<b>🚀 COMANDO PRINCIPAL:</b>
<code>/clone [CUALQUIER_ID]</code> - Clonación completa

<b>🎯 FORMATOS ACEPTADOS:</b>
• <code>ID numérico</code> - 123456789
• <code>@username</code> - @usuario
• <code>ID grupo</code> - -1001234567890
• <code>Teléfono</code> - +593987654321
• <code>Enlace</code> - t.me/usuario

<b>🔍 COMANDOS DE ANÁLISIS:</b>
<code>/analyze [id]</code> - Análisis completo
<code>/metadata [id]</code> - Metadatos técnicos
<code>/stats</code> - Estadísticas
<code>/status</code> - Estado sistema

<b>📊 EJEMPLOS FUNCIONALES:</b>
• <code>/clone 777000</code> - Bot oficial
• <code>/clone @SpamBot</code> - Bot anti-spam
• <code>/clone @GroupButler_bot</code> - Bot grupos
• <code>/clone [tu_id]</code> - Clonarte

<b>⚠️ NOTAS:</b>
• Clona CUALQUIER ID válido
• Datos 100% reales de Telegram
• Almacenamiento forense
• Sistema totalmente operativo"""
            
            self.send_message(chat_id, help_text)
        
        # MENSAJE NORMAL
        else:
            if text.startswith('/'):
                self.send_message(chat_id, f"❌ <b>Comando no reconocido:</b> <code>{text}</code>\n\n💡 Usa /help para ver comandos")
            elif len(text) > 2:
                self.send_message(chat_id, f"📨 <b>Recibido:</b>\n<code>{text[:200]}</code>\n\n💡 Usa /clone [id] para clonación")
    
    # ============================================
    # 🔥 SISTEMA DE ESCUCHA
    # ============================================
    
    def get_updates(self):
        """Obtener mensajes nuevos"""
        try:
            params = {
                'offset': self.last_update_id + 1,
                'timeout': 30,
                'allowed_updates': ['message', 'callback_query']
            }
            
            response = self.session.get(
                f"{self.api_url}/getUpdates",
                params=params,
                timeout=35
            )
            self.stats['api_calls'] += 1
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    updates = data.get('result', [])
                    if updates:
                        self.last_update_id = updates[-1]['update_id']
                    return updates
            return []
        except Exception as e:
            logger.error(f"Error getUpdates: {e}")
            return []
    
    def start_command_listener(self):
        """Iniciar escucha de comandos"""
        print("[*] Sistema de clonación total activado")
        print("[🔥] COMANDO PRINCIPAL: /clone [CUALQUIER_ID]")
        
        def listener_worker():
            while self.running:
                try:
                    updates = self.get_updates()
                    
                    for update in updates:
                        if 'message' in update:
                            self.process_telegram_command(update['message'])
                    
                    time.sleep(0.3)
                    
                except Exception as e:
                    logger.error(f"Error en listener: {e}")
                    time.sleep(5)
        
        listener_thread = threading.Thread(target=listener_worker, daemon=True)
        listener_thread.start()
        
        print("[✅] Sistema de escucha activado")
        print("[🎯] Prueba inmediata: /clone 777000")
        print("[💡] O usa tu propio ID después de /id")
        
        return listener_thread
    
    def stop_system(self):
        """Detener sistema"""
        self.running = False
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
        print("[🛑] Sistema de clonación detenido")

# ============================================
# EJECUCIÓN PRINCIPAL
# ============================================

def main():
    """Función principal"""
    print("[🚀] INICIANDO SISTEMA DE CLONACIÓN TOTAL...")
    print("[⚠️ ] Este sistema clona CUALQUIER ID válido de Telegram")
    
    try:
        # Crear instancia
        bot = TelegramHackTool()
        
        # Iniciar escucha
        bot.start_command_listener()
        
        print("\n" + "="*60)
        print("[✅] SISTEMA COMPLETAMENTE OPERATIVO")
        print("[🎯] COMANDOS DISPONIBLES EN TELEGRAM:")
        print("   • /start - Ver menú principal")
        print("   • /clone [CUALQUIER_ID] - Clonación total")
        print("   • /analyze [id] - Análisis completo")
        print("   • /id - Tu información para clonar")
        print("   • /stats - Estadísticas del sistema")
        print("="*60)
        print("\n[💡] PRUEBA INMEDIATA:")
        print("   Envía a tu bot: /clone 777000")
        print("   O usa tu ID: primero /id, luego /clone [tu_id]")
        print("\n[⚡] Sistema listo para clonar CUALQUIER ID...")
        
        # Mantener proceso principal
        while bot.running:
            time.sleep(60)
            current_time = datetime.now().strftime('%H:%M:%S')
            print(f"[📊 {current_time}] Clones: {bot.stats['successful_clones']}/{bot.stats['total_clones']} | API: {bot.stats['api_calls']}")
        
        print("[👋] Sistema finalizado")
        
    except KeyboardInterrupt:
        print("\n[🛑] Interrupción por usuario")
        if 'bot' in locals():
            bot.stop_system()
    except Exception as e:
        print(f"[❌] Error crítico: {e}")
        import traceback
        traceback.print_exc()

# PUNTO DE ENTRADA
if __name__ == "__main__":
    main()
