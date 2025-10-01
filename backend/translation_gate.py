"""
Translation Gate System - Phase 2
Sistema avançado de detecção de idioma e enforcement de requisitos de tradução
"""
import re
from typing import Dict, List, Any, Optional, Tuple
import logging
from collections import Counter

logger = logging.getLogger(__name__)

class TranslationGate:
    """
    Sistema de controle de tradução para documentos de imigração
    """
    
    def __init__(self):
        self.language_patterns = self._initialize_language_patterns()
        self.translation_rules = self._initialize_translation_rules()
        self.english_requirements = self._initialize_english_requirements()
    
    def _initialize_language_patterns(self) -> Dict[str, Dict]:
        """
        Inicializa padrões para detecção de idiomas
        """
        return {
            'english': {
                'common_words': [
                    'the', 'and', 'of', 'to', 'in', 'is', 'was', 'for', 'with', 'on',
                    'as', 'are', 'by', 'at', 'this', 'that', 'from', 'have', 'has',
                    'will', 'be', 'an', 'or', 'been', 'his', 'her', 'their', 'our'
                ],
                'government_terms': [
                    'united states', 'department', 'citizenship', 'immigration',
                    'services', 'form', 'petition', 'application', 'notice',
                    'receipt', 'approval', 'beneficiary', 'petitioner'
                ],
                'patterns': [
                    r'\b(?:born|birth)\s+(?:in|on)\b',
                    r'\b(?:expires?|expiry)\s+(?:on|date)\b',
                    r'\b(?:issued|issue)\s+(?:on|date)\b',
                    r'\b(?:valid|validity)\s+(?:from|until)\b'
                ]
            },
            'portuguese': {
                'common_words': [
                    'de', 'da', 'do', 'em', 'para', 'com', 'por', 'uma', 'um',
                    'na', 'no', 'dos', 'das', 'que', 'não', 'ou', 'se', 'mas',
                    'como', 'quando', 'onde', 'pelo', 'pela', 'sua', 'seu'
                ],
                'government_terms': [
                    'república federativa', 'brasil', 'ministério', 'secretaria',
                    'estado', 'governo', 'passaporte', 'documento', 'identidade',
                    'certidão', 'nascimento', 'casamento', 'óbito'
                ],
                'patterns': [
                    r'\b(?:nascido|nascimento)\s+(?:em|no)\b',
                    r'\b(?:expira|vencimento)\s+(?:em|no)\b',
                    r'\b(?:emitido|emissão)\s+(?:em|no)\b',
                    r'\bválido\s+(?:até|para)\b'
                ]
            },
            'spanish': {
                'common_words': [
                    'de', 'la', 'el', 'en', 'para', 'con', 'por', 'una', 'un',
                    'del', 'los', 'las', 'que', 'no', 'o', 'si', 'pero',
                    'como', 'cuando', 'donde', 'por', 'su', 'sus'
                ],
                'government_terms': [
                    'república', 'gobierno', 'ministerio', 'secretaría',
                    'estado', 'pasaporte', 'documento', 'identidad',
                    'certificado', 'nacimiento', 'matrimonio', 'defunción'
                ],
                'patterns': [
                    r'\b(?:nacido|nacimiento)\s+(?:en|el)\b',
                    r'\b(?:expira|vencimiento)\s+(?:en|el)\b',
                    r'\b(?:emitido|emisión)\s+(?:en|el)\b',
                    r'\bválido\s+(?:hasta|para)\b'
                ]
            }
        }
    
    def _initialize_translation_rules(self) -> Dict[str, Dict]:
        """
        Inicializa regras de tradução por tipo de documento
        """
        return {
            'PASSPORT_ID_PAGE': {
                'rule': 'CFR_103_2_b_3',
                'english_required': False,  # Passaportes podem ter idioma nativo
                'certified_translation_required': True,
                'acceptable_languages': ['en'],
                'exceptions': ['mrz_section'],  # MRZ é sempre em formato padrão
                'description': '8 CFR 103.2(b)(3) - Foreign language documents must be accompanied by certified English translation'
            },
            'BIRTH_CERTIFICATE': {
                'rule': 'CFR_103_2_b_3',
                'english_required': False,
                'certified_translation_required': True,
                'acceptable_languages': ['en'],
                'exceptions': [],
                'description': 'Birth certificates in foreign languages require certified translation'
            },
            'MARRIAGE_CERT': {
                'rule': 'CFR_103_2_b_3',
                'english_required': False,
                'certified_translation_required': True,
                'acceptable_languages': ['en'],
                'exceptions': [],
                'description': 'Marriage certificates in foreign languages require certified translation'
            },
            'DEGREE_CERTIFICATE': {
                'rule': 'CFR_103_2_b_3',
                'english_required': False,
                'certified_translation_required': True,
                'acceptable_languages': ['en'],
                'exceptions': [],
                'description': 'Educational documents in foreign languages require certified translation'
            },
            'EMPLOYMENT_OFFER_LETTER': {
                'rule': 'BUSINESS_ENGLISH',
                'english_required': True,
                'certified_translation_required': False,
                'acceptable_languages': ['en'],
                'exceptions': [],
                'description': 'Employment letters must be in English as they are created by US employers'
            },
            'I797_NOTICE': {
                'rule': 'USCIS_OFFICIAL',
                'english_required': True,
                'certified_translation_required': False,
                'acceptable_languages': ['en'],
                'exceptions': [],
                'description': 'USCIS notices are always issued in English'
            },
            'TAX_RETURN_1040': {
                'rule': 'IRS_OFFICIAL',
                'english_required': True,
                'certified_translation_required': False,
                'acceptable_languages': ['en'],
                'exceptions': [],
                'description': 'US tax returns are filed in English'
            }
        }
    
    def _initialize_english_requirements(self) -> Dict[str, float]:
        """
        Define thresholds para diferentes tipos de requirement de inglês
        """
        return {
            'strict_english_only': 0.90,      # Documentos que DEVEM estar em inglês
            'english_or_translation': 0.60,   # Pode estar em idioma estrangeiro com tradução
            'minimal_english': 0.30,          # Alguns elementos em inglês são suficientes
            'no_requirement': 0.0             # Sem requirement de inglês
        }
    
    def analyze_document_language(self, 
                                 text: str, 
                                 document_type: str,
                                 filename: str = '') -> Dict[str, Any]:
        """
        Analisa idioma do documento e determina requirements de tradução
        """
        try:
            # 1. Detectar idiomas presentes
            language_scores = self._detect_languages(text)
            
            # 2. Obter regras para o tipo de documento
            translation_rule = self.translation_rules.get(document_type, {})
            
            # 3. Analisar compliance
            compliance_result = self._analyze_compliance(
                language_scores, translation_rule, document_type
            )
            
            # 4. Gerar recomendações
            recommendations = self._generate_recommendations(
                language_scores, translation_rule, compliance_result, filename
            )
            
            result = {
                'document_type': document_type,
                'language_detection': language_scores,
                'translation_rule': translation_rule,
                'compliance': compliance_result,
                'recommendations': recommendations,
                'status': compliance_result.get('status', 'unknown'),
                'requires_action': compliance_result.get('requires_translation', False)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in language analysis: {e}")
            return {
                'document_type': document_type,
                'language_detection': {},
                'translation_rule': {},
                'compliance': {'status': 'error', 'message': str(e)},
                'recommendations': [],
                'status': 'error',
                'requires_action': False
            }
    
    def _detect_languages(self, text: str) -> Dict[str, Any]:
        """
        Detecta idiomas presentes no texto
        """
        if not text or len(text.strip()) < 50:
            return {
                'primary_language': 'unknown',
                'confidence': 0.0,
                'language_scores': {},
                'mixed_language': False,
                'text_length': len(text) if text else 0
            }
        
        text_clean = re.sub(r'[^\w\s]', ' ', text.lower())
        words = text_clean.split()
        
        if len(words) < 10:
            return {
                'primary_language': 'insufficient_text',
                'confidence': 0.0,
                'language_scores': {},
                'mixed_language': False,
                'text_length': len(words)
            }
        
        language_scores = {}
        
        # Calcular scores para cada idioma
        for lang_code, lang_config in self.language_patterns.items():
            score = self._calculate_language_score(text_clean, words, lang_config)
            language_scores[lang_code] = score
        
        # Determinar idioma primário
        primary_language = max(language_scores.keys(), key=lambda k: language_scores[k])
        primary_score = language_scores[primary_language]
        
        # Detectar se é texto misto
        second_highest = sorted(language_scores.values(), reverse=True)[1] if len(language_scores) > 1 else 0
        mixed_language = (primary_score - second_highest) < 0.3
        
        return {
            'primary_language': primary_language if primary_score > 0.2 else 'unknown',
            'confidence': primary_score,
            'language_scores': language_scores,
            'mixed_language': mixed_language,
            'text_length': len(words)
        }
    
    def _calculate_language_score(self, 
                                 text_clean: str, 
                                 words: List[str], 
                                 lang_config: Dict) -> float:
        """
        Calcula score de probabilidade para um idioma específico
        """
        total_score = 0.0
        
        # 1. Score baseado em palavras comuns
        common_words = lang_config.get('common_words', [])
        common_matches = sum(1 for word in words if word in common_words)
        common_score = min(common_matches / len(words), 0.5)
        total_score += common_score * 0.4
        
        # 2. Score baseado em termos governamentais/oficiais
        gov_terms = lang_config.get('government_terms', [])
        gov_matches = sum(1 for term in gov_terms if term in text_clean)
        gov_score = min(gov_matches / max(len(gov_terms), 1) * 2, 0.4)
        total_score += gov_score * 0.3
        
        # 3. Score baseado em padrões regex
        patterns = lang_config.get('patterns', [])
        pattern_matches = 0
        for pattern in patterns:
            if re.search(pattern, text_clean, re.IGNORECASE):
                pattern_matches += 1
        pattern_score = min(pattern_matches / max(len(patterns), 1), 0.3)
        total_score += pattern_score * 0.3
        
        return min(total_score, 1.0)
    
    def _analyze_compliance(self, 
                           language_scores: Dict[str, Any], 
                           translation_rule: Dict[str, Any],
                           document_type: str) -> Dict[str, Any]:
        """
        Analisa compliance com regras de tradução
        """
        primary_language = language_scores.get('primary_language', 'unknown')
        confidence = language_scores.get('confidence', 0.0)
        
        # Regras default se não há configuração específica
        if not translation_rule:
            return {
                'status': 'no_rule',
                'compliant': True,
                'requires_translation': False,
                'message': 'No translation rule defined for this document type'
            }
        
        english_required = translation_rule.get('english_required', False)
        cert_translation_required = translation_rule.get('certified_translation_required', False)
        acceptable_languages = translation_rule.get('acceptable_languages', ['en'])
        
        # Analisar compliance
        if english_required:
            # Documento DEVE estar em inglês
            if primary_language == 'english' and confidence > 0.7:
                return {
                    'status': 'compliant',
                    'compliant': True,
                    'requires_translation': False,
                    'message': 'Document is in English as required'
                }
            else:
                return {
                    'status': 'non_compliant',
                    'compliant': False,
                    'requires_translation': True,
                    'message': f'Document must be in English but appears to be in {primary_language}',
                    'severity': 'critical'
                }
        
        elif cert_translation_required:
            # Documento pode estar em idioma estrangeiro, mas precisa de tradução certificada
            if primary_language in acceptable_languages and confidence > 0.6:
                return {
                    'status': 'compliant',
                    'compliant': True,
                    'requires_translation': False,
                    'message': 'Document is in acceptable language'
                }
            else:
                return {
                    'status': 'requires_translation',
                    'compliant': False,
                    'requires_translation': True,
                    'message': f'Document in {primary_language} requires certified English translation',
                    'severity': 'high',
                    'rule_reference': translation_rule.get('rule', 'CFR_103_2_b_3')
                }
        
        else:
            # Sem requirements específicos de idioma
            return {
                'status': 'compliant',
                'compliant': True,
                'requires_translation': False,
                'message': 'No language requirements for this document type'
            }
    
    def _generate_recommendations(self, 
                                language_scores: Dict[str, Any],
                                translation_rule: Dict[str, Any],
                                compliance_result: Dict[str, Any],
                                filename: str) -> List[Dict[str, Any]]:
        """
        Gera recomendações específicas baseadas na análise
        """
        recommendations = []
        
        if not compliance_result.get('compliant', True):
            severity = compliance_result.get('severity', 'medium')
            
            if compliance_result.get('requires_translation', False):
                rec = {
                    'type': 'translation_required',
                    'severity': severity,
                    'title': 'Certified Translation Required',
                    'description': compliance_result.get('message', ''),
                    'actions': [
                        'Obtain certified English translation from qualified translator',
                        'Ensure translator provides certificate of accuracy',
                        'Submit both original document and certified translation'
                    ]
                }
                
                # Adicionar informação sobre regra específica
                rule_ref = compliance_result.get('rule_reference')
                if rule_ref:
                    rec['rule_reference'] = rule_ref
                    rec['actions'].append(f'Translation must comply with {rule_ref}')
                
                recommendations.append(rec)
        
        # Recomendações de qualidade
        primary_language = language_scores.get('primary_language', 'unknown')
        confidence = language_scores.get('confidence', 0.0)
        
        if confidence < 0.5:
            recommendations.append({
                'type': 'quality_improvement',
                'severity': 'medium',
                'title': 'Document Quality Issue',
                'description': 'Text extraction confidence is low - document may be unclear',
                'actions': [
                    'Ensure document is high resolution and clearly legible',
                    'Check for proper scanning/photo quality',
                    'Consider re-scanning if text appears blurry'
                ]
            })
        
        # Recomendações específicas por idioma
        if primary_language == 'portuguese' and translation_rule.get('certified_translation_required'):
            recommendations.append({
                'type': 'brazilian_specific',
                'severity': 'info',
                'title': 'Brazilian Document Detected',
                'description': 'Document appears to be in Portuguese',
                'actions': [
                    'Use certified translator familiar with Brazilian documents',
                    'Ensure all stamps and official marks are translated',
                    'Consider apostille requirements if applicable'
                ]
            })
        
        return recommendations
    
    def check_translation_certificate(self, text: str) -> Dict[str, Any]:
        """
        Verifica se o documento contém certificado de tradução
        """
        translation_indicators = [
            r'certified translation',
            r'certificate of translation',
            r'i certify that',
            r'translator.*certif',
            r'sworn translator',
            r'tradutor.*juramentado',
            r'tradução.*certificada'
        ]
        
        found_indicators = []
        for pattern in translation_indicators:
            if re.search(pattern, text, re.IGNORECASE):
                found_indicators.append(pattern)
        
        has_certificate = len(found_indicators) > 0
        
        return {
            'has_translation_certificate': has_certificate,
            'indicators_found': found_indicators,
            'confidence': min(len(found_indicators) * 0.3, 1.0) if has_certificate else 0.0,
            'status': 'found' if has_certificate else 'not_found'
        }
    
    def get_translation_requirements(self, document_type: str) -> Dict[str, Any]:
        """
        Retorna requirements de tradução para um tipo de documento
        """
        rule = self.translation_rules.get(document_type, {})
        
        return {
            'document_type': document_type,
            'english_required': rule.get('english_required', False),
            'certified_translation_required': rule.get('certified_translation_required', False),
            'acceptable_languages': rule.get('acceptable_languages', ['en']),
            'rule_reference': rule.get('rule', 'No specific rule'),
            'description': rule.get('description', 'No description available'),
            'exceptions': rule.get('exceptions', [])
        }

# Instância global do translation gate
translation_gate = TranslationGate()