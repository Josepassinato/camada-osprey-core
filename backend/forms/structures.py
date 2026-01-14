"""
Estruturas de Formulário Amigável baseadas em Formulários Oficiais USCIS

Este módulo define a estrutura completa do formulário amigável para cada tipo de visto,
garantindo que TODOS os campos obrigatórios do formulário oficial USCIS sejam coletados.

Mapeamento:
- Campo Amigável (português) → Campo Oficial USCIS (inglês)
- Validações específicas por campo
- Seções organizadas logicamente para o usuário
"""

from typing import Any, Dict, List


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
                        "help_text": "Digite seu nome exatamente como aparece no passaporte",
                    },
                    {
                        "id": "data_nascimento",
                        "label": "Data de Nascimento",
                        "type": "date",
                        "required": True,
                        "placeholder": "1990-05-15",
                        "validation": "date|past",
                        "official_mapping": "Pt1Line3a_DateOfBirth",
                        "help_text": "Formato: YYYY-MM-DD",
                    },
                    {
                        "id": "pais_nascimento",
                        "label": "País de Nascimento",
                        "type": "country",
                        "required": True,
                        "placeholder": "Brazil",
                        "official_mapping": "Pt1Line4_CountryOfBirth",
                    },
                    {
                        "id": "pais_cidadania",
                        "label": "País de Cidadania",
                        "type": "country",
                        "required": True,
                        "placeholder": "Brazil",
                        "official_mapping": "Pt1Line5_CountryOfCitizenship",
                    },
                    {
                        "id": "sexo",
                        "label": "Sexo",
                        "type": "select",
                        "required": True,
                        "options": ["Masculino", "Feminino"],
                        "official_mapping": "Pt1Line6_Gender",
                    },
                ],
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
                        "official_mapping": "Pt1Line6_PassportNumber",
                    },
                    {
                        "id": "pais_emissao_passaporte",
                        "label": "País de Emissão do Passaporte",
                        "type": "country",
                        "required": True,
                        "official_mapping": "Pt1Line7_PassportCountryOfIssuance",
                    },
                    {
                        "id": "data_expiracao_passaporte",
                        "label": "Data de Expiração do Passaporte",
                        "type": "date",
                        "required": True,
                        "validation": "date|future",
                        "official_mapping": "Pt1Line8_PassportExpirationDate",
                    },
                    {
                        "id": "numero_i94",
                        "label": "Número do I-94 (Arrival/Departure Record)",
                        "type": "text",
                        "required": True,
                        "placeholder": "1234567890",
                        "validation": "numeric|length:11",
                        "official_mapping": "Pt1Line9_I94Number",
                        "help_text": "Encontre em: https://i94.cbp.dhs.gov/",
                    },
                    {
                        "id": "data_ultima_entrada",
                        "label": "Data da Última Entrada nos EUA",
                        "type": "date",
                        "required": True,
                        "validation": "date|past",
                        "official_mapping": "Pt1Line10_DateOfLastEntry",
                    },
                    {
                        "id": "local_entrada",
                        "label": "Local de Entrada nos EUA",
                        "type": "text",
                        "required": True,
                        "placeholder": "JFK Airport, New York",
                        "official_mapping": "Pt1Line11_PlaceOfLastEntry",
                    },
                ],
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
                        "options": [
                            "F-1",
                            "F-2",
                            "M-1",
                            "M-2",
                            "J-1",
                            "J-2",
                            "B-1",
                            "B-2",
                            "H-1B",
                            "H-4",
                            "L-1",
                            "L-2",
                            "O-1",
                            "O-3",
                            "Other",
                        ],
                        "official_mapping": "Pt2Line1_CurrentNonimmigrantStatus",
                    },
                    {
                        "id": "data_expiracao_status",
                        "label": "Data de Expiração do Status Atual",
                        "type": "date",
                        "required": True,
                        "validation": "date",
                        "official_mapping": "Pt2Line2_ExpirationOfAuthorizedStay",
                        "help_text": "Data que aparece no seu I-94",
                    },
                    {
                        "id": "tipo_pedido",
                        "label": "O que você está solicitando?",
                        "type": "select",
                        "required": True,
                        "options": ["Extensão do mesmo status", "Mudança para outro status"],
                        "official_mapping": "Pt2_ApplicationType",
                    },
                    {
                        "id": "status_solicitado",
                        "label": "Status Solicitado (se mudança)",
                        "type": "select",
                        "required": False,
                        "options": [
                            "F-1",
                            "F-2",
                            "M-1",
                            "M-2",
                            "J-1",
                            "J-2",
                            "B-1",
                            "B-2",
                            "H-1B",
                            "H-4",
                            "L-1",
                            "L-2",
                            "O-1",
                            "O-3",
                            "Other",
                        ],
                        "official_mapping": "Pt2Line3_RequestedNonimmigrantStatus",
                        "conditional": "tipo_pedido == 'Mudança para outro status'",
                    },
                    {
                        "id": "numero_sevis",
                        "label": "Número SEVIS (se F-1, F-2, M-1, M-2, J-1, J-2)",
                        "type": "text",
                        "required": False,
                        "placeholder": "N0123456789",
                        "validation": "alphanumeric",
                        "official_mapping": "Pt2Line4_SEVISNumber",
                        "conditional": "status_atual in ['F-1', 'F-2', 'M-1', 'M-2', 'J-1', 'J-2'] or status_solicitado in ['F-1', 'F-2', 'M-1', 'M-2', 'J-1', 'J-2']",
                    },
                ],
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
                        "official_mapping": "Pt1Line7a_StreetNumberName",
                    },
                    {
                        "id": "cidade",
                        "label": "Cidade",
                        "type": "text",
                        "required": True,
                        "placeholder": "New York",
                        "official_mapping": "Pt1Line7c_CityOrTown",
                    },
                    {
                        "id": "estado",
                        "label": "Estado",
                        "type": "select",
                        "required": True,
                        "options": [
                            "AL",
                            "AK",
                            "AZ",
                            "AR",
                            "CA",
                            "CO",
                            "CT",
                            "DE",
                            "FL",
                            "GA",
                            "HI",
                            "ID",
                            "IL",
                            "IN",
                            "IA",
                            "KS",
                            "KY",
                            "LA",
                            "ME",
                            "MD",
                            "MA",
                            "MI",
                            "MN",
                            "MS",
                            "MO",
                            "MT",
                            "NE",
                            "NV",
                            "NH",
                            "NJ",
                            "NM",
                            "NY",
                            "NC",
                            "ND",
                            "OH",
                            "OK",
                            "OR",
                            "PA",
                            "RI",
                            "SC",
                            "SD",
                            "TN",
                            "TX",
                            "UT",
                            "VT",
                            "VA",
                            "WA",
                            "WV",
                            "WI",
                            "WY",
                        ],
                        "official_mapping": "Pt1Line7d_State",
                    },
                    {
                        "id": "cep",
                        "label": "CEP/ZIP Code",
                        "type": "text",
                        "required": True,
                        "placeholder": "10001",
                        "validation": "numeric|length:5",
                        "official_mapping": "Pt1Line7e_ZipCode",
                    },
                    {
                        "id": "telefone",
                        "label": "Telefone",
                        "type": "tel",
                        "required": True,
                        "placeholder": "+1 (555) 123-4567",
                        "validation": "phone",
                        "official_mapping": "Pt1Line9_DaytimeTelephone",
                    },
                    {
                        "id": "email",
                        "label": "Email",
                        "type": "email",
                        "required": True,
                        "placeholder": "seu.email@example.com",
                        "validation": "email",
                        "official_mapping": "Pt1Line8_Email",
                    },
                ],
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
                        "help_text": "Seja específico e detalhado. Mínimo 100 caracteres.",
                    },
                    {
                        "id": "data_desejada_permanencia",
                        "label": "Até quando você deseja permanecer nos EUA?",
                        "type": "date",
                        "required": True,
                        "validation": "date|future",
                        "official_mapping": "Pt2Line5_DateOfIntendedDeparture",
                    },
                ],
            },
        ],
        "total_fields": 27,
        "estimated_time": "20-30 minutos",
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
                        "official_mapping": "PartA_FamilyName, PartA_FirstName, PartA_MiddleName",
                    },
                    {
                        "id": "data_nascimento",
                        "label": "Data de Nascimento",
                        "type": "date",
                        "required": True,
                        "validation": "date|past",
                        "official_mapping": "PartA_DateOfBirth",
                    },
                    {
                        "id": "pais_nascimento",
                        "label": "País de Nascimento",
                        "type": "country",
                        "required": True,
                        "official_mapping": "PartA_CountryOfBirth",
                    },
                    {
                        "id": "nacionalidade",
                        "label": "Nacionalidade Atual",
                        "type": "country",
                        "required": True,
                        "official_mapping": "PartA_Nationality",
                    },
                    {
                        "id": "raca_etnia_tribo",
                        "label": "Raça, Grupo Étnico ou Tribo",
                        "type": "text",
                        "required": False,
                        "official_mapping": "PartA_Race_Ethnic_TribalGroup",
                    },
                    {
                        "id": "religiao",
                        "label": "Religião",
                        "type": "text",
                        "required": False,
                        "official_mapping": "PartA_Religion",
                    },
                    {
                        "id": "sexo",
                        "label": "Sexo",
                        "type": "select",
                        "required": True,
                        "options": ["Masculino", "Feminino"],
                        "official_mapping": "PartA_Sex",
                    },
                    {
                        "id": "estado_civil",
                        "label": "Estado Civil",
                        "type": "select",
                        "required": True,
                        "options": ["Solteiro(a)", "Casado(a)", "Divorciado(a)", "Viúvo(a)"],
                        "official_mapping": "PartA_MaritalStatus",
                    },
                ],
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
                        "official_mapping": "PartA_PassportNumber",
                    },
                    {
                        "id": "numero_i94",
                        "label": "Número do I-94",
                        "type": "text",
                        "required": True,
                        "validation": "numeric",
                        "official_mapping": "PartA_I94Number",
                    },
                    {
                        "id": "data_chegada_eua",
                        "label": "Data de Chegada nos EUA",
                        "type": "date",
                        "required": True,
                        "validation": "date|past",
                        "official_mapping": "PartA_DateOfArrival",
                    },
                    {
                        "id": "local_chegada",
                        "label": "Local de Chegada nos EUA",
                        "type": "text",
                        "required": True,
                        "official_mapping": "PartA_PlaceOfArrival",
                    },
                    {
                        "id": "status_entrada",
                        "label": "Status na Entrada",
                        "type": "text",
                        "required": True,
                        "placeholder": "B-2, F-1, etc.",
                        "official_mapping": "PartA_StatusAtEntry",
                    },
                ],
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
                        "official_mapping": "PartA_CurrentAddress",
                    },
                    {
                        "id": "cidade",
                        "label": "Cidade",
                        "type": "text",
                        "required": True,
                        "official_mapping": "PartA_City",
                    },
                    {
                        "id": "estado",
                        "label": "Estado",
                        "type": "select",
                        "required": True,
                        "options": [
                            "AL",
                            "AK",
                            "AZ",
                            "AR",
                            "CA",
                            "CO",
                            "CT",
                            "DE",
                            "FL",
                            "GA",
                            "HI",
                            "ID",
                            "IL",
                            "IN",
                            "IA",
                            "KS",
                            "KY",
                            "LA",
                            "ME",
                            "MD",
                            "MA",
                            "MI",
                            "MN",
                            "MS",
                            "MO",
                            "MT",
                            "NE",
                            "NV",
                            "NH",
                            "NJ",
                            "NM",
                            "NY",
                            "NC",
                            "ND",
                            "OH",
                            "OK",
                            "OR",
                            "PA",
                            "RI",
                            "SC",
                            "SD",
                            "TN",
                            "TX",
                            "UT",
                            "VT",
                            "VA",
                            "WA",
                            "WV",
                            "WI",
                            "WY",
                        ],
                        "official_mapping": "PartA_State",
                    },
                    {
                        "id": "cep",
                        "label": "ZIP Code",
                        "type": "text",
                        "required": True,
                        "validation": "numeric|length:5",
                        "official_mapping": "PartA_ZipCode",
                    },
                    {
                        "id": "telefone",
                        "label": "Telefone",
                        "type": "tel",
                        "required": True,
                        "official_mapping": "PartA_Telephone",
                    },
                    {
                        "id": "email",
                        "label": "Email",
                        "type": "email",
                        "required": True,
                        "validation": "email",
                        "official_mapping": "PartA_Email",
                    },
                ],
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
                            "Pertencimento a Grupo Social Particular",
                        ],
                        "official_mapping": "PartB_FearBasis",
                    },
                    {
                        "id": "historia_perseguicao",
                        "label": "Descreva em detalhes a perseguição ou medo de perseguição que você sofreu ou teme sofrer",
                        "type": "textarea",
                        "required": True,
                        "placeholder": "Descreva os eventos específicos, quando ocorreram, quem te perseguiu, por que...",
                        "validation": "min:500",
                        "official_mapping": "PartB_DetailedExplanation",
                        "help_text": "Seja o mais detalhado possível. Mínimo 500 caracteres.",
                    },
                    {
                        "id": "retornar_seguro",
                        "label": "Por que você não pode retornar ao seu país de origem com segurança?",
                        "type": "textarea",
                        "required": True,
                        "validation": "min:200",
                        "official_mapping": "PartB_WhyCannotReturn",
                    },
                ],
            },
        ],
        "total_fields": 28,
        "estimated_time": "45-60 minutos",
        "warning": "Este formulário é mais complexo e requer documentação extensa.",
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
                        "official_mapping": "Pt1_FamilyName, Pt1_GivenName",
                    },
                    {
                        "id": "data_nascimento",
                        "label": "Data de Nascimento",
                        "type": "date",
                        "required": True,
                        "validation": "date|past",
                        "official_mapping": "Pt1_DateOfBirth",
                    },
                    {
                        "id": "pais_nascimento",
                        "label": "País de Nascimento",
                        "type": "country",
                        "required": True,
                        "official_mapping": "Pt1_CountryOfBirth",
                    },
                    {
                        "id": "numero_passaporte",
                        "label": "Número do Passaporte",
                        "type": "text",
                        "required": True,
                        "official_mapping": "Pt1_PassportNumber",
                    },
                    {
                        "id": "email",
                        "label": "Email",
                        "type": "email",
                        "required": True,
                        "validation": "email",
                        "official_mapping": "Pt1_Email",
                    },
                ],
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
                        "options": ["Ciências", "Artes", "Educação", "Negócios", "Atletismo"],
                        "official_mapping": "Pt2_FieldOfExtraordinaryAbility",
                    },
                    {
                        "id": "descricao_expertise",
                        "label": "Descreva sua área específica de expertise",
                        "type": "textarea",
                        "required": True,
                        "placeholder": "Ex: Inteligência Artificial e Machine Learning...",
                        "validation": "min:100",
                        "official_mapping": "Pt2_SpecificArea",
                    },
                ],
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
                        "official_mapping": "Pt3_Criterion1_Awards",
                    },
                    {
                        "id": "associacoes_memberships",
                        "label": "2. Membro de associações que exigem conquistas excepcionais",
                        "type": "textarea",
                        "required": False,
                        "placeholder": "Liste associações profissionais de elite...",
                        "official_mapping": "Pt3_Criterion2_Membership",
                    },
                    {
                        "id": "publicacoes_midia",
                        "label": "3. Material publicado sobre você em mídia profissional ou grande mídia",
                        "type": "textarea",
                        "required": False,
                        "placeholder": "Liste publicações, artigos, entrevistas...",
                        "official_mapping": "Pt3_Criterion3_PublishedMaterial",
                    },
                    {
                        "id": "juiz_trabalhos",
                        "label": "4. Participação como juiz do trabalho de outros no campo",
                        "type": "textarea",
                        "required": False,
                        "placeholder": "Descreva experiências como revisor, avaliador...",
                        "official_mapping": "Pt3_Criterion4_Judging",
                    },
                    {
                        "id": "contribuicoes_originais",
                        "label": "5. Contribuições científicas ou acadêmicas originais de grande importância",
                        "type": "textarea",
                        "required": False,
                        "placeholder": "Descreva pesquisas, inovações, descobertas...",
                        "validation": "min:200",
                        "official_mapping": "Pt3_Criterion5_OriginalContributions",
                    },
                    {
                        "id": "publicacoes_academicas",
                        "label": "6. Autoria de artigos acadêmicos em periódicos ou publicações importantes",
                        "type": "textarea",
                        "required": False,
                        "placeholder": "Liste publicações científicas com citações...",
                        "official_mapping": "Pt3_Criterion6_ScholarlyArticles",
                    },
                    {
                        "id": "exibicoes_artisticas",
                        "label": "7. Exibições ou apresentações artísticas em locais de destaque",
                        "type": "textarea",
                        "required": False,
                        "placeholder": "Para artistas: liste exposições, performances...",
                        "official_mapping": "Pt3_Criterion7_ArtisticExhibitions",
                    },
                    {
                        "id": "papel_critico",
                        "label": "8. Papel crítico ou liderança em organizações de reputação distinta",
                        "type": "textarea",
                        "required": False,
                        "placeholder": "Descreva posições de liderança...",
                        "official_mapping": "Pt3_Criterion8_CriticalRole",
                    },
                    {
                        "id": "salario_alto",
                        "label": "9. Salário ou remuneração significativamente alta em relação a outros no campo",
                        "type": "textarea",
                        "required": False,
                        "placeholder": "Forneça evidências de remuneração alta...",
                        "official_mapping": "Pt3_Criterion9_HighSalary",
                    },
                    {
                        "id": "sucesso_comercial",
                        "label": "10. Sucesso comercial nas artes performáticas",
                        "type": "textarea",
                        "required": False,
                        "placeholder": "Para artistas: vendas de discos, bilheteria...",
                        "official_mapping": "Pt3_Criterion10_CommercialSuccess",
                    },
                ],
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
                        "official_mapping": "Pt4_IntentionToContinue",
                    }
                ],
            },
        ],
        "total_fields": 20,
        "estimated_time": "60-90 minutos",
        "warning": "EB-1A requer documentação extensa. Você deve demonstrar pelo menos 3 dos 10 critérios com evidências sólidas.",
    }


