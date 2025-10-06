"""
A/B Testing System for Pipeline vs Legacy Document Analysis
Sistema de testes A/B para comparar pipeline modular vs sistema legado
"""

import hashlib
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import json

logger = logging.getLogger(__name__)

class ABTestingManager:
    """
    Gerencia A/B testing entre pipeline modular e sistema legado
    """
    
    def __init__(self):
        self.pipeline_enabled = True
        self.pipeline_percentage = 50  # 50% dos usuários usam pipeline
        self.force_pipeline_for_passports = True  # Force pipeline for passports
        
        # Test groups tracking
        self.test_results = {
            'pipeline': {
                'total_documents': 0,
                'successful_analyses': 0,
                'avg_processing_time': 0.0,
                'avg_confidence': 0.0
            },
            'legacy': {
                'total_documents': 0, 
                'successful_analyses': 0,
                'avg_processing_time': 0.0,
                'avg_confidence': 0.0
            }
        }
    
    def should_use_pipeline(self, 
                           user_id: str, 
                           document_type: str, 
                           filename: str = "") -> Dict[str, Any]:
        """
        Determina se deve usar pipeline ou sistema legado
        
        Returns:
            Dict com decisão e metadados do teste
        """
        if not self.pipeline_enabled:
            return {
                'use_pipeline': False,
                'reason': 'pipeline_disabled',
                'test_group': 'legacy_forced'
            }
        
        # Force pipeline for passports (nossa implementação está pronta)
        if self.force_pipeline_for_passports and self._is_likely_passport(document_type, filename):
            return {
                'use_pipeline': True,
                'reason': 'passport_forced_pipeline',
                'test_group': 'pipeline_passport'
            }
        
        # A/B testing baseado em hash do user_id para consistência
        user_hash = int(hashlib.md5(user_id.encode()).hexdigest()[:8], 16)
        use_pipeline = (user_hash % 100) < self.pipeline_percentage
        
        return {
            'use_pipeline': use_pipeline,
            'reason': 'ab_testing',
            'test_group': 'pipeline_test' if use_pipeline else 'legacy_test',
            'user_hash': user_hash % 100
        }
    
    def _is_likely_passport(self, document_type: str, filename: str) -> bool:
        """Detecta se documento é provavelmente um passaporte"""
        passport_indicators = [
            'passport', 'pasaporte', 'passaporte',
            'travel_document', 'documento_viagem'
        ]
        
        # Check document type
        if any(indicator in document_type.lower() for indicator in passport_indicators):
            return True
        
        # Check filename
        if any(indicator in filename.lower() for indicator in passport_indicators):
            return True
        
        return False
    
    def _is_likely_i797(self, document_type: str, filename: str) -> bool:
        """Detecta se documento é provavelmente um I-797"""
        i797_indicators = [
            'i797', 'i-797', 'notice', 'uscis', 'receipt',
            'approval', 'petition', 'immigration'
        ]
        
        # Check document type
        if any(indicator in document_type.lower() for indicator in i797_indicators):
            return True
        
        # Check filename
        if any(indicator in filename.lower() for indicator in i797_indicators):
            return True
        
        return False
    
    def record_analysis_result(self, 
                             test_group: str,
                             processing_time: float,
                             confidence: float,
                             success: bool,
                             analysis_result: Dict[str, Any]):
        """
        Registra resultado da análise para comparação A/B
        """
        try:
            group = 'pipeline' if 'pipeline' in test_group else 'legacy'
            
            # Update counters
            self.test_results[group]['total_documents'] += 1
            if success:
                self.test_results[group]['successful_analyses'] += 1
            
            # Update averages
            current_avg_time = self.test_results[group]['avg_processing_time']
            current_avg_conf = self.test_results[group]['avg_confidence']
            total_docs = self.test_results[group]['total_documents']
            
            # Rolling average for processing time
            self.test_results[group]['avg_processing_time'] = (
                (current_avg_time * (total_docs - 1) + processing_time) / total_docs
            )
            
            # Rolling average for confidence
            self.test_results[group]['avg_confidence'] = (
                (current_avg_conf * (total_docs - 1) + confidence) / total_docs
            )
            
            logger.info(f"A/B Test result recorded: {group}, success: {success}, "
                       f"time: {processing_time:.3f}s, confidence: {confidence:.2f}")
            
        except Exception as e:
            logger.error(f"Error recording A/B test result: {e}")
    
    def get_test_comparison(self) -> Dict[str, Any]:
        """
        Retorna comparação detalhada entre pipeline e legacy
        """
        pipeline_stats = self.test_results['pipeline']
        legacy_stats = self.test_results['legacy']
        
        # Calculate success rates
        pipeline_success_rate = (
            pipeline_stats['successful_analyses'] / pipeline_stats['total_documents']
            if pipeline_stats['total_documents'] > 0 else 0
        )
        
        legacy_success_rate = (
            legacy_stats['successful_analyses'] / legacy_stats['total_documents']
            if legacy_stats['total_documents'] > 0 else 0
        )
        
        # Calculate improvements
        time_improvement = 0
        confidence_improvement = 0
        success_rate_improvement = 0
        
        if legacy_stats['total_documents'] > 0:
            if legacy_stats['avg_processing_time'] > 0:
                time_improvement = (
                    (legacy_stats['avg_processing_time'] - pipeline_stats['avg_processing_time']) /
                    legacy_stats['avg_processing_time'] * 100
                )
            
            confidence_improvement = (
                pipeline_stats['avg_confidence'] - legacy_stats['avg_confidence']
            )
            
            success_rate_improvement = (
                pipeline_success_rate - legacy_success_rate
            ) * 100
        
        return {
            'pipeline': {
                'total_documents': pipeline_stats['total_documents'],
                'success_rate': pipeline_success_rate,
                'avg_processing_time_ms': pipeline_stats['avg_processing_time'] * 1000,
                'avg_confidence_pct': pipeline_stats['avg_confidence']
            },
            'legacy': {
                'total_documents': legacy_stats['total_documents'],
                'success_rate': legacy_success_rate,
                'avg_processing_time_ms': legacy_stats['avg_processing_time'] * 1000,
                'avg_confidence_pct': legacy_stats['avg_confidence']
            },
            'improvements': {
                'processing_time_improvement_pct': time_improvement,
                'confidence_improvement_points': confidence_improvement,
                'success_rate_improvement_points': success_rate_improvement
            },
            'test_config': {
                'pipeline_enabled': self.pipeline_enabled,
                'pipeline_percentage': self.pipeline_percentage,
                'force_pipeline_for_passports': self.force_pipeline_for_passports
            }
        }
    
    def configure_test(self, 
                      pipeline_percentage: Optional[int] = None,
                      force_passport_pipeline: Optional[bool] = None,
                      enable_pipeline: Optional[bool] = None):
        """
        Configura parâmetros do teste A/B
        """
        if pipeline_percentage is not None:
            self.pipeline_percentage = max(0, min(100, pipeline_percentage))
            logger.info(f"Pipeline percentage set to {self.pipeline_percentage}%")
        
        if force_passport_pipeline is not None:
            self.force_pipeline_for_passports = force_passport_pipeline
            logger.info(f"Force passport pipeline: {self.force_pipeline_for_passports}")
        
        if enable_pipeline is not None:
            self.pipeline_enabled = enable_pipeline
            logger.info(f"Pipeline enabled: {self.pipeline_enabled}")
    
    def reset_test_results(self):
        """Reset test results for fresh comparison"""
        self.test_results = {
            'pipeline': {
                'total_documents': 0,
                'successful_analyses': 0,
                'avg_processing_time': 0.0,
                'avg_confidence': 0.0
            },
            'legacy': {
                'total_documents': 0,
                'successful_analyses': 0,
                'avg_processing_time': 0.0,
                'avg_confidence': 0.0
            }
        }
        logger.info("A/B test results reset")

# Global instance
ab_testing_manager = ABTestingManager()