"""
Workflow Engine - Phase 4D
Sistema de workflow automático para processos de imigração
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    """Status possíveis do workflow"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class StepStatus(Enum):
    """Status possíveis de um step"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRY = "retry"

@dataclass
class WorkflowStep:
    """Define um passo no workflow"""
    step_id: str
    name: str
    handler: str  # Nome da função/método a ser executado
    dependencies: List[str] = field(default_factory=list)  # IDs dos steps que devem completar primeiro
    parameters: Dict[str, Any] = field(default_factory=dict)
    timeout: Optional[float] = None
    retry_attempts: int = 3
    retry_delay: float = 1.0
    required: bool = True  # Se False, falha não interrompe o workflow
    condition: Optional[str] = None  # Condição para executar o step
    
    # Status tracking
    status: StepStatus = StepStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None
    attempts: int = 0

@dataclass
class WorkflowExecution:
    """Execução de um workflow"""
    execution_id: str
    workflow_name: str
    case_id: str
    status: WorkflowStatus
    steps: List[WorkflowStep]
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    context: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    progress: float = 0.0

class WorkflowEngine:
    """
    Engine principal para execução de workflows
    """
    
    def __init__(self, db: AsyncIOMotorDatabase = None):
        self.db = db
        self.workflows: Dict[str, List[WorkflowStep]] = {}
        self.active_executions: Dict[str, WorkflowExecution] = {}
        self.step_handlers: Dict[str, Callable] = {}
        
        # Register built-in workflows
        self._register_default_workflows()
        
        # Register built-in handlers
        self._register_default_handlers()
    
    def _register_default_workflows(self):
        """
        Registra workflows padrão para processos de imigração
        """
        
        # Workflow completo para H-1B
        self.workflows["h1b_complete_process"] = [
            WorkflowStep(
                step_id="validate_documents",
                name="Validar Documentos",
                handler="document_validation_handler",
                timeout=300.0,
                retry_attempts=2
            ),
            WorkflowStep(
                step_id="fill_forms",
                name="Preencher Formulários",
                handler="form_filling_handler",
                dependencies=["validate_documents"],
                timeout=180.0
            ),
            WorkflowStep(
                step_id="generate_cover_letter", 
                name="Gerar Carta de Apresentação",
                handler="cover_letter_handler",
                dependencies=["fill_forms"],
                timeout=120.0
            ),
            WorkflowStep(
                step_id="finalize_package",
                name="Finalizar Pacote",
                handler="package_finalization_handler",
                dependencies=["generate_cover_letter"],
                timeout=240.0
            ),
            WorkflowStep(
                step_id="quality_check",
                name="Verificação de Qualidade",
                handler="quality_check_handler",
                dependencies=["finalize_package"],
                required=False
            ),
            WorkflowStep(
                step_id="send_notifications",
                name="Enviar Notificações",
                handler="notification_handler", 
                dependencies=["finalize_package"],
                required=False
            )
        ]
        
        # Workflow para F-1
        self.workflows["f1_student_process"] = [
            WorkflowStep(
                step_id="validate_i20",
                name="Validar I-20",
                handler="i20_validation_handler",
                timeout=60.0
            ),
            WorkflowStep(
                step_id="sevis_payment",
                name="Verificar Pagamento SEVIS",
                handler="sevis_payment_handler",
                dependencies=["validate_i20"]
            ),
            WorkflowStep(
                step_id="fill_ds160",
                name="Preencher DS-160",
                handler="ds160_handler",
                dependencies=["sevis_payment"],
                timeout=300.0
            ),
            WorkflowStep(
                step_id="schedule_interview",
                name="Agendar Entrevista",
                handler="interview_scheduling_handler",
                dependencies=["fill_ds160"]
            )
        ]
        
        # Workflow para I-485
        self.workflows["i485_adjustment_process"] = [
            WorkflowStep(
                step_id="priority_date_check",
                name="Verificar Priority Date",
                handler="priority_date_handler"
            ),
            WorkflowStep(
                step_id="medical_exam",
                name="Exame Médico I-693",
                handler="medical_exam_handler",
                dependencies=["priority_date_check"],
                timeout=1800.0  # 30 minutes
            ),
            WorkflowStep(
                step_id="fill_i485",
                name="Preencher I-485",
                handler="i485_form_handler",
                dependencies=["medical_exam"]
            ),
            WorkflowStep(
                step_id="concurrent_filing",
                name="Petições Concorrentes (I-765, I-131)",
                handler="concurrent_filing_handler",
                dependencies=["fill_i485"],
                required=False
            ),
            WorkflowStep(
                step_id="package_review",
                name="Revisão Final",
                handler="package_review_handler",
                dependencies=["fill_i485", "concurrent_filing"]
            )
        ]
        
        # Workflow de recuperação de erros
        self.workflows["error_recovery"] = [
            WorkflowStep(
                step_id="analyze_error",
                name="Analisar Erro",
                handler="error_analysis_handler"
            ),
            WorkflowStep(
                step_id="attempt_recovery",
                name="Tentar Recuperação",
                handler="recovery_attempt_handler",
                dependencies=["analyze_error"],
                retry_attempts=1
            ),
            WorkflowStep(
                step_id="escalate_if_needed",
                name="Escalar se Necessário",
                handler="escalation_handler",
                dependencies=["attempt_recovery"],
                condition="recovery_failed"
            )
        ]
    
    def _register_default_handlers(self):
        """
        Registra handlers padrão
        """
        
        self.step_handlers.update({
            # Document handlers
            "document_validation_handler": self._document_validation_handler,
            "i20_validation_handler": self._i20_validation_handler,
            
            # Form handlers
            "form_filling_handler": self._form_filling_handler,
            "ds160_handler": self._ds160_handler,
            "i485_form_handler": self._i485_form_handler,
            
            # Process handlers
            "cover_letter_handler": self._cover_letter_handler,
            "package_finalization_handler": self._package_finalization_handler,
            "quality_check_handler": self._quality_check_handler,
            
            # Special handlers
            "sevis_payment_handler": self._sevis_payment_handler,
            "medical_exam_handler": self._medical_exam_handler,
            "priority_date_handler": self._priority_date_handler,
            "concurrent_filing_handler": self._concurrent_filing_handler,
            "interview_scheduling_handler": self._interview_scheduling_handler,
            "notification_handler": self._notification_handler,
            "package_review_handler": self._package_review_handler,
            
            # Error recovery
            "error_analysis_handler": self._error_analysis_handler,
            "recovery_attempt_handler": self._recovery_attempt_handler,
            "escalation_handler": self._escalation_handler
        })
    
    async def start_workflow(self, 
                           workflow_name: str,
                           case_id: str,
                           context: Dict[str, Any] = None) -> str:
        """
        Inicia execução de um workflow
        """
        if workflow_name not in self.workflows:
            raise ValueError(f"Workflow '{workflow_name}' não encontrado")
        
        execution_id = str(uuid.uuid4())
        context = context or {}
        
        # Criar cópia dos steps para esta execução
        steps = []
        for step_template in self.workflows[workflow_name]:
            step = WorkflowStep(
                step_id=step_template.step_id,
                name=step_template.name,
                handler=step_template.handler,
                dependencies=step_template.dependencies.copy(),
                parameters=step_template.parameters.copy(),
                timeout=step_template.timeout,
                retry_attempts=step_template.retry_attempts,
                retry_delay=step_template.retry_delay,
                required=step_template.required,
                condition=step_template.condition
            )
            steps.append(step)
        
        execution = WorkflowExecution(
            execution_id=execution_id,
            workflow_name=workflow_name,
            case_id=case_id,
            status=WorkflowStatus.PENDING,
            steps=steps,
            created_at=datetime.now(timezone.utc),
            context=context
        )
        
        self.active_executions[execution_id] = execution
        
        # Salvar no banco se disponível
        if self.db is not None:
            await self._save_execution_to_db(execution)
        
        logger.info(f"🚀 Started workflow {workflow_name} for case {case_id} (execution: {execution_id})")
        
        # Executar workflow em background
        asyncio.create_task(self._execute_workflow(execution_id))
        
        return execution_id
    
    async def _execute_workflow(self, execution_id: str):
        """
        Executa workflow completo
        """
        execution = self.active_executions.get(execution_id)
        if not execution:
            return
        
        try:
            execution.status = WorkflowStatus.RUNNING
            execution.started_at = datetime.now(timezone.utc)
            
            logger.info(f"🔄 Executing workflow {execution.workflow_name}")
            
            completed_steps = set()
            
            while True:
                # Encontrar próximo step a executar
                next_step = None
                
                for step in execution.steps:
                    if (step.status == StepStatus.PENDING and 
                        all(dep in completed_steps for dep in step.dependencies)):
                        
                        # Verificar condição se existir
                        if step.condition and not self._evaluate_condition(step.condition, execution):
                            step.status = StepStatus.SKIPPED
                            completed_steps.add(step.step_id)
                            logger.info(f"⏭️ Skipping step {step.step_id} due to condition")
                            continue
                        
                        next_step = step
                        break
                
                if not next_step:
                    # Verificar se há steps falhados obrigatórios
                    failed_required_steps = [s for s in execution.steps 
                                           if s.status == StepStatus.FAILED and s.required]
                    
                    if failed_required_steps:
                        execution.status = WorkflowStatus.FAILED
                        execution.error = f"Required steps failed: {[s.step_id for s in failed_required_steps]}"
                        break
                    
                    # Verificar se todos os steps foram processados
                    remaining_steps = [s for s in execution.steps 
                                     if s.status == StepStatus.PENDING]
                    
                    if not remaining_steps:
                        execution.status = WorkflowStatus.COMPLETED
                        break
                    
                    # Não há steps prontos para executar - possível deadlock
                    logger.error(f"❌ Workflow deadlock detected for {execution_id}")
                    execution.status = WorkflowStatus.FAILED
                    execution.error = "Workflow deadlock - circular dependencies or missing handlers"
                    break
                
                # Executar step
                await self._execute_step(execution, next_step)
                
                if next_step.status == StepStatus.COMPLETED:
                    completed_steps.add(next_step.step_id)
                
                # Atualizar progresso
                execution.progress = len(completed_steps) / len(execution.steps) * 100
                
                # Salvar estado
                if self.db is not None:
                    await self._save_execution_to_db(execution)
            
            execution.completed_at = datetime.now(timezone.utc)
            
            if execution.status == WorkflowStatus.COMPLETED:
                logger.info(f"✅ Workflow {execution.workflow_name} completed successfully")
            else:
                logger.error(f"❌ Workflow {execution.workflow_name} failed: {execution.error}")
            
            # Salvar estado final
            if self.db:
                await self._save_execution_to_db(execution)
                
        except Exception as e:
            logger.error(f"❌ Workflow execution error: {e}")
            execution.status = WorkflowStatus.FAILED
            execution.error = str(e)
            execution.completed_at = datetime.now(timezone.utc)
            
            if self.db:
                await self._save_execution_to_db(execution)
        
        finally:
            # Manter execution por algum tempo para consulta
            await asyncio.sleep(3600)  # 1 hora
            self.active_executions.pop(execution_id, None)
    
    async def _execute_step(self, execution: WorkflowExecution, step: WorkflowStep):
        """
        Executa um step individual
        """
        step.status = StepStatus.RUNNING
        step.started_at = datetime.now(timezone.utc)
        step.attempts += 1
        
        logger.info(f"🔄 Executing step {step.step_id}: {step.name}")
        
        try:
            handler = self.step_handlers.get(step.handler)
            if not handler:
                raise ValueError(f"Handler '{step.handler}' not found")
            
            # Preparar contexto para o handler
            step_context = {
                "execution_id": execution.execution_id,
                "case_id": execution.case_id,
                "workflow_context": execution.context,
                "step_parameters": step.parameters,
                "previous_results": execution.results
            }
            
            # Executar com timeout se configurado
            if step.timeout:
                step.result = await asyncio.wait_for(
                    handler(step_context), 
                    timeout=step.timeout
                )
            else:
                step.result = await handler(step_context)
            
            step.status = StepStatus.COMPLETED
            step.completed_at = datetime.now(timezone.utc)
            execution.results[step.step_id] = step.result
            
            logger.info(f"✅ Step {step.step_id} completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Step {step.step_id} failed: {e}")
            step.error = str(e)
            
            # Tentar retry se configurado
            if step.attempts < step.retry_attempts:
                step.status = StepStatus.RETRY
                logger.info(f"🔄 Retrying step {step.step_id} (attempt {step.attempts + 1})")
                
                if step.retry_delay > 0:
                    await asyncio.sleep(step.retry_delay)
                
                # Recursive call for retry
                await self._execute_step(execution, step)
            else:
                step.status = StepStatus.FAILED
                step.completed_at = datetime.now(timezone.utc)
    
    def _evaluate_condition(self, condition: str, execution: WorkflowExecution) -> bool:
        """
        Avalia condição para execução de step
        """
        try:
            # Condições simples baseadas em resultados
            if condition == "recovery_failed":
                return execution.results.get("attempt_recovery", {}).get("success", True) == False
            
            # Adicionar mais condições conforme necessário
            return True
            
        except Exception as e:
            logger.warning(f"Error evaluating condition '{condition}': {e}")
            return True
    
    async def _save_execution_to_db(self, execution: WorkflowExecution):
        """
        Salva execução no banco de dados
        """
        try:
            execution_dict = {
                "execution_id": execution.execution_id,
                "workflow_name": execution.workflow_name,
                "case_id": execution.case_id,
                "status": execution.status.value,
                "created_at": execution.created_at,
                "started_at": execution.started_at,
                "completed_at": execution.completed_at,
                "context": execution.context,
                "results": execution.results,
                "error": execution.error,
                "progress": execution.progress,
                "steps": [
                    {
                        "step_id": step.step_id,
                        "name": step.name,
                        "handler": step.handler,
                        "status": step.status.value,
                        "started_at": step.started_at,
                        "completed_at": step.completed_at,
                        "attempts": step.attempts,
                        "error": step.error
                    }
                    for step in execution.steps
                ]
            }
            
            await self.db.workflow_executions.replace_one(
                {"execution_id": execution.execution_id},
                execution_dict,
                upsert=True
            )
            
        except Exception as e:
            logger.error(f"Error saving workflow execution: {e}")
    
    # ===========================================
    # DEFAULT STEP HANDLERS
    # ===========================================
    
    async def _document_validation_handler(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handler para validação de documentos"""
        case_id = context["case_id"]
        logger.info(f"Validating documents for case {case_id}")
        
        # Simular validação de documentos
        await asyncio.sleep(2)  # Simular processamento
        
        return {
            "success": True,
            "documents_validated": 5,
            "issues_found": 1,
            "quality_score": 0.92
        }
    
    async def _form_filling_handler(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handler para preenchimento de formulários"""
        case_id = context["case_id"]
        logger.info(f"Filling forms for case {case_id}")
        
        await asyncio.sleep(3)
        
        return {
            "success": True,
            "forms_filled": ["I-129", "H-Classification"],
            "completeness": 0.95
        }
    
    async def _cover_letter_handler(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handler para geração de carta"""
        case_id = context["case_id"]
        logger.info(f"Generating cover letter for case {case_id}")
        
        await asyncio.sleep(2)
        
        return {
            "success": True,
            "letter_generated": True,
            "word_count": 850
        }
    
    async def _package_finalization_handler(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handler para finalização do pacote"""
        case_id = context["case_id"]
        logger.info(f"Finalizing package for case {case_id}")
        
        await asyncio.sleep(4)
        
        return {
            "success": True,
            "package_ready": True,
            "total_pages": 45,
            "pdf_size_mb": 12.8
        }
    
    async def _quality_check_handler(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handler para verificação de qualidade"""
        await asyncio.sleep(1)
        
        return {
            "success": True,
            "quality_score": 0.94,
            "recommendations": ["Review employment letter dates"]
        }
    
    async def _notification_handler(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handler para envio de notificações"""
        await asyncio.sleep(0.5)
        
        return {
            "success": True,
            "notifications_sent": 2,
            "channels": ["email", "sms"]
        }
    
    # Handlers específicos para F-1
    async def _i20_validation_handler(self, context: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(1)
        return {"success": True, "i20_valid": True}
    
    async def _sevis_payment_handler(self, context: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(1)
        return {"success": True, "sevis_paid": True, "receipt_number": "SEV123456789"}
    
    async def _ds160_handler(self, context: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(5)
        return {"success": True, "ds160_completed": True, "confirmation": "AA123456"}
    
    async def _interview_scheduling_handler(self, context: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(2)
        return {"success": True, "interview_scheduled": True, "date": "2025-02-15"}
    
    # Handlers específicos para I-485
    async def _priority_date_handler(self, context: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.5)
        return {"success": True, "priority_date_current": True}
    
    async def _medical_exam_handler(self, context: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(3)
        return {"success": True, "i693_completed": True, "sealed_envelope": True}
    
    async def _i485_form_handler(self, context: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(4)
        return {"success": True, "i485_completed": True, "pages": 15}
    
    async def _concurrent_filing_handler(self, context: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(2)
        return {"success": True, "i765_filed": True, "i131_filed": True}
    
    async def _package_review_handler(self, context: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(2)
        return {"success": True, "review_completed": True, "approval_ready": True}
    
    # Error recovery handlers
    async def _error_analysis_handler(self, context: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(1)
        return {"success": True, "error_type": "temporary", "recoverable": True}
    
    async def _recovery_attempt_handler(self, context: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(2)
        return {"success": False, "recovery_failed": True}  # Simular falha para testar escalation
    
    async def _escalation_handler(self, context: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(1)
        return {"success": True, "escalated_to": "support_team", "ticket_id": "SUP-123456"}
    
    # ===========================================
    # PUBLIC METHODS
    # ===========================================
    
    def get_execution_status(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Obtém status de uma execução"""
        return self.active_executions.get(execution_id)
    
    def list_active_executions(self) -> List[WorkflowExecution]:
        """Lista execuções ativas"""
        return list(self.active_executions.values())
    
    def list_available_workflows(self) -> List[str]:
        """Lista workflows disponíveis"""
        return list(self.workflows.keys())
    
    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancela uma execução"""
        execution = self.active_executions.get(execution_id)
        if execution:
            execution.status = WorkflowStatus.CANCELLED
            execution.completed_at = datetime.now(timezone.utc)
            if self.db:
                await self._save_execution_to_db(execution)
            return True
        return False
    
    def register_workflow(self, name: str, steps: List[WorkflowStep]):
        """Registra novo workflow"""
        self.workflows[name] = steps
        logger.info(f"Registered workflow: {name}")
    
    def register_handler(self, name: str, handler: Callable):
        """Registra novo handler"""
        self.step_handlers[name] = handler
        logger.info(f"Registered handler: {name}")

# Instância global
workflow_engine: Optional[WorkflowEngine] = None