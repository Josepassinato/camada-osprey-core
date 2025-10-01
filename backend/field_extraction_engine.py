"""
Enhanced Field Extraction Engine - Phase 2
Sistema avançado de extração de campos usando regex aprimorado e validadores de alta precisão
"""
import re
from typing import Dict, List, Any, Optional, Tuple
import logging
from validators import (
    normalize_date, 
    parse_mrz_td3, 
    is_valid_uscis_receipt,
    is_plausible_ssn,
    validate_passport_number_with_nationality,
    validate_date_with_context,
    extract_and_validate_mrz,
    enhance_field_validation
)

logger = logging.getLogger(__name__)

class FieldExtractionEngine:
    """
    Motor avançado de extração de campos com validação de alta precisão
    """
    
    def __init__(self):
        self.extraction_patterns = self._initialize_patterns()
        self.field_validators = self._initialize_validators()
    
    def _initialize_patterns(self) -> Dict[str, Dict]:
        """
        Inicializa padrões regex aprimorados para extração de campos
        """
        return {
            # Padrões para passaporte
            'passport_number': {
                'patterns': [
                    r'\b(?:Passport\s*(?:No|Number)|Pasaporte\s*(?:No|Número))[:\s]*([A-Z0-9]{6,12})\b',
                    r'\b([A-Z]{1,2}\d{6,10})\b',  # Padrão brasileiro: AB123456
                    r'\b(\d{9})\b',  # Padrão americano: 123456789
                    r'\b([A-Z0-9]{6,12})\b'  # Padrão genérico
                ],
                'confidence_weights': [0.95, 0.90, 0.90, 0.70],
                'context_keywords': ['passport', 'pasaporte', 'documento', 'identity']
            },
            
            # Padrões para datas aprimorados
            'date_fields': {
                'patterns': [
                    # Formato completo com contexto
                    r'(?:Born|Birth|DOB|Data\s*de\s*Nascimento)[:\s]*(\d{1,2}[\/\.-]\d{1,2}[\/\.-]\d{4})',
                    r'(?:Expires?|Expiry|Expira)[:\s]*(\d{1,2}[\/\.-]\d{1,2}[\/\.-]\d{4})',
                    r'(?:Issue[d]?|Issued|Emitido)[:\s]*(\d{1,2}[\/\.-]\d{1,2}[\/\.-]\d{4})',
                    # Formatos ISO
                    r'(\d{4}-\d{2}-\d{2})',
                    # Formatos textuais
                    r'([A-Za-z]{3,9}\s+\d{1,2},?\s+\d{4})',  # Jan 15, 2023
                    # D/S para I-94
                    r'\b(D\/S)\b'
                ],
                'confidence_weights': [0.95, 0.95, 0.95, 0.90, 0.85, 1.0],
                'context_keywords': ['date', 'born', 'birth', 'expire', 'issue', 'valid']
            },
            
            # USCIS Receipt Numbers
            'uscis_receipt': {
                'patterns': [
                    r'\b(?:Receipt\s*(?:No|Number)|Case\s*(?:No|Number))[:\s]*([A-Z]{3}\d{10})\b',
                    r'\b([A-Z]{3}\d{10})\b'
                ],
                'confidence_weights': [0.98, 0.85],
                'context_keywords': ['receipt', 'case', 'uscis', 'notice']
            },
            
            # SSN patterns
            'ssn': {
                'patterns': [
                    r'\b(?:SSN|Social\s*Security)[:\s]*(\d{3}-\d{2}-\d{4})\b',
                    r'\b(\d{3}-\d{2}-\d{4})\b'
                ],
                'confidence_weights': [0.95, 0.80],
                'context_keywords': ['ssn', 'social', 'security']
            },
            
            # Nomes e entidades
            'name_fields': {
                'patterns': [
                    r'(?:Name|Nome|Surname|Apellido)[:\s]*([A-Z][a-zA-Z\s\-\']{2,50})',
                    r'(?:Given\s*Names?|First\s*Name)[:\s]*([A-Z][a-zA-Z\s\-\']{2,30})',
                    r'(?:Last\s*Name|Family\s*Name)[:\s]*([A-Z][a-zA-Z\s\-\']{2,30})'
                ],
                'confidence_weights': [0.90, 0.90, 0.90],
                'context_keywords': ['name', 'nome', 'surname', 'given']
            },
            
            # Endereços
            'address_fields': {
                'patterns': [
                    r'(?:Address|Endereço)[:\s]*([A-Za-z0-9\s\-\,\.]{10,100})',
                    r'(?:City|Cidade)[:\s]*([A-Za-z\s\-\']{2,30})',
                    r'(?:State|Estado)[:\s]*([A-Z]{2}|[A-Za-z\s]{2,30})',
                    r'(?:ZIP|Postal|CEP)[:\s]*(\d{5}(?:-\d{4})?|\d{8})'
                ],
                'confidence_weights': [0.85, 0.85, 0.85, 0.90],
                'context_keywords': ['address', 'city', 'state', 'zip', 'postal']
            },
            
            # Valores monetários
            'monetary_fields': {
                'patterns': [
                    r'(?:Salary|Salário|Wage|Amount)[:\s]*\$?([0-9,]+(?:\.\d{2})?)',
                    r'\$([0-9,]+(?:\.\d{2})?)',
                    r'([0-9,]+(?:\.\d{2})?\s*(?:USD|BRL|dollars?))'
                ],
                'confidence_weights': [0.90, 0.80, 0.85],
                'context_keywords': ['salary', 'wage', 'amount', 'payment', 'fee']
            }
        }
    
    def _initialize_validators(self) -> Dict[str, callable]:
        """
        Inicializa validadores específicos para tipos de campos
        """
        return {
            'passport_number': self._validate_passport_field,
            'date_fields': self._validate_date_field,
            'uscis_receipt': self._validate_uscis_receipt_field,
            'ssn': self._validate_ssn_field,
            'name_fields': self._validate_name_field,
            'address_fields': self._validate_address_field,
            'monetary_fields': self._validate_monetary_field
        }
    
    def extract_all_fields(self, 
                          text: str, 
                          policy_fields: List[Dict] = None,
                          context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Extrai todos os campos do texto usando padrões aprimorados
        """
        context = context or {}
        all_extractions = {}
        
        # 1. Extrair campos usando padrões genéricos
        for field_type, config in self.extraction_patterns.items():
            extractions = self._extract_field_type(text, field_type, config, context)
            if extractions:
                all_extractions[field_type] = extractions
        
        # 2. Extrair campos específicos da política (se fornecida)
        if policy_fields:
            policy_extractions = self._extract_policy_fields(text, policy_fields, context)
            all_extractions['policy_fields'] = policy_extractions
        
        # 3. Extrair MRZ se documento for passaporte
        mrz_data = extract_and_validate_mrz(text)
        if mrz_data:
            all_extractions['mrz'] = mrz_data
        
        return all_extractions
    
    def _extract_field_type(self, 
                           text: str, 
                           field_type: str, 
                           config: Dict, 
                           context: Dict) -> List[Dict]:
        """
        Extrai campos de um tipo específico
        """
        extractions = []
        patterns = config['patterns']
        weights = config['confidence_weights']
        keywords = config['context_keywords']
        
        # Verificar se há contexto relevante no texto
        context_score = self._calculate_context_score(text, keywords)
        
        for i, pattern in enumerate(patterns):
            try:
                matches = list(re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE))
                
                for match in matches:
                    extracted_value = match.group(1) if match.groups() else match.group()
                    
                    # Calcular posição e contexto
                    position_info = self._get_position_context(text, match)
                    
                    # Aplicar validador específico
                    validation_result = self._apply_field_validator(
                        field_type, extracted_value, context, position_info
                    )
                    
                    # Calcular confidence final
                    base_confidence = weights[i] if i < len(weights) else 0.5
                    final_confidence = (
                        base_confidence * 0.6 +
                        context_score * 0.2 +
                        validation_result['confidence'] * 0.2
                    )
                    
                    extraction = {
                        'value': extracted_value,
                        'normalized_value': validation_result.get('normalized_value', extracted_value),
                        'confidence': final_confidence,
                        'validation': validation_result,
                        'position': position_info,
                        'pattern_used': pattern,
                        'field_type': field_type
                    }
                    
                    extractions.append(extraction)
                    
            except re.error as e:
                logger.warning(f"Invalid regex pattern for {field_type}: {pattern} - {e}")
        
        # Ordenar por confidence e remover duplicatas
        extractions.sort(key=lambda x: x['confidence'], reverse=True)
        return self._remove_duplicates(extractions)
    
    def _extract_policy_fields(self, 
                              text: str, 
                              policy_fields: List[Dict], 
                              context: Dict) -> Dict[str, Any]:
        """
        Extrai campos específicos definidos na política
        """
        results = {}
        
        for field_def in policy_fields:
            field_name = field_def.get('name')
            field_regex = field_def.get('regex')
            field_description = field_def.get('description', '')
            is_required = field_def.get('required', True)
            
            if not field_name or not field_regex:
                continue
            
            try:
                # Aplicar regex da política
                matches = list(re.finditer(field_regex, text, re.IGNORECASE | re.MULTILINE))
                
                field_results = []
                for match in matches:
                    value = match.group(1) if match.groups() else match.group()
                    
                    # Usar validador avançado
                    enhanced_validation = enhance_field_validation(
                        field_name, value, context.get('document_type', ''), context
                    )
                    
                    position_info = self._get_position_context(text, match)
                    
                    field_result = {
                        'value': value,
                        'normalized_value': enhanced_validation.get('normalized_value', value),
                        'confidence': enhanced_validation.get('confidence', 0.5),
                        'validation': enhanced_validation,
                        'position': position_info,
                        'is_required': is_required,
                        'description': field_description
                    }
                    
                    field_results.append(field_result)
                
                results[field_name] = {
                    'found': len(field_results) > 0,
                    'values': field_results,
                    'required': is_required,
                    'best_match': field_results[0] if field_results else None
                }
                
            except re.error as e:
                logger.warning(f"Invalid regex for policy field {field_name}: {e}")
                results[field_name] = {
                    'found': False,
                    'values': [],
                    'required': is_required,
                    'error': f"Regex error: {str(e)}"
                }
        
        return results
    
    def _calculate_context_score(self, text: str, keywords: List[str]) -> float:
        """
        Calcula score de contexto baseado na presença de palavras-chave
        """
        text_lower = text.lower()
        found_keywords = sum(1 for keyword in keywords if keyword.lower() in text_lower)
        return min(found_keywords / len(keywords) if keywords else 0, 1.0)
    
    def _get_position_context(self, text: str, match: re.Match) -> Dict[str, Any]:
        """
        Obtém contexto posicional do match encontrado
        """
        start, end = match.span()
        
        # Contexto antes e depois (50 caracteres cada)
        context_before = text[max(0, start-50):start]
        context_after = text[end:end+50]
        
        # Linha onde o match foi encontrado
        lines_before = text[:start].count('\n')
        
        return {
            'start_pos': start,
            'end_pos': end,
            'line_number': lines_before + 1,
            'context_before': context_before.strip(),
            'context_after': context_after.strip()
        }
    
    def _apply_field_validator(self, 
                              field_type: str, 
                              value: str, 
                              context: Dict, 
                              position_info: Dict) -> Dict[str, Any]:
        """
        Aplica validador específico para o tipo de campo
        """
        validator = self.field_validators.get(field_type)
        if validator:
            return validator(value, context, position_info)
        
        # Validador padrão
        return {
            'is_valid': bool(value and value.strip()),
            'confidence': 0.5,
            'normalized_value': value.strip() if value else '',
            'issues': [],
            'validation_method': 'basic'
        }
    
    def _validate_passport_field(self, value: str, context: Dict, position_info: Dict) -> Dict[str, Any]:
        """Valida campo de passaporte usando validador de alta precisão"""
        nationality = context.get('nationality', '')
        is_valid, confidence, message = validate_passport_number_with_nationality(value, nationality)
        
        return {
            'is_valid': is_valid,
            'confidence': confidence,
            'normalized_value': value.upper().strip(),
            'issues': [message] if not is_valid else [],
            'validation_method': 'nationality_aware_passport_validator'
        }
    
    def _validate_date_field(self, value: str, context: Dict, position_info: Dict) -> Dict[str, Any]:
        """Valida campo de data usando normalizador robusto"""
        # Determinar tipo de data baseado no contexto
        field_type = 'general'
        context_before = position_info.get('context_before', '').lower()
        if 'birth' in context_before or 'born' in context_before:
            field_type = 'birth_date'
        elif 'expiry' in context_before or 'expire' in context_before:
            field_type = 'expiry_date'
        elif 'issue' in context_before or 'issued' in context_before:
            field_type = 'issue_date'
        
        is_valid, confidence, normalized, error = validate_date_with_context(value, field_type)
        
        return {
            'is_valid': is_valid,
            'confidence': confidence,
            'normalized_value': normalized,
            'issues': [error] if error else [],
            'validation_method': 'robust_date_normalizer'
        }
    
    def _validate_uscis_receipt_field(self, value: str, context: Dict, position_info: Dict) -> Dict[str, Any]:
        """Valida número de recibo USCIS"""
        is_valid = is_valid_uscis_receipt(value)
        
        return {
            'is_valid': is_valid,
            'confidence': 0.98 if is_valid else 0.1,
            'normalized_value': value.upper().strip(),
            'issues': [] if is_valid else ['Invalid USCIS receipt format or prefix'],
            'validation_method': 'uscis_receipt_validator'
        }
    
    def _validate_ssn_field(self, value: str, context: Dict, position_info: Dict) -> Dict[str, Any]:
        """Valida SSN"""
        is_valid = is_plausible_ssn(value)
        
        return {
            'is_valid': is_valid,
            'confidence': 0.95 if is_valid else 0.1,
            'normalized_value': value.strip(),
            'issues': [] if is_valid else ['Invalid or implausible SSN'],
            'validation_method': 'ssn_plausibility_validator'
        }
    
    def _validate_name_field(self, value: str, context: Dict, position_info: Dict) -> Dict[str, Any]:
        """Valida campos de nome"""
        cleaned = value.strip()
        is_valid = len(cleaned) >= 2 and cleaned.replace(' ', '').replace('-', '').replace("'", '').isalpha()
        
        return {
            'is_valid': is_valid,
            'confidence': 0.85 if is_valid else 0.3,
            'normalized_value': cleaned.title(),
            'issues': [] if is_valid else ['Invalid name format'],
            'validation_method': 'name_format_validator'
        }
    
    def _validate_address_field(self, value: str, context: Dict, position_info: Dict) -> Dict[str, Any]:
        """Valida campos de endereço"""
        cleaned = value.strip()
        is_valid = len(cleaned) >= 5
        
        return {
            'is_valid': is_valid,
            'confidence': 0.7 if is_valid else 0.2,
            'normalized_value': cleaned,
            'issues': [] if is_valid else ['Address too short or invalid'],
            'validation_method': 'basic_address_validator'
        }
    
    def _validate_monetary_field(self, value: str, context: Dict, position_info: Dict) -> Dict[str, Any]:
        """Valida campos monetários"""
        # Remover símbolos e formatar
        cleaned = re.sub(r'[^\d.,]', '', value)
        cleaned = cleaned.replace(',', '')
        
        try:
            amount = float(cleaned)
            is_valid = amount > 0
            normalized = f"${amount:,.2f}"
            
            return {
                'is_valid': is_valid,
                'confidence': 0.9 if is_valid else 0.1,
                'normalized_value': normalized,
                'issues': [] if is_valid else ['Invalid monetary amount'],
                'validation_method': 'monetary_format_validator'
            }
        except ValueError:
            return {
                'is_valid': False,
                'confidence': 0.0,
                'normalized_value': value,
                'issues': ['Cannot parse monetary value'],
                'validation_method': 'monetary_format_validator'
            }
    
    def _remove_duplicates(self, extractions: List[Dict]) -> List[Dict]:
        """
        Remove extrações duplicadas baseado em valores normalizados
        """
        seen_values = set()
        unique_extractions = []
        
        for extraction in extractions:
            normalized = extraction.get('normalized_value', extraction['value'])
            if normalized not in seen_values:
                seen_values.add(normalized)
                unique_extractions.append(extraction)
        
        return unique_extractions

# Instância global do motor de extração
field_extraction_engine = FieldExtractionEngine()