"""
Automatic Retry System - Phase 4D
Sistema de retry automático para operações que podem falhar temporariamente
"""

import asyncio
import logging
from typing import Callable, Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
import functools
import traceback

logger = logging.getLogger(__name__)

class RetryStrategy(Enum):
    """Estratégias de retry disponíveis"""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    FIXED_DELAY = "fixed_delay"
    LINEAR_BACKOFF = "linear_backoff"
    IMMEDIATE = "immediate"

@dataclass
class RetryConfig:
    """Configuração de retry para diferentes operações"""
    max_attempts: int = 3
    base_delay: float = 1.0  # seconds
    max_delay: float = 60.0  # seconds
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    backoff_multiplier: float = 2.0
    retry_on_exceptions: List[type] = field(default_factory=lambda: [Exception])
    stop_on_exceptions: List[type] = field(default_factory=list)
    operation_timeout: Optional[float] = None

@dataclass
class RetryAttempt:
    """Informações de uma tentativa de retry"""
    attempt_number: int
    timestamp: datetime
    exception: Optional[Exception] = None
    success: bool = False
    duration: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass  
class RetryResult:
    """Resultado final de uma operação com retry"""
    success: bool
    result: Any = None
    total_attempts: int = 0
    total_duration: float = 0.0
    attempts: List[RetryAttempt] = field(default_factory=list)
    final_exception: Optional[Exception] = None

