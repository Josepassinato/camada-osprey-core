"""
Script automatizado para criar usuário admin de teste
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

MONGO_URL = os.environ.get("MONGODB_URI") or os.environ.get(
    "MONGO_URL", "mongodb://localhost:27017/"
)
DB_NAME = os.environ.get("MONGODB_DB") or os.environ.get("DB_NAME", "test_database")


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


async def create_test_admin():
    """Criar usuário admin de teste automaticamente"""

    logger.info("\n" + "=" * 60)
    logger.info("  🔐 CRIANDO USUÁRIO ADMIN DE TESTE")
    logger.info("=" * 60 + "\n")

    try:
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]

        await client.admin.command("ping")
        logger.info("✅ Conectado ao MongoDB\n")
    except Exception as e:
        logger.error(f"❌ Erro ao conectar: {e}")
        return

    # Dados do admin de teste
    test_admin = {
        "email": "admin@osprey.com",
        "password": "admin123",
        "first_name": "Admin",
        "last_name": "Osprey",
        "phone": "+5511999999999",
        "role": "admin",
    }

    # Verificar se já existe
    existing = await db.users.find_one({"email": test_admin["email"]})

    if existing:
        logger.warning(f"⚠️  Usuário '{test_admin['email']}' já existe!")
        logger.info(f"   Atualizando role para 'admin'...\n")

        await db.users.update_one(
            {"email": test_admin["email"]},
            {"$set": {"role": "admin", "updated_at": datetime.now(timezone.utc)}},
        )

        logger.info("✅ Role atualizado com sucesso!")
    else:
        # Criar novo usuário
        user_id = str(uuid.uuid4())
        hashed_password = hash_password(test_admin["password"])

        user_data = {
            "id": user_id,
            "email": test_admin["email"],
            "hashed_password": hashed_password,
            "first_name": test_admin["first_name"],
            "last_name": test_admin["last_name"],
            "phone": test_admin["phone"],
            "role": test_admin["role"],
            "country_of_birth": None,
            "current_country": None,
            "date_of_birth": None,
            "passport_number": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        await db.users.insert_one(user_data)
        logger.info("✅ Usuário admin criado com sucesso!")

    logger.info("\n" + "=" * 60)
    logger.info("  📋 CREDENCIAIS DO ADMIN DE TESTE")
    logger.info("=" * 60)
    logger.info(f"\n   Email:    {test_admin['email']}")
    logger.info(f"   Senha:    {test_admin['password']}")
    logger.info(f"   Role:     ADMIN")
    logger.info("\n🔗 Faça login em: http://localhost:3000/login")
    logger.info("\n💡 Depois do login, você pode acessar:")
    logger.info("   - http://localhost:3000/admin/visa-updates")
    logger.info("   - http://localhost:3000/admin/knowledge-base")
    logger.warning("\n⚠️  Este é um usuário de TESTE. Use apenas em desenvolvimento!")
    logger.info("\n")

    client.close()


if __name__ == "__main__":
    asyncio.run(create_test_admin())
