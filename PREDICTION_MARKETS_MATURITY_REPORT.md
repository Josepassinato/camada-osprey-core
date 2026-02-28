# Produto Mais Maduro e Confiável — Mercado de Prediction Markets (Fev 2026)

## Resumo Executivo

Não existe um único "produto mais maduro" neste ramo — a resposta depende do critério. Segue a análise por camada do ecossistema.

---

## 1. Plataformas (onde o dinheiro está)

### 🏆 Kalshi — O Mais Maduro para Produção

| Critério | Avaliação |
|---|---|
| **Regulação** | ✅ Única plataforma com licença CFTC (Designated Contract Market) desde 2018 |
| **API** | ✅ REST v2 + WebSocket + FIX 4.4 (protocolo institucional) |
| **Sandbox** | ✅ Ambiente demo completo para testes sem risco |
| **SDKs** | ⚠️ Python/JS auto-gerados (Swagger), funcionais mas não polidos |
| **Autenticação** | ✅ Token-based tradicional (familiar para devs backend) |
| **Latência** | ✅ Single-digit ms (CLOB off-chain centralizado) |
| **Uptime** | ✅ Infraestrutura centralizada, SLA implícito |
| **Documentação** | ✅ ReadMe-powered, OpenAPI spec, multi-linguagem |
| **Suporte Dev** | ✅ Canal Slack direto com o time |
| **Market share** | 35% (~$474M open interest) |

**Por que é o mais maduro:**
- Regulação CFTC = clareza jurídica e confiança institucional
- FIX 4.4 = mesmo protocolo da NYSE/CME — integração trivial para firmas quant
- Sandbox = testes sem risco real (Polymarket não tem sandbox)
- API tradicional = sem blockchain, sem wallets, sem gas — familiar para qualquer dev backend

**Limitações:**
- Restrita a residentes dos EUA
- SDK oficial auto-gerado (o próprio Kalshi recomenda gerar seu próprio client para produção)
- Menos volume que Polymarket ($56B vs ~$20B)
- Token expira a cada 30 min (requer refresh automático)

---

### Polymarket — O Maior em Volume, Menos Maduro em Tooling

| Critério | Avaliação |
|---|---|
| **Regulação** | ❌ Sem regulação, proíbe traders dos EUA |
| **API** | ✅ REST + WebSocket (CLOB), latência <50ms |
| **Sandbox** | ❌ Não existe — teste com dinheiro real na mainnet |
| **SDKs** | ⚠️ py-clob-client (826★, mas muitos bugs abertos — auth 401, stale data, sell bugs) |
| **Autenticação** | ⚠️ EIP-712 / wallet signing (requer expertise blockchain) |
| **Latência** | ⚠️ Matching off-chain rápido, mas settlement 2-3s (Polygon) |
| **Documentação** | ⚠️ Razoável, menos organizada que Kalshi |
| **Suporte Dev** | ⚠️ GitHub issues, Discord (sem SLA) |
| **Market share** | 44% (~$56B volume) |

**Pontos fortes:**
- Maior volume e liquidez do mercado
- Mercados mais diversos (política, crypto, esportes, cultura)
- Fees quase zero para makers
- Novo CLI em Rust (polymarket-cli) — promissor mas v0.1.4
- Aquisição da Dome (YC) + programa de $1M para builders

**Problemas sérios do SDK Python (py-clob-client):**
- Issue #278: Auth 401 com credenciais válidas
- Issue #180: Order book retorna dados stale enquanto /price funciona
- Issue #265: Compra funciona, venda falha ("not enough balance")
- Issue #182: Bug de paginação em 500+ ordens
- Dezenas de issues abertos em Fev 2026 — manutenção limitada

---

## 2. SDKs e CLIs (ferramentas de desenvolvimento)

### Comparativo de Maturidade

