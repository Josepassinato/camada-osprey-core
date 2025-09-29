"""
Document Analysis Metrics System
Sistema de métricas e KPIs para análise de documentos com alta precisão
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import re
import statistics

logger = logging.getLogger(__name__)

class DecisionType(Enum):
    PASS = "PASS"
    ALERT = "ALERT"
    FAIL = "FAIL"

class SeverityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class FieldExtractionResult:
    field_name: str
    extracted_value: str
    expected_value: str
    confidence_score: float
    exact_match: bool
    similarity_score: float

@dataclass
class DocumentMetrics:
    document_id: str
    doc_type: str
    classification_confidence: float
    classification_correct: bool
    field_extractions: List[FieldExtractionResult]
    quality_score: float
    decision: DecisionType
    human_review_required: bool
    processing_time_ms: float
    analysis_timestamp: datetime

class DocumentAnalysisKPIs:
    """
    Sistema de KPIs baseado no plano de alta precisão
    """
    
    def __init__(self):
        self.metrics_history: List[DocumentMetrics] = []
        
        # KPI Targets from the plan
        self.targets = {
            'classification_f1': 0.95,
            'identity_exact_match': 0.98,
            'dates_exact_match': 0.97,
            'formatted_numbers_exact_match': 0.995,
            'false_fail_rate': 0.01,
            'processing_time_target_ms': 5000
        }
    
    def calculate_classification_f1(self, timeframe_days: int = 30) -> float:
        """
        Calcula F1 score para classificação de tipos de documento
        """
        recent_metrics = self._get_recent_metrics(timeframe_days)
        
        if not recent_metrics:
            return 0.0
        
        true_positives = sum(1 for m in recent_metrics if m.classification_correct)
        total_predictions = len(recent_metrics)
        
        # Simplified F1 calculation (assuming balanced dataset)
        accuracy = true_positives / total_predictions if total_predictions > 0 else 0
        
        # For detailed F1, we'd need false positives/negatives per class
        # Using accuracy as proxy for now
        return accuracy
    
    def calculate_field_exact_match_rate(self, 
                                       field_category: str,
                                       timeframe_days: int = 30) -> float:
        """
        Calcula exact match rate para categoria de campos
        """
        recent_metrics = self._get_recent_metrics(timeframe_days)
        
        category_fields = self._get_fields_by_category(field_category)
        all_extractions = []
        
        for metric in recent_metrics:
            for extraction in metric.field_extractions:
                if extraction.field_name in category_fields:
                    all_extractions.append(extraction)
        
        if not all_extractions:
            return 0.0
        
        exact_matches = sum(1 for e in all_extractions if e.exact_match)
        return exact_matches / len(all_extractions)
    
    def calculate_false_fail_rate(self, timeframe_days: int = 30) -> float:
        """
        Calcula taxa de falsos FAILs (documentos válidos rejeitados)
        """
        recent_metrics = self._get_recent_metrics(timeframe_days)
        
        failed_decisions = [m for m in recent_metrics if m.decision == DecisionType.FAIL]
        
        if not failed_decisions:
            return 0.0
        
        # False fails are FAILs that required human review and were overturned
        false_fails = sum(1 for m in failed_decisions if m.human_review_required)
        
        # This is a simplified calculation - in practice, need human review results
        return false_fails / len(recent_metrics) if recent_metrics else 0.0
    
    def calculate_processing_performance(self, timeframe_days: int = 30) -> Dict[str, float]:
        """
        Calcula métricas de performance de processamento
        """
        recent_metrics = self._get_recent_metrics(timeframe_days)
        
        if not recent_metrics:
            return {}
        
        processing_times = [m.processing_time_ms for m in recent_metrics]
        
        return {
            'avg_processing_time_ms': statistics.mean(processing_times),
            'p95_processing_time_ms': statistics.quantiles(processing_times, n=20)[18] if len(processing_times) >= 20 else max(processing_times),
            'within_target_percentage': sum(1 for t in processing_times if t <= self.targets['processing_time_target_ms']) / len(processing_times)
        }
    
    def generate_kpi_report(self, timeframe_days: int = 30) -> Dict[str, Any]:
        """
        Gera relatório completo de KPIs
        """
        return {
            'report_period': f"Last {timeframe_days} days",
            'generated_at': datetime.utcnow().isoformat(),
            'total_documents_analyzed': len(self._get_recent_metrics(timeframe_days)),
            'kpis': {
                'classification_f1_score': {
                    'value': self.calculate_classification_f1(timeframe_days),
                    'target': self.targets['classification_f1'],
                    'status': 'PASS' if self.calculate_classification_f1(timeframe_days) >= self.targets['classification_f1'] else 'FAIL'
                },
                'identity_fields_exact_match': {
                    'value': self.calculate_field_exact_match_rate('identity', timeframe_days),
                    'target': self.targets['identity_exact_match'],
                    'status': 'PASS' if self.calculate_field_exact_match_rate('identity', timeframe_days) >= self.targets['identity_exact_match'] else 'FAIL'
                },
                'dates_exact_match': {
                    'value': self.calculate_field_exact_match_rate('dates', timeframe_days),
                    'target': self.targets['dates_exact_match'],
                    'status': 'PASS' if self.calculate_field_exact_match_rate('dates', timeframe_days) >= self.targets['dates_exact_match'] else 'FAIL'
                },
                'formatted_numbers_exact_match': {
                    'value': self.calculate_field_exact_match_rate('formatted_numbers', timeframe_days),
                    'target': self.targets['formatted_numbers_exact_match'],
                    'status': 'PASS' if self.calculate_field_exact_match_rate('formatted_numbers', timeframe_days) >= self.targets['formatted_numbers_exact_match'] else 'FAIL'
                },
                'false_fail_rate': {
                    'value': self.calculate_false_fail_rate(timeframe_days),
                    'target': self.targets['false_fail_rate'],
                    'status': 'PASS' if self.calculate_false_fail_rate(timeframe_days) <= self.targets['false_fail_rate'] else 'FAIL'
                }
            },
            'performance_metrics': self.calculate_processing_performance(timeframe_days)
        }
    
    def _get_recent_metrics(self, days: int) -> List[DocumentMetrics]:
        """Obtém métricas dos últimos N dias"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return [m for m in self.metrics_history if m.analysis_timestamp >= cutoff_date]
    
    def _get_fields_by_category(self, category: str) -> List[str]:
        """Categoriza campos por tipo"""
        field_categories = {
            'identity': ['full_name', 'date_of_birth', 'passport_number', 'ssn'],
            'dates': ['expiry_date', 'issue_date', 'valid_from', 'valid_to', 'birth_date'],
            'formatted_numbers': ['receipt_number', 'uscis_number', 'i94_number', 'case_number', 'ssn']
        }
        return field_categories.get(category, [])

