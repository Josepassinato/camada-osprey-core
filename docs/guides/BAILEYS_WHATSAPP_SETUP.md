# 🟢 Configuração do Baileys - WhatsApp para Maria

Este guia explica como configurar a integração do WhatsApp usando Baileys para permitir que a Maria envie mensagens proativas aos usuários.

## 📋 O que é Baileys?

**Baileys** é uma biblioteca JavaScript que permite conectar-se ao WhatsApp Web de forma programática (não-oficial). É amplamente utilizada para automação e bots do WhatsApp.

- **GitHub**: https://github.com/WhiskeySockets/Baileys
- **Documentação**: https://whiskeysockets.github.io/Baileys/

## ⚙️ Arquitetura Atual

O backend Python da Maria já está configurado para comunicar-se com um servidor Baileys via API HTTP:

- **Backend (Maria)**: `/app/backend/maria_whatsapp.py` - Cliente Python que faz requisições HTTP
- **Servidor Baileys (Node.js)**: Precisa ser executado separadamente (ainda não criado)

## 🚀 Passo a Passo para Configuração

### 1. Criar Servidor Baileys (Node.js)

Você precisa criar um pequeno servidor Node.js que rodará o Baileys. Crie uma nova pasta:

```bash
mkdir /app/baileys-server
cd /app/baileys-server
npm init -y
```

### 2. Instalar Dependências

```bash
npm install @whiskeysockets/baileys express qrcode-terminal
```

### 3. Criar o Servidor (`server.js`)

Crie o arquivo `/app/baileys-server/server.js`:

```javascript
const { default: makeWASocket, DisconnectReason, useMultiFileAuthState } = require('@whiskeysockets/baileys');
const express = require('express');
const qrcode = require('qrcode-terminal');

const app = express();
app.use(express.json());

let sock; // Socket do WhatsApp
let qrCodeData = null;
let isConnected = false;

// Inicializar conexão WhatsApp
async function connectToWhatsApp() {
    const { state, saveCreds } = await useMultiFileAuthState('auth_info_baileys');
    
    sock = makeWASocket({
        auth: state,
        printQRInTerminal: true
    });

    sock.ev.on('creds.update', saveCreds);

    sock.ev.on('connection.update', (update) => {
        const { connection, lastDisconnect, qr } = update;
        
        if (qr) {
            qrCodeData = qr;
            qrcode.generate(qr, { small: true });
            console.log('🔷 Escaneie o QR Code com WhatsApp');
        }
        
        if (connection === 'close') {
            const shouldReconnect = lastDisconnect?.error?.output?.statusCode !== DisconnectReason.loggedOut;
            console.log('❌ Conexão fechada:', lastDisconnect?.error);
            isConnected = false;
            
            if (shouldReconnect) {
                connectToWhatsApp();
            }
        } else if (connection === 'open') {
            console.log('✅ Conectado ao WhatsApp!');
            isConnected = true;
            qrCodeData = null;
        }
    });
}

// API Endpoints

// Status da conexão
app.get('/status', (req, res) => {
    res.json({
        connected: isConnected,
        phone: sock?.user?.id?.split(':')[0] || null,
        status: isConnected ? 'connected' : 'disconnected',
        qrCode: qrCodeData
    });
});

// Enviar mensagem
app.post('/send-message', async (req, res) => {
    const { to, message } = req.body;
    
    if (!isConnected) {
        return res.status(503).json({ error: 'WhatsApp não conectado' });
    }
    
    try {
        const jid = to.includes('@') ? to : `${to}@s.whatsapp.net`;
        const result = await sock.sendMessage(jid, { text: message });
        
        res.json({
            success: true,
            messageId: result.key.id,
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Iniciar servidor
const PORT = process.env.BAILEYS_PORT || 3001;

app.listen(PORT, () => {
    console.log(`🚀 Baileys Server rodando na porta ${PORT}`);
    connectToWhatsApp();
});
```

### 4. Iniciar o Servidor Baileys

```bash
cd /app/baileys-server
node server.js
```

### 5. Escanear QR Code

1. Quando o servidor iniciar, um **QR Code** será exibido no terminal
2. Abra o **WhatsApp** no seu celular
3. Vá em **Configurações > Aparelhos Conectados**
4. Clique em **Conectar um Aparelho**
5. Escaneie o QR Code do terminal

### 6. Configurar URL no Backend Python

No arquivo `/app/backend/.env`, adicione:

```env
BAILEYS_API_URL=http://localhost:3001
```

Se o servidor Baileys estiver em outra máquina, ajuste o URL.

### 7. Reiniciar Backend Python

```bash
sudo supervisorctl restart backend
```

## 📱 Como Usar

Agora a Maria pode enviar mensagens proativas via WhatsApp!

### Endpoints Disponíveis

1. **Mensagem de Boas-Vindas (automática após signup)**
   - Endpoint: `POST /api/maria/whatsapp/welcome/{user_id}`
   - Enviado automaticamente quando usuário se cadastra

2. **Enviar Mensagem Manual**
   - Endpoint: `POST /api/maria/whatsapp/send`
   - Body: `{ "phone": "5511999999999", "message": "Olá!" }`

3. **Verificar Status**
   - Endpoint: `GET /api/maria/whatsapp/status`

## 🔧 Troubleshooting

### Problema: QR Code não aparece
- Certifique-se de que o Node.js está instalado (`node --version`)
- Reinstale as dependências: `npm install`

### Problema: Conexão cai constantemente
- Baileys pode ter limitações de estabilidade
- Considere usar a API oficial do WhatsApp Business (paga): https://developers.facebook.com/docs/whatsapp

### Problema: Mensagens não enviadas
- Verifique se o número está no formato correto: `5511999999999` (código país + DDD + número)
- Certifique-se de que o número está salvo nos contatos do WhatsApp conectado

## 🏢 Alternativa: WhatsApp Business API (Oficial)

Para uso em produção, recomendamos a **WhatsApp Business API oficial**:

- **Vantagens**: Oficial, suporte, mais estável, recursos avançados
- **Desvantagens**: Pago, requer aprovação do Facebook
- **Link**: https://business.whatsapp.com/products/business-platform

### Migração para API Oficial

Caso opte pela API oficial, você precisará:

1. Criar uma conta Facebook Business
2. Solicitar acesso à API do WhatsApp
3. Configurar webhook
4. Atualizar `/app/backend/maria_whatsapp.py` com credenciais da API oficial

## 📝 Notas Importantes

1. **Baileys é não-oficial**: Pode violar os Termos de Serviço do WhatsApp
2. **Risco de ban**: Contas podem ser banidas por uso de bibliotecas não-oficiais
3. **Use com moderação**: Não envie spam
4. **Recomendação**: Para produção, use a API oficial

## ✅ Status Atual

- ✅ Backend Python configurado (`maria_whatsapp.py`)
- ✅ Endpoints API prontos
- ⚠️ Servidor Baileys precisa ser criado e iniciado
- ⚠️ QR Code precisa ser escaneado para conectar

## 🤝 Suporte

Para dúvidas:
- Documentação Baileys: https://whiskeysockets.github.io/Baileys/
- WhatsApp Business API: https://developers.facebook.com/docs/whatsapp
