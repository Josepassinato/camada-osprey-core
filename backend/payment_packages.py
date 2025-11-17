"""
Pacotes de Pagamento por Categoria de Visto
Sistema de preços para "Agente Coruja" - Mudança de Status
"""

from typing import Dict, List

# Definição de preços por categoria de visto
VISA_PACKAGES = {
    # Categoria Básica - $299.00
    "I-539": {
        "name": "Extensão/Mudança de Status",
        "price": 299.00,
        "category": "basic",
        "category_name": "Básica",
        "description": "Formulário I-539 completo com instruções",
        "includes": [
            "Formulário I-539 preenchido em PDF",
            "Checklist de documentos personalizada",
            "Instruções de envio ao USCIS",
            "Carta com informações de taxas",
            "Acesso vitalício ao formulário salvo"
        ]
    },
    "I-765": {
        "name": "Autorização de Trabalho (EAD)",
        "price": 299.00,
        "category": "basic",
        "category_name": "Básica",
        "description": "Formulário I-765 completo com instruções",
        "includes": [
            "Formulário I-765 preenchido em PDF",
            "Checklist de documentos personalizada",
            "Instruções de envio ao USCIS",
            "Carta com informações de taxas",
            "Acesso vitalício ao formulário salvo"
        ]
    },
    "I-90": {
        "name": "Renovação de Green Card",
        "price": 299.00,
        "category": "basic",
        "category_name": "Básica",
        "description": "Formulário I-90 completo com instruções",
        "includes": [
            "Formulário I-90 preenchido em PDF",
            "Checklist de documentos personalizada",
            "Instruções de envio ao USCIS",
            "Carta com informações de taxas",
            "Acesso vitalício ao formulário salvo"
        ]
    },
    
    # Categoria Especial - $800.00
    "N-400": {
        "name": "Cidadania Americana",
        "price": 800.00,
        "category": "special",
        "category_name": "Especial",
        "description": "Formulário N-400 completo com preparação para teste de cidadania",
        "includes": [
            "Formulário N-400 preenchido em PDF",
            "Checklist de documentos personalizada",
            "Instruções de envio ao USCIS",
            "Guia de preparação para teste de cidadania",
            "Perguntas e respostas do teste cívico",
            "Acesso vitalício ao formulário salvo"
        ]
    },
    "I-589": {
        "name": "Pedido de Asilo",
        "price": 800.00,
        "category": "special",
        "category_name": "Especial",
        "description": "Formulário I-589 completo para pedido de asilo",
        "includes": [
            "Formulário I-589 preenchido em PDF",
            "Checklist de documentos personalizada",
            "Instruções de envio ao USCIS",
            "Orientações para declaração pessoal",
            "Guia de evidências necessárias",
            "Acesso vitalício ao formulário salvo"
        ]
    },
    
    # Categoria Intermediária - $980.00
    "F-1": {
        "name": "Visto de Estudante",
        "price": 980.00,
        "category": "intermediate",
        "category_name": "Intermediária",
        "description": "Formulário para mudança de status para F-1",
        "includes": [
            "Formulário I-539 preenchido para F-1",
            "Checklist de documentos acadêmicos",
            "Instruções de envio ao USCIS",
            "Orientações sobre I-20 e SEVIS",
            "Carta com informações de taxas",
            "Acesso vitalício ao formulário salvo"
        ]
    },
    "I-130": {
        "name": "Petição para Familiar",
        "price": 980.00,
        "category": "intermediate",
        "category_name": "Intermediária",
        "description": "Formulário I-130 completo para petição familiar",
        "includes": [
            "Formulário I-130 preenchido em PDF",
            "Checklist de documentos familiares",
            "Instruções de envio ao USCIS",
            "Guia de evidências de relacionamento",
            "Carta com informações de taxas",
            "Acesso vitalício ao formulário salvo"
        ]
    },
    "I-751": {
        "name": "Remoção de Condições",
        "price": 980.00,
        "category": "intermediate",
        "category_name": "Intermediária",
        "description": "Formulário I-751 para remover condições do Green Card",
        "includes": [
            "Formulário I-751 preenchido em PDF",
            "Checklist de evidências de casamento",
            "Instruções de envio ao USCIS",
            "Guia completo de documentação necessária",
            "Carta com informações de taxas",
            "Acesso vitalício ao formulário salvo"
        ]
    },
    
    # Categoria Avançada - $1,400.00
    "H-1B": {
        "name": "Trabalho Especializado",
        "price": 1400.00,
        "category": "advanced",
        "category_name": "Avançada",
        "description": "Documentação completa para mudança de status H-1B",
        "includes": [
            "Formulário I-129 orientado para empregador",
            "Checklist de documentos especializados",
            "Instruções de envio ao USCIS",
            "Orientações sobre LCA e requisitos",
            "Guia de evidências profissionais",
            "Carta com informações de taxas",
            "Acesso vitalício ao formulário salvo"
        ]
    },
    "O-1": {
        "name": "Habilidade Extraordinária",
        "price": 1400.00,
        "category": "advanced",
        "category_name": "Avançada",
        "description": "Documentação completa para mudança de status O-1",
        "includes": [
            "Formulário I-129 orientado para O-1",
            "Checklist de evidências extraordinárias",
            "Instruções de envio ao USCIS",
            "Guia completo de documentação necessária",
            "Orientações sobre cartas de recomendação",
            "Carta com informações de taxas",
            "Acesso vitalício ao formulário salvo"
        ]
    },
    "I-485": {
        "name": "Ajuste de Status (Green Card)",
        "price": 1400.00,
        "category": "advanced",
        "category_name": "Avançada",
        "description": "Pacote completo para ajuste de status",
        "includes": [
            "Formulário I-485 preenchido em PDF",
            "Checklist completa de documentos",
            "Instruções de exame médico (I-693)",
            "Orientações sobre EAD e Advance Parole",
            "Guia de preparação para entrevista",
            "Carta com informações de taxas",
            "Acesso vitalício ao formulário salvo"
        ]
    },
    
    # Categoria Premium - Vistos de Alto Valor
    "EB-2 NIW": {
        "name": "EB-2 NIW (National Interest Waiver)",
        "price": 2500.00,
        "category": "premium",
        "category_name": "Premium",
        "description": "Green Card por interesse nacional - Profissionais de alto nível",
        "includes": [
            "Formulário I-140 completo preenchido em PDF",
            "Análise de elegibilidade detalhada",
            "Estratégia de evidências personalizada",
            "Checklist de documentação especializada",
            "Guia de cartas de recomendação",
            "Orientações sobre comprovação de interesse nacional",
            "Instruções de envio ao USCIS",
            "Carta com informações de taxas",
            "Acesso vitalício ao formulário salvo"
        ]
    },
    "EB-1A": {
        "name": "EB-1A (Extraordinary Ability)",
        "price": 3000.00,
        "category": "premium",
        "category_name": "Premium",
        "description": "Green Card para pessoas com habilidade extraordinária",
        "includes": [
            "Formulário I-140 completo preenchido em PDF",
            "Análise profunda dos 10 critérios EB-1A",
            "Estratégia de evidências personalizada",
            "Checklist de documentação avançada",
            "Guia completo de cartas de recomendação",
            "Orientações sobre prêmios e reconhecimentos",
            "Análise de publicações e contribuições",
            "Instruções de envio ao USCIS",
            "Carta com informações de taxas",
            "Acesso vitalício ao formulário salvo"
        ]
    }
}


