# 🧪 Email Bypass para Testes

## Visão Geral

Sistema de bypass de email para facilitar testes durante o desenvolvimento, similar ao `TEST_MODE` para pagamentos.

## Configuração

### Variáveis de Ambiente (`.env`)

```env
# Testing Mode - Email Bypass
EMAIL_BYPASS_FOR_TESTING=TRUE
TEST_EMAIL_DOMAIN=test.com
```

- **EMAIL_BYPASS_FOR_TESTING**: `TRUE` para ativar, `FALSE` para desativar
- **TEST_EMAIL_DOMAIN**: Domínio dos emails de teste (padrão: `test.com`)

## Como Usar

### 1. Criar Conta de Teste

Use emails com o domínio configurado:

```
usuario1@test.local
maria@test.local
joao.teste@test.local
```

**Exemplo de Request:**
```json
POST /api/auth/signup
{
  "email": "usuario1@test.local",
  "password": "qualquer123",
  "first_name": "Usuario",
  "last_name": "Teste",
  "phone": "+5511999999999"
}
```

**Response (Test Mode):**
```json
{
  "message": "🧪 TEST MODE: User created (email verification bypassed)",
  "test_mode": true,
  "token": "eyJ...",
  "user": {
    "id": "...",
    "email": "usuario1@test.local",
    "first_name": "Usuario",
    "last_name": "Teste"
  }
}
```

### 2. Login com Conta de Teste

**Qualquer senha funciona** para emails de teste quando `EMAIL_BYPASS_FOR_TESTING=TRUE`:

```json
POST /api/auth/login
{
  "email": "usuario1@test.local",
  "password": "qualquer-senha-funciona"
}
```

**Response (Test Mode):**
```json
{
  "message": "🧪 TEST MODE: Login successful (password verification bypassed)",
  "test_mode": true,
  "token": "eyJ...",
  "user": {
    "id": "...",
    "email": "usuario1@test.local",
    "first_name": "Usuario",
    "last_name": "Teste"
  }
}
```

## Funcionalidades

### ✅ Signup com Email Bypass
- ✅ Não valida formato real de email
- ✅ Auto-verifica email (`email_verified: true`)
- ✅ Marca usuário como teste (`is_test_user: true`)
- ✅ Retorna indicador `test_mode: true`

### ✅ Login com Password Bypass
- ✅ Aceita qualquer senha para emails de teste
- ✅ Não verifica hash de senha
- ✅ Retorna indicador `test_mode: true`

### ✅ Owl Agent Support
- ✅ `/owl-agent/auth/register` com email bypass
- ✅ `/owl-agent/auth/login` com password bypass
- ✅ Mesmo comportamento que auth principal

## Segurança

### Produção
- Em produção, defina `EMAIL_BYPASS_FOR_TESTING=FALSE`
- Sistema volta ao comportamento normal
- Validações de email e senha completas

### Identificação de Usuários de Teste
Usuários criados com email bypass têm:
- `email_verified: true` (auto-verificado)
- `is_test_user: true` (marcador)
- Podem ser facilmente filtrados/removidos

## Logs

O sistema registra quando bypass está ativo:

```
🧪 TEST MODE: Email bypass active for usuario1@test.local
🧪 TEST MODE: Login bypass active for usuario1@test.local
```

## Exemplos de Teste

### Teste Rápido - Criar e Logar

```bash
# 1. Criar conta
curl -X POST http://localhost:8001/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@test.local",
    "password": "123456",
    "first_name": "Teste",
    "last_name": "Usuario"
  }'

# 2. Login (qualquer senha)
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@test.local",
    "password": "outra-senha"
  }'
```

### Teste com Owl Agent

```bash
# Registrar no Owl Agent
curl -X POST http://localhost:8001/api/owl-agent/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "owl@test.local",
    "password": "123456",
    "name": "Owl Test User"
  }'

# Login no Owl Agent (qualquer senha)
curl -X POST http://localhost:8001/api/owl-agent/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "owl@test.local",
    "password": "senha-diferente"
  }'
```

## Fluxo Completo de Teste

### 1. Ativar Modo de Teste
```env
EMAIL_BYPASS_FOR_TESTING=TRUE
SKIP_PAYMENT_FOR_TESTING=TRUE
```

### 2. Criar Usuário de Teste
- Email: `usuario@test.local`
- Senha: qualquer (ex: "123456")

### 3. Testar Fluxo Completo
1. ✅ Signup → automático
2. ✅ Login → qualquer senha
3. ✅ Pagamento → bypassed
4. ✅ Aplicação → fluxo normal

## Domínios de Teste Sugeridos

Use estes domínios para diferentes tipos de teste:

```
usuario1@test.local
maria.silva@test.local
joao.teste@test.local
admin@test.local
owl.user@test.local
visa.applicant@test.local
```

## Desativar Email Bypass

Para voltar ao modo produção:

```env
EMAIL_BYPASS_FOR_TESTING=FALSE
```

Ou simplesmente remova/comente a linha.

## Compatibilidade

✅ Auth principal (`/auth/signup`, `/auth/login`)  
✅ Owl Agent (`/owl-agent/auth/*`)  
✅ MongoDB markers (`is_test_user`, `email_verified`)  
✅ JWT tokens normais  
✅ Todos os endpoints funcionam normalmente

---

**Criado**: 2024-12-04  
**Status**: ✅ Ativo e Funcional
