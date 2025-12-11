const TelegramBot = require('node-telegram-bot-api');
require('dotenv').config();

const token = process.env.TELEGRAM_BOT_TOKEN;
const bot = new TelegramBot(token, { polling: true });

console.log('🕵️‍♂️ Bot OSINT iniciado...');

// COMANDOS BÁSICOS
bot.onText(/\/start/, (msg) => {
    const chatId = msg.chat.id;
    const userName = msg.from.first_name;
    
    const welcome = `
🕵️‍♂️ *Bienvenido ${userName} al OSINT Bot*

*Comandos:*
🔍 /ip [IP] - Información de IP
🌐 /domain [url] - Análisis de dominio
👤 /user [username] - Buscar usuario
📸 Envía imagen - Analizar EXIF
ℹ️ /help - Más comandos
    `;
    
    bot.sendMessage(chatId, welcome, { parse_mode: 'Markdown' });
});

bot.onText(/\/help/, (msg) => {
    const chatId = msg.chat.id;
    const help = `
🕵️‍♂️ *OSINT Bot - Ayuda*

🔍 *Investigación Digital:*
/ip [IP] - Información de dirección IP
/domain [url] - Análisis de dominio
/whois [dominio] - Consulta WHOIS

👤 *Personas:*
/user [username] - Buscar en redes
/email [email] - Verificar email

📊 *Multimedia:*
Envía imagen - Analizar metadatos EXIF

📍 *Geolocalización:*
/geo [IP] - Ubicación geográfica

⚙️ *Otros:*
/status - Estado del bot
/report [texto] - Reportar problema
    `;
    
    bot.sendMessage(chatId, help, { parse_mode: 'Markdown' });
});

// Análisis de IP (versión simple)
bot.onText(/\/ip (.+)/, async (msg, match) => {
    const chatId = msg.chat.id;
    const ip = match[1];
    
    bot.sendMessage(chatId, `🔍 Analizando IP: ${ip}...`);
    
    try {
        const axios = require('axios');
        const response = await axios.get(`http://ip-api.com/json/${ip}?lang=es`);
        
        if (response.data.status === 'success') {
            const info = `
🔍 *IP:* ${ip}
📍 *Ubicación:* ${response.data.city}, ${response.data.country}
🌐 *ISP:* ${response.data.isp}
🏢 *Org:* ${response.data.org}
📡 *AS:* ${response.data.as}
            `;
            bot.sendMessage(chatId, info, { parse_mode: 'Markdown' });
        } else {
            bot.sendMessage(chatId, '❌ IP no válida o no encontrada');
        }
    } catch (error) {
        bot.sendMessage(chatId, '❌ Error al consultar la IP');
    }
});

// Análisis de dominio (versión simple)
bot.onText(/\/domain (.+)/, async (msg, match) => {
    const chatId = msg.chat.id;
    const domain = match[1].replace(/^https?:\/\//, '').split('/')[0];
    
    bot.sendMessage(chatId, `🌐 Analizando dominio: ${domain}...`);
    
    try {
        const dns = require('dns').promises;
        const ips = await dns.resolve4(domain);
        
        const info = `
🌐 *Dominio:* ${domain}
📡 *IPs:* ${ips.join(', ')}
🔗 *URL:* https://${domain}
💡 *Tip:* Usa /whois para más información
        `;
        bot.sendMessage(chatId, info, { parse_mode: 'Markdown' });
    } catch (error) {
        bot.sendMessage(chatId, '❌ Dominio no encontrado o error en resolución DNS');
    }
});

// Búsqueda de usuario
bot.onText(/\/user (.+)/, async (msg, match) => {
    const chatId = msg.chat.id;
    const username = match[1];
    
    const results = `
👤 *Usuario:* @${username}

*Plataformas verificadas:*
🔗 GitHub: https://github.com/${username}
🐦 Twitter: https://twitter.com/${username}
📸 Instagram: https://instagram.com/${username}
💼 LinkedIn: https://linkedin.com/in/${username}
📱 Telegram: https://t.me/${username}

💡 *Nota:* Estos son enlaces comunes, no garantizan existencia.
    `;
    
    bot.sendMessage(chatId, results, { parse_mode: 'Markdown' });
});

// Comando de estado
bot.onText(/\/status/, (msg) => {
    const chatId = msg.chat.id;
    const uptime = Math.floor(process.uptime());
    
    const status = `
🤖 *Estado del Bot:*
✅ En línea
⏱️ Uptime: ${uptime} segundos
💾 RAM: ${(process.memoryUsage().heapUsed / 1024 / 1024).toFixed(2)} MB
🕐 Hora: ${new Date().toLocaleString()}
    `;
    
    bot.sendMessage(chatId, status, { parse_mode: 'Markdown' });
});

// Manejar imágenes para EXIF
bot.on('photo', async (msg) => {
    const chatId = msg.chat.id;
    bot.sendMessage(chatId, '📸 *Función EXIF desactivada temporalmente*\n\nPara análisis EXIF completo, necesita configuración adicional.', { parse_mode: 'Markdown' });
});

// Manejar errores
bot.on('polling_error', (error) => {
    console.error('❌ Error del bot:', error);
});

// Log de mensajes
bot.on('message', (msg) => {
    console.log(`📨 ${msg.from.username || msg.from.first_name}: ${msg.text || '(media)'}`);
});
