# 🟢 Baileys WhatsApp Server - Osprey Maria

Servidor Node.js para integração do WhatsApp com a assistente virtual Maria usando Baileys.

## 🚀 Como Iniciar

### Passo 1: Iniciar o Servidor

```bash
cd /app/baileys-server
npm start
```

### Passo 2: Escanear QR Code

1. Quando o servidor iniciar, um **QR Code** aparecerá no terminal
2. Abra o **WhatsApp** no seu celular
3. Vá em: **Configurações > Aparelhos Conectados**
4. Clique em: **Conectar um Aparelho**
5. Escaneie o QR Code do terminal

### Passo 3: Aguardar Conexão

Quando conectar com sucesso, você verá:
```
✅ CONECTADO AO WHATSAPP COM SUCESSO!
📱 Número conectado: +5511999999999
🚀 Servidor Baileys pronto para enviar mensagens!
```

## 📡 API Endpoints

### 1. Status da Conexão
```bash
GET http://localhost:3001/status
```

**Resposta:**
```json
{
  "connected": true,
  "phone": "5511999999999",
  "status": "connected",
  "timestamp": "2025-11-21T08:30:00.000Z"
}
```

### 2. Enviar Mensagem
```bash
POST http://localhost:3001/send-message
Content-Type: application/json

{
  "to": "5511999999999",
  "message": "Olá! Esta é uma mensagem da Maria 👋"
}
```

**Resposta:**
```json
{
  "success": true,
  "messageId": "3EB0XXXXXXXXXXXXXXXX",
  "to": "5511999999999@s.whatsapp.net",
  "timestamp": "2025-11-21T08:30:00.000Z"
}
```

### 3. Enviar Imagem
```bash
POST http://localhost:3001/send-image
Content-Type: application/json

{
  "to": "5511999999999",
  "imageUrl": "https://example.com/image.jpg",
  "caption": "Olha esta imagem!"
}
```

### 4. Desconectar
```bash
POST http://localhost:3001/disconnect
```

## 🧪 Testar com cURL

```bash
# Verificar status
curl http://localhost:3001/status

# Enviar mensagem
curl -X POST http://localhost:3001/send-message \
  -H "Content-Type: application/json" \
  -d '{"to":"5511999999999","message":"Teste da Maria!"}'
```

## 🔧 Integração com Backend Python

O backend Python (`/app/backend/maria_whatsapp.py`) já está configurado para se comunicar com este servidor!

Endpoints da Maria que usam WhatsApp:
- `POST /api/maria/whatsapp/welcome/{user_id}` - Mensagem de boas-vindas
- `POST /api/maria/whatsapp/send` - Enviar mensagem manual
- `GET /api/maria/whatsapp/status` - Status da conexão

## ⚠️ Notas Importantes

1. **Baileys é não-oficial**: Pode violar os Termos de Serviço do WhatsApp
2. **Risco de ban**: Contas podem ser banidas por uso não autorizado
3. **Use com moderação**: Não envie spam
4. **Para produção**: Considere usar WhatsApp Business API oficial

## 🐛 Troubleshooting

### QR Code não aparece
- Certifique-se de que o Node.js está instalado: `node --version`
- Reinstale dependências: `npm install`

### Conexão cai constantemente
- Mantenha o servidor rodando em background
- Use `pm2` para gerenciamento: `npm install -g pm2 && pm2 start server.js`

### Mensagens não são enviadas
- Verifique se está conectado: `curl http://localhost:3001/status`
- Confirme formato do número: `5511999999999` (sem espaços ou caracteres)
- Certifique-se de que o número está salvo nos contatos

## 📂 Arquivos Gerados

O servidor cria uma pasta `auth_info_baileys/` com as credenciais de autenticação. **Não delete esta pasta** ou terá que escanear o QR Code novamente.

## 🔄 Reiniciar Servidor

```bash
# Parar o servidor (Ctrl+C no terminal)
# Iniciar novamente
cd /app/baileys-server
npm start
```

## 💡 Dicas

- Use `pm2` para rodar em background e auto-restart
- Configure logs para monitorar mensagens
- Implemente rate limiting para evitar spam
- Considere migrar para API oficial do WhatsApp Business para produção
