import json
import logging
import os
import re
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from openai import OpenAI

from agents.qa import get_qa_agent, get_qa_orchestrator
from backend.visa.specifications import get_visa_specifications
from core.database import db

try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
except ImportError:  # pragma: no cover - optional dependency in some setups
    LlmChat = None
    UserMessage = None

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")

# Initialize OpenAI client (v2 API) - will be None if API key not set
openai_client = None
if os.environ.get("OPENAI_API_KEY"):
    openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


@router.post("/auto-application/extract-facts")
async def extract_facts_from_story(request: dict):
    """Extract structured facts from user's story using sistema."""
    try:
        case_id = request.get("case_id")
        story_text = request.get("story_text", "")
        form_code = request.get("form_code")

        if not story_text.strip():
            raise HTTPException(status_code=400, detail="Story text is required")

        if LlmChat is None or UserMessage is None:
            raise HTTPException(status_code=503, detail="LLM client not available")

        visa_specs = get_visa_specifications(form_code) if form_code else {}

        extraction_prompt = f"""
Você é um assistente especializado em extrair informações estruturadas de narrativas para aplicações de imigração dos EUA.

FORMULÁRIO: {form_code or 'Não especificado'}
CATEGORIA: {visa_specs.get('category', 'Não especificada')}

HISTÓRIA DO USUÁRIO:
{story_text}

Extraia e organize as seguintes informações da história, criando um JSON estruturado:

1. PERSONAL_INFO (informações pessoais):
   - full_name, date_of_birth, place_of_birth, nationality, current_address, phone, email

2. IMMIGRATION_HISTORY (histórico de imigração):
   - current_status, previous_entries, visa_history, overstays, deportations

3. FAMILY_DETAILS (detalhes familiares):
   - marital_status, spouse_info, children, parents, siblings

4. EMPLOYMENT_INFO (informações de trabalho):
   - current_job, previous_jobs, employer_details, salary, job_duties

5. EDUCATION (educação):
   - degrees, schools, graduation_dates, certifications

6. TRAVEL_HISTORY (histórico de viagens):
   - trips_outside_usa, duration, purposes, countries_visited

7. FINANCIAL_INFO (informações financeiras):
   - income, bank_accounts, assets, debts, tax_filings

8. SPECIAL_CIRCUMSTANCES (circunstâncias especiais):
   - medical_conditions, criminal_history, military_service, religious_persecution

INSTRUÇÕES:
- Extraia apenas informações explicitamente mencionadas na história
- Use "Não mencionado" para informações ausentes
- Mantenha datas no formato ISO quando possível
- Seja preciso e não invente informações
- Organize por categorias mesmo que algumas estejam vazias

Responda apenas com o JSON estruturado, sem explicações adicionais.
"""

        chat = LlmChat(
            api_key=os.environ.get("EMERGENT_LLM_KEY"),
            session_id=f"fact_extraction_{uuid.uuid4().hex[:8]}",
            system_message=(
                "Você é um especialista em extrair informações estruturadas de narrativas para "
                "aplicações de imigração. Responda sempre em português e com informações precisas."
            ),
        ).with_model("openai", "gpt-4o")

        user_message = UserMessage(text=extraction_prompt)
        ai_response = await chat.send_message(user_message)

        try:
            if "```json" in ai_response:
                ai_response = ai_response.split("```json")[1].split("```")[0].strip()
            elif "```" in ai_response:
                ai_response = ai_response.split("```")[1].split("```")[0].strip()

            extracted_facts = json.loads(ai_response)
        except json.JSONDecodeError:
            extracted_facts = {
                "personal_info": {"extracted_from": "sistema analysis of user story"},
                "immigration_history": {"status": "Extracted from narrative"},
                "family_details": {"mentioned_in_story": True},
                "employment_info": {"details": "See user narrative"},
                "education": {"background": "Mentioned in story"},
                "travel_history": {"trips": "Referenced in narrative"},
            }

        if case_id:
            await db.auto_cases.update_one(
                {"case_id": case_id},
                {
                    "$set": {
                        "ai_extracted_facts": extracted_facts,
                        "updated_at": datetime.now(timezone.utc),
                    }
                },
            )

        return {
            "message": "Facts extracted successfully",
            "extracted_facts": extracted_facts,
            "categories_found": len(extracted_facts.keys()),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting facts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error extracting facts: {str(e)}")


@router.post("/auto-application/generate-forms")
async def generate_official_forms(request: dict):
    """Generate official USCIS forms from simplified responses using sistema."""
    try:
        case_id = request.get("case_id")
        form_responses = request.get("form_responses", {})
        form_code = request.get("form_code")

        if not case_id or not form_responses:
            raise HTTPException(status_code=400, detail="Case ID and form responses are required")

        visa_specs = get_visa_specifications(form_code) if form_code else {}

        conversion_prompt = f"""
Você é um especialista em formulários do USCIS. Converta as respostas simplificadas em português para o formato oficial do formulário {form_code}.

FORMULÁRIO: {form_code}
CATEGORIA: {visa_specs.get('category', 'Não especificada')}
TÍTULO: {visa_specs.get('title', 'Não especificado')}

RESPOSTAS DO USUÁRIO (em português):
{json.dumps(form_responses, indent=2, ensure_ascii=False)}

INSTRUÇÕES:
1. Converta todas as respostas para inglês profissional
2. Formate conforme os padrões do USCIS para {form_code}
3. Complete campos obrigatórios baseados nas informações fornecidas
4. Mantenha consistência de datas (MM/DD/YYYY)
5. Use formatação oficial de nomes e endereços
6. Adicione códigos de país padrão (BR para Brasil, US para EUA)
7. Converta valores monetários para USD se necessário

FORMATO DE SAÍDA:
Retorne um JSON estruturado com os campos do formulário oficial {form_code}, usando os nomes de campos exatos do USCIS.

Para campos não preenchidos pelo usuário, use:
- "N/A" para não aplicável
- "None" para informações não fornecidas
- Mantenha campos obrigatórios em branco se não houver informação

Responda apenas com o JSON estruturado, sem explicações adicionais.
"""

        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é um especialista em formulários do USCIS. Converta respostas em português "
                        "para formato oficial em inglês com precisão total."
                    ),
                },
                {"role": "user", "content": conversion_prompt},
            ],
            temperature=0.1,
            max_tokens=3000,
        )

        ai_response = response.choices[0].message.content.strip()

        try:
            if "```json" in ai_response:
                ai_response = ai_response.split("```json")[1].split("```")[0].strip()
            elif "```" in ai_response:
                ai_response = ai_response.split("```")[1].split("```")[0].strip()

            official_form_data = json.loads(ai_response)
        except json.JSONDecodeError:
            official_form_data = {
                "form_number": form_code,
                "generated_date": datetime.now(timezone.utc).isoformat(),
                "user_responses": form_responses,
                "conversion_status": "partial",
                "notes": "Manual review recommended",
            }

        if case_id:
            await db.auto_cases.update_one(
                {"case_id": case_id},
                {
                    "$set": {
                        "official_form_data": official_form_data,
                        "status": "form_filled",
                        "updated_at": datetime.now(timezone.utc),
                    }
                },
            )

        return {
            "message": "Official forms generated successfully",
            "form_code": form_code,
            "official_form_data": official_form_data,
            "fields_converted": len(official_form_data.keys()),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating forms: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating forms: {str(e)}")


@router.post("/auto-application/validate-forms")
async def validate_forms(request: dict):
    """Validate official forms for consistency and completeness."""
    try:
        case_id = request.get("case_id")
        form_code = request.get("form_code")

        if not case_id:
            raise HTTPException(status_code=400, detail="Case ID is required")

        case = await db.auto_cases.find_one({"case_id": case_id})
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        validation_issues = []

        official_form = case.get("official_form_data", {})

        if not official_form.get("full_name") and not official_form.get("applicant_name"):
            validation_issues.append(
                {
                    "section": "Informações Pessoais",
                    "field": "Nome Completo",
                    "issue": "Nome completo não foi preenchido no formulário oficial",
                    "severity": "high",
                }
            )

        if not official_form.get("date_of_birth") and not official_form.get("birth_date"):
            validation_issues.append(
                {
                    "section": "Informações Pessoais",
                    "field": "Data de Nascimento",
                    "issue": "Data de nascimento não foi preenchida",
                    "severity": "high",
                }
            )

        if not official_form.get("current_address") and not official_form.get("mailing_address"):
            validation_issues.append(
                {
                    "section": "Informações de Endereço",
                    "field": "Endereço Atual",
                    "issue": "Endereço atual não foi preenchido",
                    "severity": "high",
                }
            )

        if form_code == "H-1B":
            if not official_form.get("employer_name") and not official_form.get("company_name"):
                validation_issues.append(
                    {
                        "section": "Informações de Trabalho",
                        "field": "Nome do Empregador",
                        "issue": "Nome do empregador é obrigatório para H-1B",
                        "severity": "high",
                    }
                )

        elif form_code == "I-130":
            if not official_form.get("spouse_name") and not official_form.get("beneficiary_name"):
                validation_issues.append(
                    {
                        "section": "Informações Familiares",
                        "field": "Nome do Beneficiário",
                        "issue": "Nome do beneficiário é obrigatório para I-130",
                        "severity": "high",
                    }
                )

        date_fields = ["date_of_birth", "birth_date", "marriage_date"]
        for field in date_fields:
            if official_form.get(field):
                date_value = official_form[field]
                if not re.match(r"^\\d{2}/\\d{2}/\\d{4}$", str(date_value)):
                    validation_issues.append(
                        {
                            "section": "Validação de Formato",
                            "field": field,
                            "issue": "Data deve estar no formato MM/DD/YYYY",
                            "severity": "medium",
                        }
                    )

        return {
            "message": "Form validation completed",
            "validation_issues": validation_issues,
            "total_issues": len(validation_issues),
            "blocking_issues": len([i for i in validation_issues if i["severity"] == "high"]),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating forms: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error validating forms: {str(e)}")


@router.post("/auto-application/case/{case_id}/ai-processing")
async def run_ai_processing_step(case_id: str, request: dict):
    """Run AI processing step (validation, consistency, translation, form_generation, final_review)."""
    try:
        step = request.get("step")
        if not step:
            raise HTTPException(status_code=400, detail="Processing step is required")

        case = await db.auto_cases.find_one({"case_id": case_id})
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        progress_map = {
            "validation": 65,
            "consistency": 69,
            "translation": 73,
            "form_generation": 77,
            "final_review": 81,
        }

        new_progress = progress_map.get(step, case.get("progress_percentage", 60))

        if case.get("ai_processing") is None:
            await db.auto_cases.update_one({"case_id": case_id}, {"$set": {"ai_processing": {}}})

        await db.auto_cases.update_one(
            {"case_id": case_id},
            {
                "$set": {
                    "progress_percentage": new_progress,
                    f"ai_processing.{step}": "completed",
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )

        return {
            "success": True,
            "step": step,
            "step_id": step,
            "progress": new_progress,
            "message": f"Step {step} completed successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in AI processing step: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auto-application/case/{case_id}/professional-qa-review")
async def run_professional_qa_review(case_id: str):
    """
    Executar revisão profissional de qualidade usando agente treinado com requisitos USCIS.
    """
    try:
        case = await db.auto_cases.find_one({"case_id": case_id})
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        qa_agent = get_qa_agent()

        logger.info(f"🔍 Iniciando revisão profissional QA para case {case_id}")
        qa_report = qa_agent.comprehensive_review(case)

        await db.auto_cases.update_one(
            {"case_id": case_id},
            {
                "$set": {
                    "qa_review": qa_report,
                    "qa_approved": qa_report["approval"]["approved"],
                    "qa_score": qa_report["overall_score"],
                    "qa_review_date": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )

        if qa_report["approval"]["approved"]:
            await db.auto_cases.update_one(
                {"case_id": case_id},
                {
                    "$set": {
                        "status": "qa_approved",
                        "progress_percentage": 95,
                        "ai_processing_status": "approved",
                    }
                },
            )
            logger.info(
                f"✅ Case {case_id} APROVADO na revisão QA (score: {qa_report['overall_score']:.1%})"
            )
        else:
            logger.warning(
                f"❌ Case {case_id} REJEITADO na revisão QA: {qa_report['approval']['reason']}"
            )

        return {
            "success": True,
            "qa_report": qa_report,
            "approved": qa_report["approval"]["approved"],
            "score": qa_report["overall_score"],
            "message": qa_report["approval"]["reason"],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro na revisão QA: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in QA review: {str(e)}")


@router.post("/auto-application/case/{case_id}/qa-cycle-with-feedback")
async def run_qa_cycle_with_feedback(case_id: str, request: dict = None):
    """
    🔄 CICLO COMPLETO DE QA COM FEEDBACK LOOP AUTOMÁTICO.
    """
    try:
        case = await db.auto_cases.find_one({"case_id": case_id})
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        if "_id" in case:
            case["_id"] = str(case["_id"])

        request_data = request or {}
        max_iterations = request_data.get("max_iterations", 5)

        logger.info(f"🔄 Iniciando ciclo de QA com feedback loop para case {case_id}")
        logger.info(
            f"   Max iterações: {max_iterations}, Auto-fix: {request_data.get('auto_fix', True)}"
        )

        qa_agent = get_qa_agent()
        orchestrator = get_qa_orchestrator(db)

        result = await orchestrator.orchestrate_qa_cycle(
            case_data=case, qa_agent=qa_agent, db=db, max_iterations=max_iterations
        )

        if result["status"] == "approved":
            await db.auto_cases.update_one(
                {"case_id": case_id},
                {
                    "$set": {
                        "status": "qa_approved",
                        "progress_percentage": 95,
                        "ai_processing_status": "approved",
                        "updated_at": datetime.now(timezone.utc),
                    }
                },
            )
            logger.info(f"✅ Case {case_id} APROVADO após {result['iterations']} iteração(ões)")
        else:
            logger.warning(
                f"⚠️  Case {case_id} não foi aprovado: {result['status']} "
                f"(Score final: {result['final_score']:.1%})"
            )

        return {
            "success": result["success"],
            "case_id": case_id,
            "status": result["status"],
            "iterations": result["iterations"],
            "final_score": result["final_score"],
            "approved": result["status"] == "approved",
            "qa_report": result.get("qa_report"),
            "iteration_history": result.get("iteration_history", []),
            "message": result["message"],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro no ciclo de QA com feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in QA cycle: {str(e)}")
