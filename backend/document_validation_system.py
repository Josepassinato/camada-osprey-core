"""
Sistema Completo de Validação de Documentos
Valida automaticamente: legibilidade, validade, tipo correto, e propriedade
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class DocumentValidationSystem:
    """
    Sistema completo de validação automática de documentos
    """
    
    def __init__(self):
        self.validation_rules = self._initialize_validation_rules()
    
    def _initialize_validation_rules(self) -> Dict:
        """Define regras de validação por tipo de documento"""
        return {
            'passport': {
                'required_fields': ['passport_number', 'expiry_date', 'date_of_birth'],
                'expiry_check': True,
                'min_validity_months': 6,  # Mínimo 6 meses de validade
                'name_match_required': True
            },
            'driver_license': {
                'required_fields': ['license_number', 'expiry_date'],
                'expiry_check': True,
                'min_validity_months': 0,
                'name_match_required': True
            },
            'birth_certificate': {
                'required_fields': ['birth_date'],
                'expiry_check': False,
                'name_match_required': True
            },
            'marriage_certificate': {
                'required_fields': [],
                'expiry_check': False,
                'name_match_required': True
            },
            'i797': {
                'required_fields': ['receipt_number', 'notice_type'],
                'expiry_check': True,
                'min_validity_months': 0,
                'name_match_required': True
            },
            'tax_return': {
                'required_fields': [],
                'expiry_check': False,
                'name_match_required': True
            },
            'medical_exam': {
                'required_fields': [],
                'expiry_check': True,
                'min_validity_months': 12,  # Exames médicos válidos por 1 ano
                'name_match_required': True
            }
        }
    
    def validate_document_comprehensive(
        self,
        doc_type: str,
        extracted_fields: Dict[str, Any],
        extracted_text: str,
        applicant_name: str,
        confidence: float
    ) -> Dict[str, Any]:
        """
        Validação completa de documento
        
        Valida:
        1. Legibilidade
        2. Tipo correto
        3. Data de validade
        4. Pertence à pessoa correta
        """
        
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'checks': {}
        }
        
        # 1. VALIDAÇÃO DE LEGIBILIDADE
        legibility_check = self._check_legibility(extracted_text, confidence)
        validation_result['checks']['legibility'] = legibility_check
        
        if not legibility_check['passed']:
            validation_result['is_valid'] = False
            validation_result['errors'].append({
                'code': 'ILLEGIBLE_DOCUMENT',
                'message': '❌ DOCUMENTO ILEGÍVEL',
                'details': 'O documento não está legível o suficiente para análise.',
                'recommendation': 'Tire uma foto mais clara com melhor iluminação e foco.'
            })
            return validation_result  # Retorna imediatamente se ilegível
        
        # 2. VALIDAÇÃO DE DATA DE VALIDADE
        if doc_type in self.validation_rules:
            rules = self.validation_rules[doc_type]
            
            if rules.get('expiry_check', False):
                expiry_check = self._check_expiry_date(
                    extracted_fields,
                    rules.get('min_validity_months', 0)
                )
                validation_result['checks']['expiry'] = expiry_check
                
                if not expiry_check['passed']:
                    validation_result['is_valid'] = False
                    validation_result['errors'].append({
                        'code': 'DOCUMENT_EXPIRED',
                        'message': '❌ DOCUMENTO VENCIDO',
                        'details': expiry_check['message'],
                        'recommendation': 'Renove o documento e envie a versão atualizada.'
                    })
        
        # 3. VALIDAÇÃO DE CAMPOS OBRIGATÓRIOS
        if doc_type in self.validation_rules:
            rules = self.validation_rules[doc_type]
            required_fields_check = self._check_required_fields(
                extracted_fields,
                rules.get('required_fields', [])
            )
            validation_result['checks']['required_fields'] = required_fields_check
            
            if not required_fields_check['passed']:
                validation_result['is_valid'] = False
                validation_result['errors'].append({
                    'code': 'MISSING_FIELDS',
                    'message': '❌ CAMPOS OBRIGATÓRIOS FALTANDO',
                    'details': f"Campos não identificados: {', '.join(required_fields_check['missing_fields'])}",
                    'recommendation': 'Certifique-se de que o documento está completo e legível.'
                })
        
        # 4. VALIDAÇÃO DE NOME (se aplicável)
        if doc_type in self.validation_rules:
            rules = self.validation_rules[doc_type]
            
            if rules.get('name_match_required', False) and applicant_name:
                name_check = self._check_name_match(
                    extracted_text,
                    extracted_fields,
                    applicant_name
                )
                validation_result['checks']['name_match'] = name_check
                
                if not name_check['passed']:
                    validation_result['warnings'].append({
                        'code': 'NAME_MISMATCH',
                        'message': '⚠️ NOME NÃO CORRESPONDE',
                        'details': name_check['message'],
                        'recommendation': 'Verifique se o documento pertence ao aplicante correto.'
                    })
        
        return validation_result
    
    def _check_legibility(self, text: str, confidence: float) -> Dict:
        """Verifica se o documento está legível"""
        
        # Critérios de legibilidade
        min_text_length = 50  # Mínimo de caracteres
        min_confidence = 0.6   # Confiança mínima do OCR
        
        if len(text) < min_text_length:
            return {
                'passed': False,
                'confidence': confidence,
                'text_length': len(text),
                'message': f'Texto extraído muito curto ({len(text)} caracteres). Mínimo: {min_text_length}'
            }
        
        if confidence < min_confidence:
            return {
                'passed': False,
                'confidence': confidence,
                'text_length': len(text),
                'message': f'Confiança do OCR muito baixa ({confidence:.1%}). Mínimo: {min_confidence:.0%}'
            }
        
        return {
            'passed': True,
            'confidence': confidence,
            'text_length': len(text),
            'message': 'Documento legível'
        }
    
    def _check_expiry_date(
        self,
        extracted_fields: Dict,
        min_validity_months: int
    ) -> Dict:
        """Verifica se o documento está válido (não expirado)"""
        
        # Procura por campo de data de validade
        expiry_date = None
        expiry_field_names = ['expiry_date', 'valid_until', 'validade', 'expiration_date']
        
        for field_name in expiry_field_names:
            if field_name in extracted_fields:
                expiry_date = extracted_fields[field_name]
                break
        
        if not expiry_date:
            return {
                'passed': True,  # Se não encontrou data, assume válido (conservador)
                'message': 'Data de validade não encontrada no documento'
            }
        
        # Parse da data
        parsed_date = self._parse_date(expiry_date)
        
        if not parsed_date:
            return {
                'passed': False,
                'message': f'Data de validade inválida: {expiry_date}'
            }
        
        today = datetime.now()
        min_valid_until = today + timedelta(days=min_validity_months * 30)
        
        # Verifica se está expirado
        if parsed_date < today:
            days_expired = (today - parsed_date).days
            return {
                'passed': False,
                'expiry_date': expiry_date,
                'message': f'Documento expirado há {days_expired} dias (desde {parsed_date.strftime("%d/%m/%Y")})'
            }
        
        # Verifica validade mínima
        if min_validity_months > 0 and parsed_date < min_valid_until:
            days_remaining = (parsed_date - today).days
            months_remaining = days_remaining / 30
            return {
                'passed': False,
                'expiry_date': expiry_date,
                'message': f'Documento expira em {days_remaining} dias ({months_remaining:.1f} meses). Mínimo necessário: {min_validity_months} meses'
            }
        
        days_remaining = (parsed_date - today).days
        return {
            'passed': True,
            'expiry_date': expiry_date,
            'days_remaining': days_remaining,
            'message': f'Documento válido até {parsed_date.strftime("%d/%m/%Y")} ({days_remaining} dias)'
        }
    
    def _check_required_fields(
        self,
        extracted_fields: Dict,
        required_fields: List[str]
    ) -> Dict:
        """Verifica se todos os campos obrigatórios foram encontrados"""
        
        missing_fields = []
        
        for field in required_fields:
            if field not in extracted_fields or not extracted_fields[field]:
                missing_fields.append(field)
        
        if missing_fields:
            return {
                'passed': False,
                'missing_fields': missing_fields,
                'message': f'Campos obrigatórios não encontrados: {", ".join(missing_fields)}'
            }
        
        return {
            'passed': True,
            'missing_fields': [],
            'message': 'Todos os campos obrigatórios encontrados'
        }
    
    def _check_name_match(
        self,
        text: str,
        extracted_fields: Dict,
        applicant_name: str
    ) -> Dict:
        """Verifica se o nome no documento corresponde ao aplicante"""
        
        if not applicant_name:
            return {
                'passed': True,
                'message': 'Nome do aplicante não fornecido'
            }
        
        # Normaliza nomes
        applicant_name_normalized = self._normalize_name(applicant_name)
        text_normalized = self._normalize_name(text)
        
        # Separa primeiro e último nome
        name_parts = applicant_name_normalized.split()
        
        if len(name_parts) < 2:
            return {
                'passed': True,
                'message': 'Nome do aplicante muito curto para validação'
            }
        
        first_name = name_parts[0]
        last_name = name_parts[-1]
        
        # Verifica se primeiro E último nome aparecem no texto
        first_found = first_name in text_normalized
        last_found = last_name in text_normalized
        
        if first_found and last_found:
            return {
                'passed': True,
                'message': f'Nome correspondente: {first_name} {last_name}'
            }
        
        # Verifica campos específicos de nome
        name_fields = ['full_name', 'name', 'nome', 'nome_completo']
        for field in name_fields:
            if field in extracted_fields:
                field_value_normalized = self._normalize_name(str(extracted_fields[field]))
                if first_name in field_value_normalized and last_name in field_value_normalized:
                    return {
                        'passed': True,
                        'message': f'Nome correspondente no campo {field}'
                    }
        
        return {
            'passed': False,
            'message': f'Nome "{applicant_name}" não encontrado no documento. Verifique se o documento pertence ao aplicante.'
        }
    
    def _normalize_name(self, name: str) -> str:
        """Normaliza nome para comparação"""
        # Remove acentos, converte para maiúsculas
        import unicodedata
        name = ''.join(
            c for c in unicodedata.normalize('NFD', name)
            if unicodedata.category(c) != 'Mn'
        )
        return name.upper().strip()
    
    def _parse_date(self, date_str: Any) -> Optional[datetime]:
        """Parse de data em vários formatos"""
        
        if isinstance(date_str, datetime):
            return date_str
        
        if not isinstance(date_str, str):
            date_str = str(date_str)
        
        # Formatos comuns
        formats = [
            '%d/%m/%Y',
            '%d-%m-%Y',
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%d/%m/%y',
            '%Y/%m/%d',
            '%d.%m.%Y'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except:
                continue
        
        return None
    
    def analyze_all_documents(
        self,
        documents: List[Dict],
        visa_type: str,
        applicant_data: Dict
    ) -> Dict:
        """
        Análise final de todos os documentos
        Dá parecer se está satisfatório ou necessita mais documentos
        """
        
        analysis = {
            'status': 'pending',
            'completeness_score': 0.0,
            'total_documents': len(documents),
            'valid_documents': 0,
            'invalid_documents': 0,
            'warnings': 0,
            'required_documents': self._get_required_documents_for_visa(visa_type),
            'missing_required': [],
            'recommendations': [],
            'final_verdict': ''
        }
        
        # Conta documentos válidos/inválidos
        for doc in documents:
            if doc.get('validation_result', {}).get('is_valid', False):
                analysis['valid_documents'] += 1
            else:
                analysis['invalid_documents'] += 1
            
            warnings = doc.get('validation_result', {}).get('warnings', [])
            analysis['warnings'] += len(warnings)
        
        # Verifica documentos obrigatórios
        submitted_types = [doc.get('document_type') for doc in documents]
        
        for req_doc in analysis['required_documents']:
            if req_doc not in submitted_types:
                analysis['missing_required'].append(req_doc)
        
        # Calcula score de completude
        if analysis['required_documents']:
            submitted_required = len(analysis['required_documents']) - len(analysis['missing_required'])
            analysis['completeness_score'] = submitted_required / len(analysis['required_documents'])
        
        # Determina status
        if analysis['invalid_documents'] > 0:
            analysis['status'] = 'requires_correction'
            analysis['final_verdict'] = '❌ NECESSITA CORREÇÕES'
            analysis['recommendations'].append(
                f"Corrija os {analysis['invalid_documents']} documento(s) com problemas antes de continuar."
            )
        
        elif len(analysis['missing_required']) > 0:
            analysis['status'] = 'incomplete'
            analysis['final_verdict'] = '⚠️ DOCUMENTAÇÃO INCOMPLETA'
            analysis['recommendations'].append(
                f"Envie os seguintes documentos obrigatórios: {', '.join([self._translate_doc_type(d) for d in analysis['missing_required']])}"
            )
        
        elif analysis['warnings'] > 0:
            analysis['status'] = 'acceptable_with_warnings'
            analysis['final_verdict'] = '✅ ACEITÁVEL COM RESSALVAS'
            analysis['recommendations'].append(
                f"Há {analysis['warnings']} aviso(s) que podem ser revisados, mas a documentação é aceitável."
            )
        
        else:
            analysis['status'] = 'satisfactory'
            analysis['final_verdict'] = '✅ DOCUMENTAÇÃO SATISFATÓRIA'
            analysis['recommendations'].append(
                "Todos os documentos obrigatórios foram enviados e validados com sucesso!"
            )
        
        # Recomendações adicionais baseadas no tipo de visto
        additional_docs = self._get_optional_documents_for_visa(visa_type)
        if additional_docs:
            analysis['recommendations'].append(
                f"Documentos opcionais que podem fortalecer o caso: {', '.join([self._translate_doc_type(d) for d in additional_docs[:3]])}"
            )
        
        return analysis
    
    def _get_required_documents_for_visa(self, visa_type: str) -> List[str]:
        """Retorna lista de documentos obrigatórios por tipo de visto"""
        
        required = {
            'H-1B': ['passport', 'education_diploma', 'education_transcript', 'employment_letter'],
            'F-1': ['passport', 'i20', 'education_transcript', 'bank_statement'],
            'B-1/B-2': ['passport', 'bank_statement'],
            'O-1': ['passport', 'education_diploma', 'employment_letter', 'recommendation_letters'],
            'I-589': ['passport', 'birth_certificate', 'police_clearance'],
            'I-130': ['passport', 'birth_certificate', 'marriage_certificate'],
            'N-400': ['passport', 'green_card', 'tax_return']
        }
        
        return required.get(visa_type, ['passport'])
    
    def _get_optional_documents_for_visa(self, visa_type: str) -> List[str]:
        """Retorna lista de documentos opcionais que fortalecem o caso"""
        
        optional = {
            'H-1B': ['recommendation_letters', 'pay_stub', 'previous_visa'],
            'F-1': ['employment_letter', 'sponsor_documents'],
            'O-1': ['awards', 'publications', 'media_coverage'],
        }
        
        return optional.get(visa_type, [])
    
    def _translate_doc_type(self, doc_type: str) -> str:
        """Traduz tipo de documento para português"""
        translations = {
            'passport': 'Passaporte',
            'driver_license': 'Carteira de Motorista',
            'birth_certificate': 'Certidão de Nascimento',
            'marriage_certificate': 'Certidão de Casamento',
            'education_diploma': 'Diploma',
            'education_transcript': 'Histórico Escolar',
            'employment_letter': 'Carta de Emprego',
            'bank_statement': 'Extrato Bancário',
            'tax_return': 'Declaração de IR',
            'i797': 'Formulário I-797',
            'i20': 'Formulário I-20',
            'green_card': 'Green Card',
            'medical_exam': 'Exame Médico',
            'police_clearance': 'Antecedentes Criminais',
            'recommendation_letters': 'Cartas de Recomendação',
            'pay_stub': 'Contracheque'
        }
        return translations.get(doc_type, doc_type.upper())


# Instância global
document_validation_system = DocumentValidationSystem()
