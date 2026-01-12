# 🎁 Vouchers de Gratuidade - Beta Testers

## 📋 Lista de Vouchers (100% de Desconto)

Estes vouchers concedem **gratuidade total** (100% de desconto) para testar o sistema durante a fase BETA.

### Vouchers Disponíveis (10 unidades):

| # | Código Voucher | Status | Usos | Validade |
|---|---------------|--------|------|----------|
| 1 | `BETA-FREE-001` | ✅ Ativo | 0/1 | Até 31/12/2025 |
| 2 | `BETA-FREE-002` | ✅ Ativo | 0/1 | Até 31/12/2025 |
| 3 | `BETA-FREE-003` | ✅ Ativo | 0/1 | Até 31/12/2025 |
| 4 | `BETA-FREE-004` | ✅ Ativo | 0/1 | Até 31/12/2025 |
| 5 | `BETA-FREE-005` | ✅ Ativo | 0/1 | Até 31/12/2025 |
| 6 | `BETA-FREE-006` | ✅ Ativo | 0/1 | Até 31/12/2025 |
| 7 | `BETA-FREE-007` | ✅ Ativo | 0/1 | Até 31/12/2025 |
| 8 | `BETA-FREE-008` | ✅ Ativo | 0/1 | Até 31/12/2025 |
| 9 | `BETA-FREE-009` | ✅ Ativo | 0/1 | Até 31/12/2025 |
| 10 | `BETA-FREE-010` | ✅ Ativo | 0/1 | Até 31/12/2025 |

## 🎯 Características dos Vouchers

- **Desconto:** 100% (Gratuidade Total)
- **Tipo:** Voucher de uso único
- **Validade:** 21/11/2024 a 31/12/2025
- **Usos por voucher:** 1 uso
- **Aplicável a:** Todos os tipos de visto
- **Categorias:** Todas

## 🔧 Como Usar o Voucher

### Método 1: Via API (Backend)

```bash
# Criar Payment Intent com voucher
curl -X POST "https://your-domain.com/api/payment/create-payment-intent" \
  -H "Content-Type: application/json" \
  -d '{
    "visa_code": "H-1B",
    "case_id": "OSP-123",
    "voucher_code": "BETA-FREE-001"
  }'
```

**Resposta esperada (100% desconto):**
```json
{
  "success": true,
  "free": true,
  "message": "🎁 Voucher de gratuidade aplicado! Processo liberado sem custo.",
  "voucher_code": "BETA-FREE-001",
  "original_price": 460.0,
  "final_price": 0.0,
  "discount_percentage": 100.0
}
```

### Método 2: Via URL (Frontend)

Adicionar o voucher como query parameter na URL do checkout:

```
https://your-domain.com/checkout?visa_code=H-1B&case_id=OSP-123&voucher=BETA-FREE-001
```

### Método 3: Validar Voucher Antes

```bash
# Validar voucher antes de usar
curl -X GET "https://your-domain.com/api/vouchers/validate/BETA-FREE-001?visa_code=H-1B"
```

**Resposta:**
```json
{
  "valid": true,
  "discount_percentage": 100.0,
  "message": "Voucher válido e ativo",
  "voucher_code": "BETA-FREE-001"
}
```

## 📊 Verificar Status de Vouchers

### Endpoint de Estatísticas

```bash
curl -X GET "https://your-domain.com/api/vouchers/active"
```

**Resposta:**
```json
{
  "success": true,
  "vouchers": [
    {
      "code": "BETA-FREE-001",
      "discount_percentage": 100.0,
      "description": "🎁 Voucher de Gratuidade BETA - Testador #1",
      "max_uses": 1,
      "current_uses": 0,
      "active": true,
      "valid_until": "2025-12-31T23:59:59"
    },
    ...
  ]
}
```

## 🎁 Comportamento no Checkout

### Quando voucher de 100% é aplicado:

1. **Sem Payment Intent:** Sistema não cria PaymentIntent no Stripe
2. **Marcado como Pago:** Caso é automaticamente marcado como `payment_status: completed`
3. **Transação Registrada:** Salva transação com `amount: 0.0` e `payment_method: voucher_100`
4. **Processo Liberado:** Usuário pode prosseguir sem pagamento

### Registro no Banco de Dados:

