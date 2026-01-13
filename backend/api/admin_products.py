import logging

from fastapi import APIRouter, Depends, HTTPException, Request

from admin_products import (
    get_all_products,
    get_product,
    sync_all_products_to_stripe,
    sync_product_to_stripe,
    update_product_price,
)
from admin_security import require_admin
from core.database import db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


@router.get("/admin/products")
async def admin_get_all_products(admin=Depends(require_admin)):
    """Lista todos os produtos/vistos - PROTECTED"""
    try:
        products = await get_all_products(db)
        return {"success": True, "products": products, "total": len(products)}
    except Exception as e:
        logger.error(f"Erro ao listar produtos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/products/{visa_code}")
async def admin_get_product(visa_code: str, admin=Depends(require_admin)):
    """Busca produto específico - PROTECTED"""
    try:
        product = await get_product(db, visa_code)

        if not product:
            raise HTTPException(status_code=404, detail=f"Produto {visa_code} não encontrado")

        return {"success": True, "product": product}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar produto: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/admin/products/{visa_code}/price")
async def admin_update_product_price(
    visa_code: str,
    request: Request,
    admin=Depends(require_admin),
):
    """Atualiza preço de um produto e sincroniza com Stripe - PROTECTED"""
    try:
        body = await request.json()
        new_price = body.get("price")
        sync_stripe = body.get("sync_stripe", True)

        if not new_price:
            raise HTTPException(status_code=400, detail="Campo 'price' é obrigatório")

        if not isinstance(new_price, (int, float)) or new_price <= 0:
            raise HTTPException(status_code=400, detail="Preço deve ser um número maior que zero")

        result = await update_product_price(db, visa_code, float(new_price), sync_stripe)

        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Erro ao atualizar preço"))

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar preço: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/products/{visa_code}/sync-stripe")
async def admin_sync_product_stripe(visa_code: str, admin=Depends(require_admin)):
    """Sincroniza produto com Stripe - PROTECTED"""
    try:
        result = await sync_product_to_stripe(db, visa_code)

        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Erro ao sincronizar"))

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao sincronizar com Stripe: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/products/sync-all-stripe")
async def admin_sync_all_products_stripe(admin=Depends(require_admin)):
    """Sincroniza todos os produtos com Stripe - PROTECTED"""
    try:
        result = await sync_all_products_to_stripe(db)
        return result
    except Exception as e:
        logger.error(f"Erro ao sincronizar todos produtos: {e}")
        raise HTTPException(status_code=500, detail=str(e))
