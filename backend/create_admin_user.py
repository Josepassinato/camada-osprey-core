"""
Script para criar usuário admin no MongoDB
Uso: python create_admin_user.py
"""

import asyncio
import os
import sys
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import bcrypt
import uuid

# Carregar variáveis de ambiente
load_dotenv()

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
DB_NAME = os.environ.get('DB_NAME', 'test_database')


def hash_password(password: str) -> str:
    """Hash de senha usando bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


async def create_admin_user():
    """Criar usuário admin no banco de dados"""
    
    print("\n" + "="*60)
    print("  🔐 CRIAR USUÁRIO ADMIN - OSPREY")
    print("="*60 + "\n")
    
    # Conectar ao MongoDB
    try:
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
        
        # Testar conexão
        await client.admin.command('ping')
        print("✅ Conectado ao MongoDB com sucesso!")
        print(f"   Database: {DB_NAME}\n")
    except Exception as e:
        print(f"❌ Erro ao conectar ao MongoDB: {e}")
        return
    
    # Coletar dados do usuário
    print("Por favor, forneça os dados do usuário admin:\n")
    
    email = input("📧 Email: ").strip()
    if not email:
        print("❌ Email é obrigatório!")
        return
    
    # Verificar se email já existe
    existing_user = await db.users.find_one({"email": email})
    if existing_user:
        print(f"\n⚠️  Usuário com email '{email}' já existe!")
        
        update = input("   Deseja atualizar o role para admin? (s/n): ").strip().lower()
        if update == 's':
            result = await db.users.update_one(
                {"email": email},
                {"$set": {
                    "role": "admin",
                    "updated_at": datetime.utcnow()
                }}
            )
            
            if result.modified_count > 0:
                print(f"\n✅ Usuário '{email}' atualizado para admin com sucesso!")
            else:
                print(f"\n⚠️  Nenhuma alteração foi feita (usuário já era admin).")
        return
    
    password = input("🔑 Senha: ").strip()
    if not password or len(password) < 6:
        print("❌ Senha deve ter pelo menos 6 caracteres!")
        return
    
    first_name = input("👤 Nome: ").strip() or "Admin"
    last_name = input("👤 Sobrenome: ").strip() or "Osprey"
    phone = input("📱 Telefone (opcional): ").strip() or None
    
    # Escolher role
    print("\n🔐 Escolha o nível de acesso:")
    print("   1. admin      - Acesso administrativo padrão")
    print("   2. superadmin - Acesso administrativo total")
    
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
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    try:
        await db.users.insert_one(user_data)
        
        print("\n" + "="*60)
        print("  ✅ USUÁRIO ADMIN CRIADO COM SUCESSO!")
        print("="*60)
        print(f"\n📋 Detalhes do usuário:")
        print(f"   ID:         {user_id}")
        print(f"   Email:      {email}")
        print(f"   Nome:       {first_name} {last_name}")
        print(f"   Telefone:   {phone or 'Não informado'}")
        print(f"   Role:       {role.upper()}")
        print(f"   Criado em:  {user_data['created_at'].strftime('%d/%m/%Y %H:%M:%S')}")
        print("\n💡 Use estas credenciais para fazer login:")
        print(f"   Email:    {email}")
        print(f"   Senha:    ********")
        print("\n🔗 Faça login em: http://localhost:3000/login")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Erro ao criar usuário: {e}")
    
    finally:
        client.close()


async def list_admin_users():
    """Listar todos os usuários admin"""
    
    try:
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
        
        # Buscar admins
        admins = await db.users.find({
            "role": {"$in": ["admin", "superadmin"]}
        }).to_list(length=100)
        
        if not admins:
            print("\n⚠️  Nenhum usuário admin encontrado no banco.")
            return
        
        print("\n" + "="*60)
        print("  👥 USUÁRIOS ADMIN NO SISTEMA")
        print("="*60 + "\n")
        
        for idx, admin in enumerate(admins, 1):
            print(f"{idx}. {admin['email']}")
            print(f"   Nome: {admin.get('first_name', '')} {admin.get('last_name', '')}")
            print(f"   Role: {admin.get('role', 'user').upper()}")
            print(f"   Criado: {admin['created_at'].strftime('%d/%m/%Y')}")
            print()
        
        client.close()
        
    except Exception as e:
        print(f"❌ Erro ao listar admins: {e}")


async def main():
    """Menu principal"""
    
    if len(sys.argv) > 1 and sys.argv[1] == "--list":
        await list_admin_users()
        return
    
    await create_admin_user()


if __name__ == "__main__":
    asyncio.run(main())
