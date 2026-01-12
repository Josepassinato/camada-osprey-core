# 🚨 REGRAS JURÍDICAS DE IMIGRAÇÃO - IMPLEMENTAÇÃO

## Visão Geral

Este documento descreve as **regras jurídicas obrigatórias** implementadas no sistema, fornecidas por **advogado especialista em imigração**. Estas regras substituem quaisquer comportamentos anteriores conflitantes e devem ser aplicadas imediatamente em todos os fluxos de validação.

---

## 📋 Regras Implementadas por Tipo de Visto

### 🟦 VISTO DE ESTUDANTE (F-1)

#### Requisitos Obrigatórios:
1. ✅ **Proficiência em Inglês**
   - TOEFL, IELTS, Duolingo ou certificado equivalente
   - **Bloqueio**: Sistema não permite prosseguir sem comprovação

2. ✅ **I-20 Emitido**
   - Documento deve estar emitido pela instituição
   - **Bloqueio**: Sistema não permite prosseguir sem I-20

3. ✅ **Taxa SEVIS Paga**
   - Confirmação de pagamento obrigatória
   - **Bloqueio**: Sistema não permite prosseguir sem pagamento

#### Regras de Trabalho:
- ✅ **On-Campus**: Permitido até 20h/semana
- ❌ **Off-Campus**: NÃO permitido (exceto casos específicos)
- ✅ **OPT**: Permitido após conclusão do curso

#### Alertas Críticos:
- 🚨 **Viagem**: Sair dos EUA durante processo ANULA o pedido
- ⏰ **Mudança B2→F1**: Apenas após 90 dias da entrada nos EUA

---

### 🟦 AJUSTE DE STATUS (CASAMENTO)

#### Requisitos:
1. ✅ Deve estar **fisicamente nos EUA**
2. ✅ **Entrada legal** (B2, F1, etc.)
3. ✅ Casamento válido comprovado

#### Formulários Obrigatórios:
- ✅ I-130: Petição para Parente Estrangeiro
- ✅ I-130A: Informações Suplementares
- ✅ I-485: Aplicação para Registro de Residência Permanente
- ✅ I-864: Affidavit of Support

#### Formulários Opcionais (Recomendados):
- 💡 I-765: Autorização de Trabalho (EAD)
- 💡 I-131: Advance Parole (Permissão de Viagem)

#### Importante:
- ✅ **Concurrent Filing**: Envio conjunto permitido
- ❌ **Não Consular**: Este processo é apenas para quem está nos EUA

---

### 🟦 RENOVAÇÃO DE GREEN CARD

#### Timing:
- ✅ **Antecedência**: Até 6 meses antes do vencimento
- ⚠️ **Vencido**: Pode renovar, mas com alertas sobre viagem
- ❌ **Muito Cedo**: Bloqueado se mais de 6 meses para vencer

#### Alertas:
- Se vencido: Aviso sobre dificuldades em viagens internacionais
- Sistema calcula automaticamente janela de renovação

---

### 🟦 EXTENSÃO DE STATUS (B-2)

#### Requisitos de Timing:
- ⏰ **90 dias mínimos**: Desde a entrada nos EUA
- **Bloqueio**: Sistema não permite antes de 90 dias

#### Restrições:
- ❌ **ESTA**: Não pode ser estendido (alerta automático)
- ⏱️ **Duração**: Extensão padrão de 6 meses
- 🚨 **Viagem**: Sair dos EUA CANCELA o processo

---

### 🟦 REINSTATEMENT F-1

#### Aplicável Para:
- Estudantes cujo status F1 foi **encerrado pela escola**

#### Requisitos Obrigatórios:
1. ✅ Novo I-20 da escola
2. ✅ I-20 deve indicar "**Reinstatement**"
3. ✅ Formulário I-539
4. ⚠️ Retornar às aulas IMEDIATAMENTE

#### Bloqueios:
- Sistema verifica se status anterior era F1
- Exige motivo do encerramento
- Valida existência de novo I-20

---

## 📑 DOCUMENTAÇÃO OBRIGATÓRIA (Todos os Casos)

### Documentos Principais:
1. ✅ **Passaporte**
   - Alerta se vencido (pode continuar)
   - Alerta se vence em < 6 meses

2. ✅ **Visto Atual** (cópia)

3. ✅ **I-94**
   - Download em: https://i94.cbp.dhs.gov/
   - Data de vencimento obrigatória

4. ✅ **Extrato Bancário**
   - Últimos 3 meses
   - **Traduzido** para inglês

5. ✅ **Vínculos com Brasil**
   - Contas, CNPS, IR, propriedades
   - **Traduzidos** para inglês

### Com Dependentes:
Para cada dependente, adicionar:
- ✅ Passaporte
- ✅ Visto
- ✅ I-94
- ✅ Certidão de nascimento/casamento (**traduzida**)

