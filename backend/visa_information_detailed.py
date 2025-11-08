"""
Informações Detalhadas de Vistos
Separando Processo Consular vs. Mudança de Status dentro dos EUA

Este arquivo contém informações precisas sobre taxas e tempos de processamento
para cada tipo de visto, diferenciando claramente:
- Processo Consular (aplicação em consulado fora dos EUA)
- Mudança de Status (Change of Status - aplicação dentro dos EUA)
"""

VISA_DETAILED_INFO = {
    "F-1": {
        "name": "Visto de Estudante",
        "description": "Para estudos acadêmicos em instituições americanas",
        
        "processo_consular": {
            "description": "Aplicação em consulado dos EUA no Brasil (primeira vez ou renovação)",
            "tempo_processamento": "2-6 semanas",
            "tempo_detalhes": "Tempo desde agendamento de entrevista até recebimento do passaporte com visto",
            "taxas": {
                "taxa_ds160": {
                    "valor": "$185",
                    "descricao": "Taxa de aplicação do visto (MRV Fee)",
                    "pago_para": "Consulado dos EUA",
                    "quando_pagar": "Antes de agendar entrevista"
                },
                "taxa_sevis": {
                    "valor": "$350",
                    "descricao": "Taxa SEVIS I-901",
                    "pago_para": "DHS/ICE",
                    "quando_pagar": "Antes da entrevista consular"
                },
                "total": "$535"
            },
            "etapas": [
                "Obter I-20 da instituição aprovada pelo SEVP",
                "Pagar taxa SEVIS ($350)",
                "Preencher formulário DS-160",
                "Pagar taxa MRV ($185)",
                "Agendar entrevista no consulado",
                "Comparecer à entrevista com documentos",
                "Aguardar processamento (2-6 semanas)"
            ]
        },
        
        "change_of_status": {
            "description": "Mudança de status para F-1 estando JÁ nos EUA com outro visto",
            "tempo_processamento": "3-5 meses",
            "tempo_detalhes": "Tempo médio do USCIS para processar formulário I-539",
            "taxas": {
                "taxa_i539": {
                    "valor": "$370",
                    "descricao": "Taxa de processamento I-539",
                    "pago_para": "USCIS",
                    "quando_pagar": "Ao enviar aplicação"
                },
                "taxa_biometrics": {
                    "valor": "$85",
                    "descricao": "Taxa de biometria (se aplicável)",
                    "pago_para": "USCIS",
                    "quando_pagar": "Quando notificado"
                },
                "taxa_sevis": {
                    "valor": "$350",
                    "descricao": "Taxa SEVIS I-901",
                    "pago_para": "DHS/ICE",
                    "quando_pagar": "Antes de submeter I-539"
                },
                "total": "$805"
            },
            "etapas": [
                "Obter I-20 da instituição SEVP",
                "Pagar taxa SEVIS ($350)",
                "Preencher formulário I-539",
                "Juntar documentação de suporte",
                "Pagar taxa I-539 ($370)",
                "Enviar pacote ao USCIS",
                "Aguardar biometria (se necessário)",
                "Aguardar decisão (3-5 meses)"
            ],
            "requisitos_especiais": [
                "Deve aplicar ANTES do visto atual expirar",
                "Não pode viajar enquanto I-539 está pendente",
                "Se negado, deve deixar os EUA imediatamente"
            ]
        },
        
        "dependentes": "Cônjuge e filhos permitidos (F-2)",
        "trabalho": "Não permitido trabalhar off-campus (apenas on-campus após 1 ano)",
        "duracao_maxima": "Duração do programa + 60 dias de graça",
        
        "criterios_elegibilidade": [
            "Aceito em instituição educacional aprovada pelo SEVP",
            "Matrícula em programa acadêmico ou de idiomas",
            "Recursos financeiros suficientes para cobrir estudos",
            "Intenção de retornar ao país de origem após estudos"
        ]
    },
    
    "H-1B": {
        "name": "Visto de Trabalho Especializado",
        "description": "Para trabalhadores em ocupações especializadas",
        
        "processo_consular": {
            "description": "Aplicação em consulado após aprovação do I-129 pelo empregador",
            "tempo_processamento": "2-4 semanas",
            "tempo_detalhes": "Após aprovação do I-129, tempo até receber visto no passaporte",
            "taxas": {
                "taxa_ds160": {
                    "valor": "$190",
                    "descricao": "Taxa de aplicação do visto (MRV Fee)",
                    "pago_para": "Consulado dos EUA",
                    "quando_pagar": "Antes de agendar entrevista"
                },
                "total": "$190"
            },
            "etapas": [
                "Empregador obtém aprovação I-129 do USCIS",
                "Receber Notice of Approval (I-797)",
                "Preencher formulário DS-160",
                "Pagar taxa MRV ($190)",
                "Agendar entrevista no consulado",
                "Comparecer à entrevista com I-797 e documentos",
                "Aguardar processamento (2-4 semanas)"
            ]
        },
        
        "change_of_status": {
            "description": "Mudança para H-1B estando JÁ nos EUA (incluído na petition do empregador)",
            "tempo_processamento": "3-6 meses (regular) ou 15 dias úteis (premium)",
            "tempo_detalhes": "Tempo do USCIS para processar I-129 com mudança de status",
            "taxas": {
                "taxa_i129": {
                    "valor": "$460",
                    "descricao": "Taxa básica de petition",
                    "pago_para": "USCIS",
                    "pago_por": "Empregador",
                    "quando_pagar": "Ao enviar I-129"
                },
                "taxa_fraud": {
                    "valor": "$500",
                    "descricao": "Taxa de prevenção de fraude",
                    "pago_para": "USCIS",
                    "pago_por": "Empregador",
                    "quando_pagar": "Ao enviar I-129"
                },
                "taxa_acwia": {
                    "valor": "$750 ou $1,500",
                    "descricao": "Taxa ACWIA (varia por tamanho da empresa)",
                    "pago_para": "USCIS",
                    "pago_por": "Empregador",
                    "quando_pagar": "Ao enviar I-129"
                },
                "taxa_premium": {
                    "valor": "$2,500",
                    "descricao": "Premium Processing (opcional para 15 dias)",
                    "pago_para": "USCIS",
                    "pago_por": "Empregador",
                    "quando_pagar": "Ao enviar I-129 ou depois"
                },
                "total_minimo": "$1,710 (empresa pequena)",
                "total_com_premium": "$4,210 (empresa pequena) ou $4,960 (empresa grande)"
            },
            "etapas": [
                "Empregador completa Labor Condition Application (LCA)",
                "LCA aprovado pelo Department of Labor",
                "Preencher formulário I-129",
                "Juntar documentação (diploma, experiência, etc.)",
                "Pagar taxas do USCIS",
                "Enviar pacote ao USCIS",
                "Aguardar aprovação (3-6 meses ou 15 dias com premium)",
                "Se aprovado, status muda para H-1B automaticamente"
            ],
            "requisitos_especiais": [
                "Empregador deve solicitar, não o trabalhador",
                "LCA deve ser aprovado primeiro",
                "Pode começar a trabalhar assim que aprovado (não precisa viajar)",
                "Cap subject (65,000 + 20,000 mestrado) - apenas em Abril"
            ]
        },
        
        "dependentes": "Cônjuge e filhos permitidos (H-4), cônjuge pode solicitar trabalho",
        "trabalho": "Apenas para o empregador patrocinador",
        "duracao_maxima": "3 anos iniciais, prorrogável até 6 anos total",
        
        "criterios_elegibilidade": [
            "Diploma de ensino superior ou equivalente",
            "Oferta de trabalho em ocupação especializada",
            "Empregador americano deve fazer petition",
            "Labor Condition Application (LCA) aprovada"
        ]
    },
    
    "I-130": {
        "name": "Petição para Parente",
        "description": "Petição de cidadão americano ou residente permanente para parente",
        
        "processo_consular": {
            "description": "Imigração através de consulado após aprovação do I-130 e espera de visa disponível",
            "tempo_processamento": "12-36 meses",
            "tempo_detalhes": "Tempo varia muito: 12-18 meses para parentes imediatos, 2-20+ anos para outras categorias",
            "taxas": {
                "taxa_i130": {
                    "valor": "$535",
                    "descricao": "Taxa de petition I-130",
                    "pago_para": "USCIS",
                    "pago_por": "Peticionário",
                    "quando_pagar": "Ao enviar I-130"
                },
                "taxa_ds260": {
                    "valor": "$325",
                    "descricao": "Taxa de processamento de visto de imigrante",
                    "pago_para": "NVC/Consulado",
                    "pago_por": "Beneficiário",
                    "quando_pagar": "Após I-130 aprovado e visto disponível"
                },
                "taxa_affidavit": {
                    "valor": "$120",
                    "descricao": "Taxa do Affidavit of Support (I-864)",
                    "pago_para": "NVC",
                    "pago_por": "Patrocinador",
                    "quando_pagar": "Junto com DS-260"
                },
                "total": "$980"
            },
            "etapas": [
                "Peticionário envia I-130 ao USCIS",
                "USCIS processa e aprova I-130 (8-18 meses)",
                "Caso vai para National Visa Center (NVC)",
                "Aguardar visa disponível (varia por categoria)",
                "Pagar taxas do NVC ($325 + $120)",
                "Preencher DS-260 e documentação",
                "Agendar entrevista no consulado",
                "Comparecer à entrevista",
                "Receber visa de imigrante",
                "Viajar aos EUA e receber green card"
            ]
        },
        
        "change_of_status": {
            "description": "Ajuste de status para residente permanente estando JÁ nos EUA",
            "tempo_processamento": "10-24 meses",
            "tempo_detalhes": "Tempo para processar I-485 Adjustment of Status",
            "taxas": {
                "taxa_i130": {
                    "valor": "$535",
                    "descricao": "Taxa de petition I-130",
                    "pago_para": "USCIS",
                    "pago_por": "Peticionário",
                    "quando_pagar": "Ao enviar"
                },
                "taxa_i485": {
                    "valor": "$1,140 ou $1,225",
                    "descricao": "Taxa de Adjustment of Status (varia por idade)",
                    "pago_para": "USCIS",
                    "pago_por": "Beneficiário",
                    "quando_pagar": "Ao enviar I-485"
                },
                "taxa_biometrics": {
                    "valor": "$85",
                    "descricao": "Taxa de biometria",
                    "pago_para": "USCIS",
                    "pago_por": "Beneficiário",
                    "quando_pagar": "Incluída no I-485 (alguns casos)"
                },
                "taxa_ead": {
                    "valor": "$410",
                    "descricao": "Taxa de autorização de trabalho (I-765) - opcional",
                    "pago_para": "USCIS",
                    "pago_por": "Beneficiário",
                    "quando_pagar": "Se desejar trabalhar durante espera"
                },
                "taxa_ap": {
                    "valor": "$575",
                    "descricao": "Taxa de Advance Parole (I-131) - opcional",
                    "pago_para": "USCIS",
                    "pago_por": "Beneficiário",
                    "quando_pagar": "Se desejar viajar durante espera"
                },
                "total_minimo": "$1,675",
                "total_com_ead_ap": "$2,660"
            },
            "etapas": [
                "Verificar se visa está disponível",
                "Peticionário envia I-130",
                "Beneficiário envia I-485 (simultâneo ou após I-130)",
                "Pagar taxas do USCIS",
                "Submeter exame médico (I-693)",
                "Aguardar biometria",
                "Possivelmente entrevista no USCIS",
                "Aguardar decisão (10-24 meses)",
                "Se aprovado, receber green card pelo correio"
            ],
            "requisitos_especiais": [
                "Beneficiário deve estar legalmente nos EUA",
                "Parentes imediatos de cidadãos: sem fila de espera",
                "Outras categorias: deve aguardar visa disponível",
                "Pode solicitar EAD/AP enquanto aguarda",
                "Não pode viajar sem Advance Parole"
            ]
        },
        
        "dependentes": "Cônjuge e filhos menores de 21 anos podem ser incluídos",
        "trabalho": "Com green card, pode trabalhar em qualquer emprego",
        "duracao": "Permanente (green card)",
        
        "criterios_elegibilidade": [
            "Peticionário deve ser cidadão americano ou residente permanente",
            "Relacionamento familiar comprovado",
            "Peticionário deve ter renda suficiente (125% da linha da pobreza)",
            "Beneficiário deve ser admissível aos EUA"
        ]
    },
    
    "I-539": {
        "name": "Extensão/Mudança de Status de Não-Imigrante",
        "description": "Para estender ou mudar status de visto de não-imigrante",
        
        "change_of_status": {
            "description": "Aplicação para estender ou mudar status estando JÁ nos EUA",
            "tempo_processamento": "6-10 meses",
            "tempo_detalhes": "Tempo médio do USCIS para processar I-539",
            "taxas": {
                "taxa_i539": {
                    "valor": "$370",
                    "descricao": "Taxa de processamento I-539",
                    "pago_para": "USCIS",
                    "quando_pagar": "Ao enviar aplicação"
                },
                "taxa_biometrics": {
                    "valor": "$85",
                    "descricao": "Taxa de biometria (se aplicável)",
                    "pago_para": "USCIS",
                    "quando_pagar": "Quando notificado"
                },
                "total": "$455"
            },
            "etapas": [
                "Verificar elegibilidade para extensão/mudança",
                "Preencher formulário I-539",
                "Juntar documentação de suporte",
                "Pagar taxa ($370)",
                "Enviar pacote ao USCIS",
                "Aguardar recibo (2-4 semanas)",
                "Biometria se necessário",
                "Aguardar decisão (6-10 meses)"
            ],
            "requisitos_especiais": [
                "Deve aplicar ANTES do visto atual expirar (recomendado 45 dias antes)",
                "Não pode viajar enquanto pendente (pode perder aplicação)",
                "Período de graça de 60 dias se F-1 ou J-1 completa programa",
                "Se negado após expiração, deve deixar os EUA imediatamente"
            ]
        },
        
        "processo_consular": {
            "description": "Não aplicável - I-539 é apenas para quem já está nos EUA",
            "tempo_processamento": "N/A",
            "taxas": {},
            "etapas": []
        },
        
        "dependentes": "Cônjuge e filhos podem ser incluídos na mesma aplicação",
        "trabalho": "Depende do tipo de visto sendo estendido/mudado",
        "duracao": "Varia por tipo de visto",
        
        "criterios_elegibilidade": [
            "Status de não-imigrante válido",
            "Não violou condições do visto atual",
            "Razão válida para extensão/mudança",
            "Meios financeiros para se manter"
        ]
    }
}


