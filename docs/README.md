# 📚 Documentação da API OSPREY

Bem-vindo à documentação completa da API da plataforma OSPREY - sua solução completa para automação de processos de imigração americana.

## 🚀 Links Rápidos

### Documentação Interativa
- **Swagger UI**: [https://api.osprey.com/docs](https://api.osprey.com/docs) - Interface interativa para testar endpoints
- **ReDoc**: [https://api.osprey.com/redoc](https://api.osprey.com/redoc) - Documentação limpa e organizada

### Arquivos de Documentação
- [`openapi.json`](./openapi.json) - Schema OpenAPI completo
- [`API_DOCUMENTATION.md`](./API_DOCUMENTATION.md) - Documentação detalhada em Markdown
- [`OSPREY_API_Postman_Collection.json`](./OSPREY_API_Postman_Collection.json) - Coleção para Postman

## 🛠️ Como Usar Esta Documentação

### 1. Para Desenvolvedores Frontend
Use a **Swagger UI** para explorar endpoints interativamente:
```bash
# Acesse no navegador
https://api.osprey.com/docs

# Ou localmente (desenvolvimento)
http://localhost:8001/docs
```

### 2. Para Integração com Postman
1. Faça download da [`OSPREY_API_Postman_Collection.json`](./OSPREY_API_Postman_Collection.json)
2. Importe no Postman
3. Configure as variáveis de ambiente:
   - `base_url`: URL base da API
   - `jwt_token`: Seu token JWT de autenticação

### 3. Para Documentação Offline
Use o arquivo [`API_DOCUMENTATION.md`](./API_DOCUMENTATION.md) para referência completa offline.

## 🔐 Autenticação

A API OSPREY usa **JWT Bearer tokens** para autenticação.

### Como Obter Token
1. **Registrar**: `POST /api/auth/signup`
2. **Login**: `POST /api/auth/login`
3. **Usar Token**: Inclua no header `Authorization: Bearer <token>`

### Exemplo de Autenticação
```javascript
// JavaScript
const response = await fetch('/api/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'sua_senha'
  })
});

const { access_token } = await response.json();

// Use o token em requests subsequentes
const protectedResponse = await fetch('/api/documents/upload', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json',
  },
  body: formData
});
```

```python
# Python
import requests

# Login
login_response = requests.post('https://api.osprey.com/api/auth/login', json={
    'email': 'user@example.com',
    'password': 'sua_senha'
})

token = login_response.json()['access_token']

# Use token
headers = {'Authorization': f'Bearer {token}'}
response = requests.get('https://api.osprey.com/api/documents', headers=headers)
```

## 📋 Categorias de Endpoints

### 🔑 Authentication
- Registro e login de usuários
- Gerenciamento de tokens JWT

### 📄 Documents  
- Upload de documentos com IA
- Validação automática
- OCR e extração de dados
- Sistema de disclaimer por etapa

### 📋 Forms
- Preenchimento inteligente de formulários USCIS
- Conversão português → inglês
- Validação com Dra. Ana (IA)

### 🤖 AI Agents
- Dra. Ana (Validação de formulários)
- Dr. Paula (Geração de cartas)
- Agentes especializados por funcionalidade

### 📦 Case Management
- Gestão de casos
- Auditoria avançada
- Montagem de pacotes finais

### 📊 Analytics
- Business Intelligence
- Métricas de performance
- Relatórios avançados

### 🔧 Production
- Monitoramento de sistema
- Health checks
- Performance metrics

### ⚙️ Automation
- Workflow automation
- Sistema de retry
- Notificações automáticas

### 📝 Disclaimer
- Aceites de responsabilidade
- Compliance por etapa
- Auditoria de aceites

## 🌍 Ambientes

### Produção
```
Base URL: https://api.osprey.com
Swagger UI: https://api.osprey.com/docs
ReDoc: https://api.osprey.com/redoc
```

### Desenvolvimento
```
Base URL: http://localhost:8001
Swagger UI: http://localhost:8001/docs
ReDoc: http://localhost:8001/redoc
```

## 📊 Rate Limits

| Endpoint Category | Requests/Minuto | Burst Limit |
|------------------|-----------------|-------------|
| Authentication   | 20              | 5           |
| Documents        | 100             | 20          |
| Forms            | 50              | 10          |
| AI Agents        | 30              | 8           |
| Production       | 200             | 50          |
| Outros           | 60              | 15          |

## 🚨 Códigos de Erro Comuns

| Código | Descrição | Solução |
|--------|-----------|---------|
| 400    | Dados inválidos | Verifique os parâmetros enviados |
| 401    | Token inválido/expirado | Faça login novamente |
| 403    | Sem permissão | Verifique suas permissões |
| 429    | Rate limit excedido | Aguarde antes de tentar novamente |
| 500    | Erro interno | Contacte o suporte |

## 🛠️ Gerar Documentação Atualizada

Para desenvolvedores que precisam atualizar a documentação:

```bash
# No diretório /app/docs
python generate_api_docs.py

# Isso gera:
# - openapi.json
# - API_DOCUMENTATION.md  
# - OSPREY_API_Postman_Collection.json
```

## 📞 Suporte

- **Email**: support@osprey.com
- **URL**: https://osprey.com/support/
- **Documentação**: https://docs.osprey.com/

## 📄 Licença

Este projeto está sob licença proprietária. Consulte [https://osprey.com/license/](https://osprey.com/license/) para mais informações.

---

**Última atualização**: 2025-10-09  
**Versão da API**: 2.0.0