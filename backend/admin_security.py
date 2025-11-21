"""
Admin Security Module
Implementa autenticação e autorização para endpoints administrativos
"""

from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
from datetime import datetime
import jwt
import os
from motor.motor_asyncio import AsyncIOMotorClient

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'osprey-secret-key-change-in-production')
JWT_ALGORITHM = "HS256"

security = HTTPBearer()

# MongoDB client - será inicializado no startup
db = None

def init_db(database):
    """Inicializa a referência ao banco de dados"""
    global db
    db = database


# ============================================================================
# RBAC (Role-Based Access Control)
# ============================================================================

class UserRole:
    """Roles disponíveis no sistema"""
    USER = "user"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Obtém o usuário atual a partir do token JWT.
    Lança HTTPException se o token for inválido.
    """
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def require_admin(current_user: Dict = Depends(get_current_user)):
    """
    Dependency que verifica se o usuário atual é admin ou superadmin.
    
    Uso:
        @api_router.get("/admin/endpoint")
        async def admin_endpoint(admin = Depends(require_admin)):
            # Apenas admins podem acessar
            ...
    
    Raises:
        HTTPException 403: Se o usuário não for admin
    """
    user_role = current_user.get('role', 'user')
    
    if user_role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(
            status_code=403,
            detail="Admin access required. Your role: " + user_role
        )
    
    return current_user


async def require_superadmin(current_user: Dict = Depends(get_current_user)):
    """
    Dependency que verifica se o usuário atual é superadmin.
    Para operações críticas que requerem permissões elevadas.
    
    Raises:
        HTTPException 403: Se o usuário não for superadmin
    """
    user_role = current_user.get('role', 'user')
    
    if user_role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=403,
            detail="Superadmin access required. Your role: " + user_role
        )
    
    return current_user


# ============================================================================
# AUDIT LOGGING
# ============================================================================

class AuditAction:
    """Tipos de ações administrativas para audit log"""
    # Visa Updates
    APPROVE_VISA_UPDATE = "approve_visa_update"
    REJECT_VISA_UPDATE = "reject_visa_update"
    RUN_MANUAL_SCAN = "run_manual_scan"
    
    # Knowledge Base
    UPLOAD_DOCUMENT = "upload_document"
    DELETE_DOCUMENT = "delete_document"
    DOWNLOAD_DOCUMENT = "download_document"
    
    # User Management
    CREATE_USER = "create_user"
    DELETE_USER = "delete_user"
    UPDATE_USER_ROLE = "update_user_role"
    
    # System
    SYSTEM_CONFIG_CHANGE = "system_config_change"
    VIEW_SENSITIVE_DATA = "view_sensitive_data"


async def log_admin_action(
    admin_user: Dict[str, Any],
    action: str,
    resource_type: str,
    resource_id: str,
    details: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None,
    success: bool = True
):
    """
    Registra uma ação administrativa no audit log.
    
    Args:
        admin_user: Usuário admin que executou a ação
        action: Tipo de ação (usar AuditAction constants)
        resource_type: Tipo do recurso afetado ("visa_update", "document", etc.)
        resource_id: ID do recurso afetado
        details: Detalhes adicionais sobre a ação
        request: Request object (para capturar IP, user-agent)
        success: Se a ação foi bem-sucedida
    
    Example:
        await log_admin_action(
            admin_user=admin,
            action=AuditAction.APPROVE_VISA_UPDATE,
            resource_type="visa_update",
            resource_id=update_id,
            details={"form_code": "I-539", "update_type": "processing_time"},
            request=request,
            success=True
        )
    """
    try:
        # Capturar IP e user-agent do request
        ip_address = None
        user_agent = None
        
        if request:
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")
        
        # Criar log entry
        log_entry = {
            "log_id": f"audit_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{admin_user.get('id')[:8]}",
            "admin_id": admin_user.get('id'),
            "admin_email": admin_user.get('email'),
            "admin_name": f"{admin_user.get('first_name', '')} {admin_user.get('last_name', '')}".strip(),
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details or {},
            "success": success,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "timestamp": datetime.utcnow(),
            "created_at": datetime.utcnow()
        }
        
        # Inserir no MongoDB
        await db.admin_audit_log.insert_one(log_entry)
        
        # Log também no console para monitoramento
        status = "✅" if success else "❌"
        print(f"{status} AUDIT: {admin_user.get('email')} - {action} - {resource_type}:{resource_id}")
        
    except Exception as e:
        # Não falhar a operação principal se o log falhar
        print(f"⚠️ Failed to log admin action: {e}")


async def get_admin_audit_log(
    limit: int = 100,
    admin_id: Optional[str] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """
    Busca logs de auditoria com filtros.
    
    Args:
        limit: Número máximo de registros
        admin_id: Filtrar por admin específico
        action: Filtrar por tipo de ação
        resource_type: Filtrar por tipo de recurso
        start_date: Data inicial
        end_date: Data final
    
    Returns:
        Lista de log entries
    """
    query = {}
    
    if admin_id:
        query["admin_id"] = admin_id
    
    if action:
        query["action"] = action
    
    if resource_type:
        query["resource_type"] = resource_type
    
    if start_date or end_date:
        query["timestamp"] = {}
        if start_date:
            query["timestamp"]["$gte"] = start_date
        if end_date:
            query["timestamp"]["$lte"] = end_date
    
    cursor = db.admin_audit_log.find(query).sort("timestamp", -1).limit(limit)
    logs = await cursor.to_list(length=limit)
    
    return logs


# ============================================================================
# RATE LIMITING
# ============================================================================

class RateLimiter:
    """
    Simple in-memory rate limiter para endpoints admin.
    Em produção, considerar usar Redis.
    """
    
    def __init__(self):
        self._requests = {}  # {key: [(timestamp, count)]}
    
    async def check_rate_limit(
        self,
        key: str,
        max_requests: int = 100,
        window_seconds: int = 3600
    ) -> bool:
        """
        Verifica se o rate limit foi excedido.
        
        Args:
            key: Identificador único (user_id, IP, etc.)
            max_requests: Número máximo de requests
            window_seconds: Janela de tempo em segundos
        
        Returns:
            True se dentro do limite, False se excedido
        """
        now = datetime.utcnow()
        window_start = now.timestamp() - window_seconds
        
        # Limpar requests antigas
        if key in self._requests:
            self._requests[key] = [
                (ts, count) for ts, count in self._requests[key]
                if ts > window_start
            ]
        else:
            self._requests[key] = []
        
        # Contar requests na janela
        total_requests = sum(count for _, count in self._requests[key])
        
        if total_requests >= max_requests:
            return False
        
        # Adicionar nova request
        self._requests[key].append((now.timestamp(), 1))
        return True


# Instância global do rate limiter
rate_limiter = RateLimiter()


async def check_admin_rate_limit(
    admin_user: Dict = Depends(require_admin),
    max_requests: int = 100
):
    """
    Dependency para rate limiting de endpoints admin.
    
    Uso:
        @api_router.post("/admin/sensitive-endpoint")
        async def endpoint(admin = Depends(check_admin_rate_limit)):
            ...
    
    Raises:
        HTTPException 429: Se rate limit foi excedido
    """
    key = f"admin_{admin_user.get('id')}"
    
    if not await rate_limiter.check_rate_limit(key, max_requests=max_requests):
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Max {max_requests} requests per hour."
        )
    
    return admin_user
