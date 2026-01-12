# 📋 Repositório de Formulários Oficiais USCIS

## Visão Geral

Este sistema mantém uma biblioteca local de todos os formulários oficiais do USCIS para cada tipo de visto. Os formulários são baixados uma vez e armazenados localmente, garantindo velocidade e disponibilidade.

## 📁 Estrutura

```
/app/official_forms/
├── uscis_forms/              # Formulários oficiais baixados
│   ├── i-129.pdf            # Form I-129 (H-1B)
│   ├── eta-9035-lca.pdf     # LCA (H-1B)
│   ├── i-539.pdf            # Change of Status
│   ├── i-485.pdf            # Green Card
│   └── ...
└── guides/                   # Guias e checklists (do toolkit)
    ├── I-129_Completion_Guide.docx
    ├── Supporting_Document_Checklist.docx
    └── ...
```

## 🎯 Formulários Disponíveis

### H-1B
- ✅ **I-129** - Petition for a Nonimmigrant Worker (20 páginas)
- ✅ **LCA (ETA-9035)** - Labor Condition Application (10 páginas)
- ⚠️ **I-129-H** - H Classification Supplement (URL desatualizada, precisa atualizar)

### F-1
- ⚠️ **I-20** - Emitido pela escola (não baixável)
- ✅ **I-539** - Change/Extend Status (12 páginas)

### Green Card
- ✅ **I-485** - Application to Register Permanent Residence (18 páginas)
- ✅ **I-130** - Petition for Alien Relative (12 páginas)
- ✅ **I-140** - Immigrant Petition for Alien Workers (8 páginas)
- ✅ **I-864** - Affidavit of Support (11 páginas)

### Citizenship
- ✅ **N-400** - Application for Naturalization (21 páginas)

## 💻 Uso do Sistema

### Python API

```python
from official_forms_repository import OfficialFormsRepository

# Criar instância
repo = OfficialFormsRepository()

# Buscar formulário específico
i129_path = repo.get_form("H-1B", "I-129")
# Retorna: /app/official_forms/uscis_forms/i-129.pdf

# Listar formulários obrigatórios
required = repo.get_required_forms_for_visa("H-1B")
# Retorna lista com I-129, I-129-H, LCA

# Baixar todos os formulários para um visto
repo.download_all_forms_for_visa("Green_Card")
```

### Integração no Gerador de Pacotes

```python
from official_forms_repository import OfficialFormsRepository

repo = OfficialFormsRepository()

# Buscar I-129 oficial
official_i129 = repo.get_form("H-1B", "I-129")

# Usar no pacote
merger = PdfWriter()
i129_reader = PdfReader(official_i129)
for page in i129_reader.pages:
    merger.add_page(page)
```

## 🚀 Vantagens

1. **Velocidade** ⚡
   - Formulários baixados uma vez
   - Acesso instantâneo em gerações futuras
   - Sem dependência de rede após download inicial

2. **Confiabilidade** 🛡️
   - Cópias locais sempre disponíveis
   - Não depende do site do USCIS estar online
   - Versões consistentes

3. **Organização** 📚
   - Catálogo centralizado de todos os formulários
   - Mapeamento por tipo de visto
   - Metadados completos (páginas, URLs, etc.)

4. **Manutenção** 🔧
   - Fácil adicionar novos formulários
   - URLs atualizáveis via código
   - Versionamento possível

## 📥 Downloads Automáticos

O sistema tenta baixar de múltiplas fontes:

1. **URL Direta** (preferencial)
   ```
   https://www.reginfo.gov/public/do/DownloadDocument?objectID=4578401
   ```

2. **URL do USCIS** (fallback)
   ```
   https://www.uscis.gov/sites/default/files/document/forms/i-129.pdf
   ```

3. **Cache Local** (se já existe)
   ```
   /app/official_forms/uscis_forms/i-129.pdf
   ```

## 🔄 Atualização de Formulários

Quando o USCIS lança uma nova versão:

```python
# 1. Deletar versão antiga
os.remove("/app/official_forms/uscis_forms/i-129.pdf")

# 2. Atualizar URL no código (se mudou)
FORMS_CATALOG["H-1B"]["I-129"]["url"] = "nova_url"

# 3. Baixar nova versão
repo.get_form("H-1B", "I-129")
```

## 📊 Estatísticas Atuais

- **Total de formulários catalogados**: 11
- **Formulários baixados**: 2 (I-129, LCA)
- **Espaço usado**: ~1 MB
- **Tipos de visto suportados**: 5

## 🎯 Roadmap

- [ ] Adicionar mais formulários (I-765, I-94, etc.)
- [ ] Sistema de versionamento
- [ ] Cache com TTL (atualização automática)
- [ ] Validação de integridade (checksum)
- [ ] Download paralelo de múltiplos formulários
- [ ] Dashboard web para gerenciamento

## 📞 Suporte

Para adicionar novos formulários ou reportar problemas, consulte:
- USCIS Forms: https://www.uscis.gov/forms
- DOL Forms: https://www.dol.gov/agencies/eta/foreign-labor/forms
