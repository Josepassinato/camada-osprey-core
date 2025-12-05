"""
Estruturas de Formulário Amigável baseadas em Formulários Oficiais USCIS

Este módulo define a estrutura completa do formulário amigável para cada tipo de visto,
garantindo que TODOS os campos obrigatórios do formulário oficial USCIS sejam coletados.

Mapeamento:
- Campo Amigável (português) → Campo Oficial USCIS (inglês)
- Validações específicas por campo
- Seções organizadas logicamente para o usuário
"""

from typing import Dict, List, Any


def get_i539_friendly_form_structure() -> Dict[str, Any]:
    """
    Estrutura completa do formulário amigável para I-539
    (Application to Extend/Change Nonimmigrant Status)
    
    Baseado no formulário oficial I-539 da USCIS
    """
    return {
        "form_code": "I-539",
        "form_name": "Pedido de Extensão ou Mudança de Status de Não-Imigrante",
        "sections": [
            {
                "id": "informacoes_pessoais",
                "title": "1. Informações Pessoais",
                "description": "Dados básicos do requerente",
                "fields": [
                    {
                        "id": "nome_completo",
                        "label": "Nome Completo (como está no passaporte)",
                        "type": "text",
                        "required": True,
                        "placeholder": "João Silva Santos",
                        "validation": "min:3",
                        "official_mapping": "Pt1Line1a_FamilyName, Pt1Line1b_GivenName",
                        "help_text": "Digite seu nome exatamente como aparece no passaporte"
                    },
                    {
                        "id": "data_nascimento",
                        "label": "Data de Nascimento",
                        "type": "date",
                        "required": True,
                        "placeholder": "1990-05-15",
                        "validation": "date|past",
                        "official_mapping": "Pt1Line3a_DateOfBirth",
                        "help_text": "Formato: YYYY-MM-DD"
                    },
                    {
                        "id": "pais_nascimento",
                        "label": "País de Nascimento",
                        "type": "country",
                        "required": True,
                        "placeholder": "Brazil",
                        "official_mapping": "Pt1Line4_CountryOfBirth"
                    },
                    {
                        "id": "pais_cidadania",
                        "label": "País de Cidadania",
                        "type": "country",
                        "required": True,
                        "placeholder": "Brazil",
                        "official_mapping": "Pt1Line5_CountryOfCitizenship"
                    },
                    {
                        "id": "sexo",
                        "label": "Sexo",
                        "type": "select",
                        "required": True,
                        "options": ["Masculino", "Feminino"],
                        "official_mapping": "Pt1Line6_Gender"
                    }
                ]
            },
            {
                "id": "documentos_viagem",
                "title": "2. Documentos de Viagem",
                "description": "Informações do seu passaporte e documentos de entrada",
                "fields": [
                    {
                        "id": "numero_passaporte",
                        "label": "Número do Passaporte",
                        "type": "text",
                        "required": True,
                        "placeholder": "BR123456789",
                        "validation": "min:5|alphanumeric",
                        "official_mapping": "Pt1Line6_PassportNumber"
                    },
                    {
                        "id": "pais_emissao_passaporte",
                        "label": "País de Emissão do Passaporte",
                        "type": "country",
                        "required": True,
                        "official_mapping": "Pt1Line7_PassportCountryOfIssuance"
                    },
                    {
                        "id": "data_expiracao_passaporte",
                        "label": "Data de Expiração do Passaporte",
                        "type": "date",
                        "required": True,
                        "validation": "date|future",
                        "official_mapping": "Pt1Line8_PassportExpirationDate"
                    },
                    {
                        "id": "numero_i94",
                        "label": "Número do I-94 (Arrival/Departure Record)",
                        "type": "text",
                        "required": True,
                        "placeholder": "1234567890",
                        "validation": "numeric|length:11",
                        "official_mapping": "Pt1Line9_I94Number",
                        "help_text": "Encontre em: https://i94.cbp.dhs.gov/"
                    },
                    {
                        "id": "data_ultima_entrada",
                        "label": "Data da Última Entrada nos EUA",
                        "type": "date",
                        "required": True,
                        "validation": "date|past",
                        "official_mapping": "Pt1Line10_DateOfLastEntry"
                    },
                    {
                        "id": "local_entrada",
                        "label": "Local de Entrada nos EUA",
                        "type": "text",
                        "required": True,
                        "placeholder": "JFK Airport, New York",
                        "official_mapping": "Pt1Line11_PlaceOfLastEntry"
                    }
                ]
            },
            {
                "id": "status_imigratorio",
                "title": "3. Status Imigratório",
                "description": "Seu status atual e o que você está solicitando",
                "fields": [
                    {
                        "id": "status_atual",
                        "label": "Status Atual de Não-Imigrante",
                        "type": "select",
                        "required": True,
                        "options": ["F-1", "F-2", "M-1", "M-2", "J-1", "J-2", "B-1", "B-2", "H-1B", "H-4", "L-1", "L-2", "O-1", "O-3", "Other"],
                        "official_mapping": "Pt2Line1_CurrentNonimmigrantStatus"
                    },
                    {
                        "id": "data_expiracao_status",
                        "label": "Data de Expiração do Status Atual",
                        "type": "date",
                        "required": True,
                        "validation": "date",
                        "official_mapping": "Pt2Line2_ExpirationOfAuthorizedStay",
                        "help_text": "Data que aparece no seu I-94"
                    },
                    {
                        "id": "tipo_pedido",
                        "label": "O que você está solicitando?",
                        "type": "select",
                        "required": True,
                        "options": [
                            "Extensão do mesmo status",
                            "Mudança para outro status"
                        ],
                        "official_mapping": "Pt2_ApplicationType"
                    },
                    {
                        "id": "status_solicitado",
                        "label": "Status Solicitado (se mudança)",
                        "type": "select",
                        "required": False,
                        "options": ["F-1", "F-2", "M-1", "M-2", "J-1", "J-2", "B-1", "B-2", "H-1B", "H-4", "L-1", "L-2", "O-1", "O-3", "Other"],
                        "official_mapping": "Pt2Line3_RequestedNonimmigrantStatus",
                        "conditional": "tipo_pedido == 'Mudança para outro status'"
                    },
                    {
                        "id": "numero_sevis",
                        "label": "Número SEVIS (se F-1, F-2, M-1, M-2, J-1, J-2)",
                        "type": "text",
                        "required": False,
                        "placeholder": "N0123456789",
                        "validation": "alphanumeric",
                        "official_mapping": "Pt2Line4_SEVISNumber",
                        "conditional": "status_atual in ['F-1', 'F-2', 'M-1', 'M-2', 'J-1', 'J-2'] or status_solicitado in ['F-1', 'F-2', 'M-1', 'M-2', 'J-1', 'J-2']"
                    }
                ]
            },
            {
                "id": "endereco_contato",
                "title": "4. Endereço e Contato nos EUA",
                "description": "Onde você mora atualmente e como podemos te contatar",
                "fields": [
                    {
                        "id": "endereco",
                        "label": "Endereço Completo",
                        "type": "text",
                        "required": True,
                        "placeholder": "123 Main Street, Apt 4B",
                        "validation": "min:10",
                        "official_mapping": "Pt1Line7a_StreetNumberName"
                    },
                    {
                        "id": "cidade",
                        "label": "Cidade",
                        "type": "text",
                        "required": True,
                        "placeholder": "New York",
                        "official_mapping": "Pt1Line7c_CityOrTown"
                    },
                    {
                        "id": "estado",
                        "label": "Estado",
                        "type": "select",
                        "required": True,
                        "options": ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"],
                        "official_mapping": "Pt1Line7d_State"
                    },
                    {
                        "id": "cep",
                        "label": "CEP/ZIP Code",
                        "type": "text",
                        "required": True,
                        "placeholder": "10001",
                        "validation": "numeric|length:5",
                        "official_mapping": "Pt1Line7e_ZipCode"
                    },
                    {
                        "id": "telefone",
                        "label": "Telefone",
                        "type": "tel",
                        "required": True,
                        "placeholder": "+1 (555) 123-4567",
                        "validation": "phone",
                        "official_mapping": "Pt1Line9_DaytimeTelephone"
                    },
                    {
                        "id": "email",
                        "label": "Email",
                        "type": "email",
                        "required": True,
                        "placeholder": "seu.email@example.com",
                        "validation": "email",
                        "official_mapping": "Pt1Line8_Email"
                    }
                ]
            },
            {
                "id": "informacoes_adicionais",
                "title": "5. Informações Adicionais",
                "description": "Explicações sobre sua solicitação",
                "fields": [
                    {
                        "id": "motivo_pedido",
                        "label": "Explique em detalhes o motivo do seu pedido",
                        "type": "textarea",
                        "required": True,
                        "placeholder": "Descreva por que você precisa estender ou mudar seu status...",
                        "validation": "min:100",
                        "official_mapping": "Pt4_AdditionalInformation",
                        "help_text": "Seja específico e detalhado. Mínimo 100 caracteres."
                    },
                    {
                        "id": "data_desejada_permanencia",
                        "label": "Até quando você deseja permanecer nos EUA?",
                        "type": "date",
                        "required": True,
                        "validation": "date|future",
                        "official_mapping": "Pt2Line5_DateOfIntendedDeparture"
                    }
                ]
            }
        ],
        "total_fields": 27,
        "estimated_time": "20-30 minutos"
    }


