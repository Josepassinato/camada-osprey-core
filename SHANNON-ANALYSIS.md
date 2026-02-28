# Analise do Repositorio Shannon (KeygraphHQ)

**Repositorio:** https://github.com/KeygraphHQ/shannon
**Data da analise:** 2026-02-28
**Licenca:** AGPL-3.0
**Linguagem principal:** TypeScript (~9.700 linhas)
**Commits:** 170 | **Contribuidores:** 5 | **Primeiro commit:** 2025-10-03

---

## 1. Visao Geral

**Shannon** e um framework de pentest (teste de penetracao) totalmente autonomo alimentado por IA. Seu objetivo e encontrar e explorar vulnerabilidades em aplicacoes web antes que atacantes reais o facam. Diferente de scanners tradicionais que apenas alertam, Shannon **executa exploits reais** para comprovar que vulnerabilidades sao de fato exploraveis.

O projeto e desenvolvido pela **Keygraph** e existe em duas edicoes:
- **Shannon Lite** (este repositorio, AGPL-3.0) - Para equipes de seguranca e pesquisadores
- **Shannon Pro** (comercial) - Para empresas com analise avancada de fluxo de dados baseada em LLM

### Problema que Resolve

Equipes de desenvolvimento usando ferramentas como Claude Code e Cursor publicam codigo constantemente, mas testes de penetracao tradicionais acontecem tipicamente uma vez por ano. Shannon fecha essa lacuna atuando como um pentester white-box sob demanda.

---

## 2. Arquitetura

### 2.1 Stack Tecnologico

| Componente | Tecnologia |
|------------|-----------|
| **Linguagem** | TypeScript (Node.js, ESM) |
| **Motor de IA** | Anthropic Claude Agent SDK (`@anthropic-ai/claude-agent-sdk`) |
| **Orquestracao** | Temporal.io (workflows duraveis com recuperacao de falhas) |
| **Containerizacao** | Docker + Docker Compose |
| **Automacao de Browser** | Playwright via MCP (Model Context Protocol) |
| **Ferramentas de Seguranca** | Nmap, Subfinder, WhatWeb, Schemathesis |
| **Validacao de Config** | AJV (JSON Schema) |
| **CLI** | Script Bash (`./shannon`) |

### 2.2 Diagrama de Fluxo

```
CLI (./shannon)
    |
Docker Compose (Temporal Server + Worker + Router opcional)
    |
Temporal Client (src/temporal/client.ts)
    |
Temporal Server (orquestracao duravel)
    |
Temporal Worker (src/temporal/worker.ts)
    |
Activities (src/temporal/activities.ts)  <-->  Workflows (src/temporal/workflows.ts)
    |
Services Layer (DI Container)
    |
Claude Agent SDK (com servidores MCP)
    |
Agentes AI autonomos (13 agentes especializados)
```

### 2.3 Pipeline de 5 Fases

Shannon emula a metodologia de um pentester humano em 5 fases:

```
Fase 1: PRE-RECONHECIMENTO (Sequencial)
   - Analise de codigo-fonte + scans externos (nmap, subfinder, whatweb)
   - Deliverable: code_analysis_deliverable.md
        |
Fase 2: RECONHECIMENTO (Sequencial)
   - Mapeamento de superficie de ataque
   - Deliverable: recon_deliverable.md
        |
Fase 3: ANALISE DE VULNERABILIDADES (5 agentes em paralelo)
   |-- Injection Analysis --> injection_exploitation_queue.json
   |-- XSS Analysis --> xss_exploitation_queue.json
   |-- Auth Analysis --> auth_exploitation_queue.json
   |-- Authz Analysis --> authz_exploitation_queue.json
   |-- SSRF Analysis --> ssrf_exploitation_queue.json
        |
Fase 4: EXPLORACAO (5 agentes em paralelo, condicional)
   |-- Injection Exploit --> injection_exploitation_evidence.md
   |-- XSS Exploit --> xss_exploitation_evidence.md
   |-- Auth Exploit --> auth_exploitation_evidence.md
   |-- Authz Exploit --> authz_exploitation_evidence.md
   |-- SSRF Exploit --> ssrf_exploitation_evidence.md
        |
Fase 5: RELATORIO (Sequencial)
   - Compilacao de evidencias validadas
   - Deliverable: comprehensive_security_assessment_report.md
```

**Politica "No Exploit, No Report"**: Se uma vulnerabilidade hipotetica nao puder ser explorada com sucesso, ela e descartada como falso positivo.

---

