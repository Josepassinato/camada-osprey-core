"""
Script automatizado para criar usuário admin de teste
"""

import asyncio
import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import bcrypt
import uuid

load_dotenv()

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
DB_NAME = os.environ.get('DB_NAME', 'test_database')


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


async def create_test_admin():
    """Criar usuário admin de teste automaticamente"""
    
    print("\n" + "="*60)
    print("  🔐 CRIANDO USUÁRIO ADMIN DE TESTE")
    print("="*60 + "\n")
    
    try:
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
        
        await client.admin.command('ping')
        print("✅ Conectado ao MongoDB\n")
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return
    
    # Dados do admin - use env vars para email e senha
    admin_email = os.environ.get('ADMIN_EMAIL', 'admin@osprey.com')
    admin_password = os.environ.get('ADMIN_PASSWORD')
    if not admin_password:
        import secrets
        admin_password = secrets.token_urlsafe(16)
        print(f"⚠️  ADMIN_PASSWORD not set. Generated random password: {admin_password}")

    test_admin = {
        "email": admin_email,
        "password": admin_password,
        "first_name": "Admin",
        "last_name": "Osprey",
        "phone": "+5511999999999",
        "role": "admin"
    }
    
    # Verificar se já existe
    existing = await db.users.find_one({"email": test_admin["email"]})
    
    if existing:
        print(f"⚠️  Usuário '{test_admin['email']}' já existe!")
        print(f"   Atualizando role para 'admin'...\n")
        
        await db.users.update_one(
            {"email": test_admin["email"]},
            {"$set": {
                "role": "admin",
                "updated_at": datetime.utcnow()
            }}
        )
        
        print("✅ Role atualizado com sucesso!")
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
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.users.insert_one(user_data)
        print("✅ Usuário admin criado com sucesso!")
    
    print("\n" + "="*60)
    print("  📋 CREDENCIAIS DO ADMIN DE TESTE")
    print("="*60)
    print(f"\n   Email:    {test_admin['email']}")
    print(f"   Senha:    {test_admin['password']}")
    print(f"   Role:     ADMIN")
    print("\n🔗 Faça login em: http://localhost:3000/login")
    print("\n💡 Depois do login, você pode acessar:")
    print("   - http://localhost:3000/admin/visa-updates")
    print("   - http://localhost:3000/admin/knowledge-base")
    print("\n⚠️  Este é um usuário de TESTE. Use apenas em desenvolvimento!")
    print("\n")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(create_test_admin())
