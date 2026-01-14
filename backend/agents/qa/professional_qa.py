"""
Professional Quality Assurance Agent
Agente de revisão profissional treinado com requisitos USCIS
Garante que nenhum processo incompleto ou com baixa qualidade seja liberado
"""

import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class ProfessionalQAAgent:
    """
    Agente de controle de qualidade profissional
    Treinado com requisitos específicos do USCIS para cada tipo de processo
    """

    def __init__(self):
        """Inicializa o agente de QA com requisitos USCIS"""
        self.knowledge_base = self._load_uscis_requirements()

        # 🧪 MODO DE TESTE: Se SKIP_QA_THRESHOLD=TRUE, usar threshold mais baixo
        test_mode = os.environ.get("SKIP_QA_THRESHOLD", "FALSE").upper() == "TRUE"
        self.test_mode = test_mode  # 🆕 P1-8: Store test mode for use in other methods

        if test_mode:
            self.minimum_approval_score = 0.50  # 50% em modo de teste
            self.critical_threshold = 0.60  # 60% para processos críticos em teste
            logger.warning("⚠️  QA Agent em MODO DE TESTE - thresholds reduzidos")
        else:
            self.minimum_approval_score = 0.85  # 85% mínimo para aprovação
            self.critical_threshold = 0.95  # 95% para processos críticos

        logger.info("✅ Professional QA Agent inicializado com base USCIS")

    def _load_uscis_requirements(self) -> Dict[str, Any]:
        """Carrega requisitos USCIS de cada tipo de processo"""
        requirements = {
            "O-1": {
                "form": "I-129",
                "category_weights": {
                    "personal_data": 0.10,
                    "professional_data": 0.40,  # Muito importante - habilidade extraordinária
                    "documents": 0.35,  # Evidências críticas
                    "critical_criteria": 0.15,
                },
                "required_documents": [
                    "Passport copy (valid for at least 6 months)",
                    "I-94 Arrival/Departure Record",
                    "Consultation letter from peer group",
                    "Written advisory opinion from labor organization",
                    "Evidence of extraordinary ability (minimum 3 types):",
                    "- Receipt of major prizes/awards",
                    "- Membership in associations requiring outstanding achievements",
                    "- Published material about the person in professional publications",
                    "- Original contributions of major significance",
                    "- Authorship of scholarly articles",
                    "- High salary or remuneration",
                    "- Participation as judge of others' work",
                    "- Employment in critical/essential capacity",
                    "Employment contract or written description of proposed work",
                    "Itinerary of events/activities",
                ],
                "critical_checks": [
                    "Consultation letter must be dated within 6 months",
                    "Evidence must show sustained acclaim and recognition",
                    "Must demonstrate extraordinary ability in sciences, arts, education, business, or athletics",
                    "Must show that coming to US to continue work in area of extraordinary ability",
                ],
                "common_mistakes": [
                    "Insufficient evidence of extraordinary ability",
                    "Missing consultation letter",
                    "Evidence not recent enough",
                    "Lack of sustained national or international acclaim",
                ],
                "processing_time": "2-4 months (6-15 days with premium processing)",
                "filing_fee": "$460 + $2,805 (premium processing optional)",
            },
            "F-1": {
                "form": "I-20",
                "category_weights": {
                    "personal_data": 0.15,
                    "professional_data": 0.25,  # Histórico acadêmico
                    "documents": 0.40,  # I-20, SEVIS, financeiro
                    "critical_criteria": 0.20,  # Vínculos, não-imigrante intent
                },
                "required_documents": [
                    "Valid passport (at least 6 months beyond program end)",
                    "Form I-20 from SEVP-certified school",
                    "SEVIS fee payment receipt",
                    "Acceptance letter from US school",
                    "Financial documents proving ability to pay tuition and living expenses",
                    "Academic transcripts and diplomas",
                    "Standardized test scores (TOEFL, IELTS, GRE, GMAT, SAT, etc.)",
                    "Proof of ties to home country",
                ],
                "critical_checks": [
                    "SEVIS fee must be paid at least 3 days before interview",
                    "Financial documents must show sufficient funds for full program",
                    "I-20 must be signed and dated",
                    "Must demonstrate non-immigrant intent",
                ],
                "common_mistakes": [
                    "Insufficient financial documentation",
                    "Weak ties to home country",
                    "Incomplete academic records",
                    "Outdated SEVIS fee receipt",
                ],
                "processing_time": "Varies by consulate (typically 2-8 weeks)",
                "filing_fee": "$160 application fee + $350 SEVIS fee",
            },
            "H-1B": {
                "form": "I-129 (H-1B)",
                "category_weights": {
                    "personal_data": 0.15,
                    "professional_data": 0.35,  # Qualificações profissionais
                    "documents": 0.35,  # LCA, diplomas, CV
                    "critical_criteria": 0.15,  # Specialty occupation
                },
                "required_documents": [
                    "Form I-129 with H Classification Supplement",
                    "Labor Condition Application (LCA) certified by DOL",
                    "Job offer letter",
                    "Evidence of employer's ability to pay",
                    "Evidence of specialty occupation:",
                    "- Bachelor's degree or equivalent required for position",
                    "- Position duties require specialized knowledge",
                    "Educational credentials:",
                    "- Diploma and transcripts",
                    "- Credential evaluation (if foreign degree)",
                    "Resume/CV showing relevant experience",
                    "Support letters from current/previous employers",
                ],
                "critical_checks": [
                    "LCA must be certified and match petition dates",
                    "Degree must be directly related to specialty occupation",
                    "Job duties must require bachelor's degree minimum",
                    "Wage must meet prevailing wage requirement",
                    "Position must be specialty occupation",
                ],
                "common_mistakes": [
                    "LCA wage not matching offered wage",
                    "Insufficient evidence of specialty occupation",
                    "Degree not related to position",
                    "Missing LCA or not properly certified",
                ],
                "processing_time": "3-6 months regular, 15 business days premium",
                "filing_fee": "$460 base + $500 fraud prevention + $750/$1,500 training fee",
            },
            "EB-1A": {
                "form": "I-140",
                "required_documents": [
                    "Form I-140 Immigrant Petition",
                    "Evidence of extraordinary ability (minimum 3 of 10 criteria):",
                    "1. Receipt of major internationally-recognized prizes/awards",
                    "2. Membership in associations requiring outstanding achievements",
                    "3. Published material about person in professional publications",
                    "4. Participation as judge of work of others",
                    "5. Original scientific/scholarly/artistic contributions",
                    "6. Authorship of scholarly articles",
                    "7. Display of work at artistic exhibitions",
                    "8. Leading/critical role in distinguished organizations",
                    "9. High salary relative to others in field",
                    "10. Commercial success in performing arts",
                    "Letters of recommendation from experts",
                    "Publications list with citation counts",
                    "Media coverage about achievements",
                ],
                "critical_checks": [
                    "Must meet at least 3 of 10 criteria",
                    "Evidence must show sustained national or international acclaim",
                    "Must show continued work in area of expertise in US",
                    "Letters must be from independent experts",
                    "Evidence must demonstrate extraordinary ability",
                ],
                "common_mistakes": [
                    "Not meeting minimum 3 criteria threshold",
                    "Evidence not substantial enough",
                    "Letters from non-independent sources",
                    "Insufficient proof of sustained acclaim",
                    "Missing evidence of future work in US",
                ],
                "processing_time": "12-18 months (may vary by service center)",
                "filing_fee": "$700 + $2,805 (premium processing when available)",
            },
            "I-539": {
                "form": "I-539",
                "category_weights": {
                    "personal_data": 0.15,
                    "professional_data": 0.10,  # Menos importante para turismo
                    "documents": 0.50,  # Mais importante - evidência de turismo
                    "critical_criteria": 0.25,  # Timing e elegibilidade
                },
                "required_documents": [
                    "Form I-539 Application to Extend/Change Nonimmigrant Status",
                    "Copy of I-94 Arrival/Departure Record",
                    "Copy of current visa",
                    "Passport biographical page",
                    "Evidence of financial support",
                    "Letter explaining reason for extension",
                    "For B-2 tourist:",
                    "- Proof of ties to home country",
                    "- Travel itinerary",
                    "- Medical records (if medical reason)",
                    "For dependent status:",
                    "- Marriage certificate",
                    "- Birth certificates",
                    "- Principal's status documents",
                ],
                "critical_checks": [
                    "Must file before current status expires",
                    "Must maintain status since entry",
                    "Must show continued nonimmigrant intent",
                    "Financial evidence must be current",
                    "Reason for extension must be legitimate",
                ],
                "common_mistakes": [
                    "Filing after status expires",
                    "Insufficient financial documentation",
                    "Weak explanation for extension",
                    "Missing I-94 or incorrect I-94 number",
                ],
                "processing_time": "6-12 months",
                "filing_fee": "$370",
            },
            "I-130": {
                "form": "I-130",
                "required_documents": [
                    "Form I-130 Petition for Alien Relative",
                    "Proof of US citizenship/LPR status of petitioner:",
                    "- Birth certificate",
                    "- Passport",
                    "- Naturalization certificate",
                    "- Green card (if LPR)",
                    "Proof of relationship:",
                    "- Marriage certificate (for spouse)",
                    "- Birth certificate (for parent/child)",
                    "- Adoption papers (if applicable)",
                    "Two passport-style photos of beneficiary",
                    "Copy of beneficiary's passport",
                    "Form I-864 Affidavit of Support (if applicable)",
                    "Evidence of bona fide marriage (for spouses):",
                    "- Joint bank accounts",
                    "- Joint lease/mortgage",
                    "- Photos together",
                    "- Correspondence",
                    "- Bills in both names",
                ],
                "critical_checks": [
                    "Relationship must be qualifying (spouse, parent, child, sibling)",
                    "Marriage must be legally valid",
                    "Marriage certificate must be official/certified",
                    "Must prove bona fide marriage (not for immigration)",
                    "Photos must meet specifications",
                ],
                "common_mistakes": [
                    "Insufficient evidence of bona fide marriage",
                    "Missing required relationship proof",
                    "Photos not meeting specifications",
                    "Translation not certified",
                    "Missing affidavit of support",
                ],
                "processing_time": "12-24 months depending on relationship",
                "filing_fee": "$535",
            },
            "I-765": {
                "form": "I-765",
                "required_documents": [
                    "Form I-765 Application for Employment Authorization",
                    "Copy of passport biographical page",
                    "Two passport-style photos",
                    "Copy of I-94 Arrival/Departure Record",
                    "Evidence of eligibility category:",
                    "- F-1 OPT: I-20 with OPT recommendation",
                    "- Pending I-485: Receipt notice",
                    "- Asylum pending: Asylum receipt",
                    "Previous EAD card (if renewal)",
                    "Fee or fee waiver documentation",
                ],
                "critical_checks": [
                    "Must have qualifying immigration status",
                    "Must file within eligibility window",
                    "Photos must meet specifications",
                    "I-20 must show OPT recommendation (for F-1 OPT)",
                    "Must file before current EAD expires (if renewal)",
                ],
                "common_mistakes": [
                    "Filing too early or too late",
                    "Missing qualifying documents",
                    "Photos not meeting requirements",
                    "Incorrect fee",
                    "Missing previous EAD info",
                ],
                "processing_time": "3-6 months",
                "filing_fee": "$410 + $85 biometrics (fee waiver available)",
            },
        }

        return requirements

    def comprehensive_review(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Revisão profissional completa de um caso

        Args:
            case_data: Dados completos do caso incluindo:
                - form_code: Tipo de visto (O-1, F-1, H-1B, etc.)
                - basic_data: Dados pessoais do aplicante
                - simplified_form_responses: Dados profissionais
                - documents: Lista de documentos enviados
                - ai_processing_status: Status do processamento

        Returns:
            Relatório detalhado de QA com aprovação/rejeição
        """
        form_code = case_data.get("form_code", "").upper()

        logger.info(f"🔍 Iniciando revisão profissional para {form_code}")

        # Verificar se temos requisitos para este tipo
        if form_code not in self.knowledge_base:
            logger.warning(
                f"⚠️  Tipo de visto {form_code} não tem requisitos específicos cadastrados"
            )
            return self._generic_review(case_data)

        requirements = self.knowledge_base[form_code]

        # Estrutura do relatório
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "case_id": case_data.get("case_id"),
            "form_code": form_code,
            "form_name": requirements["form"],
            "status": "pending",
            "overall_score": 0.0,
            "categories": {},
            "critical_issues": [],
            "missing_items": [],
            "warnings": [],
            "recommendations": [],
            "approval": {"approved": False, "reason": "", "required_actions": []},
        }

        # Obter pesos dinâmicos por tipo de visto (ou usar defaults)
        default_weights = {
            "personal_data": 0.15,
            "professional_data": 0.25,
            "documents": 0.40,
            "critical_criteria": 0.20,
        }
        weights = requirements.get("category_weights", default_weights)

        # 1. Verificar completude de dados pessoais
        personal_score, personal_issues = self._check_personal_data(case_data)
        report["categories"]["personal_data"] = {
            "score": personal_score,
            "weight": weights["personal_data"],
            "issues": personal_issues,
        }

        # 2. Verificar dados profissionais/específicos do visto
        professional_score, professional_issues = self._check_professional_data(
            case_data, requirements
        )
        report["categories"]["professional_data"] = {
            "score": professional_score,
            "weight": weights["professional_data"],
            "issues": professional_issues,
        }

        # 3. Verificar documentos obrigatórios
        documents_score, documents_issues, missing = self._check_required_documents(
            case_data, requirements
        )
        report["categories"]["documents"] = {
            "score": documents_score,
            "weight": weights["documents"],
            "issues": documents_issues,
        }
        report["missing_items"] = missing

        # 4. Verificar critérios críticos do USCIS
        critical_score, critical_issues = self._check_critical_criteria(case_data, requirements)
        report["categories"]["critical_criteria"] = {
            "score": critical_score,
            "weight": weights["critical_criteria"],
            "issues": critical_issues,
        }

        # Calcular score geral
        overall_score = sum(cat["score"] * cat["weight"] for cat in report["categories"].values())
        report["overall_score"] = overall_score

        # Determinar aprovação
        approval_decision = self._make_approval_decision(report, requirements, form_code)
        report["approval"] = approval_decision
        report["status"] = "approved" if approval_decision["approved"] else "rejected"

        # Gerar recomendações
        report["recommendations"] = self._generate_recommendations(report, requirements)

        # Log resultado
        self._log_review_result(report)

        return report

    def _check_personal_data(self, case_data: Dict[str, Any]) -> tuple[float, List[str]]:
        """Verifica dados pessoais básicos"""
        issues = []
        score = 1.0

        basic_data = case_data.get("basic_data", {})

        required_fields = [
            "full_name",
            "date_of_birth",
            "country_of_birth",
            "passport_number",
            "email",
            "phone",
        ]

        for field in required_fields:
            if not basic_data.get(field):
                issues.append(f"Missing required field: {field}")
                score -= 0.15

        # Validar formato de dados
        if basic_data.get("email") and "@" not in basic_data["email"]:
            issues.append("Invalid email format")
            score -= 0.10

        if basic_data.get("passport_number"):
            if len(basic_data["passport_number"]) < 6:
                issues.append("Passport number appears invalid (too short)")
                score -= 0.10

        return max(0.0, score), issues

    def _check_professional_data(
        self, case_data: Dict[str, Any], requirements: Dict[str, Any]
    ) -> tuple[float, List[str]]:
        """Verifica dados profissionais específicos do tipo de visto"""
        issues = []
        score = 1.0

        form_responses = case_data.get("simplified_form_responses", {})

        if not form_responses:
            issues.append("No professional data provided")
            return 0.0, issues

        # Verificações específicas por tipo
        form_code = case_data.get("form_code", "").upper()

        if form_code in ["O-1", "EB-1A"]:
            # Verificar evidências de habilidade extraordinária
            achievements = form_responses.get("achievements", [])
            if len(achievements) < 3:
                issues.append("Insufficient evidence of extraordinary ability (minimum 3 required)")
                score -= 0.30

            publications = form_responses.get("publications", {})
            if not publications or publications.get("total", 0) < 10:
                issues.append("Limited publications for extraordinary ability claim")
                score -= 0.15

        elif form_code == "H-1B":
            # Verificar specialty occupation
            education = form_responses.get("education", [])
            if not education or not any(
                "Bachelor" in str(e) or "Master" in str(e) or "PhD" in str(e) for e in education
            ):
                issues.append("Missing bachelor's degree or higher for H-1B specialty occupation")
                score -= 0.40

            professional_bg = form_responses.get("professional_background", {})
            if not professional_bg.get("current_employer"):
                issues.append("Missing current employer information")
                score -= 0.20

        elif form_code == "F-1":
            # Verificar documentos acadêmicos
            education = form_responses.get("education", [])
            if not education:
                issues.append("Missing educational background for F-1 student visa")
                score -= 0.30

        return max(0.0, score), issues

    def _check_required_documents(
        self, case_data: Dict[str, Any], requirements: Dict[str, Any]
    ) -> tuple[float, List[str], List[str]]:
        """Verifica presença e qualidade de documentos obrigatórios"""
        issues = []
        missing = []
        score = 1.0

        # Verificar ambos os campos (uploaded_documents tem prioridade)
        documents = case_data.get("uploaded_documents", case_data.get("documents", []))
        document_types = [doc.get("document_type", "") for doc in documents]

        # Documentos essenciais que TODO processo precisa
        essential_docs = ["passport", "photo"]

        for essential in essential_docs:
            if not any(essential in dtype.lower() for dtype in document_types):
                missing.append(f"Essential document: {essential}")
                issues.append(f"❌ Critical: Missing {essential}")
                score -= 0.25

        # 🆕 Verificar documentos específicos por tipo de visto
        form_code = case_data.get("form_code", "").upper()

        if form_code == "I-539":  # Extension/Change of Status
            # Documentos específicos para extensão
            i539_docs = {
                "i94": "I-94 Arrival/Departure Record",
                "financial_support": "Financial support documents (bank statements)",
                "supporting_letter": "Letter explaining reason for extension",
            }

            for doc_type, doc_name in i539_docs.items():
                if not any(doc_type in dtype.lower() for dtype in document_types):
                    missing.append(doc_name)
                    issues.append(f"⚠️ Missing: {doc_name}")
                    score -= 0.15

            # 🆕 Verificar evidência de turismo (se B-2)
            status = case_data.get("simplified_form_responses", {}).get("status_atual", "")
            if "B-2" in status or "B2" in status:
                has_tourism_evidence = any(
                    "tourism" in dtype.lower() or "itinerary" in dtype.lower()
                    for dtype in document_types
                )
                if not has_tourism_evidence:
                    issues.append(
                        "⚠️ Recommended: Tourism evidence (photos, itinerary) strengthens B-2 extension"
                    )
                    score -= 0.10

        elif form_code == "F-1":  # Student
            f1_docs = {
                "i20": "Form I-20",
                "sevis": "SEVIS fee receipt",
                "financial": "Financial documents",
                "academic": "Academic transcripts",
            }

            for doc_type, doc_name in f1_docs.items():
                if not any(doc_type in dtype.lower() for dtype in document_types):
                    missing.append(doc_name)
                    issues.append(f"❌ Missing: {doc_name}")
                    score -= 0.20

        elif form_code == "H-1B":  # Work
            h1b_docs = {
                "lca": "Labor Condition Application (LCA)",
                "diploma": "Diploma/Degree certificate",
                "employment": "Employment offer letter",
                "resume": "Resume/CV",
            }

            for doc_type, doc_name in h1b_docs.items():
                if not any(doc_type in dtype.lower() for dtype in document_types):
                    missing.append(doc_name)
                    issues.append(f"❌ Missing: {doc_name}")
                    score -= 0.20

        # 🆕 Verificar qualidade dos documentos
        for doc in documents:
            file_size = doc.get("file_size", 0)
            filename = doc.get("filename", "")

            # Arquivo muito pequeno pode ser corrupto
            if file_size < 100:  # Menos de 100 bytes
                issues.append(
                    f"⚠️ Suspicious file size: {filename} ({file_size} bytes) - may be corrupted"
                )
                score -= 0.05

            # Verificar se tem descrição
            if not doc.get("description"):
                issues.append(f"ℹ️ Missing description for: {filename}")
                score -= 0.02

        # Verificar quantidade mínima de documentos (ajustado por tipo)
        min_docs = 5 if form_code in ["O-1", "EB-1A"] else 3
        if len(documents) < min_docs:
            issues.append(
                f"⚠️ Only {len(documents)} documents uploaded (minimum {min_docs} expected for {form_code})"
            )
            score -= 0.20

        # 🆕 Bônus por documentação completa
        if len(documents) >= min_docs + 3:
            issues.append(f"✅ Good: {len(documents)} documents provided (above minimum)")
            score += 0.10

        # Verificar se documentos estão validados
        unvalidated = [doc["filename"] for doc in documents if not doc.get("validated", False)]

        if unvalidated:
            issues.append(
                f"ℹ️ {len(unvalidated)} documents not yet validated: {', '.join(unvalidated[:3])}"
            )
            # Não penalizar tanto se documentos existem mas não foram validados
            score -= 0.05 * min(len(unvalidated), 3)

        return max(0.0, min(1.0, score)), issues, missing

    def _check_critical_criteria(
        self, case_data: Dict[str, Any], requirements: Dict[str, Any]
    ) -> tuple[float, List[str]]:
        """Verifica critérios críticos do USCIS"""
        issues = []
        score = 1.0

        requirements.get("critical_checks", [])

        # 🆕 P1-8: Bypass payment/AI checks in test mode
        if self.test_mode:
            logger.info("🧪 Test mode: Skipping payment and AI processing checks")
        else:
            # Verificar pagamento
            payment_status = case_data.get("payment_status")
            if payment_status != "completed":
                issues.append("CRITICAL: Payment not completed")
                score -= 0.40

            # Verificar processamento AI
            ai_status = case_data.get("ai_processing_status")
            if ai_status != "approved":
                issues.append(f"AI processing not approved (status: {ai_status})")
                score -= 0.30

        # Verificar progresso
        progress = case_data.get("progress_percentage", 0)
        if progress < 80:
            issues.append(f"Application only {progress}% complete (minimum 80% required)")
            score -= 0.30

        return max(0.0, score), issues

    def _make_approval_decision(
        self, report: Dict[str, Any], requirements: Dict[str, Any], form_code: str
    ) -> Dict[str, Any]:
        """Toma decisão final de aprovação baseada em todos os critérios"""
        overall_score = report["overall_score"]
        missing_items = report["missing_items"]

        # Critérios de aprovação
        approval = {
            "approved": False,
            "confidence": overall_score,
            "reason": "",
            "required_actions": [],
            "category_breakdown": {},  # 🆕 Breakdown detalhado por categoria
        }

        # Processos críticos (O-1, EB-1A) exigem score mais alto
        threshold = (
            self.critical_threshold
            if form_code in ["O-1", "EB-1A"]
            else self.minimum_approval_score
        )

        # 🆕 Adicionar breakdown detalhado de cada categoria
        for category_name, category_data in report["categories"].items():
            cat_score = category_data["score"]
            cat_weight = category_data["weight"]
            contribution = cat_score * cat_weight

            # Nome amigável da categoria
            friendly_names = {
                "personal_data": "Dados Pessoais",
                "professional_data": "Dados Profissionais",
                "documents": "Documentos",
                "critical_criteria": "Critérios Críticos USCIS",
            }

            approval["category_breakdown"][category_name] = {
                "name": friendly_names.get(category_name, category_name),
                "score": f"{cat_score:.1%}",
                "weight": f"{cat_weight:.0%}",
                "contribution": f"{contribution:.1%}",
                "status": (
                    "✅ OK"
                    if cat_score >= 0.80
                    else ("⚠️ Atenção" if cat_score >= 0.60 else "❌ Crítico")
                ),
                "issues_count": len(category_data.get("issues", [])),
            }

        # Decisão com feedback específico
        if overall_score < threshold:
            approval["approved"] = False
            approval["reason"] = (
                f"Overall quality score ({overall_score:.1%}) below required threshold ({threshold:.1%})"
            )

            # 🆕 Adicionar ações específicas por categoria com score baixo
            for cat_name, cat_data in report["categories"].items():
                if cat_data["score"] < 0.70:
                    friendly_name = approval["category_breakdown"][cat_name]["name"]
                    approval["required_actions"].append(
                        f"🔴 {friendly_name}: Score {cat_data['score']:.1%} - {len(cat_data['issues'])} issues found"
                    )
                    # Adicionar até 3 issues específicos
                    for issue in cat_data["issues"][:3]:
                        approval["required_actions"].append(f"  • {issue}")

        elif missing_items:
            approval["approved"] = False
            approval["reason"] = f"Missing {len(missing_items)} critical items"
            approval["required_actions"] = [f"📄 Add: {item}" for item in missing_items]

        elif report["categories"]["critical_criteria"]["score"] < 0.70:
            approval["approved"] = False
            approval["reason"] = "Critical USCIS criteria not met"
            approval["required_actions"].append("⚠️ Address all critical criteria issues")
            # Adicionar issues específicos
            for issue in report["categories"]["critical_criteria"]["issues"]:
                approval["required_actions"].append(f"  • {issue}")

        else:
            approval["approved"] = True
            approval["reason"] = f"Application meets professional standards ({overall_score:.1%})"
            approval["required_actions"] = []

        return approval

    def _generate_recommendations(
        self, report: Dict[str, Any], requirements: Dict[str, Any]
    ) -> List[str]:
        """Gera recomendações profissionais para melhorar o caso"""
        recommendations = []

        # Baseado em scores de categorias
        for category, data in report["categories"].items():
            if data["score"] < 0.90:
                if category == "personal_data":
                    recommendations.append(
                        "✅ Complete all personal information fields with accurate data"
                    )
                elif category == "professional_data":
                    recommendations.append(
                        "✅ Enhance professional background with detailed achievements and qualifications"
                    )
                elif category == "documents":
                    recommendations.append(
                        "✅ Upload all required supporting documents with proper validation"
                    )
                elif category == "critical_criteria":
                    recommendations.append("✅ Ensure all USCIS critical criteria are fully met")

        # Adicionar avisos sobre erros comuns
        common_mistakes = requirements.get("common_mistakes", [])
        if common_mistakes:
            recommendations.append("⚠️  Common mistakes to avoid:")
            for mistake in common_mistakes[:3]:
                recommendations.append(f"   • {mistake}")

        # Status geral
        if report["approval"]["approved"]:
            recommendations.append("🎉 Application approved! Ready for submission to USCIS")
            recommendations.append(f"📋 Form to file: {requirements['form']}")
            recommendations.append(f"💰 Filing fee: {requirements['filing_fee']}")
            recommendations.append(
                f"⏱️  Expected processing time: {requirements['processing_time']}"
            )
        else:
            recommendations.append(
                "❌ Application NOT approved - address all issues before submission"
            )
            recommendations.append(
                "⚠️  Submitting incomplete applications may result in rejection and loss of fees"
            )

        return recommendations

    def _generic_review(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Revisão genérica para tipos de visto sem requisitos específicos"""
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "case_id": case_data.get("case_id"),
            "form_code": case_data.get("form_code"),
            "status": "pending_manual_review",
            "overall_score": 0.70,
            "approval": {
                "approved": False,
                "reason": "Manual review required for this visa type",
                "required_actions": ["Contact support for manual quality review"],
            },
            "recommendations": [
                "This visa type requires manual review by immigration specialist",
                "Please contact our support team for assistance",
            ],
        }

    def _log_review_result(self, report: Dict[str, Any]):
        """Registra resultado da revisão em log"""
        case_id = report["case_id"]
        form_code = report["form_code"]
        approved = report["approval"]["approved"]
        score = report["overall_score"]

        status_icon = "✅" if approved else "❌"

        logger.info(
            f"{status_icon} QA Review: {case_id} ({form_code}) - Score: {score:.1%} - {'APPROVED' if approved else 'REJECTED'}"
        )

        if not approved:
            logger.warning(f"❌ Rejection reason: {report['approval']['reason']}")
            logger.warning(f"📋 Required actions: {len(report['approval']['required_actions'])}")


# Singleton instance
_qa_agent = None


def get_qa_agent() -> ProfessionalQAAgent:
    """Retorna instância singleton do QA Agent"""
    global _qa_agent
    if _qa_agent is None:
        _qa_agent = ProfessionalQAAgent()
    return _qa_agent