def get_i589_friendly_form_structure() -> Dict[str, Any]:
    """
    Estrutura completa do formulário amigável para I-589
    (Application for Asylum and for Withholding of Removal)
    
    Baseado no formulário oficial I-589 da USCIS
    """
    return {
        "form_code": "I-589",
        "form_name": "Pedido de Asilo e Proteção contra Remoção",
        "sections": [
            {
                "id": "informacoes_pessoais",
                "title": "Parte A: Informações Sobre Você",
                "description": "Dados pessoais do requerente de asilo",
                "fields": [
                    {
                        "id": "nome_completo",
                        "label": "Nome Completo",
                        "type": "text",
                        "required": True,
                        "official_mapping": "PartA_FamilyName, PartA_FirstName, PartA_MiddleName"
                    },
                    {
                        "id": "data_nascimento",
                        "label": "Data de Nascimento",
                        "type": "date",
                        "required": True,
                        "validation": "date|past",
                        "official_mapping": "PartA_DateOfBirth"
                    },
                    {
                        "id": "pais_nascimento",
                        "label": "País de Nascimento",
                        "type": "country",
                        "required": True,
                        "official_mapping": "PartA_CountryOfBirth"
                    },
                    {
                        "id": "nacionalidade",
                        "label": "Nacionalidade Atual",
                        "type": "country",
                        "required": True,
                        "official_mapping": "PartA_Nationality"
                    },
                    {
                        "id": "raca_etnia_tribo",
                        "label": "Raça, Grupo Étnico ou Tribo",
                        "type": "text",
                        "required": False,
                        "official_mapping": "PartA_Race_Ethnic_TribalGroup"
                    },
                    {
                        "id": "religiao",
                        "label": "Religião",
                        "type": "text",
                        "required": False,
                        "official_mapping": "PartA_Religion"
                    },
                    {
                        "id": "sexo",
                        "label": "Sexo",
                        "type": "select",
                        "required": True,
                        "options": ["Masculino", "Feminino"],
                        "official_mapping": "PartA_Sex"
                    },
                    {
                        "id": "estado_civil",
                        "label": "Estado Civil",
                        "type": "select",
                        "required": True,
                        "options": ["Solteiro(a)", "Casado(a)", "Divorciado(a)", "Viúvo(a)"],
                        "official_mapping": "PartA_MaritalStatus"
                    }
                ]
            },
            {
                "id": "documentos_viagem",
                "title": "Parte A: Documentos de Viagem",
                "fields": [
                    {
                        "id": "numero_passaporte",
                        "label": "Número do Passaporte",
                        "type": "text",
                        "required": True,
                        "validation": "min:5",
                        "official_mapping": "PartA_PassportNumber"
                    },
                    {
                        "id": "numero_i94",
                        "label": "Número do I-94",
                        "type": "text",
                        "required": True,
                        "validation": "numeric",
                        "official_mapping": "PartA_I94Number"
                    },
                    {
                        "id": "data_chegada_eua",
                        "label": "Data de Chegada nos EUA",
                        "type": "date",
                        "required": True,
                        "validation": "date|past",
                        "official_mapping": "PartA_DateOfArrival"
                    },
                    {
                        "id": "local_chegada",
                        "label": "Local de Chegada nos EUA",
                        "type": "text",
                        "required": True,
                        "official_mapping": "PartA_PlaceOfArrival"
                    },
                    {
                        "id": "status_entrada",
                        "label": "Status na Entrada",
                        "type": "text",
                        "required": True,
                        "placeholder": "B-2, F-1, etc.",
                        "official_mapping": "PartA_StatusAtEntry"
                    }
                ]
            },
            {
                "id": "endereco_atual",
                "title": "Parte A: Endereço Atual nos EUA",
                "fields": [
                    {
                        "id": "endereco",
                        "label": "Endereço Completo",
                        "type": "text",
                        "required": True,
                        "validation": "min:10",
                        "official_mapping": "PartA_CurrentAddress"
                    },
                    {
                        "id": "cidade",
                        "label": "Cidade",
                        "type": "text",
                        "required": True,
                        "official_mapping": "PartA_City"
                    },
                    {
                        "id": "estado",
                        "label": "Estado",
                        "type": "select",
                        "required": True,
                        "options": ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"],
                        "official_mapping": "PartA_State"
                    },
                    {
                        "id": "cep",
                        "label": "ZIP Code",
                        "type": "text",
                        "required": True,
                        "validation": "numeric|length:5",
                        "official_mapping": "PartA_ZipCode"
                    },
                    {
                        "id": "telefone",
                        "label": "Telefone",
                        "type": "tel",
                        "required": True,
                        "official_mapping": "PartA_Telephone"
                    },
                    {
                        "id": "email",
                        "label": "Email",
                        "type": "email",
                        "required": True,
                        "validation": "email",
                        "official_mapping": "PartA_Email"
                    }
                ]
            },
            {
                "id": "motivo_asilo",
                "title": "Parte B: Informações Sobre Seu Pedido de Asilo",
                "description": "Por que você está pedindo asilo?",
                "fields": [
                    {
                        "id": "motivo_principal",
                        "label": "Qual é o principal motivo do seu medo?",
                        "type": "select",
                        "required": True,
                        "options": [
                            "Raça",
                            "Religião",
                            "Nacionalidade",
                            "Opinião Política",
                            "Pertencimento a Grupo Social Particular"
                        ],
                        "official_mapping": "PartB_FearBasis"
                    },
                    {
                        "id": "historia_perseguicao",
                        "label": "Descreva em detalhes a perseguição ou medo de perseguição que você sofreu ou teme sofrer",
                        "type": "textarea",
                        "required": True,
                        "placeholder": "Descreva os eventos específicos, quando ocorreram, quem te perseguiu, por que...",
                        "validation": "min:500",
                        "official_mapping": "PartB_DetailedExplanation",
                        "help_text": "Seja o mais detalhado possível. Mínimo 500 caracteres."
                    },
                    {
                        "id": "retornar_seguro",
                        "label": "Por que você não pode retornar ao seu país de origem com segurança?",
                        "type": "textarea",
                        "required": True,
                        "validation": "min:200",
                        "official_mapping": "PartB_WhyCannotReturn"
                    }
                ]
            }
        ],
        "total_fields": 28,
        "estimated_time": "45-60 minutos",
        "warning": "Este formulário é mais complexo e requer documentação extensa."
    }


