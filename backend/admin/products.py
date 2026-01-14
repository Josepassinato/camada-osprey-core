"""
Admin - Gerenciamento de Produtos e Preços
Sistema para atualizar preços e sincronizar com Stripe
"""

import os
import stripe
import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone
from backend.packages.payment_packages import VISA_PACKAGES

logger = logging.getLogger(__name__)

# Configurar Stripe
stripe.api_key = os.environ.get('STRIPE_API_KEY')


async def initialize_products_in_db(db):
    """
    Inicializa produtos no MongoDB com base no payment_packages.py
    Apenas se não existirem ainda
    """
    try:
        # Verificar se já existem produtos
        count = await db.products.count_documents({})
        
        if count > 0:
            logger.info(f"✅ Produtos já inicializados: {count} produtos no banco")
            return
        
        logger.info("🔄 Inicializando produtos no MongoDB...")
        
        # Inserir todos os produtos do VISA_PACKAGES
        products_to_insert = []
        for visa_code, package in VISA_PACKAGES.items():
            product = {
                "visa_code": visa_code,
                "name": package["name"],
                "price": package["price"],
                "category": package["category"],
                "category_name": package["category_name"],
                "description": package["description"],
                "includes": package["includes"],
                "stripe_product_id": None,  # Será preenchido na sincronização
                "stripe_price_id": None,    # Será preenchido na sincronização
                "active": True,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            products_to_insert.append(product)
        
        if products_to_insert:
            await db.products.insert_many(products_to_insert)
            logger.info(f"✅ {len(products_to_insert)} produtos inicializados no MongoDB")
        
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar produtos: {e}")


async def get_all_products(db) -> List[Dict]:
    """
    Retorna todos os produtos do banco de dados
    """
    try:
        products = await db.products.find({}).sort("category", 1).to_list(length=100)
        
        # Converter ObjectId para string
        for product in products:
            if '_id' in product:
                product['_id'] = str(product['_id'])
        
        return products
    except Exception as e:
        logger.error(f"Erro ao buscar produtos: {e}")
        return []


async def get_product(db, visa_code: str) -> Optional[Dict]:
    """
    Retorna um produto específico
    """
    try:
        product = await db.products.find_one({"visa_code": visa_code})
        
        if product and '_id' in product:
            product['_id'] = str(product['_id'])
        
        return product
    except Exception as e:
        logger.error(f"Erro ao buscar produto {visa_code}: {e}")
        return None


async def update_product_price(db, visa_code: str, new_price: float, sync_stripe: bool = True) -> Dict:
    """
    Atualiza o preço de um produto no banco e opcionalmente no Stripe
    
    Args:
        db: Conexão com MongoDB
        visa_code: Código do visto
        new_price: Novo preço em dólares
        sync_stripe: Se True, sincroniza com Stripe
    
    Returns:
        Dict com resultado da operação
    """
    try:
        # Validar preço
        if new_price <= 0:
            return {
                "success": False,
                "error": "Preço deve ser maior que zero"
            }
        
        # Buscar produto
        product = await db.products.find_one({"visa_code": visa_code})
        
        if not product:
            return {
                "success": False,
                "error": f"Produto {visa_code} não encontrado"
            }
        
        old_price = product.get("price", 0)
        
        # Atualizar no banco
        result = await db.products.update_one(
            {"visa_code": visa_code},
            {
                "$set": {
                    "price": new_price,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        if result.modified_count == 0:
            return {
                "success": False,
                "error": "Nenhuma alteração realizada"
            }
        
        logger.info(f"✅ Preço do {visa_code} atualizado: ${old_price} → ${new_price}")
        
        # Sincronizar com Stripe se solicitado
        stripe_sync_result = None
        if sync_stripe:
            stripe_sync_result = await sync_product_to_stripe(db, visa_code)
        
        return {
            "success": True,
            "visa_code": visa_code,
            "old_price": old_price,
            "new_price": new_price,
            "stripe_synced": sync_stripe,
            "stripe_result": stripe_sync_result
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao atualizar preço: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def sync_product_to_stripe(db, visa_code: str) -> Dict:
    """
    Sincroniza produto com Stripe (cria ou atualiza)
    
    Cria um novo Price no Stripe sempre que o preço muda
    (Stripe não permite atualizar preços existentes)
    """
    try:
        # Buscar produto
        product = await db.products.find_one({"visa_code": visa_code})
        
        if not product:
            return {
                "success": False,
                "error": f"Produto {visa_code} não encontrado"
            }
        
        # 1. Criar ou buscar Produto no Stripe
        stripe_product_id = product.get("stripe_product_id")
        
        if not stripe_product_id:
            # Criar novo produto no Stripe
            stripe_product = stripe.Product.create(
                name=f"{product['name']} - {visa_code}",
                description=product['description'],
                metadata={
                    "visa_code": visa_code,
                    "category": product['category']
                }
            )
            stripe_product_id = stripe_product.id
            
            logger.info(f"✅ Produto criado no Stripe: {stripe_product_id}")
        else:
            # Atualizar produto existente
            stripe.Product.modify(
                stripe_product_id,
                name=f"{product['name']} - {visa_code}",
                description=product['description']
            )
            logger.info(f"✅ Produto atualizado no Stripe: {stripe_product_id}")
        
        # 2. Criar novo Price no Stripe
        # (Stripe não permite atualizar prices, então criamos um novo)
        stripe_price = stripe.Price.create(
            product=stripe_product_id,
            unit_amount=int(product['price'] * 100),  # Converter para centavos
            currency='usd',
            metadata={
                "visa_code": visa_code,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        )
        
        logger.info(f"✅ Price criado no Stripe: {stripe_price.id} - ${product['price']}")
        
        # 3. Arquivar price antigo se existir
        old_price_id = product.get("stripe_price_id")
        if old_price_id and old_price_id != stripe_price.id:
            try:
                stripe.Price.modify(old_price_id, active=False)
                logger.info(f"📦 Price antigo arquivado: {old_price_id}")
            except:
                pass
        
        # 4. Atualizar no MongoDB
        await db.products.update_one(
            {"visa_code": visa_code},
            {
                "$set": {
                    "stripe_product_id": stripe_product_id,
                    "stripe_price_id": stripe_price.id,
                    "stripe_synced_at": datetime.now(timezone.utc)
                }
            }
        )
        
        return {
            "success": True,
            "stripe_product_id": stripe_product_id,
            "stripe_price_id": stripe_price.id,
            "price": product['price']
        }
        
    except stripe.error.StripeError as e:
        logger.error(f"❌ Erro Stripe: {e}")
        return {
            "success": False,
            "error": f"Erro Stripe: {str(e)}"
        }
    except Exception as e:
        logger.error(f"❌ Erro ao sincronizar com Stripe: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def sync_all_products_to_stripe(db) -> Dict:
    """
    Sincroniza todos os produtos com o Stripe
    Útil para inicialização ou migração
    """
    try:
        products = await get_all_products(db)
        
        results = []
        success_count = 0
        error_count = 0
        
        for product in products:
            visa_code = product['visa_code']
            result = await sync_product_to_stripe(db, visa_code)
            
            results.append({
                "visa_code": visa_code,
                "result": result
            })
            
            if result.get("success"):
                success_count += 1
            else:
                error_count += 1
        
        return {
            "success": True,
            "total": len(products),
            "synced": success_count,
            "errors": error_count,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao sincronizar todos produtos: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def get_product_for_checkout(db, visa_code: str) -> Optional[Dict]:
    """
    Retorna informações do produto para criar checkout do Stripe
    Usa o stripe_price_id do banco se disponível
    """
    try:
        product = await db.products.find_one({"visa_code": visa_code})
        
        if not product:
            return None
        
        return {
            "name": product['name'],
            "price": product['price'],
            "description": product['description'],
            "stripe_price_id": product.get('stripe_price_id'),
            "includes": product['includes']
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar produto para checkout: {e}")
        return None