def get_visa_price(visa_code: str) -> float:
    """
    Retorna o preço de um visto específico
    
    Args:
        visa_code: Código do visto (ex: "H-1B", "I-539")
    
    Returns:
        Preço em dólares (float)
    
    Raises:
        ValueError: Se o visto não existir
    """
    if visa_code not in VISA_PACKAGES:
        raise ValueError(f"Visto {visa_code} não encontrado")
    
    return VISA_PACKAGES[visa_code]["price"]


def get_visa_package(visa_code: str) -> Dict:
    """
    Retorna informações completas do pacote de um visto
    
    Args:
        visa_code: Código do visto (ex: "H-1B", "I-539")
    
    Returns:
        Dicionário com todas informações do pacote
    
    Raises:
        ValueError: Se o visto não existir
    """
    if visa_code not in VISA_PACKAGES:
        raise ValueError(f"Visto {visa_code} não encontrado")
    
    return VISA_PACKAGES[visa_code]


def get_all_packages() -> Dict[str, Dict]:
    """
    Retorna todos os pacotes disponíveis
    
    Returns:
        Dicionário com todos os pacotes
    """
    return VISA_PACKAGES


def get_packages_by_category(category: str) -> Dict[str, Dict]:
    """
    Retorna pacotes de uma categoria específica
    
    Args:
        category: "basic", "special", "intermediate", "advanced"
    
    Returns:
        Dicionário com pacotes da categoria
    """
    return {
        code: package 
        for code, package in VISA_PACKAGES.items() 
        if package["category"] == category
    }


def validate_visa_code(visa_code: str) -> bool:
    """
    Valida se um código de visto existe
    
    Args:
        visa_code: Código do visto
    
    Returns:
        True se existe, False caso contrário
    """
    return visa_code in VISA_PACKAGES


def calculate_final_price(visa_code: str, discount_percentage: float = 0.0) -> Dict:
    """
    Calcula preço final com desconto aplicado
    
    Args:
        visa_code: Código do visto
        discount_percentage: Porcentagem de desconto (0-100)
    
    Returns:
        Dict com preço original, desconto e preço final
    """
    if visa_code not in VISA_PACKAGES:
        raise ValueError(f"Visto {visa_code} não encontrado")
    
    original_price = VISA_PACKAGES[visa_code]["price"]
    discount_amount = (original_price * discount_percentage) / 100.0
    final_price = original_price - discount_amount
    
    return {
        "visa_code": visa_code,
        "visa_name": VISA_PACKAGES[visa_code]["name"],
        "original_price": round(original_price, 2),
        "discount_percentage": discount_percentage,
        "discount_amount": round(discount_amount, 2),
        "final_price": round(final_price, 2),
        "savings": round(discount_amount, 2)
    }
