"""
Cross-Document Consistency Engine - Phase 3
Sistema avançado para verificação de consistência entre documentos
"""
import re
from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime, date
from difflib import SequenceMatcher
from validators import normalize_date

logger = logging.getLogger(__name__)

class CrossDocumentConsistencyEngine:
    """
    Motor de verificação de consistência entre múltiplos documentos
    """
    
    def __init__(self):
        self.consistency_rules = self._initialize_consistency_rules()
        self.field_matchers = self._initialize_field_matchers()
        self.tolerance_thresholds = self._initialize_tolerances()
    
    def _initialize_consistency_rules(self) -> Dict[str, Dict]:
        """
        Inicializa regras de consistência entre tipos de documentos
        """
        return {
            'beneficiary_name_consistency': {
                'documents': ['PASSPORT_ID_PAGE', 'BIRTH_CERTIFICATE', 'I797_NOTICE', 'EMPLOYMENT_OFFER_LETTER'],
                'fields': ['full_name', 'beneficiary', 'employee_name'],
                'match_type': 'name_similarity',
                'tolerance': 0.85,
                'critical': True,
                'description': 'Beneficiary name must be consistent across all documents'
            },
            'date_of_birth_consistency': {
                'documents': ['PASSPORT_ID_PAGE', 'BIRTH_CERTIFICATE', 'I797_NOTICE'],
                'fields': ['date_of_birth', 'birth_date', 'dob'],
                'match_type': 'exact_date',
                'tolerance': 0,
                'critical': True,
                'description': 'Date of birth must match exactly across documents'
            },
            'passport_number_consistency': {
                'documents': ['PASSPORT_ID_PAGE', 'I94_RECORD', 'EMPLOYMENT_OFFER_LETTER'],
                'fields': ['passport_number', 'passport_no', 'document_number'],
                'match_type': 'exact_match',
                'tolerance': 0,
                'critical': True,
                'description': 'Passport number must match exactly'
            },
            'employer_consistency': {
                'documents': ['EMPLOYMENT_OFFER_LETTER', 'I797_NOTICE', 'PAY_STUB'],
                'fields': ['employer_legal_name', 'petitioner', 'employer_name'],
                'match_type': 'company_name_similarity',
                'tolerance': 0.80,
                'critical': True,
                'description': 'Employer name must be consistent across employment documents'
            },
            'job_title_consistency': {
                'documents': ['EMPLOYMENT_OFFER_LETTER', 'I797_NOTICE', 'PAY_STUB'],
                'fields': ['job_title', 'position', 'job_classification'],
                'match_type': 'text_similarity',
                'tolerance': 0.75,
                'critical': False,
                'description': 'Job title should be consistent across employment documents'
            },
            'salary_consistency': {
                'documents': ['EMPLOYMENT_OFFER_LETTER', 'PAY_STUB', 'TAX_RETURN_1040'],
                'fields': ['compensation', 'salary', 'annual_wage', 'income'],
                'match_type': 'salary_range',
                'tolerance': 0.15,  # 15% de variação permitida
                'critical': False,
                'description': 'Salary information should be consistent within reasonable range'
            },
            'address_consistency': {
                'documents': ['PASSPORT_ID_PAGE', 'BIRTH_CERTIFICATE', 'EMPLOYMENT_OFFER_LETTER'],
                'fields': ['address', 'birth_place', 'work_location'],
                'match_type': 'address_similarity',
                'tolerance': 0.70,
                'critical': False,
                'description': 'Address information should show reasonable consistency'
            }
        }
    
    def _initialize_field_matchers(self) -> Dict[str, callable]:
        """
        Inicializa funções de matching específicas para tipos de campos
        """
        return {
            'name_similarity': self._match_names,
            'exact_date': self._match_dates_exact,
            'exact_match': self._match_exact,
            'company_name_similarity': self._match_company_names,
            'text_similarity': self._match_text_similarity,
            'salary_range': self._match_salary_range,
            'address_similarity': self._match_addresses
        }
    
    def _initialize_tolerances(self) -> Dict[str, float]:
        """
        Define tolerâncias padrão para diferentes tipos de matching
        """
        return {
            'name_high_confidence': 0.90,
            'name_medium_confidence': 0.80,
            'name_low_confidence': 0.70,
            'text_high_similarity': 0.85,
            'text_medium_similarity': 0.75,
            'company_name_similarity': 0.80,
            'address_similarity': 0.70,
            'salary_variance_acceptable': 0.15
        }
    
    def analyze_document_consistency(self, 
                                   documents_data: List[Dict[str, Any]],
                                   case_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analisa consistência entre múltiplos documentos
        
        Args:
            documents_data: Lista de dados extraídos de documentos
            case_context: Contexto adicional do caso
            
        Returns:
            Resultado da análise de consistência
        """
        try:
            if len(documents_data) < 2:
                return {
                    'status': 'insufficient_documents',
                    'consistency_score': 1.0,
                    'issues': [],
                    'recommendations': [],
                    'document_count': len(documents_data)
                }
            
            # 1. Organizar documentos por tipo
            organized_docs = self._organize_documents_by_type(documents_data)
            
            # 2. Executar verificações de consistência
            consistency_results = []
            
            for rule_name, rule_config in self.consistency_rules.items():
                result = self._check_consistency_rule(
                    rule_name, rule_config, organized_docs, case_context
                )
                if result:
                    consistency_results.append(result)
            
            # 3. Calcular score geral e identificar problemas
            overall_score, critical_issues, warnings = self._calculate_consistency_score(
                consistency_results
            )
            
            # 4. Gerar recomendações
            recommendations = self._generate_consistency_recommendations(
                consistency_results, critical_issues, warnings
            )
            
            return {
                'status': 'analyzed',
                'consistency_score': overall_score,
                'results': consistency_results,
                'critical_issues': critical_issues,
                'warnings': warnings,
                'recommendations': recommendations,
                'document_count': len(documents_data),
                'documents_analyzed': list(organized_docs.keys())
            }
            
        except Exception as e:
            logger.error(f"Error in consistency analysis: {e}")
            return {
                'status': 'error',
                'error_message': str(e),
                'consistency_score': 0.0,
                'issues': [],
                'recommendations': []
            }
    
    def _organize_documents_by_type(self, documents_data: List[Dict]) -> Dict[str, Dict]:
        """
        Organiza documentos por tipo para facilitar comparação
        """
        organized = {}
        
        for doc_data in documents_data:
            doc_type = doc_data.get('doc_type') or doc_data.get('document_type')
            if doc_type:
                organized[doc_type] = doc_data
        
        return organized
    
    def _check_consistency_rule(self, 
                               rule_name: str, 
                               rule_config: Dict, 
                               organized_docs: Dict[str, Dict],
                               case_context: Dict) -> Optional[Dict]:
        """
        Verifica uma regra específica de consistência
        """
        required_docs = rule_config['documents']
        target_fields = rule_config['fields']
        match_type = rule_config['match_type']
        tolerance = rule_config['tolerance']
        is_critical = rule_config['critical']
        
        # Verificar se temos documentos suficientes para esta regra
        available_docs = [doc_type for doc_type in required_docs if doc_type in organized_docs]
        if len(available_docs) < 2:
            return None  # Não há documentos suficientes para esta verificação
        
        # Extrair valores dos campos relevantes
        field_values = self._extract_field_values_for_consistency(
            available_docs, target_fields, organized_docs
        )
        
        if not field_values or len(field_values) < 2:
            return None  # Não há valores suficientes para comparar
        
        # Aplicar função de matching apropriada
        matcher_func = self.field_matchers.get(match_type, self._match_text_similarity)
        match_result = matcher_func(field_values, tolerance)
        
        # Determinar status baseado no resultado
        if match_result['consistent']:
            status = 'pass'
            severity = 'low'
        elif match_result['similarity_score'] >= (tolerance - 0.1):  # Próximo da tolerância
            status = 'alert'
            severity = 'medium' if is_critical else 'low'
        else:
            status = 'fail'
            severity = 'critical' if is_critical else 'medium'
        
        return {
            'rule_name': rule_name,
            'status': status,
            'severity': severity,
            'is_critical': is_critical,
            'similarity_score': match_result['similarity_score'],
            'tolerance': tolerance,
            'documents_checked': available_docs,
            'field_values': field_values,
            'match_details': match_result,
            'description': rule_config['description'],
            'message': self._generate_consistency_message(rule_name, match_result, available_docs)
        }
    
    def _extract_field_values_for_consistency(self, 
                                            doc_types: List[str], 
                                            field_names: List[str], 
                                            organized_docs: Dict[str, Dict]) -> List[Dict]:
        """
        Extrai valores de campos relevantes para verificação de consistência
        """
        field_values = []
        
        for doc_type in doc_types:
            doc_data = organized_docs.get(doc_type, {})
            
            # Buscar em diferentes seções dos dados do documento
            fields_section = doc_data.get('fields', {})
            
            for field_name in field_names:
                value = None
                
                # Buscar em policy_fields primeiro
                policy_fields = fields_section.get('policy_fields', {})
                if field_name in policy_fields:
                    field_data = policy_fields[field_name]
                    if field_data.get('found') and field_data.get('best_match'):
                        value = field_data['best_match'].get('normalized_value')
                
                # Buscar em outros tipos de campos se não encontrado
                if not value:
                    for field_type, extractions in fields_section.items():
                        if field_type == 'policy_fields':
                            continue
                        if isinstance(extractions, list):
                            for extraction in extractions:
                                if field_name.lower() in extraction.get('field_type', '').lower():
                                    value = extraction.get('normalized_value')
                                    break
                        if value:
                            break
                
                # Buscar diretamente nos dados do documento se ainda não encontrado
                if not value:
                    value = doc_data.get(field_name)
                
                if value:
                    field_values.append({
                        'document_type': doc_type,
                        'field_name': field_name,
                        'value': value,
                        'source': 'extracted_fields'
                    })
        
        return field_values
    
    def _match_names(self, field_values: List[Dict], tolerance: float) -> Dict[str, Any]:
        """
        Compara nomes com algoritmos específicos para nomes de pessoas
        """
        if len(field_values) < 2:
            return {'consistent': False, 'similarity_score': 0.0, 'details': 'Insufficient values'}
        
        names = [self._normalize_name(fv['value']) for fv in field_values]
        
        # Comparar todos os pares
        similarities = []
        comparisons = []
        
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                name1, name2 = names[i], names[j]
                
                # Múltiplas estratégias de comparação de nomes
                similarities_methods = [
                    self._name_similarity_tokens(name1, name2),
                    self._name_similarity_sequence(name1, name2),
                    self._name_similarity_initials(name1, name2)
                ]
                
                # Usar a maior similaridade encontrada
                max_similarity = max(similarities_methods)
                similarities.append(max_similarity)
                
                comparisons.append({
                    'name1': field_values[i]['value'],
                    'name2': field_values[j]['value'],
                    'similarity': max_similarity,
                    'doc1': field_values[i]['document_type'],
                    'doc2': field_values[j]['document_type']
                })
        
        avg_similarity = sum(similarities) / len(similarities) if similarities else 0.0
        min_similarity = min(similarities) if similarities else 0.0
        
        return {
            'consistent': min_similarity >= tolerance,
            'similarity_score': avg_similarity,
            'min_similarity': min_similarity,
            'details': comparisons,
            'method': 'advanced_name_matching'
        }
    
    def _match_dates_exact(self, field_values: List[Dict], tolerance: float) -> Dict[str, Any]:
        """
        Compara datas com matching exato (tolerância zero para datas)
        """
        if len(field_values) < 2:
            return {'consistent': False, 'similarity_score': 0.0, 'details': 'Insufficient values'}
        
        # Normalizar todas as datas
        normalized_dates = []
        for fv in field_values:
            normalized = normalize_date(str(fv['value']))
            normalized_dates.append({
                'original': fv['value'],
                'normalized': normalized,
                'document': fv['document_type']
            })
        
        # Verificar se todas as datas normalizadas são iguais
        valid_dates = [nd for nd in normalized_dates if nd['normalized']]
        
        if len(valid_dates) < 2:
            return {'consistent': False, 'similarity_score': 0.0, 'details': 'Invalid dates found'}
        
        unique_dates = set(nd['normalized'] for nd in valid_dates)
        consistent = len(unique_dates) == 1
        
        return {
            'consistent': consistent,
            'similarity_score': 1.0 if consistent else 0.0,
            'details': normalized_dates,
            'unique_dates_count': len(unique_dates),
            'method': 'exact_date_matching'
        }
    
    def _match_exact(self, field_values: List[Dict], tolerance: float) -> Dict[str, Any]:
        """
        Comparação exata de valores (para números de documentos, etc.)
        """
        if len(field_values) < 2:
            return {'consistent': False, 'similarity_score': 0.0, 'details': 'Insufficient values'}
        
        # Normalizar valores (remover espaços, converter para uppercase)
        normalized_values = []
        for fv in field_values:
            normalized = re.sub(r'\s+', '', str(fv['value']).upper())
            normalized_values.append({
                'original': fv['value'],
                'normalized': normalized,
                'document': fv['document_type']
            })
        
        unique_values = set(nv['normalized'] for nv in normalized_values)
        consistent = len(unique_values) == 1
        
        return {
            'consistent': consistent,
            'similarity_score': 1.0 if consistent else 0.0,
            'details': normalized_values,
            'unique_values_count': len(unique_values),
            'method': 'exact_matching'
        }
    
    def _match_company_names(self, field_values: List[Dict], tolerance: float) -> Dict[str, Any]:
        """
        Comparação específica para nomes de empresas
        """
        if len(field_values) < 2:
            return {'consistent': False, 'similarity_score': 0.0, 'details': 'Insufficient values'}
        
        # Normalizar nomes de empresas
        normalized_names = []
        for fv in field_values:
            normalized = self._normalize_company_name(fv['value'])
            normalized_names.append({
                'original': fv['value'],
                'normalized': normalized,
                'document': fv['document_type']
            })
        
        # Comparar todas as combinações
        similarities = []
        comparisons = []
        
        for i in range(len(normalized_names)):
            for j in range(i + 1, len(normalized_names)):
                name1 = normalized_names[i]['normalized']
                name2 = normalized_names[j]['normalized']
                
                # Similaridade baseada em tokens
                similarity = self._company_name_similarity(name1, name2)
                similarities.append(similarity)
                
                comparisons.append({
                    'company1': field_values[i]['value'],
                    'company2': field_values[j]['value'],
                    'similarity': similarity,
                    'doc1': field_values[i]['document_type'],
                    'doc2': field_values[j]['document_type']
                })
        
        avg_similarity = sum(similarities) / len(similarities) if similarities else 0.0
        min_similarity = min(similarities) if similarities else 0.0
        
        return {
            'consistent': min_similarity >= tolerance,
            'similarity_score': avg_similarity,
            'min_similarity': min_similarity,
            'details': comparisons,
            'method': 'company_name_matching'
        }
    
    def _match_text_similarity(self, field_values: List[Dict], tolerance: float) -> Dict[str, Any]:
        """
        Comparação genérica de similaridade de texto
        """
        if len(field_values) < 2:
            return {'consistent': False, 'similarity_score': 0.0, 'details': 'Insufficient values'}
        
        values = [str(fv['value']).lower().strip() for fv in field_values]
        
        # Calcular similaridade média entre todos os pares
        similarities = []
        for i in range(len(values)):
            for j in range(i + 1, len(values)):
                similarity = SequenceMatcher(None, values[i], values[j]).ratio()
                similarities.append(similarity)
        
        avg_similarity = sum(similarities) / len(similarities) if similarities else 0.0
        
        return {
            'consistent': avg_similarity >= tolerance,
            'similarity_score': avg_similarity,
            'details': [{'value': fv['value'], 'document': fv['document_type']} for fv in field_values],
            'method': 'text_similarity'
        }
    
    def _match_salary_range(self, field_values: List[Dict], tolerance: float) -> Dict[str, Any]:
        """
        Comparação de valores salariais com tolerância para variação
        """
        if len(field_values) < 2:
            return {'consistent': False, 'similarity_score': 0.0, 'details': 'Insufficient values'}
        
        # Extrair valores numéricos dos salários
        salary_values = []
        for fv in field_values:
            amount = self._extract_monetary_amount(fv['value'])
            if amount:
                salary_values.append({
                    'original': fv['value'],
                    'amount': amount,
                    'document': fv['document_type']
                })
        
        if len(salary_values) < 2:
            return {'consistent': False, 'similarity_score': 0.0, 'details': 'No valid salary amounts found'}
        
        amounts = [sv['amount'] for sv in salary_values]
        min_amount = min(amounts)
        max_amount = max(amounts)
        
        # Calcular variação percentual
        if min_amount > 0:
            variation = (max_amount - min_amount) / min_amount
            consistent = variation <= tolerance
            similarity_score = max(0, 1 - (variation / tolerance))
        else:
            consistent = False
            similarity_score = 0.0
        
        return {
            'consistent': consistent,
            'similarity_score': similarity_score,
            'variation_percentage': variation if min_amount > 0 else 1.0,
            'tolerance': tolerance,
            'details': salary_values,
            'method': 'salary_range_matching'
        }
    
    def _match_addresses(self, field_values: List[Dict], tolerance: float) -> Dict[str, Any]:
        """
        Comparação de endereços com normalização
        """
        if len(field_values) < 2:
            return {'consistent': False, 'similarity_score': 0.0, 'details': 'Insufficient values'}
        
        # Normalizar endereços
        normalized_addresses = []
        for fv in field_values:
            normalized = self._normalize_address(fv['value'])
            normalized_addresses.append({
                'original': fv['value'],
                'normalized': normalized,
                'document': fv['document_type']
            })
        
        # Comparar similaridade
        similarities = []
        for i in range(len(normalized_addresses)):
            for j in range(i + 1, len(normalized_addresses)):
                addr1 = normalized_addresses[i]['normalized']
                addr2 = normalized_addresses[j]['normalized']
                similarity = self._address_similarity(addr1, addr2)
                similarities.append(similarity)
        
        avg_similarity = sum(similarities) / len(similarities) if similarities else 0.0
        
        return {
            'consistent': avg_similarity >= tolerance,
            'similarity_score': avg_similarity,
            'details': normalized_addresses,
            'method': 'address_similarity'
        }
    
    # Métodos auxiliares para normalização e comparação
    
    def _normalize_name(self, name: str) -> str:
        """Normaliza nome para comparação"""
        if not name:
            return ""
        # Remove pontuação, converte para minúsculo, remove espaços extras
        normalized = re.sub(r'[^\w\s]', '', str(name).lower())
        return ' '.join(normalized.split())
    
    def _normalize_company_name(self, company_name: str) -> str:
        """Normaliza nome de empresa"""
        if not company_name:
            return ""
        
        # Remove sufixos comuns de empresas
        suffixes = ['inc', 'corp', 'corporation', 'llc', 'ltd', 'limited', 'co', 'company']
        normalized = str(company_name).lower().strip()
        
        for suffix in suffixes:
            normalized = re.sub(rf'\b{suffix}\.?\b', '', normalized)
        
        # Remove pontuação e espaços extras
        normalized = re.sub(r'[^\w\s]', '', normalized)
        return ' '.join(normalized.split())
    
    def _normalize_address(self, address: str) -> str:
        """Normaliza endereço"""
        if not address:
            return ""
        
        normalized = str(address).lower()
        
        # Normalizar abreviações comuns
        abbreviations = {
            'street': 'st', 'avenue': 'ave', 'boulevard': 'blvd',
            'road': 'rd', 'drive': 'dr', 'lane': 'ln'
        }
        
        for full, abbr in abbreviations.items():
            normalized = re.sub(rf'\b{full}\b', abbr, normalized)
        
        return normalized.strip()
    
    def _name_similarity_tokens(self, name1: str, name2: str) -> float:
        """Similaridade baseada em tokens de nome"""
        tokens1 = set(name1.split())
        tokens2 = set(name2.split())
        
        if not tokens1 and not tokens2:
            return 1.0
        if not tokens1 or not tokens2:
            return 0.0
        
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _name_similarity_sequence(self, name1: str, name2: str) -> float:
        """Similaridade baseada em sequência de caracteres"""
        return SequenceMatcher(None, name1, name2).ratio()
    
    def _name_similarity_initials(self, name1: str, name2: str) -> float:
        """Similaridade baseada em iniciais"""
        initials1 = ''.join([word[0] for word in name1.split() if word])
        initials2 = ''.join([word[0] for word in name2.split() if word])
        
        if initials1 == initials2:
            return 0.8  # Boa similaridade para iniciais iguais
        return 0.0
    
    def _company_name_similarity(self, name1: str, name2: str) -> float:
        """Similaridade específica para nomes de empresas"""
        # Combinar similaridade de tokens e sequência
        token_sim = self._name_similarity_tokens(name1, name2)
        sequence_sim = SequenceMatcher(None, name1, name2).ratio()
        
        # Peso maior para tokens (palavras-chave da empresa)
        return (token_sim * 0.7 + sequence_sim * 0.3)
    
    def _address_similarity(self, addr1: str, addr2: str) -> float:
        """Similaridade específica para endereços"""
        return SequenceMatcher(None, addr1, addr2).ratio()
    
    def _extract_monetary_amount(self, value: str) -> Optional[float]:
        """Extrai valor monetário de uma string"""
        if not value:
            return None
        
        # Remover símbolos e extrair números
        cleaned = re.sub(r'[^\d.,]', '', str(value))
        cleaned = cleaned.replace(',', '')
        
        try:
            return float(cleaned)
        except ValueError:
            return None
    
    def _calculate_consistency_score(self, consistency_results: List[Dict]) -> Tuple[float, List[Dict], List[Dict]]:
        """
        Calcula score geral de consistência e identifica problemas
        """
        if not consistency_results:
            return 1.0, [], []
        
        critical_issues = []
        warnings = []
        scores = []
        
        for result in consistency_results:
            if result['status'] == 'fail':
                if result['is_critical']:
                    critical_issues.append(result)
                else:
                    warnings.append(result)
                scores.append(0.0)
            elif result['status'] == 'alert':
                warnings.append(result)
                scores.append(0.7)
            else:  # pass
                scores.append(1.0)
        
        overall_score = sum(scores) / len(scores)
        
        return overall_score, critical_issues, warnings
    
    def _generate_consistency_message(self, rule_name: str, match_result: Dict, documents: List[str]) -> str:
        """
        Gera mensagem descritiva para o resultado da consistência
        """
        if match_result['consistent']:
            return f"Consistência verificada entre {', '.join(documents)}"
        else:
            similarity = match_result.get('similarity_score', 0.0)
            return f"Inconsistência detectada entre {', '.join(documents)} (similaridade: {similarity:.2f})"
    
    def _generate_consistency_recommendations(self, 
                                           consistency_results: List[Dict],
                                           critical_issues: List[Dict],
                                           warnings: List[Dict]) -> List[Dict]:
        """
        Gera recomendações baseadas nos resultados de consistência
        """
        recommendations = []
        
        if critical_issues:
            for issue in critical_issues:
                recommendations.append({
                    'type': 'critical_inconsistency',
                    'severity': 'critical',
                    'title': f"Critical Inconsistency: {issue['rule_name']}",
                    'description': issue['description'],
                    'documents_affected': issue['documents_checked'],
                    'actions': [
                        'Verify the accuracy of information in all affected documents',
                        'Obtain corrected versions if errors are found',
                        'Ensure all documents refer to the same individual/entity'
                    ]
                })
        
        if warnings:
            for warning in warnings[:3]:  # Limitar a 3 warnings principais
                recommendations.append({
                    'type': 'consistency_warning',
                    'severity': 'medium',
                    'title': f"Consistency Alert: {warning['rule_name']}",
                    'description': warning['description'],
                    'documents_affected': warning['documents_checked'],
                    'actions': [
                        'Review the information in the affected documents',
                        'Verify that variations are expected and acceptable',
                        'Consider providing explanation if differences are legitimate'
                    ]
                })
        
        return recommendations

# Instância global do motor de consistência
cross_document_consistency = CrossDocumentConsistencyEngine()