## 3. Estrutura do Codigo-Fonte

### 3.1 Diretorios Principais

```
shannon/
├── src/                          # Codigo-fonte TypeScript (~9.700 linhas)
│   ├── ai/                       # Integracao com Claude Agent SDK
│   │   ├── claude-executor.ts    # Execucao do SDK com retry e streaming
│   │   ├── message-handlers.ts   # Processamento de mensagens do SDK
│   │   ├── output-formatters.ts  # Formatacao de saida
│   │   ├── progress-manager.ts   # Indicadores de progresso
│   │   ├── router-utils.ts       # Suporte a multi-modelo (experimental)
│   │   └── types.ts              # Tipos da camada AI
│   ├── services/                 # Camada de logica de negocios (sem dependencia do Temporal)
│   │   ├── agent-execution.ts    # Ciclo de vida completo do agente
│   │   ├── config-loader.ts      # Carregamento de configuracao
│   │   ├── container.ts          # Container DI por workflow
│   │   ├── error-handling.ts     # Tratamento de erros
│   │   ├── exploitation-checker.ts # Decisao de executar exploits
│   │   ├── git-manager.ts        # Checkpoints via Git
│   │   ├── preflight.ts          # Validacao pre-execucao
│   │   ├── prompt-manager.ts     # Sistema de templates de prompts
│   │   ├── queue-validation.ts   # Validacao de filas de vulnerabilidades
│   │   └── reporting.ts          # Pipeline de geracao de relatorio
│   ├── temporal/                 # Orquestracao Temporal
│   │   ├── workflows.ts          # Workflow principal (pentestPipelineWorkflow)
│   │   ├── activities.ts         # Wrappers de atividades (heartbeat + classificacao de erro)
│   │   ├── client.ts             # Cliente CLI para iniciar workflows
│   │   ├── worker.ts             # Worker que executa atividades
│   │   ├── shared.ts             # Tipos compartilhados
│   │   ├── workspaces.ts         # Gerenciamento de workspaces
│   │   └── workflow-errors.ts    # Formatacao de erros do workflow
│   ├── audit/                    # Sistema de auditoria e logging
│   │   ├── audit-session.ts      # Sessao de auditoria (facade principal)
│   │   ├── workflow-logger.ts    # Log unificado por workflow
│   │   ├── metrics-tracker.ts    # Rastreamento de custos e metricas
│   │   └── log-stream.ts         # Primitiva de stream compartilhada
│   ├── types/                    # Tipos TypeScript consolidados
│   │   ├── agents.ts             # AgentName, AgentDefinition
│   │   ├── result.ts             # Result<T,E> para propagacao explicita de erro
│   │   ├── errors.ts             # ErrorCode enum
│   │   └── config.ts             # Tipos de configuracao
│   └── utils/                    # Utilitarios compartilhados
├── prompts/                      # Templates de prompt para cada agente
│   ├── shared/                   # Partials compartilhadas (@include)
│   └── pipeline-testing/         # Prompts minimos para teste rapido
├── mcp-server/                   # Servidor MCP (ferramentas para agentes)
│   └── src/tools/                # save_deliverable, generate_totp
├── configs/                      # Configuracoes YAML + JSON Schema
├── audit-logs/                   # Logs de auditoria (gerados em runtime)
├── repos/                        # Repositorios-alvo (colocados pelo usuario)
├── sample-reports/               # Relatorios de exemplo (Juice Shop, crAPI, cAPItal)
├── xben-benchmark-results/       # Resultados de benchmark XBOW
├── shannon                       # CLI Bash (ponto de entrada)
├── docker-compose.yml            # Orquestracao de servicos
├── Dockerfile                    # Build multi-estagio
└── package.json                  # Dependencias Node.js
```

### 3.2 Modulos-Chave

#### `src/session-manager.ts` - Registro Central de Agentes
- Define os **13 agentes** com seus metadados (nome, prompt template, deliverable)
- Mapeia agentes para instancias do Playwright (5 instancias paralelas)
- Define validadores por agente (verificacao de existencia de deliverables)

#### `src/ai/claude-executor.ts` - Motor de Execucao IA
- Integra o Claude Agent SDK via funcao `query()`
- Configura servidores MCP (shannon-helper + Playwright)
- Streaming de mensagens com contagem de turnos e rastreamento de custo
- **Defesa contra spending cap**: Detecta se custo=0 apesar de turnos > 2
- Validacao de output pos-execucao

