"""
Sistema de Instrumentação Não-Intrusivo
Decorators que coletam métricas sem afetar o funcionamento atual
"""

import time
import functools
import logging
from typing import Dict, Any, Optional, Callable
from .passive_collector import passive_metrics

logger = logging.getLogger(__name__)

def monitor_document_analysis(document_type_extractor: Callable = None):
    """
    Decorator não-intrusivo para monitorar análise de documentos
    
    Args:
        document_type_extractor: Função para extrair tipo do documento do resultado
    """
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Não faz nada se métricas estão desabilitadas
            if not passive_metrics.enabled:
                return await func(*args, **kwargs)
            
            start_time = time.time()
            document_id = kwargs.get('document_id', f"doc_{int(start_time)}")
            
            try:
                # Executa função original (sem alteração)
                result = await func(*args, **kwargs)
                end_time = time.time()
                
                # Extrai métricas do resultado (de forma segura)
                metrics_data = _extract_metrics_safely(result, document_type_extractor)
                
                # Registra métricas de forma assíncrona (não bloqueia)
                _record_metrics_async(
                    document_id=document_id,
                    start_time=start_time,
                    end_time=end_time,
                    result=result,
                    **metrics_data
                )
                
                return result
                
            except Exception as e:
                end_time = time.time()
                
                # Registra erro nas métricas (opcional)
                _record_error_metric(document_id, start_time, end_time, str(e))
                
                # Re-raise para não afetar comportamento original
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Versão síncrona do decorator
            if not passive_metrics.enabled:
                return func(*args, **kwargs)
            
            start_time = time.time()
            document_id = kwargs.get('document_id', f"doc_{int(start_time)}")
            
            try:
                result = func(*args, **kwargs)
                end_time = time.time()
                
                metrics_data = _extract_metrics_safely(result, document_type_extractor)
                _record_metrics_async(
                    document_id=document_id,
                    start_time=start_time,
                    end_time=end_time,
                    result=result,
                    **metrics_data
                )
                
                return result
                
            except Exception as e:
                end_time = time.time()
                _record_error_metric(document_id, start_time, end_time, str(e))
                raise
        
        # Retorna wrapper correto baseado na função original
        if hasattr(func, '__call__') and hasattr(func, '__await__'):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def _extract_metrics_safely(result: Any, extractor: Callable = None) -> Dict[str, Any]:
    """
    Extrai métricas do resultado de forma segura (nunca falha)
    """
    try:
        # Default values
        metrics = {
            'document_type': 'unknown',
            'confidence': 50.0,
            'verdict': 'UNKNOWN',
            'ai_agent': 'unknown'
        }
        
        # Se é um dicionário, tenta extrair campos conhecidos
        if isinstance(result, dict):
            # Extrai tipo do documento
            if 'dr_miguel_validation' in result:
                dr_miguel = result['dr_miguel_validation']
                metrics['document_type'] = dr_miguel.get('document_type_identified', 'unknown')
                metrics['verdict'] = dr_miguel.get('verdict', 'UNKNOWN')
                metrics['ai_agent'] = 'dr_miguel'
            
            # Extrai confidence score
            if 'completeness_score' in result:
                metrics['confidence'] = float(result['completeness_score'])
            
            # Usa extractor customizado se fornecido
            if extractor:
                custom_data = extractor(result)
                metrics.update(custom_data)
        
        return metrics
        
    except Exception as e:
        logger.debug(f"Error extracting metrics (non-critical): {e}")
        return {
            'document_type': 'unknown',
            'confidence': 0.0,
            'verdict': 'ERROR',
            'ai_agent': 'unknown'
        }

def _record_metrics_async(document_id: str, 
                         start_time: float, 
                         end_time: float, 
                         result: Any, 
                         **kwargs):
    """
    Registra métricas de forma assíncrona para não impactar performance
    """
    try:
        passive_metrics.record_document_analysis(
            document_id=document_id,
            document_type=kwargs.get('document_type', 'unknown'),
            start_time=start_time,
            end_time=end_time,
            confidence=kwargs.get('confidence', 0.0),
            verdict=kwargs.get('verdict', 'UNKNOWN'),
            ai_agent=kwargs.get('ai_agent', 'unknown'),
            user_session=kwargs.get('user_session')
        )
    except Exception as e:
        # Falha silenciosa - métricas nunca devem quebrar funcionalidade
        logger.debug(f"Metrics recording failed (non-critical): {e}")

def _record_error_metric(document_id: str, start_time: float, end_time: float, error_msg: str):
    """Registra métrica de erro"""
    try:
        passive_metrics.record_document_analysis(
            document_id=document_id,
            document_type='error',
            start_time=start_time,
            end_time=end_time,
            confidence=0.0,
            verdict='ERROR',
            ai_agent='system',
            user_session=None
        )
    except Exception:
        # Falha silenciosa
        pass

# Feature flag para controlar instrumentação
ENABLE_INSTRUMENTATION = True

def enable_instrumentation():
    """Ativa instrumentação global"""
    global ENABLE_INSTRUMENTATION
    ENABLE_INSTRUMENTATION = True
    passive_metrics.enable()
    logger.info("✅ Instrumentation enabled globally")

def disable_instrumentation():
    """Desativa instrumentação global"""
    global ENABLE_INSTRUMENTATION
    ENABLE_INSTRUMENTATION = False
    passive_metrics.disable()
    logger.info("⏸️ Instrumentation disabled globally")