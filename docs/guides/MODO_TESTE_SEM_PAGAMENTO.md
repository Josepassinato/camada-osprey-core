# 🧪 Modo de Teste - Bypass de Pagamento

**Data de Criação:** 26 de Novembro de 2024  
**Status:** ✅ ATIVO  
**Ambiente:** Desenvolvimento/Testes

---

## 🎯 OBJETIVO

Permitir testes completos de todas as jornadas de vistos **sem necessidade de pagamento**, facilitando:
- ✅ Teste de fluxos completos
- ✅ Validação de funcionalidades
- ✅ Demonstrações para clientes
- ✅ Treinamento de equipe
- ✅ QA e debugging

---

## ⚙️ CONFIGURAÇÃO

### **Variável de Ambiente:**

**Arquivo:** `/app/backend/.env`

```env
# Testing Mode - Skip Payment
SKIP_PAYMENT_FOR_TESTING=TRUE
```

### **Valores Possíveis:**
- `TRUE` = **Pagamento desabilitado** (modo teste)
- `FALSE` = **Pagamento obrigatório** (modo produção)

---

## 🔄 COMO FUNCIONA

### **Com SKIP_PAYMENT_FOR_TESTING=TRUE:**

1. **Usuário seleciona visto** (ex: O-1, H-1B, I-539)
2. **Preenche informações** básicas
3. **Chega no checkout** 
4. **Sistema detecta modo teste** 🧪
5. **Bypassa pagamento automaticamente**
6. **Marca caso como "paid"** (payment_status: completed)
7. **Usuário prossegue** com aplicação normalmente
8. **Sem cobrança Stripe** (nenhuma transação real)

### **Transação Registrada:**
```json
{
  "transaction_id": "TEST-{case_id}",
  "case_id": "xxx",
  "visa_code": "O-1",
  "amount": 0.0,
  "original_amount": 1400.0,
  "discount_percentage": 100.0,
  "voucher_code": "TESTING_MODE",
  "status": "completed",
  "payment_method": "testing_mode",
  "created_at": "2024-11-26T..."
}
```

---

## 📝 ENDPOINTS MODIFICADOS

### **1. POST /api/payment/create-payment-intent**
**Usado por:** Checkout com Stripe Elements (EmbeddedCheckout)

**Comportamento em modo teste:**
```javascript
// Request normal
POST /api/payment/create-payment-intent
{
  "visa_code": "O-1",
  "case_id": "123-456"
}

// Response em modo teste
{
  "success": true,
  "free": true,
  "testing_mode": true,
  "message": "🧪 TESTING MODE: Payment skipped",
  "original_price": 1400,
  "final_price": 0.0,
  "discount_percentage": 100.0
}
```

### **2. POST /api/payment/create-checkout**
**Usado por:** Checkout redirect (sessão Stripe antiga)

**Comportamento em modo teste:**
```javascript
// Request normal
POST /api/payment/create-checkout
{
  "visa_code": "H-1B",
  "case_id": "789-012"
}

// Response em modo teste
{
  "success": true,
  "testing_mode": true,
  "message": "🧪 Payment skipped for testing",
  "session_id": "test_session_789-012_1234567890",
  "redirect_url": "/payment/success?session_id=...",
  "skip_checkout": true
}
```

---

## 🎨 EXPERIÊNCIA DO USUÁRIO

### **Fluxo Normal (Produção):**
```
1. Selecionar visto
2. Preencher dados
3. 💳 Ver preço ($1,400)
4. 💳 Inserir cartão Stripe
5. 💳 Processar pagamento
6. ✅ Pagamento aprovado
7. Continuar aplicação
```

### **Fluxo em Modo Teste:**
```
1. Selecionar visto
2. Preencher dados
3. 🧪 Ver mensagem "Testing Mode"
4. 🎁 Pagamento automaticamente aprovado
5. ✅ Prosseguir imediatamente
6. Continuar aplicação
```

---

## 💡 CASOS DE USO

