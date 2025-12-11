import re
import ipaddress
from urllib.parse import urlparse
import socket

def validate_ip(ip_str):
    """Validar dirección IP"""
    try:
        ipaddress.ip_address(ip_str)
        return True
    except ValueError:
        return False

def validate_domain(domain):
    """Validar dominio"""
    pattern = r'^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, domain))

def validate_email(email):
    """Validar email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone):
    """Validar número de teléfono"""
    # Patrón básico internacional
    pattern = r'^\+?[1-9]\d{1,14}$'
    return bool(re.match(pattern, phone))

def extract_emails_from_text(text):
    """Extraer emails de un texto"""
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.findall(pattern, text)

def extract_urls_from_text(text):
    """Extraer URLs de un texto"""
    pattern = r'https?://[^\s]+'
    return re.findall(pattern, text)

def extract_ips_from_text(text):
    """Extraer IPs de un texto"""
    pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
    ips = re.findall(pattern, text)
    return [ip for ip in ips if validate_ip(ip)]

def get_domain_from_url(url):
    """Extraer dominio de una URL"""
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except:
        return None

def is_valid_url(url):
    """Validar URL"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False
