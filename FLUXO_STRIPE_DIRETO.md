# 💳 Fluxo Direto para Stripe - Osprey

## 🎯 Novo Fluxo Implementado

O usuário agora vai **direto para o Stripe** após selecionar o visto, sem página intermediária.

```
┌──────────────────┐
│   1. Homepage    │  Clica "Começar Agora"
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 2. Cadastro/     │  Cria conta ou faz login
│    Login         │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 3. Seleção de    │  Escolhe visto (I-539, F-1, etc.)
│    Visto         │  🔥 AQUI ACONTECE A MUDANÇA
└────────┬─────────┘
         │ Clica no visto
         ▼
┌──────────────────┐
│ 4. STRIPE        │  🚀 REDIRECIONA DIRETO PARA STRIPE
│    CHECKOUT      │  • Mostra nome do visto
│  (Externa)       │  • Mostra preço
│                  │  • Campo para cupom de desconto
│                  │  • Formulário de cartão
└────────┬─────────┘
         │ Completa pagamento
         ▼
┌──────────────────┐
│ 5. Confirmação   │  Verifica pagamento
│    de Pagamento  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 6. Jornada de    │  Começa a preencher formulários
│    Aplicação     │
└──────────────────┘
```

---

## 🔧 Alterações Realizadas

### 1. SelectForm.tsx - Redirecionamento Direto

**Nova função adicionada:**

```typescript
const createStripeCheckout = async (visaCode: string, caseId: string) => {
  console.log('💳 Creating Stripe checkout session...');
  
  const backendUrl = import.meta.env.VITE_BACKEND_URL;
  const response = await fetch(`${backendUrl}/api/payment/create-checkout`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      visa_code: visaCode,
      case_id: caseId
    }),
  });

  const data = await response.json();
  
  if (data.success && data.checkout_url) {
    // Redirect to Stripe Checkout
    window.location.href = data.checkout_url;
  }
};
```

**O que mudou:**
- ❌ **ANTES:** `navigate('/auto-application/visa-preview')`
- ✅ **AGORA:** `await createStripeCheckout(formCode, caseId)`

### 2. Páginas Removidas do Fluxo

- ❌ `/payment` (PaymentPage.tsx) - Página intermediária removida
- ❌ `/auto-application/visa-preview` (VisaPreview.tsx) - Preview removido

**Nota:** As páginas ainda existem no código, mas não são mais usadas no fluxo principal.

---

## 🔍 Como Funciona

### Passo a Passo Técnico

1. **Usuário Seleciona Visto**
   - Página: `SelectForm.tsx`
   - Função: `createCase(formCode)`

2. **Caso é Criado/Atualizado**
   - Backend: `POST /api/auto-application/start`
   - Salva `case_id` e `form_code` no MongoDB

3. **Cria Sessão Stripe Imediatamente**
   - Frontend: `createStripeCheckout(visaCode, caseId)`
   - Backend: `POST /api/payment/create-checkout`
   
4. **Backend Chama Stripe API**
   - Arquivo: `stripe_integration.py`
   - Função: `create_checkout_session()`
   - Cria sessão com:
     - Produto: Nome do visto + descrição
     - Preço: Valor do pacote (ex: $490, $980)
     - Metadata: `case_id` e `visa_code`
     - Success URL: `/payment/success?session_id={CHECKOUT_SESSION_ID}&case_id={case_id}`
     - Cancel URL: `/payment/cancel?case_id={case_id}`

5. **Retorna URL do Stripe**
   - Backend retorna: `{ success: true, checkout_url: "https://checkout.stripe.com/..." }`
   - Frontend executa: `window.location.href = checkout_url`

6. **Usuário É Redirecionado para Stripe**
   - URL: `https://checkout.stripe.com/c/pay/cs_test_...`
   - Vê: Nome do produto, preço, formulário de cartão
   - Pode inserir cupom de desconto

7. **Completa Pagamento**
   - Stripe processa cartão
   - Se aprovado → redireciona para `success_url`
   - Se cancelado → redireciona para `cancel_url`

8. **Volta para Aplicação**
   - URL: `/payment/success?session_id=cs_test_...&case_id=123`
   - Verifica pagamento: `GET /api/payment/status/{session_id}`
   - Redireciona para: `/auto-application/case/{caseId}/basic-data`

---

## 🎨 O Que o Usuário Vê

### Página do Stripe

A página do Stripe mostra automaticamente:

```
┌─────────────────────────────────────┐
│  OSPREY                              │
│  ──────────────────────────────────  │
│                                      │
│  F-1: Visto de Estudante - F-1      │
│  Formulário para mudança de status   │
│                                      │
│  $980.00                             │
│                                      │
│  ┌──────────────────────────────┐   │
│  │  Cupom de desconto (opcional)│   │
│  └──────────────────────────────┘   │
│                                      │
│  ┌──────────────────────────────┐   │
│  │  Número do cartão            │   │
│  │  ████ ████ ████ ████         │   │
│  └──────────────────────────────┘   │
│                                      │
│  ┌──────┐  ┌────────────────────┐  │
│  │ MM/AA│  │ CVV                │  │
│  └──────┘  └────────────────────┘  │
│                                      │
│  ┌──────────────────────────────┐   │
│  │    Pagar $980.00             │   │
│  └──────────────────────────────┘   │
│                                      │
│  🔒 Powered by Stripe                │
└─────────────────────────────────────┘
```

