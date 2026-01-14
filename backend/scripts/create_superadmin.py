"""
Script automatizado para criar usuário SUPERADMIN
"""

import asyncio
import logging
import os
import uuid
from datetime import datetime, timezone

import bcrypt
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

load_dotenv()

MONGO_URL = os.environ.get('MONGODB_URI') or os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
DB_NAME = os.environ.get('MONGODB_DB') or os.environ.get('DB_NAME', 'test_database')


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


async def create_superadmin():
    """Criar usuário superadmin"""
    
    logger.info("\n" + "="*60)
    logger.info("  🔐 CRIANDO USUÁRIO SUPERADMIN")
    logger.info("="*60 + "\n")
    
    try:
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
        
        await client.admin.command('ping')
        logger.info("✅ Conectado ao MongoDB\n")
    except Exception as e:
        logger.error(f"❌ Erro ao conectar: {e}")
        return
    
    # Dados do superadmin
    superadmin = {
        "email": "superadmin@osprey.com",
        "password": "super123",
        "first_name": "Super",
        "last_name": "Admin",
        "phone": "+5511888888888",
        "role": "superadmin"
    }
    
    # Verificar se já existe
    existing = await db.users.find_one({"email": superadmin["email"]})
    
    if existing:
        logger.warning(f"⚠️  Usuário '{superadmin['email']}' já existe!")
        logger.info(f"   Atualizando role para 'superadmin'...\n")
        
        await db.users.update_one(
            {"email": superadmin["email"]},
            {"$set": {
                "role": "superadmin",
                "updated_at": datetime.now(timezone.utc)
            }}
        )
        
        logger.info("✅ Role atualizado com sucesso!")
    else:
        # Criar novo usuário
        user_id = str(uuid.uuid4())
        hashed_password = hash_password(superadmin["password"])
        
        user_data = {
            "id": user_id,
            "email": superadmin["email"],
            "hashed_password": hashed_password,
            "first_name": superadmin["first_name"],
            "last_name": superadmin["last_name"],
            "phone": superadmin["phone"],
            "role": superadmin["role"],
            "country_of_birth": None,
            "current_country": None,
            "date_of_birth": None,
            "passport_number": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        await db.users.insert_one(user_data)
        logger.info("✅ Usuário superadmin criado com sucesso!")
    
    logger.info("\n" + "="*60)
    logger.info("  📋 CREDENCIAIS DO SUPERADMIN")
    logger.info("="*60)
    logger.info(f"\n   Email:    {superadmin['email']}")
    logger.info(f"   Senha:    {superadmin['password']}")
    logger.info(f"   Role:     SUPERADMIN (acesso total)")
    logger.info("\n🔗 Faça login em: http://localhost:3000/login")
    logger.info("\n💡 Superadmins têm acesso a TODAS funcionalidades administrativas")
    logger.warning("\n⚠️  Este é um usuário de TESTE. Use apenas em desenvolvimento!")
    logger.info("\n")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(create_superadmin())
