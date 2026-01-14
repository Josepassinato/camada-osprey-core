import json
import logging
import os
import re
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from backend.visa.specifications import get_visa_specifications
from core.auth import get_current_user_optional
from core.database import db
from services.cases import update_case_status_and_progress

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")

try:
    from backend.compliance.legal_rules import apply_legal_rules

    LEGAL_RULES_AVAILABLE = True
    logger.info("✅ Immigration Legal Rules loaded successfully")
except ImportError as e:
    LEGAL_RULES_AVAILABLE = False
    logger.warning(f"⚠️  Immigration Legal Rules not available: {e}")


@router.post("/case/{case_id}/friendly-form")
async def submit_friendly_form(
    case_id: str, request: dict, current_user=Depends(get_current_user_optional)
):
    """
    Submit and validate friendly form data with AI analysis.
    This endpoint:
    1. Receives data from user-friendly form (in Portuguese or user's language)
    2. Validates data completeness and coherence using AI
    3. Notifies user of any missing or incorrect information
    4. Saves validated data for later use in official USCIS forms
    """
    try:
        # Extract form data from request
        friendly_form_data = request.get("friendly_form_data", {})
        basic_data = request.get("basic_data", {})

        # 🆕 BUG FIX DEBUG: Log incoming data
        logger.info(f"🔍 Received friendly_form_data: {len(friendly_form_data)} keys")
        logger.info(f"🔍 Keys: {list(friendly_form_data.keys())}")

        if not case_id:
            raise HTTPException(status_code=400, detail="case_id is required")

        # Get case from database
        query = {"case_id": case_id}
        if current_user:
            query["user_id"] = current_user["id"]

        case = await db.auto_cases.find_one(query)
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        # Get visa type for specific validation
        # 🆕 BUG P1 FIX: Improved auto-detect form_code from friendly form data
        visa_type = case.get("form_code", "N/A")

        logger.info(f"🔍 Current form_code for case {case_id}: {visa_type}")

        if not visa_type or visa_type == "N/A":
            # Try to detect from friendly form data
            detected_visa = None
            status_atual = str(friendly_form_data.get("status_atual", "")).upper()
            status_solicitado = str(friendly_form_data.get("status_solicitado", "")).upper()

            logger.info(
                f"🔍 Attempting auto-detection - status_atual: {status_atual}, status_solicitado: {status_solicitado}"
            )

            # Enhanced detection logic with better patterns
            # I-539: Extension or Change of Status
            if "B-2" in status_atual or "B2" in status_atual or "TOURIST" in status_atual:
                if (
                    "EXTENSION" in status_solicitado
                    or "EXTENSÃO" in status_solicitado
                    or "B-2" in status_solicitado
                ):
                    detected_visa = "I-539"
                    logger.info("✅ Detected I-539 (B-2 Extension)")

            # Check if explicitly asking for I-539
            if "I-539" in status_solicitado or "I539" in status_solicitado:
                detected_visa = "I-539"
                logger.info("✅ Detected I-539 (Explicit)")

            # F-1 Student Visa
            if (
                "F-1" in status_solicitado
                or "F1" in status_solicitado
                or "STUDENT" in status_solicitado
            ):
                detected_visa = "I-539"  # F-1 uses I-539 for status change
                logger.info("✅ Detected I-539 (F-1 Status Change)")

            # H-1B Work Visa
            if "H-1B" in status_solicitado or "H1B" in status_solicitado:
                detected_visa = "I-539"  # H-1B also uses I-539 for extension
                logger.info("✅ Detected I-539 (H-1B Extension)")

            # O-1 Extraordinary Ability
            if "O-1" in status_solicitado or "O1" in status_solicitado:
                detected_visa = "O-1"
                logger.info("✅ Detected O-1")

            # EB-1A Extraordinary Ability (Immigrant)
            if "EB-1A" in status_solicitado or "EB1A" in status_solicitado:
                detected_visa = "I-140"
                logger.info("✅ Detected I-140 (EB-1A)")

            # I-589 Asylum
            if (
                "ASYLUM" in status_solicitado
                or "ASILO" in status_solicitado
                or "I-589" in status_solicitado
            ):
                detected_visa = "I-589"
                logger.info("✅ Detected I-589 (Asylum)")

            if detected_visa:
                # Update case with detected visa type
                result = await db.auto_cases.update_one(
                    {"case_id": case_id},
                    {
                        "$set": {
                            "form_code": detected_visa,
                            "updated_at": datetime.now(timezone.utc),
                        }
                    },
                )
                visa_type = detected_visa
                logger.info(
                    "✅ BUG P1 FIX: Auto-detected and saved form_code: "
                    f"{detected_visa} for case {case_id} (matched: {result.matched_count}, modified: {result.modified_count})"
                )
            else:
                logger.warning(f"⚠️ Could not auto-detect form_code for case {case_id}")

        # If still not detected, use I-539 as default (most common)
        if not visa_type or visa_type == "N/A":
            visa_type = "I-539"
            logger.info(f"ℹ️ Using default form_code: I-539 for case {case_id}")

        # STEP 1: Apply Legal Rules Validation (CRITICAL - From Immigration Attorney)
        legal_validation_issues = []
        legal_rules_passed = True

        if LEGAL_RULES_AVAILABLE:
            logger.info(f"Applying legal rules validation for visa type: {visa_type}")
            try:
                legal_rules_passed, legal_messages = apply_legal_rules(
                    friendly_form_data, visa_type
                )
                if not legal_rules_passed or legal_messages:
                    for message in legal_messages:
                        # Categorize messages by type
                        if message.startswith("❌"):
                            legal_validation_issues.append(
                                {
                                    "field": "legal_requirement",
                                    "issue": message,
                                    "severity": "critical",
                                    "type": "legal_rule",
                                }
                            )
                        elif message.startswith("⚠️") or message.startswith("🚨"):
                            legal_validation_issues.append(
                                {
                                    "field": "legal_warning",
                                    "issue": message,
                                    "severity": "warning",
                                    "type": "legal_rule",
                                }
                            )
                        else:
                            legal_validation_issues.append(
                                {
                                    "field": "legal_info",
                                    "issue": message,
                                    "severity": "info",
                                    "type": "legal_rule",
                                }
                            )
                    logger.warning(
                        f"Legal validation found {len(legal_validation_issues)} issues/warnings"
                    )
            except Exception as e:
                logger.error(f"Error applying legal rules: {e}")
                legal_validation_issues.append(
                    {
                        "field": "legal_validation",
                        "issue": f"⚠️ Erro ao aplicar regras jurídicas: {str(e)}",
                        "severity": "warning",
                        "type": "system_error",
                    }
                )

        # STEP 2: AI Validation - Check completeness and coherence
        logger.info(f"Starting AI validation for case {case_id}, visa type: {visa_type}")

        validation_result = await validate_friendly_form_ai(
            case=case,
            friendly_form_data=friendly_form_data,
            basic_data=basic_data,
            visa_type=visa_type,
        )

        # STEP 3: Merge legal validation with AI validation
        validation_status = validation_result.get("overall_status", "needs_review")
        validation_issues = legal_validation_issues + validation_result.get("validation_issues", [])

        # If legal rules failed, override status to needs_review
        if not legal_rules_passed:
            validation_status = "needs_review"
            logger.warning(f"Legal rules validation failed for case {case_id}")

        completion_percentage = validation_result.get("completion_percentage", 0)

        # STEP 3: Save data to database (even if validation found issues)
        # Merge basic_data safely
        existing_basic_data = case.get("basic_data")
        if existing_basic_data is None or not isinstance(existing_basic_data, dict):
            existing_basic_data = {}
        merged_basic_data = {**existing_basic_data, **basic_data}

        update_data = {
            "simplified_form_responses": friendly_form_data,
            "basic_data": merged_basic_data,
            "friendly_form_validation": {
                "status": validation_status,
                "completion_percentage": completion_percentage,
                "validation_date": datetime.now(timezone.utc),
                "issues": validation_issues,
                "legal_rules_applied": LEGAL_RULES_AVAILABLE,
                "legal_rules_passed": legal_rules_passed,
                "total_legal_issues": len(legal_validation_issues),
            },
            "updated_at": datetime.now(timezone.utc),
        }

        # 🆕 P1-5: Update progress status
        if completion_percentage >= 100:
            await update_case_status_and_progress(case_id, "friendly-form-complete", "auto_cases")
        elif completion_percentage >= 50:
            await update_case_status_and_progress(case_id, "friendly_form_partial", "auto_cases")

        # Update progress based on completion
        if completion_percentage >= 90:
            update_data["progress_percentage"] = 50
            update_data["current_step"] = "friendly-form-complete"
        elif completion_percentage >= 50:
            update_data["progress_percentage"] = 45
            update_data["current_step"] = "friendly-form-partial"

        # 🆕 BUG FIX DEBUG: Log what we're saving
        logger.info(
            f"🔍 About to save simplified_form_responses with {len(friendly_form_data)} fields"
        )
        logger.info(f"🔍 Sample data: {dict(list(friendly_form_data.items())[:3])}")

        result = await db.auto_cases.update_one({"case_id": case_id}, {"$set": update_data})

        logger.info(
            f"✅ Friendly form data saved for case {case_id} (matched: {result.matched_count}, modified: {result.modified_count})"
        )

        # 🆕 BUG FIX DEBUG: Verify data was saved
        saved_case = await db.auto_cases.find_one({"case_id": case_id})
        saved_simplified = saved_case.get("simplified_form_responses", {})
        logger.info(
            f"🔍 Verification: simplified_form_responses has {len(saved_simplified)} fields after save"
        )
        if len(saved_simplified) == 0 and len(friendly_form_data) > 0:
            logger.error(
                f"⚠️ DATA LOSS DETECTED! Sent {len(friendly_form_data)} fields but saved 0!"
            )

        # STEP 4: Return validation result to user
        response = {
            "success": True,
            "case_id": case_id,
            "validation_status": validation_status,
            "completion_percentage": completion_percentage,
            "message": get_validation_message_pt(validation_status, completion_percentage),
            "validation_issues": validation_issues,
            "next_steps": get_next_steps_pt(validation_status, completion_percentage),
        }

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in friendly form submission: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing friendly form: {str(e)}")


