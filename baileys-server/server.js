const { default: makeWASocket, DisconnectReason, useMultiFileAuthState } = require('@whiskeysockets/baileys');
const express = require('express');
const qrcode = require('qrcode-terminal');

const app = express();
app.use(express.json());

let sock; // Socket do WhatsApp
let qrCodeData = null;
let isConnected = false;
let phoneNumber = null;

// Inicializar conexão WhatsApp
async function connectToWhatsApp() {
    console.log('🔄 Iniciando conexão com WhatsApp...');
    
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
            console.log('\n');
            console.log('═══════════════════════════════════════════════════════════');
            console.log('🔷 ESCANEIE O QR CODE COM SEU WHATSAPP');
            console.log('═══════════════════════════════════════════════════════════');
            console.log('1. Abra o WhatsApp no seu celular');
            console.log('2. Vá em: Configurações > Aparelhos Conectados');
            console.log('3. Clique em: Conectar um Aparelho');
            console.log('4. Escaneie o QR Code abaixo:\n');
            qrcode.generate(qr, { small: true });
            console.log('═══════════════════════════════════════════════════════════\n');
        }
        
        if (connection === 'close') {
            const shouldReconnect = lastDisconnect?.error?.output?.statusCode !== DisconnectReason.loggedOut;
            console.log('❌ Conexão fechada:', lastDisconnect?.error);
            isConnected = false;
            phoneNumber = null;
            
            if (shouldReconnect) {
                console.log('🔄 Reconectando em 5 segundos...');
                setTimeout(() => connectToWhatsApp(), 5000);
            } else {
                console.log('⚠️ Você foi desconectado. Reinicie o servidor para escanear novamente.');
            }
        } else if (connection === 'open') {
            console.log('\n✅ CONECTADO AO WHATSAPP COM SUCESSO!');
            isConnected = true;
            
            if (sock.user) {
                phoneNumber = sock.user.id.split(':')[0];
                console.log(`📱 Número conectado: +${phoneNumber}`);
            }
            
            console.log('🚀 Servidor Baileys pronto para enviar mensagens!\n');
        }
    });

    // Log de mensagens recebidas (útil para debug)
    sock.ev.on('messages.upsert', async ({ messages, type }) => {
        if (type === 'notify') {
            for (const msg of messages) {
                if (!msg.key.fromMe && msg.message) {
                    const from = msg.key.remoteJid;
                    const text = msg.message.conversation || msg.message.extendedTextMessage?.text;
                    console.log(`📨 Mensagem recebida de ${from}: ${text}`);
                }
            }
        }
    });
}

// ============================================================================
// API ENDPOINTS
// ============================================================================

// Health check / Status
app.get('/status', (req, res) => {
    res.json({
        connected: isConnected,
        phone: phoneNumber,
        status: isConnected ? 'connected' : (qrCodeData ? 'waiting_qr_scan' : 'disconnected'),
        qrCode: qrCodeData,
        timestamp: new Date().toISOString()
    });
});

// Enviar mensagem
app.post('/send-message', async (req, res) => {
    const { to, message, quoted } = req.body;
    
    if (!to || !message) {
        return res.status(400).json({ 
            success: false,
            error: 'Campos "to" e "message" são obrigatórios' 
        });
    }
    
    if (!isConnected) {
        return res.status(503).json({ 
            success: false,
            error: 'WhatsApp não conectado. Verifique o status em /status' 
        });
    }
    
    try {
        // Formatar número para WhatsApp
        let whatsappNumber = to.replace(/[^0-9]/g, '');
        
        // Se não tiver @, adicionar
        const jid = whatsappNumber.includes('@') ? whatsappNumber : `${whatsappNumber}@s.whatsapp.net`;
        
        console.log(`📤 Enviando mensagem para ${jid}...`);
        
        // Enviar mensagem
        const result = await sock.sendMessage(jid, { 
            text: message 
        });
        
        console.log(`✅ Mensagem enviada com sucesso! ID: ${result.key.id}`);
        
        res.json({
            success: true,
            messageId: result.key.id,
            to: jid,
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        console.error(`❌ Erro ao enviar mensagem: ${error.message}`);
        res.status(500).json({ 
            success: false,
            error: error.message 
        });
    }
});

// Enviar mensagem com imagem
app.post('/send-image', async (req, res) => {
    const { to, imageUrl, caption } = req.body;
    
    if (!to || !imageUrl) {
        return res.status(400).json({ 
            success: false,
            error: 'Campos "to" e "imageUrl" são obrigatórios' 
        });
    }
    
    if (!isConnected) {
        return res.status(503).json({ 
            success: false,
            error: 'WhatsApp não conectado' 
        });
    }
    
    try {
        const jid = to.includes('@') ? to : `${to}@s.whatsapp.net`;
        
        const result = await sock.sendMessage(jid, { 
            image: { url: imageUrl },
            caption: caption || ''
        });
        
        res.json({
            success: true,
            messageId: result.key.id,
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        res.status(500).json({ 
            success: false,
            error: error.message 
        });
    }
});

// Desconectar
app.post('/disconnect', async (req, res) => {
    try {
        if (sock) {
            await sock.logout();
            console.log('👋 WhatsApp desconectado');
        }
        
        res.json({
            success: true,
            message: 'WhatsApp desconectado com sucesso'
        });
    } catch (error) {
        res.status(500).json({ 
            success: false,
            error: error.message 
        });
    }
});

// ============================================================================
// INICIAR SERVIDOR
// ============================================================================

const PORT = process.env.BAILEYS_PORT || 3001;

app.listen(PORT, () => {
    console.log('\n');
    console.log('═══════════════════════════════════════════════════════════');
    console.log('  🦅 BAILEYS WHATSAPP SERVER - OSPREY MARIA');
    console.log('═══════════════════════════════════════════════════════════');
    console.log(`  📡 Servidor rodando em: http://localhost:${PORT}`);
    console.log('  📚 Endpoints disponíveis:');
    console.log('     GET  /status         - Status da conexão');
    console.log('     POST /send-message   - Enviar mensagem');
    console.log('     POST /send-image     - Enviar imagem');
    console.log('     POST /disconnect     - Desconectar');
    console.log('═══════════════════════════════════════════════════════════\n');
    
    // Iniciar conexão WhatsApp
    connectToWhatsApp();
});

// Tratamento de erros não capturados
process.on('uncaughtException', (error) => {
    console.error('❌ Erro não capturado:', error);
});

process.on('unhandledRejection', (reason, promise) => {
    console.error('❌ Promise rejeitada:', reason);
});