class AdvancedFieldValidators:
    """
    Validadores específicos para campos críticos baseados no plano
    """
    
    @staticmethod
    def validate_receipt_number(value: str) -> Tuple[bool, float]:
        """
        Valida I-797 receipt number: 3 letras + 10 dígitos
        """
        pattern = r'^[A-Z]{3}\d{10}$'
        match = re.match(pattern, value.strip())
        
        if match:
            return True, 1.0
        
        # Check partial match for confidence score
        if len(value) == 13 and value[:3].isalpha() and value[3:].isdigit():
            return False, 0.8  # Correct format but case issues
        
        return False, 0.0
    
    @staticmethod
    def validate_ssn(value: str) -> Tuple[bool, float]:
        """
        Valida SSN: XXX-XX-XXXX
        """
        pattern = r'^\d{3}-\d{2}-\d{4}$'
        match = re.match(pattern, value.strip())
        
        if match:
            return True, 1.0
        
        # Check if it's digits only (needs formatting)
        digits_only = re.sub(r'[^0-9]', '', value)
        if len(digits_only) == 9:
            return False, 0.7  # Valid digits, needs formatting
        
        return False, 0.0
    
    @staticmethod
    def validate_passport_number(value: str, nationality: str = None) -> Tuple[bool, float]:
        """
        Valida número de passaporte (padrões por país)
        """
        # Brazilian passport pattern
        if nationality == 'BR' or nationality == 'Brazilian':
            pattern = r'^[A-Z]{2}\d{6}$'
            if re.match(pattern, value.strip()):
                return True, 1.0
        
        # Generic pattern: 6-12 alphanumeric characters
        pattern = r'^[A-Z0-9]{6,12}$'
        match = re.match(pattern, value.strip().upper())
        
        if match:
            return True, 0.9
        
        return False, 0.0
    
    @staticmethod
    def validate_date_format(value: str) -> Tuple[bool, float, str]:
        """
        Valida e normaliza datas para ISO format
        """
        # Common date patterns
        patterns = [
            (r'(\d{4})-(\d{1,2})-(\d{1,2})', '%Y-%m-%d'),  # ISO format
            (r'(\d{1,2})/(\d{1,2})/(\d{4})', '%m/%d/%Y'),  # US format
            (r'(\d{1,2})/(\d{1,2})/(\d{4})', '%d/%m/%Y'),  # BR format
            (r'([A-Za-z]{3})\s+(\d{1,2}),\s+(\d{4})', '%b %d, %Y'),  # Mon DD, YYYY
        ]
        
        for pattern, format_str in patterns:
            match = re.match(pattern, value.strip())
            if match:
                try:
                    if format_str == '%b %d, %Y':
                        parsed_date = datetime.strptime(value.strip(), format_str)
                    else:
                        groups = match.groups()
                        if format_str == '%Y-%m-%d':
                            parsed_date = datetime(int(groups[0]), int(groups[1]), int(groups[2]))
                        elif format_str in ['%m/%d/%Y', '%d/%m/%Y']:
                            # Ambiguous - try both interpretations
                            try:
                                parsed_date = datetime.strptime(value.strip(), format_str)
                            except ValueError:
                                # Try the other format
                                alt_format = '%d/%m/%Y' if format_str == '%m/%d/%Y' else '%m/%d/%Y'
                                parsed_date = datetime.strptime(value.strip(), alt_format)
                    
                    iso_date = parsed_date.strftime('%Y-%m-%d')
                    return True, 1.0, iso_date
                except ValueError:
                    continue
        
        return False, 0.0, value

