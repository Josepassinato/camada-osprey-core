# Archive - Código Legado

Esta pasta contém código que foi movido do diretório principal para manter o projeto organizado.

## 📁 Estrutura

### old_generators/
Contém 14 scripts de geração de pacotes antigos e duplicados.
**Mantido no projeto principal:** `generate_final_perfect_package.py` (o mais completo e recente)

### old_tests/
Contém 54 arquivos de teste antigos, scripts de debug e testes diversos.
Scripts movidos incluem:
- test_*.py (vários testes unitários e de integração antigos)
- comprehensive_*.py (testes abrangentes antigos)
- *_test.py (testes diversos)

### debug_scripts/
Contém 10 scripts de debug e investigação.
Inclui:
- debug_*.py (scripts de debugging)
- investigate_*.py (scripts de investigação)
- Scripts utilitários de desenvolvimento

## 🎯 Motivo da Limpeza

O projeto tinha **85 arquivos Python** no root, com muita duplicação:
- 16 geradores de pacotes fazendo basicamente a mesma coisa
- 50+ arquivos de teste espalhados
- Múltiplos scripts de debug

Após a limpeza: **9 arquivos principais** no root.

## ♻️ Restauração

Se precisar de algum arquivo:
1. Localize-o na pasta apropriada (old_generators, old_tests, ou debug_scripts)
2. Copie de volta para /app/
3. Atualize imports se necessário

## 📅 Data da Limpeza

Novembro 20, 2024

## ✅ Arquivos Mantidos no Projeto Principal

Arquivos essenciais que permaneceram no /app/:
1. **h1b_data_model.py** - Modelo de dados centralizado
2. **document_image_generator.py** - Gerador de imagens de documentos
3. **knowledge_base_integration.py** - Integração com base de conhecimento
4. **official_forms_repository.py** - Repositório de formulários oficiais
5. **simulated_case_data.py** - Dados de caso simulado
6. **fill_official_i129.py** - Preenchimento de formulários
7. **generate_filled_forms.py** - Geração de formulários preenchidos
8. **generate_final_perfect_package.py** - Gerador principal (mais recente e completo)
9. **extract_and_organize_all.py** - Script de organização da base de conhecimento