def get_f1_friendly_form_structure() -> Dict[str, Any]:
    """
    Estrutura para F-1 Student Visa (Extension/Change of Status)
    Usa formulário I-539 com campos específicos para estudantes
    Inclui validações jurídicas conforme diretrizes de advogados de imigração
    """
    base_structure = get_i539_friendly_form_structure()

    # Add F-1 specific fields
    base_structure["form_name"] = "Extensão de Visto de Estudante (F-1)"
    base_structure["warning"] = (
        "Para estudantes F-1, você também precisará do Form I-20 atualizado da sua escola."
    )

    # Add student-specific section with legal validation fields
    student_section = {
        "id": "informacoes_estudante",
        "title": "6. Informações do Estudante F-1",
        "description": "Informações específicas para estudantes",
        "fields": [
            {
                "id": "nome_escola",
                "label": "Nome da Escola/Universidade",
                "type": "text",
                "required": True,
                "placeholder": "Harvard University",
                "official_mapping": "Pt3_SchoolName",
            },
            {
                "id": "programa_estudo",
                "label": "Programa de Estudo",
                "type": "text",
                "required": True,
                "placeholder": "Bachelor of Science in Computer Science",
                "official_mapping": "Pt3_ProgramOfStudy",
            },
            {
                "id": "data_conclusao_esperada",
                "label": "Data de Conclusão Esperada",
                "type": "date",
                "required": True,
                "validation": "date|future",
                "official_mapping": "Pt3_ExpectedCompletionDate",
            },
            {
                "id": "trabalhando_cpt_opt",
                "label": "Você está trabalhando sob CPT ou OPT?",
                "type": "select",
                "required": True,
                "options": [
                    "Não",
                    "CPT (Curricular Practical Training)",
                    "OPT (Optional Practical Training)",
                ],
                "official_mapping": "Pt3_EmploymentStatus",
            },
        ],
    }

    # LEGAL VALIDATION SECTION - F1 Requirements
    legal_validation_section = {
        "id": "validacao_legal_f1",
        "title": "7. Requisitos Legais F-1 (OBRIGATÓRIO)",
        "description": "Validações obrigatórias conforme legislação de imigração",
        "fields": [
            {
                "id": "english_proficiency_proof",
                "label": "Você possui comprovação de proficiência em inglês?",
                "type": "select",
                "required": True,
                "options": ["none", "TOEFL", "IELTS", "Duolingo", "Cambridge", "PTE", "Outro"],
                "help_text": "❌ OBRIGATÓRIO: Prova de proficiência em inglês é necessária para admissão em instituições educacionais nos EUA",
            },
            {
                "id": "has_i20_issued",
                "label": "Você já possui o formulário I-20 emitido pela instituição?",
                "type": "select",
                "required": True,
                "options": ["yes", "no"],
                "help_text": "❌ OBRIGATÓRIO: O I-20 deve estar emitido antes de prosseguir com a aplicação",
            },
            {
                "id": "sevis_fee_paid",
                "label": "Você já pagou a taxa SEVIS (I-901)?",
                "type": "select",
                "required": True,
                "options": ["yes", "no"],
                "help_text": "❌ OBRIGATÓRIO: Taxa SEVIS deve estar paga. Acesse: https://www.fmjfee.com/",
            },
            {
                "id": "current_visa_status",
                "label": "Qual é seu status de visto atual nos EUA?",
                "type": "select",
                "required": False,
                "options": ["F1", "B2", "J1", "H1B", "Outro", "Nenhum (primeira aplicação)"],
                "help_text": "Se você está mudando de B2 para F1, deve esperar 90 dias desde a entrada nos EUA",
            },
            {
                "id": "entry_date_usa",
                "label": "Data de entrada nos EUA (se aplicável)",
                "type": "date",
                "required": False,
                "validation": "date|past",
                "help_text": "Necessário se estiver mudando de outro status (ex: B2 → F1)",
            },
            {
                "id": "plans_to_work",
                "label": "Você planeja trabalhar durante seus estudos?",
                "type": "select",
                "required": True,
                "options": ["no", "yes"],
                "help_text": "Trabalho para estudantes F-1 possui restrições legais",
            },
            {
                "id": "work_type",
                "label": "Tipo de trabalho (se aplicável)",
                "type": "select",
                "required": False,
                "options": ["on_campus", "off_campus", "opt", "cpt"],
                "help_text": "❌ Trabalho off-campus NÃO é permitido. Apenas on-campus (máx 20h/semana) ou OPT após conclusão",
            },
            {
                "id": "work_hours_per_week",
                "label": "Horas de trabalho por semana (se aplicável)",
                "type": "text",
                "required": False,
                "placeholder": "20",
                "validation": "numeric",
                "help_text": "❌ Trabalho on-campus limitado a 20 horas por semana durante o período letivo",
            },
            {
                "id": "plans_to_travel_during_process",
                "label": "Você planeja viajar para fora dos EUA durante o processo?",
                "type": "select",
                "required": True,
                "options": ["no", "yes"],
                "help_text": "⚠️ ATENÇÃO CRÍTICA: Viajar para fora dos EUA durante o processo CANCELA seu pedido!",
            },
        ],
    }

    base_structure["sections"].append(student_section)
    base_structure["sections"].append(legal_validation_section)
    base_structure["total_fields"] = 40

    return base_structure


