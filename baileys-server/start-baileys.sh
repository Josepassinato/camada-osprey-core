#!/bin/bash

echo "═══════════════════════════════════════════════════════════"
echo "  🦅 INICIANDO BAILEYS WHATSAPP SERVER"
echo "═══════════════════════════════════════════════════════════"
echo ""

cd /app/baileys-server

# Verificar se Node.js está instalado
if ! command -v node &> /dev/null; then
    echo "❌ Node.js não está instalado!"
    echo "   Instale com: apt-get install nodejs npm"
    exit 1
fi

echo "✅ Node.js instalado: $(node --version)"
echo "✅ NPM instalado: $(npm --version)"
echo ""

# Verificar se as dependências estão instaladas
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependências..."
    npm install
    echo ""
fi

echo "🚀 Iniciando servidor Baileys..."
echo ""
echo "📝 INSTRUÇÕES:"
echo "   1. Um QR Code aparecerá abaixo"
echo "   2. Abra o WhatsApp no seu celular"
echo "   3. Vá em: Configurações > Aparelhos Conectados"
echo "   4. Clique em: Conectar um Aparelho"
echo "   5. Escaneie o QR Code"
echo ""
echo "⚠️  IMPORTANTE: Mantenha este terminal aberto!"
echo ""

# Iniciar servidor
npm start
