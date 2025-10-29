"""
Sistema de Análise de Completude para Aplicações de Imigração
Analisa qualidade e completude das informações fornecidas pelo usuário
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
from emergentintegrations import OAICompatible

logger = logging.getLogger(__name__)

# Initialize emergent integrations client
emergent_llm_key = os.environ.get('EMERGENT_LLM_KEY')
client = OAICompatible(emergent_llm_key)

class CompletenessLevel(str, Enum):
    """Níveis de completude da aplicação"""
    CRITICAL = "critical"  # < 70% - Informações insuficientes
    WARNING = "warning"    # 70-89% - Necessita melhorias
    GOOD = "good"         # 90-100% - Pronta para revisão

class FieldQuality(str, Enum):
    """Qualidade de cada campo individual"""
    MISSING = "missing"           # Campo vazio ou não fornecido
    INCOMPLETE = "incomplete"     # Fornecido mas falta detalhes
    VAGUE = "vague"              # Muito genérico ou vago
    ADEQUATE = "adequate"        # Bom, mas pode melhorar
    COMPLETE = "complete"        # Completo e detalhado

# Requisitos do USCIS por tipo de visto (baseado em informações públicas)
VISA_REQUIREMENTS = {
    "I-130": {
        "name": "Petition for Alien Relative",
        "categories": {
            "petitioner_info": {
                "name": "Informações do Peticionário",
                "required_fields": [
                    "petitioner_full_name",
                    "petitioner_dob",
                    "petitioner_citizenship_status",
                    "petitioner_address",
                    "petitioner_contact"
                ],
                "description": "Cidadão americano ou residente permanente que está peticionando"
            },
            "beneficiary_info": {
                "name": "Informações do Beneficiário",
                "required_fields": [
                    "beneficiary_full_name",
                    "beneficiary_dob",
                    "beneficiary_pob",
                    "beneficiary_current_address",
                    "beneficiary_passport"
                ],
                "description": "Parente que está sendo peticionado para imigrar"
            },
            "relationship": {
                "name": "Relacionamento",
                "required_fields": [
                    "relationship_type",
                    "marriage_date_place",
                    "relationship_evidence"
                ],
                "description": "Comprovação do relacionamento familiar"
            },
            "immigration_history": {
                "name": "Histórico de Imigração",
                "required_fields": [
                    "previous_us_visits",
                    "immigration_status",
                    "visa_history",
                    "entry_exit_dates"
                ],
                "description": "Histórico completo de imigração do beneficiário"
            }
        }
    },
    "H-1B": {
        "name": "Specialty Occupation Worker",
        "categories": {
            "personal_info": {
                "name": "Informações Pessoais",
                "required_fields": [
                    "full_name",
                    "dob",
                    "passport",
                    "current_address",
                    "education"
                ],
                "description": "Informações pessoais completas"
            },
            "employment": {
                "name": "Informações de Emprego",
                "required_fields": [
                    "employer_name",
                    "job_title",
                    "job_description",
                    "salary",
                    "work_location",
                    "start_date"
                ],
                "description": "Detalhes da oferta de emprego"
            },
            "qualifications": {
                "name": "Qualificações",
                "required_fields": [
                    "degree",
                    "field_of_study",
                    "work_experience",
                    "specialized_skills"
                ],
                "description": "Educação e experiência relevantes"
            }
        }
    },
    "I-539": {
        "name": "Application to Extend/Change Nonimmigrant Status",
        "categories": {
            "personal_info": {
                "name": "Informações Pessoais",
                "required_fields": [
                    "full_name",
                    "dob",
                    "passport",
                    "current_address",
                    "i94_number"
                ],
                "description": "Informações pessoais e I-94"
            },
            "current_status": {
                "name": "Status Atual",
                "required_fields": [
                    "current_visa_status",
                    "expiration_date",
                    "reason_for_extension",
                    "intended_departure_date"
                ],
                "description": "Status de imigração atual e razão para extensão"
            }
        }
    }
}

class CompletenessAnalyzer:
    """Analisador de completude usando IA"""
    
    def __init__(self):
        self.openai_client = openai
    
    async def analyze_field_quality(
        self,
        field_name: str,
        field_value: Any,
        field_context: str,
        visa_type: str
    ) -> Dict[str, Any]:
        """Analisa a qualidade de um campo específico"""
        
        if not field_value or str(field_value).strip() == "":
            return {
                "quality": FieldQuality.MISSING,
                "score": 0,
                "feedback": f"Campo '{field_name}' não foi fornecido.",
                "suggestion": f"Este campo é obrigatório para aplicações {visa_type}."
            }
        
        # Usar IA para analisar qualidade
        try:
            prompt = f"""
            Analise a qualidade desta informação fornecida em uma aplicação de visto {visa_type}:
            
            Campo: {field_name}
            Contexto: {field_context}
            Valor fornecido: "{field_value}"
            
            Avalie baseado em requisitos públicos do USCIS:
            1. A informação está completa?
            2. É específica o suficiente?
            3. Está no formato adequado?
            
            Responda APENAS em JSON:
            {{
                "quality": "missing|incomplete|vague|adequate|complete",
                "score": 0-100,
                "feedback": "Feedback educativo sobre o que foi fornecido",
                "suggestion": "Sugestão específica de melhoria",
                "uscis_requirement": "O que o USCIS tipicamente espera para este campo"
            }}
            
            IMPORTANTE: Seja educativo, não diretivo. Use frases como "O USCIS geralmente requer..." ao invés de "Você deve...".
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um assistente educativo sobre requisitos do USCIS. Forneça feedback baseado em informações públicas, nunca como aconselhamento jurídico."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            result_text = response.choices[0].message.content.strip()
            result_text = result_text.replace('```json', '').replace('```', '').strip()
            result = json.loads(result_text)
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing field quality: {e}")
            return {
                "quality": FieldQuality.ADEQUATE,
                "score": 70,
                "feedback": "Campo fornecido.",
                "suggestion": "Verifique se todas as informações necessárias estão incluídas.",
                "uscis_requirement": "Informação completa e precisa."
            }
    
    async def analyze_application_completeness(
        self,
        visa_type: str,
        user_data: Dict[str, Any],
        application_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analisa completude geral da aplicação"""
        
        if visa_type not in VISA_REQUIREMENTS:
            return {
                "overall_score": 50,
                "level": CompletenessLevel.WARNING,
                "message": f"Tipo de visto {visa_type} não reconhecido.",
                "categories": [],
                "recommendations": []
            }
        
        requirements = VISA_REQUIREMENTS[visa_type]
        categories_analysis = []
        total_score = 0
        total_fields = 0
        critical_issues = []
        warnings = []
        
        # Analisar cada categoria de requisitos
        for category_key, category_info in requirements["categories"].items():
            category_score = 0
            category_fields = len(category_info["required_fields"])
            field_analyses = []
            
            for field in category_info["required_fields"]:
                field_value = user_data.get(field)
                
                # Analisar qualidade do campo
                field_analysis = await self.analyze_field_quality(
                    field_name=field,
                    field_value=field_value,
                    field_context=category_info["description"],
                    visa_type=visa_type
                )
                
                field_analyses.append({
                    "field": field,
                    **field_analysis
                })
                
                category_score += field_analysis["score"]
                total_score += field_analysis["score"]
                total_fields += 1
                
                # Identificar problemas críticos
                if field_analysis["quality"] in [FieldQuality.MISSING, FieldQuality.INCOMPLETE]:
                    critical_issues.append({
                        "field": field,
                        "category": category_info["name"],
                        "issue": field_analysis["feedback"],
                        "suggestion": field_analysis["suggestion"]
                    })
                elif field_analysis["quality"] == FieldQuality.VAGUE:
                    warnings.append({
                        "field": field,
                        "category": category_info["name"],
                        "issue": field_analysis["feedback"],
                        "suggestion": field_analysis["suggestion"]
                    })
            
            category_avg = category_score / category_fields if category_fields > 0 else 0
            
            categories_analysis.append({
                "category": category_info["name"],
                "category_key": category_key,
                "description": category_info["description"],
                "score": round(category_avg, 1),
                "fields_analyzed": category_fields,
                "field_details": field_analyses
            })
        
        # Calcular score geral
        overall_score = round(total_score / total_fields if total_fields > 0 else 0, 1)
        
        # Determinar nível
        if overall_score < 70:
            level = CompletenessLevel.CRITICAL
            level_message = "🔴 Informações Insuficientes"
            level_description = "Várias informações essenciais estão faltando. Esta aplicação provavelmente será rejeitada pelo USCIS."
        elif overall_score < 90:
            level = CompletenessLevel.WARNING
            level_message = "🟡 Necessita Melhorias"
            level_description = "Informações básicas completas, mas faltam detalhes importantes."
        else:
            level = CompletenessLevel.GOOD
            level_message = "🟢 Pronta para Revisão"
            level_description = "Todas as informações essenciais fornecidas. Sugerimos revisar com advogado antes de enviar."
        
        # Gerar recomendações
        recommendations = []
        
        if critical_issues:
            recommendations.append({
                "priority": "high",
                "title": "Complete Informações Obrigatórias",
                "description": f"Existem {len(critical_issues)} campos obrigatórios que precisam de atenção imediata.",
                "action": "Revisar campos marcados em vermelho"
            })
        
        if warnings:
            recommendations.append({
                "priority": "medium",
                "title": "Melhore Detalhamento",
                "description": f"Existem {len(warnings)} campos que podem ser melhorados com mais detalhes.",
                "action": "Adicionar informações específicas aos campos marcados em amarelo"
            })
        
        if overall_score < 90:
            recommendations.append({
                "priority": "high",
                "title": "Consulte um Advogado",
                "description": "Para casos complexos, recomendamos fortemente consultar um advogado de imigração licenciado.",
                "action": "Buscar orientação profissional"
            })
        
        return {
            "overall_score": overall_score,
            "level": level,
            "level_message": level_message,
            "level_description": level_description,
            "visa_type": visa_type,
            "visa_name": requirements["name"],
            "total_fields_analyzed": total_fields,
            "critical_issues_count": len(critical_issues),
            "warnings_count": len(warnings),
            "categories": categories_analysis,
            "critical_issues": critical_issues,
            "warnings": warnings,
            "recommendations": recommendations,
            "analyzed_at": datetime.utcnow().isoformat(),
            "disclaimer": "Esta análise é educativa e baseada em requisitos públicos do USCIS. Não constitui aconselhamento jurídico. Para orientação legal, consulte um advogado de imigração licenciado."
        }
    
    def get_visa_checklist(self, visa_type: str) -> Dict[str, Any]:
        """Retorna checklist de requisitos para um tipo de visto"""
        
        if visa_type not in VISA_REQUIREMENTS:
            return {
                "success": False,
                "message": f"Tipo de visto {visa_type} não encontrado."
            }
        
        requirements = VISA_REQUIREMENTS[visa_type]
        checklist_items = []
        
        for category_key, category_info in requirements["categories"].items():
            for field in category_info["required_fields"]:
                checklist_items.append({
                    "field": field,
                    "category": category_info["name"],
                    "description": self._get_field_description(field, visa_type),
                    "required": True
                })
        
        return {
            "success": True,
            "visa_type": visa_type,
            "visa_name": requirements["name"],
            "total_items": len(checklist_items),
            "checklist_items": checklist_items,
            "source": "Baseado em requisitos públicos do USCIS",
            "disclaimer": "Este checklist é educativo. Para aplicação real, consulte os formulários oficiais do USCIS e considere orientação de advogado."
        }
    
    def _get_field_description(self, field: str, visa_type: str) -> str:
        """Retorna descrição amigável de cada campo"""
        
        descriptions = {
            "full_name": "Nome completo legal (como aparece no passaporte)",
            "dob": "Data de nascimento (MM/DD/AAAA)",
            "pob": "Local de nascimento (cidade, país)",
            "passport": "Número do passaporte válido",
            "current_address": "Endereço completo atual (rua, cidade, estado, ZIP code)",
            "petitioner_full_name": "Nome completo legal do peticionário",
            "petitioner_dob": "Data de nascimento do peticionário",
            "petitioner_citizenship_status": "Status de cidadania (cidadão americano ou residente permanente)",
            "petitioner_address": "Endereço completo do peticionário nos EUA",
            "petitioner_contact": "Telefone e email do peticionário",
            "beneficiary_full_name": "Nome completo legal do beneficiário",
            "beneficiary_dob": "Data de nascimento do beneficiário",
            "beneficiary_pob": "Local de nascimento do beneficiário",
            "beneficiary_current_address": "Endereço atual completo do beneficiário",
            "beneficiary_passport": "Número do passaporte do beneficiário",
            "relationship_type": "Tipo de relacionamento (cônjuge, filho, pai, irmão)",
            "marriage_date_place": "Data e local do casamento (se aplicável)",
            "relationship_evidence": "Evidências do relacionamento (certidões, fotos, documentos conjuntos)",
            "previous_us_visits": "Histórico de visitas anteriores aos EUA (datas)",
            "immigration_status": "Status de imigração atual e histórico",
            "visa_history": "Histórico de vistos anteriores",
            "entry_exit_dates": "Datas de entrada e saída dos EUA",
            "employer_name": "Nome completo do empregador",
            "job_title": "Título do cargo",
            "job_description": "Descrição detalhada das funções",
            "salary": "Salário anual oferecido",
            "work_location": "Local de trabalho (endereço completo)",
            "start_date": "Data de início prevista",
            "education": "Nível de educação e diploma obtido",
            "degree": "Diploma/grau acadêmico",
            "field_of_study": "Área de estudo",
            "work_experience": "Experiência de trabalho relevante",
            "specialized_skills": "Habilidades especializadas",
            "i94_number": "Número do formulário I-94",
            "current_visa_status": "Status de visto atual (B-2, F-1, etc.)",
            "expiration_date": "Data de expiração do status atual",
            "reason_for_extension": "Razão detalhada para solicitar extensão",
            "intended_departure_date": "Data prevista de saída dos EUA"
        }
        
        return descriptions.get(field, f"Informação sobre {field}")