def get_h1b_friendly_form_structure() -> Dict[str, Any]:
    """
    Estrutura para H-1B Specialty Occupation (Extension/Change of Status)
    Usa formulário I-539 com campos específicos para H-1B
    """
    base_structure = get_i539_friendly_form_structure()

    base_structure["form_name"] = "Extensão/Mudança para Visto H-1B (Trabalho Especializado)"
    base_structure["warning"] = (
        "Para H-1B, você precisará de uma petição I-129 aprovada do seu empregador."
    )

    # Add H-1B specific section
    h1b_section = {
        "id": "informacoes_emprego",
        "title": "6. Informações de Emprego H-1B",
        "description": "Dados do seu emprego especializado",
        "fields": [
            {
                "id": "nome_empregador",
                "label": "Nome do Empregador/Empresa",
                "type": "text",
                "required": True,
                "placeholder": "Google LLC",
                "official_mapping": "Pt3_EmployerName",
            },
            {
                "id": "cargo",
                "label": "Cargo/Posição",
                "type": "text",
                "required": True,
                "placeholder": "Software Engineer",
                "official_mapping": "Pt3_JobTitle",
            },
            {
                "id": "salario_anual",
                "label": "Salário Anual (USD)",
                "type": "text",
                "required": True,
                "placeholder": "120000",
                "validation": "numeric",
                "official_mapping": "Pt3_AnnualSalary",
            },
            {
                "id": "numero_petição_i129",
                "label": "Número da Petição I-129",
                "type": "text",
                "required": True,
                "placeholder": "EAC1234567890",
                "official_mapping": "Pt3_I129ReceiptNumber",
            },
            {
                "id": "data_aprovacao_i129",
                "label": "Data de Aprovação do I-129",
                "type": "date",
                "required": True,
                "validation": "date|past",
                "official_mapping": "Pt3_I129ApprovalDate",
            },
        ],
    }

    base_structure["sections"].append(h1b_section)
    base_structure["total_fields"] = 32

    return base_structure


