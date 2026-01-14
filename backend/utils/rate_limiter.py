"""
Simple Rate Limiter for FastAPI
Protege APIs contra abuso e ataques DDoS
"""

import asyncio
import logging
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Dict

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    In-memory rate limiter
    Para produção enterprise, usar Redis
    """

    def __init__(self):
        # Estrutura: {ip_address: [(timestamp, count), ...]}
        self.requests: Dict[str, list] = defaultdict(list)
        self.lock = asyncio.Lock()

        # Rate limits por tipo de endpoint
        self.limits = {
            "default": (100, 60),  # 100 requests per minute
            "auth": (10, 60),  # 10 auth attempts per minute
            "payment": (5, 60),  # 5 payment attempts per minute
            "upload": (20, 60),  # 20 uploads per minute
            "api": (200, 60),  # 200 API calls per minute
        }

    async def check_rate_limit(self, request: Request, limit_type: str = "default") -> bool:
        """
        Verifica se o request está dentro do rate limit

        Args:
            request: FastAPI Request object
            limit_type: Tipo de limite (default, auth, payment, etc)

        Returns:
            True se permitido, False se bloqueado

        Raises:
            HTTPException: 429 se exceder rate limit
        """
        # Get client IP
        client_ip = self._get_client_ip(request)

        # Get limit config
        max_requests, window_seconds = self.limits.get(limit_type, self.limits["default"])

        async with self.lock:
            # Clean old requests
            now = datetime.now(timezone.utc)
            cutoff = now - timedelta(seconds=window_seconds)

            # Remove requests older than window
            self.requests[client_ip] = [ts for ts in self.requests[client_ip] if ts > cutoff]

            # Count requests in window
            request_count = len(self.requests[client_ip])

            # Check if over limit
            if request_count >= max_requests:
                logger.warning(
                    f"Rate limit exceeded",
                    extra={
                        "client_ip": client_ip,
                        "limit_type": limit_type,
                        "request_count": request_count,
                        "max_requests": max_requests,
                    },
                )

                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "Rate limit exceeded",
                        "retry_after": window_seconds,
                        "limit": f"{max_requests} requests per {window_seconds} seconds",
                    },
                    headers={"Retry-After": str(window_seconds)},
                )

            # Add current request
            self.requests[client_ip].append(now)

            return True

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        # Check for forwarded header (behind load balancer)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        # Check for real IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fallback to direct client
        return request.client.host if request.client else "unknown"

    async def cleanup_old_entries(self):
        """
        Background task to cleanup old entries
        Run periodically to prevent memory growth
        """
        while True:
            try:
                await asyncio.sleep(300)  # Every 5 minutes

                async with self.lock:
                    now = datetime.now(timezone.utc)
                    cutoff = now - timedelta(seconds=3600)  # Keep last hour

                    # Clean each IP's request list
                    for ip in list(self.requests.keys()):
                        self.requests[ip] = [ts for ts in self.requests[ip] if ts > cutoff]

                        # Remove empty entries
                        if not self.requests[ip]:
                            del self.requests[ip]

                    logger.info(f"Rate limiter cleanup: {len(self.requests)} active IPs")

            except Exception as e:
                logger.error(f"Error in rate limiter cleanup: {str(e)}")


# Middleware for FastAPI
class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Global rate limiter middleware.
    For route-specific limits, keep using the dependency version.
    """

    def __init__(self, app, limit_type: str = "default"):
        super().__init__(app)
        self.limit_type = limit_type

    async def dispatch(self, request: Request, call_next):
        await rate_limiter.check_rate_limit(request, self.limit_type)
        return await call_next(request)


# Global rate limiter instance
rate_limiter = RateLimiter()


# Dependency for FastAPI endpoints
async def check_rate_limit(request: Request, limit_type: str = "default"):
    """
    FastAPI dependency para rate limiting

    Usage:
        @app.get("/api/endpoint", dependencies=[Depends(check_rate_limit)])
        async def my_endpoint():
            ...
    """
    await rate_limiter.check_rate_limit(request, limit_type)
    return True
