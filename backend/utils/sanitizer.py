"""
Input Sanitization and Validation
Protege contra XSS, SQL Injection, e outras vulnerabilidades
"""

import re
import html
import json
from typing import Any, Dict, List, Union
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger(__name__)


class InputSanitizer:
    """Sanitiza e valida inputs de usuários"""
    
    # Padrões perigosos
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # Scripts
        r'javascript:',                 # JavaScript protocol
        r'on\w+\s*=',                  # Event handlers (onclick, onerror, etc)
        r'<iframe[^>]*>',              # Iframes
        r'<object[^>]*>',              # Objects
        r'<embed[^>]*>',               # Embeds
    ]
    
    # Padrões SQL injection
    SQL_INJECTION_PATTERNS = [
        r"('|(\\')|(;)|(--)|(\/\*)|(xp_))",  # Common SQL injection patterns
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
    ]
    
    @staticmethod
    def sanitize_string(value: str, allow_html: bool = False) -> str:
        """
        Sanitiza uma string
        
        Args:
            value: String para sanitizar
            allow_html: Se True, permite HTML seguro (escapado)
        
        Returns:
            String sanitizada
        """
        if not isinstance(value, str):
            return value
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Trim whitespace
        value = value.strip()
        
        # Check for dangerous patterns
        for pattern in InputSanitizer.DANGEROUS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"Dangerous pattern detected: {pattern}")
                value = re.sub(pattern, '', value, flags=re.IGNORECASE)
        
        # Escape HTML if not allowed
        if not allow_html:
            value = html.escape(value)
        
        return value
    
    @staticmethod
    def sanitize_dict(data: Dict[str, Any], allow_html: bool = False) -> Dict[str, Any]:
        """
        Sanitiza todos os valores de um dicionário
        
        Args:
            data: Dicionário para sanitizar
            allow_html: Se True, permite HTML seguro
        
        Returns:
            Dicionário sanitizado
        """
        sanitized = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = InputSanitizer.sanitize_string(value, allow_html)
            elif isinstance(value, dict):
                sanitized[key] = InputSanitizer.sanitize_dict(value, allow_html)
            elif isinstance(value, list):
                sanitized[key] = InputSanitizer.sanitize_list(value, allow_html)
            else:
                sanitized[key] = value
        
        return sanitized
    
    @staticmethod
    def sanitize_list(data: List[Any], allow_html: bool = False) -> List[Any]:
        """
        Sanitiza todos os valores de uma lista
        
        Args:
            data: Lista para sanitizar
            allow_html: Se True, permite HTML seguro
        
        Returns:
            Lista sanitizada
        """
        sanitized = []
        
        for item in data:
            if isinstance(item, str):
                sanitized.append(InputSanitizer.sanitize_string(item, allow_html))
            elif isinstance(item, dict):
                sanitized.append(InputSanitizer.sanitize_dict(item, allow_html))
            elif isinstance(item, list):
                sanitized.append(InputSanitizer.sanitize_list(item, allow_html))
            else:
                sanitized.append(item)
        
        return sanitized
    
    @staticmethod
    def check_sql_injection(value: str) -> bool:
        """
        Verifica se string contém padrões de SQL injection
        
        Args:
            value: String para verificar
        
        Returns:
            True se suspeito, False se seguro
        """
        if not isinstance(value, str):
            return False
        
        for pattern in InputSanitizer.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"SQL injection pattern detected: {value}")
                return True
        
        return False
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Valida formato de email
        
        Args:
            email: Email para validar
        
        Returns:
            True se válido, False se inválido
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """
        Valida formato de telefone (internacional)
        
        Args:
            phone: Telefone para validar
        
        Returns:
            True se válido, False se inválido
        """
        # Remove non-digits
        digits_only = re.sub(r'\D', '', phone)
        
        # Check length (10-15 digits for international)
        return 10 <= len(digits_only) <= 15
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitiza nome de arquivo
        
        Args:
            filename: Nome do arquivo
        
        Returns:
            Nome sanitizado
        """
        # Remove path traversal
        filename = filename.replace('../', '').replace('..\\', '')
        
        # Remove null bytes
        filename = filename.replace('\x00', '')
        
        # Keep only alphanumeric, dash, underscore, dot
        filename = re.sub(r'[^\w\s.-]', '', filename)
        
        # Limit length
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:250] + '.' + ext if ext else name[:255]
        
        return filename
    
    @staticmethod
    def sanitize_url(url: str) -> str:
        """
        Sanitiza URL
        
        Args:
            url: URL para sanitizar
        
        Returns:
            URL sanitizada
        """
        # Remove javascript: protocol
        url = re.sub(r'javascript:', '', url, flags=re.IGNORECASE)
        
        # Remove data: protocol (can contain scripts)
        url = re.sub(r'data:', '', url, flags=re.IGNORECASE)
        
        # Ensure http or https
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        return url


# Helper function for FastAPI
def sanitize_request_body(body: Union[Dict, List, str]) -> Union[Dict, List, str]:
    """
    Sanitiza request body completo
    
    Usage in FastAPI:
        body_sanitized = sanitize_request_body(body)
    """
    if isinstance(body, dict):
        return InputSanitizer.sanitize_dict(body)
    elif isinstance(body, list):
        return InputSanitizer.sanitize_list(body)
    elif isinstance(body, str):
        return InputSanitizer.sanitize_string(body)
    else:
        return body


class InputSanitizerMiddleware(BaseHTTPMiddleware):
    """
    Sanitizes JSON request bodies to reduce XSS/SQLi risks.
    Non-JSON payloads are passed through untouched.
    """
    async def dispatch(self, request: Request, call_next):
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type.lower():
            raw_body = await request.body()
            if raw_body:
                try:
                    data = json.loads(raw_body)
                    sanitized = sanitize_request_body(data)
                    sanitized_bytes = json.dumps(sanitized).encode("utf-8")

                    async def receive():
                        return {
                            "type": "http.request",
                            "body": sanitized_bytes,
                            "more_body": False,
                        }

                    request = Request(request.scope, receive)
                except json.JSONDecodeError:
                    pass

        return await call_next(request)