def get_b2_friendly_form_structure() -> Dict[str, Any]:
    """
    Estrutura para B-2 Tourist Visa Extension
    Formulário I-539 simplificado para turistas
    Inclui validações jurídicas conforme diretrizes de advogados de imigração
    """
    base_structure = get_i539_friendly_form_structure()

    base_structure["form_name"] = "Extensão de Visto de Turista (B-2)"
    base_structure["estimated_time"] = "15-20 minutos"
    base_structure["warning"] = (
        "Extensões de B-2 são normalmente concedidas apenas em casos de emergência ou circunstâncias extraordinárias."
    )

    # Add tourist-specific section
    tourist_section = {
        "id": "motivo_extensao_turista",
        "title": "6. Motivo da Extensão (B-2)",
        "description": "Por que você precisa estender sua estadia?",
        "fields": [
            {
                "id": "motivo_emergencia",
                "label": "Motivo da Extensão",
                "type": "select",
                "required": True,
                "options": [
                    "Emergência médica pessoal",
                    "Emergência médica familiar",
                    "Questões legais urgentes",
                    "Outro motivo extraordinário",
                ],
                "official_mapping": "Pt4_ReasonForExtension",
            },
            {
                "id": "explicacao_detalhada",
                "label": "Explique detalhadamente o motivo da extensão",
                "type": "textarea",
                "required": True,
                "placeholder": "Descreva a situação que justifica a extensão...",
                "validation": "min:200",
                "official_mapping": "Pt4_DetailedExplanation",
                "help_text": "Seja específico. Extensões de B-2 são difíceis de obter sem motivo válido.",
            },
            {
                "id": "fundos_manutencao",
                "label": "Como você planeja se sustentar financeiramente durante a extensão?",
                "type": "textarea",
                "required": True,
                "placeholder": "Poupanças pessoais, suporte familiar, etc.",
                "validation": "min:50",
                "official_mapping": "Pt4_FinancialSupport",
            },
        ],
    }

    # LEGAL VALIDATION SECTION - B2 Requirements
    legal_validation_section = {
        "id": "validacao_legal_b2",
        "title": "7. Requisitos Legais B-2 (OBRIGATÓRIO)",
        "description": "Validações obrigatórias conforme legislação de imigração",
        "fields": [
            {
                "id": "entry_type",
                "label": "Como você entrou nos EUA?",
                "type": "select",
                "required": True,
                "options": ["Visto B-2", "Visto B-1", "ESTA", "Outro visto"],
                "help_text": "❌ ATENÇÃO: ESTA não pode ser estendido. Você deve sair dos EUA e retornar.",
            },
            {
                "id": "entry_date_usa",
                "label": "Data de entrada nos EUA",
                "type": "date",
                "required": True,
                "validation": "date|past",
                "help_text": "❌ OBRIGATÓRIO: Você deve esperar pelo menos 90 dias desde a entrada para solicitar extensão",
            },
            {
                "id": "i94_expiration_date",
                "label": "Data de vencimento do I-94",
                "type": "date",
                "required": True,
                "validation": "date",
                "help_text": "❌ OBRIGATÓRIO: Verifique em https://i94.cbp.dhs.gov/",
            },
            {
                "id": "extension_duration_months",
                "label": "Por quantos meses você deseja estender? (padrão: 6 meses)",
                "type": "text",
                "required": True,
                "placeholder": "6",
                "validation": "numeric",
                "help_text": "⚠️ A extensão padrão é de 6 meses. Períodos maiores podem ser negados.",
            },
            {
                "id": "plans_to_travel_during_process",
                "label": "Você planeja viajar para fora dos EUA durante o processo?",
                "type": "select",
                "required": True,
                "options": ["no", "yes"],
                "help_text": "🚨 ATENÇÃO CRÍTICA: Sair dos EUA durante o processo CANCELA automaticamente seu pedido!",
            },
            {
                "id": "has_i94",
                "label": "Você possui o formulário I-94?",
                "type": "select",
                "required": True,
                "options": ["yes", "no"],
                "help_text": "❌ OBRIGATÓRIO: Baixe em https://i94.cbp.dhs.gov/",
            },
        ],
    }

    base_structure["sections"].append(tourist_section)
    base_structure["sections"].append(legal_validation_section)
    base_structure["total_fields"] = 36

    return base_structure