async def validate_friendly_form_ai(
    case: dict, friendly_form_data: dict, basic_data: dict, visa_type: str
):
    """
    Enhanced AI-powered validation of friendly form data.

    TWO-STAGE VALIDATION:
    1. Programmatic validation (fast, rule-based)
    2. AI validation (slow, intelligent analysis)

    Checks for:
    - Completeness (all required fields filled)
    - Coherence (data makes sense and is consistent)
    - Format correctness (dates, emails, phone numbers)
    - Visa-specific requirements
    """
    try:
        # STAGE 1: Programmatic Validation (Fast & Reliable)
        logger.info(f"🔍 Stage 1: Programmatic validation for {visa_type}")

        programmatic_result = validate_fields_programmatically(
            friendly_form_data=friendly_form_data,
            basic_data=basic_data,
            visa_type=visa_type,
        )

        validation_issues = programmatic_result["validation_issues"]
        completion_percentage = programmatic_result["completion_percentage"]
        missing_fields = programmatic_result["missing_fields"]

        logger.info(
            f"📊 Programmatic validation: {completion_percentage}% complete, {len(validation_issues)} issues found"
        )

        # If completion is very low, skip AI validation (no point)
        if completion_percentage < 30:
            logger.warning(
                f"⚠️ Completion too low ({completion_percentage}%), skipping AI validation"
            )
            return {
                "validation_issues": validation_issues,
                "overall_status": "rejected",
                "completion_percentage": completion_percentage,
                "missing_fields": missing_fields,
                "message_to_user": "Formulário muito incompleto. Preencha pelo menos os campos básicos obrigatórios.",
            }

        # STAGE 2: AI Validation (Intelligent Analysis)
        logger.info("🤖 Stage 2: AI validation for enhanced analysis")

        # Use Emergent LLM key
        emergent_key = os.environ.get("EMERGENT_LLM_KEY")
        if not emergent_key:
            logger.warning("EMERGENT_LLM_KEY not found, using programmatic validation only")
            overall_status = determine_overall_status(completion_percentage, validation_issues)
            return {
                "validation_issues": validation_issues,
                "overall_status": overall_status,
                "completion_percentage": completion_percentage,
                "missing_fields": missing_fields,
                "message_to_user": f"Validação programática concluída. {len(missing_fields)} campos obrigatórios faltando.",
            }

        try:
            from emergentintegrations import EmergentLLM

            llm = EmergentLLM(api_key=emergent_key)
        except ImportError:
            logger.error("EmergentLLM import failed, using programmatic validation only")
            overall_status = determine_overall_status(completion_percentage, validation_issues)
            return {
                "validation_issues": validation_issues,
                "overall_status": overall_status,
                "completion_percentage": completion_percentage,
                "missing_fields": missing_fields,
                "message_to_user": f"Validação programática concluída. {len(missing_fields)} campos obrigatórios faltando.",
            }

        # Get visa-specific requirements
        try:
            visa_specs = get_visa_specifications(visa_type) if visa_type else {}
            if visa_specs is None:
                visa_specs = {}
        except Exception as spec_error:
            logger.warning(f"Could not get visa specifications: {spec_error}")
            visa_specs = {}

        validation_prompt = f"""
Você é um especialista em imigração dos EUA. Uma validação programática inicial já foi feita.

**CONTEXTO**:
- Tipo de Visto: {visa_type}
- Validação Programática: {completion_percentage}% completo
- Problemas Detectados: {len(validation_issues)} problemas
- Campos Faltando: {len(missing_fields)} campos

**DADOS DO USUÁRIO**:
Dados Básicos: {json.dumps(basic_data, indent=2, ensure_ascii=False)}
Formulário Amigável: {json.dumps(friendly_form_data, indent=2, ensure_ascii=False)}

**PROBLEMAS JÁ IDENTIFICADOS**:
{json.dumps(validation_issues[:5], indent=2, ensure_ascii=False) if validation_issues else "Nenhum problema detectado na validação inicial"}

**SUA TAREFA ADICIONAL** (além dos problemas já detectados):
1. Verificar COERÊNCIA dos dados (datas cronológicas, informações consistentes)
2. Identificar CONTRADIÇÕES ou INCONSISTÊNCIAS que a validação programática não detectou
3. Avaliar se as EXPLICAÇÕES/TEXTOS são suficientemente detalhados
4. Verificar LÓGICA do pedido (ex: motivo da mudança de status faz sentido?)
5. Sugerir MELHORIAS nos textos e respostas

**IMPORTANTE**:
- NÃO repita os problemas já listados acima
- Foque em análise semântica e coerência
- Se não encontrar problemas adicionais, retorne array vazio em "additional_issues"
- Mantenha o completion_percentage próximo ao detectado ({completion_percentage}%)

**RESPONDA EM JSON** (APENAS JSON, SEM TEXTO ADICIONAL):
{{
    "additional_issues": [
        {{
            "field": "nome_do_campo",
            "issue": "problema de coerência ou lógica",
            "severity": "warning|info",
            "suggestion": "como melhorar"
        }}
    ],
    "coherence_score": 85,
    "recommendations": [
        "Recomendação específica para melhorar a aplicação"
    ],
    "overall_assessment": "Breve avaliação geral em português"
}}
"""

        try:
            response_text = llm.chat([{"role": "user", "content": validation_prompt}])
        except Exception as e:
            logger.error(f"Error calling Emergent LLM: {e}")
            overall_status = determine_overall_status(completion_percentage, validation_issues)
            return {
                "validation_issues": validation_issues,
                "overall_status": overall_status,
                "completion_percentage": completion_percentage,
                "missing_fields": missing_fields,
                "message_to_user": "Validação programática concluída (IA indisponível).",
            }

        # Extract JSON from response
        try:
            start_idx = response_text.find("{")
            end_idx = response_text.rfind("}") + 1
            json_str = response_text[start_idx:end_idx]
            ai_response = json.loads(json_str)
        except Exception as json_error:
            logger.error(f"Could not parse AI response: {json_error}")
            overall_status = determine_overall_status(completion_percentage, validation_issues)
            return {
                "validation_issues": validation_issues,
                "overall_status": overall_status,
                "completion_percentage": completion_percentage,
                "missing_fields": missing_fields,
                "message_to_user": "Validação programática concluída (resposta IA inválida).",
            }

        additional_issues = ai_response.get("additional_issues", [])
        recommendations = ai_response.get("recommendations", [])
        coherence_score = ai_response.get("coherence_score", 85)
        overall_assessment = ai_response.get("overall_assessment", "")

        # Merge AI issues with programmatic issues
        validation_issues.extend(additional_issues)

        # Adjust completion based on coherence score
        if coherence_score < 70:
            completion_percentage = max(0, completion_percentage - 10)

        overall_status = determine_overall_status(completion_percentage, validation_issues)

        return {
            "validation_issues": validation_issues,
            "overall_status": overall_status,
            "completion_percentage": completion_percentage,
            "missing_fields": missing_fields,
            "coherence_score": coherence_score,
            "recommendations": recommendations,
            "overall_assessment": overall_assessment,
            "visa_specs": visa_specs,
        }

    except Exception as e:
        logger.error(f"Error in AI validation: {e}")
        overall_status = determine_overall_status(0, [])
        return {
            "validation_issues": [],
            "overall_status": overall_status,
            "completion_percentage": 0,
            "missing_fields": [],
            "message_to_user": "Erro no sistema de validação. Tente novamente.",
        }


