"""
Inadmissibility Screening System
Triage inicial para detectar casos que requerem advogado
Baseado em INA §212 (Inadmissibilidades)
"""

import logging
from enum import Enum
from typing import Dict, List

logger = logging.getLogger(__name__)


class InadmissibilityCategory(str, Enum):
    """Categorias de inadmissibilidade conforme INA §212"""
    HEALTH = "health"  # Doenças comunicáveis
    CRIMINAL = "criminal"  # Antecedentes criminais
    SECURITY = "security"  # Segurança nacional/terrorismo
    PUBLIC_CHARGE = "public_charge"  # Carga pública
    LABOR = "labor"  # Certificação de trabalho
    ILLEGAL_ENTRY = "illegal_entry"  # Entrada ilegal
    DOCUMENTATION = "documentation"  # Documentação inadequada
    INELIGIBLE_CITIZENSHIP = "ineligible_citizenship"  # Cidadania inelegível
    PREVIOUSLY_REMOVED = "previously_removed"  # Previamente deportado
    UNLAWFUL_PRESENCE = "unlawful_presence"  # Permanência ilegal
    FRAUD = "fraud"  # Fraude ou deturpação
    OTHER = "other"  # Outras inadmissibilidades


class RiskLevel(str, Enum):
    """Nível de risco do caso"""
    LOW = "low"  # Caso simples, pode usar plataforma
    MEDIUM = "medium"  # Caso com complicações, advogado recomendado
    HIGH = "high"  # Caso complexo, advogado OBRIGATÓRIO
    CRITICAL = "critical"  # Inadmissibilidade grave, consulta imediata


