"""
Automated Document Classification System - Phase 3
Sistema de classificação automática de documentos baseado em conteúdo
"""
import re
from typing import Dict, List, Any, Optional, Tuple
import logging
from collections import Counter
import os

logger = logging.getLogger(__name__)

class DocumentClassifier:
    """
    Sistema de classificação automática de documentos de imigração
    """
    
    def __init__(self):
        self.classification_patterns = self._initialize_classification_patterns()
        self.document_signatures = self._initialize_document_signatures()
        self.confidence_thresholds = self._initialize_confidence_thresholds()
    
    def _initialize_classification_patterns(self) -> Dict[str, Dict]:
        """
        Inicializa padrões para identificação de tipos de documentos
        """
        return {
            'PASSPORT_ID_PAGE': {
                'required_patterns': [
                    r'passport|pasaporte|passaporte',
                    r'\b[A-Z]{1,2}\d{6,10}\b',  # Número de passaporte
                    r'P<[A-Z]{3}'  # MRZ header
                ],
                'optional_patterns': [
                    r'republic|república|kingdom|united states',
                    r'nationality|nacionalidade',
                    r'date of birth|data de nascimento',
                    r'sex|sexo|gender'
                ],
                'negative_patterns': [
                    r'birth certificate|certidão de nascimento',
                    r'marriage|casamento'
                ],
                'file_patterns': [
                    r'passport.*\.(pdf|jpg|jpeg|png)',
                    r'pass.*\.(pdf|jpg|jpeg|png)',
                    r'pp\d*\.(pdf|jpg|jpeg|png)'
                ],
                'weight': {
                    'required': 0.6,
                    'optional': 0.3,
                    'negative': -0.4,
                    'filename': 0.1
                }
            },
            
            'BIRTH_CERTIFICATE': {
                'required_patterns': [
                    r'birth certificate|certidão de nascimento|certificate of birth',
                    r'born|nascimento|nascido|nascida',
                    r'registry|registro|cartório'
                ],
                'optional_patterns': [
                    r'father|pai|mother|mãe|parents',
                    r'hospital|clinic|clínica',
                    r'state|estado|county|município',
                    r'seal|carimbo|stamp'
                ],
                'negative_patterns': [
                    r'passport|marriage|diploma|employment'
                ],
                'file_patterns': [
                    r'birth.*\.(pdf|jpg|jpeg|png)',
                    r'cert.*nasc.*\.(pdf|jpg|jpeg|png)',
                    r'nascimento.*\.(pdf|jpg|jpeg|png)'
                ],
                'weight': {
                    'required': 0.7,
                    'optional': 0.2,
                    'negative': -0.3,
                    'filename': 0.1
                }
            },
            
            'MARRIAGE_CERT': {
                'required_patterns': [
                    r'marriage certificate|certidão de casamento|certificate of marriage',
                    r'married|casamento|casado|casada',
                    r'spouse|cônjuge|husband|wife|marido|esposa'
                ],
                'optional_patterns': [
                    r'wedding|matrimony|matrimônio',
                    r'ceremony|cerimônia',
                    r'witnesses|testemunhas'
                ],
                'negative_patterns': [
                    r'birth|passport|employment|diploma'
                ],
                'file_patterns': [
                    r'marriage.*\.(pdf|jpg|jpeg|png)',
                    r'casamento.*\.(pdf|jpg|jpeg|png)',
                    r'cert.*marriage.*\.(pdf|jpg|jpeg|png)'
                ],
                'weight': {
                    'required': 0.7,
                    'optional': 0.2,
                    'negative': -0.3,
                    'filename': 0.1
                }
            },
            
            'DEGREE_CERTIFICATE': {
                'required_patterns': [
                    r'bachelor|master|doctorate|diploma|degree',
                    r'university|universidade|college|faculdade',
                    r'graduated|formado|formada|conclusão'
                ],
                'optional_patterns': [
                    r'cum laude|honors|honras',
                    r'transcript|histórico',
                    r'academic|acadêmic',
                    r'registrar|secretaria'
                ],
                'negative_patterns': [
                    r'passport|birth|marriage|employment'
                ],
                'file_patterns': [
                    r'diploma.*\.(pdf|jpg|jpeg|png)',
                    r'degree.*\.(pdf|jpg|jpeg|png)',
                    r'university.*\.(pdf|jpg|jpeg|png)'
                ],
                'weight': {
                    'required': 0.6,
                    'optional': 0.3,
                    'negative': -0.3,
                    'filename': 0.1
                }
            },
            
            'EMPLOYMENT_OFFER_LETTER': {
                'required_patterns': [
                    r'employment|job offer|offer of employment',
                    r'salary|compensation|wage|remuneração',
                    r'position|cargo|job title'
                ],
                'optional_patterns': [
                    r'start date|data de início',
                    r'benefits|benefícios',
                    r'company|empresa|corporation',
                    r'letterhead|papel timbrado'
                ],
                'negative_patterns': [
                    r'passport|birth|marriage|degree'
                ],
                'file_patterns': [
                    r'offer.*\.(pdf|jpg|jpeg|png)',
                    r'employment.*\.(pdf|jpg|jpeg|png)',
                    r'job.*letter.*\.(pdf|jpg|jpeg|png)'
                ],
                'weight': {
                    'required': 0.6,
                    'optional': 0.3,
                    'negative': -0.3,
                    'filename': 0.1
                }
            },
            
            'I797_NOTICE': {
                'required_patterns': [
                    r'i-?797|form i-797',
                    r'uscis|u\.s\. citizenship and immigration services',
                    r'receipt number|case number',
                    r'[A-Z]{3}\d{10}'  # USCIS receipt pattern
                ],
                'optional_patterns': [
                    r'petitioner|beneficiary',
                    r'approval|receipt|notice',
                    r'priority date|data de prioridade',
                    r'h-?1b|l-?1|o-?1'
                ],
                'negative_patterns': [
                    r'passport|birth|marriage|degree|employment offer'
                ],
                'file_patterns': [
                    r'i?797.*\.(pdf|jpg|jpeg|png)',
                    r'uscis.*\.(pdf|jpg|jpeg|png)',
                    r'receipt.*\.(pdf|jpg|jpeg|png)'
                ],
                'weight': {
                    'required': 0.8,
                    'optional': 0.1,
                    'negative': -0.2,
                    'filename': 0.1
                }
            },
            
            'I94_RECORD': {
                'required_patterns': [
                    r'i-?94|form i-94',
                    r'arrival.*record|registro de entrada',
                    r'admission|admissão|admitted',
                    r'class of admission|classe de admissão'
                ],
                'optional_patterns': [
                    r'cbp|customs and border protection',
                    r'port of entry|porto de entrada',
                    r'duration|duração|d/s',
                    r'hasta|until|até'
                ],
                'negative_patterns': [
                    r'passport|birth|marriage|degree'
                ],
                'file_patterns': [
                    r'i?94.*\.(pdf|jpg|jpeg|png)',
                    r'arrival.*\.(pdf|jpg|jpeg|png)',
                    r'entry.*record.*\.(pdf|jpg|jpeg|png)'
                ],
                'weight': {
                    'required': 0.7,
                    'optional': 0.2,
                    'negative': -0.3,
                    'filename': 0.1
                }
            },
            
            'PAY_STUB': {
                'required_patterns': [
                    r'pay stub|pay slip|holerite|contracheque',
                    r'gross pay|salário bruto|net pay|salário líquido',
                    r'employer|empregador|company'
                ],
                'optional_patterns': [
                    r'deductions|deduções|taxes|impostos',
                    r'year to date|ytd',
                    r'federal|state|fica',
                    r'hours|horas|overtime'
                ],
                'negative_patterns': [
                    r'passport|birth|marriage|degree'
                ],
                'file_patterns': [
                    r'pay.*stub.*\.(pdf|jpg|jpeg|png)',
                    r'salary.*\.(pdf|jpg|jpeg|png)',
                    r'payroll.*\.(pdf|jpg|jpeg|png)'
                ],
                'weight': {
                    'required': 0.7,
                    'optional': 0.2,
                    'negative': -0.3,
                    'filename': 0.1
                }
            },
            
            'TAX_RETURN_1040': {
                'required_patterns': [
                    r'form 1040|1040.*form',
                    r'u\.?s\.? individual income tax return',
                    r'irs|internal revenue service',
                    r'adjusted gross income|agi'
                ],
                'optional_patterns': [
                    r'w-?2|1099',
                    r'filing status|estado civil',
                    r'refund|reembolso|owed|devido',
                    r'social security|ssn'
                ],
                'negative_patterns': [
                    r'passport|birth|marriage|degree'
                ],
                'file_patterns': [
                    r'1040.*\.(pdf|jpg|jpeg|png)',
                    r'tax.*return.*\.(pdf|jpg|jpeg|png)',
                    r'irs.*\.(pdf|jpg|jpeg|png)'
                ],
                'weight': {
                    'required': 0.8,
                    'optional': 0.1,
                    'negative': -0.2,
                    'filename': 0.1
                }
            }
        }
    
    def _initialize_document_signatures(self) -> Dict[str, List[str]]:
        """
        Assinaturas únicas para identificação rápida de documentos
        """
        return {
            'PASSPORT_ID_PAGE': ['P<', 'MRZ', 'Machine Readable Zone'],
            'I797_NOTICE': ['I-797', 'USCIS', 'Receipt Number'],
            'I94_RECORD': ['I-94', 'CBP', 'Class of Admission'],
            'TAX_RETURN_1040': ['Form 1040', 'IRS', 'Department of Treasury'],
            'BIRTH_CERTIFICATE': ['Birth Certificate', 'Registry', 'Vital Records'],
            'MARRIAGE_CERT': ['Marriage Certificate', 'Civil Registry'],
            'DEGREE_CERTIFICATE': ['Diploma', 'University', 'Bachelor', 'Master'],
            'EMPLOYMENT_OFFER_LETTER': ['Job Offer', 'Employment', 'Compensation'],
            'PAY_STUB': ['Pay Stub', 'Payroll', 'Gross Pay']
        }
    
    def _initialize_confidence_thresholds(self) -> Dict[str, float]:
        """
        Define thresholds de confiança para classificação
        """
        return {
            'high_confidence': 0.80,
            'medium_confidence': 0.65,
            'low_confidence': 0.45,
            'ambiguous': 0.30
        }
    
    def classify_document(self, 
                         text_content: str, 
                         filename: str = '',
                         file_size: int = 0) -> Dict[str, Any]:
        """
        Classifica documento baseado no conteúdo e metadados
        
        Args:
            text_content: Texto extraído do documento
            filename: Nome do arquivo original
            file_size: Tamanho do arquivo em bytes
            
        Returns:
            Resultado da classificação com tipo detectado e confiança
        """
        try:
            if not text_content or len(text_content.strip()) < 20:
                return {
                    'document_type': 'UNKNOWN',
                    'confidence': 0.0,
                    'status': 'insufficient_content',
                    'message': 'Insufficient text content for classification',
                    'candidates': []
                }
            
            # 1. Verificação rápida por assinaturas únicas
            signature_result = self._check_document_signatures(text_content)
            
            # 2. Análise detalhada por padrões
            pattern_results = self._analyze_all_patterns(text_content, filename)
            
            # 3. Combinar resultados
            combined_results = self._combine_classification_results(
                signature_result, pattern_results
            )
            
            # 4. Determinar classificação final
            final_classification = self._determine_final_classification(combined_results)
            
            # 5. Adicionar metadados e validações
            result = self._enrich_classification_result(
                final_classification, text_content, filename, file_size
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in document classification: {e}")
            return {
                'document_type': 'ERROR',
                'confidence': 0.0,
                'status': 'error',
                'message': f'Classification error: {str(e)}',
                'candidates': []
            }
    
    def _check_document_signatures(self, text: str) -> Dict[str, float]:
        """
        Verifica assinaturas únicas para identificação rápida
        """
        signature_scores = {}
        text_lower = text.lower()
        
        for doc_type, signatures in self.document_signatures.items():
            score = 0.0
            matches = 0
            
            for signature in signatures:
                if signature.lower() in text_lower:
                    matches += 1
                    score += 1.0 / len(signatures)
            
            # Bonus para múltiplas assinaturas
            if matches > 1:
                score *= (1 + (matches - 1) * 0.2)
            
            signature_scores[doc_type] = min(score, 1.0)
        
        return signature_scores
    
    def _analyze_all_patterns(self, text: str, filename: str) -> Dict[str, Dict]:
        """
        Analisa todos os padrões de classificação
        """
        results = {}
        
        for doc_type, patterns in self.classification_patterns.items():
            score = self._calculate_pattern_score(text, filename, patterns)
            
            results[doc_type] = {
                'score': score,
                'matches': self._get_pattern_matches(text, filename, patterns),
                'confidence': min(max(score, 0.0), 1.0)
            }
        
        return results
    
    def _calculate_pattern_score(self, text: str, filename: str, patterns: Dict) -> float:
        """
        Calcula score baseado em padrões específicos de um tipo de documento
        """
        text_lower = text.lower()
        filename_lower = filename.lower()
        
        score = 0.0
        weights = patterns['weight']
        
        # 1. Padrões obrigatórios
        required_patterns = patterns.get('required_patterns', [])
        if required_patterns:
            required_matches = sum(
                1 for pattern in required_patterns 
                if re.search(pattern, text_lower, re.IGNORECASE)
            )
            required_score = required_matches / len(required_patterns)
            score += required_score * weights['required']
        
        # 2. Padrões opcionais
        optional_patterns = patterns.get('optional_patterns', [])
        if optional_patterns:
            optional_matches = sum(
                1 for pattern in optional_patterns 
                if re.search(pattern, text_lower, re.IGNORECASE)
            )
            optional_score = min(optional_matches / len(optional_patterns), 1.0)
            score += optional_score * weights['optional']
        
        # 3. Padrões negativos (reduzem score)
        negative_patterns = patterns.get('negative_patterns', [])
        if negative_patterns:
            negative_matches = sum(
                1 for pattern in negative_patterns 
                if re.search(pattern, text_lower, re.IGNORECASE)
            )
            negative_score = negative_matches / len(negative_patterns)
            score += negative_score * weights['negative']  # negative weight
        
        # 4. Padrões de nome de arquivo
        file_patterns = patterns.get('file_patterns', [])
        if file_patterns and filename:
            file_matches = sum(
                1 for pattern in file_patterns 
                if re.search(pattern, filename_lower, re.IGNORECASE)
            )
            if file_matches > 0:
                score += weights['filename']
        
        return score
    
    def _get_pattern_matches(self, text: str, filename: str, patterns: Dict) -> Dict[str, List[str]]:
        """
        Obtém matches específicos para análise detalhada
        """
        text_lower = text.lower()
        filename_lower = filename.lower()
        
        matches = {
            'required': [],
            'optional': [],
            'negative': [],
            'filename': []
        }
        
        # Verificar cada tipo de padrão
        for pattern_type in ['required_patterns', 'optional_patterns', 'negative_patterns']:
            if pattern_type in patterns:
                key = pattern_type.split('_')[0]
                for pattern in patterns[pattern_type]:
                    match = re.search(pattern, text_lower, re.IGNORECASE)
                    if match:
                        matches[key].append(match.group())
        
        # Verificar padrões de filename
        if 'file_patterns' in patterns and filename:
            for pattern in patterns['file_patterns']:
                match = re.search(pattern, filename_lower, re.IGNORECASE)
                if match:
                    matches['filename'].append(match.group())
        
        return matches
    
    def _combine_classification_results(self, 
                                      signature_scores: Dict[str, float],
                                      pattern_results: Dict[str, Dict]) -> Dict[str, Dict]:
        """
        Combina resultados de assinaturas e padrões
        """
        combined = {}
        
        all_doc_types = set(signature_scores.keys()).union(set(pattern_results.keys()))
        
        for doc_type in all_doc_types:
            signature_score = signature_scores.get(doc_type, 0.0)
            pattern_data = pattern_results.get(doc_type, {'score': 0.0, 'confidence': 0.0})
            pattern_score = pattern_data['score']
            
            # Combinação ponderada: assinaturas têm peso maior para identificação rápida
            if signature_score > 0.7:
                final_score = signature_score * 0.7 + pattern_score * 0.3
            else:
                final_score = signature_score * 0.4 + pattern_score * 0.6
            
            combined[doc_type] = {
                'signature_score': signature_score,
                'pattern_score': pattern_score,
                'combined_score': final_score,
                'matches': pattern_data.get('matches', {}),
                'confidence': min(max(final_score, 0.0), 1.0)
            }
        
        return combined
    
    def _determine_final_classification(self, combined_results: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Determina a classificação final baseada nos scores combinados
        """
        if not combined_results:
            return {
                'document_type': 'UNKNOWN',
                'confidence': 0.0,
                'status': 'no_matches'
            }
        
        # Ordenar por score combinado
        sorted_results = sorted(
            combined_results.items(), 
            key=lambda x: x[1]['combined_score'], 
            reverse=True
        )
        
        best_match = sorted_results[0]
        best_doc_type, best_data = best_match
        best_score = best_data['combined_score']
        
        # Determinar status baseado na confiança
        thresholds = self.confidence_thresholds
        
        if best_score >= thresholds['high_confidence']:
            status = 'high_confidence'
        elif best_score >= thresholds['medium_confidence']:
            status = 'medium_confidence'
        elif best_score >= thresholds['low_confidence']:
            status = 'low_confidence'
        else:
            status = 'ambiguous'
        
        # Verificar se há empate entre candidatos
        candidates = []
        for doc_type, data in sorted_results[:3]:  # Top 3 candidatos
            candidates.append({
                'document_type': doc_type,
                'confidence': data['confidence'],
                'score': data['combined_score'],
                'matches': data['matches']
            })
        
        # Detectar empate
        if len(sorted_results) > 1:
            second_best_score = sorted_results[1][1]['combined_score']
            if best_score - second_best_score < 0.15:  # Diferença pequena
                status = 'ambiguous_multiple_candidates'
        
        return {
            'document_type': best_doc_type,
            'confidence': best_data['confidence'],
            'score': best_score,
            'status': status,
            'candidates': candidates,
            'matches': best_data['matches']
        }
    
    def _enrich_classification_result(self, 
                                    classification: Dict[str, Any],
                                    text_content: str,
                                    filename: str,
                                    file_size: int) -> Dict[str, Any]:
        """
        Enriquece resultado da classificação com informações adicionais
        """
        result = classification.copy()
        
        # Adicionar metadados
        result['metadata'] = {
            'filename': filename,
            'file_size': file_size,
            'text_length': len(text_content),
            'word_count': len(text_content.split()) if text_content else 0
        }
        
        # Adicionar sugestões baseadas no tipo detectado
        result['suggestions'] = self._generate_classification_suggestions(
            classification['document_type'], 
            classification['confidence'],
            classification.get('status', 'unknown')
        )
        
        # Adicionar validações específicas do tipo de documento
        result['validation_hints'] = self._get_document_validation_hints(
            classification['document_type']
        )
        
        return result
    
    def _generate_classification_suggestions(self, 
                                          doc_type: str, 
                                          confidence: float,
                                          status: str) -> List[Dict[str, str]]:
        """
        Gera sugestões baseadas na classificação
        """
        suggestions = []
        
        if status == 'high_confidence':
            suggestions.append({
                'type': 'success',
                'message': f'Document successfully classified as {doc_type} with high confidence'
            })
        elif status == 'medium_confidence':
            suggestions.append({
                'type': 'warning',
                'message': f'Document classified as {doc_type} with medium confidence - please verify'
            })
        elif status in ['low_confidence', 'ambiguous', 'ambiguous_multiple_candidates']:
            suggestions.append({
                'type': 'alert',
                'message': 'Classification confidence is low - manual verification recommended'
            })
            suggestions.append({
                'type': 'action',
                'message': 'Consider improving image quality or providing additional context'
            })
        
        # Sugestões específicas por tipo de documento
        if doc_type == 'PASSPORT_ID_PAGE':
            suggestions.append({
                'type': 'info',
                'message': 'Ensure MRZ (Machine Readable Zone) is clearly visible'
            })
        elif doc_type == 'I797_NOTICE':
            suggestions.append({
                'type': 'info',
                'message': 'Verify receipt number format (3 letters + 10 digits)'
            })
        
        return suggestions
    
    def _get_document_validation_hints(self, doc_type: str) -> List[str]:
        """
        Retorna dicas de validação específicas para o tipo de documento
        """
        hints = {
            'PASSPORT_ID_PAGE': [
                'Check MRZ consistency with printed information',
                'Verify passport number format matches issuing country',
                'Ensure expiry date is clearly visible'
            ],
            'BIRTH_CERTIFICATE': [
                'Verify official seal or stamp is present',
                'Check for registrar signature',
                'Ensure document is recent (not older than 6 months for some purposes)'
            ],
            'I797_NOTICE': [
                'Verify USCIS receipt number format',
                'Check that beneficiary and petitioner names match other documents',
                'Ensure notice type matches the petition'
            ],
            'EMPLOYMENT_OFFER_LETTER': [
                'Verify letter is on company letterhead',
                'Check for authorized signatory',
                'Ensure job details match I-797 petition if available'
            ]
        }
        
        return hints.get(doc_type, ['Verify document authenticity and completeness'])
    
    def classify_multiple_documents(self, documents_data: List[Dict]) -> Dict[str, Any]:
        """
        Classifica múltiplos documentos e identifica possíveis duplicatas
        """
        classifications = []
        doc_type_counts = Counter()
        
        for i, doc_data in enumerate(documents_data):
            text = doc_data.get('text_content', '')
            filename = doc_data.get('filename', f'document_{i}')
            file_size = doc_data.get('file_size', 0)
            
            classification = self.classify_document(text, filename, file_size)
            classification['index'] = i
            classifications.append(classification)
            
            doc_type_counts[classification['document_type']] += 1
        
        # Identificar duplicatas possíveis
        potential_duplicates = [doc_type for doc_type, count in doc_type_counts.items() if count > 1]
        
        # Calcular estatísticas gerais
        high_confidence_count = sum(1 for c in classifications if c.get('confidence', 0) >= 0.80)
        low_confidence_count = sum(1 for c in classifications if c.get('confidence', 0) < 0.50)
        
        return {
            'total_documents': len(documents_data),
            'classifications': classifications,
            'document_type_counts': dict(doc_type_counts),
            'potential_duplicates': potential_duplicates,
            'statistics': {
                'high_confidence': high_confidence_count,
                'low_confidence': low_confidence_count,
                'success_rate': high_confidence_count / len(documents_data) if documents_data else 0
            }
        }

# Instância global do classificador
document_classifier = DocumentClassifier()