def get_required_fields_by_visa_type(visa_type: str) -> dict:
    """Return required fields based on visa type"""
    visa_type = (visa_type or "").upper()

    common_fields = {
        "nome_completo": {
            "label": "Nome Completo",
            "validation": "required|min:3",
            "example": "João Silva",
        },
        "data_nascimento": {
            "label": "Data de Nascimento",
            "validation": "required|date",
            "example": "1990-01-15",
        },
        "numero_passaporte": {
            "label": "Número do Passaporte",
            "validation": "required|min:6",
            "example": "BR123456",
        },
        "pais_nascimento": {
            "label": "País de Nascimento",
            "validation": "required",
            "example": "Brasil",
        },
        "pais_cidadania": {
            "label": "País de Cidadania",
            "validation": "required",
            "example": "Brasil",
        },
    }

    if visa_type == "I-539":
        return {
            **common_fields,
            "endereco": {
                "label": "Endereço nos EUA",
                "validation": "required|min:5",
                "example": "123 Main Street, Apt 4B",
            },
            "cidade": {
                "label": "Cidade",
                "validation": "required",
                "example": "New York",
            },
            "estado": {
                "label": "Estado",
                "validation": "required|length:2",
                "example": "NY",
            },
            "cep": {
                "label": "CEP/ZIP Code",
                "validation": "required",
                "example": "10001",
            },
            "telefone": {
                "label": "Telefone",
                "validation": "required",
                "example": "+1 555-1234",
            },
            "status_atual": {
                "label": "Status de Visto Atual",
                "validation": "required",
                "example": "F-1",
            },
            "status_solicitado": {
                "label": "Status de Visto Solicitado",
                "validation": "required",
                "example": "H-1B",
            },
            "data_entrada_eua": {
                "label": "Data de Entrada nos EUA",
                "validation": "required|date",
                "example": "2020-08-15",
            },
            "numero_i94": {
                "label": "Número I-94",
                "validation": "required|numeric",
                "example": "1234567890",
            },
        }

    if visa_type == "I-589":
        return {
            **common_fields,
            "data_chegada_eua": {
                "label": "Data de Chegada nos EUA",
                "validation": "required|date",
                "example": "2023-01-15",
            },
            "numero_i94": {
                "label": "Número I-94",
                "validation": "required|numeric",
                "example": "1234567890",
            },
            "nacionalidade": {
                "label": "Nacionalidade",
                "validation": "required",
                "example": "Brazilian",
            },
            "motivo_asilo": {
                "label": "Motivo do Pedido de Asilo",
                "validation": "required|min:50",
                "example": "Perseguição política no país de origem...",
            },
            "endereco": {
                "label": "Endereço Atual nos EUA",
                "validation": "required|min:5",
                "example": "123 Main Street",
            },
            "telefone": {
                "label": "Telefone",
                "validation": "required",
                "example": "+1 555-1234",
            },
        }

    if visa_type in ["EB-1A", "EB1A", "I-140"]:
        return {
            **common_fields,
            "area_expertise": {
                "label": "Área de Expertise",
                "validation": "required|min:3",
                "example": "Tecnologia da Informação",
            },
            "realizacoes": {
                "label": "Realizações Extraordinárias",
                "validation": "required|min:100",
                "example": "Publicações, prêmios, patentes...",
            },
            "publicacoes": {
                "label": "Publicações",
                "validation": "optional",
                "example": "Lista de publicações acadêmicas",
            },
            "premios": {
                "label": "Prêmios e Reconhecimentos",
                "validation": "optional",
                "example": "Prêmios nacionais ou internacionais",
            },
        }

    return common_fields


