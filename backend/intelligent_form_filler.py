"""
Intelligent Form Filler System
Sistema inteligente de preenchimento de formulários USCIS
Integra dados dos documentos validados com formulários oficiais
"""

import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timezone
import json
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class FormSuggestion:
    """Sugestão de preenchimento de campo"""
    field_id: str
    suggested_value: str
    confidence: float
    source: str  # 'document', 'basic_data', 'ai_analysis'
    explanation: str

@dataclass
class FormValidationResult:
    """Resultado de validação de formulário"""
    is_valid: bool
    errors: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    completeness_score: float
    suggestions: List[FormSuggestion]

class IntelligentFormFiller:
    """
    Sistema inteligente de preenchimento de formulários
    Combina dados de documentos + validação em tempo real + Dra. Ana
    """
    
    def __init__(self):
        self.form_mappings = self._initialize_form_mappings()
        
    def _initialize_form_mappings(self) -> Dict[str, Dict[str, str]]:
        """Mapeamento de dados extraídos para campos de formulário"""
        return {
            'H-1B': {
                'full_name': ['full_name', 'applicant_name', 'beneficiary_name'],
                'date_of_birth': ['date_of_birth', 'birth_date', 'dob'],
                'place_of_birth': ['place_of_birth', 'birth_place', 'country_of_birth'],
                'passport_number': ['passport_number', 'document_number', 'passport_no'],
                'passport_country': ['passport_country', 'nationality', 'country_of_issuance'],
                'current_address': ['current_address', 'mailing_address', 'residence_address'],
                'phone': ['phone_number', 'telephone', 'contact_phone'],
                'email': ['email_address', 'email', 'contact_email']
            },
            'B-1/B-2': {
                'full_name': ['full_name', 'applicant_name', 'traveler_name'],
                'date_of_birth': ['date_of_birth', 'birth_date'],
                'passport_number': ['passport_number', 'travel_document_number'],
                'purpose_of_visit': ['purpose_of_visit', 'travel_purpose', 'visit_reason']
            },
            'F-1': {
                'full_name': ['full_name', 'student_name', 'applicant_name'],
                'school_name': ['school_name', 'institution_name', 'university_name'],
                'degree_program': ['degree_program', 'program_of_study', 'field_of_study']
            }
        }
    
    async def generate_intelligent_suggestions(
        self, 
        case_data: Dict[str, Any], 
        form_code: str,
        current_form_data: Dict[str, Any] = None,
        db_connection = None
    ) -> List[FormSuggestion]:
        """
        Gera sugestões inteligentes baseadas em dados dos documentos
        """
        suggestions = []
        
        try:
            # Extrair dados de múltiplas fontes
            basic_data = case_data.get('basic_data', {})
            ai_extracted_facts = case_data.get('ai_extracted_facts', {})
            
            # Buscar documentos validados para este caso
            document_analysis = []
            if db_connection and case_data.get('case_id'):
                case_id = case_data['case_id']
                documents_cursor = db_connection.documents.find({"case_id": case_id})
                case_documents = await documents_cursor.to_list(length=None)
                
                logger.info(f"🔍 Encontrados {len(case_documents)} documentos para caso {case_id}")
                
                # Extrair análises dos documentos
                for doc in case_documents:
                    if doc.get('ai_analysis'):
                        document_analysis.append(doc['ai_analysis'])
            
            logger.info(f"🤖 Gerando sugestões para {form_code} com {len(document_analysis)} documentos analisados")
            
            # Processar análises de documentos
            extracted_data = self._extract_data_from_documents(document_analysis)
            
            # Combinar com dados básicos
            combined_data = {**basic_data, **extracted_data, **ai_extracted_facts}
            
            # Gerar sugestões baseadas no tipo de formulário
            form_fields = self.form_mappings.get(form_code, {})
            
            for target_field, possible_sources in form_fields.items():
                suggestion = self._find_best_suggestion(
                    target_field, possible_sources, combined_data, current_form_data
                )
                if suggestion:
                    suggestions.append(suggestion)
            
            # Sugestões específicas por tipo de visto
            if form_code == 'H-1B':
                suggestions.extend(self._generate_h1b_specific_suggestions(combined_data))
            elif form_code == 'B-1/B-2':
                suggestions.extend(self._generate_b1b2_specific_suggestions(combined_data))
            
            logger.info(f"✅ Geradas {len(suggestions)} sugestões inteligentes")
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar sugestões: {str(e)}")
        
        return suggestions
    
    def _extract_data_from_documents(self, document_analysis: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extrai dados úteis das análises de documentos"""
        
        extracted_data = {}
        
        for doc_analysis in document_analysis:
            if not isinstance(doc_analysis, dict):
                continue
                
            # Extrair dados do sistema de visão real
            extracted_doc_data = doc_analysis.get('extracted_data', {})
            
            if extracted_doc_data:
                # Dados de passaporte
                if 'full_name' in extracted_doc_data:
                    extracted_data['full_name'] = extracted_doc_data['full_name']
                    extracted_data['passport_name'] = extracted_doc_data['full_name']
                
                if 'nationality' in extracted_doc_data:
                    extracted_data['nationality'] = extracted_doc_data['nationality']
                    extracted_data['passport_country'] = extracted_doc_data['nationality']
                
                if 'document_number' in extracted_doc_data:
                    extracted_data['passport_number'] = extracted_doc_data['document_number']
                
                if 'place_of_birth' in extracted_doc_data:
                    extracted_data['place_of_birth'] = extracted_doc_data['place_of_birth']
                
                # Dados de CNH
                if 'license_number' in extracted_doc_data:
                    extracted_data['license_number'] = extracted_doc_data['license_number']
                
                # Dados gerais
                for field in ['issue_date', 'expiry_date', 'issuing_authority']:
                    if field in extracted_doc_data:
                        extracted_data[field] = extracted_doc_data[field]
        
        return extracted_data
    
    def _find_best_suggestion(
        self, 
        target_field: str, 
        possible_sources: List[str], 
        combined_data: Dict[str, Any],
        current_form_data: Dict[str, Any] = None
    ) -> Optional[FormSuggestion]:
        """Encontra a melhor sugestão para um campo"""
        
        # Verificar se campo já está preenchido
        if current_form_data and current_form_data.get(target_field):
            return None
        
        for source_field in possible_sources:
            value = combined_data.get(source_field)
            if value and isinstance(value, str) and len(value.strip()) > 0:
                
                # Determinar fonte e confiança
                source_type = self._determine_source_type(source_field, combined_data)
                confidence = self._calculate_confidence(value, source_type)
                
                # Formatar valor conforme necessário
                formatted_value = self._format_field_value(target_field, value)
                
                return FormSuggestion(
                    field_id=target_field,
                    suggested_value=formatted_value,
                    confidence=confidence,
                    source=source_type,
                    explanation=f"Extraído de {source_type}: {source_field}"
                )
        
        return None
    
    def _determine_source_type(self, field_name: str, combined_data: Dict[str, Any]) -> str:
        """Determina o tipo de fonte dos dados"""
        
        if field_name in ['firstName', 'lastName', 'city', 'state']:
            return 'basic_data'
        elif 'passport' in field_name.lower() or 'document' in field_name.lower():
            return 'document'
        elif 'extracted' in field_name.lower() or 'ai' in field_name.lower():
            return 'ai_analysis'
        else:
            return 'document'
    
    def _calculate_confidence(self, value: str, source_type: str) -> float:
        """Calcula confiança na sugestão"""
        
        base_confidence = {
            'document': 0.95,  # Dados extraídos de documentos têm alta confiança
            'basic_data': 0.85,  # Dados inseridos pelo usuário
            'ai_analysis': 0.80   # Análise de IA
        }.get(source_type, 0.70)
        
        # Ajustar baseado na qualidade do valor
        if len(value) < 3:
            base_confidence *= 0.6
        elif len(value) > 50:
            base_confidence *= 0.8
        elif re.match(r'^[A-Z\s]+$', value):  # Nomes em maiúsculas
            base_confidence *= 1.1
        
        return min(1.0, base_confidence)
    
    def _format_field_value(self, field_name: str, value: str) -> str:
        """Formata valor conforme necessário para o campo"""
        
        # Formatação de nomes
        if 'name' in field_name.lower():
            return self._format_name(value)
        
        # Formatação de datas
        elif 'date' in field_name.lower():
            return self._format_date(value)
        
        # Formatação de endereços
        elif 'address' in field_name.lower():
            return self._format_address(value)
        
        # Formatação de números de documento
        elif any(doc_type in field_name.lower() for doc_type in ['passport', 'license', 'document']):
            return value.upper().replace(' ', '')
        
        return value.strip()
    
    def _format_name(self, name: str) -> str:
        """Formata nomes adequadamente"""
        # Converter para title case, mas manter acentos
        return ' '.join(word.capitalize() for word in name.strip().split())
    
    def _format_date(self, date_str: str) -> str:
        """Formata datas para padrão americano MM/DD/YYYY"""
        try:
            # Tentar diferentes formatos
            for fmt in ['%d/%m/%Y', '%Y-%m-%d', '%m/%d/%Y']:
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    return date_obj.strftime('%m/%d/%Y')
                except:
                    continue
        except:
            pass
        return date_str
    
    def _format_address(self, address: str) -> str:
        """Formata endereços"""
        return address.strip().title()
    
    def _generate_h1b_specific_suggestions(self, combined_data: Dict[str, Any]) -> List[FormSuggestion]:
        """Sugestões específicas para H-1B"""
        suggestions = []
        
        # Sugestão de classe de admissão
        if not combined_data.get('class_of_admission'):
            suggestions.append(FormSuggestion(
                field_id='class_of_admission',
                suggested_value='H-1B',
                confidence=0.95,
                source='form_logic',
                explanation='Classe de admissão padrão para petição H-1B'
            ))
        
        # Sugestão de duração da permanência
        if not combined_data.get('duration_of_stay'):
            suggestions.append(FormSuggestion(
                field_id='duration_of_stay',
                suggested_value='3 years',
                confidence=0.90,
                source='form_logic',
                explanation='Duração padrão inicial para H-1B'
            ))
        
        return suggestions
    
    def _generate_b1b2_specific_suggestions(self, combined_data: Dict[str, Any]) -> List[FormSuggestion]:
        """Sugestões específicas para B-1/B-2"""
        suggestions = []
        
        # Sugestão de duração da visita
        if not combined_data.get('duration_of_visit'):
            suggestions.append(FormSuggestion(
                field_id='duration_of_visit',
                suggested_value='30 days',
                confidence=0.80,
                source='form_logic',
                explanation='Duração típica para visita de turismo/negócios'
            ))
        
        return suggestions
    
    async def validate_form_with_dra_ana(
        self, 
        form_data: Dict[str, Any], 
        visa_type: str, 
        step_id: str = "form_review"
    ) -> FormValidationResult:
        """
        Validação completa do formulário usando Dra. Ana
        """
        try:
            from specialized_agents import create_form_validator
            
            validator = create_form_validator()
            
            # Prompt específico para validação
            validation_prompt = f"""
            VALIDAÇÃO COMPLETA DE FORMULÁRIO USCIS
            
            TIPO DE VISTO: {visa_type}
            ETAPA: {step_id}
            
            DADOS DO FORMULÁRIO:
            {json.dumps(form_data, indent=2, ensure_ascii=False)}
            
            EXECUTE VALIDAÇÃO SISTEMÁTICA:
            
            1. CAMPOS OBRIGATÓRIOS:
            - Verifique se todos os campos obrigatórios para {visa_type} estão preenchidos
            - Liste campos em falta com severidade (crítico/importante/opcional)
            
            2. CONSISTÊNCIA DE DADOS:
            - Verificar formato de datas (MM/DD/YYYY)
            - Validar formatos de nomes (consistência)
            - Conferir números de documentos
            
            3. LÓGICA DE NEGÓCIO:
            - Verificar se dados fazem sentido para {visa_type}
            - Identificar inconsistências entre campos relacionados
            
            4. SUGESTÕES DE MELHORIA:
            - Campos que podem ser otimizados
            - Informações adicionais que ajudariam
            
            FORMATO DE RESPOSTA:
            {{
                "validation_result": "APROVADO/REPROVADO/COM_RESSALVAS",
                "completeness_score": [0-100],
                "critical_errors": [lista de erros críticos],
                "warnings": [lista de avisos],
                "suggestions": [lista de sugestões],
                "missing_fields": [campos obrigatórios em falta],
                "next_steps": "orientação sobre próximos passos"
            }}
            """
            
            session_id = f"form_validation_{visa_type}_{hash(str(form_data)) % 10000}"
            analysis = await validator._call_agent(validation_prompt, session_id)
            
            # Processar resposta da Dra. Ana
            validation_data = self._process_dra_ana_response(analysis)
            
            return FormValidationResult(
                is_valid=validation_data.get('validation_result') == 'APROVADO',
                errors=validation_data.get('critical_errors', []),
                warnings=validation_data.get('warnings', []),
                completeness_score=float(validation_data.get('completeness_score', 0)),
                suggestions=self._convert_to_form_suggestions(validation_data.get('suggestions', []))
            )
            
        except Exception as e:
            logger.error(f"❌ Erro na validação com Dra. Ana: {str(e)}")
            
            # Retornar validação básica em caso de erro
            return FormValidationResult(
                is_valid=False,
                errors=[{"message": "Erro na validação automática", "severity": "high"}],
                warnings=[],
                completeness_score=0.0,
                suggestions=[]
            )
    
    def _process_dra_ana_response(self, analysis: str) -> Dict[str, Any]:
        """Processa resposta da Dra. Ana"""
        
        try:
            # Tentar extrair JSON da resposta
            import json
            import re
            
            # Procurar por JSON na resposta
            json_match = re.search(r'\{.*\}', analysis, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            # Se não encontrar JSON, processar texto
            return {
                "validation_result": "COM_RESSALVAS",
                "completeness_score": 75,
                "critical_errors": [],
                "warnings": ["Resposta de validação não estruturada"],
                "suggestions": [],
                "analysis_text": analysis
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar resposta da Dra. Ana: {e}")
            return {
                "validation_result": "COM_RESSALVAS", 
                "completeness_score": 50,
                "critical_errors": ["Erro no processamento da validação"],
                "warnings": [],
                "suggestions": []
            }
    
    def _convert_to_form_suggestions(self, suggestions_data: List[Any]) -> List[FormSuggestion]:
        """Converte sugestões da Dra. Ana para objetos FormSuggestion"""
        
        suggestions = []
        
        for suggestion in suggestions_data:
            if isinstance(suggestion, str):
                suggestions.append(FormSuggestion(
                    field_id="general",
                    suggested_value="",
                    confidence=0.80,
                    source="dra_ana",
                    explanation=suggestion
                ))
            elif isinstance(suggestion, dict):
                suggestions.append(FormSuggestion(
                    field_id=suggestion.get('field', 'general'),
                    suggested_value=suggestion.get('value', ''),
                    confidence=suggestion.get('confidence', 0.80),
                    source="dra_ana",
                    explanation=suggestion.get('explanation', str(suggestion))
                ))
        
        return suggestions


# Função helper para uso fácil
async def get_intelligent_form_suggestions(case_data: Dict[str, Any], form_code: str, db_connection = None) -> List[Dict[str, Any]]:
    """
    Função helper para obter sugestões inteligentes de preenchimento
    """
    filler = IntelligentFormFiller()
    suggestions = await filler.generate_intelligent_suggestions(case_data, form_code, db_connection=db_connection)
    
    # Converter para formato JSON serializável
    return [
        {
            "field_id": s.field_id,
            "suggested_value": s.suggested_value,
            "confidence": s.confidence,
            "source": s.source,
            "explanation": s.explanation
        }
        for s in suggestions
    ]

async def validate_form_with_ai(form_data: Dict[str, Any], visa_type: str) -> Dict[str, Any]:
    """
    Função helper para validação de formulário com IA
    """
    filler = IntelligentFormFiller()
    result = await filler.validate_form_with_dra_ana(form_data, visa_type)
    
    return {
        "is_valid": result.is_valid,
        "errors": result.errors,
        "warnings": result.warnings,
        "completeness_score": result.completeness_score,
        "suggestions": [
            {
                "field_id": s.field_id,
                "suggested_value": s.suggested_value,
                "confidence": s.confidence,
                "source": s.source,
                "explanation": s.explanation
            }
            for s in result.suggestions
        ]
    }