### **1. Testes de Desenvolvimento**
```bash
# Ativar modo teste
SKIP_PAYMENT_FOR_TESTING=TRUE

# Testar cada tipo de visto sem pagar:
- O-1 visa
- H-1B visa
- I-539 change of status
- EB-1A green card
- Etc.
```

### **2. Demonstrações para Clientes**
```bash
# Mostrar sistema completo sem cobrar:
- Flow end-to-end
- Todos os 8 agentes de IA
- Geração de documentos
- QA automático
- Dashboard completo
```

### **3. QA e Testing**
```bash
# Testar funcionalidades rapidamente:
- Diferentes tipos de visto
- Edge cases
- Validações
- Integrações
```

### **4. Treinamento de Equipe**
```bash
# Ensinar uso do sistema:
- Sem custo para treinar
- Sem limite de testes
- Ambiente seguro
```

---

## 🔍 IDENTIFICAÇÃO

### **Como saber se modo teste está ativo:**

**1. Logs do Backend:**
```
🧪 TESTING MODE: Skipping payment for O-1 - 123-456
```

**2. Response da API:**
```json
{
  "testing_mode": true,
  "message": "🧪 TESTING MODE: Payment skipped"
}
```

**3. MongoDB (payment_transactions):**
```json
{
  "transaction_id": "TEST-...",
  "payment_method": "testing_mode",
  "voucher_code": "TESTING_MODE"
}
```

**4. Dashboard Admin:**
- Transações mostram "TESTING_MODE" como voucher
- Amount sempre $0.00
- Payment method: "testing_mode"

---

## ⚠️ IMPORTANTE

### **Segurança:**

❌ **NUNCA deixar ativo em produção!**

```env
# ❌ ERRADO - Em produção
SKIP_PAYMENT_FOR_TESTING=TRUE

# ✅ CORRETO - Em produção
SKIP_PAYMENT_FOR_TESTING=FALSE
```

### **Quando Desativar:**
- Antes de fazer deploy para produção
- Ao testar integrações Stripe reais
- Para verificar fluxo de pagamento completo
- Em ambiente staging antes de produção

### **Quando Manter Ativo:**
- Ambiente de desenvolvimento local
- Testes de features novas
- Demonstrações internas
- QA de funcionalidades não relacionadas a pagamento

---

## 🔄 COMO ATIVAR/DESATIVAR

### **Ativar Modo Teste:**
```bash
# 1. Editar .env
nano /app/backend/.env

# 2. Adicionar/modificar
SKIP_PAYMENT_FOR_TESTING=TRUE

# 3. Reiniciar backend
sudo supervisorctl restart backend

# 4. Verificar logs
tail -f /var/log/supervisor/backend.out.log | grep "TESTING"
```

### **Desativar Modo Teste (Produção):**
```bash
# 1. Editar .env
nano /app/backend/.env

# 2. Modificar para FALSE
SKIP_PAYMENT_FOR_TESTING=FALSE

# 3. Reiniciar backend
sudo supervisorctl restart backend

# 4. Testar pagamento real funciona
curl -X POST http://localhost:8001/api/payment/create-payment-intent \
  -H "Content-Type: application/json" \
  -d '{"visa_code":"O-1","case_id":"test"}'
```

---

## 📊 DIFERENÇAS: Teste vs Produção

| Aspecto | Modo Teste | Produção |
|---------|------------|----------|
| **Pagamento** | Bypassado | Obrigatório |
| **Stripe API** | Não chamada | Chamada |
| **Cobrança** | $0.00 | Preço real |
| **Transação** | "testing_mode" | Stripe real |
| **Voucher** | "TESTING_MODE" | Códigos reais |
| **Payment Intent** | Não criado | Criado via Stripe |
| **Checkout** | Pulado | Stripe Elements |

---

## 🧪 TESTANDO O MODO TESTE

### **Verificar se está ativo:**

**1. Via API:**
```bash
# Criar payment intent de teste
curl -X POST http://localhost:8001/api/payment/create-payment-intent \
  -H "Content-Type: application/json" \
  -d '{
    "visa_code": "O-1",
    "case_id": "test-123"
  }'

# Se modo teste ativo, resposta terá:
# "testing_mode": true
# "free": true
```

