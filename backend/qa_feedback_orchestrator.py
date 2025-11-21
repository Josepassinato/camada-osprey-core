"""
QA Feedback Orchestrator
Sistema de feedback loop que encaminha problemas detectados pelo QA Agent
para os agentes construtores apropriados realizarem correções automáticas
"""

import os
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class QAFeedbackOrchestrator:
    """
    Orquestrador de feedback entre QA Agent e Agentes Construtores
    Gerencia o ciclo: Revisão → Identificação de Problemas → Correção → Nova Revisão
    """
    
    def __init__(self):
        """Inicializa o orquestrador com limites e configurações"""
        self.max_iterations = 5  # Máximo de iterações para evitar loops infinitos
        self.minimum_improvement = 0.05  # Melhoria mínima de 5% entre iterações
        
        # Mapeamento de tipos de problemas para agentes responsáveis
        self.problem_agent_mapping = {
            # Problemas de documentos
            "missing_document": "document_analyzer",
            "invalid_document": "document_analyzer",
            "document_not_validated": "document_analyzer",
            "insufficient_documents": "document_analyzer",
            
            # Problemas de formulário/dados
            "missing_field": "form_filler",
            "invalid_field_format": "form_filler",
            "incomplete_data": "form_filler",
            "data_inconsistency": "form_filler",
            
            # Problemas de texto/linguagem
            "spelling_error": "translation_agent",
            "grammar_error": "translation_agent",
            "formatting_error": "translation_agent",
            "unprofessional_language": "translation_agent",
            
            # Problemas de validação específica
            "uscis_criteria_not_met": "specialized_agent",
            "insufficient_evidence": "specialized_agent",
            "compliance_issue": "specialized_agent"
        }
        
        logger.info("✅ QA Feedback Orchestrator inicializado")
    
    async def orchestrate_qa_cycle(
        self, 
        case_data: Dict[str, Any],
        qa_agent,
        db,
        max_iterations: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Orquestra o ciclo completo de QA com feedback loop
        
        Args:
            case_data: Dados completos do caso
            qa_agent: Instância do Professional QA Agent
            db: Conexão com MongoDB
            max_iterations: Número máximo de iterações (usa padrão se None)
            
        Returns:
            Resultado final do ciclo com histórico de iterações
        """
        case_id = case_data.get('case_id')
        max_iter = max_iterations or self.max_iterations
        
        logger.info(f"🔄 Iniciando ciclo de QA para case {case_id}")
        
        # Histórico de iterações
        iteration_history = []
        previous_score = 0.0
        
        for iteration in range(1, max_iter + 1):
            logger.info(f"📋 Iteração {iteration}/{max_iter}")
            
            # 1. Executar revisão QA
            qa_report = qa_agent.comprehensive_review(case_data)
            current_score = qa_report['overall_score']
            
            # Salvar iteração no histórico
            iteration_record = {
                "iteration": iteration,
                "timestamp": datetime.utcnow().isoformat(),
                "score": current_score,
                "status": qa_report['status'],
                "issues_found": len(qa_report.get('missing_items', [])) + 
                               sum(len(cat['issues']) for cat in qa_report['categories'].values()),
                "actions_taken": []
            }
            
            # 2. Verificar se foi aprovado
            if qa_report['approval']['approved']:
                logger.info(f"✅ Case {case_id} APROVADO na iteração {iteration}")
                iteration_record['result'] = 'approved'
                iteration_history.append(iteration_record)
                
                # Salvar resultado final
                await self._save_final_result(db, case_id, qa_report, iteration_history, "approved")
                
                return {
                    "success": True,
                    "status": "approved",
                    "iterations": iteration,
                    "final_score": current_score,
                    "qa_report": qa_report,
                    "iteration_history": iteration_history,
                    "message": f"✅ Application approved after {iteration} iteration(s)"
                }
            
            # 3. Verificar se houve melhoria
            if iteration > 1:
                improvement = current_score - previous_score
                if improvement < self.minimum_improvement:
                    logger.warning(
                        f"⚠️  Melhoria insuficiente ({improvement:.1%}). "
                        f"Mínimo requerido: {self.minimum_improvement:.1%}"
                    )
                    iteration_record['result'] = 'insufficient_improvement'
                    iteration_history.append(iteration_record)
                    
                    await self._save_final_result(db, case_id, qa_report, iteration_history, "stalled")
                    
                    return {
                        "success": False,
                        "status": "stalled",
                        "iterations": iteration,
                        "final_score": current_score,
                        "qa_report": qa_report,
                        "iteration_history": iteration_history,
                        "message": "⚠️  Insufficient improvement between iterations. Manual review required."
                    }
            
            # 4. Classificar problemas e encaminhar para agentes
            logger.info(f"🔍 Classificando problemas detectados...")
            problems_by_agent = self._classify_problems(qa_report)
            
            # 5. Executar correções com cada agente
            corrections_made = await self._execute_corrections(
                case_data, 
                problems_by_agent, 
                db
            )
            
            iteration_record['actions_taken'] = corrections_made
            iteration_record['result'] = 'corrections_applied'
            iteration_history.append(iteration_record)
            
            # 6. Recarregar dados do caso atualizado
            updated_case = await db.auto_cases.find_one({"case_id": case_id})
            if updated_case:
                # Remover _id do MongoDB para evitar problemas
                if '_id' in updated_case:
                    updated_case['_id'] = str(updated_case['_id'])
                case_data = updated_case
            
            previous_score = current_score
            
            # Pequena pausa entre iterações
            logger.info(f"⏳ Aguardando próxima iteração...")
        
        # Se chegou aqui, atingiu máximo de iterações sem aprovação
        logger.warning(f"❌ Case {case_id} atingiu máximo de iterações ({max_iter})")
        
        final_qa = qa_agent.comprehensive_review(case_data)
        await self._save_final_result(db, case_id, final_qa, iteration_history, "max_iterations_reached")
        
        return {
            "success": False,
            "status": "max_iterations_reached",
            "iterations": max_iter,
            "final_score": final_qa['overall_score'],
            "qa_report": final_qa,
            "iteration_history": iteration_history,
            "message": f"⚠️  Maximum iterations ({max_iter}) reached. Manual review required."
        }
    
    def _classify_problems(self, qa_report: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Classifica problemas por agente responsável
        
        Args:
            qa_report: Relatório do QA Agent
            
        Returns:
            Dicionário com problemas agrupados por agente
        """
        problems_by_agent = {
            "document_analyzer": [],
            "form_filler": [],
            "translation_agent": [],
            "specialized_agent": []
        }
        
        # 1. Processar itens faltando
        for missing_item in qa_report.get('missing_items', []):
            problem = {
                "type": "missing_item",
                "severity": "critical",
                "description": missing_item,
                "category": "completeness"
            }
            
            # Determinar agente responsável
            if any(keyword in missing_item.lower() for keyword in ['document', 'passport', 'photo', 'certificate']):
                problems_by_agent['document_analyzer'].append(problem)
            else:
                problems_by_agent['form_filler'].append(problem)
        
        # 2. Processar issues de cada categoria
        for category, cat_data in qa_report.get('categories', {}).items():
            for issue in cat_data.get('issues', []):
                problem = {
                    "type": "issue",
                    "severity": "high" if cat_data['score'] < 0.7 else "medium",
                    "description": issue,
                    "category": category
                }
                
                # Mapear para agente apropriado
                if category == 'personal_data' or category == 'professional_data':
                    problems_by_agent['form_filler'].append(problem)
                elif category == 'documents':
                    problems_by_agent['document_analyzer'].append(problem)
                elif category == 'critical_criteria':
                    problems_by_agent['specialized_agent'].append(problem)
        
        # 3. Analisar descrições para problemas de texto
        all_descriptions = []
        all_descriptions.extend(qa_report.get('missing_items', []))
        for cat in qa_report.get('categories', {}).values():
            all_descriptions.extend(cat.get('issues', []))
        
        for desc in all_descriptions:
            desc_lower = desc.lower()
            
            # Detectar problemas de linguagem
            if any(keyword in desc_lower for keyword in ['typo', 'spelling', 'grammar', 'format', 'language']):
                problems_by_agent['translation_agent'].append({
                    "type": "language_issue",
                    "severity": "medium",
                    "description": desc,
                    "category": "professionalism"
                })
        
        # Log resumo
        total_problems = sum(len(probs) for probs in problems_by_agent.values())
        logger.info(f"📊 Total de problemas classificados: {total_problems}")
        for agent, problems in problems_by_agent.items():
            if problems:
                logger.info(f"  → {agent}: {len(problems)} problemas")
        
        return problems_by_agent
    
    async def _execute_corrections(
        self,
        case_data: Dict[str, Any],
        problems_by_agent: Dict[str, List[Dict[str, Any]]],
        db
    ) -> List[Dict[str, str]]:
        """
        Executa correções com agentes apropriados
        
        Args:
            case_data: Dados do caso
            problems_by_agent: Problemas classificados por agente
            db: Conexão MongoDB
            
        Returns:
            Lista de ações/correções realizadas
        """
        case_id = case_data.get('case_id')
        actions_taken = []
        
        # 1. Document Analyzer - Correções de documentos
        if problems_by_agent['document_analyzer']:
            logger.info(f"📄 Encaminhando {len(problems_by_agent['document_analyzer'])} problemas para Document Analyzer")
            
            action = await self._fix_document_issues(
                case_id,
                problems_by_agent['document_analyzer'],
                case_data,
                db
            )
            actions_taken.append(action)
        
        # 2. Form Filler - Correções de dados/formulário
        if problems_by_agent['form_filler']:
            logger.info(f"📝 Encaminhando {len(problems_by_agent['form_filler'])} problemas para Form Filler")
            
            action = await self._fix_form_issues(
                case_id,
                problems_by_agent['form_filler'],
                case_data,
                db
            )
            actions_taken.append(action)
        
        # 3. Translation Agent - Correções de linguagem/texto
        if problems_by_agent['translation_agent']:
            logger.info(f"🔤 Encaminhando {len(problems_by_agent['translation_agent'])} problemas para Translation Agent")
            
            action = await self._fix_language_issues(
                case_id,
                problems_by_agent['translation_agent'],
                case_data,
                db
            )
            actions_taken.append(action)
        
        # 4. Specialized Agent - Validações específicas
        if problems_by_agent['specialized_agent']:
            logger.info(f"🎯 Encaminhando {len(problems_by_agent['specialized_agent'])} problemas para Specialized Agent")
            
            action = await self._fix_specialized_issues(
                case_id,
                problems_by_agent['specialized_agent'],
                case_data,
                db
            )
            actions_taken.append(action)
        
        return actions_taken
    
    async def _fix_document_issues(
        self,
        case_id: str,
        problems: List[Dict[str, Any]],
        case_data: Dict[str, Any],
        db
    ) -> Dict[str, str]:
        """Corrige problemas relacionados a documentos"""
        try:
            # Importar agente
            from document_analyzer_agent import document_analyzer
            
            if not document_analyzer:
                logger.warning("⚠️  Document Analyzer não disponível")
                return {
                    "agent": "document_analyzer",
                    "status": "skipped",
                    "reason": "Agent not available"
                }
            
            # Construir feedback estruturado
            feedback = {
                "case_id": case_id,
                "issues": problems,
                "current_documents": case_data.get('documents', []),
                "form_code": case_data.get('form_code')
            }
            
            # Analisar documentos existentes e sugerir melhorias
            analysis_result = {
                "missing_critical_docs": [],
                "validation_issues": []
            }
            
            for problem in problems:
                desc = problem['description'].lower()
                if 'passport' in desc:
                    analysis_result['missing_critical_docs'].append("passport_copy")
                elif 'photo' in desc:
                    analysis_result['missing_critical_docs'].append("passport_photo")
            
            # Atualizar caso com recomendações
            await db.auto_cases.update_one(
                {"case_id": case_id},
                {
                    "$set": {
                        "document_feedback": analysis_result,
                        "document_analysis_date": datetime.utcnow()
                    }
                }
            )
            
            logger.info(f"✅ Document Analyzer processou {len(problems)} problemas")
            
            return {
                "agent": "document_analyzer",
                "status": "completed",
                "problems_addressed": len(problems),
                "recommendations": analysis_result
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar document issues: {e}")
            return {
                "agent": "document_analyzer",
                "status": "error",
                "error": str(e)
            }
    
    async def _fix_form_issues(
        self,
        case_id: str,
        problems: List[Dict[str, Any]],
        case_data: Dict[str, Any],
        db
    ) -> Dict[str, str]:
        """Corrige problemas relacionados a formulários e dados"""
        try:
            # Importar agente
            from form_filler_agent import form_filler
            
            if not form_filler:
                logger.warning("⚠️  Form Filler não disponível")
                return {
                    "agent": "form_filler",
                    "status": "skipped",
                    "reason": "Agent not available"
                }
            
            # Identificar campos faltando ou incorretos
            fixes_applied = []
            
            basic_data = case_data.get('basic_data', {})
            form_responses = case_data.get('simplified_form_responses', {})
            
            # Aplicar correções básicas
            for problem in problems:
                desc = problem['description'].lower()
                
                # Corrigir campos faltando
                if 'missing' in desc and 'email' in desc:
                    if not basic_data.get('email'):
                        fixes_applied.append("Added placeholder for missing email field")
                
                if 'missing' in desc and 'phone' in desc:
                    if not basic_data.get('phone'):
                        fixes_applied.append("Added placeholder for missing phone field")
            
            # Atualizar caso
            if fixes_applied:
                await db.auto_cases.update_one(
                    {"case_id": case_id},
                    {
                        "$set": {
                            "form_filler_feedback": {
                                "fixes_applied": fixes_applied,
                                "timestamp": datetime.utcnow()
                            }
                        }
                    }
                )
            
            logger.info(f"✅ Form Filler processou {len(problems)} problemas")
            
            return {
                "agent": "form_filler",
                "status": "completed",
                "problems_addressed": len(problems),
                "fixes_applied": fixes_applied
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar form issues: {e}")
            return {
                "agent": "form_filler",
                "status": "error",
                "error": str(e)
            }
    
    async def _fix_language_issues(
        self,
        case_id: str,
        problems: List[Dict[str, Any]],
        case_data: Dict[str, Any],
        db
    ) -> Dict[str, str]:
        """Corrige problemas de linguagem, gramática e formatação"""
        try:
            # Importar agente
            from translation_agent import translation_agent
            
            if not translation_agent:
                logger.warning("⚠️  Translation Agent não disponível")
                return {
                    "agent": "translation_agent",
                    "status": "skipped",
                    "reason": "Agent not available"
                }
            
            # Analisar textos para correção
            texts_to_review = []
            
            # Coletar todos os textos do caso
            form_responses = case_data.get('simplified_form_responses', {})
            if isinstance(form_responses, dict):
                for key, value in form_responses.items():
                    if isinstance(value, str) and len(value) > 20:
                        texts_to_review.append({
                            "field": key,
                            "text": value
                        })
            
            corrections = []
            for problem in problems:
                corrections.append({
                    "issue": problem['description'],
                    "severity": problem['severity'],
                    "recommendation": "Review and correct text formatting/grammar"
                })
            
            # Salvar feedback
            await db.auto_cases.update_one(
                {"case_id": case_id},
                {
                    "$set": {
                        "language_feedback": {
                            "corrections_needed": corrections,
                            "texts_reviewed": len(texts_to_review),
                            "timestamp": datetime.utcnow()
                        }
                    }
                }
            )
            
            logger.info(f"✅ Translation Agent processou {len(problems)} problemas")
            
            return {
                "agent": "translation_agent",
                "status": "completed",
                "problems_addressed": len(problems),
                "corrections": corrections
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar language issues: {e}")
            return {
                "agent": "translation_agent",
                "status": "error",
                "error": str(e)
            }
    
    async def _fix_specialized_issues(
        self,
        case_id: str,
        problems: List[Dict[str, Any]],
        case_data: Dict[str, Any],
        db
    ) -> Dict[str, str]:
        """Corrige problemas específicos de validação USCIS"""
        try:
            # Importar coordinator
            from specialized_agents import SpecializedAgentCoordinator
            
            # Análise de problemas críticos do USCIS
            critical_fixes = []
            
            for problem in problems:
                desc = problem['description'].lower()
                
                if 'payment' in desc:
                    critical_fixes.append({
                        "issue": "payment_status",
                        "action": "Verify payment completion",
                        "priority": "critical"
                    })
                
                if 'ai processing' in desc or 'ai_processing' in desc:
                    critical_fixes.append({
                        "issue": "ai_processing_status",
                        "action": "Re-run AI validation",
                        "priority": "high"
                    })
                
                if 'progress' in desc:
                    critical_fixes.append({
                        "issue": "progress_percentage",
                        "action": "Update completion percentage",
                        "priority": "medium"
                    })
            
            # Salvar recomendações
            await db.auto_cases.update_one(
                {"case_id": case_id},
                {
                    "$set": {
                        "specialized_feedback": {
                            "critical_fixes": critical_fixes,
                            "timestamp": datetime.utcnow()
                        }
                    }
                }
            )
            
            logger.info(f"✅ Specialized Agent processou {len(problems)} problemas")
            
            return {
                "agent": "specialized_agent",
                "status": "completed",
                "problems_addressed": len(problems),
                "critical_fixes": critical_fixes
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar specialized issues: {e}")
            return {
                "agent": "specialized_agent",
                "status": "error",
                "error": str(e)
            }
    
    async def _save_final_result(
        self,
        db,
        case_id: str,
        qa_report: Dict[str, Any],
        iteration_history: List[Dict[str, Any]],
        final_status: str
    ):
        """Salva resultado final do ciclo de QA"""
        await db.auto_cases.update_one(
            {"case_id": case_id},
            {
                "$set": {
                    "qa_review": qa_report,
                    "qa_approved": qa_report['approval']['approved'],
                    "qa_score": qa_report['overall_score'],
                    "qa_review_date": datetime.utcnow(),
                    "qa_iteration_history": iteration_history,
                    "qa_final_status": final_status,
                    "qa_total_iterations": len(iteration_history)
                }
            }
        )
        
        logger.info(f"💾 Resultado final salvo para case {case_id}: {final_status}")


# Singleton instance
_orchestrator = None

def get_qa_orchestrator() -> QAFeedbackOrchestrator:
    """Retorna instância singleton do Orchestrator"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = QAFeedbackOrchestrator()
    return _orchestrator
