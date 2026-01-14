"""
Script para remover índices duplicados do MongoDB
"""
import asyncio
import logging
import os

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

load_dotenv()

async def fix_indexes():
    # Conectar ao MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client.test_database
    
    logger.info("🔄 Removendo índices antigos da coleção payment_transactions...")
    
    try:
        # Listar todos os índices
        indexes = await db.payment_transactions.list_indexes().to_list(length=100)
        logger.info(f"📋 Índices existentes: {[idx['name'] for idx in indexes]}")
        
        # Remover o índice problemático (se existir)
        try:
            await db.payment_transactions.drop_index("stripe_session_id_1")
            logger.info("✅ Índice 'stripe_session_id_1' removido com sucesso")
        except Exception as e:
            logger.warning(f"⚠️  Índice 'stripe_session_id_1' não encontrado ou já removido: {e}")
        
        # Recriar o índice corretamente (sparse=True)
        await db.payment_transactions.create_index("stripe_session_id", unique=True, sparse=True)
        logger.info("✅ Índice 'stripe_session_id' recriado com sparse=True")
        
        logger.info("✅ Correção de índices concluída!")
        
    except Exception as e:
        logger.error(f"❌ Erro ao corrigir índices: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(fix_indexes())
