"""
Sistema de Vouchers/Cupons de Desconto
Agente Coruja - Bônus de Lançamento e Promoções
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, List
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class Voucher(BaseModel):
    """Modelo de Voucher"""
    code: str
    discount_percentage: float  # Ex: 50.0 para 50%
    description: str
    valid_from: datetime
    valid_until: datetime
    max_uses: Optional[int] = None  # None = ilimitado
    current_uses: int = 0
    active: bool = True
    categories: Optional[List[str]] = None  # None = todos, ou ["basic", "intermediate", etc]
    visa_codes: Optional[List[str]] = None  # None = todos, ou ["H-1B", "I-539", etc]


# Vouchers pré-configurados
PREDEFINED_VOUCHERS = {
    "LANCAMENTO50": {
        "code": "LANCAMENTO50",
        "discount_percentage": 50.0,
        "description": "Bônus de Lançamento - 50% de Desconto",
        "valid_from": datetime(2024, 1, 1),
        "valid_until": datetime(2025, 12, 31),
        "max_uses": None,  # Ilimitado
        "current_uses": 0,
        "active": True,
        "categories": None,  # Válido para todas categorias
        "visa_codes": None   # Válido para todos vistos
    },
    "PRIMEIRACOMPRA": {
        "code": "PRIMEIRACOMPRA",
        "discount_percentage": 30.0,
        "description": "Desconto de Primeira Compra - 30% OFF",
        "valid_from": datetime(2024, 1, 1),
        "valid_until": datetime(2025, 12, 31),
        "max_uses": 1000,  # Limite de 1000 usos
        "current_uses": 0,
        "active": True,
        "categories": None,
        "visa_codes": None
    },
    "BLACKFRIDAY": {
        "code": "BLACKFRIDAY",
        "discount_percentage": 60.0,
        "description": "Black Friday - 60% de Desconto",
        "valid_from": datetime(2024, 11, 20),
        "valid_until": datetime(2024, 12, 5),
        "max_uses": None,
        "current_uses": 0,
        "active": False,  # Ativar apenas durante Black Friday
        "categories": None,
        "visa_codes": None
    },
    
    # ========================================
    # VOUCHERS DE GRATUIDADE - BETA TESTERS
    # 100% de desconto para testes
    # ========================================
    "BETA-FREE-001": {
        "code": "BETA-FREE-001",
        "discount_percentage": 100.0,
        "description": "🎁 Voucher de Gratuidade BETA - Testador #1",
        "valid_from": datetime(2024, 11, 21),
        "valid_until": datetime(2025, 12, 31),
        "max_uses": 1,  # 1 uso por voucher
        "current_uses": 0,
        "active": True,
        "categories": None,
        "visa_codes": None
    },
    "BETA-FREE-002": {
        "code": "BETA-FREE-002",
        "discount_percentage": 100.0,
        "description": "🎁 Voucher de Gratuidade BETA - Testador #2",
        "valid_from": datetime(2024, 11, 21),
        "valid_until": datetime(2025, 12, 31),
        "max_uses": 1,
        "current_uses": 0,
        "active": True,
        "categories": None,
        "visa_codes": None
    },
    "BETA-FREE-003": {
        "code": "BETA-FREE-003",
        "discount_percentage": 100.0,
        "description": "🎁 Voucher de Gratuidade BETA - Testador #3",
        "valid_from": datetime(2024, 11, 21),
        "valid_until": datetime(2025, 12, 31),
        "max_uses": 1,
        "current_uses": 0,
        "active": True,
        "categories": None,
        "visa_codes": None
    },
    "BETA-FREE-004": {
        "code": "BETA-FREE-004",
        "discount_percentage": 100.0,
        "description": "🎁 Voucher de Gratuidade BETA - Testador #4",
        "valid_from": datetime(2024, 11, 21),
        "valid_until": datetime(2025, 12, 31),
        "max_uses": 1,
        "current_uses": 0,
        "active": True,
        "categories": None,
        "visa_codes": None
    },
    "BETA-FREE-005": {
        "code": "BETA-FREE-005",
        "discount_percentage": 100.0,
        "description": "🎁 Voucher de Gratuidade BETA - Testador #5",
        "valid_from": datetime(2024, 11, 21),
        "valid_until": datetime(2025, 12, 31),
        "max_uses": 1,
        "current_uses": 0,
        "active": True,
        "categories": None,
        "visa_codes": None
    },
    "BETA-FREE-006": {
        "code": "BETA-FREE-006",
        "discount_percentage": 100.0,
        "description": "🎁 Voucher de Gratuidade BETA - Testador #6",
        "valid_from": datetime(2024, 11, 21),
        "valid_until": datetime(2025, 12, 31),
        "max_uses": 1,
        "current_uses": 0,
        "active": True,
        "categories": None,
        "visa_codes": None
    },
    "BETA-FREE-007": {
        "code": "BETA-FREE-007",
        "discount_percentage": 100.0,
        "description": "🎁 Voucher de Gratuidade BETA - Testador #7",
        "valid_from": datetime(2024, 11, 21),
        "valid_until": datetime(2025, 12, 31),
        "max_uses": 1,
        "current_uses": 0,
        "active": True,
        "categories": None,
        "visa_codes": None
    },
    "BETA-FREE-008": {
        "code": "BETA-FREE-008",
        "discount_percentage": 100.0,
        "description": "🎁 Voucher de Gratuidade BETA - Testador #8",
        "valid_from": datetime(2024, 11, 21),
        "valid_until": datetime(2025, 12, 31),
        "max_uses": 1,
        "current_uses": 0,
        "active": True,
        "categories": None,
        "visa_codes": None
    },
    "BETA-FREE-009": {
        "code": "BETA-FREE-009",
        "discount_percentage": 100.0,
        "description": "🎁 Voucher de Gratuidade BETA - Testador #9",
        "valid_from": datetime(2024, 11, 21),
        "valid_until": datetime(2025, 12, 31),
        "max_uses": 1,
        "current_uses": 0,
        "active": True,
        "categories": None,
        "visa_codes": None
    },
    "BETA-FREE-010": {
        "code": "BETA-FREE-010",
        "discount_percentage": 100.0,
        "description": "🎁 Voucher de Gratuidade BETA - Testador #10",
        "valid_from": datetime(2024, 11, 21),
        "valid_until": datetime(2025, 12, 31),
        "max_uses": 1,
        "current_uses": 0,
        "active": True,
        "categories": None,
        "visa_codes": None
    }
}


class VoucherValidationResult(BaseModel):
    """Resultado da validação de voucher"""
    valid: bool
    discount_percentage: float = 0.0
    message: str
    voucher_code: Optional[str] = None


async def validate_voucher(
    voucher_code: str, 
    visa_code: str,
    db = None
) -> VoucherValidationResult:
    """
    Valida um voucher e retorna o desconto aplicável
    
    Args:
        voucher_code: Código do voucher (ex: "LANCAMENTO50")
        visa_code: Código do visto (ex: "H-1B")
        db: Conexão com banco de dados (opcional, usa vouchers pré-configurados)
    
    Returns:
        VoucherValidationResult com informações de validação
    """
    
    # Normalizar código (uppercase, sem espaços)
    voucher_code = voucher_code.strip().upper()
    
    if not voucher_code:
        return VoucherValidationResult(
            valid=False,
            message="Código de voucher vazio"
        )
    
    # Verificar se existe nos vouchers pré-configurados
    if voucher_code not in PREDEFINED_VOUCHERS:
        # Tentar buscar no banco de dados (se fornecido)
        if db:
            try:
                voucher_doc = await db.vouchers.find_one({"code": voucher_code})
                if not voucher_doc:
                    return VoucherValidationResult(
                        valid=False,
                        message="Voucher inválido ou não encontrado"
                    )
                voucher_data = voucher_doc
            except Exception as e:
                logger.error(f"Erro ao buscar voucher no banco: {e}")
                return VoucherValidationResult(
                    valid=False,
                    message="Erro ao validar voucher"
                )
        else:
            return VoucherValidationResult(
                valid=False,
                message="Voucher inválido ou não encontrado"
            )
    else:
        voucher_data = PREDEFINED_VOUCHERS[voucher_code]
    
    # Criar objeto Voucher
    try:
        voucher = Voucher(**voucher_data)
    except Exception as e:
        logger.error(f"Erro ao criar objeto Voucher: {e}")
        return VoucherValidationResult(
            valid=False,
            message="Erro ao processar voucher"
        )
    
    # Verificar se está ativo
    if not voucher.active:
        return VoucherValidationResult(
            valid=False,
            message="Voucher não está ativo no momento"
        )
    
    # Verificar data de validade
    now = datetime.now()
    if now < voucher.valid_from:
        return VoucherValidationResult(
            valid=False,
            message="Voucher ainda não está disponível"
        )
    
    if now > voucher.valid_until:
        return VoucherValidationResult(
            valid=False,
            message="Voucher expirado"
        )
    
    # Verificar limite de usos
    if voucher.max_uses is not None and voucher.current_uses >= voucher.max_uses:
        return VoucherValidationResult(
            valid=False,
            message="Voucher atingiu o limite de usos"
        )
    
    # Verificar se é válido para este visto
    if voucher.visa_codes and visa_code not in voucher.visa_codes:
        return VoucherValidationResult(
            valid=False,
            message=f"Voucher não é válido para o visto {visa_code}"
        )
    
    # Verificar categoria (se aplicável)
    if voucher.categories:
        from payment_packages import get_visa_package
        try:
            package = get_visa_package(visa_code)
            if package["category"] not in voucher.categories:
                return VoucherValidationResult(
                    valid=False,
                    message=f"Voucher não é válido para esta categoria de visto"
                )
        except ValueError:
            logger.warning(f"Visto {visa_code} não encontrado ao validar categoria")
    
    # Voucher válido!
    return VoucherValidationResult(
        valid=True,
        discount_percentage=voucher.discount_percentage,
        message=f"✅ {voucher.description}",
        voucher_code=voucher.code
    )


def calculate_discounted_price(original_price: float, discount_percentage: float) -> Dict[str, float]:
    """
    Calcula preço com desconto
    
    Args:
        original_price: Preço original
        discount_percentage: Porcentagem de desconto (ex: 50.0 para 50%)
    
    Returns:
        Dict com original_price, discount_amount, final_price
    """
    discount_amount = (original_price * discount_percentage) / 100
    final_price = original_price - discount_amount
    
    return {
        "original_price": round(original_price, 2),
        "discount_percentage": discount_percentage,
        "discount_amount": round(discount_amount, 2),
        "final_price": round(final_price, 2)
    }


async def increment_voucher_usage(voucher_code: str, db = None):
    """
    Incrementa contador de uso de um voucher
    
    Args:
        voucher_code: Código do voucher
        db: Conexão com banco (opcional)
    """
    voucher_code = voucher_code.strip().upper()
    
    if voucher_code in PREDEFINED_VOUCHERS:
        # Para vouchers pré-configurados, apenas incrementar contador em memória
        # (em produção, você pode persistir isso no banco)
        PREDEFINED_VOUCHERS[voucher_code]["current_uses"] += 1
        logger.info(f"Voucher {voucher_code} usado. Total usos: {PREDEFINED_VOUCHERS[voucher_code]['current_uses']}")
    
    if db:
        try:
            await db.vouchers.update_one(
                {"code": voucher_code},
                {"$inc": {"current_uses": 1}}
            )
        except Exception as e:
            logger.error(f"Erro ao incrementar uso de voucher: {e}")


def get_all_active_vouchers() -> List[Dict]:
    """
    Retorna lista de todos vouchers ativos
    
    Returns:
        Lista de vouchers ativos
    """
    active_vouchers = []
    now = datetime.now()
    
    for code, voucher_data in PREDEFINED_VOUCHERS.items():
        voucher = Voucher(**voucher_data)
        if voucher.active and voucher.valid_from <= now <= voucher.valid_until:
            active_vouchers.append({
                "code": voucher.code,
                "description": voucher.description,
                "discount_percentage": voucher.discount_percentage,
                "valid_until": voucher.valid_until.isoformat()
            })
    
    return active_vouchers