def get_eb1a_friendly_form_structure() -> Dict[str, Any]:
    """
    Estrutura completa do formulário amigável para EB-1A
    (Employment-Based First Preference - Extraordinary Ability)
    
    Baseado no formulário oficial I-140 da USCIS
    """
    return {
        "form_code": "EB-1A",
        "form_name": "Pedido de Imigrante Baseado em Habilidade Extraordinária",
        "sections": [
            {
                "id": "informacoes_pessoais",
                "title": "Parte 1: Informações Sobre Você",
                "fields": [
                    {
                        "id": "nome_completo",
                        "label": "Nome Completo",
                        "type": "text",
                        "required": True,
                        "official_mapping": "Pt1_FamilyName, Pt1_GivenName"
                    },
                    {
                        "id": "data_nascimento",
                        "label": "Data de Nascimento",
                        "type": "date",
                        "required": True,
                        "validation": "date|past",
                        "official_mapping": "Pt1_DateOfBirth"
                    },
                    {
                        "id": "pais_nascimento",
                        "label": "País de Nascimento",
                        "type": "country",
                        "required": True,
                        "official_mapping": "Pt1_CountryOfBirth"
                    },
                    {
                        "id": "numero_passaporte",
                        "label": "Número do Passaporte",
                        "type": "text",
                        "required": True,
                        "official_mapping": "Pt1_PassportNumber"
                    },
                    {
                        "id": "email",
                        "label": "Email",
                        "type": "email",
                        "required": True,
                        "validation": "email",
                        "official_mapping": "Pt1_Email"
                    }
                ]
            },
            {
                "id": "area_expertise",
                "title": "Parte 2: Área de Habilidade Extraordinária",
                "fields": [
                    {
                        "id": "campo_atuacao",
                        "label": "Campo de Atuação",
                        "type": "select",
                        "required": True,
                        "options": [
                            "Ciências",
                            "Artes",
                            "Educação",
                            "Negócios",
                            "Atletismo"
                        ],
                        "official_mapping": "Pt2_FieldOfExtraordinaryAbility"
                    },
                    {
                        "id": "descricao_expertise",
                        "label": "Descreva sua área específica de expertise",
                        "type": "textarea",
                        "required": True,
                        "placeholder": "Ex: Inteligência Artificial e Machine Learning...",
                        "validation": "min:100",
                        "official_mapping": "Pt2_SpecificArea"
                    }
                ]
            },
            {
                "id": "criterios_uscis",
                "title": "Parte 3: Critérios de Habilidade Extraordinária",
                "description": "Você deve demonstrar pelo menos 3 dos 10 critérios abaixo",
                "fields": [
                    {
                        "id": "premios_nacionais",
                        "label": "1. Prêmios ou distinções nacionais ou internacionais de excelência",
                        "type": "textarea",
                        "required": False,
                        "placeholder": "Liste prêmios recebidos com datas e descrições...",
                        "official_mapping": "Pt3_Criterion1_Awards"
                    },
                    {
                        "id": "associacoes_memberships",
                        "label": "2. Membro de associações que exigem conquistas excepcionais",
                        "type": "textarea",
                        "required": False,
                        "placeholder": "Liste associações profissionais de elite...",
                        "official_mapping": "Pt3_Criterion2_Membership"
                    },
                    {
                        "id": "publicacoes_midia",
                        "label": "3. Material publicado sobre você em mídia profissional ou grande mídia",
                        "type": "textarea",
                        "required": False,
                        "placeholder": "Liste publicações, artigos, entrevistas...",
                        "official_mapping": "Pt3_Criterion3_PublishedMaterial"
                    },
                    {
                        "id": "juiz_trabalhos",
                        "label": "4. Participação como juiz do trabalho de outros no campo",
                        "type": "textarea",
                        "required": False,
                        "placeholder": "Descreva experiências como revisor, avaliador...",
                        "official_mapping": "Pt3_Criterion4_Judging"
                    },
                    {
                        "id": "contribuicoes_originais",
                        "label": "5. Contribuições científicas ou acadêmicas originais de grande importância",
                        "type": "textarea",
                        "required": False,
                        "placeholder": "Descreva pesquisas, inovações, descobertas...",
                        "validation": "min:200",
                        "official_mapping": "Pt3_Criterion5_OriginalContributions"
                    },
                    {
                        "id": "publicacoes_academicas",
                        "label": "6. Autoria de artigos acadêmicos em periódicos ou publicações importantes",
                        "type": "textarea",
                        "required": False,
                        "placeholder": "Liste publicações científicas com citações...",
                        "official_mapping": "Pt3_Criterion6_ScholarlyArticles"
                    },
                    {
                        "id": "exibicoes_artisticas",
                        "label": "7. Exibições ou apresentações artísticas em locais de destaque",
                        "type": "textarea",
                        "required": False,
                        "placeholder": "Para artistas: liste exposições, performances...",
                        "official_mapping": "Pt3_Criterion7_ArtisticExhibitions"
                    },
                    {
                        "id": "papel_critico",
                        "label": "8. Papel crítico ou liderança em organizações de reputação distinta",
                        "type": "textarea",
                        "required": False,
                        "placeholder": "Descreva posições de liderança...",
                        "official_mapping": "Pt3_Criterion8_CriticalRole"
                    },
                    {
                        "id": "salario_alto",
                        "label": "9. Salário ou remuneração significativamente alta em relação a outros no campo",
                        "type": "textarea",
                        "required": False,
                        "placeholder": "Forneça evidências de remuneração alta...",
                        "official_mapping": "Pt3_Criterion9_HighSalary"
                    },
                    {
                        "id": "sucesso_comercial",
                        "label": "10. Sucesso comercial nas artes performáticas",
                        "type": "textarea",
                        "required": False,
                        "placeholder": "Para artistas: vendas de discos, bilheteria...",
                        "official_mapping": "Pt3_Criterion10_CommercialSuccess"
                    }
                ]
            },
            {
                "id": "plano_futuro",
                "title": "Parte 4: Planos Futuros nos EUA",
                "fields": [
                    {
                        "id": "continuacao_trabalho",
                        "label": "Como você planeja continuar trabalhando em sua área de expertise nos EUA?",
                        "type": "textarea",
                        "required": True,
                        "placeholder": "Descreva planos de pesquisa, emprego, projetos...",
                        "validation": "min:200",
                        "official_mapping": "Pt4_IntentionToContinue"
                    }
                ]
            }
        ],
        "total_fields": 20,
        "estimated_time": "60-90 minutos",
        "warning": "EB-1A requer documentação extensa. Você deve demonstrar pelo menos 3 dos 10 critérios com evidências sólidas."
    }


