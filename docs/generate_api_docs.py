#!/usr/bin/env python3
"""
Script para gerar documentação da API automaticamente
Gera documentação OpenAPI/Swagger e arquivos markdown
"""

import json
import os
import sys
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

def generate_openapi_json():
    """Gera o arquivo OpenAPI JSON da API"""
    try:
        from server import app
        
        # Get OpenAPI schema
        openapi_schema = app.openapi()
        
        # Create docs directory if it doesn't exist
        docs_dir = Path(__file__).parent
        docs_dir.mkdir(exist_ok=True)
        
        # Save OpenAPI JSON
        openapi_file = docs_dir / "openapi.json"
        with open(openapi_file, "w", encoding="utf-8") as f:
            json.dump(openapi_schema, f, indent=2, ensure_ascii=False)
        
        print(f"✅ OpenAPI JSON gerado: {openapi_file}")
        return openapi_schema
        
    except Exception as e:
        print(f"❌ Erro ao gerar OpenAPI JSON: {e}")
        return None

def generate_markdown_docs(openapi_schema):
    """Gera documentação em Markdown baseada no schema OpenAPI"""
    if not openapi_schema:
        return
    
    docs_dir = Path(__file__).parent
    md_file = docs_dir / "API_DOCUMENTATION.md"
    
    try:
        with open(md_file, "w", encoding="utf-8") as f:
            # Header
            f.write(f"# {openapi_schema['info']['title']}\n\n")
            f.write(f"**Versão:** {openapi_schema['info']['version']}\n\n")
            f.write(f"{openapi_schema['info']['description']}\n\n")
            
            # Contact Info
            if 'contact' in openapi_schema['info']:
                contact = openapi_schema['info']['contact']
                f.write("## 📞 Contato\n\n")
                f.write(f"- **Nome:** {contact.get('name', 'N/A')}\n")
                f.write(f"- **Email:** {contact.get('email', 'N/A')}\n")
                f.write(f"- **URL:** {contact.get('url', 'N/A')}\n\n")
            
            # Base URL
            f.write("## 🌐 Base URL\n\n")
            f.write("```\nhttps://api.osprey.com\n```\n\n")
            
            # Tags (Categories)
            if 'tags' in openapi_schema:
                f.write("## 📋 Categorias de Endpoints\n\n")
                for tag in openapi_schema['tags']:
                    f.write(f"### {tag['name']}\n")
                    f.write(f"{tag['description']}\n\n")
            
            # Endpoints by tag
            paths = openapi_schema.get('paths', {})
            endpoints_by_tag = {}
            
            # Group endpoints by tag
            for path, methods in paths.items():
                for method, details in methods.items():
                    if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                        tags = details.get('tags', ['Uncategorized'])
                        for tag in tags:
                            if tag not in endpoints_by_tag:
                                endpoints_by_tag[tag] = []
                            endpoints_by_tag[tag].append({
                                'path': path,
                                'method': method.upper(),
                                'summary': details.get('summary', 'N/A'),
                                'description': details.get('description', 'N/A')
                            })
            
            # Write endpoints by category
            f.write("## 🛠️ Endpoints\n\n")
            for tag, endpoints in endpoints_by_tag.items():
                f.write(f"### {tag}\n\n")
                for endpoint in endpoints:
                    f.write(f"#### `{endpoint['method']} {endpoint['path']}`\n\n")
                    f.write(f"**Resumo:** {endpoint['summary']}\n\n")
                    f.write(f"**Descrição:** {endpoint['description']}\n\n")
                    f.write("---\n\n")
            
            # Security
            f.write("## 🔐 Autenticação\n\n")
            f.write("Esta API utiliza JWT Bearer tokens para autenticação.\n\n")
            f.write("### Como usar:\n\n")
            f.write("```http\nAuthorization: Bearer <seu_jwt_token>\n```\n\n")
            
            # Status Codes
            f.write("## 📊 Códigos de Status\n\n")
            f.write("| Código | Descrição |\n")
            f.write("|--------|----------|\n")
            f.write("| 200 | Sucesso |\n")
            f.write("| 400 | Erro de validação |\n")
            f.write("| 401 | Não autorizado |\n")
            f.write("| 403 | Sem permissão |\n")
            f.write("| 404 | Não encontrado |\n")
            f.write("| 429 | Rate limit excedido |\n")
            f.write("| 500 | Erro interno do servidor |\n\n")
            
        print(f"✅ Documentação Markdown gerada: {md_file}")
        
    except Exception as e:
        print(f"❌ Erro ao gerar documentação Markdown: {e}")

def generate_postman_collection(openapi_schema):
    """Gera coleção do Postman baseada no schema OpenAPI"""
    if not openapi_schema:
        return
    
    docs_dir = Path(__file__).parent
    postman_file = docs_dir / "OSPREY_API_Postman_Collection.json"
    
    try:
        # Basic Postman collection structure
        postman_collection = {
            "info": {
                "name": openapi_schema['info']['title'],
                "description": openapi_schema['info']['description'],
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "auth": {
                "type": "bearer",
                "bearer": [
                    {
                        "key": "token",
                        "value": "{{jwt_token}}",
                        "type": "string"
                    }
                ]
            },
            "variable": [
                {
                    "key": "base_url",
                    "value": "https://api.osprey.com"
                },
                {
                    "key": "jwt_token",
                    "value": "",
                    "type": "string"
                }
            ],
            "item": []
        }
        
        # Convert OpenAPI paths to Postman requests
        paths = openapi_schema.get('paths', {})
        for path, methods in paths.items():
            for method, details in methods.items():
                if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                    request_item = {
                        "name": details.get('summary', f"{method.upper()} {path}"),
                        "request": {
                            "method": method.upper(),
                            "header": [
                                {
                                    "key": "Content-Type",
                                    "value": "application/json"
                                }
                            ],
                            "url": {
                                "raw": "{{base_url}}" + path,
                                "host": ["{{base_url}}"],
                                "path": path.strip('/').split('/')
                            },
                            "description": details.get('description', '')
                        }
                    }
                    
                    # Add body for POST/PUT methods
                    if method.upper() in ['POST', 'PUT', 'PATCH']:
                        request_item["request"]["body"] = {
                            "mode": "raw",
                            "raw": "{\n  \n}",
                            "options": {
                                "raw": {
                                    "language": "json"
                                }
                            }
                        }
                    
                    postman_collection["item"].append(request_item)
        
        # Save Postman collection
        with open(postman_file, "w", encoding="utf-8") as f:
            json.dump(postman_collection, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Coleção Postman gerada: {postman_file}")
        
    except Exception as e:
        print(f"❌ Erro ao gerar coleção Postman: {e}")

def main():
    """Função principal"""
    print("🚀 Gerando documentação da API OSPREY...\n")
    
    # Generate OpenAPI JSON
    openapi_schema = generate_openapi_json()
    
    # Generate Markdown docs
    generate_markdown_docs(openapi_schema)
    
    # Generate Postman collection
    generate_postman_collection(openapi_schema)
    
    print("\n🎉 Documentação gerada com sucesso!")
    print("\nArquivos criados:")
    print("- docs/openapi.json - Schema OpenAPI completo")
    print("- docs/API_DOCUMENTATION.md - Documentação em Markdown")
    print("- docs/OSPREY_API_Postman_Collection.json - Coleção do Postman")
    print("\nPara visualizar a documentação interativa, acesse:")
    print("https://api.osprey.com/docs (Swagger UI)")
    print("https://api.osprey.com/redoc (ReDoc)")

if __name__ == "__main__":
    main()