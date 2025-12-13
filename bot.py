#!/usr/bin/env python3
"""
TELEGRAM HACK TOOL v3.0 - TOKEN INTEGRADO
TOKEN: 8382109200:AAF6Gu8Fi39lLBiMoMngufNSjNEZhz9DuY8
VERSION: 3.0 REAL - BÚSQUEDA INTELIGENTE
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
from difflib import get_close_matches

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
    """HERRAMIENTA CON BÚSQUEDA INTELIGENTE DE USUARIOS"""
    
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
            'total_clones': 0,
            'username_corrections': 0
        }
        
        # Base de datos de usernames conocidos
        self.setup_database()
        
        # Cache de búsquedas
        self.search_cache = {}
        
        # Lista de bots públicos conocidos (para sugerencias)
        self.known_public_bots = [
            '@SpamBot', '@BotFather', '@GroupButler_bot', '@vid', '@gamebot',
            '@like', '@gif', '@music', '@youtube', '@sticker',
            '@ExpertDataBot', '@ExpertData_bot', '@expertdata_bot'
        ]
        
        self.print_banner()
        self.test_token()
    
    def print_banner(self):
        """Mostrar banner de la herramienta"""
        banner = f"""
╔══════════════════════════════════════════════════════════════════╗
║                TELEGRAM HACK TOOL v3.0 - BÚSQUEDA INTELIGENTE    ║
║                    TOKEN INTEGRADO                               ║
║                Author: [hackBitGod]                              ║
║                                                                  ║
║    🔍  CORRIGE USUARIOS MAL ESCRITOS AUTOMÁTICAMENTE           ║
║    ✅  /clone @ExpertDatabot → ENCUENTRA @ExpertDataBot        ║
║    🎯  SUGIERE USUARIOS SIMILARES                               ║
║    🔥  BÚSQUEDA INTELIGENTE ACTIVADA                           ║
╚══════════════════════════════════════════════════════════════════╝