class QualityAssessment:
    """
    Avaliação de qualidade baseada nos critérios do plano
    """
    
    @staticmethod
    def assess_file_quality(file_content: bytes, file_name: str) -> Dict[str, Any]:
        """
        Avalia qualidade técnica do arquivo
        """
        file_size = len(file_content)
        
        quality_metrics = {
            'file_size_bytes': file_size,
            'estimated_dpi': 'unknown',  # Would need image analysis
            'blur_variance': 'unknown',   # Would need image analysis
            'skew_degrees': 'unknown',    # Would need image analysis
        }
        
        # File size based quality assessment
        quality_score = 100
        issues = []
        
        if file_size < 50000:  # < 50KB
            quality_score -= 50
            issues.append("File too small - may be corrupted or very low resolution")
        elif file_size < 200000:  # < 200KB
            quality_score -= 20
            issues.append("Small file size - resolution may be insufficient")
        
        if file_size > 10000000:  # > 10MB
            quality_score -= 10
            issues.append("Very large file - processing may be slow")
        
        # File extension check
        valid_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.tiff']
        file_extension = '.' + file_name.lower().split('.')[-1] if '.' in file_name else ''
        
        if file_extension not in valid_extensions:
            quality_score -= 30
            issues.append(f"Invalid file type: {file_extension}")
        
        # Determine status
        if quality_score >= 80:
            status = "ok"
        elif quality_score >= 60:
            status = "alert"
        else:
            status = "fail"
        
        return {
            'overall_quality_score': max(quality_score, 0),
            'status': status,
            'metrics': quality_metrics,
            'issues': issues,
            'recommendations': []
        }

