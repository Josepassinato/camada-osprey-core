# Visa Specialists - Multi-Agent Architecture

## 🎯 Overview

Arquitetura multi-agente onde cada agente é especializado em um tipo específico de visto de imigração.

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│  SUPERVISOR AGENT (Orquestrador)        │
│  - Analisa demanda do usuário           │
│  - Identifica tipo de visto             │
│  - Delega para especialista correto     │
│  - Valida resultado final               │
└─────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┬───────────┐
        ▼           ▼           ▼           ▼
    ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐
    │ H-1B │   │ B-2  │   │ F-1  │   │ GC   │
    │Expert│   │Expert│   │Expert│   │Expert│
    └──────┘   └──────┘   └──────┘   └──────┘
```

## 📁 Structure

```
visa_specialists/
├── base_agent.py          # Classe base para todos os agentes
├── supervisor/
│   └── supervisor_agent.py # Orquestrador principal
├── b2_extension/          # Especialista B-2
│   ├── b2_agent.py
│   ├── knowledge_base/
│   ├── templates/
│   ├── checklist.json
│   └── lessons_learned.md
├── h1b_worker/            # Especialista H-1B
│   ├── h1b_agent.py
│   ├── knowledge_base/
│   ├── templates/
│   ├── checklist.json
│   └── lessons_learned.md
└── f1_student/            # Especialista F-1
    ├── f1_agent.py
    ├── knowledge_base/
    ├── templates/
    ├── checklist.json
    └── lessons_learned.md
```

## 🚀 Usage

```python
from visa_specialists import SupervisorAgent
from visa_specialists.b2_extension.b2_agent import B2ExtensionAgent

# Criar supervisor
supervisor = SupervisorAgent()

# Registrar especialistas
b2_agent = B2ExtensionAgent()
supervisor.register_specialist('B-2', b2_agent)

# Processar requisição
user_input = "Preciso estender meu visto de turista B-2 por motivos médicos"
applicant_data = {...}

result = supervisor.process_request(user_input, applicant_data)
```

## ✅ Benefits

1. **Especialização**: Cada agente domina um tipo de visto
2. **Prevenção de Erros**: Validação cruzada evita documentos errados
3. **Manutenibilidade**: Código isolado e organizado
4. **Escalabilidade**: Fácil adicionar novos tipos de visto
5. **Learning System**: Cada agente aprende com erros anteriores

## 📝 Lessons Learned System

Cada agente mantém um arquivo `lessons_learned.md` que registra:
- ❌ Erros cometidos
- ✅ Correções aplicadas
- 📝 Melhores práticas

Próximas gerações de agentes leem estas lições e evitam repetir erros.

## 🔒 Validation

Cada agente tem:
- **REQUIRED_FORMS**: Formulários obrigatórios
- **REQUIRED_DOCUMENTS**: Documentos necessários
- **FORBIDDEN_DOCUMENTS**: Documentos que NÃO devem ser incluídos

O supervisor valida que o pacote gerado está correto.