def get_l1_friendly_form_structure() -> Dict[str, Any]:
    """
    Estrutura para L-1 Intracompany Transfer
    Formulário I-539 para extensão/mudança
    """
    base_structure = get_i539_friendly_form_structure()

    base_structure["form_name"] = "Extensão/Mudança L-1 (Transferência Intra-Empresa)"
    base_structure["warning"] = (
        "Para L-1, você precisará de petição I-129 aprovada e comprovação de relacionamento entre empresas."
    )

    l1_section = {
        "id": "informacoes_l1",
        "title": "6. Informações L-1",
        "fields": [
            {
                "id": "empresa_eua",
                "label": "Nome da Empresa nos EUA",
                "type": "text",
                "required": True,
                "official_mapping": "Pt3_USCompanyName",
            },
            {
                "id": "empresa_origem",
                "label": "Nome da Empresa no País de Origem",
                "type": "text",
                "required": True,
                "official_mapping": "Pt3_ForeignCompanyName",
            },
            {
                "id": "tipo_l1",
                "label": "Tipo de L-1",
                "type": "select",
                "required": True,
                "options": ["L-1A (Executivo/Gerente)", "L-1B (Conhecimento Especializado)"],
                "official_mapping": "Pt3_L1Type",
            },
            {
                "id": "cargo_eua",
                "label": "Cargo nos EUA",
                "type": "text",
                "required": True,
                "official_mapping": "Pt3_JobTitleUS",
            },
            {
                "id": "tempo_empresa_origem",
                "label": "Tempo de Trabalho na Empresa do Exterior (em meses)",
                "type": "text",
                "required": True,
                "validation": "numeric",
                "official_mapping": "Pt3_TimeWithForeignCompany",
                "help_text": "Mínimo 1 ano nos últimos 3 anos",
            },
        ],
    }

    base_structure["sections"].append(l1_section)
    base_structure["total_fields"] = 32

    return base_structure