def get_required_fields_by_visa_type_old(visa_type: str) -> dict:
    return get_required_fields_by_visa_type(visa_type)


def validate_fields_programmatically(
    friendly_form_data: dict, basic_data: dict, visa_type: str
) -> dict:
    """
    Perform programmatic validation before AI validation
    This is faster and more reliable for basic checks

    Returns: dict with validation_issues, completion_percentage, missing_fields
    """
    required_fields = get_required_fields_by_visa_type(visa_type)
    validation_issues = []
    missing_fields = []
    filled_count = 0
    total_required = len(required_fields)

    all_data = {**basic_data, **friendly_form_data}

    for field_name, field_config in required_fields.items():
        field_value = all_data.get(field_name, "")
        field_label = field_config["label"]
        validation_rules = field_config["validation"]

        # Check if field is empty
        if not field_value or (isinstance(field_value, str) and field_value.strip() == ""):
            if "required" in validation_rules:
                missing_fields.append(field_name)
                validation_issues.append(
                    {
                        "field": field_name,
                        "field_label": field_label,
                        "issue": "Campo obrigatório não preenchido",
                        "severity": "error",
                        "suggestion": f"Por favor, preencha o campo '{field_label}'. Exemplo: {field_config.get('example', 'N/A')}",
                    }
                )
        else:
            filled_count += 1

            if "email" in validation_rules:
                if not re.match(
                    r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", str(field_value)
                ):
                    validation_issues.append(
                        {
                            "field": field_name,
                            "field_label": field_label,
                            "issue": "Formato de email inválido",
                            "severity": "error",
                            "suggestion": f"Use um email válido, como: {field_config.get('example', 'usuario@example.com')}",
                        }
                    )

            if "date" in validation_rules:
                if not re.match(r"^\\d{4}-\\d{2}-\\d{2}$", str(field_value)):
                    validation_issues.append(
                        {
                            "field": field_name,
                            "field_label": field_label,
                            "issue": "Formato de data inválido",
                            "severity": "error",
                            "suggestion": f"Use o formato YYYY-MM-DD, como: {field_config.get('example', '1990-01-15')}",
                        }
                    )

            if "numeric" in validation_rules:
                if not str(field_value).replace("-", "").isdigit():
                    validation_issues.append(
                        {
                            "field": field_name,
                            "field_label": field_label,
                            "issue": "Deve conter apenas números",
                            "severity": "warning",
                            "suggestion": f"Use apenas números, como: {field_config.get('example', '123456')}",
                        }
                    )

            if "min:" in validation_rules:
                min_length = int(validation_rules.split("min:")[1].split("|")[0])
                if len(str(field_value)) < min_length:
                    validation_issues.append(
                        {
                            "field": field_name,
                            "field_label": field_label,
                            "issue": f"Muito curto (mínimo {min_length} caracteres)",
                            "severity": "warning",
                            "suggestion": f"Forneça mais detalhes. Exemplo: {field_config.get('example', 'N/A')}",
                        }
                    )

    base_completion = int((filled_count / total_required) * 100) if total_required > 0 else 0

    format_errors = [
        i
        for i in validation_issues
        if i.get("severity") == "error" and i.get("issue") != "Campo obrigatório não preenchido"
    ]
    format_warnings = [i for i in validation_issues if i.get("severity") == "warning"]

    penalty = (len(format_errors) * 5) + (len(format_warnings) * 2)
    completion_percentage = max(0, base_completion - penalty)

    return {
        "validation_issues": validation_issues,
        "missing_fields": missing_fields,
        "completion_percentage": completion_percentage,
        "total_required": total_required,
        "filled_count": filled_count,
    }


