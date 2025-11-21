# 🚀 Guia Rápido de Setup - Osprey

## ✅ O que já está funcionando

### 1. Maria - Assistente Virtual
- ✅ Backend API completo
- ✅ Integração com Gemini 2.0 Flash
- ✅ Chat Widget na homepage
- ✅ Histórico de conversas no MongoDB

### 2. Segurança Admin (RBAC)
- ✅ Todos endpoints admin protegidos
- ✅ Rotas frontend protegidas
- ✅ Sistema de roles (user/admin/superadmin)

---

## 🔐 1. USUÁRIOS ADMIN CRIADOS

Dois usuários admin foram criados para teste:

### Admin Padrão
```
Email:    admin@osprey.com
Senha:    admin123
Role:     ADMIN
```

### Super Admin
```
Email:    superadmin@osprey.com
Senha:    super123
Role:     SUPERADMIN (acesso total)
```

### Como Testar:

1. **Fazer Login:**
   ```
   http://localhost:3000/login
   ```

2. **Acessar Painel Admin:**
   ```
   http://localhost:3000/admin/visa-updates
   http://localhost:3000/admin/knowledge-base
   ```

3. **Testar Proteção:**
   - Faça login com usuário normal (sem role admin)
   - Tente acessar `/admin/*`
   - Deve redirecionar para dashboard ✅

---

## 🟢 2. CONFIGURAR WHATSAPP (BAILEYS)

O servidor Baileys foi criado e está pronto para uso!

### Iniciar Servidor Baileys:

```bash
cd /app/baileys-server
npm start
```

**OU use o script automatizado:**

```bash
bash /app/baileys-server/start-baileys.sh
```

### O que vai acontecer:

1. Servidor inicia na porta **3001**
2. Um **QR Code** aparece no terminal
3. Você escaneia com WhatsApp
4. Servidor fica conectado e pronto!

### Escanear QR Code:

1. Abra o **WhatsApp** no celular
2. Vá em: **Configurações > Aparelhos Conectados**
3. Clique em: **Conectar um Aparelho**
4. Escaneie o QR Code do terminal

### Testar Conexão:

```bash
# Verificar status
curl http://localhost:3001/status

# Enviar mensagem de teste
curl -X POST http://localhost:3001/send-message \
  -H "Content-Type: application/json" \
  -d '{"to":"5511999999999","message":"Teste da Maria! 👋"}'
```

### Integração com Backend Python:

O backend já está configurado! Endpoints disponíveis:

```bash
# Enviar boas-vindas para um usuário
POST /api/maria/whatsapp/welcome/{user_id}

# Enviar mensagem manual
POST /api/maria/whatsapp/send
Body: {"phone": "5511999999999", "message": "Olá!"}

# Verificar status
GET /api/maria/whatsapp/status
```

---

## 💬 3. TESTAR CHAT DA MARIA

### Na Interface Web:

1. Acesse: `http://localhost:3000`
2. No canto inferior direito, clique no **botão roxo** (💬)
3. O chat da Maria abrirá!
4. Converse com ela em português 🇧🇷

### Via API (Backend):

```bash
# Chat com Maria
curl -X POST http://localhost:8001/api/maria/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Olá Maria! Me explique sobre visto F-1"}'

# Mensagem de boas-vindas
curl http://localhost:8001/api/maria/welcome

# Status do serviço
curl http://localhost:8001/api/maria/health
```

---

## 📝 4. SCRIPTS ÚTEIS

### Criar Novos Usuários Admin:

```bash
# Interativo (pergunta dados)
cd /app/backend
python3 create_admin_user.py

# Listar admins existentes
python3 create_admin_user.py --list
```

### Verificar Logs:

```bash
# Backend
tail -f /var/log/supervisor/backend.err.log

# Frontend
tail -f /var/log/supervisor/frontend.err.log

# Baileys (se rodando em background)
cd /app/baileys-server
pm2 logs baileys-server
```

---

## 🔧 5. TROUBLESHOOTING

### Maria não responde (Gemini):

✅ **Já resolvido!** Usando Emergent LLM Key que funciona perfeitamente.

### WhatsApp não conecta:

1. Certifique-se de que o servidor Baileys está rodando
2. Verifique se o QR Code está aparecendo
3. Escaneie novamente se necessário
4. Verifique logs: `cd /app/baileys-server && npm start`

### Rotas admin não protegidas:

1. Verifique se fez login com usuário admin
2. Limpe o localStorage: `localStorage.clear()`
3. Faça login novamente

### Backend não inicia:

```bash
# Verificar logs
tail -n 50 /var/log/supervisor/backend.err.log

# Reiniciar
sudo supervisorctl restart backend

# Verificar status
sudo supervisorctl status
```

---

## 📊 6. TESTAR TUDO

### Checklist Completo:

- [ ] Backend rodando (`sudo supervisorctl status backend`)
- [ ] Frontend rodando (`sudo supervisorctl status frontend`)
- [ ] Login com admin funciona (`admin@osprey.com / admin123`)
- [ ] Acesso a `/admin/visa-updates` protegido ✅
- [ ] Chat da Maria aparece na homepage
- [ ] Maria responde no chat
- [ ] Baileys conectado (opcional, para WhatsApp)
- [ ] API da Maria funcionando (`curl /api/maria/health`)

---

## 🎯 PRÓXIMOS PASSOS

### Opcionais (quando necessário):

1. **Configurar Google Cloud TTS/STT** para voz da Maria
   - Obter credenciais do Google Cloud
   - Configurar em `/app/backend/maria_voice.py`

2. **Migrar para WhatsApp Business API Oficial** (produção)
   - Mais estável que Baileys
   - Requer aprovação do Facebook
   - Link: https://business.whatsapp.com/

3. **Adicionar mais usuários admin**
   - Use `create_admin_user.py` interativo
   - Configure roles específicos

---

## 📞 SUPORTE

Se algo não funcionar:

1. Verifique os logs (backend e frontend)
2. Reinicie os serviços: `sudo supervisorctl restart all`
3. Limpe cache do navegador
4. Verifique conectividade com MongoDB

---

## ✅ RESUMO

**Pronto para usar:**
- ✅ Maria (Chat AI) funcionando
- ✅ Admin Panel protegido
- ✅ 2 usuários admin criados
- ✅ Baileys WhatsApp Server configurado

**Para iniciar WhatsApp:**
```bash
cd /app/baileys-server && npm start
```

**Credenciais de Teste:**
```
Admin:      admin@osprey.com / admin123
Superadmin: superadmin@osprey.com / super123
```

🎉 **Tudo pronto! Bom uso!**
