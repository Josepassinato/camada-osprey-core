import logging
import os
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from backend.visa.specifications import (
    get_visa_specifications,
)
from core.database import db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


@router.post("/auto-application/generate-package")
async def generate_final_package(request: dict):
    """Generate final document package for download."""
    try:
        case_id = request.get("case_id")
        package_type = request.get("package_type", "complete")

        if not case_id:
            raise HTTPException(status_code=400, detail="Case ID is required")

        case = await db.auto_cases.find_one({"case_id": case_id})
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        skip_payment = os.getenv("SKIP_PAYMENT_FOR_TESTING", "FALSE").upper() == "TRUE"

        if not skip_payment and case.get("payment_status") != "completed":
            raise HTTPException(
                status_code=400, detail="Payment required before package generation"
            )
        if skip_payment:
            logger.warning(f"⚠️ BUG P2 FIX: Skipping payment check for case {case_id} (TEST MODE)")

        form_code = case.get("form_code")
        visa_specs = get_visa_specifications(form_code) if form_code else {}

        package_contents = {
            "case_id": case_id,
            "form_code": form_code,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "package_type": package_type,
            "files": [],
            "visa_specs": visa_specs,
        }

        if case.get("official_form_data"):
            package_contents["files"].append(
                {
                    "name": f"{form_code}_Official_Form.pdf",
                    "type": "official_form",
                    "description": f"Formulário oficial {form_code} preenchido em inglês",
                }
            )

        package_contents["files"].append(
            {
                "name": "Document_Checklist.pdf",
                "type": "checklist",
                "description": "Lista completa de documentos necessários",
            }
        )

        package_contents["files"].append(
            {
                "name": "Submission_Instructions.pdf",
                "type": "instructions",
                "description": "Instruções passo-a-passo para submissão",
            }
        )

        if case.get("user_story_text"):
            package_contents["files"].append(
                {
                    "name": "User_Story_Summary.pdf",
                    "type": "summary",
                    "description": "Resumo da sua história e fatos extraídos",
                }
            )

        if package_type in ["complete", "premium"]:
            package_contents["files"].extend(
                [
                    {
                        "name": "Cover_Letter_Template.docx",
                        "type": "template",
                        "description": "Modelo de carta de apresentação",
                    },
                    {
                        "name": "RFE_Response_Guide.pdf",
                        "type": "guide",
                        "description": "Guia para responder Request for Evidence",
                    },
                    {
                        "name": "Interview_Preparation.pdf",
                        "type": "guide",
                        "description": "Guia de preparação para entrevista",
                    },
                ]
            )

        download_url = f"/downloads/packages/OSPREY-{form_code}-{case_id}-{package_type}.zip"

        await db.auto_cases.update_one(
            {"case_id": case_id},
            {
                "$set": {
                    "final_package_generated": True,
                    "final_package_url": download_url,
                    "package_contents": package_contents,
                    "status": "completed",
                    "current_step": "finalized",
                    "progress_percentage": 100,
                    "completed_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )

        logger.info(
            f"✅ BUG P2 FIX: Case {case_id} finalized with status='completed', progress=100%"
        )

        return {
            "message": "Package generated successfully",
            "download_url": download_url,
            "package_contents": package_contents,
            "total_files": len(package_contents["files"]),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating package: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating package: {str(e)}")


@router.get("/auto-application/case/{case_id}/submission-instructions")
async def get_submission_instructions(case_id: str):
    """Generate complete USCIS submission instructions for the case."""
    try:
        case = await db.auto_cases.find_one({"case_id": case_id})
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        form_code = case.get("form_code")
        uscis_info = get_uscis_filing_info(form_code)

        instructions = {
            "case_id": case_id,
            "form_code": form_code,
            "submission_info": uscis_info,
            "required_documents": get_required_documents_checklist(form_code),
            "signature_guide": get_signature_instructions(form_code),
            "payment_info": get_payment_instructions(form_code),
            "submission_steps": get_step_by_step_guide(form_code),
            "important_notes": get_important_submission_notes(form_code),
        }

        return instructions

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating submission instructions: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error generating submission instructions: {str(e)}"
        )


def get_uscis_filing_info(form_code: str) -> dict:
    """Get USCIS filing information based on form type."""
    filing_info = {
        "H-1B": {
            "filing_office": "USCIS Vermont Service Center",
            "address": {
                "name": "USCIS Vermont Service Center",
                "street": "75 Lower Welden Street",
                "city": "St. Albans",
                "state": "VT",
                "zip": "05479-0001",
            },
            "po_box": "USCIS, Attn: I-129 H-1B, P.O. Box 6500, St. Albans, VT 05479-6500",
            "filing_fee": "$555",
            "additional_fees": {
                "Anti-Fraud Fee": "$500",
                "ACWIA Fee": "$750 (companies with 1-25 employees) or $1,500 (companies with 26+ employees)",
                "Premium Processing (optional)": "$2,805",
            },
            "processing_time": "2-4 months (regular) or 15 calendar days (premium)",
        },
        "B-1/B-2": {
            "filing_office": "Consulado Americano no Brasil",
            "address": {
                "name": "Consulado Geral dos EUA",
                "street": "Avenida das Nações, Quadra 801, Lote 3",
                "city": "Brasília",
                "state": "DF",
                "zip": "70403-900",
            },
            "online_application": "https://ceac.state.gov/genniv/",
            "filing_fee": "$185",
            "additional_fees": {
                "Reciprocity Fee": "Varies by country - $0 for Brazil",
                "Courier Fee (optional)": "Approximately $15",
            },
            "processing_time": "3-5 dias úteis após a entrevista",
        },
        "F-1": {
            "filing_office": "Consulado Americano no Brasil",
            "address": {
                "name": "Consulado Geral dos EUA",
                "street": "Avenida das Nações, Quadra 801, Lote 3",
                "city": "Brasília",
                "state": "DF",
                "zip": "70403-900",
            },
            "online_application": "https://ceac.state.gov/genniv/",
            "filing_fee": "$185",
            "additional_fees": {"SEVIS I-901 Fee": "$350", "Reciprocity Fee": "$0 for Brazil"},
            "processing_time": "3-5 dias úteis após a entrevista",
        },
    }

    return filing_info.get(
        form_code,
        {
            "filing_office": "USCIS National Benefits Center",
            "address": {
                "name": "USCIS National Benefits Center",
                "street": "13770 EDS Drive",
                "city": "Herndon",
                "state": "VA",
                "zip": "20171",
            },
            "filing_fee": "Consulte o site do USCIS",
            "processing_time": "Varia por tipo de formulário",
        },
    )


def get_required_documents_checklist(form_code: str) -> list:
    """Get required documents checklist based on form type."""
    checklists = {
        "H-1B": [
            {
                "item": "Formulário I-129 completo e assinado",
                "required": True,
                "page": "Última página",
            },
            {"item": "Diploma de ensino superior", "required": True, "notes": "Cópia autenticada"},
            {
                "item": "Histórico acadêmico",
                "required": True,
                "notes": "Tradução certificada se necessário",
            },
            {
                "item": "Carta da empresa patrocinadora",
                "required": True,
                "notes": "Detalhando a posição",
            },
            {
                "item": "Labor Condition Application (LCA) aprovada",
                "required": True,
                "notes": "Certificada pelo DOL",
            },
            {
                "item": "Evidência de qualificações",
                "required": True,
                "notes": "Experiência relevante",
            },
            {
                "item": "Cópia do passaporte",
                "required": True,
                "notes": "Válido por pelo menos 6 meses",
            },
            {"item": "Cheque ou money order", "required": True, "notes": "Valor total das taxas"},
        ],
        "B-1/B-2": [
            {
                "item": "Formulário DS-160 online completo",
                "required": True,
                "notes": "Imprimir página de confirmação",
            },
            {
                "item": "Passaporte válido",
                "required": True,
                "notes": "Válido por pelo menos 6 meses",
            },
            {
                "item": "Foto 5x5cm recente",
                "required": True,
                "notes": "Fundo branco, conforme especificações",
            },
            {
                "item": "Comprovante de renda/vínculos no Brasil",
                "required": True,
                "notes": "Holerites, declaração IR",
            },
            {"item": "Itinerário de viagem", "required": False, "notes": "Se já definido"},
            {
                "item": "Carta convite (se aplicável)",
                "required": False,
                "notes": "Para visitas familiares/negócios",
            },
            {"item": "Comprovante de pagamento da taxa", "required": True, "notes": "$185"},
        ],
        "F-1": [
            {
                "item": "Formulário DS-160 online completo",
                "required": True,
                "notes": "Imprimir página de confirmação",
            },
            {
                "item": "Formulário I-20 da instituição",
                "required": True,
                "notes": "Assinado e válido",
            },
            {
                "item": "Passaporte válido",
                "required": True,
                "notes": "Válido por pelo menos 6 meses",
            },
            {"item": "Foto 5x5cm recente", "required": True, "notes": "Fundo branco"},
            {"item": "Comprovante de pagamento SEVIS I-901", "required": True, "notes": "$350"},
            {
                "item": "Comprovantes financeiros",
                "required": True,
                "notes": "Suficientes para cobrir estudos",
            },
            {"item": "Histórico escolar", "required": True, "notes": "Tradução certificada"},
            {
                "item": "Comprovante de proficiência em inglês",
                "required": False,
                "notes": "TOEFL, IELTS, etc.",
            },
        ],
    }

    return checklists.get(form_code, [])


def get_signature_instructions(form_code: str) -> dict:
    """Get signature instructions for the form."""
    signature_guides = {
        "H-1B": {
            "petitioner_signature": {
                "location": "Parte 8, Item 1.a",
                "instructions": "O empregador deve assinar e datar",
            },
            "attorney_signature": {
                "location": "Parte 9 (se aplicável)",
                "instructions": "Somente se representado por advogado",
            },
            "important_notes": [
                "Use tinta azul ou preta",
                "Assinatura deve corresponder ao nome no documento",
                "Data no formato MM/DD/AAAA",
            ],
        },
        "B-1/B-2": {
            "applicant_signature": {
                "location": "DS-160 é assinado digitalmente",
                "instructions": "Confirme todas as informações antes de submeter",
            },
            "important_notes": [
                "Não é necessário assinar documentos físicos",
                "Verifique todas as informações no DS-160",
                "Leve página de confirmação impressa para entrevista",
            ],
        },
        "F-1": {
            "applicant_signature": {
                "location": "DS-160 é assinado digitalmente",
                "instructions": "Confirme todas as informações antes de submeter",
            },
            "i20_signature": {
                "location": "Formulário I-20",
                "instructions": "Estudante deve assinar na página 1",
            },
            "important_notes": [
                "I-20 deve ser assinado antes da entrevista",
                "Use tinta azul ou preta para I-20",
                "DS-160 é totalmente digital",
            ],
        },
    }

    return signature_guides.get(form_code, {})


def get_payment_instructions(form_code: str) -> dict:
    """Get payment instructions based on form type."""
    payment_info = {
        "H-1B": {
            "total_amount": "$555 + taxas adicionais",
            "payment_method": "Cheque ou Money Order",
            "payable_to": "U.S. Department of Homeland Security",
            "additional_fees": [
                "Anti-Fraud Fee: $500",
                "ACWIA Fee: $750 ou $1,500 (dependendo do tamanho da empresa)",
                "Premium Processing (opcional): $2,805",
            ],
            "check_instructions": [
                "Usar cheque bancário ou money order",
                "Não enviar dinheiro em espécie",
                "Escrever o número do case no cheque",
                "Cheque deve ser de banco americano",
            ],
        },
        "B-1/B-2": {
            "total_amount": "$185",
            "payment_method": "Online ou Boleto Bancário",
            "payment_location": "https://ais.usvisa-info.com/",
            "instructions": [
                "Pague online antes de agendar entrevista",
                "Guarde comprovante de pagamento",
                "Taxa não é reembolsável",
                "Válida por 1 ano a partir do pagamento",
            ],
        },
        "F-1": {
            "total_amount": "$185 + $350 (SEVIS)",
            "payment_method": "Online",
            "sevis_payment": "https://www.fmjfee.com/",
            "visa_payment": "https://ais.usvisa-info.com/",
            "instructions": [
                "Pagar SEVIS I-901 primeiro ($350)",
                "Aguardar 3 dias úteis para processamento SEVIS",
                "Depois pagar taxa de visto ($185)",
                "Guardar ambos os comprovantes",
            ],
        },
    }

    return payment_info.get(form_code, {})


def get_step_by_step_guide(form_code: str) -> list:
    """Get step-by-step submission guide."""
    guides = {
        "H-1B": [
            {
                "step": 1,
                "title": "Revisar Documentação",
                "description": "Verifique se todos os documentos estão completos e assinados",
            },
            {
                "step": 2,
                "title": "Preparar Pagamento",
                "description": "Obtenha cheque bancário ou money order no valor total das taxas",
            },
            {
                "step": 3,
                "title": "Organizar Pacote",
                "description": "Coloque documentos na ordem do checklist fornecido",
            },
            {
                "step": 4,
                "title": "Carta de Apresentação",
                "description": "Inclua carta explicando o caso e listando documentos",
            },
            {
                "step": 5,
                "title": "Envio Correio",
                "description": "Envie via correio registrado para o endereço do USCIS",
            },
            {
                "step": 6,
                "title": "Acompanhar Caso",
                "description": "Use o número de recibo para acompanhar no site do USCIS",
            },
            {
                "step": 7,
                "title": "Aguardar Decisão",
                "description": "Prazo normal: 2-4 meses (ou 15 dias se premium processing)",
            },
        ],
        "B-1/B-2": [
            {
                "step": 1,
                "title": "Completar DS-160",
                "description": "Preencha o formulário online completamente",
            },
            {
                "step": 2,
                "title": "Pagar Taxa de Visto",
                "description": "Pague $185 online e guarde o comprovante",
            },
            {
                "step": 3,
                "title": "Agendar Entrevista",
                "description": "Marque entrevista no consulado mais próximo",
            },
            {
                "step": 4,
                "title": "Preparar Documentos",
                "description": "Organize todos os documentos conforme checklist",
            },
            {
                "step": 5,
                "title": "Comparecer à Entrevista",
                "description": "Chegue 15 minutos antes com todos os documentos",
            },
            {
                "step": 6,
                "title": "Aguardar Processamento",
                "description": "3-5 dias úteis após aprovação na entrevista",
            },
            {
                "step": 7,
                "title": "Retirar Passaporte",
                "description": "Retire no local indicado ou receba via correio",
            },
        ],
        "F-1": [
            {
                "step": 1,
                "title": "Pagar Taxa SEVIS",
                "description": "Pague $350 no site https://www.fmjfee.com/",
            },
            {
                "step": 2,
                "title": "Aguardar SEVIS",
                "description": "Aguarde 3 dias úteis para processamento",
            },
            {
                "step": 3,
                "title": "Completar DS-160",
                "description": "Preencha formulário online com I-20 em mãos",
            },
            {
                "step": 4,
                "title": "Pagar Taxa de Visto",
                "description": "Pague $185 e agende entrevista",
            },
            {
                "step": 5,
                "title": "Preparar Documentos",
                "description": "Organize conforme checklist de estudante",
            },
            {
                "step": 6,
                "title": "Entrevista Consular",
                "description": "Compareça com I-20 assinado e documentos",
            },
            {
                "step": 7,
                "title": "Aguardar Aprovação",
                "description": "3-5 dias úteis para processamento",
            },
            {"step": 8, "title": "Receber Visto", "description": "Visto será colado no passaporte"},
        ],
    }

    return guides.get(form_code, [])


def get_important_submission_notes(form_code: str) -> list:
    """Get important notes for submission."""
    notes = {
        "H-1B": [
            "⚠️ PRAZO: Petições H-1B regulares só podem ser submetidas a partir de 1º de abril",
            "⚠️ LIMITE: Há um limite anual de 65.000 vistos H-1B (+ 20.000 para mestrados americanos)",
            "⚠️ LOTERIA: Se houver mais pedidos que o limite, será realizada loteria",
            "📋 PREMIUM: Considere Premium Processing ($2,805) para decisão em 15 dias",
            "📞 SUPORTE: Em caso de RFE (Request for Evidence), responda dentro do prazo",
            "🔄 STATUS: Acompanhe o caso em uscis.gov com o número de recibo",
        ],
        "B-1/B-2": [
            "⚠️ VALIDADE: Visto B-1/B-2 normalmente tem validade de 10 anos para brasileiros",
            "⚠️ ESTADIA: Cada entrada permite até 6 meses de permanência (definido na chegada)",
            "📋 ENTREVISTA: Seja honesto e direto nas respostas durante a entrevista",
            "💰 VÍNCULOS: Demonstre vínculos fortes com o Brasil (emprego, família, propriedades)",
            "🎯 PROPÓSITO: Seja claro sobre o propósito da viagem e data de retorno",
            "📱 AGENDAMENTO: Agende com antecedência - consulados têm alta demanda",
        ],
        "F-1": [
            "⚠️ I-20: Visto só pode ser solicitado com I-20 válido da instituição",
            "⚠️ SEVIS: Taxa SEVIS deve ser paga antes da entrevista (aguarde 3 dias)",
            "📋 FINANCEIRO: Demonstre capacidade financeira para cobrir estudos e vida",
            "🎓 INTENÇÃO: Demonstre intenção de retornar ao Brasil após os estudos",
            "📅 TIMING: Visto F-1 pode ser solicitado até 120 dias antes do início do curso",
            "🇺🇸 ENTRADA: Pode entrar nos EUA até 30 dias antes do início das aulas",
        ],
    }

    return notes.get(form_code, [])
