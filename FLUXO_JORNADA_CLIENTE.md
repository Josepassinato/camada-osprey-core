# 🛣️ Fluxo Completo da Jornada do Cliente - Osprey

## 📊 Visão Geral do Fluxo

```
┌──────────────────┐
│   1. Homepage    │  👉 Usuário clica "Começar Agora"
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 2. Verificação   │  🔍 Sistema verifica se usuário está logado
│    de Login      │     Se NÃO → vai para Cadastro
└────────┬─────────┘     Se SIM → pula para Seleção
         │
         ▼
┌──────────────────┐
│  3. Cadastro/    │  📝 Usuário cria conta ou faz login
│     Login        │     Salva URL de redirecionamento
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 4. Seleção de    │  🎯 Usuário escolhe tipo de visto
│     Visto        │     (I-539, F-1, I-130, etc.)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  5. Preview do   │  📋 NOVO! Mostra:
│     Visto        │     • Passos da jornada (5 etapas)
│                  │     • Documentos necessários
│                  │     • Tempo de processamento
│                  │     • Taxa USCIS
│                  │     • Avisos importantes
└────────┬─────────┘
         │ Clica "Confirmar e Ir para Pagamento"
         ▼
┌──────────────────┐
│ 6. Página de     │  💳 Mostra resumo do pacote
│    Pagamento     │     Usuário clica "Pagar com Stripe"
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  7. STRIPE       │  💰 Redireciona para checkout Stripe
│    CHECKOUT      │     Processamento seguro do pagamento
│  (Externa)       │     Aceita cartões de crédito
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 8. Confirmação   │  ✅ Verifica pagamento foi aprovado
│   de Pagamento   │     Aguarda confirmação do Stripe
└────────┬─────────┘
         │ Pagamento confirmado
         ▼
┌──────────────────┐
│ 9. Jornada de    │  📝 Usuário preenche formulários:
│    Aplicação     │     • Dados básicos
│    (Formulários) │     • Upload documentos
│                  │     • Revisão IA
│                  │     • Formulário USCIS
└────────┬─────────┘     🔄 Pode salvar progresso
         │
         ▼
┌──────────────────┐
│ 10. Finalização  │  📦 Sistema gera pacote final
│     e Review     │     Revisão completa dos documentos
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 11. Download     │  📥 AVISOS:
│    do Pacote     │     ⚠️ Link expira em 24h
│                  │     🔒 Dados são deletados após download
└──────────────────┘
```

---

## 🔍 Detalhamento de Cada Etapa

### 1️⃣ Homepage (NewHomepage.tsx)
- **Rota:** `/`
- **Ação:** Usuário vê benefícios e clica "Começar Agora"
- **Verificação:** Checa se termos foram aceitos
- **Próximo:** Vai para verificação de login

### 2️⃣ Verificação de Login (NewHomepage.tsx - linha 30)
```typescript
const token = localStorage.getItem('osprey_token');
const user = localStorage.getItem('osprey_user');

if (!token || !user) {
  // Salva onde deve voltar depois do login
  localStorage.setItem('osprey_redirect_after_login', '/auto-application/select-form');
  navigate('/signup');
  return;
}
```
- **Se NÃO logado:** Redireciona para `/signup`
- **Se JÁ logado:** Cria caso e vai para seleção

### 3️⃣ Cadastro/Login
- **Rotas:** `/signup` ou `/login`
- **Ação:** Usuário cria conta ou faz login
- **Após sucesso:** 
  - Salva token no localStorage
  - Busca `osprey_redirect_after_login`
  - Redireciona para URL salva (select-form)

### 4️⃣ Seleção de Visto (SelectForm.tsx)
- **Rota:** `/auto-application/select-form`
- **Vistos disponíveis:**
  - I-539 (Extensão Turista)
  - F-1 (Estudante)
  - I-130 (Petição Familiar)
  - I-765 (Autorização Trabalho)
  - I-90 (Renovação Green Card)
  - EB-2 NIW
  - EB-1A
  - I-589 (Asilo)
- **Ação:** Usuário clica no visto desejado
- **Próximo:** Redireciona para preview (`/auto-application/visa-preview`)

### 5️⃣ Preview do Visto (VisaPreview.tsx) - **NOVO!**
- **Rota:** `/auto-application/visa-preview?visa_code=XXX&case_id=YYY`
- **Informações exibidas:**
  
  📋 **Visão Geral:**
  - Descrição do visto
  - Tempo de processamento (ex: 4-8 meses)
  - Taxa USCIS (ex: $370)
  - Nível de complexidade

  📝 **Passos da Jornada (5 etapas):**
  1. Dados Básicos
  2. Upload de Documentos
  3. Revisão do Sistema
  4. Formulário USCIS
  5. Download Final

  📄 **Documentos Necessários:**
  - Lista completa de documentos
  - Checklist visual com ✓

  ⚠️ **Avisos Importantes:**
  - Acesso vitalício ao formulário
  - Salvamento de progresso
  - Sistema em português
  - Link expira em 24h
  - Dados não são guardados

- **Botões:**
  - ← "Voltar para Seleção"
  - "Confirmar e Ir para Pagamento" →

### 6️⃣ Página de Pagamento (PaymentPage.tsx)
- **Rota:** `/payment?visa_code=XXX&case_id=YYY`
- **Informações exibidas:**
  - Nome do pacote
  - Preço original
  - Desconto (50% OFF lançamento)
  - Preço final
  - O que está incluído
  - Aceita cupons de desconto
- **Ação:** Usuário clica "Pagar com Stripe"
- **Backend:** Chama `/api/payment/create-checkout`
- **Próximo:** Redireciona para Stripe Checkout (externo)

