"""
Sistema de Aprendizado Iterativo para Geração de Pacotes de Imigração

FLUXO:
1. Agente Gerador cria pacote inicial
2. Agente Revisor analisa e REJEITA com instruções detalhadas
3. Agente Gerador APRENDE com as instruções e cria versão melhorada
4. Ciclo continua até APROVAÇÃO (score >= 95%, zero erros críticos)

O revisor atua como um "senior attorney" ensinando agentes júnior
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import sys

sys.path.insert(0, '/app')

from backend.immigration_compliance_reviewer import ImmigrationComplianceReviewer
from h1b_data_model import h1b_data


class IterativeLearningSystem:
    """
    Sistema que coordena o aprendizado iterativo entre revisor e geradores
    """
    
    def __init__(self, visa_type: str = "H-1B", max_iterations: int = 5):
        """
        Args:
            visa_type: Tipo de visto
            max_iterations: Número máximo de iterações antes de desistir
        """
        self.visa_type = visa_type
        self.max_iterations = max_iterations
        self.reviewer = ImmigrationComplianceReviewer(visa_type=visa_type, h1b_data_model=h1b_data)
        
        # Arquivo para armazenar lições aprendidas
        self.lessons_file = f"/app/immigration_lessons_{visa_type.lower().replace('-', '_')}.json"
        self.lessons = self._load_lessons()
        
        # Histórico de iterações
        self.iteration_history = []
    
    def _load_lessons(self) -> Dict:
        """Carrega lições aprendidas de iterações anteriores"""
        if os.path.exists(self.lessons_file):
            with open(self.lessons_file, 'r') as f:
                return json.load(f)
        return {
            "total_iterations": 0,
            "successful_approvals": 0,
            "common_errors": {},
            "correction_instructions": [],
            "best_practices": []
        }
    
    def _save_lessons(self):
        """Salva lições aprendidas"""
        with open(self.lessons_file, 'w') as f:
            json.dump(self.lessons, f, indent=2)
    
    def generate_detailed_correction_instructions(self, review_result: Dict) -> List[str]:
        """
        Gera instruções DETALHADAS de correção baseadas nos erros encontrados
        
        O revisor não apenas diz "falta documento X", mas ensina COMO adicionar corretamente
        """
        instructions = []
        
        print(f"\n{'='*80}")
        print(f"📚 GERANDO INSTRUÇÕES DE CORREÇÃO DETALHADAS")
        print(f"{'='*80}")
        
        # Instruções para erros críticos
        if review_result.get('critical_errors'):
            instructions.append("=" * 80)
            instructions.append("🔴 ERROS CRÍTICOS - CORREÇÃO OBRIGATÓRIA:")
            instructions.append("=" * 80)
            
            for i, error in enumerate(review_result['critical_errors'], 1):
                instructions.append(f"\n{i}. {error}")
                
                # Gerar instrução específica baseada no tipo de erro
                if "FORMULÁRIO OBRIGATÓRIO AUSENTE" in error:
                    form_name = error.split(": ")[-1]
                    instruction = self._generate_form_instruction(form_name)
                    instructions.append(f"   INSTRUÇÃO: {instruction}")
                
                elif "DOCUMENTO CRÍTICO AUSENTE" in error:
                    doc_name = error.split(": ")[-1]
                    instruction = self._generate_document_instruction(doc_name)
                    instructions.append(f"   INSTRUÇÃO: {instruction}")
                
                elif "LCA - Campo obrigatório ausente" in error:
                    field_name = error.split(": ")[-1]
                    instruction = self._generate_lca_field_instruction(field_name)
                    instructions.append(f"   INSTRUÇÃO: {instruction}")
                
                elif "PASSAPORTE EXPIRADO" in error:
                    instructions.append(f"   INSTRUÇÃO: Solicitar ao usuário renovação do passaporte. "
                                      f"O passaporte deve ser válido por pelo menos 6 meses além da data de término da estadia pretendida.")
        
        # Instruções para erros maiores
        if review_result.get('major_errors'):
            instructions.append("\n" + "=" * 80)
            instructions.append("🟡 ERROS MAIORES - CORREÇÃO RECOMENDADA:")
            instructions.append("=" * 80)
            
            for i, error in enumerate(review_result['major_errors'], 1):
                instructions.append(f"\n{i}. {error}")
                
                if "Documento obrigatório ausente" in error:
                    doc_name = error.split(": ")[-1]
                    instruction = self._generate_document_instruction(doc_name)
                    instructions.append(f"   INSTRUÇÃO: {instruction}")
                
                elif "Conteúdo repetitivo detectado" in error:
                    instructions.append(f"   INSTRUÇÃO: Cada seção do pacote deve ter conteúdo ÚNICO e contextual. "
                                      f"Evite usar templates genéricos. Cada página deve conter informações específicas "
                                      f"e relevantes para aquela seção (ex: Cover Letter com narrativa única, "
                                      f"Form I-129 com campos específicos, Resume com experiências detalhadas).")
                
                elif "Seções faltando" in error:
                    instructions.append(f"   INSTRUÇÃO: Adicione todas as seções obrigatórias do formulário. "
                                      f"Consulte a versão oficial mais recente do formulário no site do USCIS.")
        
        # Resumo de ações necessárias
        instructions.append("\n" + "=" * 80)
        instructions.append("📋 RESUMO DE AÇÕES NECESSÁRIAS:")
        instructions.append("=" * 80)
        
        critical_count = len(review_result.get('critical_errors', []))
        major_count = len(review_result.get('major_errors', []))
        
        instructions.append(f"\n✓ Corrigir {critical_count} erros críticos (OBRIGATÓRIO)")
        instructions.append(f"✓ Corrigir {major_count} erros maiores (RECOMENDADO)")
        instructions.append(f"✓ Score atual: {review_result.get('compliance_score', 0)}/100")
        instructions.append(f"✓ Score necessário: 95/100")
        instructions.append(f"✓ Após correções, executar revisão novamente")
        
        # Adicionar melhores práticas aprendidas
        if self.lessons['best_practices']:
            instructions.append("\n" + "=" * 80)
            instructions.append("💡 MELHORES PRÁTICAS APRENDIDAS EM ITERAÇÕES ANTERIORES:")
            instructions.append("=" * 80)
            for practice in self.lessons['best_practices'][-5:]:  # Últimas 5
                instructions.append(f"• {practice}")
        
        return instructions
    
    def _generate_form_instruction(self, form_name: str) -> str:
        """Gera instrução específica para adicionar formulário"""
        instructions_map = {
            "H Classification Supplement": (
                "Adicione o H Classification Supplement to Form I-129 (páginas 8-9 do formulário oficial). "
                "Este suplemento DEVE incluir: (1) Tipo de classificação H (H-1B), (2) Informações sobre emprego anterior nos EUA, "
                "(3) Detalhes sobre o empregador e posição, (4) Qualificações do beneficiário. "
                "Localize o formulário oficial em: https://www.uscis.gov/i-129"
            ),
            "Form I-20": (
                "Adicione o Form I-20 (Certificate of Eligibility for Nonimmigrant Student Status) emitido pela escola. "
                "Este formulário DEVE estar: (1) Assinado pelo DSO (Designated School Official), "
                "(2) Com número SEVIS válido, (3) Com todas as informações financeiras preenchidas. "
                "O I-20 é emitido APENAS pela instituição educacional SEVP-certificada."
            ),
            "Form I-539": (
                "Adicione o Form I-539 (Application to Extend/Change Nonimmigrant Status) completo. "
                "DEVE incluir: (1) Parte 1: Informações sobre o aplicante, (2) Parte 2: Aplicação type, "
                "(3) Parte 3: Informações de processamento, (4) Parte 4: Informações adicionais, "
                "(5) Supplement A se aplicável para dependentes."
            )
        }
        
        return instructions_map.get(form_name, 
            f"Adicione o formulário {form_name}. Consulte o site oficial do USCIS para obter a versão mais recente "
            f"e preencha TODOS os campos obrigatórios.")
    
    def _generate_document_instruction(self, doc_name: str) -> str:
        """Gera instrução específica para adicionar documento"""
        instructions_map = {
            "Labor Condition Application (LCA) - CERTIFIED": (
                "Adicione o LCA CERTIFICADO pelo Department of Labor. O LCA DEVE: "
                "(1) Ter número de certificação válido (formato: I-200-XXXXX-XXXXXX), "
                "(2) Mostrar status 'CERTIFIED' claramente, "
                "(3) Incluir wage determination mostrando prevailing wage, "
                "(4) Ter data de certificação anterior à data de filing do I-129, "
                "(5) Incluir cópia do posting notice (se aplicável). "
                "Posicione o LCA certificado na seção TAB D do pacote."
            ),
            "Educational Credentials (Diploma and Transcripts)": (
                "Adicione cópias LEGÍVEIS dos diplomas e transcripts do beneficiário. DEVE incluir: "
                "(1) Diploma de Bachelor's degree (frente e verso se houver informações), "
                "(2) Diploma de Master's degree (se aplicável), "
                "(3) Transcripts oficiais completos de TODAS as instituições, "
                "(4) Se diploma estrangeiro: adicionar credential evaluation de agência NACES/AICE-approved, "
                "(5) Traduções juramentadas se documentos não estiverem em inglês. "
                "Organize na seção TAB J com identificação clara de cada documento."
            ),
            "Passport Biographical Page": (
                "Adicione cópia COLORIDA e LEGÍVEL da página biográfica do passaporte do beneficiário. "
                "DEVE mostrar: (1) Nome completo (EXATAMENTE como em outros documentos), "
                "(2) Data de nascimento, (3) Número do passaporte, "
                "(4) Data de emissão, (5) Data de EXPIRAÇÃO (deve ser válida por >6 meses), "
                "(6) País de emissão. Posicione na seção TAB K."
            ),
            "Financial Evidence (Tax Returns, Annual Reports, or Audited Financial Statements)": (
                "Adicione evidência financeira robusta do employer para demonstrar ability to pay. "
                "OPÇÕES (escolha as mais relevantes): "
                "(1) Tax Returns (Form 1120) dos últimos 2 anos, "
                "(2) Audited Financial Statements com parecer de CPA, "
                "(3) Annual Reports (para empresas públicas), "
                "(4) Bank statements mostrando fundos suficientes. "
                "A evidência DEVE demonstrar que o employer pode pagar o salário oferecido de ${salary}. "
                "Posicione na seção TAB H com análise financeira explicativa."
            ),
            "Letters of Recommendation (at least 2)": (
                "Adicione pelo menos 2 cartas de recomendação profissional. Cada carta DEVE: "
                "(1) Ser escrita por supervisor direto ou líder técnico, "
                "(2) Estar em papel timbrado da empresa, "
                "(3) Incluir nome completo, título e informações de contato do autor, "
                "(4) Descrever relacionamento profissional com o beneficiário, "
                "(5) Detalhar contribuições técnicas específicas e realizações, "
                "(6) Estar assinada e datada. "
                "Posicione na seção TAB M."
            )
        }
        
        return instructions_map.get(doc_name,
            f"Adicione o documento: {doc_name}. Certifique-se de que o documento é legível, "
            f"completo e relevante para a aplicação.")
    
    def _generate_lca_field_instruction(self, field_name: str) -> str:
        """Gera instrução para campos específicos do LCA"""
        instructions_map = {
            "Employer Name and Address": (
                "Na seção LCA, adicione CLARAMENTE: Nome legal completo do employer, "
                "endereço completo (rua, cidade, estado, ZIP), "
                "EIN (Employer Identification Number). "
                "Estes dados DEVEM ser IDÊNTICOS aos do Form I-129 Part 1."
            ),
            "Worksite Address": (
                "Na seção LCA, especifique o endereço EXATO onde o beneficiário trabalhará. "
                "Se for diferente do endereço principal do employer, isso DEVE estar documentado. "
                "Inclua: rua, número, cidade, estado, ZIP code. "
                "Este endereço determina o prevailing wage aplicável."
            )
        }
        
        return instructions_map.get(field_name,
            f"No LCA, preencha o campo: {field_name}. Este é um campo obrigatório.")
    
    def learn_from_rejection(self, review_result: Dict, instructions: List[str]):
        """Registra lições aprendidas da rejeição"""
        
        # Atualizar estatísticas de erros comuns
        for error in review_result.get('critical_errors', []):
            error_type = self._classify_error(error)
            self.lessons['common_errors'][error_type] = \
                self.lessons['common_errors'].get(error_type, 0) + 1
        
        # Adicionar instruções ao histórico
        self.lessons['correction_instructions'].append({
            'date': datetime.now().isoformat(),
            'iteration': self.lessons['total_iterations'],
            'instructions': instructions,
            'errors_count': len(review_result.get('critical_errors', [])) + 
                          len(review_result.get('major_errors', []))
        })
        
        # Manter apenas últimas 20 instruções
        if len(self.lessons['correction_instructions']) > 20:
            self.lessons['correction_instructions'] = \
                self.lessons['correction_instructions'][-20:]
        
        self._save_lessons()
    
    def _classify_error(self, error: str) -> str:
        """Classifica tipo de erro para aprendizado"""
        if "FORMULÁRIO" in error:
            return "missing_form"
        elif "DOCUMENTO" in error:
            return "missing_document"
        elif "Campo obrigatório" in error:
            return "missing_field"
        elif "EXPIRADO" in error:
            return "expired_document"
        elif "wage" in error.lower():
            return "wage_violation"
        elif "repetitivo" in error.lower():
            return "repetitive_content"
        else:
            return "other"
    
    def add_best_practice(self, practice: str):
        """Adiciona melhor prática aprendida"""
        if practice not in self.lessons['best_practices']:
            self.lessons['best_practices'].append(practice)
            self._save_lessons()
    
    def iterative_improvement_loop(self, initial_pdf_path: str, 
                                   generator_function: callable) -> Dict:
        """
        Loop de melhoria iterativa
        
        Args:
            initial_pdf_path: Caminho para o PDF inicial
            generator_function: Função que gera nova versão do pacote
                               Deve aceitar (iteration, instructions) e retornar novo PDF path
        
        Returns:
            Dict com resultado final
        """
        
        print(f"\n{'='*80}")
        print(f"🔄 INICIANDO LOOP DE APRENDIZADO ITERATIVO")
        print(f"{'='*80}")
        print(f"Visa Type: {self.visa_type}")
        print(f"Max Iterations: {self.max_iterations}")
        print(f"Lições anteriores: {self.lessons['total_iterations']} iterações registradas")
        
        current_pdf = initial_pdf_path
        
        for iteration in range(1, self.max_iterations + 1):
            print(f"\n{'='*80}")
            print(f"📍 ITERAÇÃO {iteration}/{self.max_iterations}")
            print(f"{'='*80}")
            
            # Revisar pacote atual
            print(f"\n🔍 Revisando pacote: {current_pdf}")
            review_result = self.reviewer.comprehensive_review(current_pdf)
            
            # Registrar iteração
            self.iteration_history.append({
                'iteration': iteration,
                'pdf_path': current_pdf,
                'status': review_result['status'],
                'score': review_result['compliance_score'],
                'critical_errors': len(review_result.get('critical_errors', [])),
                'major_errors': len(review_result.get('major_errors', []))
            })
            
            # Atualizar contador total
            self.lessons['total_iterations'] += 1
            
            # Verificar se foi aprovado
            if review_result['status'] == "APPROVED":
                print(f"\n{'='*80}")
                print(f"✅ PACOTE APROVADO NA ITERAÇÃO {iteration}!")
                print(f"{'='*80}")
                
                self.lessons['successful_approvals'] += 1
                
                # Adicionar melhores práticas
                self.add_best_practice(
                    f"Aprovado após {iteration} iteração(ões) em {datetime.now().strftime('%Y-%m-%d')}"
                )
                
                self._save_lessons()
                
                return {
                    'status': 'SUCCESS',
                    'final_pdf': current_pdf,
                    'iterations_needed': iteration,
                    'review_result': review_result,
                    'history': self.iteration_history
                }
            
            # Se rejeitado, gerar instruções detalhadas
            print(f"\n❌ Pacote REJEITADO. Gerando instruções de correção...")
            instructions = self.generate_detailed_correction_instructions(review_result)
            
            # Salvar instruções em arquivo
            instructions_file = f"/app/correction_instructions_iter_{iteration}.txt"
            with open(instructions_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(instructions))
            
            print(f"\n📄 Instruções salvas em: {instructions_file}")
            
            # Aprender com a rejeição
            self.learn_from_rejection(review_result, instructions)
            
            # Se não é a última iteração, gerar nova versão
            if iteration < self.max_iterations:
                print(f"\n🔧 Gerando versão melhorada baseada nas instruções...")
                try:
                    current_pdf = generator_function(iteration, instructions, review_result)
                    print(f"✅ Nova versão gerada: {current_pdf}")
                except Exception as e:
                    print(f"❌ Erro ao gerar nova versão: {e}")
                    break
            else:
                print(f"\n⚠️ Número máximo de iterações ({self.max_iterations}) atingido")
        
        # Se chegou aqui, não foi aprovado
        print(f"\n{'='*80}")
        print(f"❌ PACOTE NÃO APROVADO APÓS {self.max_iterations} ITERAÇÕES")
        print(f"{'='*80}")
        
        self._save_lessons()
        
        return {
            'status': 'FAILED',
            'final_pdf': current_pdf,
            'iterations_attempted': self.max_iterations,
            'last_review_result': review_result,
            'history': self.iteration_history,
            'message': 'Número máximo de iterações atingido sem aprovação'
        }
    
    def print_learning_summary(self):
        """Imprime resumo do aprendizado acumulado"""
        print(f"\n{'='*80}")
        print(f"📚 RESUMO DE APRENDIZADO ACUMULADO - {self.visa_type}")
        print(f"{'='*80}")
        print(f"Total de iterações executadas: {self.lessons['total_iterations']}")
        print(f"Aprovações bem-sucedidas: {self.lessons['successful_approvals']}")
        
        if self.lessons['common_errors']:
            print(f"\n🔴 Erros mais comuns:")
            sorted_errors = sorted(self.lessons['common_errors'].items(), 
                                 key=lambda x: x[1], reverse=True)
            for error_type, count in sorted_errors[:5]:
                print(f"  • {error_type}: {count}x")
        
        if self.lessons['best_practices']:
            print(f"\n💡 Melhores práticas aprendidas:")
            for practice in self.lessons['best_practices'][-5:]:
                print(f"  • {practice}")
        
        print(f"{'='*80}")


if __name__ == "__main__":
    # Teste do sistema de aprendizado
    learning_system = IterativeLearningSystem(visa_type="H-1B", max_iterations=3)
    learning_system.print_learning_summary()
    
    # Testar geração de instruções com pacote existente
    print("\n🧪 TESTE: Gerando instruções de correção...")
    
    if os.path.exists('/app/PROFESSIONAL_H1B_PACKAGE_FERNANDA_SANTOS.pdf'):
        result = learning_system.reviewer.comprehensive_review(
            '/app/PROFESSIONAL_H1B_PACKAGE_FERNANDA_SANTOS.pdf'
        )
        
        instructions = learning_system.generate_detailed_correction_instructions(result)
        
        # Salvar instruções
        with open('/app/SAMPLE_CORRECTION_INSTRUCTIONS.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(instructions))
        
        print(f"\n✅ Instruções de exemplo salvas em: /app/SAMPLE_CORRECTION_INSTRUCTIONS.txt")
        print(f"\n📄 Primeiras 20 linhas das instruções:")
        print('\n'.join(instructions[:20]))