### Fotos:
- ✅ 2 fotos padrão passaporte **por pessoa**
- Formato: 5x5 cm, fundo branco

---

## 🚨 REGRA UNIVERSAL: VIAGEM DURANTE PROCESSOS

### Regra Geral:
❌ **NUNCA** sair dos EUA durante processos ativos

### Exceção:
✅ Com **Advance Parole** (I-131) aprovado

### Consequências:
- Cancelamento automático do pedido
- Possível dificuldade para retornar aos EUA
- Perda de taxas pagas

### Implementação no Sistema:
- Alerta crítico exibido se usuário indicar planos de viagem
- Bloqueio em alguns processos (F1, B2)
- Verificação de Advance Parole

---

## 🔧 IMPLEMENTAÇÃO TÉCNICA

### Arquivo Principal:
```
/app/backend/immigration_legal_rules.py
```

### Classe:
```python
class ImmigrationLegalRules
```

### Métodos Disponíveis:
1. `validate_f1_student_visa(form_data)`
2. `validate_adjustment_of_status_marriage(form_data)`
3. `validate_green_card_renewal(form_data)`
4. `validate_status_extension_b2(form_data)`
5. `validate_f1_reinstatement(form_data)`
6. `validate_mandatory_documents(form_data, visa_type)`
7. `validate_travel_during_process(form_data, process_type)`

### Função Helper:
```python
apply_legal_rules(form_data: Dict, visa_type: str) -> Tuple[bool, List[str]]
```

### Integração:
- ✅ Integrado em `/api/case/{case_id}/friendly-form`
- ✅ Validação executada ANTES da validação por IA
- ✅ Resultados salvos no banco de dados
- ✅ Mensagens retornadas ao frontend

---

## 📊 FORMATO DE RESPOSTA

### Tipos de Mensagens:
1. **❌ ERRO CRÍTICO**: Bloqueia prosseguimento
2. **⚠️ AVISO**: Permite continuar com alerta
3. **💡 RECOMENDAÇÃO**: Informação útil
4. **✅ CONFIRMAÇÃO**: Validação positiva

### Severidades:
- `critical`: Bloqueia processo
- `warning`: Alerta importante
- `info`: Informação adicional

### Estrutura JSON:
```json
{
  "field": "legal_requirement",
  "issue": "❌ OBRIGATÓRIO: Prova de proficiência em inglês",
  "severity": "critical",
  "type": "legal_rule"
}
```

---

## 🔄 FLUXO DE VALIDAÇÃO

```
1. Usuário submete formulário
   ↓
2. VALIDAÇÃO JURÍDICA (immigration_legal_rules.py)
   - Aplica regras por tipo de visto
   - Verifica documentação obrigatória
   - Valida timing e elegibilidade
   ↓
3. VALIDAÇÃO IA (validate_friendly_form_ai)
   - Verifica completude
   - Analisa coerência
   ↓
4. MERGE DE RESULTADOS
   - Combina validações jurídicas + IA
   - Prioriza regras jurídicas
   ↓
5. RESPOSTA AO USUÁRIO
   - Lista completa de issues
   - Status geral
   - Próximos passos
```

---

## ⚠️ AVISOS IMPORTANTES

### Para Desenvolvedores:
1. ⚠️ **Nunca ignorar regras jurídicas**
2. ⚠️ **Não modificar sem consultar advogado**
3. ⚠️ **Prioridade sobre validações de IA**
4. ⚠️ **Testar mudanças extensivamente**

### Para Usuários:
1. ⚠️ Estas regras são baseadas em lei de imigração dos EUA
2. ⚠️ Violá-las pode resultar em negação de visto
3. ⚠️ Sempre consulte um advogado para casos complexos
4. ⚠️ Sistema não substitui consultoria jurídica

---

## 📞 SUPORTE

Para dúvidas sobre:
- **Regras jurídicas**: Consultar advogado de imigração
- **Implementação técnica**: Equipe de desenvolvimento
- **Bugs/Issues**: Abrir ticket no sistema

---

## 📝 CHANGELOG

### v1.0.0 - Dezembro 2024
- ✅ Implementação inicial de todas as regras
- ✅ Integração com endpoint de validação
- ✅ Documentação completa
- ✅ Testes de validação por tipo de visto

---

## ✅ STATUS DA IMPLEMENTAÇÃO

- [x] Regras jurídicas implementadas
- [x] Integração com server.py
- [x] Validação por tipo de visto
- [x] Documentação obrigatória
- [x] Alertas de viagem
- [x] Timing e elegibilidade
- [x] Mensagens em português
- [ ] Testes automatizados (próximo passo)
- [ ] Frontend UI para alertas (próximo passo)

---

**Última Atualização**: 07 de Dezembro de 2024  
**Status**: ✅ **ATIVO E OBRIGATÓRIO**