**2. Via UI:**
```
1. Acesse o site
2. Selecione qualquer visto
3. Preencha dados básicos
4. Vá para checkout
5. Se modo teste: bypass automático
6. Se produção: pedirá cartão
```

**3. Via Logs:**
```bash
# Acompanhar em tempo real
tail -f /var/log/supervisor/backend.out.log | grep -i "testing\|payment"

# Deve aparecer:
# 🧪 TESTING MODE: Skipping payment for ...
```

---

## 📋 CHECKLIST DE TESTES

### **Com Modo Teste Ativo:**

- [ ] Aplicação O-1 completa sem pagar
- [ ] Aplicação H-1B completa sem pagar
- [ ] Aplicação I-539 completa sem pagar
- [ ] Aplicação EB-1A completa sem pagar
- [ ] Todos os 8 agentes funcionando
- [ ] Documentos sendo gerados
- [ ] QA automático rodando
- [ ] Dashboard acessível
- [ ] Nenhuma cobrança Stripe
- [ ] Transações marcadas como "testing_mode"

### **Antes de Produção:**

- [ ] SKIP_PAYMENT_FOR_TESTING=FALSE
- [ ] Testar pagamento real com cartão teste Stripe
- [ ] Verificar Stripe dashboard recebe transações
- [ ] Confirmar vouchers reais funcionam
- [ ] Webhook Stripe configurado
- [ ] Payment status atualiza corretamente

---

## 🎯 EXEMPLOS DE USO

### **Exemplo 1: Testar O-1 Visa**
```javascript
// Frontend faz request normal
const response = await makeApiCall('/payment/create-payment-intent', 'POST', {
  visa_code: 'O-1',
  case_id: user_case_id
});

// Em modo teste, recebe:
{
  testing_mode: true,
  free: true,
  message: "🧪 TESTING MODE: Payment skipped",
  final_price: 0.0
}

// Frontend pode prosseguir direto sem Stripe
navigate('/dashboard');
```

### **Exemplo 2: Demonstração para Cliente**
```bash
# 1. Ativar modo teste
SKIP_PAYMENT_FOR_TESTING=TRUE

# 2. Mostrar flow completo
- Cliente vê todo o sistema
- Todos os recursos disponíveis
- Nenhuma cobrança real

# 3. Após demo, desativar
SKIP_PAYMENT_FOR_TESTING=FALSE
```

---

## 💰 IMPACTO FINANCEIRO

### **Em Modo Teste:**
- ✅ Zero cobranças Stripe
- ✅ Zero transaction fees
- ✅ Zero processamento de cartão
- ✅ Unlimited testes gratuitos

### **Economia em Testes:**
```
Sem modo teste:
- $1,400 × 10 testes O-1 = $14,000
- Stripe fees (2.9% + $0.30) × 10 = ~$410
- Total: $14,410 em custos de teste

Com modo teste:
- $0 × unlimited testes = $0
- Total: $0 (economia 100%)
```

---

## 🔐 SEGURANÇA

### **Proteções Implementadas:**

1. **Variável de Ambiente**
   - Não hardcoded no código
   - Fácil de controlar por ambiente

2. **Logs Claros**
   - 🧪 emoji identifica modo teste
   - Fácil de auditar

3. **Marcação no DB**
   - Transações claramente marcadas
   - "testing_mode" identificável

4. **Sem Stripe API**
   - Nenhuma chamada real em teste
   - Zero risco de cobrança acidental

---

## 🎊 RESUMO

✅ **Modo teste ativo:** SKIP_PAYMENT_FOR_TESTING=TRUE  
✅ **Pagamentos:** Bypassados automaticamente  
✅ **Cobranças:** $0.00 (zero)  
✅ **Funcionalidades:** 100% disponíveis  
✅ **Testes:** Ilimitados  
✅ **Reversível:** Mudança de 1 linha no .env  

**Agora você pode testar TODAS as jornadas de visto sem custo!** 🚀

---

**Status Atual:** 🟢 ATIVO  
**Ambiente:** Desenvolvimento  
**Pronto para testes:** ✅ SIM
