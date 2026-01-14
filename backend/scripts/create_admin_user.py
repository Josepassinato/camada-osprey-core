"""
Script para criar usuário admin no MongoDB
Uso: python create_admin_user.py
"""

import asyncio
import logging
import os
import sys
import uuid
from datetime import datetime, timezone

import bcrypt
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

MONGO_URL = os.environ.get("MONGODB_URI") or os.environ.get(
    "MONGO_URL", "mongodb://localhost:27017/"
)
DB_NAME = os.environ.get("MONGODB_DB") or os.environ.get("DB_NAME", "test_database")


def hash_password(password: str) -> str:
    """Hash de senha usando bcrypt"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


async def create_admin_user():
    """Criar usuário admin no banco de dados"""

    logger.info("\n" + "=" * 60)
    logger.info("  🔐 CRIAR USUÁRIO ADMIN - OSPREY")
    logger.info("=" * 60 + "\n")

    # Conectar ao MongoDB
    try:
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]

        # Testar conexão
        await client.admin.command("ping")
        logger.info("✅ Conectado ao MongoDB com sucesso!")
        logger.info(f"   Database: {DB_NAME}\n")
    except Exception as e:
        logger.error(f"❌ Erro ao conectar ao MongoDB: {e}")
        return

    # Coletar dados do usuário
    logger.info("Por favor, forneça os dados do usuário admin:\n")

    email = input("📧 Email: ").strip()
    if not email:
        logger.error("❌ Email é obrigatório!")
        return

    # Verificar se email já existe
    existing_user = await db.users.find_one({"email": email})
    if existing_user:
        logger.warning(f"\n⚠️  Usuário com email '{email}' já existe!")

        update = input("   Deseja atualizar o role para admin? (s/n): ").strip().lower()
        if update == "s":
            result = await db.users.update_one(
                {"email": email},
                {"$set": {"role": "admin", "updated_at": datetime.now(timezone.utc)}},
            )

            if result.modified_count > 0:
                logger.info(f"\n✅ Usuário '{email}' atualizado para admin com sucesso!")
            else:
                logger.warning(f"\n⚠️  Nenhuma alteração foi feita (usuário já era admin).")
        return

    password = input("🔑 Senha: ").strip()
    if not password or len(password) < 6:
        logger.error("❌ Senha deve ter pelo menos 6 caracteres!")
        return

    first_name = input("👤 Nome: ").strip() or "Admin"
    last_name = input("👤 Sobrenome: ").strip() or "Osprey"
    phone = input("📱 Telefone (opcional): ").strip() or None

    # Escolher role
    logger.info("\n🔐 Escolha o nível de acesso:")
    logger.info("   1. admin      - Acesso administrativo padrão")
    logger.info("   2. superadmin - Acesso administrativo total")

    role_choice = input("\nEscolha (1 ou 2): ").strip()
    role = "superadmin" if role_choice == "2" else "admin"

    # Criar usuário
    user_id = str(uuid.uuid4())
    hashed_password = hash_password(password)

    user_data = {
        "id": user_id,
        "email": email,
        "hashed_password": hashed_password,
        "first_name": first_name,
        "last_name": last_name,
        "phone": phone,
        "role": role,
        "country_of_birth": None,
        "current_country": None,
        "date_of_birth": None,
        "passport_number": None,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }

    try:
        await db.users.insert_one(user_data)

        logger.info("\n" + "=" * 60)
        logger.info("  ✅ USUÁRIO ADMIN CRIADO COM SUCESSO!")
        logger.info("=" * 60)
        logger.info(f"\n📋 Detalhes do usuário:")
        logger.info(f"   ID:         {user_id}")
        logger.info(f"   Email:      {email}")
        logger.info(f"   Nome:       {first_name} {last_name}")
        logger.info(f"   Telefone:   {phone or 'Não informado'}")
        logger.info(f"   Role:       {role.upper()}")
        logger.info(f"   Criado em:  {user_data['created_at'].strftime('%d/%m/%Y %H:%M:%S')}")
        logger.info("\n💡 Use estas credenciais para fazer login:")
        logger.info(f"   Email:    {email}")
        logger.info(f"   Senha:    ********")
        logger.info("\n🔗 Faça login em: http://localhost:3000/login")
        logger.info("\n")

    except Exception as e:
        logger.error(f"\n❌ Erro ao criar usuário: {e}")

    finally:
        client.close()


async def list_admin_users():
    """Listar todos os usuários admin"""

    try:
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]

        # Buscar admins
        admins = await db.users.find({"role": {"$in": ["admin", "superadmin"]}}).to_list(length=100)

        if not admins:
            logger.warning("\n⚠️  Nenhum usuário admin encontrado no banco.")
            return

        logger.info("\n" + "=" * 60)
        logger.info("  👥 USUÁRIOS ADMIN NO SISTEMA")
        logger.info("=" * 60 + "\n")

        for idx, admin in enumerate(admins, 1):
            logger.info(f"{idx}. {admin['email']}")
            logger.info(f"   Nome: {admin.get('first_name', '')} {admin.get('last_name', '')}")
            logger.info(f"   Role: {admin.get('role', 'user').upper()}")
            logger.info(f"   Criado: {admin['created_at'].strftime('%d/%m/%Y')}")
            logger.info()

        client.close()

    except Exception as e:
        logger.error(f"❌ Erro ao listar admins: {e}")


async def main():
    """Menu principal"""

    if len(sys.argv) > 1 and sys.argv[1] == "--list":
        await list_admin_users()
        return

    await create_admin_user()


if __name__ == "__main__":
    asyncio.run(main())