#### `src/services/agent-execution.ts` - Ciclo de Vida do Agente
Executa um agente completo em 9 passos:
1. Carregar configuracao
2. Carregar template de prompt
3. Criar checkpoint Git
4. Iniciar logging de auditoria
5. Executar agente via Claude SDK
6. Verificar spending cap
7. Validar output
8. Commit Git (sucesso) ou rollback (falha)
9. Registrar metricas

#### `src/temporal/workflows.ts` - Orquestrador Principal
- Define o DAG (grafo aciclico dirigido) do pipeline
- Suporta **resume/checkpointing** (pula agentes ja completos)
- Execucao paralela com limite de concorrencia configuravel
- Multiplos presets de retry (producao, teste, subscription)

---

## 4. Sistema de Prompts

### 4.1 Estrutura

Cada agente recebe um prompt elaborado contendo:
1. **Definicao de papel** - Especialidade e expertise do agente
2. **Objetivo** - Criterio de sucesso
3. **Escopo/Alvo/Regras** - Via diretivas `@include`
4. **Padroes criticos** - Expectativas de rigor profissional
5. **Ferramentas disponiveis** - MCP, bash, Playwright, TodoWrite
6. **Metodologia** - Procedimento detalhado de analise/exploracao
7. **Instrucoes de deliverable** - Formato e estrutura exigidos

### 4.2 Variaveis de Template

```
{{WEB_URL}}              - URL alvo
{{REPO_PATH}}            - Caminho do repositorio
{{MCP_SERVER}}           - Caminho do servidor MCP
{{CONFIG_CONTEXT}}       - Contexto de configuracao
{{LOGIN_INSTRUCTIONS}}   - Fluxo de login
{{RULES_AVOID}}          - Regras de areas a evitar
{{RULES_FOCUS}}          - Regras de areas a focar
```

### 4.3 Partials Compartilhadas

- `_target.txt` - Informacoes basicas do alvo
- `_rules.txt` - Regras de teste (avoid/focus)
- `_vuln-scope.txt` - Definicao de vulnerabilidades em escopo
- `_exploit-scope.txt` - Fronteira de explorabilidade externa
- `login-instructions.txt` - Templates de fluxo de login (form, SSO, API)

---

## 5. Servidor MCP (Model Context Protocol)

O servidor MCP fornece ferramentas para os agentes AI:

### `save_deliverable`
- Salva arquivos de evidencias e analises de vulnerabilidades
- Suporta 10 tipos de deliverables (CODE_ANALYSIS, RECON, queues, etc.)
- Valida estrutura JSON de filas de vulnerabilidades
- Protecao contra path traversal

### `generate_totp`
- Gera codigos TOTP para autenticacao 2FA
- Compativel com RFC 6238 (TOTP) e RFC 4226 (HOTP)
- Retorna codigo de 6 digitos + segundos ate expiracao

---

## 6. Infraestrutura Docker

### Dockerfile (Build Multi-Estagio)
1. **Estagio Builder**: Compila ferramentas de seguranca (subfinder, WhatWeb, Chromium)
2. **Estagio Runtime**: Imagem minima Chainguard Wolfi, usuario nao-root (UID 1001)

### Docker Compose (3 Servicos)
1. **temporal** - Servidor Temporal (gRPC:7233, WebUI:8233) com SQLite
2. **worker** - Container Shannon com volumes para configs, prompts, repos, logs
3. **router** (opcional) - claude-code-router para suporte multi-modelo

---

## 7. Cobertura de Vulnerabilidades

Shannon Lite cobre as seguintes classes de vulnerabilidades **exploraveis**:

| Categoria | Tipos Especificos |
|-----------|-------------------|
| **Injection** | SQLi, Command Injection, LFI, RFI, SSTI, Path Traversal |
| **XSS** | Reflected, Stored, DOM-based |
| **Auth** | Bypass de autenticacao, JWT attacks, TOTP bypass |
| **Authz** | IDOR, escalacao de privilegios, BOLA/BFLA |
| **SSRF** | Server-Side Request Forgery, reconhecimento interno |

### Resultados Demonstrados
- **OWASP Juice Shop**: 20+ vulnerabilidades criticas (auth bypass completo, exfiltracao de DB)
- **cAPItal API**: ~15 vulnerabilidades criticas (injection root-level, mass assignment)
- **OWASP crAPI**: 15+ vulnerabilidades (JWT attacks, SSRF, database compromise)
- **Benchmark XBOW**: 96.15% taxa de sucesso (hint-free, source-aware)

---

## 8. Padroes de Design Notaveis