class InadmissibilityScreening:
    """Sistema de triagem de inadmissibilidade"""
    
    def __init__(self):
        # Perguntas críticas de triagem
        self.screening_questions = [
            {
                "id": "visa_denial",
                "question": "Você já teve algum visto negado?",
                "category": InadmissibilityCategory.DOCUMENTATION,
                "risk_if_yes": RiskLevel.MEDIUM,
                "follow_up": "Quando foi negado e qual foi o motivo?"
            },
            {
                "id": "visa_revocation",
                "question": "Você já teve um visto revogado ou cancelado?",
                "category": InadmissibilityCategory.DOCUMENTATION,
                "risk_if_yes": RiskLevel.HIGH,
                "follow_up": "Por que seu visto foi revogado?"
            },
            {
                "id": "unlawful_presence",
                "question": "Você já ficou ilegalmente nos EUA (overstay)?",
                "category": InadmissibilityCategory.UNLAWFUL_PRESENCE,
                "risk_if_yes": RiskLevel.HIGH,
                "follow_up": "Por quanto tempo ficou além do permitido?"
            },
            {
                "id": "deportation",
                "question": "Você já foi deportado ou removido dos EUA?",
                "category": InadmissibilityCategory.PREVIOUSLY_REMOVED,
                "risk_if_yes": RiskLevel.CRITICAL,
                "follow_up": "Quando foi deportado e qual foi o motivo?"
            },
            {
                "id": "criminal_record",
                "question": "Você tem antecedentes criminais (em qualquer país)?",
                "category": InadmissibilityCategory.CRIMINAL,
                "risk_if_yes": RiskLevel.HIGH,
                "follow_up": "Qual foi a natureza do crime?"
            },
            {
                "id": "fraud",
                "question": "Você já cometeu fraude de visto ou forneceu informações falsas?",
                "category": InadmissibilityCategory.FRAUD,
                "risk_if_yes": RiskLevel.CRITICAL,
                "follow_up": "Quando isso ocorreu?"
            },
            {
                "id": "communicable_disease",
                "question": "Você tem alguma doença comunicável (tuberculose, HIV não tratado, etc.)?",
                "category": InadmissibilityCategory.HEALTH,
                "risk_if_yes": RiskLevel.MEDIUM,
                "follow_up": "Você está em tratamento?"
            },
            {
                "id": "drug_abuse",
                "question": "Você tem histórico de abuso de drogas ou foi condenado por tráfico?",
                "category": InadmissibilityCategory.CRIMINAL,
                "risk_if_yes": RiskLevel.CRITICAL,
                "follow_up": "Forneça detalhes"
            },
            {
                "id": "terrorism",
                "question": "Você esteve envolvido com atividades terroristas ou organizações terroristas?",
                "category": InadmissibilityCategory.SECURITY,
                "risk_if_yes": RiskLevel.CRITICAL,
                "follow_up": "Este é um caso extremamente sério"
            },
            {
                "id": "public_charge",
                "question": "Você recebeu assistência pública (welfare) nos últimos 3 anos?",
                "category": InadmissibilityCategory.PUBLIC_CHARGE,
                "risk_if_yes": RiskLevel.MEDIUM,
                "follow_up": "Que tipo de assistência?"
            },
            {
                "id": "marriage_fraud",
                "question": "Você já se casou apenas para obter benefícios de imigração?",
                "category": InadmissibilityCategory.FRAUD,
                "risk_if_yes": RiskLevel.CRITICAL,
                "follow_up": "Este é um caso muito sério"
            },
            {
                "id": "previous_eoir_proceedings",
                "question": "Você já esteve em processo de remoção/deportação perante um juiz de imigração?",
                "category": InadmissibilityCategory.PREVIOUSLY_REMOVED,
                "risk_if_yes": RiskLevel.CRITICAL,
                "follow_up": "Qual foi o resultado?"
            },
            {
                "id": "entry_without_inspection",
                "question": "Você já entrou nos EUA sem inspeção (ilegalmente)?",
                "category": InadmissibilityCategory.ILLEGAL_ENTRY,
                "risk_if_yes": RiskLevel.HIGH,
                "follow_up": "Quando e como entrou?"
            },
            {
                "id": "misrepresentation",
                "question": "Você já mentiu para um oficial de imigração ou em uma aplicação?",
                "category": InadmissibilityCategory.FRAUD,
                "risk_if_yes": RiskLevel.CRITICAL,
                "follow_up": "O que foi dito/escrito?"
            }
        ]
    
    def get_screening_questions(self) -> List[Dict]:
        """Retorna lista de perguntas de triagem"""
        return [
            {
                "id": q["id"],
                "question": q["question"],
                "type": "yes_no"
            }
            for q in self.screening_questions
        ]
    
    def assess_risk(self, answers: Dict[str, str]) -> Dict[str, any]:
        """
        Avalia risco baseado nas respostas
        
        Args:
            answers: {"question_id": "yes"/"no"}
        
        Returns:
            {
                "risk_level": RiskLevel,
                "inadmissibilities": List[InadmissibilityCategory],
                "requires_attorney": bool,
                "recommendations": List[str],
                "follow_up_questions": List[str]
            }
        """
        inadmissibilities = []
        risk_scores = {
            RiskLevel.LOW: 0,
            RiskLevel.MEDIUM: 1,
            RiskLevel.HIGH: 3,
            RiskLevel.CRITICAL: 5
        }
        
        total_risk = 0
        follow_ups = []
        issues = []
        
        for question in self.screening_questions:
            q_id = question["id"]
            answer = answers.get(q_id, "no").lower()
            
            if answer == "yes":
                # Adicionar categoria de inadmissibilidade
                inadmissibilities.append(question["category"])
                
                # Adicionar risco
                risk = question["risk_if_yes"]
                total_risk += risk_scores[risk]
                
                # Adicionar follow-up
                if question.get("follow_up"):
                    follow_ups.append({
                        "question_id": q_id,
                        "follow_up": question["follow_up"]
                    })
                
                # Registrar issue
                issues.append({
                    "question": question["question"],
                    "category": question["category"].value,
                    "risk": risk.value
                })
        
        # Determinar nível de risco geral
        if total_risk == 0:
            overall_risk = RiskLevel.LOW
        elif total_risk <= 2:
            overall_risk = RiskLevel.MEDIUM
        elif total_risk <= 5:
            overall_risk = RiskLevel.HIGH
        else:
            overall_risk = RiskLevel.CRITICAL
        
        # Gerar recomendações
        recommendations = self._generate_recommendations(overall_risk, inadmissibilities, issues)
        
        # Determinar se requer advogado
        requires_attorney = overall_risk in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        
        result = {
            "risk_level": overall_risk.value,
            "inadmissibilities": list(set([i.value for i in inadmissibilities])),
            "requires_attorney": requires_attorney,
            "can_proceed": overall_risk in [RiskLevel.LOW, RiskLevel.MEDIUM],
            "recommendations": recommendations,
            "follow_up_questions": follow_ups,
            "issues_detected": issues,
            "total_risk_score": total_risk
        }
        
        logger.info(f"📊 Inadmissibility screening completed: risk={overall_risk.value}, issues={len(issues)}")
        
        return result
    
    def _generate_recommendations(
        self, 
        risk: RiskLevel, 
        inadmissibilities: List[InadmissibilityCategory],
        issues: List[Dict]
    ) -> List[str]:
        """Gera recomendações baseadas no risco"""
        recommendations = []
        
        if risk == RiskLevel.LOW:
            recommendations.append("✅ Seu caso parece direto. Você pode usar nossa plataforma com segurança.")
            recommendations.append("💡 Certifique-se de ter todos os documentos necessários.")
            recommendations.append("📚 Revise cuidadosamente todas as informações antes de enviar.")
        
        elif risk == RiskLevel.MEDIUM:
            recommendations.append("⚠️ Seu caso tem algumas complicações.")
            recommendations.append("💡 RECOMENDAMOS FORTEMENTE consultar um advogado de imigração.")
            recommendations.append("✅ Se decidir prosseguir sozinho, revise tudo MUITO cuidadosamente.")
            recommendations.append("📞 Considere pelo menos uma consulta com advogado antes de submeter.")
        
        elif risk == RiskLevel.HIGH:
            recommendations.append("🚨 Seu caso é COMPLEXO e requer atenção de advogado.")
            recommendations.append("❌ NÃO RECOMENDAMOS usar nossa plataforma sem orientação legal.")
            recommendations.append("⚖️ Um advogado pode:")
            recommendations.append("   - Avaliar suas chances reais")
            recommendations.append("   - Identificar problemas que você pode não ver")
            recommendations.append("   - Recomendar estratégias legais")
            recommendations.append("   - Representá-lo se necessário")
            recommendations.append("📞 CONSULTE UM ADVOGADO antes de prosseguir.")
        
        elif risk == RiskLevel.CRITICAL:
            recommendations.append("🚨🚨 ATENÇÃO: Seu caso tem inadmissibilidades GRAVES.")
            recommendations.append("⛔ NÃO PROSSIGA sem advogado.")
            recommendations.append("⚖️ Você PRECISA de representação legal IMEDIATA.")
            recommendations.append("⚠️ Aplicar sem orientação adequada pode:")
            recommendations.append("   - Resultar em negação permanente")
            recommendations.append("   - Piorar sua situação")
            recommendations.append("   - Levar a processos de remoção")
            recommendations.append("📞 CONSULTE UM ADVOGADO IMEDIATAMENTE.")
            recommendations.append("🔍 Considere advogado especializado em:")
            
            if InadmissibilityCategory.CRIMINAL in inadmissibilities:
                recommendations.append("   - Casos criminais de imigração")
            if InadmissibilityCategory.FRAUD in inadmissibilities:
                recommendations.append("   - Waivers de fraude")
            if InadmissibilityCategory.PREVIOUSLY_REMOVED in inadmissibilities:
                recommendations.append("   - Reentrada após deportação")
        
        # Adicionar recomendações específicas por categoria
        if InadmissibilityCategory.UNLAWFUL_PRESENCE in inadmissibilities:
            recommendations.append("\n📋 Sobre permanência ilegal (unlawful presence):")
            recommendations.append("   - 180-364 dias = bar de 3 anos")
            recommendations.append("   - 365+ dias = bar de 10 anos")
            recommendations.append("   - Pode precisar de waiver (I-601)")
        
        if InadmissibilityCategory.CRIMINAL in inadmissibilities:
            recommendations.append("\n⚖️ Sobre antecedentes criminais:")
            recommendations.append("   - Nem todos os crimes são inadmissibilidades")
            recommendations.append("   - Advogado pode avaliar se aplica a você")
            recommendations.append("   - Pode precisar de waiver criminal")
        
        return recommendations