def get_o1_friendly_form_structure() -> Dict[str, Any]:
    """
    Estrutura para O-1 Individual with Extraordinary Ability or Achievement
    Formulário I-539 para dependentes O-3 ou extensão
    """
    base_structure = get_i539_friendly_form_structure()

    base_structure["form_name"] = "Extensão/Mudança O-1 (Habilidade Extraordinária)"
    base_structure["warning"] = (
        "Para O-1, você precisa demonstrar habilidade extraordinária contínua e petição I-129 aprovada."
    )

    o1_section = {
        "id": "informacoes_o1",
        "title": "6. Informações O-1",
        "fields": [
            {
                "id": "categoria_o1",
                "label": "Categoria O-1",
                "type": "select",
                "required": True,
                "options": [
                    "O-1A (Ciências, Educação, Negócios, Atletismo)",
                    "O-1B (Artes, Cinema, TV)",
                ],
                "official_mapping": "Pt3_O1Category",
            },
            {
                "id": "area_especialidade",
                "label": "Área de Especialidade",
                "type": "text",
                "required": True,
                "placeholder": "Ex: Artificial Intelligence Research",
                "official_mapping": "Pt3_FieldOfExpertise",
            },
            {
                "id": "realizacoes_principais",
                "label": "Principais Realizações que Demonstram Habilidade Extraordinária",
                "type": "textarea",
                "required": True,
                "placeholder": "Liste prêmios, publicações, reconhecimentos...",
                "validation": "min:200",
                "official_mapping": "Pt3_MajorAchievements",
            },
            {
                "id": "empregador_patrocinador",
                "label": "Empregador/Agente Patrocinador",
                "type": "text",
                "required": True,
                "official_mapping": "Pt3_PetitionerName",
            },
        ],
    }

    base_structure["sections"].append(o1_section)
    base_structure["total_fields"] = 31

    return base_structure


def get_green_card_renewal_form_structure() -> Dict[str, Any]:
    """
    Estrutura para Renovação de Green Card (I-90)
    Inclui validações jurídicas conforme diretrizes de advogados de imigração
    """
    return {
        "form_code": "I-90",
        "form_name": "Renovação de Green Card",
        "estimated_time": "20-25 minutos",
        "total_fields": 25,
        "warning": "Você pode renovar seu Green Card até 6 meses antes do vencimento.",
        "sections": [
            {
                "id": "informacoes_green_card",
                "title": "1. Informações do Green Card Atual",
                "description": "Dados do seu Green Card que será renovado",
                "fields": [
                    {
                        "id": "nome_completo",
                        "label": "Nome Completo (como está no Green Card)",
                        "type": "text",
                        "required": True,
                        "placeholder": "João Silva Santos",
                    },
                    {
                        "id": "alien_registration_number",
                        "label": "Alien Registration Number (A-Number)",
                        "type": "text",
                        "required": True,
                        "placeholder": "A123456789",
                        "help_text": "Número de 9 dígitos no seu Green Card",
                    },
                    {
                        "id": "green_card_expiration_date",
                        "label": "Data de Vencimento do Green Card",
                        "type": "date",
                        "required": True,
                        "validation": "date",
                        "help_text": "❌ OBRIGATÓRIO: Data de vencimento para validar período de renovação",
                    },
                    {
                        "id": "data_emissao_green_card",
                        "label": "Data de Emissão do Green Card",
                        "type": "date",
                        "required": True,
                        "validation": "date|past",
                    },
                    {
                        "id": "categoria_green_card",
                        "label": "Categoria do Green Card",
                        "type": "select",
                        "required": True,
                        "options": [
                            "IR1 - Spouse of U.S. Citizen",
                            "IR2 - Child of U.S. Citizen",
                            "EB-1 - Priority Worker",
                            "EB-2 - Advanced Degree",
                            "EB-3 - Skilled Worker",
                            "DV - Diversity Visa",
                            "Outro",
                        ],
                    },
                ],
            },
            {
                "id": "endereco_atual",
                "title": "2. Endereço Atual",
                "description": "Onde você mora atualmente",
                "fields": [
                    {
                        "id": "endereco_completo",
                        "label": "Endereço Completo",
                        "type": "text",
                        "required": True,
                        "placeholder": "123 Main Street, Apt 4B",
                    },
                    {
                        "id": "cidade",
                        "label": "Cidade",
                        "type": "text",
                        "required": True,
                        "placeholder": "New York",
                    },
                    {
                        "id": "estado",
                        "label": "Estado",
                        "type": "text",
                        "required": True,
                        "placeholder": "NY",
                    },
                    {
                        "id": "cep",
                        "label": "ZIP Code",
                        "type": "text",
                        "required": True,
                        "placeholder": "10001",
                        "validation": "numeric",
                    },
                ],
            },
            {
                "id": "motivo_renovacao",
                "title": "3. Motivo da Renovação",
                "description": "Por que você está renovando",
                "fields": [
                    {
                        "id": "razao_renovacao",
                        "label": "Razão da Renovação",
                        "type": "select",
                        "required": True,
                        "options": [
                            "Green Card vencido ou vai vencer em 6 meses",
                            "Green Card perdido ou roubado",
                            "Green Card danificado",
                            "Mudança de nome",
                            "Erro no Green Card original",
                        ],
                    }
                ],
            },
            {
                "id": "validacao_legal_green_card",
                "title": "4. Validação Legal (OBRIGATÓRIO)",
                "description": "Verificações conforme legislação de imigração",
                "fields": [
                    {
                        "id": "passport_expiration_date",
                        "label": "Data de Validade do Passaporte",
                        "type": "date",
                        "required": True,
                        "validation": "date",
                        "help_text": "⚠️ Se vencido, você pode continuar mas considere renovar",
                    },
                    {
                        "id": "has_current_visa_copy",
                        "label": "Você possui cópia do Green Card atual?",
                        "type": "select",
                        "required": True,
                        "options": ["yes", "no"],
                        "help_text": "Necessário anexar cópia (frente e verso)",
                    },
                    {
                        "id": "has_passport_photos",
                        "label": "Você possui 2 fotos tamanho passaporte?",
                        "type": "select",
                        "required": True,
                        "options": ["yes", "no"],
                        "help_text": "❌ OBRIGATÓRIO: 2 fotos padrão passaporte",
                    },
                ],
            },
        ],
    }


