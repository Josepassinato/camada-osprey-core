"""
Visa API Endpoints
Endpoints para integração com arquitetura multi-agente
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import sys
from pathlib import Path
import time

# Add visa_specialists to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from visa_specialists.supervisor.supervisor_agent import SupervisorAgent
from visa_specialists.b2_extension.b2_agent import B2ExtensionAgent
from visa_specialists.h1b_worker.h1b_agent import H1BWorkerAgent
from visa_specialists.f1_student.f1_agent import F1StudentAgent
from visa_specialists.qa_agent import QualityAssuranceAgent
from visa_specialists.metrics_tracker import MetricsTracker

router = APIRouter(prefix="/api/visa", tags=["visa"])

# Initialize agents
supervisor = SupervisorAgent()
b2_agent = B2ExtensionAgent()
h1b_agent = H1BWorkerAgent()
f1_agent = F1StudentAgent()

# Register specialists
supervisor.register_specialist('B-2', b2_agent)
supervisor.register_specialist('H-1B', h1b_agent)
supervisor.register_specialist('F-1', f1_agent)

# Initialize QA and Metrics
qa_agent = QualityAssuranceAgent()
metrics = MetricsTracker()


class VisaRequest(BaseModel):
    """Request model para geração de pacote"""
    visa_type: str
    user_request: str
    applicant_data: Optional[Dict[str, Any]] = None
    enable_qa: bool = True


class VisaResponse(BaseModel):
    """Response model"""
    success: bool
    visa_type: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    validation: Optional[Dict[str, Any]] = None
    qa_report: Optional[Dict[str, Any]] = None
    processing_time: float
    error: Optional[str] = None


@router.post("/generate", response_model=VisaResponse)
async def generate_visa_package(request: VisaRequest):
    """
    Gera pacote de visto usando arquitetura multi-agente
    
    Process:
    1. Supervisor analisa requisição
    2. Delega para especialista apropriado
    3. Especialista gera pacote
    4. Validação cruzada
    5. QA review (opcional)
    6. Métricas registradas
    """
    start_time = time.time()
    
    try:
        # Process request
        result = supervisor.process_request(
            request.user_input,
            request.applicant_data or {}
        )
        
        if not result['success']:
            processing_time = time.time() - start_time
            
            # Track failed request
            if result.get('visa_type'):
                metrics.track_request(
                    visa_type=result['visa_type'],
                    success=False,
                    processing_time=processing_time
                )
            
            return VisaResponse(
                success=False,
                error=result.get('error'),
                processing_time=processing_time
            )
        
        # QA Review (if enabled)
        qa_report = None
        if request.enable_qa:
            qa_report = qa_agent.review_package(
                result['result'],
                result['validation']
            )
        
        processing_time = time.time() - start_time
        
        # Track successful request
        metrics.track_request(
            visa_type=result['visa_type'],
            success=True,
            processing_time=processing_time,
            validation_result=result['validation'],
            qa_score=qa_report['overall_score'] if qa_report else None
        )
        
        return VisaResponse(
            success=True,
            visa_type=result['visa_type'],
            result=result['result'],
            validation=result['validation'],
            qa_report=qa_report,
            processing_time=processing_time
        )
    
    except Exception as e:
        processing_time = time.time() - start_time
        
        return VisaResponse(
            success=False,
            error=str(e),
            processing_time=processing_time
        )


@router.get("/detect-type")
async def detect_visa_type(user_input: str):
    """
    Detecta tipo de visto baseado na descrição do usuário
    """
    try:
        visa_type = supervisor.detect_visa_type(user_input)
        
        return {
            'success': True,
            'visa_type': visa_type,
            'has_specialist': visa_type in supervisor.specialists if visa_type else False
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/checklist/{visa_type}")
async def get_checklist(visa_type: str):
    """
    Retorna checklist para tipo de visto específico
    """
    try:
        if visa_type not in supervisor.specialists:
            raise HTTPException(
                status_code=404,
                detail=f"Specialist for {visa_type} not found"
            )
        
        specialist = supervisor.specialists[visa_type]
        checklist = specialist.get_package_checklist()
        
        return {
            'success': True,
            'checklist': checklist
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/specialists")
async def list_specialists():
    """
    Lista todos os especialistas disponíveis
    """
    return {
        'success': True,
        'specialists': list(supervisor.specialists.keys())
    }


@router.get("/metrics")
async def get_metrics():
    """
    Retorna métricas e analytics
    """
    try:
        dashboard_data = metrics.get_dashboard_data()
        
        return {
            'success': True,
            'metrics': dashboard_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """
    Health check do sistema multi-agente
    """
    return {
        'success': True,
        'supervisor': 'active',
        'specialists': len(supervisor.specialists),
        'qa_agent': 'active',
        'metrics_tracker': 'active'
    }
