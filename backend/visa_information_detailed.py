"""
Informações Detalhadas de Vistos - APENAS MUDANÇA DE STATUS
Sistema focado em pessoas JÁ nos Estados Unidos que precisam mudar status
"""

VISA_DETAILED_INFO = {
    "F-1": {
        "name": "Visto de Estudante",
        "description": "Para mudança de status para estudos acadêmicos em instituições americanas",
        
        "change_of_status": {
            "description": "Mudança para F-1 estando JÁ nos EUA (por exemplo, de B-2 para F-1)",
            "tempo_processamento": "3-5 meses",
            "tempo_detalhes": "Tempo médio do USCIS para processar I-539 para mudança para F-1",
            "taxas": {
                "taxa_i539": {
                    "valor": "$370",
                    "descricao": "Taxa de processamento I-539",
                    "pago_para": "USCIS",
                    "quando_pagar": "Ao enviar aplicação"
                },
                "taxa_biometrics": {
                    "valor": "$85",
                    "descricao": "Taxa de biometria",
                    "pago_para": "USCIS",
                    "quando_pagar": "Se solicitado pelo USCIS"
                },
                "taxa_sevis": {
                    "valor": "$350",
                    "descricao": "Taxa SEVIS I-901",
                    "pago_para": "DHS/ICE",
                    "quando_pagar": "Antes de enviar I-539"
                },
                "total": "$805"
            },
            "etapas": [
                "Obter I-20 de instituição aprovada pelo SEVIS",
                "Pagar taxa SEVIS I-901 ($350)",
                "Preencher formulário I-539",
                "Pagar taxa USCIS ($370 + $85 se biometria)",
                "Enviar pacote ao USCIS",
                "Aguardar decisão (3-5 meses)",
                "Não viajar enquanto pedido está pendente"
            ],
            "requisitos_especiais": [
                "Deve estar nos EUA legalmente",
                "I-20 válido de escola certificada SEVIS",
                "Provar intenção de retorno após estudos",
                "Demonstrar capacidade financeira",
                "Não pode trabalhar sem autorização (OPT/CPT)"
            ]
        },
        
        "dependentes": "Cônjuge e filhos (F-2)",
        "trabalho": "Permitido campus (20h/semana) ou OPT após conclusão",
        "duracao_maxima": "Duração do programa + 60 dias",
        
        "criterios_elegibilidade": [
            "Aceito em instituição certificada SEVP",
            "Capacidade financeira para estudos",
            "Residência no exterior mantida",
            "Proficiência em inglês",
            "Intenção de retorno ao país de origem após estudos"
        ]
    },
    
    "H-1B": {
        "name": "Visto de Trabalho Especializado",
        "description": "Para mudança de status para trabalho que requer conhecimento especializado",
        
        "change_of_status": {
            "description": "Mudança para H-1B estando JÁ nos EUA com outro visto",
            "tempo_processamento": "2-4 meses (ou 15 dias com premium)",
            "tempo_detalhes": "Tempo do USCIS para processar I-129 com mudança de status",
            "taxas": {
                "taxa_i129": {
                    "valor": "$460",
                    "descricao": "Taxa de processamento I-129",
                    "pago_para": "USCIS",
                    "quando_pagar": "Ao enviar petição"
                },
                "taxa_fraude": {
                    "valor": "$500",
                    "descricao": "Taxa de prevenção de fraude",
                    "pago_para": "USCIS",
                    "quando_pagar": "Junto com I-129"
                },
                "taxa_premium": {
                    "valor": "$2,805",
                    "descricao": "Premium Processing (opcional - resposta em 15 dias)",
                    "pago_para": "USCIS",
                    "quando_pagar": "Se desejar processamento acelerado"
                },
                "total": "$960 (ou $3,765 com premium)"
            },
            "etapas": [
                "Empregador submete petição I-129 ao USCIS",
                "Pagar taxas ($460 + $500)",
                "Aguardar decisão (2-4 meses ou 15 dias com premium)",
                "Receber I-797 de aprovação",
                "Começar trabalho na data aprovada",
                "Não viajar enquanto pendente sem visto H-1B"
            ],
            "requisitos_especiais": [
                "Empregador deve patrocinar",
                "Posição requer bacharel ou superior",
                "Salário prevailing wage",
                "Cap lottery (65k geral + 20k mestrados dos EUA) se aplicável"
            ]
        },
        
        "dependentes": "Cônjuge e filhos menores (H-4)",
        "trabalho": "Apenas para empregador patrocinador",
        "duracao_maxima": "3 anos, renovável até 6 anos total",
        
        "criterios_elegibilidade": [
            "Bacharel ou superior",
            "Trabalho requer conhecimento especializado",
            "Oferta de emprego de empregador dos EUA",
            "Qualificações equivalentes aceitas",
            "Salário adequado (prevailing wage)"
        ]
    },
    
    "I-130": {
        "name": "Petição para Familiar Imediato ou Parente",
        "description": "Para petição de familiar para Green Card",
        
        "change_of_status": {
            "description": "Petição I-130 é o primeiro passo para Green Card via família",
            "tempo_processamento": "10-24 meses",
            "tempo_detalhes": "Tempo varia muito por centro do USCIS e categoria (imediato vs preferência)",
            "taxas": {
                "taxa_i130": {
                    "valor": "$535",
                    "descricao": "Taxa de processamento I-130",
                    "pago_para": "USCIS",
                    "quando_pagar": "Ao enviar petição"
                },
                "total": "$535"
            },
            "etapas": [
                "Cidadão/residente permanente arquiva I-130",
                "Pagar taxa ($535)",
                "Juntar evidências de relação familiar",
                "Enviar ao USCIS",
                "Aguardar aprovação (10-24 meses)",
                "Se imediato: pode arquivar I-485 simultaneamente",
                "Se preferência: aguardar priority date ficar current"
            ],
            "requisitos_especiais": [
                "Peticionário deve ser cidadão ou residente permanente",
                "Comprovar relação familiar válida",
                "Documentos de nascimento, casamento, etc.",
                "Familiares imediatos não têm fila (cônjuge, pais, filhos menores)",
                "Outros parentes têm categorias de preferência com fila"
            ]
        },
        
        "dependentes": "Depende da categoria (cônjuge, filhos podem derivar)",
        "trabalho": "Não permite trabalho até I-485 com EAD",
        "duracao_maxima": "Petição válida, mas não é status - precisa I-485 ou processo consular",
        
        "criterios_elegibilidade": [
            "Peticionário cidadão ou residente permanente",
            "Relação familiar qualificante",
            "Casamento genuíno (se baseado em casamento)",
            "Documentação comprovando relação",
            "Peticionário com capacidade financeira (I-864)"
        ]
    },
    
    "I-539": {
        "name": "Extensão/Mudança de Status de Não-Imigrante",
        "description": "Para estender permanência ou mudar para outro status de não-imigrante",
        
        "change_of_status": {
            "description": "Extensão ou mudança de status estando JÁ nos EUA",
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
                    "quando_pagar": "Se solicitado pelo USCIS"
                },
                "total": "$455"
            },
            "etapas": [
                "Determinar elegibilidade para extensão/mudança",
                "Preencher formulário I-539",
                "Juntar documentação de suporte",
                "Pagar taxa ($370 + $85 se biometria)",
                "Enviar ao USCIS ANTES do visto expirar",
                "Aguardar decisão (6-10 meses)",
                "Período de graça automático de 240 dias se aplicado a tempo"
            ],
            "requisitos_especiais": [
                "Aplicar ANTES de I-94 expirar",
                "Manter status válido",
                "Razão válida para extensão/mudança",
                "Não ter violado condições do visto anterior",
                "Comprovante financeiro"
            ]
        },
        
        "dependentes": "Cônjuge e filhos podem ser incluídos na mesma aplicação",
        "trabalho": "Depende do tipo de visto sendo estendido/mudado",
        "duracao_maxima": "Varia por tipo de visto",
        
        "criterios_elegibilidade": [
            "Status de não-imigrante válido",
            "Não violou condições do visto atual",
            "Razão válida para extensão/mudança",
            "Meios financeiros para se manter"
        ]
    },
    
    "O-1": {
        "name": "Visto de Habilidade Extraordinária",
        "description": "Para mudança de status para indivíduos com habilidades extraordinárias",
        
        "change_of_status": {
            "description": "Mudança para O-1 estando JÁ nos EUA com outro visto",
            "tempo_processamento": "2-4 meses (ou 15 dias com premium processing)",
            "tempo_detalhes": "Tempo do USCIS para processar I-129",
            "taxas": {
                "taxa_i129": {
                    "valor": "$460",
                    "descricao": "Taxa de processamento I-129",
                    "pago_para": "USCIS",
                    "quando_pagar": "Ao enviar petição"
                },
                "taxa_fraude": {
                    "valor": "$500",
                    "descricao": "Taxa de prevenção de fraude",
                    "pago_para": "USCIS",
                    "quando_pagar": "Junto com I-129"
                },
                "taxa_premium": {
                    "valor": "$2,805",
                    "descricao": "Premium Processing (opcional - resposta em 15 dias)",
                    "pago_para": "USCIS",
                    "quando_pagar": "Se desejar processamento acelerado"
                },
                "total": "$960 (ou $3,765 com premium)"
            },
            "etapas": [
                "Empregador/Agente submete I-129 com evidências",
                "Pagar taxas ($460 + $500)",
                "Incluir evidências de habilidade extraordinária",
                "Aguardar decisão (2-4 meses ou 15 dias com premium)",
                "Receber I-797 de aprovação",
                "Começar trabalho na data aprovada"
            ],
            "requisitos_especiais": [
                "Deve ter oferta de emprego/contrato nos EUA",
                "Evidências extensivas de reconhecimento na área",
                "Cartas de suporte de experts",
                "Não pode viajar enquanto pendente sem Advance Parole"
            ]
        },
        
        "dependentes": "Cônjuge e filhos menores (O-3)",
        "trabalho": "Apenas para empregador/projeto aprovado",
        "duracao_maxima": "Até 3 anos, renovável",
        
        "criterios_elegibilidade": [
            "Habilidade extraordinária comprovada",
            "Reconhecimento nacional/internacional",
            "Prêmios, publicações, ou mídia sobre você",
            "Salário/remuneração alta na área",
            "Membro de associações que exigem conquistas extraordinárias",
            "Evidências substanciais de contribuições na área"
        ]
    },
    
    "N-400": {
        "name": "Pedido de Naturalização (Cidadania Americana)",
        "description": "Para residentes permanentes elegíveis que desejam se tornar cidadãos dos EUA",
        
        "change_of_status": {
            "description": "Aplicação para cidadania estando JÁ nos EUA como residente permanente",
            "tempo_processamento": "8-14 meses",
            "tempo_detalhes": "Tempo médio do USCIS para processar e agendar cerimônia",
            "taxas": {
                "taxa_n400": {
                    "valor": "$640",
                    "descricao": "Taxa de aplicação N-400",
                    "pago_para": "USCIS",
                    "quando_pagar": "Ao enviar aplicação"
                },
                "taxa_biometrics": {
                    "valor": "$85",
                    "descricao": "Taxa de biometria",
                    "pago_para": "USCIS",
                    "quando_pagar": "Incluída no total"
                },
                "total": "$725"
            },
            "etapas": [
                "Preencher formulário N-400 online ou papel",
                "Pagar taxa ($725)",
                "Enviar aplicação ao USCIS",
                "Aguardar recibo (2-4 semanas)",
                "Comparecer a biometria",
                "Estudar para teste de cidadania",
                "Entrevista com oficial USCIS",
                "Fazer teste de inglês e cívica",
                "Aguardar decisão",
                "Cerimônia de juramento (se aprovado)"
            ],
            "requisitos_especiais": [
                "Residente permanente há pelo menos 5 anos (ou 3 se casado com cidadão)",
                "Fisicamente presente nos EUA pelo menos metade do tempo requerido",
                "Não ter viagens longas fora dos EUA (geralmente < 6 meses)",
                "Bom caráter moral",
                "Conhecimento básico de inglês",
                "Conhecimento de história e governo americano"
            ]
        },
        
        "dependentes": "Filhos menores podem derivar cidadania automaticamente",
        "trabalho": "Sem restrições após naturalização",
        "duracao_maxima": "Permanente (cidadania vitalícia)",
        
        "criterios_elegibilidade": [
            "Residente permanente há 5 anos (ou 3 anos se casado com cidadão)",
            "Idade 18+ anos",
            "Presença física nos EUA",
            "Residência contínua",
            "Bom caráter moral",
            "Conhecimento de inglês e cívica",
            "Lealdade à Constituição dos EUA"
        ]
    },
    
    "I-765": {
        "name": "Autorização de Trabalho (EAD)",
        "description": "Para solicitar permissão de trabalho nos Estados Unidos",
        
        "change_of_status": {
            "description": "Aplicação para autorização de trabalho estando JÁ nos EUA",
            "tempo_processamento": "3-6 meses",
            "tempo_detalhes": "Tempo médio do USCIS para processar I-765",
            "taxas": {
                "taxa_i765": {
                    "valor": "$410",
                    "descricao": "Taxa de processamento I-765",
                    "pago_para": "USCIS",
                    "quando_pagar": "Ao enviar aplicação"
                },
                "taxa_biometrics": {
                    "valor": "$85",
                    "descricao": "Taxa de biometria (se aplicável)",
                    "pago_para": "USCIS",
                    "quando_pagar": "Incluída se necessário"
                },
                "total": "$410-$495"
            },
            "etapas": [
                "Verificar elegibilidade (estudante F-1 OPT, asylum pendente, etc.)",
                "Preencher formulário I-765",
                "Juntar documentação de suporte",
                "Pagar taxa ($410)",
                "Enviar ao USCIS",
                "Aguardar recibo (2-4 semanas)",
                "Biometria se necessário",
                "Aguardar EAD card (3-6 meses)"
            ],
            "requisitos_especiais": [
                "Deve ter categoria elegível (F-1 OPT, H-4 EAD, asylum, etc.)",
                "Estar nos EUA legalmente",
                "Não ter autorização automática de trabalho",
                "Manter status válido durante processamento",
                "Alguns casos permitem renovação automática (auto-extend)"
            ]
        },
        
        "dependentes": "Dependentes elegíveis podem aplicar separadamente",
        "trabalho": "Permite trabalhar para qualquer empregador nos EUA",
        "duracao_maxima": "Geralmente 1-2 anos, renovável",
        
        "criterios_elegibilidade": [
            "Ter categoria elegível (F-1 OPT, asylum pendente, TPS, etc.)",
            "Estar nos EUA legalmente",
            "Não ter autorização de trabalho automática",
            "Cumprir requisitos específicos da categoria",
            "Aplicar antes do vencimento do EAD anterior (para renovação)"
        ]
    },
    
    "I-485": {
        "name": "Ajuste de Status (Green Card)",
        "description": "Para ajustar status para residente permanente estando nos EUA",
        
        "change_of_status": {
            "description": "Ajuste de status para Green Card estando JÁ nos EUA",
            "tempo_processamento": "8-24 meses",
            "tempo_detalhes": "Varia muito por categoria e centro de serviço do USCIS",
            "taxas": {
                "taxa_i485": {
                    "valor": "$1,140",
                    "descricao": "Taxa de processamento I-485 (idade 14-78)",
                    "pago_para": "USCIS",
                    "quando_pagar": "Ao enviar aplicação"
                },
                "taxa_biometrics": {
                    "valor": "$85",
                    "descricao": "Taxa de biometria",
                    "pago_para": "USCIS",
                    "quando_pagar": "Incluída no total"
                },
                "taxa_i765_ead": {
                    "valor": "$0",
                    "descricao": "EAD (incluído com I-485)",
                    "pago_para": "USCIS",
                    "quando_pagar": "Sem custo adicional se incluído"
                },
                "taxa_i131_ap": {
                    "valor": "$0",
                    "descricao": "Advance Parole (incluído com I-485)",
                    "pago_para": "USCIS",
                    "quando_pagar": "Sem custo adicional se incluído"
                },
                "total": "$1,225"
            },
            "etapas": [
                "Ter petição aprovada ou categoria imediata (I-130, I-140, etc.)",
                "Visa number disponível (priority date current)",
                "Preencher I-485 e formulários auxiliares",
                "Exame médico (I-693) com médico aprovado USCIS",
                "Pagar taxas ($1,225)",
                "Enviar pacote ao USCIS",
                "Receber recibo e notices",
                "Biometria (fingerprints, foto)",
                "Possível entrevista (nem sempre necessário)",
                "Receber EAD/AP em 3-6 meses (se solicitado)",
                "Aguardar decisão final (8-24 meses)",
                "Receber Green Card físico (se aprovado)"
            ],
            "requisitos_especiais": [
                "Deve ter entrada legal nos EUA",
                "Manter status legal (ou ter exceção)",
                "Não pode viajar sem Advance Parole (exceto H-1B/L-1)",
                "Priority date deve estar current",
                "Passar exame médico",
                "Não ter crimes ou violações migratórias graves"
            ]
        },
        
        "dependentes": "Cônjuge e filhos menores podem incluir I-485 derivativos",
        "trabalho": "Permitido com EAD enquanto I-485 pendente",
        "duracao_maxima": "Green Card permanente (condicional 2 anos se baseado em casamento < 2 anos)",
        
        "criterios_elegibilidade": [
            "Ter petição aprovada ou ser elegível",
            "Estar fisicamente presente nos EUA",
            "Entrada legal nos EUA",
            "Visa disponível (se EB ou FB com prioridade)",
            "Não ter crimes/fraudes graves",
            "Passar verificação de antecedentes",
            "Passar exame médico"
        ]
    },
    
    "I-90": {
        "name": "Renovação/Substituição de Green Card",
        "description": "Para renovar ou substituir cartão de residente permanente",
        
        "change_of_status": {
            "description": "Renovação/substituição de Green Card estando nos EUA",
            "tempo_processamento": "6-12 meses",
            "tempo_detalhes": "Tempo médio do USCIS para processar e enviar novo card",
            "taxas": {
                "taxa_i90": {
                    "valor": "$455",
                    "descricao": "Taxa de processamento I-90",
                    "pago_para": "USCIS",
                    "quando_pagar": "Ao enviar aplicação"
                },
                "taxa_biometrics": {
                    "valor": "$85",
                    "descricao": "Taxa de biometria",
                    "pago_para": "USCIS",
                    "quando_pagar": "Incluída no total"
                },
                "total": "$540"
            },
            "etapas": [
                "Preencher formulário I-90 online (preferível) ou papel",
                "Indicar motivo (expiração, perda, erro, etc.)",
                "Upload de foto recente (se online)",
                "Pagar taxa ($540)",
                "Receber recibo com extensão temporária (12 meses)",
                "Biometria se necessário",
                "Aguardar novo Green Card (6-12 meses)",
                "Receber card no endereço registrado"
            ],
            "requisitos_especiais": [
                "Aplicar 6 meses antes da expiração (recomendado)",
                "Green Card condicional usa I-751, não I-90",
                "Recibo I-797 serve como extensão temporária",
                "Pode viajar com Green Card expirado + recibo I-797",
                "Atualizar endereço é obrigatório dentro de 10 dias de mudança"
            ]
        },
        
        "dependentes": "Cada pessoa precisa de seu próprio I-90",
        "trabalho": "Sem restrições de trabalho",
        "duracao_maxima": "Novo Green Card válido por 10 anos",
        
        "criterios_elegibilidade": [
            "Ser residente permanente",
            "Card expirado ou próximo de expirar",
            "Card perdido, roubado ou danificado",
            "Mudança de informações (nome, gênero)",
            "Erro no cartão emitido pelo USCIS",
            "Card de residente comutador (commuter) expirando"
        ]
    },
    
    "I-751": {
        "name": "Remoção de Condições do Green Card",
        "description": "Para remover condições do status de residente permanente condicional",
        
        "change_of_status": {
            "description": "Remoção de condições para Green Card permanente",
            "tempo_processamento": "12-24 meses",
            "tempo_detalhes": "Tempo do USCIS para processar e enviar Green Card permanente",
            "taxas": {
                "taxa_i751": {
                    "valor": "$595",
                    "descricao": "Taxa de processamento I-751",
                    "pago_para": "USCIS",
                    "quando_pagar": "Ao enviar petição"
                },
                "taxa_biometrics": {
                    "valor": "$85",
                    "descricao": "Taxa de biometria",
                    "pago_para": "USCIS",
                    "quando_pagar": "Incluída no total"
                },
                "total": "$680"
            },
            "etapas": [
                "Arquivar 90 dias ANTES de Green Card expirar",
                "Preencher I-751 (conjuntamente com cônjuge ou waiver)",
                "Juntar evidências de casamento genuíno (fotos, contas, filhos, etc.)",
                "Pagar taxa ($680)",
                "Receber recibo com extensão de 24 meses",
                "Biometria se necessário",
                "Possível entrevista (nem sempre)",
                "Aguardar decisão (12-24 meses)",
                "Receber Green Card permanente (10 anos)"
            ],
            "requisitos_especiais": [
                "DEVE arquivar dentro de 90 dias antes da expiração",
                "Se divórcios/separados: pode arquivar waiver sozinho",
                "Extensão automática de 24 ou 48 meses com recibo",
                "Evidências extensivas de casamento genuíno",
                "Pode viajar com Green Card expirado + recibo I-797"
            ]
        },
        
        "dependentes": "Filhos dependentes incluídos na mesma petição",
        "trabalho": "Sem restrições de trabalho",
        "duracao_maxima": "Green Card permanente válido por 10 anos",
        
        "criterios_elegibilidade": [
            "Residente permanente condicional há quase 2 anos",
            "Green Card obtido através de casamento < 2 anos",
            "Casamento genuíno (não fraude)",
            "Ainda casado OU waiver aprovado",
            "Aplicação dentro da janela de 90 dias"
        ]
    },
    
    "I-589": {
        "name": "Pedido de Asilo e Proteção Contra Deportação",
        "description": "Para pessoas que buscam proteção nos EUA devido a perseguição",
        
        "change_of_status": {
            "description": "Pedido de asilo estando JÁ nos EUA",
            "tempo_processamento": "2-7 anos",
            "tempo_detalhes": "Varia muito, backlog enorme no sistema",
            "taxas": {
                "taxa_i589": {
                    "valor": "$0",
                    "descricao": "Sem taxa para I-589",
                    "pago_para": "N/A",
                    "quando_pagar": "Gratuito"
                },
                "total": "$0"
            },
            "etapas": [
                "Aplicar dentro de 1 ano da chegada aos EUA (salvo exceções)",
                "Preencher formulário I-589 completo",
                "Escrever declaração pessoal detalhada",
                "Juntar evidências de perseguição",
                "Enviar ao USCIS (se afirmativo) ou Immigration Court",
                "Aguardar entrevista (meses ou anos)",
                "Entrevista com asylum officer ou juiz",
                "Decisão inicial",
                "Se negado: pode apelar",
                "Se aprovado: aguardar Green Card (1 ano após aprovação)"
            ],
            "requisitos_especiais": [
                "Deve aplicar dentro de 1 ano da última entrada",
                "Exceções: mudança de circunstâncias, razões extraordinárias",
                "Pode trabalhar após 180 dias (I-765 gratuito)",
                "Não pode viajar sem Advance Parole (perde caso)",
                "Deve demonstrar perseguição ou medo bem fundamentado",
                "Baseado em raça, religião, nacionalidade, opinião política, ou grupo social"
            ]
        },
        
        "dependentes": "Cônjuge e filhos menores podem ser incluídos",
        "trabalho": "Permitido após 180 dias com EAD (gratuito)",
        "duracao_maxima": "Asilo permanente (renovável indefinidamente até Green Card)",
        
        "criterios_elegibilidade": [
            "Estar fisicamente presente nos EUA",
            "Aplicar dentro de 1 ano (salvo exceções)",
            "Demonstrar perseguição ou medo bem fundamentado",
            "Perseguição baseada em motivos protegidos",
            "Não ter participado em perseguição de outros",
            "Não ser perigo à segurança dos EUA",
            "Não ter crimes graves"
        ]
    }
}


def get_visa_processing_info(visa_type: str, process_type: str = "change_of_status") -> dict:
    """
    Retorna informações de processamento de visto para MUDANÇA DE STATUS
    
    Args:
        visa_type: Código do visto (F-1, H-1B, I-130, I-539, etc.)
        process_type: Sempre "change_of_status" (aplicação só atende pessoas nos EUA)
    
    Returns:
        Dicionário com informações detalhadas
    """
    if visa_type not in VISA_DETAILED_INFO:
        return {"error": f"Visa type {visa_type} not found"}
    
    visa_info = VISA_DETAILED_INFO[visa_type]
    
    return {
        "name": visa_info["name"],
        "description": visa_info["description"],
        "change_of_status": visa_info.get("change_of_status", {}),
        "dependentes": visa_info.get("dependentes"),
        "trabalho": visa_info.get("trabalho"),
        "duracao_maxima": visa_info.get("duracao_maxima"),
        "criterios_elegibilidade": visa_info.get("criterios_elegibilidade")
    }
