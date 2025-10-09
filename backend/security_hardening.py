"""
Security Hardening System - Phase 4B
Sistema de segurança avançada e proteção de APIs
"""

import time
import hashlib
import hmac
import secrets
import logging
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from collections import defaultdict, deque
import ipaddress
import re
import asyncio
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

@dataclass
class SecurityEvent:
    """Evento de segurança detectado"""
    event_type: str
    ip_address: str
    user_agent: str
    endpoint: str
    timestamp: datetime
    severity: str  # low, medium, high, critical
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RateLimitRule:
    """Regra de rate limiting"""
    name: str
    endpoint_pattern: str
    requests_per_minute: int
    requests_per_hour: int
    burst_limit: int
    block_duration_minutes: int = 15

class SecurityHardeningSystem:
    """
    Sistema avançado de segurança e proteção
    """
    
    def __init__(self):
        # Rate limiting tracking
        self.request_counts: Dict[str, deque] = defaultdict(lambda: deque())
        self.blocked_ips: Dict[str, datetime] = {}
        self.suspicious_ips: Set[str] = set()
        
        # Security events
        self.security_events: List[SecurityEvent] = []
        
        # Rate limiting rules
        self.rate_limit_rules = {
            # Endpoints críticos de análise
            "document_analysis": RateLimitRule(
                name="Document Analysis",
                endpoint_pattern=r"/api/documents/analyze.*",
                requests_per_minute=10,
                requests_per_hour=100,
                burst_limit=3,
                block_duration_minutes=30
            ),
            
            # Endpoints de autenticação
            "auth_endpoints": RateLimitRule(
                name="Authentication",
                endpoint_pattern=r"/api/auth/(login|signup|reset).*",
                requests_per_minute=5,
                requests_per_hour=20,
                burst_limit=3,
                block_duration_minutes=60
            ),
            
            # Workflow automation (podem ser intensivos)
            "workflow_automation": RateLimitRule(
                name="Workflow Automation",
                endpoint_pattern=r"/api/automation/workflows.*",
                requests_per_minute=20,
                requests_per_hour=200,
                burst_limit=5,
                block_duration_minutes=15
            ),
            
            # Notifications (burst permitido)
            "notifications": RateLimitRule(
                name="Notifications",
                endpoint_pattern=r"/api/automation/notifications.*",
                requests_per_minute=30,
                requests_per_hour=300,
                burst_limit=10,
                block_duration_minutes=10
            ),
            
            # Analytics (leitura frequente)
            "analytics_read": RateLimitRule(
                name="Analytics Read",
                endpoint_pattern=r"/api/(analytics|metrics).*",
                requests_per_minute=60,
                requests_per_hour=600,
                burst_limit=20,
                block_duration_minutes=5
            ),
            
            # Default para outros endpoints
            "default": RateLimitRule(
                name="Default API",
                endpoint_pattern=r"/api/.*",
                requests_per_minute=30,
                requests_per_hour=300,
                burst_limit=10,
                block_duration_minutes=15
            )
        }
        
        # Trusted IP ranges (can be configured)
        self.trusted_ip_ranges = [
            ipaddress.ip_network('127.0.0.0/8'),  # Localhost
            ipaddress.ip_network('10.0.0.0/8'),   # Private network
            ipaddress.ip_network('172.16.0.0/12'), # Private network
            ipaddress.ip_network('192.168.0.0/16') # Private network
        ]
        
        # Suspicious patterns
        self.suspicious_patterns = {
            # SQL injection attempts
            "sql_injection": [
                r"(?i)(union|select|insert|update|delete|drop|exec|script)",
                r"(?i)(\-\-|\#|\/\*|\*\/)",
                r"(?i)(or\s+1\s*=\s*1|and\s+1\s*=\s*1)"
            ],
            
            # XSS attempts
            "xss": [
                r"(?i)(<script|javascript:|onload=|onerror=)",
                r"(?i)(alert\(|confirm\(|prompt\()",
                r"(?i)(<iframe|<object|<embed)"
            ],
            
            # Path traversal
            "path_traversal": [
                r"(\.\.\/|\.\.\\)",
                r"(?i)(\/etc\/passwd|\/proc\/|\/sys\/)",
                r"(?i)(boot\.ini|win\.ini)"
            ],
            
            # Command injection
            "command_injection": [
                r"(?i)(;|\||\&|\$\(|\`)",
                r"(?i)(bash|sh|cmd|powershell)",
                r"(?i)(wget|curl|nc|netcat)"
            ]
        }
        
        # Start cleanup task
        asyncio.create_task(self._cleanup_old_data())
    
    def get_client_ip(self, request: Request) -> str:
        """
        Extrai IP real do cliente considerando proxies
        """
        # Check X-Forwarded-For header (common in load balancers)
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        # Check X-Real-IP header
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip
        
        # Fallback to direct connection
        return request.client.host if request.client else "unknown"
    
    def is_trusted_ip(self, ip_address: str) -> bool:
        """
        Verifica se IP está em range confiável
        """
        try:
            ip = ipaddress.ip_address(ip_address)
            return any(ip in network for network in self.trusted_ip_ranges)
        except ValueError:
            return False
    
    def check_rate_limit(self, request: Request) -> Optional[HTTPException]:
        """
        Verifica rate limits para request
        """
        ip_address = self.get_client_ip(request)
        endpoint = str(request.url.path)
        current_time = datetime.now(timezone.utc)
        
        # Check if IP is blocked
        if ip_address in self.blocked_ips:
            block_until = self.blocked_ips[ip_address]
            if current_time < block_until:
                self._log_security_event(
                    "rate_limit_blocked",
                    ip_address,
                    request.headers.get('User-Agent', ''),
                    endpoint,
                    "high",
                    {"block_until": block_until.isoformat()}
                )
                return HTTPException(
                    status_code=429,
                    detail=f"IP blocked due to rate limiting until {block_until.isoformat()}"
                )
            else:
                # Unblock expired IPs
                del self.blocked_ips[ip_address]
        
        # Skip rate limiting for trusted IPs
        if self.is_trusted_ip(ip_address):
            return None
        
        # Find matching rule
        matching_rule = None
        for rule in self.rate_limit_rules.values():
            if re.match(rule.endpoint_pattern, endpoint):
                matching_rule = rule
                break
        
        if not matching_rule:
            matching_rule = self.rate_limit_rules["default"]
        
        # Track request
        request_key = f"{ip_address}:{matching_rule.name}"
        request_times = self.request_counts[request_key]
        
        # Add current request
        request_times.append(current_time)
        
        # Clean old requests (older than 1 hour)
        cutoff_time = current_time - timedelta(hours=1)
        while request_times and request_times[0] < cutoff_time:
            request_times.popleft()
        
        # Count recent requests
        minute_cutoff = current_time - timedelta(minutes=1)
        requests_last_minute = len([t for t in request_times if t > minute_cutoff])
        requests_last_hour = len(request_times)
        
        # Check burst limit (last 10 seconds)
        burst_cutoff = current_time - timedelta(seconds=10)
        requests_last_burst = len([t for t in request_times if t > burst_cutoff])
        
        # Evaluate limits
        if requests_last_burst > matching_rule.burst_limit:
            # Block IP
            block_until = current_time + timedelta(minutes=matching_rule.block_duration_minutes)
            self.blocked_ips[ip_address] = block_until
            
            self._log_security_event(
                "rate_limit_burst_exceeded",
                ip_address,
                request.headers.get('User-Agent', ''),
                endpoint,
                "high",
                {
                    "requests_in_burst": requests_last_burst,
                    "burst_limit": matching_rule.burst_limit,
                    "rule": matching_rule.name
                }
            )
            
            return HTTPException(
                status_code=429,
                detail=f"Burst limit exceeded. IP blocked until {block_until.isoformat()}"
            )
        
        elif requests_last_minute > matching_rule.requests_per_minute:
            self._log_security_event(
                "rate_limit_minute_exceeded",
                ip_address,
                request.headers.get('User-Agent', ''),
                endpoint,
                "medium",
                {
                    "requests_per_minute": requests_last_minute,
                    "limit": matching_rule.requests_per_minute,
                    "rule": matching_rule.name
                }
            )
            
            return HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded: {requests_last_minute}/{matching_rule.requests_per_minute} requests per minute"
            )
        
        elif requests_last_hour > matching_rule.requests_per_hour:
            self._log_security_event(
                "rate_limit_hour_exceeded",
                ip_address,
                request.headers.get('User-Agent', ''),
                endpoint,
                "medium",
                {
                    "requests_per_hour": requests_last_hour,
                    "limit": matching_rule.requests_per_hour,
                    "rule": matching_rule.name
                }
            )
            
            return HTTPException(
                status_code=429,
                detail=f"Hourly rate limit exceeded: {requests_last_hour}/{matching_rule.requests_per_hour} requests per hour"
            )
        
        return None
    
    def scan_for_malicious_content(self, request: Request) -> List[str]:
        """
        Escaneia request por conteúdo malicioso
        """
        threats_found = []
        
        # Scan URL path
        url_path = str(request.url.path)
        query_params = str(request.url.query) if request.url.query else ""
        
        # Scan headers
        headers_text = " ".join([f"{k}:{v}" for k, v in request.headers.items()])
        
        # Combine all text to scan
        text_to_scan = f"{url_path} {query_params} {headers_text}".lower()
        
        # Check against patterns
        for threat_type, patterns in self.suspicious_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_to_scan):
                    threats_found.append(threat_type)
                    break  # Don't duplicate threat types
        
        return threats_found
    
    def validate_request_size(self, request: Request) -> Optional[HTTPException]:
        """
        Valida tamanho do request
        """
        # Check Content-Length header
        content_length = request.headers.get('content-length')
        if content_length:
            try:
                size_bytes = int(content_length)
                max_size = 50 * 1024 * 1024  # 50MB limit
                
                if size_bytes > max_size:
                    self._log_security_event(
                        "request_size_exceeded",
                        self.get_client_ip(request),
                        request.headers.get('User-Agent', ''),
                        str(request.url.path),
                        "medium",
                        {"content_length": size_bytes, "max_size": max_size}
                    )
                    
                    return HTTPException(
                        status_code=413,
                        detail=f"Request too large: {size_bytes} bytes (max: {max_size})"
                    )
            except ValueError:
                pass
        
        return None
    
    def generate_csrf_token(self, session_id: str) -> str:
        """
        Gera token CSRF para sessão
        """
        secret = secrets.token_bytes(32)
        message = f"{session_id}:{int(time.time())}"
        token = hmac.new(secret, message.encode(), hashlib.sha256).hexdigest()
        return f"{token}:{message}"
    
    def validate_csrf_token(self, token: str, session_id: str, max_age_seconds: int = 3600) -> bool:
        """
        Valida token CSRF
        """
        try:
            if ':' not in token:
                return False
            
            token_parts = token.split(':', 2)
            if len(token_parts) != 3:
                return False
            
            provided_token, provided_session, provided_timestamp = token_parts
            
            # Check session match
            if provided_session != session_id:
                return False
            
            # Check timestamp
            timestamp = int(provided_timestamp)
            if time.time() - timestamp > max_age_seconds:
                return False
            
            return True
            
        except (ValueError, TypeError):
            return False
    
    def _log_security_event(self, event_type: str, ip_address: str, user_agent: str, endpoint: str, severity: str, details: Dict[str, Any] = None):
        """
        Registra evento de segurança
        """
        event = SecurityEvent(
            event_type=event_type,
            ip_address=ip_address,
            user_agent=user_agent,
            endpoint=endpoint,
            timestamp=datetime.now(timezone.utc),
            severity=severity,
            details=details or {}
        )
        
        self.security_events.append(event)
        
        # Log based on severity
        if severity == "critical":
            logger.error(f"🚨 CRITICAL SECURITY EVENT: {event_type} from {ip_address} on {endpoint}")
        elif severity == "high":
            logger.warning(f"⚠️ HIGH SECURITY EVENT: {event_type} from {ip_address} on {endpoint}")
        elif severity == "medium":
            logger.info(f"🔍 MEDIUM SECURITY EVENT: {event_type} from {ip_address} on {endpoint}")
        
        # Keep only recent events (last 24 hours)
        cutoff = datetime.now(timezone.utc) - timedelta(days=1)
        self.security_events = [e for e in self.security_events if e.timestamp > cutoff]
    
    async def _cleanup_old_data(self):
        """
        Limpa dados antigos periodicamente
        """
        while True:
            try:
                current_time = datetime.now(timezone.utc)
                
                # Clean expired IP blocks
                expired_blocks = [
                    ip for ip, block_until in self.blocked_ips.items()
                    if current_time > block_until
                ]
                for ip in expired_blocks:
                    del self.blocked_ips[ip]
                
                # Clean old request counts
                cutoff_time = current_time - timedelta(hours=2)
                for request_key in list(self.request_counts.keys()):
                    request_times = self.request_counts[request_key]
                    while request_times and request_times[0] < cutoff_time:
                        request_times.popleft()
                    
                    # Remove empty entries
                    if not request_times:
                        del self.request_counts[request_key]
                
                # Clean old security events
                cutoff_events = current_time - timedelta(days=7)
                self.security_events = [e for e in self.security_events if e.timestamp > cutoff_events]
                
                logger.debug("🧹 Security system cleanup completed")
                
            except Exception as e:
                logger.error(f"Error in security cleanup: {e}")
            
            # Sleep for 1 hour
            await asyncio.sleep(3600)
    
    # ===========================================
    # PUBLIC METHODS
    # ===========================================
    
    def get_security_statistics(self) -> Dict[str, Any]:
        """
        Obtém estatísticas de segurança
        """
        current_time = datetime.now(timezone.utc)
        
        # Count events by type and severity
        event_counts = defaultdict(int)
        severity_counts = defaultdict(int)
        
        for event in self.security_events:
            event_counts[event.event_type] += 1
            severity_counts[event.severity] += 1
        
        # Count recent events (last hour)
        hour_ago = current_time - timedelta(hours=1)
        recent_events = len([e for e in self.security_events if e.timestamp > hour_ago])
        
        return {
            "blocked_ips": len(self.blocked_ips),
            "suspicious_ips": len(self.suspicious_ips),
            "total_security_events": len(self.security_events),
            "recent_events_last_hour": recent_events,
            "events_by_type": dict(event_counts),
            "events_by_severity": dict(severity_counts),
            "rate_limit_rules": len(self.rate_limit_rules),
            "active_request_tracking": len(self.request_counts),
            "timestamp": current_time.isoformat()
        }
    
    def get_recent_security_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Obtém eventos de segurança recentes
        """
        recent_events = sorted(self.security_events, key=lambda x: x.timestamp, reverse=True)[:limit]
        
        return [
            {
                "event_type": event.event_type,
                "ip_address": event.ip_address,
                "user_agent": event.user_agent[:100] + "..." if len(event.user_agent) > 100 else event.user_agent,
                "endpoint": event.endpoint,
                "severity": event.severity,
                "timestamp": event.timestamp.isoformat(),
                "details": event.details
            }
            for event in recent_events
        ]
    
    def manually_block_ip(self, ip_address: str, duration_minutes: int = 60, reason: str = "Manual block"):
        """
        Bloqueia IP manualmente
        """
        block_until = datetime.now(timezone.utc) + timedelta(minutes=duration_minutes)
        self.blocked_ips[ip_address] = block_until
        
        self._log_security_event(
            "manual_ip_block",
            ip_address,
            "admin",
            "manual",
            "high",
            {"reason": reason, "duration_minutes": duration_minutes}
        )
        
        logger.warning(f"🚫 IP {ip_address} manually blocked until {block_until.isoformat()}: {reason}")
    
    def unblock_ip(self, ip_address: str, reason: str = "Manual unblock"):
        """
        Desbloqueia IP manualmente
        """
        if ip_address in self.blocked_ips:
            del self.blocked_ips[ip_address]
            
            self._log_security_event(
                "manual_ip_unblock",
                ip_address,
                "admin",
                "manual",
                "medium",
                {"reason": reason}
            )
            
            logger.info(f"✅ IP {ip_address} manually unblocked: {reason}")
            return True
        return False

class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Middleware de segurança para FastAPI
    """
    
    def __init__(self, app, security_system: SecurityHardeningSystem):
        super().__init__(app)
        self.security_system = security_system
    
    async def dispatch(self, request: Request, call_next):
        """
        Processa request através das verificações de segurança
        """
        # Skip security checks for health checks and static files
        if request.url.path in ["/health", "/", "/favicon.ico"] or request.url.path.startswith("/static"):
            return await call_next(request)
        
        # Check rate limits
        rate_limit_error = self.security_system.check_rate_limit(request)
        if rate_limit_error:
            raise rate_limit_error
        
        # Check request size
        size_error = self.security_system.validate_request_size(request)
        if size_error:
            raise size_error
        
        # Scan for malicious content
        threats = self.security_system.scan_for_malicious_content(request)
        if threats:
            ip_address = self.security_system.get_client_ip(request)
            self.security_system._log_security_event(
                "malicious_content_detected",
                ip_address,
                request.headers.get('User-Agent', ''),
                str(request.url.path),
                "high",
                {"threats": threats}
            )
            
            # Block IP for critical threats
            if any(threat in ["sql_injection", "command_injection"] for threat in threats):
                self.security_system.manually_block_ip(ip_address, 120, f"Malicious content: {', '.join(threats)}")
            
            raise HTTPException(
                status_code=400,
                detail=f"Malicious content detected: {', '.join(threats)}"
            )
        
        # Add security headers
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        
        return response

# Instância global
security_system = SecurityHardeningSystem()