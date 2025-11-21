# ⚡ Comandos Rápidos - Osprey

## 🚀 Serviços

```bash
# Ver status de todos os serviços
sudo supervisorctl status

# Reiniciar tudo
sudo supervisorctl restart all

# Reiniciar apenas backend
sudo supervisorctl restart backend

# Reiniciar apenas frontend
sudo supervisorctl restart frontend

# Ver logs backend
tail -f /var/log/supervisor/backend.err.log

# Ver logs frontend
tail -f /var/log/supervisor/frontend.err.log
```

---

## 🟢 WhatsApp (Baileys)

```bash
# Iniciar servidor Baileys
cd /app/baileys-server
npm start

# OU usar script automatizado
bash /app/baileys-server/start-baileys.sh

# Verificar status
curl http://localhost:3001/status

# Testar envio de mensagem
curl -X POST http://localhost:3001/send-message \
  -H "Content-Type: application/json" \
  -d '{"to":"5511999999999","message":"Teste!"}'
```

---

## 💬 Maria - Assistente Virtual

```bash
# Testar chat
curl -X POST http://localhost:8001/api/maria/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Olá Maria!"}'

# Mensagem de boas-vindas
curl http://localhost:8001/api/maria/welcome

# Health check
curl http://localhost:8001/api/maria/health

# Status WhatsApp
curl http://localhost:8001/api/maria/whatsapp/status
```

---

## 🔐 Usuários Admin

```bash
# Criar admin interativo
cd /app/backend
python3 create_admin_user.py

# Criar admin de teste (automático)
python3 create_test_admin.py

# Criar superadmin (automático)
python3 create_superadmin.py

# Listar todos os admins
python3 create_admin_user.py --list
```

### Credenciais de Teste:

```
Admin:      admin@osprey.com / admin123
Superadmin: superadmin@osprey.com / super123
```

---

## 🧪 Testar Segurança Admin

```bash
# 1. Fazer login (vai retornar token)
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@osprey.com","password":"admin123"}'

# 2. Salvar o token retornado
export TOKEN="seu-token-aqui"

# 3. Testar endpoint protegido
curl -X GET http://localhost:8001/api/admin/visa-updates/pending \
  -H "Authorization: Bearer $TOKEN"

# 4. Testar sem token (deve dar erro 403)
curl -X GET http://localhost:8001/api/admin/visa-updates/pending
```

---

## 📦 MongoDB

```bash
# Conectar ao MongoDB
mongosh mongodb://localhost:27017/test_database

# Ver usuários
mongosh --eval "db.users.find({}, {email:1, role:1, first_name:1}).pretty()" test_database

# Ver admins
mongosh --eval "db.users.find({role:{$in:['admin','superadmin']}}, {email:1, role:1}).pretty()" test_database

# Ver conversas da Maria
mongosh --eval "db.maria_conversations.countDocuments()" test_database
```

---

## 🔍 Debug

```bash
# Verificar se portas estão em uso
lsof -i :3000  # Frontend
lsof -i :8001  # Backend
lsof -i :3001  # Baileys

# Ver processos Python
ps aux | grep python

# Ver processos Node
ps aux | grep node

# Limpar cache Python
find /app/backend -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# Reinstalar dependências Python
cd /app/backend
pip install -r requirements.txt

# Reinstalar dependências Node (Baileys)
cd /app/baileys-server
npm install
```

---

## 🧹 Limpeza

```bash
# Limpar logs
sudo truncate -s 0 /var/log/supervisor/backend.err.log
sudo truncate -s 0 /var/log/supervisor/frontend.err.log

# Limpar sessões do Baileys (reconectar QR Code)
rm -rf /app/baileys-server/auth_info_baileys/

# Limpar cache do navegador (no navegador)
# Ctrl+Shift+Delete ou localStorage.clear() no console
```

---

## 📝 URLs Importantes

```
Frontend:              http://localhost:3000
Backend API:           http://localhost:8001
Maria Chat (UI):       http://localhost:3000 (botão flutuante)
Baileys Server:        http://localhost:3001
Login:                 http://localhost:3000/login
Admin Visa Updates:    http://localhost:3000/admin/visa-updates
Admin Knowledge Base:  http://localhost:3000/admin/knowledge-base
```

---

## 🎯 One-Liners Úteis

```bash
# Reiniciar tudo e ver logs do backend
sudo supervisorctl restart all && sleep 3 && tail -f /var/log/supervisor/backend.err.log

# Testar Maria de uma vez
curl -X POST http://localhost:8001/api/maria/chat -H "Content-Type: application/json" -d '{"message":"Olá Maria!"}'  | jq '.response'

# Ver último erro do backend
tail -n 50 /var/log/supervisor/backend.err.log | grep -i "error\|traceback" -A 5

# Verificar se tudo está rodando
sudo supervisorctl status && curl -s http://localhost:3001/status | jq '.connected' && curl -s http://localhost:8001/api/maria/health | jq '.status'
```

---

## 🆘 Resolver Problemas Comuns

```bash
# Backend não inicia
sudo supervisorctl restart backend
tail -n 100 /var/log/supervisor/backend.err.log

# Frontend não carrega
sudo supervisorctl restart frontend
curl http://localhost:3000

# Maria não responde
curl http://localhost:8001/api/maria/health
# Verificar se "gemini": true

# Admin não consegue acessar
python3 /app/backend/create_admin_user.py --list
# Verificar se role é "admin" ou "superadmin"

# Baileys desconectou
cd /app/baileys-server
npm start
# Escanear QR Code novamente
```

---

## 💡 Dica Final

Salve este arquivo nos seus favoritos! 📌

```bash
# Para ver este arquivo a qualquer momento:
cat /app/COMANDOS_RAPIDOS.md
```
