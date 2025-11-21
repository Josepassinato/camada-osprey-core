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


# ============================================================================
# DATA TRANSFORMATION LAYER - Frontend to Agent Format
# ============================================================================

# Mapping between frontend form codes and agent visa types
FORM_CODE_TO_VISA_TYPE = {
    'I-539': 'B-2',  # Tourist visa extension
    'F-1': 'F-1',    # Student visa
    'I-130': 'I-130',  # Family-based (not yet implemented)
    'I-765': 'I-765',  # EAD (not yet implemented)
    'I-90': 'I-90',    # Green card renewal (not yet implemented)
    'EB-2 NIW': 'EB-2 NIW',  # National Interest Waiver (not yet implemented)
    'EB-1A': 'EB-1A',  # Extraordinary Ability (not yet implemented)
    'H-1B': 'H-1B',    # Work visa
}


def transform_case_data_for_agent(case_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transforma dados do caso (formato MongoDB/Frontend) para formato esperado pelos agentes.
    
    Args:
        case_data: Dados do caso do MongoDB contendo:
            - form_code: Código do formulário (I-539, F-1, etc.)
            - basic_data: Dados básicos do usuário
            - simplified_form_responses: Respostas do formulário simplificado
            - user_story_text: História do usuário
            - uploaded_documents: Lista de documentos
            
    Returns:
        Dict formatado para os agentes com estrutura:
            - visa_type: Tipo do visto para o supervisor
            - applicant_data: Dados do aplicante formatados
    """
    form_code = case_data.get('form_code')
    basic_data = case_data.get('basic_data', {})
    simplified_responses = case_data.get('simplified_form_responses', {})
    user_story = case_data.get('user_story_text', '')
    
    # Map form code to visa type
    visa_type = FORM_CODE_TO_VISA_TYPE.get(form_code)
    
    if not visa_type:
        raise ValueError(f"Unsupported form code: {form_code}")
    
    # Check if agent is available
    if visa_type not in supervisor.specialists:
        raise ValueError(
            f"Agent for {visa_type} not yet implemented. "
            f"Available agents: {list(supervisor.specialists.keys())}"
        )
    
    # Build base applicant data structure
    applicant_data = {
        'personal_info': {
            'full_name': f"{basic_data.get('firstName', '')} {basic_data.get('middleName', '')} {basic_data.get('lastName', '')}".strip(),
            'first_name': basic_data.get('firstName', ''),
            'middle_name': basic_data.get('middleName', ''),
            'last_name': basic_data.get('lastName', ''),
            'date_of_birth': basic_data.get('dateOfBirth', ''),
            'country_of_birth': basic_data.get('countryOfBirth', ''),
            'gender': basic_data.get('gender', ''),
            'current_address': basic_data.get('currentAddress', ''),
            'city': basic_data.get('city', ''),
            'state': basic_data.get('state', ''),
            'zip_code': basic_data.get('zipCode', ''),
            'phone': basic_data.get('phoneNumber', ''),
            'email': basic_data.get('email', ''),
        },
        'immigration_info': {
            'alien_number': basic_data.get('alienNumber', ''),
            'ssn': basic_data.get('socialSecurityNumber', ''),
            'current_status': basic_data.get('currentStatus', ''),
            'status_expiration': basic_data.get('statusExpiration', ''),
        },
        'user_story': user_story,
        'simplified_responses': simplified_responses,
    }
    
    # Visa-specific transformations
    if visa_type == 'B-2':
        # B-2 Extension specific data
        applicant_data['extension_details'] = {
            'reason_for_extension': simplified_responses.get('extension_reason', 'Tourist purposes'),
            'requested_duration': simplified_responses.get('requested_duration', '6 months'),
            'arrival_date': simplified_responses.get('arrival_date', ''),
            'current_i94_expiration': basic_data.get('statusExpiration', ''),
        }
        
    elif visa_type == 'F-1':
        # F-1 Student specific data
        applicant_data['education_info'] = {
            'school_name': simplified_responses.get('school_name', ''),
            'program_name': simplified_responses.get('program_name', ''),
            'degree_level': simplified_responses.get('degree_level', ''),
            'start_date': simplified_responses.get('program_start_date', ''),
            'end_date': simplified_responses.get('program_end_date', ''),
            'sevis_id': simplified_responses.get('sevis_id', ''),
            'i20_issue_date': simplified_responses.get('i20_issue_date', ''),
        }
        applicant_data['financial_info'] = {
            'funding_source': simplified_responses.get('funding_source', ''),
            'annual_expenses': simplified_responses.get('annual_expenses', ''),
            'sponsor_info': simplified_responses.get('sponsor_info', {}),
        }
    
    return {
        'visa_type': visa_type,
        'applicant_data': applicant_data,
        'form_code': form_code,
    }


def generate_package_from_case(case_data: Dict[str, Any], enable_qa: bool = True) -> Dict[str, Any]:
    """
    Gera pacote de visto a partir dos dados do caso.
    Esta é a função principal que deve ser chamada pelo case_finalizer.
    
    Args:
        case_data: Dados completos do caso do MongoDB
        enable_qa: Se deve executar QA review
        
    Returns:
        Resultado da geração com:
            - success: bool
            - visa_type: str
            - package_result: dict com PDF path, etc.
            - validation: dict
            - qa_report: dict (opcional)
            - error: str (se falhou)
    """
    start_time = time.time()
    
    try:
        # Transform data
        transformed = transform_case_data_for_agent(case_data)
        
        visa_type = transformed['visa_type']
        applicant_data = transformed['applicant_data']
        
        # Create user request description
        full_name = applicant_data['personal_info']['full_name']
        user_request = f"Generate {visa_type} visa package for {full_name}"
        
        # Process with supervisor
        result = supervisor.process_request(user_request, applicant_data)
        
        if not result['success']:
            return {
                'success': False,
                'error': result.get('error', 'Unknown error'),
                'visa_type': visa_type,
                'processing_time': time.time() - start_time,
            }
        
        # QA Review (optional)
        qa_report = None
        if enable_qa:
            qa_report = qa_agent.review_package(
                result['result'],
                result['validation']
            )
        
        processing_time = time.time() - start_time
        
        # Track metrics
        metrics.track_request(
            visa_type=visa_type,
            success=True,
            processing_time=processing_time,
            validation_result=result['validation'],
            qa_score=qa_report['overall_score'] if qa_report else None
        )
        
        return {
            'success': True,
            'visa_type': visa_type,
            'package_result': result['result'],
            'validation': result['validation'],
            'qa_report': qa_report,
            'processing_time': processing_time,
        }
        
    except ValueError as e:
        # Validation or unsupported visa type
        return {
            'success': False,
            'error': str(e),
            'processing_time': time.time() - start_time,
        }
    except Exception as e:
        # Unexpected error
        return {
            'success': False,
            'error': f"Unexpected error: {str(e)}",
            'processing_time': time.time() - start_time,
        }


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
    package_result: Optional[Dict[str, Any]] = None
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
            request.user_request,
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
            package_result=result['result'],
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
