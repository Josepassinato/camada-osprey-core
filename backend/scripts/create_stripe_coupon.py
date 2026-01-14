#!/usr/bin/env python3
"""
Script para criar cupons de desconto no Stripe
"""

import logging
import os

import stripe
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

# Configurar Stripe
stripe.api_key = os.environ.get("STRIPE_API_KEY")


def create_coupon(code, percent_off, name):
    """Cria um cupom no Stripe"""
    try:
        # Criar cupom
        coupon = stripe.Coupon.create(
            percent_off=percent_off,
            duration="once",
            name=name,
            id=code,  # ID será o código do cupom
        )
        logger.info(f"✅ Cupom criado: {coupon.id}")
        logger.info(f"   Nome: {coupon.name}")
        logger.info(f"   Desconto: {coupon.percent_off}%")
        logger.info(f"   Duração: {coupon.duration}")

        # Criar código promocional
        promo_code = stripe.PromotionCode.create(coupon=coupon.id, code=code)
        logger.info(f"✅ Código promocional criado: {promo_code.code}")
        logger.info(f"   Ativo: {promo_code.active}")

        return coupon, promo_code

    except stripe.error.StripeError as e:
        logger.error(f"❌ Erro do Stripe: {str(e)}")
        return None, None
    except Exception as e:
        logger.error(f"❌ Erro: {str(e)}")
        return None, None


def list_coupons():
    """Lista todos os cupons existentes"""
    try:
        coupons = stripe.Coupon.list(limit=10)
        logger.info("\n📋 Cupons existentes:")
        for coupon in coupons.data:
            logger.info(f"   - {coupon.id}: {coupon.percent_off}% OFF ({coupon.name})")

        promo_codes = stripe.PromotionCode.list(limit=10)
        logger.info("\n🎟️ Códigos promocionais existentes:")
        for promo in promo_codes.data:
            logger.info(f"   - {promo.code}: Cupom {promo.coupon.id} (Ativo: {promo.active})")

    except Exception as e:
        logger.error(f"❌ Erro ao listar: {str(e)}")


if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("CRIAÇÃO DE CUPONS NO STRIPE")
    logger.info("=" * 50)

    # Listar cupons existentes
    list_coupons()

    logger.info("\n" + "=" * 50)
    logger.info("CRIANDO NOVO CUPOM")
    logger.info("=" * 50)

    # Criar cupom LANCAMENTO50
    create_coupon(code="LANCAMENTO50", percent_off=50, name="Bônus de Lançamento - 50% OFF")

    logger.info("\n✅ Processo concluído!")
    logger.info(
        "\nAgora os usuários podem usar o código 'LANCAMENTO50' na página de checkout do Stripe."
    )