def get_visa_processing_info(visa_type: str, process_type: str = "both") -> dict:
    """
    Retorna informações de processamento de visto
    
    Args:
        visa_type: Código do visto (F-1, H-1B, I-130, I-539)
        process_type: "consular", "change_of_status", ou "both"
    
    Returns:
        Dicionário com informações detalhadas
    """
    if visa_type not in VISA_DETAILED_INFO:
        return {"error": f"Visa type {visa_type} not found"}
    
    visa_info = VISA_DETAILED_INFO[visa_type]
    
    if process_type == "both":
        return visa_info
    elif process_type == "consular":
        return {
            "name": visa_info["name"],
            "description": visa_info["description"],
            "processo_consular": visa_info.get("processo_consular", {}),
            "dependentes": visa_info.get("dependentes"),
            "trabalho": visa_info.get("trabalho"),
            "duracao_maxima": visa_info.get("duracao_maxima"),
            "criterios_elegibilidade": visa_info.get("criterios_elegibilidade")
        }
    elif process_type == "change_of_status":
        return {
            "name": visa_info["name"],
            "description": visa_info["description"],
            "change_of_status": visa_info.get("change_of_status", {}),
            "dependentes": visa_info.get("dependentes"),
            "trabalho": visa_info.get("trabalho"),
            "duracao_maxima": visa_info.get("duracao_maxima"),
            "criterios_elegibilidade": visa_info.get("criterios_elegibilidade")
        }
    else:
        return {"error": "process_type must be 'consular', 'change_of_status', or 'both'"}