### 7️⃣ Stripe Checkout (Externa)
- **URL:** `checkout.stripe.com/...`
- **Processo:**
  1. Usuário insere dados do cartão
  2. Stripe processa pagamento
  3. Se aprovado → redireciona para `success_url`
  4. Se cancelado → redireciona para `cancel_url`

- **Success URL configurada no backend (linha 8768):**
```python
success_url = f"{frontend_url}/payment/success?session_id={{CHECKOUT_SESSION_ID}}&case_id={case_id}"
```

### 8️⃣ Confirmação de Pagamento (PaymentSuccess.tsx)
- **Rota:** `/payment/success?session_id=XXX&case_id=YYY`
- **Processo:**
  1. Recebe `session_id` do Stripe
  2. Chama backend: `/api/payment/status/{session_id}`
  3. Verifica se pagamento foi aprovado
  4. Mostra tela de sucesso

- **Informações exibidas:**
  - ✅ "Pagamento Confirmado!"
  - Valor pago
  - ID da transação
  - Email do cliente
  - Próximos passos

- **Botão:** "Continuar para o Formulário" (linha 150)
- **Ação:** `navigate(/auto-application/case/${caseId}/basic-data)`

### 9️⃣ Jornada de Aplicação (Formulários)
**Sequência de páginas:**

1. **BasicData.tsx** - `/auto-application/case/{caseId}/basic-data`
   - Dados pessoais
   - Informações de passaporte
   - Botão: **"Salvar Progresso"** ✅ FUNCIONANDO
   - Auto-save: A cada 30 segundos

2. **DocumentUploadAuto.tsx** - `/auto-application/case/{caseId}/documents`
   - Upload de documentos necessários
   - Validação de arquivos

3. **SystemReviewAndTranslation.tsx** - `/auto-application/case/{caseId}/ai-review`
   - Sistema revisa dados
   - Tradução automática

4. **USCISFormFilling.tsx** - `/auto-application/case/{caseId}/uscis-form`
   - Visualização do formulário oficial USCIS
   - Campos preenchidos automaticamente

5. **CoverLetterModule.tsx** - `/auto-application/case/{caseId}/cover-letter`
   - Carta de apresentação (se aplicável)

### 🔟 Finalização e Download (CaseFinalizer.tsx)
- **Rota:** `/auto-application/case/{caseId}/finalize`
- **Processo:**
  1. Sistema gera pacote final
  2. Executa auditoria de qualidade
  3. Cria PDFs finais

- **Downloads disponíveis:**
  - 📄 Pacote Principal (master-packet.pdf)
  - 📋 Instruções (instructions.pdf)
  - ✅ Checklist (checklist.pdf)

- **Avisos importantes:**

  ⏱️ **Expiração:**
  ```
  Após 24 horas o link de download expira.
  Faça o download de todos os documentos agora e 
  guarde-os em um local seguro.
  ```

  🔒 **Privacidade:**
  ```
  Nós não guardamos suas informações. Após o download, 
  todos os seus dados pessoais são automaticamente 
  deletados dos nossos servidores. Após 24 horas, 
  o link de download também expira e todos os arquivos 
  são permanentemente removidos.
  ```

---

## 🔄 Funcionalidade de Salvamento

### Salvar Progresso (BasicData.tsx)

**Onde:** Todos os formulários da jornada

**Como funciona:**
1. **Manual:** Botão "Salvar Progresso"
2. **Automático:** Auto-save a cada 30 segundos
3. **Backend:** Chama `PUT /api/auto-application/case/{caseId}`
4. **Armazenamento:** MongoDB

**Código (linha 196-237):**
```typescript
const saveData = async (autoSave = false) => {
  if (!autoSave) setIsSaving(true);
  
  const response = await fetch(url, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      basic_data: formData,
      status: 'basic_data'
    }),
  });
  
  // Feedback visual: "Salvando..." → "Salvo"
}
```

---

## 🔐 URLs e Endpoints

### Frontend
- Homepage: `/`
- Signup: `/signup`
- Login: `/login`
- Select Form: `/auto-application/select-form`
- **Preview:** `/auto-application/visa-preview` (NOVO)
- Payment: `/payment`
- Success: `/payment/success`
- Basic Data: `/auto-application/case/{caseId}/basic-data`
- Finalize: `/auto-application/case/{caseId}/finalize`

### Backend (API)
- Start: `POST /api/auto-application/start`
- Update Case: `PUT /api/auto-application/case/{caseId}`
- Get Package: `GET /api/packages/{visa_code}`
- **Create Checkout:** `POST /api/payment/create-checkout` (Stripe)
- **Verify Payment:** `GET /api/payment/status/{session_id}` (Stripe)

---

## ✅ Checklist de Verificação

### Fluxo Básico
- [x] Homepage → Cadastro funciona
- [x] Cadastro → Redireciona para select-form
- [x] Select-form → Preview do visto (NOVO)
- [x] Preview → Página de pagamento
- [x] Pagamento → Redireciona para Stripe
- [x] Stripe → Retorna para /payment/success
- [x] Success → Redireciona para aplicação
- [x] Aplicação → Formulários com salvamento
- [x] Finalização → Download com avisos

### Funcionalidades Especiais
- [x] Botão "Salvar Progresso" funciona
- [x] Auto-save a cada 30 segundos
- [x] Preview mostra passos da jornada
- [x] Preview mostra documentos necessários
- [x] Avisos de expiração (24h)
- [x] Avisos de privacidade (dados deletados)

---

## 🎯 Resultado Final

✅ **Fluxo completo implementado**
✅ **Preview de visto adicionado**
✅ **Integração com Stripe funcionando**
✅ **Retorno para aplicação após pagamento**
✅ **Salvamento de progresso ativo**
✅ **Avisos de privacidade presentes**

🎉 **Sistema pronto para uso!**