def determine_overall_status(completion_percentage: int, validation_issues: list) -> str:
    """Determine overall validation status based on completion and issues"""
    error_count = len([i for i in validation_issues if i.get("severity") == "error"])

    if error_count > 0:
        if completion_percentage < 70:
            return "rejected"
        return "needs_review"

    if completion_percentage >= 90:
        return "approved"
    if completion_percentage >= 70:
        return "needs_review"
    return "rejected"


def get_validation_message_pt(status: str, completion: int) -> str:
    """Get user-friendly message in Portuguese based on validation status"""
    if status == "approved" and completion >= 90:
        return "✅ Excelente! Seu formulário está completo e coerente. Você pode prosseguir para a próxima etapa."
    if status == "needs_review":
        return f"⚠️ Seu formulário está {completion}% completo. Por favor, revise as informações destacadas abaixo."
    return f"❌ Seu formulário precisa de mais informações ({completion}% completo). Por favor, preencha os campos faltantes."


def get_next_steps_pt(status: str, completion: int) -> list:
    """Get next steps recommendations in Portuguese"""
    if status == "approved" and completion >= 90:
        return [
            "Revisar seus dados uma última vez",
            "Clicar em 'Continuar' para gerar os formulários oficiais",
            "Upload de documentos de suporte (se necessário)",
        ]
    if status == "needs_review":
        return [
            "Revisar e corrigir as informações destacadas",
            "Preencher campos faltantes",
            "Verificar datas e formatos de dados",
        ]
    return [
        "Preencher todos os campos obrigatórios",
        "Revisar informações básicas",
        "Garantir que todos os dados estão corretos",
    ]


