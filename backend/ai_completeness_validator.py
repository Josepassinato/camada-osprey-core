"""
AI Completeness Validator
Sistema de validação de completude usando Dra. Ana
Verifica se formulário amigável está completo antes da conversão
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timezone
import json

logger = logging.getLogger(__name__)

@dataclass
class CompletenessIssue:
    """Problema de completude identificado"""
    field_id: str
    section: str
    severity: str  # 'critical', 'important', 'optional'
    message: str
    suggestion: str

@dataclass
class CompletenessResult:
    """Resultado da validação de completude"""
    is_complete: bool
    completeness_score: float  # 0-100%
    critical_issues: List[CompletenessIssue]
    important_issues: List[CompletenessIssue]
    optional_issues: List[CompletenessIssue]
    ready_for_conversion: bool
    next_steps: List[str]
    dra_ana_assessment: str

class AICompletenessValidator:
    """
    Validador de completude usando Dra. Ana
    Verifica se formulário está pronto para conversão oficial
    """
    
    def __init__(self):
        self.required_fields_by_visa = {
            'H-1B': {
                'personal': ['full_name', 'date_of_birth', 'place_of_birth', 'nationality'],
                'address': ['street_address', 'city', 'state', 'postal_code', 'country', 'phone', 'email'],
                'employment': ['current_job', 'employer_name', 'salary'],
                'education': ['highest_degree', 'school_name']
            },
            'B-1/B-2': {
                'personal': ['full_name', 'date_of_birth', 'place_of_birth', 'nationality'],
                'address': ['street_address', 'city', 'state', 'postal_code', 'country', 'phone', 'email'],
                'travel': ['trips_outside_usa']
            },
            'F-1': {
                'personal': ['full_name', 'date_of_birth', 'place_of_birth', 'nationality'],
                'address': ['street_address', 'city', 'state', 'postal_code', 'country', 'phone', 'email'],
                'education': ['highest_degree', 'school_name', 'graduation_date']
            }
        }
        
    async def validate_completeness_with_dra_ana(
        self, 
        form_responses: Dict[str, Any], 
        visa_type: str,
        case_data: Dict[str, Any] = None
    ) -> CompletenessResult:
        """
        Validação completa de completude usando Dra. Ana
        """
        try:
            logger.info(f"🔍 Iniciando validação de completude para {visa_type}")
            
            # Análise básica de completude
            basic_analysis = self._analyze_basic_completeness(form_responses, visa_type)
            
            # Análise avançada com Dra. Ana
            dra_ana_analysis = await self._validate_with_dra_ana(
                form_responses, visa_type, case_data
            )
            
            # Combinar análises
            result = self._combine_analyses(basic_analysis, dra_ana_analysis, visa_type)
            
            logger.info(f"✅ Validação concluída: {result.completeness_score}% completo")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro na validação de completude: {str(e)}")
            
            # Retornar análise básica como fallback
            return CompletenessResult(
                is_complete=False,
                completeness_score=0.0,
                critical_issues=[CompletenessIssue(
                    field_id="system",
                    section="validation",
                    severity="critical",
                    message="Erro na validação automática",
                    suggestion="Verifique manualmente se todos os campos estão preenchidos"
                )],
                important_issues=[],
                optional_issues=[],
                ready_for_conversion=False,
                next_steps=["Revisar formulário manualmente"],
                dra_ana_assessment="Erro na análise automática - revisão manual necessária"
            )
    
    def _analyze_basic_completeness(
        self, 
        form_responses: Dict[str, Any], 
        visa_type: str
    ) -> Dict[str, Any]:
        """Análise básica de completude"""
        
        required_fields = self.required_fields_by_visa.get(visa_type, {})
        issues = []
        total_required = 0
        filled_required = 0
        
        # Verificar cada seção
        for section, fields in required_fields.items():
            section_responses = form_responses.get(section, {})
            
            for field in fields:
                total_required += 1
                value = section_responses.get(field, '')
                
                if self._is_field_empty(value):
                    issues.append(CompletenessIssue(
                        field_id=field,
                        section=section,
                        severity="critical",
                        message=f"Campo obrigatório '{field}' não preenchido",
                        suggestion=f"Preencha o campo '{field}' na seção '{section}'"
                    ))
                else:
                    filled_required += 1
        
        # Calcular score básico
        basic_score = (filled_required / max(total_required, 1)) * 100
        
        return {
            "basic_score": basic_score,
            "basic_issues": issues,
            "filled_fields": filled_required,
            "total_required": total_required
        }
    
    def _is_field_empty(self, value: Any) -> bool:
        """Verifica se campo está vazio"""
        if value is None:
            return True
        if isinstance(value, str) and not value.strip():
            return True
        if isinstance(value, (int, float)) and value == 0:
            return True
        return False
    
    async def _validate_with_dra_ana(
        self, 
        form_responses: Dict[str, Any], 
        visa_type: str,
        case_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Validação avançada usando Dra. Ana"""
        
        try:
            from specialized_agents import create_form_validator
            
            validator = create_form_validator()
            
            # Preparar contexto para Dra. Ana
            validation_prompt = f"""
            VALIDAÇÃO DE COMPLETUDE DE FORMULÁRIO AMIGÁVEL
            
            TIPO DE VISTO: {visa_type}
            ESTÁGIO: Formulário Amigável (português) → Conversão para Oficial (inglês)
            
            RESPOSTAS DO FORMULÁRIO:
            {json.dumps(form_responses, indent=2, ensure_ascii=False)}
            
            CASO DE DADOS ADICIONAIS:
            {json.dumps(case_data or {}, indent=2, ensure_ascii=False)}
            
            EXECUTE VALIDAÇÃO COMPLETA DE COMPLETUDE:
            
            1. CAMPOS OBRIGATÓRIOS PARA {visa_type}:
               - Verifique se TODOS os campos obrigatórios estão preenchidos
               - Identifique campos em falta por seção
               - Classifique por severidade (crítico/importante/opcional)
            
            2. QUALIDADE DAS RESPOSTAS:
               - Verifique se respostas são adequadas para conversão oficial
               - Identifique respostas muito vagas ou incompletas
               - Sugira melhorias nas respostas
            
            3. CONSISTÊNCIA INTERNA:
               - Verifique se dados são consistentes entre seções
               - Identifique contradições ou inconsistências
               - Valide datas e formatos
            
            4. PREPARAÇÃO PARA CONVERSÃO:
               - Determine se formulário está pronto para conversão oficial
               - Liste o que precisa ser completado antes da conversão
               - Estime chance de sucesso na conversão
            
            RESPONDA EM FORMATO JSON:
            {{
                "completeness_percentage": [0-100],
                "ready_for_conversion": true/false,
                "critical_missing": [
                    {{
                        "field": "nome_do_campo",
                        "section": "seção",
                        "message": "descrição do problema",
                        "suggestion": "como resolver"
                    }}
                ],
                "quality_issues": [
                    {{
                        "field": "nome_do_campo",
                        "issue": "problema identificado",
                        "improvement": "como melhorar"
                    }}
                ],
                "consistency_issues": ["lista de inconsistências"],
                "conversion_readiness": {{
                    "score": [0-100],
                    "blocking_issues": ["problemas que impedem conversão"],
                    "recommended_actions": ["ações recomendadas"]
                }},
                "dra_ana_assessment": "avaliação textual completa em português",
                "next_steps": ["próximos passos específicos"]
            }}
            """
            
            session_id = f"completeness_{visa_type}_{hash(str(form_responses)) % 10000}"
            analysis = await validator._call_agent(validation_prompt, session_id)
            
            # Processar resposta da Dra. Ana
            return self._process_dra_ana_completeness_response(analysis)
            
        except Exception as e:
            logger.error(f"❌ Erro na validação com Dra. Ana: {str(e)}")
            return {
                "completeness_percentage": 50,
                "ready_for_conversion": False,
                "critical_missing": [],
                "quality_issues": [],
                "dra_ana_assessment": "Erro na análise automática",
                "next_steps": ["Verificar campos manualmente"]
            }
    
    def _process_dra_ana_completeness_response(self, analysis: str) -> Dict[str, Any]:
        """Processa resposta da Dra. Ana sobre completude"""
        
        try:
            import json
            import re
            
            # Tentar extrair JSON da resposta
            json_match = re.search(r'\{.*\}', analysis, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            # Se não encontrar JSON, criar estrutura básica
            return {
                "completeness_percentage": 75,
                "ready_for_conversion": True,
                "critical_missing": [],
                "quality_issues": [],
                "consistency_issues": [],
                "conversion_readiness": {
                    "score": 75,
                    "blocking_issues": [],
                    "recommended_actions": ["Revisar respostas"]
                },
                "dra_ana_assessment": analysis[:500] + "..." if len(analysis) > 500 else analysis,
                "next_steps": ["Continuar com conversão"]
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar resposta da Dra. Ana: {e}")
            return {
                "completeness_percentage": 50,
                "ready_for_conversion": False,
                "critical_missing": [],
                "quality_issues": [],
                "dra_ana_assessment": "Erro no processamento da validação",
                "next_steps": ["Revisar formulário manualmente"]
            }
    
    def _combine_analyses(
        self, 
        basic_analysis: Dict[str, Any], 
        dra_ana_analysis: Dict[str, Any],
        visa_type: str
    ) -> CompletenessResult:
        """Combina análises básica e da Dra. Ana"""
        
        # Combinar issues críticas
        critical_issues = []
        
        # Issues básicas
        for issue in basic_analysis.get("basic_issues", []):
            critical_issues.append(issue)
        
        # Issues da Dra. Ana
        for missing in dra_ana_analysis.get("critical_missing", []):
            critical_issues.append(CompletenessIssue(
                field_id=missing.get("field", "unknown"),
                section=missing.get("section", "unknown"),
                severity="critical",
                message=missing.get("message", "Campo obrigatório"),
                suggestion=missing.get("suggestion", "Preencher campo")
            ))
        
        # Issues de qualidade
        quality_issues = []
        for quality in dra_ana_analysis.get("quality_issues", []):
            quality_issues.append(CompletenessIssue(
                field_id=quality.get("field", "unknown"),
                section="quality",
                severity="important",
                message=quality.get("issue", "Problema de qualidade"),
                suggestion=quality.get("improvement", "Melhorar resposta")
            ))
        
        # Calcular score combinado
        basic_score = basic_analysis.get("basic_score", 0)
        dra_ana_score = dra_ana_analysis.get("completeness_percentage", 0)
        combined_score = (basic_score * 0.4 + dra_ana_score * 0.6)  # Peso maior para Dra. Ana
        
        # Determinar se está pronto
        ready_for_conversion = (
            len(critical_issues) == 0 and 
            combined_score >= 80 and
            dra_ana_analysis.get("ready_for_conversion", False)
        )
        
        return CompletenessResult(
            is_complete=combined_score >= 90,
            completeness_score=combined_score,
            critical_issues=critical_issues,
            important_issues=quality_issues,
            optional_issues=[],
            ready_for_conversion=ready_for_conversion,
            next_steps=dra_ana_analysis.get("next_steps", ["Revisar formulário"]),
            dra_ana_assessment=dra_ana_analysis.get("dra_ana_assessment", 
                f"Formulário {combined_score:.0f}% completo para {visa_type}")
        )


# Função helper para uso fácil
async def validate_form_completeness(
    form_responses: Dict[str, Any], 
    visa_type: str,
    case_data: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Função helper para validação de completude
    """
    validator = AICompletenessValidator()
    result = await validator.validate_completeness_with_dra_ana(
        form_responses, visa_type, case_data
    )
    
    return {
        "is_complete": result.is_complete,
        "completeness_score": result.completeness_score,
        "ready_for_conversion": result.ready_for_conversion,
        "critical_issues": [
            {
                "field_id": issue.field_id,
                "section": issue.section,
                "severity": issue.severity,
                "message": issue.message,
                "suggestion": issue.suggestion
            }
            for issue in result.critical_issues
        ],
        "important_issues": [
            {
                "field_id": issue.field_id,
                "section": issue.section,
                "severity": issue.severity,
                "message": issue.message,
                "suggestion": issue.suggestion
            }
            for issue in result.important_issues
        ],
        "next_steps": result.next_steps,
        "dra_ana_assessment": result.dra_ana_assessment
    }