def get_marriage_adjustment_form_structure() -> Dict[str, Any]:
    """
    Estrutura para Ajuste de Status por Casamento
    Inclui validações jurídicas conforme diretrizes de advogados de imigração
    """
    return {
        "form_code": "I-485-MARRIAGE",
        "form_name": "Ajuste de Status por Casamento (Green Card)",
        "estimated_time": "45-60 minutos",
        "total_fields": 45,
        "warning": "Este processo é apenas para quem está nos EUA com entrada legal.",
        "sections": [
            {
                "id": "informacoes_pessoais_marriage",
                "title": "1. Informações Pessoais do Requerente",
                "fields": [
                    {
                        "id": "nome_completo",
                        "label": "Nome Completo",
                        "type": "text",
                        "required": True,
                        "placeholder": "João Silva Santos",
                    },
                    {
                        "id": "data_nascimento",
                        "label": "Data de Nascimento",
                        "type": "date",
                        "required": True,
                        "validation": "date|past",
                    },
                    {
                        "id": "pais_nascimento",
                        "label": "País de Nascimento",
                        "type": "country",
                        "required": True,
                        "placeholder": "Brazil",
                    },
                ],
            },
            {
                "id": "informacoes_casamento",
                "title": "2. Informações do Casamento",
                "fields": [
                    {
                        "id": "marriage_date",
                        "label": "Data do Casamento",
                        "type": "date",
                        "required": True,
                        "validation": "date|past",
                        "help_text": "❌ OBRIGATÓRIO: Data do casamento legal",
                    },
                    {
                        "id": "local_casamento",
                        "label": "Local do Casamento (Cidade, Estado/País)",
                        "type": "text",
                        "required": True,
                        "placeholder": "Las Vegas, Nevada",
                    },
                    {
                        "id": "nome_conjuge",
                        "label": "Nome Completo do Cônjuge (Peticionário)",
                        "type": "text",
                        "required": True,
                        "placeholder": "Mary Johnson",
                    },
                    {
                        "id": "conjuge_cidadao_americano",
                        "label": "Seu cônjuge é cidadão americano?",
                        "type": "select",
                        "required": True,
                        "options": ["yes", "no"],
                        "help_text": "Para ajuste por casamento, cônjuge deve ser cidadão ou residente permanente",
                    },
                ],
            },
            {
                "id": "validacao_legal_marriage",
                "title": "3. Requisitos Legais (OBRIGATÓRIO)",
                "description": "Validações obrigatórias conforme legislação de imigração",
                "fields": [
                    {
                        "id": "currently_in_usa",
                        "label": "Você está atualmente nos Estados Unidos?",
                        "type": "select",
                        "required": True,
                        "options": ["yes", "no"],
                        "help_text": "❌ AJUSTE DE STATUS APENAS NOS EUA: Se não, deve fazer processo consular",
                    },
                    {
                        "id": "legal_entry",
                        "label": "Você entrou legalmente nos EUA?",
                        "type": "select",
                        "required": True,
                        "options": ["yes", "no"],
                        "help_text": "❌ ENTRADA LEGAL OBRIGATÓRIA: Com visto válido (B2, F1, etc.)",
                    },
                    {
                        "id": "entry_visa_type",
                        "label": "Com qual visto você entrou?",
                        "type": "select",
                        "required": True,
                        "options": [
                            "B-2 (Turista)",
                            "F-1 (Estudante)",
                            "H-1B (Trabalho)",
                            "J-1 (Intercâmbio)",
                            "Outro",
                        ],
                        "help_text": "💡 Concurrent filing aceito para entrada legal com visto de visitante",
                    },
                    {
                        "id": "entry_date_usa",
                        "label": "Data de Entrada nos EUA",
                        "type": "date",
                        "required": True,
                        "validation": "date|past",
                    },
                    {
                        "id": "i94_expiration_date",
                        "label": "Data de Vencimento do I-94",
                        "type": "date",
                        "required": True,
                        "validation": "date",
                        "help_text": "Verifique em https://i94.cbp.dhs.gov/",
                    },
                ],
            },
            {
                "id": "formularios_obrigatorios",
                "title": "4. Formulários Obrigatórios",
                "description": "Confirme quais formulários serão incluídos",
                "fields": [
                    {
                        "id": "has_i_130",
                        "label": "I-130 - Petição para Parente Estrangeiro",
                        "type": "select",
                        "required": True,
                        "options": ["yes", "no"],
                        "help_text": "❌ OBRIGATÓRIO",
                    },
                    {
                        "id": "has_i_130a",
                        "label": "I-130A - Informações Suplementares",
                        "type": "select",
                        "required": True,
                        "options": ["yes", "no"],
                        "help_text": "❌ OBRIGATÓRIO",
                    },
                    {
                        "id": "has_i_485",
                        "label": "I-485 - Ajuste de Status",
                        "type": "select",
                        "required": True,
                        "options": ["yes", "no"],
                        "help_text": "❌ OBRIGATÓRIO",
                    },
                    {
                        "id": "has_i_864",
                        "label": "I-864 - Affidavit of Support (Suporte Financeiro)",
                        "type": "select",
                        "required": True,
                        "options": ["yes", "no"],
                        "help_text": "❌ OBRIGATÓRIO: Seu cônjuge deve preencher",
                    },
                ],
            },
            {
                "id": "formularios_opcionais",
                "title": "5. Formulários Opcionais (Recomendados)",
                "fields": [
                    {
                        "id": "wants_work_permit",
                        "label": "Você deseja autorização de trabalho?",
                        "type": "select",
                        "required": True,
                        "options": ["yes", "no"],
                        "help_text": "💡 RECOMENDADO: Permite trabalhar enquanto aguarda o Green Card",
                    },
                    {
                        "id": "has_i_765",
                        "label": "I-765 - Autorização de Trabalho (EAD)",
                        "type": "select",
                        "required": False,
                        "options": ["yes", "no"],
                        "help_text": "Incluir se deseja trabalhar",
                    },
                    {
                        "id": "wants_travel_permit",
                        "label": "Você deseja permissão para viagem (Advance Parole)?",
                        "type": "select",
                        "required": True,
                        "options": ["yes", "no"],
                        "help_text": "💡 RECOMENDADO: Permite viajar internacionalmente durante o processo",
                    },
                    {
                        "id": "has_i_131",
                        "label": "I-131 - Advance Parole (Permissão de Viagem)",
                        "type": "select",
                        "required": False,
                        "options": ["yes", "no"],
                        "help_text": "Incluir se deseja viajar",
                    },
                ],
            },
            {
                "id": "documentacao_marriage",
                "title": "6. Documentação Necessária",
                "fields": [
                    {
                        "id": "has_passport",
                        "label": "Cópia do passaporte válido",
                        "type": "select",
                        "required": True,
                        "options": ["yes", "no"],
                    },
                    {
                        "id": "has_birth_certificate",
                        "label": "Certidão de nascimento traduzida",
                        "type": "select",
                        "required": True,
                        "options": ["yes", "no"],
                    },
                    {
                        "id": "has_marriage_certificate",
                        "label": "Certidão de casamento (traduzida se necessário)",
                        "type": "select",
                        "required": True,
                        "options": ["yes", "no"],
                    },
                    {
                        "id": "has_passport_photos",
                        "label": "2 fotos tamanho passaporte",
                        "type": "select",
                        "required": True,
                        "options": ["yes", "no"],
                    },
                ],
            },
        ],
    }


