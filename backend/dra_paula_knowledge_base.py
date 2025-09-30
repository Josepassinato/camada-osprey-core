"""
Dra. Paula B2C - Base de Conhecimento Centralizada
Sistema integrado de conhecimento especializado em imigração americana para todos os agentes de IA
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class DraPaulaKnowledgeBase:
    """
    Base de conhecimento centralizada da Dra. Paula B2C
    Contém todo o conhecimento especializado em imigração americana
    """
    
    def __init__(self):
        self.knowledge_base = self._initialize_knowledge_base()
        
    def _initialize_knowledge_base(self) -> Dict[str, Any]:
        """Inicializa a base de conhecimento completa da Dra. Paula"""
        return {
            "system_identity": {
                "name": "Dra. Paula B2C",
                "expertise": "Especialista em Imigração Americana",
                "focus": "Auto-aplicação de vistos para brasileiros",
                "experience": "Vasto conhecimento em leis de imigração dos EUA",
                "approach": "B2C (Business to Consumer) - Direto ao aplicante"
            },
            
            "visa_types_expertise": {
                "work_visas": {
                    "H1B": {
                        "description": "Visto para trabalhadores especializados",
                        "requirements": [
                            "Diploma de ensino superior ou equivalente",
                            "Oferta de trabalho em ocupação especializada",
                            "Empregador americano deve fazer petition",
                            "Labor Condition Application (LCA) aprovada"
                        ],
                        "common_issues": [
                            "Diploma não equivalente nos EUA",
                            "Função não qualifica como especializada",
                            "Salário abaixo do prevailing wage",
                            "Falta de documentação do empregador"
                        ],
                        "dra_paula_tips": [
                            "Sempre verifique se o diploma é reconhecido pelo USCIS",
                            "Solicite evaluation credencial se necessário",
                            "Empregador deve provar que a função exige nível superior",
                            "Mantenha cópias de todos os documentos da petition"
                        ],
                        "timeline": "2-4 meses (regular) ou 15 dias (premium processing)",
                        "fees": "$555 (base) + $1,500 (anti-fraud) + $4,000 (empregador com 50+ funcionários)"
                    },
                    "L1": {
                        "description": "Transferência intracompanhia",
                        "requirements": [
                            "1 ano trabalhando na empresa no exterior nos últimos 3 anos",
                            "Função executiva, gerencial ou especializada",
                            "Empresa americana relacionada à estrangeira",
                            "Transferência para posição similar ou superior"
                        ],
                        "types": {
                            "L1A": "Executivos e gerentes (até 7 anos)",
                            "L1B": "Conhecimento especializado (até 5 anos)"
                        },
                        "dra_paula_tips": [
                            "Documente bem a relação entre as empresas",
                            "Prove o conhecimento especializado com detalhes específicos",
                            "L1A tem caminho mais fácil para green card",
                            "Cônjuge L2 pode solicitar autorização de trabalho"
                        ]
                    },
                    "O1": {
                        "description": "Habilidade extraordinária",
                        "requirements": [
                            "Evidência de habilidade extraordinária",
                            "Reconhecimento nacional ou internacional",
                            "Prêmios ou conquistas significativas",
                            "Continuação do trabalho na área de expertise"
                        ],
                        "evidence_types": [
                            "Prêmios de excelência reconhecidos",
                            "Publicações sobre o trabalho",
                            "Participação como juiz/avaliador",
                            "Contribuições originais significativas",
                            "Artigos autorais em publicações profissionais",
                            "Salário elevado comparado aos pares",
                            "Participação em organizações de elite"
                        ],
                        "dra_paula_tips": [
                            "Precisa de pelo menos 3 dos 8 critérios do USCIS",
                            "Qualidade da evidência é mais importante que quantidade",
                            "Cartas de recomendação devem ser de especialistas reconhecidos",
                            "Organize evidências por categoria para facilitar análise"
                        ]
                    }
                },
                "family_visas": {
                    "I130": {
                        "description": "Petição para parente imediato",
                        "petitioners": [
                            "Cidadão americano para cônjuge, filhos solteiros menores de 21, pais",
                            "Residente permanente para cônjuge, filhos solteiros"
                        ],
                        "categories": {
                            "immediate_relatives": "Sem limite numérico anual",
                            "preference_categories": "Sujeito a limite numérico e country cap"
                        },
                        "dra_paula_tips": [
                            "Relationship evidence é crucial - quanto mais, melhor",
                            "Para casamento: fotos, viagens juntos, contas conjuntas",
                            "Para filhos: certidões de nascimento com traduções",
                            "Acompanhe priority dates se não for parente imediato"
                        ]
                    },
                    "K1": {
                        "description": "Visto de noivo(a)",
                        "requirements": [
                            "Peticionário deve ser cidadão americano",
                            "Casal deve ter se encontrado pessoalmente nos últimos 2 anos",
                            "Ambos livres para casar",
                            "Intenção genuine de casar dentro de 90 dias"
                        ],
                        "dra_paula_tips": [
                            "Documente bem o relacionamento com fotos e comunicações",
                            "Exceções ao requisito de encontro são raríssimas",
                            "Prepare-se para entrevista no consulado - seja honesto",
                            "Após entrada nos EUA, tem 90 dias para casar"
                        ]
                    }
                },
                "temporary_visas": {
                    "B1B2": {
                        "description": "Negócios e turismo",
                        "purposes": {
                            "B1": "Reuniões, conferências, consultas, treinamentos",
                            "B2": "Turismo, visitas familiares, tratamento médico"
                        },
                        "key_factors": [
                            "Intenção de retornar ao Brasil",
                            "Vínculos fortes com país de origem",
                            "Recursos financeiros suficientes",
                            "Propósito legítimo da viagem"
                        ],
                        "dra_paula_tips": [
                            "Demonstre vínculos com Brasil: emprego, família, propriedades",
                            "Leve documentos financeiros dos últimos 3 meses",
                            "Seja específico sobre o propósito da viagem",
                            "Não minta na entrevista - honestidade é fundamental",
                            "ESTA pode ser mais conveniente para turismo"
                        ],
                        "common_mistakes": [
                            "Não demonstrar intenção de retorno",
                            "Recursos financeiros insuficientes ou não comprovados",
                            "Inconsistências nas informações",
                            "Propósito vago da viagem"
                        ]
                    },
                    "F1": {
                        "description": "Estudante acadêmico",
                        "requirements": [
                            "Aceitação em instituição SEVP-aprovada",
                            "Formulário I-20 válido",
                            "Recursos financeiros para estudos",
                            "Intenção de retornar ao país após estudos"
                        ],
                        "dra_paula_tips": [
                            "Pague taxa SEVIS antes da entrevista consular",
                            "Mantenha status com pelo menos 12 créditos por semestre",
                            "OPT permite trabalho após graduação",
                            "STEM fields têm extensão de OPT para 24 meses adicionais"
                        ]
                    }
                }
            },
            
            "uscis_procedures": {
                "form_filing": {
                    "general_tips": [
                        "Sempre use tinta preta ou azul",
                        "Preencha todos os campos - use N/A se não aplicável",
                        "Assine e date todos os formulários",
                        "Mantenha cópias de tudo que enviar",
                        "Use correio certificado com recibo de entrega"
                    ],
                    "payment_methods": [
                        "Cashier's check ou money order para USCIS",
                        "Não envie dinheiro vivo",
                        "Cheque pessoal pode ser rejeitado",
                        "Credit card online apenas para alguns serviços"
                    ]
                },
                "document_requirements": {
                    "translations": "Todos os documentos em língua estrangeira devem ter tradução certificada",
                    "originals_vs_copies": "Envie cópias legíveis, mantenha originais",
                    "certification": "Alguns documentos precisam de certificação consular",
                    "expiration": "Documentos com data de validade devem estar vigentes"
                }
            },
            
            "brazilian_specific_guidance": {
                "common_documents": {
                    "certidao_nascimento": {
                        "translation_needed": True,
                        "apostille_required": "Sim, após 2016",
                        "dra_paula_note": "Certidão deve ser recente (máximo 1 ano para alguns casos)"
                    },
                    "certidao_casamento": {
                        "translation_needed": True,
                        "apostille_required": "Sim, após 2016",
                        "dra_paula_note": "Se divorciado, inclua certidão de divórcio também"
                    },
                    "diploma_universitario": {
                        "translation_needed": True,
                        "evaluation_needed": "Para H1B e casos profissionais",
                        "dra_paula_note": "WES, ECE ou AACRAO são avaliadores reconhecidos"
                    },
                    "antecedentes_criminais": {
                        "federal_and_state": "Ambos necessários",
                        "validity": "6 meses para imigração",
                        "dra_paula_note": "PF online é aceito se for recente"
                    }
                },
                "financial_evidence": {
                    "bank_statements": "3 meses mais recentes",
                    "income_tax": "Declaração de IR atual",
                    "employment_letter": "Carta do empregador com salário",
                    "dra_paula_tip": "Converta valores para USD para facilitar análise"
                }
            },
            
            "common_problems_solutions": {
                "inadmissibility_issues": {
                    "overstay": {
                        "problem": "Permanência irregular anterior nos EUA",
                        "solution": "Pode precisar de waiver I-601 dependendo do tempo",
                        "dra_paula_advice": "Seja honesto sobre histórico - omissão piora situação"
                    },
                    "criminal_history": {
                        "problem": "Histórico criminal mesmo que minor",
                        "solution": "Pode precisar de waiver dependendo do crime",
                        "dra_paula_advice": "Consulte advogado para crimes, não tente resolver sozinho"
                    },
                    "public_charge": {
                        "problem": "Risco de se tornar encargo público",
                        "solution": "Affidavit of Support e evidências financeiras robustas",
                        "dra_paula_advice": "Form I-864 deve ser preenchido corretamente pelo sponsor"
                    }
                }
            },
            
            "legal_disclaimers": {
                "primary": "Esta é uma ferramenta de apoio tecnológico. Não constitui consultoria jurídica.",
                "recommendation": "Sempre consulte um advogado qualificado para casos complexos.",
                "liability": "Dra. Paula B2C é um assistente virtual - orientações são baseadas em regulamentações gerais do USCIS.",
                "updates": "Leis de imigração mudam frequentemente. Verifique informações atualizadas no site oficial do USCIS."
            }
        }
    
    def get_system_prompt_enhancement(self, agent_type: str = "general") -> str:
        """
        Retorna prompt enhancement com conhecimento da Dra. Paula para qualquer agente
        """
        identity = self.knowledge_base["system_identity"]
        disclaimers = self.knowledge_base["legal_disclaimers"]
        
        enhancement = f"""
        
        [KNOWLEDGE BASE INTEGRATION - DRA. PAULA B2C]
        
        Você tem acesso completo ao conhecimento especializado da {identity['name']}, {identity['expertise']}.
        
        ESPECIALIDADES INTEGRADAS:
        - Vistos de trabalho (H1-B, L1, O1) com requisitos específicos e tips práticos
        - Vistos familiares (I-130, K1) com evidências necessárias
        - Vistos temporários (B1/B2, F1) com fatores críticos de aprovação
        - Procedimentos USCIS e documentação para brasileiros
        - Soluções para problemas comuns de inadmissibilidade
        
        DIRETRIZES DRA. PAULA INTEGRADAS:
        - Sempre forneça orientações baseadas em regulamentações atuais do USCIS
        - Identifique problemas potenciais e ofereça soluções práticas
        - Use linguagem clara em português brasileiro
        - Foque em auto-aplicação sem advogado quando apropriado
        - Inclua tips específicos para brasileiros (documentos, apostille, traduções)
        
        IMPORTANTE: {disclaimers['primary']} {disclaimers['recommendation']}
        
        Use este conhecimento para fornecer respostas mais precisas e específicas sobre imigração americana.
        """
        
        return enhancement
    
    def get_visa_specific_knowledge(self, visa_type: str) -> Dict[str, Any]:
        """Retorna conhecimento específico para um tipo de visto"""
        visa_type = visa_type.upper().replace("-", "").replace("/", "")
        
        # Mapear códigos de visto para estrutura da base de conhecimento
        visa_mapping = {
            "H1B": ["work_visas", "H1B"],
            "L1": ["work_visas", "L1"],
            "O1": ["work_visas", "O1"],
            "I130": ["family_visas", "I130"],
            "K1": ["family_visas", "K1"],
            "B1B2": ["temporary_visas", "B1B2"],
            "F1": ["temporary_visas", "F1"]
        }
        
        if visa_type in visa_mapping:
            category, specific_visa = visa_mapping[visa_type]
            return self.knowledge_base["visa_types_expertise"].get(category, {}).get(specific_visa, {})
        
        return {}
    
    def get_document_guidance(self, document_type: str = None) -> Dict[str, Any]:
        """Retorna orientações sobre documentos brasileiros"""
        if document_type:
            return self.knowledge_base["brazilian_specific_guidance"]["common_documents"].get(document_type, {})
        
        return self.knowledge_base["brazilian_specific_guidance"]
    
    def get_problem_solution(self, issue_type: str) -> Dict[str, Any]:
        """Retorna soluções para problemas comuns"""
        return self.knowledge_base["common_problems_solutions"].get("inadmissibility_issues", {}).get(issue_type, {})
    
    def get_enhanced_prompt_for_agent(self, agent_type: str, specific_context: str = "") -> str:
        """
        Gera prompt aprimorado com conhecimento da Dra. Paula para qualquer agente específico
        """
        base_enhancement = self.get_system_prompt_enhancement(agent_type)
        
        if agent_type == "document_validation":
            specific_knowledge = """
            
            [VALIDAÇÃO DE DOCUMENTOS - CONHECIMENTO DRA. PAULA]
            - Certidões brasileiras precisam apostille (Haia) após 2016
            - Traduções devem ser certificadas por tradutor qualificado
            - Diplomas universitários podem precisar de evaluation para H1B
            - Antecedentes criminais: federal E estadual, válidos por 6 meses
            - Extratos bancários: 3 meses mais recentes
            - Declaração de IR: ano mais recente
            """
        elif agent_type == "form_generation":
            specific_knowledge = """
            
            [GERAÇÃO DE FORMULÁRIOS - CONHECIMENTO DRA. PAULA]
            - Datas sempre em formato MM/DD/YYYY para formulários USCIS
            - Campos obrigatórios: nunca deixar em branco, usar N/A se não aplicável
            - Nomes devem estar exatamente como no passaporte
            - Endereços americanos seguem formato específico (Street, City, State, ZIP)
            - Sempre incluir disclaimer sobre não constituir consultoria jurídica
            """
        elif agent_type == "consistency_check":
            specific_knowledge = """
            
            [VERIFICAÇÃO DE CONSISTÊNCIA - CONHECIMENTO DRA. PAULA]
            - Nomes devem ser consistentes em todos os formulários e documentos
            - Datas de nascimento, casamento devem coincidir com certidões
            - Histórico de trabalho deve ser cronológico e sem gaps grandes
            - Informações financeiras devem ser realistas e comprovadas
            - Endereços devem ser consistentes e atuais
            """
        else:
            specific_knowledge = ""
        
        return base_enhancement + specific_knowledge + specific_context

# Instância global da base de conhecimento
dra_paula_knowledge = DraPaulaKnowledgeBase()

def get_dra_paula_enhanced_prompt(agent_type: str = "general", context: str = "") -> str:
    """Função utilitária para obter prompt aprimorado com conhecimento da Dra. Paula"""
    return dra_paula_knowledge.get_enhanced_prompt_for_agent(agent_type, context)

def get_visa_knowledge(visa_type: str) -> Dict[str, Any]:
    """Função utilitária para obter conhecimento específico de visto"""
    return dra_paula_knowledge.get_visa_specific_knowledge(visa_type)