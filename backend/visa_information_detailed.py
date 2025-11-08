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
    },
    
    "B-1/B-2": {
        "name": "Visto de Negócios e Turismo",
        "description": "Para negócios temporários, turismo, visitas familiares e tratamento médico",
        
        "processo_consular": {
            "description": "Aplicação em consulado dos EUA (primeira vez ou renovação)",
            "tempo_processamento": "2-4 semanas",
            "tempo_detalhes": "Tempo desde agendamento até recebimento do passaporte com visto",
            "taxas": {
                "taxa_ds160": {
                    "valor": "$185",
                    "descricao": "Taxa de aplicação do visto (MRV Fee)",
                    "pago_para": "Consulado dos EUA",
                    "quando_pagar": "Antes de agendar entrevista"
                },
                "total": "$185"
            },
            "etapas": [
                "Preencher formulário DS-160",
                "Pagar taxa MRV ($185)",
                "Agendar entrevista no consulado",
                "Comparecer à entrevista com documentos",
                "Aguardar processamento (2-4 semanas)"
            ]
        },
        
        "change_of_status": {
            "description": "NÃO APLICÁVEL - B-1/B-2 deve ser obtido via consulado",
            "tempo_processamento": "N/A",
            "tempo_detalhes": "B-1/B-2 não permite mudança de status. Para extensão dentro dos EUA, use I-539",
            "taxas": {},
            "etapas": [],
            "disponivel": False
        },
        
        "dependentes": "Cada pessoa precisa de visto próprio",
        "trabalho": "Não permitido trabalhar com B-1/B-2",
        "duracao_maxima": "Geralmente 6 meses por entrada",
        
        "criterios_elegibilidade": [
            "B-1: Reuniões de negócios, conferências, treinamentos",
            "B-2: Turismo, visitas familiares, tratamento médico",
            "Intenção de retornar ao Brasil",
            "Vínculos fortes com país de origem",
            "Recursos financeiros suficientes"
        ]
    },
    
    "O-1": {
        "name": "Visto de Habilidade Extraordinária",
        "description": "Para indivíduos com habilidades extraordinárias em ciências, artes, educação, negócios ou atletismo",
        
        "processo_consular": {
            "description": "Aplicação em consulado dos EUA após petição I-129 aprovada",
            "tempo_processamento": "2-4 semanas",
            "tempo_detalhes": "Após aprovação da petição I-129 pelo USCIS",
            "taxas": {
                "taxa_ds160": {
                    "valor": "$190",
                    "descricao": "Taxa de aplicação do visto",
                    "pago_para": "Consulado dos EUA",
                    "quando_pagar": "Antes de agendar entrevista"
                },
                "total": "$190"
            },
            "etapas": [
                "Empregador/Agente submete I-129 ao USCIS ($460 + $500 fraude)",
                "Aguardar aprovação I-129 (2-4 meses ou 15 dias com premium)",
                "Preencher DS-160",
                "Pagar taxa ($190)",
                "Agendar entrevista",
                "Comparecer com I-797 aprovado",
                "Receber visto (2-4 semanas)"
            ]
        },
        
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
        
        "processo_consular": {
            "description": "Não aplicável - cidadania é obtida estando nos EUA",
            "tempo_processamento": "N/A",
            "taxas": {},
            "etapas": []
        },
        
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
        
        "processo_consular": {
            "description": "Não aplicável - EAD é obtido estando nos EUA",
            "tempo_processamento": "N/A",
            "taxas": {},
            "etapas": []
        },
        
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
        
        "processo_consular": {
            "description": "Processo consular usa DS-260, não I-485",
            "tempo_processamento": "N/A",
            "taxas": {},
            "etapas": []
        },
        
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
        
        "processo_consular": {
            "description": "Não aplicável - I-90 é para quem já tem Green Card",
            "tempo_processamento": "N/A",
            "taxas": {},
            "etapas": []
        },
        
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
        
        "processo_consular": {
            "description": "Não aplicável - I-751 é para quem já tem Green Card condicional",
            "tempo_processamento": "N/A",
            "taxas": {},
            "etapas": []
        },
        
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
        
        "processo_consular": {
            "description": "Asilo é solicitado estando nos EUA ou na fronteira",
            "tempo_processamento": "N/A",
            "taxas": {},
            "etapas": []
        },
        
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
