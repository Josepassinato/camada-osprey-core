"""
Script automatizado para criar usuário SUPERADMIN
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


async def create_superadmin():
    """Criar usuário superadmin"""
    
    print("\n" + "="*60)
    print("  🔐 CRIANDO USUÁRIO SUPERADMIN")
    print("="*60 + "\n")
    
    try:
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
        
        await client.admin.command('ping')
        print("✅ Conectado ao MongoDB\n")
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
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
        print(f"⚠️  Usuário '{superadmin['email']}' já existe!")
        print(f"   Atualizando role para 'superadmin'...\n")
        
        await db.users.update_one(
            {"email": superadmin["email"]},
            {"$set": {
                "role": "superadmin",
                "updated_at": datetime.utcnow()
            }}
        )
        
        print("✅ Role atualizado com sucesso!")
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
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.users.insert_one(user_data)
        print("✅ Usuário superadmin criado com sucesso!")
    
    print("\n" + "="*60)
    print("  📋 CREDENCIAIS DO SUPERADMIN")
    print("="*60)
    print(f"\n   Email:    {superadmin['email']}")
    print(f"   Senha:    {superadmin['password']}")
    print(f"   Role:     SUPERADMIN (acesso total)")
    print("\n🔗 Faça login em: http://localhost:3000/login")
    print("\n💡 Superadmins têm acesso a TODAS funcionalidades administrativas")
    print("\n⚠️  Este é um usuário de TESTE. Use apenas em desenvolvimento!")
    print("\n")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(create_superadmin())