@router.get("/friendly-form/available-visas")
async def get_available_visa_types():
    """
    Retorna lista de todos os tipos de visto com estruturas de formulário disponíveis

    Returns:
        Lista de vistos disponíveis com informações básicas
    """
    try:
        visa_types = [
            {
                "code": "I-539",
                "name": "Extensão/Mudança de Status Geral",
                "category": "Não-Imigrante",
                "description": "Para extensão ou mudança de qualquer status não-imigrante",
                "estimated_time": "20-30 minutos",
            },
            {
                "code": "F-1",
                "name": "Visto de Estudante",
                "category": "Estudante",
                "description": "Para estudantes em programas acadêmicos",
                "estimated_time": "25-35 minutos",
            },
            {
                "code": "H-1B",
                "name": "Visto de Trabalho Especializado",
                "category": "Trabalho",
                "description": "Para profissionais em ocupações especializadas",
                "estimated_time": "30-40 minutos",
            },
            {
                "code": "B-2",
                "name": "Visto de Turista",
                "category": "Turismo",
                "description": "Extensão de visto de turista/visitante",
                "estimated_time": "15-20 minutos",
            },
            {
                "code": "L-1",
                "name": "Transferência Intra-Empresa",
                "category": "Trabalho",
                "description": "Para executivos e gerentes transferidos",
                "estimated_time": "30-40 minutos",
            },
            {
                "code": "O-1",
                "name": "Habilidade Extraordinária (O-1)",
                "category": "Habilidade Especial",
                "description": "Para indivíduos com habilidade extraordinária",
                "estimated_time": "35-45 minutos",
            },
            {
                "code": "I-589",
                "name": "Pedido de Asilo",
                "category": "Asilo/Proteção",
                "description": "Para solicitantes de asilo político",
                "estimated_time": "45-60 minutos",
            },
            {
                "code": "EB-1A",
                "name": "Imigrante - Habilidade Extraordinária",
                "category": "Imigrante",
                "description": "Green Card baseado em habilidade extraordinária",
                "estimated_time": "60-90 minutos",
            },
        ]

        return {
            "success": True,
            "visa_types": visa_types,
            "total": len(visa_types),
        }

    except Exception as e:
        logger.error(f"Error getting available visa types: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting visa types: {str(e)}")


@router.get("/friendly-form/structure/{visa_type}")
async def get_friendly_form_structure_endpoint(visa_type: str):
    """
    Retorna a estrutura completa do formulário amigável para o tipo de visto

    Este endpoint fornece ao frontend a estrutura exata do formulário que deve ser apresentado
    ao usuário, garantindo que TODOS os campos obrigatórios do formulário oficial USCIS sejam coletados.

    Args:
        visa_type: Código do visto (I-539, I-589, EB-1A, F-1, H-1B, B-2, L-1, O-1, etc.)

    Returns:
        Estrutura completa do formulário com seções, campos, validações e mapeamento para formulário oficial
    """
    try:
        from backend.forms.structures import get_friendly_form_structure

        structure = get_friendly_form_structure(visa_type)

        return {
            "success": True,
            "visa_type": visa_type,
            "structure": structure,
            "message": f"Estrutura do formulário para {visa_type} obtida com sucesso",
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting friendly form structure: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting form structure: {str(e)}")