def get_friendly_form_structure(visa_type: str) -> Dict[str, Any]:
    """
    Retorna a estrutura completa do formulário amigável para o tipo de visto especificado
    
    Args:
        visa_type: Código do visto (I-539, I-589, EB-1A, etc.)
        
    Returns:
        Dict com a estrutura completa do formulário
    """
    structures = {
        "I-539": get_i539_friendly_form_structure,
        "I-589": get_i589_friendly_form_structure,
        "EB-1A": get_eb1a_friendly_form_structure,
        "EB1A": get_eb1a_friendly_form_structure,
        "I-140": get_eb1a_friendly_form_structure
    }
    
    structure_func = structures.get(visa_type)
    if structure_func:
        return structure_func()
    else:
        raise ValueError(f"Estrutura de formulário não definida para o tipo de visto: {visa_type}")


def get_all_required_fields(visa_type: str) -> List[str]:
    """
    Retorna lista de todos os campos obrigatórios para um tipo de visto
    
    Args:
        visa_type: Código do visto
        
    Returns:
        Lista de IDs de campos obrigatórios
    """
    structure = get_friendly_form_structure(visa_type)
    required_fields = []
    
    for section in structure.get("sections", []):
        for field in section.get("fields", []):
            if field.get("required", False):
                # Check conditional requirements
                conditional = field.get("conditional")
                if not conditional:  # Always required
                    required_fields.append(field["id"])
    
    return required_fields