# Global instance
screening = InadmissibilityScreening()


def perform_screening(answers: Dict[str, str]) -> Dict:
    """
    Helper function para realizar triagem
    
    Args:
        answers: {"question_id": "yes"/"no"}
    
    Returns:
        Resultado da triagem com recomendações
    """
    return screening.assess_risk(answers)


# Example usage
if __name__ == "__main__":
    # Test case 1: Low risk
    test_answers_low = {
        q["id"]: "no" for q in screening.screening_questions
    }
    result = perform_screening(test_answers_low)
    logger.info("=== LOW RISK TEST ===")
    logger.info(f"Risk: {result['risk_level']}")
    logger.info(f"Can proceed: {result['can_proceed']}")
    logger.info("\n".join(result['recommendations']))
    
    # Test case 2: High risk
    test_answers_high = {
        "visa_denial": "yes",
        "unlawful_presence": "yes",
        "criminal_record": "yes"
    }
    for q in screening.screening_questions:
        if q["id"] not in test_answers_high:
            test_answers_high[q["id"]] = "no"
    
    result = perform_screening(test_answers_high)
    logger.info("\n\n=== HIGH RISK TEST ===")
    logger.info(f"Risk: {result['risk_level']}")
    logger.info(f"Requires attorney: {result['requires_attorney']}")
    logger.info(f"Can proceed: {result['can_proceed']}")
    logger.info("\n".join(result['recommendations']))