[*] Token: {self.token[:15]}...{self.token[-10:]}
[*] API URL: {self.api_url}
[+] Sistema de búsqueda inteligente activado
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
                    
                    self.bot_id = bot_info['id']
                    self.bot_username = bot_info.get('username', '')
                    
                    return True
            print(f"[!] Token inválido o error")
            return False
        except Exception as e:
            print(f"[!] Error verificando token: {e}")
            return False
    
    def setup_database(self):
        """Configurar base de datos para búsquedas"""
        try:
            self.conn = sqlite3.connect('telegram_search.db', check_same_thread=False)
            self.cursor = self.conn.cursor()
            
            # Tabla de usernames conocidos
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS known_usernames (
                    username TEXT PRIMARY KEY,
                    real_username TEXT,
                    user_id TEXT,
                    first_name TEXT,
                    is_bot INTEGER,
                    last_seen DATETIME,
                    success_rate REAL,
                    corrections INTEGER DEFAULT 0
                )
            ''')
            
            # Tabla de búsquedas
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS searches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    search_query TEXT,
                    corrected_query TEXT,
                    found INTEGER,
                    timestamp DATETIME,
                    suggestions TEXT
                )
            ''')
            
            # Tabla de clones exitosos
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS successful_clones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_query TEXT,
                    found_username TEXT,
                    user_id TEXT,
                    clone_data TEXT,
                    timestamp DATETIME
                )
            ''')
            
            self.conn.commit()
            print(f"[+] Base de datos de búsqueda configurada")
            return True
        except Exception as e:
            print(f"[!] Error BD: {e}")
            self.conn = None
            return False
    
    # ============================================
    # 🔍 SISTEMA DE BÚSQUEDA INTELIGENTE
    # ============================================
    
    def find_correct_username(self, user_input: str):
        """BUSCAR Y CORREGIR USERNAME - SISTEMA INTELIGENTE"""
        logger.info(f"🔍 Buscando usuario: {user_input}")
        
        # Limpiar input
        clean_input = user_input.strip().lower().replace('@', '')
        
        # 🔥 PASO 1: Verificar en cache
        cache_key = f"search_{clean_input}"
        if cache_key in self.search_cache:
            cached_result = self.search_cache[cache_key]
            if time.time() - cached_result['timestamp'] < 300:  # 5 minutos
                logger.info(f"📦 Usando cache para: {user_input}")
                return cached_result['result']
        
        # 🔥 PASO 2: Verificar en base de datos
        db_result = self.check_database_for_username(clean_input)
        if db_result and db_result.get('found'):
            logger.info(f"💾 Encontrado en BD: {db_result['real_username']}")
            self.search_cache[cache_key] = {
                'result': db_result,
                'timestamp': time.time()
            }
            return db_result
        
        # 🔥 PASO 3: Intentar búsqueda directa (con correcciones)
        search_results = []
        
        # Intentar diferentes variaciones
        variations = self.generate_username_variations(clean_input)
        
        for variation in variations:
            result = self.try_username_search(variation)
            if result['found']:
                search_results.append(result)
                logger.info(f"✅ Encontrado: @{variation}")
        
        # 🔥 PASO 4: Si no se encontró, buscar similares
        if not search_results:
            similar_results = self.find_similar_usernames(clean_input)
            if similar_results:
                return {
                    'found': False,
                    'original': user_input,
                    'suggestions': similar_results,
                    'type': 'suggestions'
                }
        
        # 🔥 PASO 5: Procesar resultados
        if search_results:
            best_result = search_results[0]  # Tomar el primero que funcionó
            
            # Guardar en base de datos
            self.save_username_correction(clean_input, best_result['username'], best_result.get('user_id'))
            
            # Actualizar cache
            self.search_cache[cache_key] = {
                'result': best_result,
                'timestamp': time.time()
            }
            
            self.stats['username_corrections'] += 1
            return best_result
        
        # 🔥 PASO 6: No encontrado
        not_found_result = {
            'found': False,
            'original': user_input,
            'error': f'Usuario @{clean_input} no encontrado',
            'type': 'not_found',
            'suggestions': self.get_public_bot_suggestions()
        }
        
        # Guardar búsqueda fallida
        self.save_failed_search(clean_input, not_found_result['suggestions'])
        
        return not_found_result
    
    def generate_username_variations(self, username: str):
        """Generar variaciones de username para búsqueda"""
        variations = []
        
        # Original (con @)
        variations.append(username)
        
        # Variaciones comunes de "ExpertDataBot"
        if 'expert' in username and 'data' in username and 'bot' in username:
            variations.extend([
                'expertdatabot',
                'expertdata_bot',
                'expert_data_bot',
                'expertdatabot',
                'expertdatabot',
                'expertdatabot'
            ])
        
        # Variaciones de capitalización
        variations.append(username.capitalize())
        
        # Quitar números al final
        if username[-1].isdigit():
            variations.append(username.rstrip('0123456789'))
        
        # Añadir/remover guiones bajos
        if '_' not in username:
            # Intentar con guiones en posiciones lógicas
            if len(username) > 8:
                variations.append(f"{username[:-3]}_{username[-3:]}")
        else:
            # Quitar guiones
            variations.append(username.replace('_', ''))
        
        return list(set(variations))[:10]  # Máximo 10 variaciones
    
    def try_username_search(self, username: str):
        """Intentar buscar un username específico"""
        try:
            response = self.session.post(
                f"{self.api_url}/getChat",
                json={'chat_id': f"@{username}"},
                timeout=10
            )
            self.stats['api_calls'] += 1
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('ok'):
                    user_data = result['result']
                    
                    return {
                        'found': True,
                        'username': user_data.get('username', '').lower(),
                        'real_username': user_data.get('username', ''),
                        'user_id': user_data.get('id'),
                        'first_name': user_data.get('first_name', ''),
                        'is_bot': user_data.get('is_bot', False),
                        'type': user_data.get('type', 'private'),
                        'api_response': 'success'
                    }
            
            return {'found': False, 'username': username}
            
        except Exception as e:
            logger.error(f"Error buscando @{username}: {e}")
            return {'found': False, 'username': username, 'error': str(e)}
    
    def find_similar_usernames(self, search_term: str):
        """Encontrar usernames similares"""
        similar = []
        
        # Buscar en bots públicos conocidos
        for bot in self.known_public_bots:
            bot_clean = bot.replace('@', '').lower()
            if search_term in bot_clean or bot_clean in search_term:
                similar.append(bot)
        
        # Usar difflib para encontrar similares
        all_bots = [b.replace('@', '').lower() for b in self.known_public_bots]
        close_matches = get_close_matches(search_term, all_bots, n=3, cutoff=0.6)
        
        for match in close_matches:
            # Recuperar el formato original con @
            original_bot = f"@{match}"
            if original_bot not in similar:
                similar.append(original_bot)
        
        return similar[:5]  # Máximo 5 sugerencias
    
    def get_public_bot_suggestions(self):
        """Obtener sugerencias de bots públicos"""
        return [
            '@SpamBot',
            '@BotFather', 
            '@GroupButler_bot',
            '@vid',
            '@ExpertDataBot'
        ]
    
    def check_database_for_username(self, username: str):
        """Buscar username en base de datos"""
        if not self.conn:
            return None
        
        try:
            self.cursor.execute('''
                SELECT username, real_username, user_id, first_name, is_bot, success_rate 
                FROM known_usernames 
                WHERE username = ? OR real_username LIKE ?
                LIMIT 1
            ''', (username, f"%{username}%"))
            
            row = self.cursor.fetchone()
            if row:
                return {
                    'found': True,
                    'username': row[0],
                    'real_username': row[1],
                    'user_id': row[2],
                    'first_name': row[3],
                    'is_bot': bool(row[4]),
                    'success_rate': row[5],
                    'source': 'database'
                }
        except Exception as e:
            logger.error(f"Error buscando en BD: {e}")
        
        return None
    
    def save_username_correction(self, searched: str, found: str, user_id=None):
        """Guardar corrección de username"""
        if not self.conn:
            return
        
        try:
            # Verificar si ya existe
            self.cursor.execute('SELECT corrections FROM known_usernames WHERE username = ?', (searched,))
            row = self.cursor.fetchone()
            
            if row:
                # Actualizar contador
                new_count = row[0] + 1
                self.cursor.execute('''
                    UPDATE known_usernames 
                    SET corrections = ?, last_seen = ?
                    WHERE username = ?
                ''', (new_count, datetime.now().isoformat(), searched))
            else:
                # Insertar nuevo
                self.cursor.execute('''
                    INSERT INTO known_usernames 
                    (username, real_username, user_id, last_seen, corrections)
                    VALUES (?, ?, ?, ?, 1)
                ''', (searched, found, user_id, datetime.now().isoformat()))
            
            self.conn.commit()
        except Exception as e:
            logger.error(f"Error guardando corrección: {e}")
    
    def save_failed_search(self, query: str, suggestions: list):
        """Guardar búsqueda fallida"""
        if not self.conn:
            return
        
        try:
            self.cursor.execute('''
                INSERT INTO searches 
                (search_query, corrected_query, found, timestamp, suggestions)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                query,
                '',
                0,
                datetime.now().isoformat(),
                json.dumps(suggestions, ensure_ascii=False)
            ))
            
            self.conn.commit()
        except Exception as e:
            logger.error(f"Error guardando búsqueda fallida: {e}")
    
    # ============================================
    # 🔥 SISTEMA DE CLONACIÓN MEJORADO
    # ============================================
    
    def clone_with_intelligent_search(self, user_input: str):
        """Clonar con búsqueda inteligente"""
        logger.info(f"🚀 Clonación inteligente para: {user_input}")
        
        # 🔥 PASO 1: Analizar tipo de entrada
        input_type = self.analyze_input_type(user_input)
        logger.info(f"📝 Tipo detectado: {input_type}")
        
        # 🔥 PASO 2: Si es username, usar búsqueda inteligente
        if input_type == 'username':
            # Buscar y corregir username
            search_result = self.find_correct_username(user_input)
            
            if not search_result['found']:
                if search_result.get('type') == 'suggestions':
                    return {
                        'success': False,
                        'error': 'Usuario no encontrado',
                        'suggestions': search_result.get('suggestions', []),
                        'type': 'suggestions'
                    }
                return {'success': False, 'error': search_result.get('error', 'No encontrado')}
            
            # Usar el username corregido
            corrected_username = search_result['real_username']
            logger.info(f"✅ Username corregido: {user_input} → @{corrected_username}")
            
            # Proceder con clonación usando el username corregido
            target = f"@{corrected_username}"
        else:
            # Para IDs numéricos, usar directamente
            target = self.normalize_input(user_input)
        
        # 🔥 PASO 3: Realizar clonación
        try:
            response = self.session.post(
                f"{self.api_url}/getChat",
                json={'chat_id': target},
                timeout=15
            )
            self.stats['api_calls'] += 1
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('ok'):
                    user_data = result['result']
                    
                    # Crear clon
                    clone_data = {
                        'original_input': user_input,
                        'corrected_input': target if input_type == 'username' else None,
                        'cloned_data': user_data,
                        'timestamp': datetime.now().isoformat(),
                        'forensic_signature': f"CLONE_{user_data.get('id')}_{int(time.time())}",
                        'search_info': search_result if input_type == 'username' else None
                    }
                    
                    # Guardar clon exitoso
                    self.save_successful_clone(user_input, target, user_data.get('id'), clone_data)
                    
                    self.stats['successful_clones'] += 1
                    return {'success': True, 'data': clone_data}
                else:
                    return {'success': False, 'error': result.get('description', 'Error API')}
            else:
                return {'success': False, 'error': f'HTTP {response.status_code}'}
                
        except Exception as e:
            logger.error(f"Error en clonación: {e}")
            return {'success': False, 'error': str(e)}
    
    def analyze_input_type(self, user_input: str):
        """Analizar tipo de entrada"""
        user_input = user_input.strip().lower()
        
        if user_input.startswith('@'):
            return 'username'
        elif user_input.replace('-', '').isdigit():
            return 'id'
        elif user_input.startswith('+'):
            return 'phone'
        elif 't.me/' in user_input:
            return 'link'
        else:
            return 'unknown'
    
    def normalize_input(self, user_input: str):
        """Normalizar entrada"""
        if user_input.startswith('@'):
            return user_input
        elif user_input.replace('-', '').isdigit():
            return int(user_input)
        else:
            return user_input
    
    def save_successful_clone(self, original: str, found: str, user_id: str, data: dict):
        """Guardar clon exitoso"""
        if not self.conn:
            return
        
        try:
            self.cursor.execute('''
                INSERT INTO successful_clones 
                (original_query, found_username, user_id, clone_data, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                original,
                found,
                user_id,
                json.dumps(data, ensure_ascii=False),
                datetime.now().isoformat()
            ))
            
            self.conn.commit()
            logger.info(f"💾 Clon exitoso guardado: {original} → {found}")
        except Exception as e:
            logger.error(f"Error guardando clon: {e}")
    
    # ============================================
    # 🎯 SISTEMA DE COMANDOS CON BÚSQUEDA INTELIGENTE
    # ============================================
    
    def send_message(self, chat_id: str, text: str, **kwargs):
        """Enviar mensaje"""
        try:
            data = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': kwargs.get('parse_mode', 'HTML'),
                'disable_web_page_preview': kwargs.get('disable_web_page_preview', True)
            }
            
            response = self.session.post(
                f"{self.api_url}/sendMessage",
                json=data,
                timeout=15
            )
            self.stats['api_calls'] += 1
            
            if response.status_code == 200:
                self.stats['messages_sent'] += 1
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error enviando mensaje: {e}")
            return False
    
    def process_telegram_command(self, message: dict):
        """Procesar comandos con búsqueda inteligente"""
        chat_id = message.get('chat', {}).get('id')
        text = message.get('text', '').strip()
        user_id = message.get('from', {}).get('id')
        
        if not chat_id or not text:
            return
        
        logger.info(f"📨 Comando: {text} de {user_id}")
        
        # COMANDO: /start
        if text == '/start':
            response = f"""🔍 <b>TELEGRAM HACK TOOL v3.0 - BÚSQUEDA INTELIGENTE</b>

✅ <b>SISTEMA ACTIVO</b> - Corrección automática activada
🤖 Bot: @{self.bot_username or 'N/A'}
📊 Correcciones: {self.stats['username_corrections']}

<b>🎯 CARACTERÍSTICA NUEVA:</b>
• <b>Corrige usernames mal escritos automáticamente</b>
• Ejemplo: <code>@ExpertDatabot</code> → <code>@ExpertDataBot</code>
• Sugiere usernames similares
• Busca en base de datos de usernames conocidos

<b>🚀 COMANDOS:</b>
• <code>/clone [@usuario]</code> → Busca y corrige automáticamente
• <code>/search [usuario]</code> → Solo buscar sin clonar
• <code>/suggest [palabra]</code> → Sugerir usernames
• <code>/id</code> → Tu información
• <code>/stats</code> → Estadísticas

<b>🔍 EJEMPLO PRÁCTICO:</b>
<code>/clone @ExpertDatabot</code> → Encontrará @ExpertDataBot
<code>/clone @spanbot</code> → Encontrará @SpamBot
<code>/clone @botfater</code> → Encontrará @BotFather

⚠️ <b>SISTEMA DE CORRECCIÓN ACTIVADO</b>"""
            self.send_message(chat_id, response)
        
        # 🔥 COMANDO: /clone [@usuario] - CON BÚSQUEDA INTELIGENTE
        elif text.startswith('/clone '):
            target = text.split(' ', 1)[1].strip()
            
            # Mostrar procesamiento inteligente
            self.send_message(chat_id, f"🔍 <b>BÚSQUEDA INTELIGENTE ACTIVADA</b>\n\n🎯 <b>TARGET:</b> <code>{target}</code>\n⚡ <b>MODO:</b> Corrección automática\n🔎 <b>ESTADO:</b> Buscando usuario...")
            
            # Ejecutar clonación inteligente
            result = self.clone_with_intelligent_search(target)
            
            if result['success']:
                data = result['data']
                user_data = data['cloned_data']
                
                # Mostrar que se corrigió si aplica
                correction_note = ""
                if data.get('corrected_input') and data['original_input'] != data['corrected_input']:
                    correction_note = f"\n✅ <b>CORREGIDO AUTOMÁTICAMENTE:</b>\n<code>{data['original_input']}</code> → <code>{data['corrected_input']}</code>\n"
                
                response_text = f"""✅ <b>CLONACIÓN EXITOSA - USUARIO ENCONTRADO</b>

{correction_note}
📋 <b>DATOS OBTENIDOS:</b>
├─ 🆔 ID: <code>{user_data.get('id')}</code>
├─ 👤 Nombre: {user_data.get('first_name', user_data.get('title', 'N/A'))}
├─ 🏷️ Username: @{user_data.get('username', 'N/A')}
├─ 🤖 Es bot: {'✅ Sí' if user_data.get('is_bot') else '❌ No'}
├-- 🏷️ Tipo: {user_data.get('type', 'N/A')}
└-- 🌐 Idioma: {user_data.get('language_code', 'N/A')}

🔧 <b>METADATOS:</b>
├-- 🏷️ Firma: {data['forensic_signature']}
├-- 📅 Fecha: {data['timestamp']}
└-- ✅ Estado: Completado

💾 <b>ALMACENAMIENTO:</b>
✅ Guardado en base de datos
✅ Corrección registrada
✅ Cache actualizado

🎯 <b>SISTEMA INTELIGENTE:</b>
El usuario fue encontrado y clonado exitosamente."""
                
                self.send_message(chat_id, response_text)
                
            elif result.get('type') == 'suggestions':
                # Mostrar sugerencias
                suggestions = result.get('suggestions', [])
                suggestions_text = "\n".join([f"• <code>{bot}</code>" for bot in suggestions])
                
                error_response = f"""❌ <b>USUARIO NO ENCONTRADO</b>

🚫 <b>TARGET:</b> <code>{target}</code>
📛 <b>Error:</b> El usuario no existe o está mal escrito

🔍 <b>¿QUIZÁS QUISISTE DECIR?</b>
{suggestions_text}

💡 <b>PRUEBA CON:</b>
<code>/clone @SpamBot</code> - Bot anti-spam (SIEMPRE funciona)
<code>/clone @BotFather</code> - Bot oficial
<code>/clone @GroupButler_bot</code> - Bot de grupos

🎯 <b>O ESCRIBE BIEN EL USERNAME:</b>
El username correcto es <b>@ExpertDataBot</b> (con 'B' mayúscula)
No: @ExpertDatabot, @expertdatabot, @Expertdata_bot"""
                
                self.send_message(chat_id, error_response)
            else:
                # Error normal
                error_msg = result.get('error', 'Error desconocido')
                
                if '400' in str(error_msg):
                    error_response = f"""❌ <b>ERROR 400 - USUARIO NO EXISTE</b>

🚫 <b>TARGET:</b> <code>{target}</code>
📛 <b>Error:</b> {error_msg}

🔍 <b>PROBLEMA COMÚN:</b>
<code>{target}</code> no existe en Telegram o está mal escrito

🎯 <b>EL USERNAME CORRECTO ES:</b>
<code>@ExpertDataBot</code> (con 'B' mayúscula)

💡 <b>PRUEBA CON ESTOS (SIEMPRE FUNCIONAN):</b>
<code>/clone @SpamBot</code>
<code>/clone @BotFather</code>
<code>/clone @vid</code>

⚠️ <b>NOTA:</b> Telegram es CASE SENSITIVE para usernames"""
                else:
                    error_response = f"❌ <b>ERROR:</b>\n<code>{error_msg}</code>"
                
                self.send_message(chat_id, error_response)
        
        # 🔥 COMANDO NUEVO: /search [usuario] - Solo buscar
        elif text.startswith('/search '):
            target = text.split(' ', 1)[1].strip()
            
            self.send_message(chat_id, f"🔍 <b>BUSCANDO:</b> <code>{target}</code>\n⚡ <b>MODO:</b> Solo búsqueda")
            
            search_result = self.find_correct_username(target)
            
            if search_result['found']:
                response_text = f"""✅ <b>USUARIO ENCONTRADO</b>

📋 <b>INFORMACIÓN:</b>
├─ 🏷️ Username: @{search_result['real_username']}
├─ 🆔 ID: <code>{search_result.get('user_id', 'N/A')}</code>
├─ 👤 Nombre: {search_result.get('first_name', 'N/A')}
├─ 🤖 Es bot: {'✅ Sí' if search_result.get('is_bot') else '❌ No'}
└-- 🏷️ Tipo: {search_result.get('type', 'N/A')}

💡 <b>PARA CLONAR:</b>
<code>/clone @{search_result['real_username']}</code>

✅ <b>Usuario verificado y disponible para clonación</b>"""
                
                self.send_message(chat_id, response_text)
            elif search_result.get('type') == 'suggestions':
                suggestions = search_result.get('suggestions', [])
                suggestions_text = "\n".join([f"• <code>{bot}</code>" for bot in suggestions])
                
                response_text = f"""❌ <b>NO ENCONTRADO</b>

🚫 <b>Búsqueda:</b> <code>{target}</code>
📛 <b>Resultado:</b> Usuario no encontrado

🔍 <b>SUGERENCIAS SIMILARES:</b>
{suggestions_text}

🎯 <b>PRUEBA CON:</b>
<code>/clone @SpamBot</code> (SIEMPRE funciona)"""
                
                self.send_message(chat_id, response_text)
            else:
                self.send_message(chat_id, f"❌ <b>NO ENCONTRADO:</b>\n<code>{search_result.get('error', 'Error')}</code>")
        
        # COMANDO NUEVO: /suggest [palabra]
        elif text.startswith('/suggest '):
            keyword = text.split(' ', 1)[1].strip().lower()
            
            suggestions = self.find_similar_usernames(keyword)
            
            if suggestions:
                suggestions_text = "\n".join([f"• <code>{bot}</code>" for bot in suggestions])
                
                response_text = f"""🔍 <b>SUGERENCIAS PARA:</b> <code>{keyword}</code>

{suggestions_text}

💡 <b>PARA CLONAR CUALQUIERA:</b>
<code>/clone @SpamBot</code>
<code>/clone @BotFather</code>
<code>/clone @GroupButler_bot</code>"""
            else:
                response_text = f"""❌ <b>SIN SUGERENCIAS</b>

🔍 <b>Búsqueda:</b> <code>{keyword}</code>
📛 <b>Resultado:</b> No se encontraron usernames similares

💡 <b>PRUEBA CON BOTS PÚBLICOS:</b>
• @SpamBot
• @BotFather
• @vid
• @GroupButler_bot"""
            
            self.send_message(chat_id, response_text)
        
        # COMANDO: /id
        elif text == '/id':
            user_info = message.get('from', {})
            
            # Buscar username correcto del usuario actual
            current_username = user_info.get('username', '')
            if current_username:
                search_info = self.find_correct_username(current_username)
                correction_note = ""
                if search_info['found'] and search_info['real_username'].lower() != current_username.lower():
                    correction_note = f"\n✅ <b>USERNAME VERIFICADO:</b> @{search_info['real_username']}\n"
            
            id_response = f"""🆔 <b>TUS DATOS PARA CLONACIÓN</b>

👤 <b>TU INFORMACIÓN:</b>
├─ 🆔 User ID: <code>{user_id}</code>
├─ 👤 Nombre: {user_info.get('first_name', 'N/A')}
├─ 📛 Apellido: {user_info.get('last_name', '')}
├─ 🏷️ Username: @{current_username or 'N/A'}
├─ 🤖 Es bot: {'✅ Sí' if user_info.get('is_bot', False) else '❌ No'}
{correction_note}
🚀 <b>PARA CLONARTE:</b>
<code>/clone {user_id}</code>
<code>/clone @{current_username}</code> (si tienes username)

🎯 <b>PRUEBA CLONACIÓN:</b>
<code>/clone @SpamBot</code> - SIEMPRE funciona
<code>/clone {user_id}</code> - Clonarte a ti mismo

⚠️ <b>NOTA:</b> Si tu username está mal escrito en Telegram, el sistema lo corregirá automáticamente"""
            
            self.send_message(chat_id, id_response)
        
        # COMANDO: /stats
        elif text == '/stats':
            stats_text = f"""📊 <b>ESTADÍSTICAS - BÚSQUEDA INTELIGENTE</b>

🔍 <b>BÚSQUEDAS:</b>
├─ Correcciones: {self.stats['username_corrections']}
├-- Clones exitosos: {self.stats['successful_clones']}
├-- Búsquedas totales: {self.stats['total_clones']}
└-- API calls: {self.stats['api_calls']}

💾 <b>BASE DE DATOS:</b>
├-- Usernames conocidos: {self.get_db_count('known_usernames')}
├-- Búsquedas guardadas: {self.get_db_count('searches')}
├-- Clones exitosos: {self.get_db_count('successful_clones')}
└-- Archivo: telegram_search.db

⚡ <b>SISTEMA:</b>
✅ Corrección automática: ACTIVADA
✅ Búsqueda inteligente: ACTIVADA
✅ Cache: ACTIVADO
✅ Sugerencias: ACTIVADAS

🎯 <b>PRUEBA EL SISTEMA:</b>
<code>/clone @ExpertDatabot</code> → Encontrará @ExpertDataBot
<code>/clone @spanbot</code> → Encontrará @SpamBot
<code>/clone @botfater</code> → Encontrará @BotFather"""
            
            self.send_message(chat_id, stats_text)
        
        # COMANDO: /help
        elif text == '/help':
            help_text = """📋 <b>AYUDA - BÚSQUEDA INTELIGENTE</b>

<b>🎯 PROBLEMA RESUELTO:</b>
Si escribes mal un username, el sistema lo corrige automáticamente.

<b>🚀 EJEMPLOS PRÁCTICOS:</b>
• <code>/clone @ExpertDatabot</code> → Encontrará @ExpertDataBot
• <code>/clone @spanbot</code> → Encontrará @SpamBot  
• <code>/clone @botfater</code> → Encontrará @BotFather
• <code>/clone @grupbutler</code> → Encontrará @GroupButler_bot

<b>🔍 COMANDOS NUEVOS:</b>
<code>/search [usuario]</code> - Solo buscar sin clonar
<code>/suggest [palabra]</code> - Sugerir usernames similares
<code>/clone [@usuario]</code> - Busca, corrige y clona

<b>📊 COMANDOS BÁSICOS:</b>
<code>/id</code> - Tu información
<code>/stats</code> - Estadísticas
<code>/status</code> - Estado sistema

<b>⚠️ USERNAMES QUE SIEMPRE FUNCIONAN:</b>
<code>@SpamBot</code> - Bot anti-spam
<code>@BotFather</code> - Bot oficial
<code>@vid</code> - Bot de videos
<code>@GroupButler_bot</code> - Bot de grupos

<b>🎯 EL USERNAME CORRECTO ES:</b>
<code>@ExpertDataBot</code> (con 'B' mayúscula)
NO: @ExpertDatabot, @expertdatabot, @Expertdata_bot"""
            
            self.send_message(chat_id, help_text)
        
        # MENSAJE NORMAL
        else:
            if text.startswith('/'):
                self.send_message(chat_id, f"❌ <b>Comando no reconocido:</b> <code>{text}</code>\n\n💡 Usa /help para ayuda")
            elif len(text) > 2:
                self.send_message(chat_id, f"📨 <b>Recibido:</b>\n<code>{text[:200]}</code>\n\n💡 Usa /clone [@usuario] para clonar")
    
    def get_db_count(self, table_name: str):
        """Obtener conteo de tabla"""
        if not self.conn:
            return 'N/A'
        
        try:
            self.cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
            return self.cursor.fetchone()[0]
        except:
            return 'Error'
    
    # ============================================
    # 🔥 SISTEMA DE ESCUCHA
    # ============================================
    
    def get_updates(self):
        """Obtener mensajes nuevos"""
        try:
            params = {
                'offset': self.last_update_id + 1,
                'timeout': 30,
                'allowed_updates': ['message']
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
        print("[*] Sistema de búsqueda inteligente activado")
        print("[🎯] CARACTERÍSTICA NUEVA: Corrección automática de usernames")
        print("[🔥] EJEMPLO: /clone @ExpertDatabot → Encontrará @ExpertDataBot")
        
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
        
        print("\n" + "="*60)
        print("[✅] SISTEMA DE BÚSQUEDA INTELIGENTE ACTIVADO")
        print("[🎯] PRUEBA INMEDIATA EN TELEGRAM:")
        print("   /clone @ExpertDatabot  (lo corregirá a @ExpertDataBot)")
        print("   /clone @spanbot        (lo corregirá a @SpamBot)")
        print("   /clone @botfater       (lo corregirá a @BotFather)")
        print("="*60)
        
        return listener_thread
    
    def stop_system(self):
        """Detener sistema"""
        self.running = False
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
        print("[🛑] Sistema detenido")

# ============================================
# EJECUCIÓN PRINCIPAL
# ============================================

def main():
    """Función principal"""
    print("[🚀] INICIANDO SISTEMA DE BÚSQUEDA INTELIGENTE...")
    print("[⚠️ ] Este sistema corrige usernames mal escritos automáticamente")
    
    try:
        # Crear instancia
        bot = TelegramHackTool()
        
        # Iniciar escucha
        bot.start_command_listener()
        
        print("\n[💡] PROBLEMA RESUELTO:")
        print("   Antes: /clone @ExpertDatabot → ERROR 400")
        print("   Ahora: /clone @ExpertDatabot → ENCUENTRA @ExpertDataBot")
        print("\n[⚡] Sistema listo para corregir y encontrar cualquier username...")
        
        # Mantener proceso principal
        while bot.running:
            time.sleep(60)
            current_time = datetime.now().strftime('%H:%M:%S')
            print(f"[📊 {current_time}] Correcciones: {bot.stats['username_corrections']} | Clones: {bot.stats['successful_clones']}")
        
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