def get_f1_reinstatement_form_structure() -> Dict[str, Any]:
    """
    Estrutura para F-1 Reinstatement
    Inclui validações jurídicas conforme diretrizes de advogados de imigração
    """
    return {
        "form_code": "I-539-REINSTATEMENT",
        "form_name": "Reinstatement de Status F-1 (Estudante)",
        "estimated_time": "35-45 minutos",
        "total_fields": 32,
        "warning": "Reinstatement é apenas para quem teve status F-1 encerrado pela escola.",
        "sections": [
            {
                "id": "informacoes_pessoais_reinstatement",
                "title": "1. Informações Pessoais",
                "fields": [
                    {
                        "id": "nome_completo",
                        "label": "Nome Completo",
                        "type": "text",
                        "required": True,
                    },
                    {
                        "id": "data_nascimento",
                        "label": "Data de Nascimento",
                        "type": "date",
                        "required": True,
                        "validation": "date|past",
                    },
                    {
                        "id": "numero_passaporte",
                        "label": "Número do Passaporte",
                        "type": "text",
                        "required": True,
                    },
                ],
            },
            {
                "id": "status_f1_anterior",
                "title": "2. Informações do Status F-1 Anterior",
                "fields": [
                    {
                        "id": "previous_visa_status",
                        "label": "Seu status anterior era F-1?",
                        "type": "select",
                        "required": True,
                        "options": ["F1", "Outro"],
                        "help_text": "❌ Reinstatement é apenas para quem tinha status F-1",
                    },
                    {
                        "id": "nome_escola_anterior",
                        "label": "Nome da Escola Anterior",
                        "type": "text",
                        "required": True,
                        "placeholder": "Harvard University",
                    },
                    {
                        "id": "data_encerramento_status",
                        "label": "Data de Encerramento do Status F-1",
                        "type": "date",
                        "required": True,
                        "validation": "date|past",
                    },
                    {
                        "id": "f1_termination_reason",
                        "label": "Motivo do Encerramento do Status F-1",
                        "type": "textarea",
                        "required": True,
                        "placeholder": "Explique detalhadamente por que seu status F-1 foi encerrado...",
                        "validation": "min:100",
                        "help_text": "❌ OBRIGATÓRIO: Explique as circunstâncias",
                    },
                ],
            },
            {
                "id": "novo_i20_reinstatement",
                "title": "3. Novo I-20 para Reinstatement",
                "fields": [
                    {
                        "id": "nome_escola_nova",
                        "label": "Nome da Escola (pode ser a mesma)",
                        "type": "text",
                        "required": True,
                    },
                    {
                        "id": "has_new_i20_for_reinstatement",
                        "label": "Você possui novo I-20 da escola?",
                        "type": "select",
                        "required": True,
                        "options": ["yes", "no"],
                        "help_text": "❌ OBRIGATÓRIO: Você precisa de novo I-20 da escola",
                    },
                    {
                        "id": "i20_indicates_reinstatement",
                        "label": "O I-20 indica especificamente 'Reinstatement'?",
                        "type": "select",
                        "required": True,
                        "options": ["yes", "no"],
                        "help_text": "❌ OBRIGATÓRIO: I-20 deve indicar que é para Reinstatement",
                    },
                    {
                        "id": "data_inicio_programa",
                        "label": "Data de Início do Programa",
                        "type": "date",
                        "required": True,
                        "validation": "date",
                    },
                ],
            },
            {
                "id": "validacao_legal_reinstatement",
                "title": "4. Requisitos Legais (OBRIGATÓRIO)",
                "fields": [
                    {
                        "id": "has_i_539",
                        "label": "Você irá preencher o formulário I-539?",
                        "type": "select",
                        "required": True,
                        "options": ["yes", "no"],
                        "help_text": "❌ OBRIGATÓRIO: Formulário I-539 é necessário para Reinstatement",
                    },
                    {
                        "id": "motivo_atraso_aplicacao",
                        "label": "Por que você não aplicou para Reinstatement antes?",
                        "type": "textarea",
                        "required": True,
                        "placeholder": "Explique as razões do atraso...",
                        "validation": "min:100",
                    },
                    {
                        "id": "vai_retomar_estudos_imediatamente",
                        "label": "Você está pronto para retomar os estudos IMEDIATAMENTE?",
                        "type": "select",
                        "required": True,
                        "options": ["yes", "no"],
                        "help_text": "⚠️ IMPORTANTE: Você deve retornar às aulas IMEDIATAMENTE após receber o I-20",
                    },
                    {
                        "id": "has_passport_photos",
                        "label": "Você possui 2 fotos tamanho passaporte?",
                        "type": "select",
                        "required": True,
                        "options": ["yes", "no"],
                    },
                ],
            },
        ],
    }


def get_friendly_form_structure(visa_type: str) -> Dict[str, Any]:
    """
    Retorna a estrutura completa do formulário amigável para o tipo de visto especificado

    Args:
        visa_type: Código do visto (I-539, I-589, EB-1A, F-1, H-1B, B-2, L-1, O-1, etc.)

    Returns:
        Dict com a estrutura completa do formulário
    """
    structures = {
        # Base forms
        "I-539": get_i539_friendly_form_structure,
        "I-589": get_i589_friendly_form_structure,
        "EB-1A": get_eb1a_friendly_form_structure,
        "EB1A": get_eb1a_friendly_form_structure,
        "I-140": get_eb1a_friendly_form_structure,
        # Specific visa types
        "F-1": get_f1_friendly_form_structure,
        "F1": get_f1_friendly_form_structure,
        "H-1B": get_h1b_friendly_form_structure,
        "H1B": get_h1b_friendly_form_structure,
        "B-2": get_b2_friendly_form_structure,
        "B2": get_b2_friendly_form_structure,
        "L-1": get_l1_friendly_form_structure,
        "L1": get_l1_friendly_form_structure,
        "O-1": get_o1_friendly_form_structure,
        "O1": get_o1_friendly_form_structure,
        # New legal validation forms
        "I-90": get_green_card_renewal_form_structure,
        "GREEN-CARD-RENEWAL": get_green_card_renewal_form_structure,
        "I-485-MARRIAGE": get_marriage_adjustment_form_structure,
        "MARRIAGE-ADJUSTMENT": get_marriage_adjustment_form_structure,
        "ADJUSTMENT-OF-STATUS": get_marriage_adjustment_form_structure,
        "I-539-REINSTATEMENT": get_f1_reinstatement_form_structure,
        "F1-REINSTATEMENT": get_f1_reinstatement_form_structure,
        "REINSTATEMENT": get_f1_reinstatement_form_structure,
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
