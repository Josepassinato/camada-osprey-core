# Polymarket CLI - Análise Técnica Completa

## 1. Visão Geral

**Repositório:** https://github.com/Polymarket/polymarket-cli
**Linguagem:** Rust (edition 2024, rust-version 1.88.0)
**Versão:** 0.1.4
**Licença:** MIT
**Status:** Experimental / Preview

O **Polymarket CLI** é uma ferramenta de linha de comando escrita em Rust que permite interagir com a plataforma [Polymarket](https://polymarket.com) — um mercado de previsões baseado em blockchain (Polygon). O programa permite navegar mercados, realizar trades, gerenciar posições e interagir com contratos on-chain diretamente do terminal ou como API JSON para scripts e agentes automatizados.

---

## 2. Arquitetura do Projeto

```
polymarket-cli/                 (8.668 linhas de código total)
├── Cargo.toml                  # Metadados e dependências
├── src/
│   ├── main.rs        (203 L) # Entry point, CLI parsing com clap, error handling
│   ├── auth.rs        (102 L) # Resolução de wallet, provider RPC, autenticação CLOB
│   ├── config.rs      (212 L) # Arquivo de config (~/.config/polymarket/config.json)
│   ├── shell.rs        (98 L) # REPL interativo com rustyline
│   ├── commands/               # Um módulo por grupo de comandos
│   │   ├── mod.rs      (90 L) # Helpers: is_numeric_id, parse_address, parse_condition_id
│   │   ├── clob.rs  (1178 L) # ★ Maior módulo - order book, trading, rewards
│   │   ├── ctf.rs    (534 L) # Operações CTF: split, merge, redeem
│   │   ├── data.rs   (395 L) # Dados on-chain: posições, trades, leaderboards
│   │   ├── wallet.rs (304 L) # Gerenciamento de carteira
│   │   ├── approve.rs(214 L) # Aprovações de contratos ERC-20/ERC-1155
│   │   ├── setup.rs  (199 L) # Wizard de configuração inicial
│   │   ├── upgrade.rs(219 L) # Auto-atualização
│   │   ├── markets.rs(158 L) # Listagem e busca de mercados
│   │   ├── events.rs (123 L) # Eventos (agrupam mercados)
│   │   ├── tags.rs   (148 L) # Tags e categorias
│   │   ├── comments.rs(166 L)# Comentários
│   │   ├── series.rs  (86 L) # Séries recorrentes
│   │   ├── sports.rs  (91 L) # Metadados esportivos
│   │   ├── bridge.rs  (65 L) # Bridge cross-chain
│   │   └── profiles.rs(42 L) # Perfis públicos
│   └── output/                 # Renderização de output (table/JSON) por grupo
│       ├── mod.rs    (153 L) # OutputFormat enum, truncate(), format_decimal()
│       ├── clob.rs  (1467 L) # ★ Maior output - rendering do CLOB
│       ├── data.rs   (607 L) # Output de dados on-chain
│       ├── events.rs (242 L) # Output de eventos
│       ├── markets.rs(237 L) # Output de mercados
│       ├── bridge.rs (202 L) # Output de bridge
│       ├── series.rs (118 L) # Output de séries
│       ├── comments.rs(113 L)# Output de comentários
│       ├── tags.rs   (103 L) # Output de tags
│       ├── approve.rs(103 L) # Output de aprovações
│       ├── ctf.rs     (85 L) # Output de operações CTF
│       ├── sports.rs  (82 L) # Output de esportes
│       └── profiles.rs(41 L) # Output de perfis
├── tests/
│   └── cli_integration.rs (488 L) # Testes de integração CLI
├── .github/workflows/
│   ├── ci.yml                  # CI: fmt, clippy, testes (ubuntu + macOS)
│   └── release.yml             # Release multi-plataforma com Homebrew
├── Formula/polymarket.rb       # Fórmula Homebrew
├── install.sh                  # Script de instalação shell
└── scripts/update-formula.sh   # Atualização automática da fórmula
```

---

## 3. Dependências Principais

| Dependência | Versão | Propósito |
|---|---|---|
| `polymarket-client-sdk` | 0.4 | SDK oficial Polymarket (gamma, data, bridge, clob, ctf) |
| `alloy` | 1.6.3 | Framework Ethereum: providers, signers, tipos Solidity |
| `clap` | 4 (derive) | Parsing de argumentos CLI com macros derive |
| `tokio` | 1 (rt-multi-thread) | Runtime assíncrono |
| `serde` / `serde_json` | 1 | Serialização JSON |
| `tabled` | 0.17 | Renderização de tabelas formatadas no terminal |
| `rust_decimal` | 1 | Aritmética decimal precisa (evita floating-point bugs) |
| `anyhow` | 1 | Error handling ergonômico |
| `chrono` | 0.4 | Manipulação de datas |
| `dirs` | 6 | Descoberta de diretórios do sistema (~/.config) |
| `rustyline` | 15 | Editor de linha com histórico (shell interativo) |

**Dev dependencies:** `assert_cmd`, `predicates`, `rust_decimal_macros`

---

## 4. Funcionalidades Principais

### 4.1 Navegação de Mercados (Sem Wallet)
- **markets list/get/search/tags** — Listagem, busca e detalhes de mercados
- **events list/get/tags** — Eventos que agrupam mercados relacionados
- **tags/series/comments/profiles/sports** — Metadados e informações sociais
- **clob price/midpoint/spread/book** — Preços, order book, spreads (somente leitura)
- **clob price-history** — Histórico de preços com intervalos configuráveis
- **data positions/trades/leaderboard** — Dados públicos on-chain

### 4.2 Trading (Requer Wallet)
- **clob create-order** — Ordens limit (GTC, FOK, GTD, FAK)
- **clob market-order** — Ordens a mercado
- **clob post-orders** — Múltiplas ordens em batch
- **clob cancel/cancel-all/cancel-market** — Cancelamento de ordens
- **clob balance/trades/orders** — Saldo, trades e ordens abertas

### 4.3 Operações On-Chain (Requer Wallet + MATIC)
- **ctf split** — Dividir USDC em tokens YES/NO
- **ctf merge** — Fundir tokens de volta em USDC
- **ctf redeem** — Resgatar tokens vencedores após resolução
- **ctf redeem-neg-risk** — Resgate de posições neg-risk
- **approve set** — Aprovar contratos (6 transações on-chain)
- **bridge deposit** — Depositar ativos de outras chains

### 4.4 Gerenciamento
- **wallet create/import/show/reset** — Gerenciamento de carteira
- **setup** — Wizard de configuração guiada
- **shell** — REPL interativo com histórico
- **upgrade** — Auto-atualização
- **status** — Health check da API

---

## 5. Padrões de Design e Qualidade

### 5.1 Separação Comando/Output
O projeto segue uma separação clara entre **lógica de comando** (`commands/`) e **renderização** (`output/`). Cada grupo de comandos tem um módulo de comando correspondente a um módulo de output, facilitando a manutenção e adição de novos formatos de saída.

### 5.2 Dual Output (Table/JSON)
Todos os comandos suportam `--output table` (padrão para humanos) e `--output json` (para scripts). Erros seguem o mesmo padrão: table mode usa stderr, JSON mode retorna `{"error": "..."}` em stdout com exit code não-zero.

### 5.3 Autenticação em Camadas
O módulo `auth.rs` implementa resolução hierárquica de credenciais:
1. Flag `--private-key` (prioridade máxima)
2. Variável de ambiente `POLYMARKET_PRIVATE_KEY`
3. Arquivo de configuração `~/.config/polymarket/config.json`

Suporta 3 tipos de assinatura: **proxy** (padrão), **eoa** e **gnosis-safe**.

### 5.4 Segurança
- Arquivos de configuração criados com permissões restritas (`0o600` no Unix)
- Diretório de config com permissões `0o700`
- Variáveis de ambiente sanitizadas nos testes (limpeza de POLYMARKET_PRIVATE_KEY)
- Uso de `rust_decimal` em vez de floating-point para valores monetários

### 5.5 Segregação de Comandos Autenticados
O módulo CLOB (`commands/clob.rs`) faz uma separação explícita entre:
- **execute_read** — Comandos públicos sem autenticação
- **execute_trade** — Comandos de trading autenticados
- **execute_rewards** — Comandos de recompensas autenticados
- **execute_account** — Gerenciamento de conta autenticado

### 5.6 Performance do Build Release
```toml
[profile.release]
lto = "thin"         # Link-Time Optimization
codegen-units = 1    # Compilação em unidade única
strip = true         # Remove símbolos de debug
panic = "abort"      # Reduz tamanho do binário
```

---

## 6. Testes

### 6.1 Testes Unitários (inline)
Distribuídos em vários módulos com `#[cfg(test)]`:
- **commands/mod.rs** — Validação de `is_numeric_id`, `parse_address`, `parse_condition_id`
- **commands/clob.rs** — Parsing de token IDs, datas
- **commands/ctf.rs** — Conversão USDC, parsing de amounts, partitions
- **commands/wallet.rs** — Normalização de chaves
- **config.rs** — Resolução de chaves e tipos de assinatura
- **auth.rs** — Parsing de tipos de assinatura
- **output/mod.rs** — Truncamento de strings, formatação decimal

### 6.2 Testes de Integração (`tests/cli_integration.rs`)
**488 linhas** com 40+ testes que verificam:
- Help de todos os top-level commands
- Subcomandos de cada grupo
- Validação de argumentos obrigatórios
- Contrato de erros JSON vs Table
- Formato de output padrão
- Comportamento gracioso sem wallet configurada

### 6.3 CI/CD
- **CI:** `cargo fmt --check`, `cargo clippy -- -D warnings`, `cargo test` em Ubuntu e macOS
- **Release:** Build multi-plataforma (x86_64/aarch64 para macOS e Linux), com cross-compilation, checksums SHA256, GitHub Release automático e atualização do Homebrew formula

---

## 7. Pontos Fortes

1. **Código bem estruturado** — Separação clara de responsabilidades com módulos coesos
2. **Cobertura de testes sólida** — Testes unitários para parsing/validação + integração CLI
3. **Dual output consistente** — JSON para automação, tabelas para humanos
4. **Aritmética monetária segura** — `rust_decimal` evita erros de floating-point
5. **Segurança de credenciais** — Permissões Unix restritivas no config
6. **UX completa** — Shell interativo, setup wizard, auto-update
7. **Build otimizado** — LTO, strip, panic=abort para binários pequenos e rápidos
8. **SDK oficial** — Usa `polymarket-client-sdk` publicado (não reimplementa APIs)
9. **Cross-platform** — CI em Ubuntu + macOS, release para 4 targets

---

## 8. Pontos de Atenção

1. **Software experimental** — O próprio README adverte: "use at your own risk and do not use with large amounts of funds"
2. **RPC hardcoded** — O endpoint Polygon RPC (`https://polygon.drpc.org`) está fixo em `auth.rs:12`, sem opção de configuração
3. **Sem rate limiting** — Nenhuma proteção contra excesso de chamadas à API
4. **Chave privada em plaintext** — O config armazena a chave privada em JSON (embora com permissões restritivas)
5. **Sem logging/debug mode** — Não há mecanismo de log para troubleshooting
6. **Shell simplificado** — O REPL não suporta aspas simples, escape, nem autocompletion
7. **Sem testes de rede** — Testes de integração verificam apenas CLI parsing, não chamadas reais à API
8. **Endereço USDC hardcoded** — O endereço do contrato USDC Polygon está fixo como default em vários locais

---

## 9. Estatísticas

| Métrica | Valor |
|---|---|
| Total de linhas de código | 8.668 |
| Módulos de comando | 15 |
| Módulos de output | 12 |
| Subcomandos CLOB | 47 |
| Total de subcomandos (estimado) | ~80+ |
| Testes de integração | 40+ |
| Dependências runtime | 11 |
| Targets de release | 4 (x86_64/aarch64 Linux/macOS) |
| Blockchain | Polygon (chain ID 137) |

---

## 10. Conclusão

O Polymarket CLI é um projeto **bem arquitetado e bem implementado** para a sua fase (v0.1.4, experimental). A escolha de Rust proporciona segurança de memória, performance e binários auto-contidos. O código segue boas práticas de Rust idiomático (uso de `clap derive`, `anyhow`, pattern matching exaustivo, separação de concerns). A cobertura de testes é boa para parsing e CLI, embora falte testes de integração com a rede real. O projeto depende fortemente do `polymarket-client-sdk`, que abstrai toda a comunicação com as APIs do Polymarket, mantendo o CLI focado em UX e formatação.
