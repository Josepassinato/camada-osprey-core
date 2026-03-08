"""
Rate limiting via slowapi for critical endpoints.
Per-IP limits + per-office daily message limits for chat.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