| Padrao | Implementacao | Beneficio |
|--------|--------------|-----------|
| **Temporal Workflows** | Orquestracao duravel com DAG | Resume, retry, crash recovery |
| **DI Container** | Per-workflow scoping em `container.ts` | Testabilidade, loose coupling |
| **Result\<T,E\>** | Propagacao explicita de erros | Sem excecoes silenciosas |
| **Git Checkpointing** | Commit pre/pos agente | Rollback seguro em falha |
| **MCP Servers** | Shannon-helper + Playwright | Ferramentas modulares para agentes |
| **Spending Cap Defense** | Deteccao em 3 camadas | Protecao contra custos inesperados |
| **Services Boundary** | Activities sao wrappers finos | Logica de negocios testavel sem Temporal |
| **Queue-Driven Pipeline** | JSON queues entre fases | Auditoria, resume, decisoes condicionais |

---

## 9. Dependencias Principais

```json
{
  "@anthropic-ai/claude-agent-sdk": "^0.2.38",   // Motor AI principal
  "@temporalio/client": "^1.11.0",                 // Orquestracao de workflows
  "@temporalio/worker": "^1.11.0",                 // Execucao de atividades
  "@temporalio/workflow": "^1.11.0",               // Definicao de workflows
  "ajv": "^8.12.0",                                // Validacao JSON Schema
  "js-yaml": "^4.1.0",                             // Parsing YAML
  "zx": "^8.0.0",                                  // Shell scripting
  "dotenv": "^16.4.5"                              // Variaveis de ambiente
}
```

---

## 10. Custos e Performance

- **Tempo de execucao**: 1 a 1.5 horas por teste completo
- **Custo estimado**: ~$50 USD por execucao (usando Claude 4.5 Sonnet)
- **Concorrencia**: Ate 5 pipelines paralelos (configuravel)
- **Retry**: Multiplos presets (producao: 5-30min backoff, subscription: ate 6h backoff)

---

## 11. Pontos Fortes

1. **Arquitetura robusta** - Temporal garante durabilidade, resume e retry inteligente
2. **Pipeline bem definido** - 5 fases que emulam metodologia real de pentest
3. **Proof-by-exploitation** - Elimina falsos positivos ao exigir exploits reais
4. **Paralelismo eficiente** - 5 especialistas de vuln e 5 de exploit em paralelo
5. **Sistema de auditoria completo** - Logs detalhados, metricas, checkpoints Git
6. **Configuracao flexivel** - YAML com JSON Schema, suporte 2FA/TOTP, regras avoid/focus
7. **Workspaces e resume** - Retoma de onde parou sem re-executar agentes completos
8. **Separacao services/temporal** - Logica de negocios testavel independentemente
9. **Benchmark publico** - 96.15% no XBOW (transparencia de resultados)

---

## 12. Pontos de Atencao

1. **Dependencia forte do Anthropic Claude** - Modo router (OpenAI/Gemini) e experimental e nao suportado
2. **Custo elevado** - ~$50 USD por execucao pode ser proibitivo para uso frequente
3. **White-box apenas** - Requer acesso ao codigo-fonte (nao faz black-box testing puro)
4. **Cobertura limitada** - 5 categorias OWASP; nao cobre CSRF, XXE, desserializacao insegura, etc.
5. **Sem contribuicoes externas** - PRs nao sao aceitos (apenas issues)
6. **Verificacao humana necessaria** - LLMs podem gerar conteudo alucinado nos relatorios
7. **Nao usar em producao** - Exploits ativos podem modificar dados e criar usuarios
8. **Tempo de execucao longo** - 1-1.5h por teste completo

---

## 13. Conclusao

Shannon e um projeto **inovador e bem arquitetado** que traz automacao de pentesting alimentada por IA para um nivel pratico. A combinacao de analise white-box de codigo com exploracao dinamica real, orquestrada por Temporal e alimentada pelo Claude Agent SDK, cria uma ferramenta que vai alem de scanners tradicionais ao fornecer **provas concretas de vulnerabilidades exploraveis**.

O projeto e especialmente relevante para equipes que usam desenvolvimento assistido por IA (Claude Code, Cursor, Copilot) e precisam de validacao de seguranca continua entre pentests anuais formais. A politica "No Exploit, No Report" e a abordagem de minimizacao de falsos positivos tornam os relatorios acionaveis e confiaveis.

A arquitetura baseada em Temporal com DI container, checkpointing Git e sistema de workspaces demonstra maturidade de engenharia significativa para um projeto com apenas ~5 meses de historia (outubro 2025 - fevereiro 2026).