```javascript
// Collection: payment_transactions
{
  "transaction_id": "FREE-OSP-123",
  "case_id": "OSP-123",
  "visa_code": "H-1B",
  "amount": 0.0,
  "original_amount": 460.0,
  "discount_percentage": 100.0,
  "voucher_code": "BETA-FREE-001",
  "currency": "usd",
  "status": "completed",
  "payment_method": "voucher_100",
  "created_at": "2024-11-21T10:00:00Z"
}

// Collection: auto_cases
{
  "case_id": "OSP-123",
  "payment_status": "completed",
  "payment_info": {
    "amount": 0.0,
    "original_amount": 460.0,
    "discount": 100.0,
    "voucher_code": "BETA-FREE-001",
    "payment_date": "2024-11-21T10:00:00Z",
    "method": "free_voucher"
  }
}
```

## 📝 Distribuição Sugerida

### Como distribuir os vouchers:

**1. Email Personalizado:**
```
Olá [Nome],

Você foi selecionado como Beta Tester da nossa plataforma!

Seu voucher de gratuidade: BETA-FREE-00X

Este voucher dá acesso GRATUITO a qualquer tipo de visto em nossa plataforma.

Como usar:
1. Acesse: [URL da plataforma]
2. Crie sua conta
3. Selecione o tipo de visto
4. No checkout, o voucher será aplicado automaticamente*

*Ou entre em contato conosco para aplicar manualmente.

Validade: até 31/12/2025
Usos: 1 vez

Seu feedback é essencial! 🎯
```

**2. Planilha de Controle:**

| Nome | Email | Voucher | Data Envio | Usado | Data Uso | Feedback |
|------|-------|---------|------------|-------|----------|----------|
| João Silva | joao@email.com | BETA-FREE-001 | 21/11/2024 | ❌ | - | - |
| Maria Santos | maria@email.com | BETA-FREE-002 | 21/11/2024 | ✅ | 22/11/2024 | Recebido |

## 🔍 Monitoramento

### Query MongoDB para verificar uso:

```javascript
// Contar vouchers usados
db.payment_transactions.countDocuments({
  "payment_method": "voucher_100",
  "voucher_code": {$regex: "BETA-FREE"}
})

// Listar transações com vouchers gratuitos
db.payment_transactions.find({
  "payment_method": "voucher_100"
}).sort({created_at: -1})

// Verificar casos aprovados sem pagamento
db.auto_cases.find({
  "payment_status": "completed",
  "payment_info.method": "free_voucher"
})
```

## ⚙️ Configuração Técnica

### Localização no Código:

**Backend:**
- Vouchers definidos em: `/app/backend/voucher_system.py`
- Endpoint de payment: `/app/backend/server.py` (linha ~8990)
- Validação: Função `validate_voucher()`

**Sistema de Vouchers:**
```python
PREDEFINED_VOUCHERS = {
    "BETA-FREE-001": {
        "code": "BETA-FREE-001",
        "discount_percentage": 100.0,
        "description": "🎁 Voucher de Gratuidade BETA - Testador #1",
        "valid_from": datetime(2024, 11, 21),
        "valid_until": datetime(2025, 12, 31),
        "max_uses": 1,
        "current_uses": 0,
        "active": True,
        "categories": None,
        "visa_codes": None
    },
    ...
}
```

## 🛡️ Segurança

### Proteções Implementadas:

1. **Uso Único:** Cada voucher só pode ser usado 1 vez
2. **Validade:** Expira em 31/12/2025
3. **Rastreamento:** Todos os usos são registrados
4. **Incremento Automático:** Sistema incrementa `current_uses` automaticamente
5. **Validação:** Voucher é validado antes de aplicar desconto

## 📞 Suporte

Para gerenciar vouchers:

**Adicionar novo voucher:**
Editar `/app/backend/voucher_system.py` e adicionar no dicionário `PREDEFINED_VOUCHERS`

**Desativar voucher:**
Mudar `"active": True` para `"active": False`

**Ver uso de voucher:**
```bash
curl -X GET "https://your-domain.com/api/vouchers/active"
```

## 🎉 Resultado Esperado

Quando um beta tester usar o voucher:

✅ Processo completo de aplicação de visto
✅ **SEM cobrança** no Stripe
✅ Todos os documentos gerados
✅ PDF completo para download
✅ Experiência idêntica ao processo pago
✅ Feedback coletado para melhorias

---

## 📊 Dashboard de Uso

Para criar um dashboard simples de uso dos vouchers:

```bash
# Ver todos os vouchers BETA e seus usos
mongo

use test_database

db.payment_transactions.aggregate([
  {
    $match: {
      voucher_code: {$regex: "BETA-FREE"}
    }
  },
  {
    $group: {
      _id: "$voucher_code",
      count: {$sum: 1},
      total_saved: {$sum: "$original_amount"}
    }
  },
  {
    $sort: {_id: 1}
  }
])
```

Isso mostrará quantas vezes cada voucher foi usado e quanto foi economizado.

---

**🚀 Os vouchers estão ATIVOS e prontos para uso!**