| Ferramenta | Linguagem | Stars | Versão | Maturidade | Confiabilidade |
|---|---|---|---|---|---|
| **Kalshi REST API v2** | Agnóstico | - | v2.0 | ★★★★☆ | ★★★★☆ |
| **kalshi-python** (oficial) | Python | 89 | 2.1.4 | ★★★☆☆ | ★★★☆☆ |
| **aiokalshi** (comunidade) | Python | ~30 | - | ★★★☆☆ | ★★★★☆ |
| **py-clob-client** (Polymarket) | Python | 826 | - | ★★★☆☆ | ★★☆☆☆ |
| **clob-client** (Polymarket) | TypeScript | ~200 | - | ★★★☆☆ | ★★★☆☆ |
| **polymarket-client-sdk** | Rust | ~50 | 0.4 | ★★★☆☆ | ★★★☆☆ |
| **polymarket-cli** | Rust | 1.320 | 0.1.4 | ★★☆☆☆ | ★★☆☆☆ |
| **pmxt** (unificado) | TS/Python | 100+ | 2.0 | ★★★☆☆ | ★★★☆☆ |

### 🏆 Para SDK individual: `aiokalshi` (Python async para Kalshi)

O `aiokalshi` é o SDK mais bem projetado do ecossistema:
- Asyncio-native (não wrapper sync)
- Modelos Pydantic tipados com autocomplete
- Paridade com a API Kalshi
- Não requer autenticação para queries públicas

### 🏆 Para API unificada cross-platform: `pmxt`

O `pmxt` é o equivalente do CCXT para prediction markets:
- Suporta Polymarket, Kalshi, Limitless
- API unificada em TypeScript e Python
- Padrões CCXT (familiar para quem já usa CCXT em crypto)
- v2.0 com OpenAPI 3.0 spec
- Ativo e mantido (Jan 2026)

---

## 3. Bots e Ferramentas de Trading

| Ferramenta | Tipo | Plataforma | Maturidade |
|---|---|---|---|
| **poly-maker** | Market Making | Polymarket | ★★★☆☆ |
| **PolyGun** | Telegram Bot | Polymarket | ★★★★☆ |
| **PolyCue** | Multi-strategy | Polymarket | ★★★☆☆ |
| **Onyx Terminal** | Trading Terminal | Polymarket | ★★★☆☆ |
| **Polymarket Agents** | AI Framework | Polymarket | ★★★☆☆ |

Nenhum bot atingiu maturidade institucional. Todos são experimentais.

---

## 4. Riscos Transversais ao Ecossistema

### Segurança — Typosquatting no Rust (Fev 2026)
Dois crates maliciosos foram publicados no crates.io tentando roubar credenciais:
- `polymarket-clients-sdk` (com "s" em clients) — RUSTSEC-2026-0010
- `polymarket-client-sdks` (com "s" no final) — 33 downloads antes de ser removido

O crate legítimo é **`polymarket-client-sdk`** (sem "s" extra). Ambos os maliciosos foram removidos.

### Regulação
- Kalshi: CFTC-regulada, clara para uso nos EUA
- Polymarket: Sem regulação, CEO investigado pelo FBI (Nov 2024), proíbe EUA
- Robinhood + Coinbase estão construindo exchanges CFTC próprias (2026)

### Sustentabilidade
- Polymarket: $56B volume, programa de $1M para builders, aquisição da Dome
- Kalshi: $474M open interest, parcerias institucionais, FIX protocol
- Ambas plataformas parecem sustentáveis a médio prazo

---

## 5. Conclusão — Ranking de Maturidade

### Por camada:

| Camada | Produto Mais Maduro | Razão |
|---|---|---|
| **Plataforma/Exchange** | **Kalshi** | CFTC-regulada, FIX 4.4, sandbox, API tradicional |
| **SDK Python** | **aiokalshi** (Kalshi) | Tipado, async, Pydantic, bem projetado |
| **SDK Rust** | **polymarket-client-sdk** | Único SDK Rust maduro no espaço |
| **CLI** | **polymarket-cli** | Único CLI oficial (mas v0.1.4, experimental) |
| **API Unificada** | **pmxt** | CCXT-style, multi-platform, v2.0 |
| **Volume/Liquidez** | **Polymarket** | $56B volume, maior mercado |

### Veredicto Final:

**Para produção com dinheiro real → Kalshi** (regulada, sandbox, API madura, FIX protocol).

**Para desenvolvimento/pesquisa/agentes AI → Polymarket CLI + pmxt** (maior ecossistema, mais mercados, fees baixas, mas experimental).

**Nenhum produto neste espaço está verdadeiramente "maduro" no sentido institucional** — o mercado inteiro de prediction markets programáticos tem menos de 3 anos de evolução séria. Mesmo a Kalshi, a mais madura, tem SDKs auto-gerados que ela própria não recomenda para produção.