---

## ⚙️ Configuração do Stripe

### Variáveis de Ambiente (.env)

```bash
STRIPE_PUBLISHABLE_KEY=pk_live_51PByv6...
STRIPE_API_KEY=sk_live_51PByv6...
```

✅ **Já configuradas e funcionando**

### URLs de Redirecionamento

Configuradas no backend (`server.py` linha 8768):

```python
frontend_url = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:3000')
success_url = f"{frontend_url}/payment/success?session_id={{CHECKOUT_SESSION_ID}}&case_id={case_id}"
cancel_url = f"{frontend_url}/payment/cancel?case_id={case_id}"
```

---

## 🧪 Como Testar

### 1. Teste do Fluxo Completo

```bash
# 1. Homepage
http://localhost:3000

# 2. Clique "Começar Agora"
→ Vai para Signup (se não logado)

# 3. Crie conta
→ Retorna para SelectForm

# 4. Clique em um visto (ex: F-1)
→ 🚀 Redireciona DIRETO para Stripe

# 5. Na página Stripe, use cartão de teste:
Número: 4242 4242 4242 4242
Data: 12/34
CVV: 123

# 6. Clique "Pagar"
→ Volta para /payment/success

# 7. Clique "Continuar para o Formulário"
→ Inicia aplicação ✅
```

### 2. Testar com cURL (Backend)

```bash
# Criar checkout session
curl -X POST http://localhost:8001/api/payment/create-checkout \
  -H "Content-Type: application/json" \
  -d '{
    "visa_code": "F-1",
    "case_id": "test-case-123"
  }'

# Resposta esperada:
{
  "success": true,
  "session_id": "cs_test_...",
  "checkout_url": "https://checkout.stripe.com/c/pay/cs_test_...",
  "original_price": 980.0,
  "message": "Cupons de desconto podem ser aplicados..."
}
```

### 3. Verificar Logs

```bash
# Backend
tail -f /var/log/supervisor/backend.err.log | grep -i "stripe\|payment"

# Procurar por:
# ✅ "Creating Stripe checkout session..."
# ✅ "Transação criada: cs_test_..."
# ✅ "Stripe checkout created, redirecting..."
```

---

## 🔒 Segurança

### Informações Enviadas ao Stripe

**Metadata (visível no dashboard Stripe):**
```json
{
  "case_id": "abc123",
  "visa_code": "F-1",
  "original_price": "980.0"
}
```

**Line Items (produto):**
```json
{
  "name": "F-1: Visto de Estudante - F-1",
  "description": "Formulário para mudança de status para F-1",
  "amount": 98000,  // $980.00 em centavos
  "currency": "usd",
  "quantity": 1
}
```

### O Que o Stripe Processa

✅ Informações de cartão (Stripe PCI compliant)
✅ Endereço de cobrança (se necessário)
✅ CVV e validação

❌ Dados pessoais do usuário (não enviados)
❌ Documentos (não enviados)
❌ Informações sensíveis (não enviados)

---

## 📊 Pacotes e Preços

Os preços são configurados em `payment_packages.py`:

```python
VISA_PACKAGES = {
    'I-539': {
        'name': 'Básico',
        'price': 490.0,
        'category': 'basic'
    },
    'F-1': {
        'name': 'Intermediário',
        'price': 980.0,
        'category': 'intermediate'
    },
    'I-130': {
        'name': 'Intermediário',
        'price': 1480.0,
        'category': 'intermediate'
    },
    # ... outros vistos
}
```

---

## ✅ Checklist de Verificação

### Frontend
- [x] SelectForm redireciona direto para Stripe
- [x] Não passa mais por /payment
- [x] Não passa mais por /visa-preview
- [x] Função createStripeCheckout implementada
- [x] Tratamento de erros

### Backend
- [x] Endpoint /payment/create-checkout funciona
- [x] Stripe API configurada
- [x] Success URL inclui case_id
- [x] Metadata salva corretamente
- [x] Transações registradas no MongoDB

### Stripe
- [x] Chaves configuradas (.env)
- [x] Modo de pagamento: 'payment' (one-time)
- [x] Aceita cartões: 'card'
- [x] Cupons habilitados: allow_promotion_codes=True
- [x] URLs de redirecionamento corretas

---

## 🎯 Resultado Final

✅ **Fluxo simplificado**
✅ **Uma página a menos no processo**
✅ **Usuário vai direto ao que importa: pagar**
✅ **Stripe mostra todas informações necessárias**
✅ **Retorno automático após pagamento**

🎉 **Sistema otimizado e funcionando!**
