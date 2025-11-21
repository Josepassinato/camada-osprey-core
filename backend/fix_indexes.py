"""
Script para remover índices duplicados do MongoDB
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

async def fix_indexes():
    # Conectar ao MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client.test_database
    
    print("🔄 Removendo índices antigos da coleção payment_transactions...")
    
    try:
        # Listar todos os índices
        indexes = await db.payment_transactions.list_indexes().to_list(length=100)
        print(f"📋 Índices existentes: {[idx['name'] for idx in indexes]}")
        
        # Remover o índice problemático (se existir)
        try:
            await db.payment_transactions.drop_index("stripe_session_id_1")
            print("✅ Índice 'stripe_session_id_1' removido com sucesso")
        except Exception as e:
            print(f"⚠️  Índice 'stripe_session_id_1' não encontrado ou já removido: {e}")
        
        # Recriar o índice corretamente (sparse=True)
        await db.payment_transactions.create_index("stripe_session_id", unique=True, sparse=True)
        print("✅ Índice 'stripe_session_id' recriado com sparse=True")
        
        print("✅ Correção de índices concluída!")
        
    except Exception as e:
        print(f"❌ Erro ao corrigir índices: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(fix_indexes())