class ConsistencyChecker:
    """
    Verificador de consistência entre documentos (Implementation do Consistency Engine)
    """
    
    def __init__(self):
        self.name_similarity_threshold = 0.8
    
    def check_name_consistency(self, documents_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Verifica consistência de nomes entre documentos
        """
        extracted_names = []
        
        for doc in documents_data:
            fields = doc.get('extracted_fields', {})
            name_fields = ['full_name', 'name', 'applicant_name', 'beneficiary_name']
            
            for field in name_fields:
                if field in fields and fields[field].get('value'):
                    extracted_names.append({
                        'name': fields[field]['value'],
                        'document': doc.get('doc_type', 'unknown'),
                        'confidence': fields[field].get('confidence', 0)
                    })
        
        if len(extracted_names) < 2:
            return {'status': 'insufficient_data', 'message': 'Need at least 2 documents with names'}
        
        # Check pairwise consistency
        inconsistencies = []
        for i, name1 in enumerate(extracted_names):
            for j, name2 in enumerate(extracted_names[i+1:], i+1):
                similarity = self._calculate_name_similarity(name1['name'], name2['name'])
                
                if similarity < self.name_similarity_threshold:
                    inconsistencies.append({
                        'doc1': name1['document'],
                        'name1': name1['name'],
                        'doc2': name2['document'], 
                        'name2': name2['name'],
                        'similarity': similarity
                    })
        
        if inconsistencies:
            return {
                'status': 'inconsistent',
                'severity': 'high',
                'inconsistencies': inconsistencies,
                'message': f"Found {len(inconsistencies)} name inconsistencies"
            }
        
        return {
            'status': 'consistent',
            'message': 'All names are consistent across documents'
        }
    
    def check_date_consistency(self, documents_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Verifica consistência lógica de datas
        """
        dates_by_type = {}
        
        for doc in documents_data:
            fields = doc.get('extracted_fields', {})
            doc_type = doc.get('doc_type', 'unknown')
            
            for field_name, field_data in fields.items():
                if 'date' in field_name.lower() and field_data.get('value'):
                    date_type = self._classify_date_type(field_name)
                    if date_type not in dates_by_type:
                        dates_by_type[date_type] = []
                    
                    dates_by_type[date_type].append({
                        'date': field_data['value'],
                        'document': doc_type,
                        'field': field_name
                    })
        
        # Check logical consistency
        issues = []
        
        # Birth date should be before all other dates
        if 'birth' in dates_by_type:
            birth_dates = dates_by_type['birth']
            for other_type, other_dates in dates_by_type.items():
                if other_type != 'birth':
                    for birth_entry in birth_dates:
                        for other_entry in other_dates:
                            if birth_entry['date'] >= other_entry['date']:
                                issues.append(f"Birth date ({birth_entry['date']}) is after {other_type} date ({other_entry['date']})")
        
        # Expiry dates should be after issue dates
        if 'issue' in dates_by_type and 'expiry' in dates_by_type:
            for issue_entry in dates_by_type['issue']:
                for expiry_entry in dates_by_type['expiry']:
                    if issue_entry['date'] >= expiry_entry['date']:
                        issues.append(f"Issue date ({issue_entry['date']}) is after expiry date ({expiry_entry['date']})")
        
        if issues:
            return {
                'status': 'inconsistent',
                'severity': 'medium',
                'issues': issues,
                'message': f"Found {len(issues)} date consistency issues"
            }
        
        return {
            'status': 'consistent',
            'message': 'All dates are logically consistent'
        }
    
    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calcula similaridade entre nomes"""
        if not name1 or not name2:
            return 0.0
        
        # Normalize names
        name1_words = set(name1.lower().replace(',', '').split())
        name2_words = set(name2.lower().replace(',', '').split())
        
        if not name1_words or not name2_words:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(name1_words.intersection(name2_words))
        union = len(name1_words.union(name2_words))
        
        return intersection / union if union > 0 else 0.0
    
    def _classify_date_type(self, field_name: str) -> str:
        """Classifica tipo de data baseado no nome do campo"""
        field_lower = field_name.lower()
        
        if 'birth' in field_lower:
            return 'birth'
        elif 'expiry' in field_lower or 'expir' in field_lower:
            return 'expiry'
        elif 'issue' in field_lower or 'issued' in field_lower:
            return 'issue'
        elif 'valid' in field_lower:
            return 'validity'
        else:
            return 'other'

# Global metrics instance
document_metrics = DocumentAnalysisKPIs()