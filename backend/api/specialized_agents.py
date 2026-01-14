import logging
from datetime import datetime

from fastapi import APIRouter

from agents.specialized import (
    SpecializedAgentCoordinator,
    create_compliance_checker,
    create_document_validator,
    create_eligibility_analyst,
    create_form_validator,
    create_immigration_letter_writer,
    create_uscis_form_translator,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


@router.post("/specialized-agents/document-validation")
async def specialized_document_validation(request: dict):
    """Ultra-specialized document validation using Dr. Miguel."""
    try:
        validator = create_document_validator()

        document_type = request.get("documentType", "passport")
        document_content = request.get("documentContent", "")
        user_data = request.get("userData", {})

        user_name = user_data.get(
            "name",
            user_data.get(
                "full_name", user_data.get("firstName", "") + " " + user_data.get("lastName", "")
            ),
        )

        analysis = await validator.validate_document_with_database(
            document_type=document_type,
            document_content=document_content,
            applicant_name=user_name,
            visa_type=user_data.get("visa_type", "unknown"),
        )

        return {
            "success": True,
            "agent": "Dr. Miguel - Validador de Documentos",
            "specialization": "Document Validation & Authenticity",
            "analysis": analysis,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Dr. Miguel document validation error: {e}")
        return {
            "success": False,
            "agent": "Dr. Miguel - Validador de Documentos",
            "error": str(e),
        }


@router.post("/specialized-agents/form-validation")
async def specialized_form_validation(request: dict):
    """Ultra-specialized form validation using Dra. Ana."""
    try:
        validator = create_form_validator()

        form_data = request.get("formData", {})
        visa_type = request.get("visaType", "H-1B")
        step_id = request.get("stepId", "personal")

        prompt = f"""
        VALIDAÇÃO COMPLETA DE FORMULÁRIO

        Dados do Formulário: {form_data}
        Tipo de Visto: {visa_type}
        Etapa Atual: {step_id}

        Execute validação sistemática conforme seu protocolo especializado.
        """

        session_id = f"form_validation_{visa_type}_{step_id}_{hash(str(form_data)) % 10000}"
        analysis = await validator._call_agent(prompt, session_id)

        return {
            "success": True,
            "agent": "Dra. Ana - Validadora de Formulários",
            "specialization": "Form Validation & Data Consistency",
            "analysis": analysis,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Dra. Ana form validation error: {e}")
        return {
            "success": False,
            "agent": "Dra. Ana - Validadora de Formulários",
            "error": str(e),
        }


@router.post("/specialized-agents/eligibility-analysis")
async def specialized_eligibility_analysis(request: dict):
    """Ultra-specialized eligibility analysis using Dr. Carlos."""
    try:
        analyst = create_eligibility_analyst()

        applicant_profile = request.get("applicantProfile", {})
        visa_type = request.get("visaType", "H-1B")
        qualifications = request.get("qualifications", {})

        prompt = f"""
        ANÁLISE COMPLETA DE ELEGIBILIDADE

        Perfil do Candidato: {applicant_profile}
        Visto Solicitado: {visa_type}
        Qualificações: {qualifications}

        Execute análise sistemática conforme seu protocolo especializado.
        """

        session_id = f"eligibility_{visa_type}_{hash(str(applicant_profile)) % 10000}"
        analysis = await analyst._call_agent(prompt, session_id)

        return {
            "success": True,
            "agent": "Dr. Carlos - Analista de Elegibilidade",
            "specialization": "Visa Eligibility Analysis",
            "analysis": analysis,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Dr. Carlos eligibility analysis error: {e}")
        return {
            "success": False,
            "agent": "Dr. Carlos - Analista de Elegibilidade",
            "error": str(e),
        }


@router.post("/specialized-agents/compliance-check")
async def specialized_compliance_check(request: dict):
    """Ultra-specialized USCIS compliance check using Dra. Patricia."""
    try:
        checker = create_compliance_checker()

        complete_application = request.get("completeApplication", {})
        documents = request.get("documents", [])
        forms = request.get("forms", {})

        prompt = f"""
        REVISÃO FINAL DE COMPLIANCE USCIS

        Aplicação Completa: {complete_application}
        Documentos Submetidos: {documents}
        Formulários: {forms}

        Execute revisão final conforme seu protocolo especializado.
        """

        session_id = f"compliance_{hash(str(complete_application)) % 10000}"
        analysis = await checker._call_agent(prompt, session_id)

        return {
            "success": True,
            "agent": "Dra. Patricia - Compliance USCIS",
            "specialization": "USCIS Compliance & Final Review",
            "analysis": analysis,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Dra. Patricia compliance check error: {e}")
        return {
            "success": False,
            "agent": "Dra. Patricia - Compliance USCIS",
            "error": str(e),
        }


@router.post("/specialized-agents/immigration-letter")
async def specialized_immigration_letter_writing(request: dict):
    """Ultra-specialized immigration letter writing using Dr. Ricardo."""
    try:
        letter_writer = create_immigration_letter_writer()

        client_story = request.get("clientStory", "")
        client_data = request.get("clientData", {})
        visa_type = request.get("visaType", "H-1B")
        letter_type = request.get("letterType", "cover_letter")

        prompt = f"""
        REDAÇÃO DE CARTA DE IMIGRAÇÃO - BASEADA APENAS EM FATOS DO CLIENTE

        TIPO DE VISTO: {visa_type}
        TIPO DE CARTA: {letter_type}

        DADOS DO CLIENTE (USE APENAS ESTES FATOS):
        {client_data}

        HISTÓRIA/CONTEXTO FORNECIDO PELO CLIENTE:
        {client_story}

        INSTRUÇÕES CRÍTICAS:
        - Use APENAS as informações fornecidas acima
        - Se informação crítica estiver faltando, indique [INFORMAÇÃO NECESSÁRIA: descrição]
        - NÃO invente datas, nomes, empresas, qualificações ou eventos
        - Mantenha tom profissional e formal apropriado para USCIS
        - Estruture conforme padrões de cartas de imigração

        Execute conforme seu protocolo especializado de redação.
        """

        session_id = f"letter_{visa_type}_{letter_type}_{hash(client_story) % 10000}"
        analysis = await letter_writer._call_agent(prompt, session_id)

        return {
            "success": True,
            "agent": "Dr. Ricardo - Redator de Cartas",
            "specialization": "Immigration Letter Writing",
            "visa_type": visa_type,
            "letter_type": letter_type,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat(),
            "fact_check": "Only client-provided facts used - no invention",
        }

    except Exception as e:
        logger.error(f"Dr. Ricardo letter writing error: {e}")
        return {"success": False, "agent": "Dr. Ricardo - Redator de Cartas", "error": str(e)}


@router.post("/specialized-agents/uscis-form-translation")
async def specialized_uscis_form_translation(request: dict):
    """Ultra-specialized USCIS form validation and translation using Dr. Fernando."""
    try:
        translator = create_uscis_form_translator()

        friendly_form_responses = request.get("friendlyFormResponses", {})
        visa_type = request.get("visaType", "H-1B")
        target_uscis_form = request.get("targetUSCISForm", "I-129")

        prompt = f"""
        VALIDAÇÃO E TRADUÇÃO DE FORMULÁRIO USCIS

        TIPO DE VISTO: {visa_type}
        FORMULÁRIO USCIS DE DESTINO: {target_uscis_form}

        RESPOSTAS DO FORMULÁRIO AMIGÁVEL (EM PORTUGUÊS):
        {friendly_form_responses}

        INSTRUÇÕES CRÍTICAS:
        1. PRIMEIRO: Valide se todas as respostas obrigatórias estão completas
        2. Verifique consistência e formato correto das informações
        3. Identifique ambiguidades ou informações insuficientes
        4. SOMENTE APÓS VALIDAÇÃO: Traduza para o formulário oficial USCIS
        5. Use terminologia técnica oficial do USCIS
        6. NUNCA traduza informações não fornecidas
        7. Mantenha rastreabilidade campo por campo

        Execute validação completa e tradução conforme seu protocolo especializado.
        """

        session_id = f"uscis_translation_{visa_type}_{target_uscis_form}_{hash(str(friendly_form_responses)) % 10000}"
        analysis = await translator._call_agent(prompt, session_id)

        return {
            "success": True,
            "agent": "Dr. Fernando - Tradutor e Validador USCIS",
            "specialization": "USCIS Form Translation & Validation",
            "visa_type": visa_type,
            "target_form": target_uscis_form,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat(),
            "translation_guarantee": "Only provided information translated - no assumptions",
        }

    except Exception as e:
        logger.error(f"Dr. Fernando USCIS translation error: {e}")
        return {
            "success": False,
            "agent": "Dr. Fernando - Tradutor e Validador USCIS",
            "error": str(e),
        }


@router.post("/specialized-agents/comprehensive-analysis")
async def comprehensive_multi_agent_analysis(request: dict):
    """Comprehensive analysis using multiple specialized agents."""
    try:
        coordinator = SpecializedAgentCoordinator()

        task_type = request.get("taskType", "form_validation")
        data = request.get("data", {})
        user_context = request.get("userContext", {})

        comprehensive_result = await coordinator.analyze_comprehensive(
            task_type=task_type,
            data=data,
            user_context=user_context,
        )

        return {
            "success": True,
            "coordinator": "Multi-Agent Specialized System",
            "result": comprehensive_result,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Comprehensive analysis error: {e}")
        return {"success": False, "coordinator": "Multi-Agent Specialized System", "error": str(e)}
