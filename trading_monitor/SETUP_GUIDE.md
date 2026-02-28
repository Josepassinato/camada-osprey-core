# Trading Monitor - Guia de Setup Completo

## ActivTrades + ZuluTrade Copy Trading com Kill Switch

---

## Fase 1: Criar Contas (15 min)

### 1.1 ActivTrades Demo
1. Acesse **activtrades.com** → "Conta Demo"
2. Preencha dados, selecione **MT5** como plataforma
3. Escolha alavancagem **1:500** (padrão para demo)
4. Anote: **Server**, **Login (número)**, **Password**
5. Baixe o **MetaTrader 5** (desktop ou mobile)

### 1.2 ActivTrades Real (pré-configurar)
1. Acesse **activtrades.com** → "Abrir Conta Real"
2. Complete verificação KYC (documento + comprovante)
3. Escolha conta **MT5** com spread variável
4. **NÃO deposite ainda** — aguarde validação com a demo
5. Anote credenciais separadamente

### 1.3 ZuluTrade
1. Acesse **zulutrade.com** → "Sign Up"
2. Selecione **ActivTrades** como broker
3. Conecte sua conta **Demo** primeiro
4. Será pedido: Server, Login, Investor Password (read-only)

---

## Fase 2: Configurar ZuluTrade (20 min)

### 2.1 Selecionar Traders para Copiar
Na aba "Traders", filtre por:
- **ROI > 20%** (últimos 12 meses)
- **Drawdown < 25%**
- **Tempo ativo > 6 meses**
- **Trades por semana: 2-10** (evitar overtrading)
- **Followers > 50** (validação social)

### 2.2 Configurar ZuluGuard (OBRIGATÓRIO)
Para CADA trader copiado:
- **Capital Protection**: Defina valor máximo de perda por trader
- Sugestão: $200 por trader em conta de $10k
- Ação quando atingir: **Close trades and unfollow**

### 2.3 Configurar Tamanho de Posição
- **Fixed Lots**: 0.01 a 0.05 por pip signal
- OU **Pro-Rata**: proporcional ao capital do trader
- Comece PEQUENO na demo, aumente após validar

---

## Fase 3: Instalar Trading Monitor (5 min)

```bash
# Instalar dependência
pip install rich

# No Windows (para conexão MT5 real):
pip install MetaTrader5

# Setup inicial
cd trading_monitor
python -m trading_monitor.main setup
```

O wizard vai pedir:
1. Credenciais da conta Demo
2. Credenciais da conta Real (pode pular com 0)
3. Limites do Kill Switch
4. Intervalo de refresh

### Comandos disponíveis:
```bash
python -m trading_monitor.main setup     # Setup inicial
python -m trading_monitor.main sim       # Dashboard simulado (teste sem MT5)
python -m trading_monitor.main monitor   # Dashboard real (precisa MT5)
python -m trading_monitor.main status    # Status rápido
python -m trading_monitor.main kill      # EMERGÊNCIA: fechar tudo
python -m trading_monitor.main switch demo   # Mudar para demo
python -m trading_monitor.main switch real   # Mudar para real
python -m trading_monitor.main config    # Ver configuração
```

---

## Fase 4: Período de Validação (15 dias)

### Checklist Diário:
- [ ] Abrir dashboard: `python -m trading_monitor.main sim` (ou `monitor` no Windows)
- [ ] Verificar P&L diário
- [ ] Verificar se kill switch está OK (verde)
- [ ] Anotar drawdown máximo do dia
- [ ] Verificar se traders estão dentro do esperado

### Critérios para Aprovar (ir para Real):
- [ ] 15 dias completos de operação
- [ ] Drawdown máximo < 10% do capital
- [ ] P&L acumulado positivo
- [ ] Nenhum trader com perda > $200 (ZuluGuard)
- [ ] Kill switch nunca ativou em emergência
- [ ] Você entende os riscos

---

## Fase 5: Migrar para Conta Real

```bash
# 1. Configure credenciais reais (se não fez no setup)
python -m trading_monitor.main setup

# 2. Switch para modo real
python -m trading_monitor.main switch real
# Vai pedir confirmação: digite "REAL"

# 3. No ZuluTrade: desconecte demo, conecte conta real
# (mesmos traders, mesmas configs de ZuluGuard)

# 4. Monitore:
python -m trading_monitor.main monitor
```

---

## Limites Recomendados (Kill Switch)

| Parâmetro | Conservador | Moderado | Agressivo |
|-----------|------------|----------|-----------|
| Daily Loss | 2% | 3% | 5% |
| Max Drawdown | 8% | 10% | 15% |
| Max Positions | 5 | 10 | 20 |
| Max Lot Size | 0.5 | 1.0 | 2.0 |
| Max Exposure | 2.0 lots | 5.0 lots | 10.0 lots |

**Recomendação para começar: CONSERVADOR**

---

## Notas Importantes

1. **MetaTrader5 Python** só funciona no Windows. No Linux/macOS, use o modo `sim` para familiarização e monitore via MT5 mobile.

2. **Nunca compartilhe a Master Password**. O ZuluTrade só precisa da Investor Password (read-only).

3. O **kill switch** fecha posições automaticamente quando limites são atingidos. Isso protege contra:
   - Flash crashes
   - Trader copiado faz operação grande inesperada
   - Drawdown acumulado além do tolerável

4. **Depósito mínimo recomendado** para conta real: $1,000-$5,000 (para os lots fazerem sentido).

5. A **alavancagem alta** (1:500) não é problema se o position sizing estiver correto. O risco está no tamanho do lote, não na alavancagem disponível.
