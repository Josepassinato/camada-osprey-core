#!/usr/bin/env python3
"""
Script para criar cupons de desconto no Stripe
"""

import os
import stripe
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurar Stripe
stripe.api_key = os.environ.get('STRIPE_API_KEY')

def create_coupon(code, percent_off, name):
    """Cria um cupom no Stripe"""
    try:
        # Criar cupom
        coupon = stripe.Coupon.create(
            percent_off=percent_off,
            duration='once',
            name=name,
            id=code  # ID será o código do cupom
        )
        print(f"✅ Cupom criado: {coupon.id}")
        print(f"   Nome: {coupon.name}")
        print(f"   Desconto: {coupon.percent_off}%")
        print(f"   Duração: {coupon.duration}")
        
        # Criar código promocional
        promo_code = stripe.PromotionCode.create(
            coupon=coupon.id,
            code=code
        )
        print(f"✅ Código promocional criado: {promo_code.code}")
        print(f"   Ativo: {promo_code.active}")
        
        return coupon, promo_code
        
    except stripe.error.StripeError as e:
        print(f"❌ Erro do Stripe: {str(e)}")
        return None, None
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return None, None


def list_coupons():
    """Lista todos os cupons existentes"""
    try:
        coupons = stripe.Coupon.list(limit=10)
        print("\n📋 Cupons existentes:")
        for coupon in coupons.data:
            print(f"   - {coupon.id}: {coupon.percent_off}% OFF ({coupon.name})")
        
        promo_codes = stripe.PromotionCode.list(limit=10)
        print("\n🎟️ Códigos promocionais existentes:")
        for promo in promo_codes.data:
            print(f"   - {promo.code}: Cupom {promo.coupon.id} (Ativo: {promo.active})")
            
    except Exception as e:
        print(f"❌ Erro ao listar: {str(e)}")


if __name__ == "__main__":
    print("=" * 50)
    print("CRIAÇÃO DE CUPONS NO STRIPE")
    print("=" * 50)
    
    # Listar cupons existentes
    list_coupons()
    
    print("\n" + "=" * 50)
    print("CRIANDO NOVO CUPOM")
    print("=" * 50)
    
    # Criar cupom LANCAMENTO50
    create_coupon(
        code="LANCAMENTO50",
        percent_off=50,
        name="Bônus de Lançamento - 50% OFF"
    )
    
    print("\n✅ Processo concluído!")
    print("\nAgora os usuários podem usar o código 'LANCAMENTO50' na página de checkout do Stripe.")