class RetrySystem:
    """
    Sistema de retry automático inteligente
    """
    
    def __init__(self):
        # Configurações por tipo de operação
        self.operation_configs = {
            # Document analysis operations
            "document_analysis": RetryConfig(
                max_attempts=3,
                base_delay=2.0,
                max_delay=30.0,
                strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
                retry_on_exceptions=[ConnectionError, TimeoutError, ValueError],
                stop_on_exceptions=[PermissionError, FileNotFoundError]
            ),
            
            # API calls to external services
            "external_api": RetryConfig(
                max_attempts=5,
                base_delay=1.0,
                max_delay=120.0,
                strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
                retry_on_exceptions=[ConnectionError, TimeoutError],
                operation_timeout=30.0
            ),
            
            # Database operations
            "database": RetryConfig(
                max_attempts=3,
                base_delay=0.5,
                max_delay=10.0,
                strategy=RetryStrategy.LINEAR_BACKOFF,
                retry_on_exceptions=[ConnectionError, TimeoutError]
            ),
            
            # File operations  
            "file_operations": RetryConfig(
                max_attempts=2,
                base_delay=1.0,
                max_delay=5.0,
                strategy=RetryStrategy.FIXED_DELAY,
                retry_on_exceptions=[OSError, IOError]
            ),
            
            # LLM/AI operations
            "llm_operations": RetryConfig(
                max_attempts=4,
                base_delay=3.0,
                max_delay=60.0,
                strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
                retry_on_exceptions=[ConnectionError, TimeoutError, ValueError],
                operation_timeout=120.0
            ),
            
            # Critical operations (fewer retries)
            "critical": RetryConfig(
                max_attempts=2,
                base_delay=0.5,
                max_delay=2.0,
                strategy=RetryStrategy.FIXED_DELAY
            ),
            
            # Default configuration
            "default": RetryConfig()
        }
        
        # Active retry operations tracking
        self.active_operations: Dict[str, RetryResult] = {}
    
    def calculate_delay(self, attempt: int, config: RetryConfig) -> float:
        """
        Calcula delay baseado na estratégia configurada
        """
        if config.strategy == RetryStrategy.IMMEDIATE:
            return 0.0
            
        elif config.strategy == RetryStrategy.FIXED_DELAY:
            return min(config.base_delay, config.max_delay)
            
        elif config.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = config.base_delay * attempt
            return min(delay, config.max_delay)
            
        elif config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = config.base_delay * (config.backoff_multiplier ** (attempt - 1))
            return min(delay, config.max_delay)
            
        return config.base_delay
    
    def should_retry(self, exception: Exception, config: RetryConfig) -> bool:
        """
        Determina se deve tentar novamente baseado na exceção
        """
        # Verificar exceções que param o retry
        for stop_exc in config.stop_on_exceptions:
            if isinstance(exception, stop_exc):
                logger.info(f"Stopping retry due to {type(exception).__name__}")
                return False
        
        # Verificar exceções que permitem retry
        for retry_exc in config.retry_on_exceptions:
            if isinstance(exception, retry_exc):
                return True
        
        # Se não há configuração específica, não retry
        return False
    
    async def execute_with_retry(self, 
                               operation: Callable,
                               operation_type: str = "default",
                               operation_id: Optional[str] = None,
                               custom_config: Optional[RetryConfig] = None,
                               context: Dict[str, Any] = None,
                               **kwargs) -> RetryResult:
        """
        Executa operação com retry automático
        """
        config = custom_config or self.operation_configs.get(operation_type, self.operation_configs["default"])
        context = context or {}
        operation_id = operation_id or f"{operation_type}_{datetime.now().timestamp()}"
        
        result = RetryResult()
        start_time = datetime.now()
        
        logger.info(f"🔄 Starting retry operation: {operation_id} (type: {operation_type})")
        
        # Track active operation
        self.active_operations[operation_id] = result
        
        try:
            for attempt in range(1, config.max_attempts + 1):
                attempt_start = datetime.now()
                attempt_info = RetryAttempt(
                    attempt_number=attempt,
                    timestamp=attempt_start
                )
                
                try:
                    # Execute with timeout if configured
                    if config.operation_timeout:
                        operation_result = await asyncio.wait_for(
                            operation(**kwargs) if asyncio.iscoroutinefunction(operation) 
                            else asyncio.to_thread(operation, **kwargs),
                            timeout=config.operation_timeout
                        )
                    else:
                        operation_result = await operation(**kwargs) if asyncio.iscoroutinefunction(operation) \
                                         else operation(**kwargs)
                    
                    # Success!
                    attempt_info.success = True
                    attempt_info.duration = (datetime.now() - attempt_start).total_seconds()
                    result.attempts.append(attempt_info)
                    result.success = True
                    result.result = operation_result
                    result.total_attempts = attempt
                    
                    logger.info(f"✅ Operation {operation_id} succeeded on attempt {attempt}")
                    break
                    
                except Exception as e:
                    attempt_info.exception = e
                    attempt_info.duration = (datetime.now() - attempt_start).total_seconds()
                    result.attempts.append(attempt_info)
                    result.final_exception = e
                    
                    logger.warning(f"⚠️ Attempt {attempt} failed for {operation_id}: {str(e)}")
                    
                    # Check if should retry
                    if attempt < config.max_attempts and self.should_retry(e, config):
                        delay = self.calculate_delay(attempt, config)
                        
                        logger.info(f"🔄 Retrying {operation_id} in {delay:.2f} seconds...")
                        
                        if delay > 0:
                            await asyncio.sleep(delay)
                    else:
                        logger.error(f"❌ Operation {operation_id} failed after {attempt} attempts")
                        result.total_attempts = attempt
                        break
            
            result.total_duration = (datetime.now() - start_time).total_seconds()
            
            return result
            
        finally:
            # Remove from active operations
            self.active_operations.pop(operation_id, None)
    
    def retry_decorator(self, 
                       operation_type: str = "default",
                       custom_config: Optional[RetryConfig] = None):
        """
        Decorator para retry automático
        """
        def decorator(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await self.execute_with_retry(
                    operation=func,
                    operation_type=operation_type,
                    custom_config=custom_config,
                    **kwargs
                )
                
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                return asyncio.run(self.execute_with_retry(
                    operation=func,
                    operation_type=operation_type,
                    custom_config=custom_config,
                    **kwargs
                ))
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        
        return decorator
    
    def get_operation_status(self, operation_id: str) -> Optional[RetryResult]:
        """
        Obtém status de uma operação em andamento
        """
        return self.active_operations.get(operation_id)
    
    def get_active_operations(self) -> Dict[str, RetryResult]:
        """
        Retorna todas as operações ativas
        """
        return self.active_operations.copy()
    
    def get_retry_statistics(self) -> Dict[str, Any]:
        """
        Obtém estatísticas de retry do sistema
        """
        stats = {
            "active_operations": len(self.active_operations),
            "operation_types": list(self.operation_configs.keys()),
            "configurations": {
                op_type: {
                    "max_attempts": config.max_attempts,
                    "strategy": config.strategy.value,
                    "base_delay": config.base_delay,
                    "max_delay": config.max_delay
                }
                for op_type, config in self.operation_configs.items()
            }
        }
        
        return stats

# Instância global do sistema de retry
retry_system = RetrySystem()

# Decorators convenientes para diferentes tipos de operação
def retry_document_analysis(func):
    return retry_system.retry_decorator("document_analysis")(func)

def retry_external_api(func):
    return retry_system.retry_decorator("external_api")(func)

def retry_database(func):
    return retry_system.retry_decorator("database")(func)

def retry_llm_operations(func):
    return retry_system.retry_decorator("llm_operations")(func)

def retry_file_operations(func):
    return retry_system.retry_decorator("file_operations")(func)

def retry_critical(func):
    return retry_system.retry_decorator("critical")(func)

# Helper functions
async def retry_operation(operation: Callable,
                         operation_type: str = "default",
                         max_attempts: int = 3,
                         base_delay: float = 1.0,
                         **kwargs) -> RetryResult:
    """
    Função helper para retry manual
    """
    config = RetryConfig(
        max_attempts=max_attempts,
        base_delay=base_delay
    )
    
    return await retry_system.execute_with_retry(
        operation=operation,
        operation_type=operation_type,
        custom_config=config,
        **kwargs
    )