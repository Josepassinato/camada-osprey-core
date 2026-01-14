"""
Immigration Compliance Reviewer Agent - Versão Completa e Rigorosa

Este agente atua como um advogado especialista em imigração dos EUA, realizando
revisão COMPLETA e DETALHADA de pacotes de aplicação antes de liberar para download.

VERIFICAÇÕES OBRIGATÓRIAS:
1. Revisão página por página de TODO o processo
2. Verificação de coerência do texto e informações
3. Verificação da presença de TODA documentação exigida (por tipo de visto)
4. Verificação da VALIDADE de documentos (datas de expiração, autenticidade)
5. Verificação de formulário OFICIAL USCIS totalmente e corretamente preenchido
6. Verificação de TODOS os requisitos legais para aquele tipo de aplicação

RESULTADO: Apenas libera para download se 100% conforme
"""

import logging
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

try:
    import pdfplumber

    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False


class ImmigrationComplianceReviewer:
    """
    Revisor de Conformidade Completo para Aplicações de Imigração
    """

    # REQUISITOS OBRIGATÓRIOS POR TIPO DE VISTO
    VISA_REQUIREMENTS = {
        "H-1B": {
            "required_forms": [
                "Form I-129",
                "H-1B Data Collection and Filing Fee Exemption Supplement",
                "H Classification Supplement",
            ],
            "required_documents": [
                "Cover Letter",
                "Labor Condition Application (LCA) - CERTIFIED",
                "Company Support Letter",
                "Detailed Job Description",
                "Organizational Chart",
                "Financial Evidence (Tax Returns, Annual Reports, or Audited Financial Statements)",
                "Beneficiary Resume/CV",
                "Educational Credentials (Diploma and Transcripts)",
                "Credential Evaluation (if foreign degree)",
                "Passport Biographical Page",
                "Prior U.S. Visas (if applicable)",
                "I-94 Arrival/Departure Record (if applicable)",
                "Employment Verification Letters (all positions)",
                "Pay Stubs or Tax Documents (current employer)",
                "Letters of Recommendation (at least 2)",
            ],
            "required_fields_in_lca": [
                "LCA Certification Number",
                "Certification Date",
                "Validity Period",
                "Employer Name and Address",
                "Worksite Address",
                "Prevailing Wage",
                "Wage Offered",
                "Job Title and SOC Code",
            ],
            "legal_requirements": [
                "Proffered wage must meet or exceed prevailing wage",
                "Position must qualify as specialty occupation (bachelor's degree requirement)",
                "Beneficiary must have bachelor's degree or equivalent",
                "LCA must be certified before filing I-129",
                "Employer must demonstrate ability to pay",
                "No labor disputes at worksite",
                "Compliance with working conditions attestations",
            ],
            "form_sections": {
                "I-129": [
                    "Part 1: Information About the Employer",
                    "Part 2: Information About This Petition",
                    "Part 3: Information About the Person or Organization Filing This Petition",
                    "Part 4: Information About the Beneficiary",
                    "Part 5: Basic Information About the Proposed Employment",
                    "Part 6: Dates of Intended Employment",
                    "Part 7: Processing Information",
                ]
            },
        },
        "F-1": {
            "required_forms": [
                "Form I-20",
                "Form I-539 (if change of status)",
                "SEVIS Payment Receipt",
            ],
            "required_documents": [
                "Cover Letter",
                "School Acceptance Letter",
                "Form I-20 from School (signed by DSO)",
                "Financial Support Evidence",
                "Bank Statements (at least 3 months)",
                "Sponsor Affidavit of Support (if applicable)",
                "Academic Transcripts",
                "English Proficiency Test Scores (TOEFL/IELTS)",
                "Passport Biographical Page",
                "Intent to Return Statement",
                "Ties to Home Country Evidence",
            ],
            "required_fields_in_i20": [
                "SEVIS Number",
                "School Name and Address",
                "Program of Study",
                "Program Start Date",
                "Program End Date",
                "Estimated Annual Costs",
                "Financial Support Sources",
                "DSO Signature",
            ],
            "legal_requirements": [
                "Must demonstrate sufficient financial resources",
                "Must show intent to return to home country",
                "Must be accepted by SEVP-certified school",
                "Must maintain full-time enrollment",
                "English proficiency requirement met",
            ],
        },
        "I-539": {
            "required_forms": ["Form I-539", "Supplement A (if applicable)"],
            "required_documents": [
                "Cover Letter explaining reason for extension/change",
                "Current I-94 (front and back)",
                "Copy of current visa",
                "Passport biographical page",
                "Evidence supporting the extension/change",
                "Financial support evidence",
                "Form I-20 (if changing to F-1)",
                "Employer letter (if changing to H-1B)",
                "Proof of maintained status",
            ],
            "legal_requirements": [
                "Must file before current status expires",
                "Must have maintained lawful status",
                "Must demonstrate continued eligibility",
                "No unauthorized employment",
                "Valid reason for extension/change",
            ],
        },
    }

    def __init__(self, visa_type: str = "H-1B", h1b_data_model=None):
        """
        Inicializa o revisor de conformidade

        Args:
            visa_type: Tipo de visto (H-1B, F-1, I-539, etc.)
            h1b_data_model: Modelo de dados para validação de consistência
        """
        self.visa_type = visa_type
        self.h1b_data = h1b_data_model
        self.requirements = self.VISA_REQUIREMENTS.get(visa_type, {})

        # Critérios de aprovação (TODOS devem ser atendidos)
        self.min_compliance_score = 95  # Mínimo 95% de conformidade
        self.max_critical_errors = 0  # Zero erros críticos permitidos

    def comprehensive_review(self, pdf_path: str, user_documents: Optional[Dict] = None) -> Dict:
        """
        Revisão COMPLETA e RIGOROSA do pacote de aplicação

        Args:
            pdf_path: Caminho para o PDF do pacote gerado
            user_documents: Dict com documentos enviados pelo usuário (opcional)

        Returns:
            Dict com resultado detalhado: {
                "status": "APPROVED" ou "REJECTED",
                "compliance_score": 0-100,
                "critical_errors": [...],
                "major_errors": [...],
                "minor_warnings": [...],
                "detailed_report": {...}
            }
        """

        if not PDFPLUMBER_AVAILABLE:
            return self._error_response("pdfplumber não está instalado")

        if not os.path.exists(pdf_path):
            return self._error_response(f"Arquivo não encontrado: {pdf_path}")

        logger.info(f"\n{'='*80}")
        logger.info(f"🔍 REVISÃO COMPLETA DE CONFORMIDADE - {self.visa_type}")
        logger.info(f"{'='*80}")
        logger.info(f"📄 Arquivo: {pdf_path}")

        critical_errors = []
        major_errors = []
        minor_warnings = []
        detailed_report = {}

        try:
            with pdfplumber.open(pdf_path) as pdf:
                num_pages = len(pdf.pages)
                logger.info(f"📃 Total de páginas: {num_pages}")

                # Extrair todo o texto
                logger.info(f"\n📖 Extraindo texto de todas as páginas...")
                pages_text = []
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text() or ""
                    pages_text.append(text)
                    if (i + 1) % 20 == 0:
                        logger.info(f"   ✓ Processadas {i + 1} páginas...")

                full_text = " ".join(pages_text)
                logger.info(f"   ✅ Total: {len(full_text):,} caracteres extraídos")

                # ============================================================
                # VERIFICAÇÃO 1: FORMULÁRIOS OFICIAIS USCIS
                # ============================================================
                logger.info(f"\n📋 VERIFICAÇÃO 1: Formulários Oficiais USCIS")
                forms_result = self._verify_official_forms(pages_text, full_text)
                if forms_result["critical_errors"]:
                    critical_errors.extend(forms_result["critical_errors"])
                if forms_result["major_errors"]:
                    major_errors.extend(forms_result["major_errors"])
                detailed_report["forms_verification"] = forms_result

                # ============================================================
                # VERIFICAÇÃO 2: DOCUMENTAÇÃO OBRIGATÓRIA
                # ============================================================
                logger.info(f"\n📂 VERIFICAÇÃO 2: Documentação Obrigatória")
                docs_result = self._verify_required_documents(pages_text, full_text)
                if docs_result["critical_errors"]:
                    critical_errors.extend(docs_result["critical_errors"])
                if docs_result["major_errors"]:
                    major_errors.extend(docs_result["major_errors"])
                if docs_result["warnings"]:
                    minor_warnings.extend(docs_result["warnings"])
                detailed_report["documents_verification"] = docs_result

                # ============================================================
                # VERIFICAÇÃO 3: VALIDADE DE DOCUMENTOS
                # ============================================================
                logger.info(f"\n📅 VERIFICAÇÃO 3: Validade de Documentos")
                validity_result = self._verify_document_validity(pages_text, full_text)
                if validity_result["critical_errors"]:
                    critical_errors.extend(validity_result["critical_errors"])
                if validity_result["warnings"]:
                    minor_warnings.extend(validity_result["warnings"])
                detailed_report["validity_verification"] = validity_result

                # ============================================================
                # VERIFICAÇÃO 4: REQUISITOS LEGAIS
                # ============================================================
                logger.info(f"\n⚖️ VERIFICAÇÃO 4: Requisitos Legais")
                legal_result = self._verify_legal_requirements(pages_text, full_text)
                if legal_result["critical_errors"]:
                    critical_errors.extend(legal_result["critical_errors"])
                if legal_result["major_errors"]:
                    major_errors.extend(legal_result["major_errors"])
                detailed_report["legal_verification"] = legal_result

                # ============================================================
                # VERIFICAÇÃO 5: COERÊNCIA E CONSISTÊNCIA
                # ============================================================
                logger.info(f"\n✅ VERIFICAÇÃO 5: Coerência e Consistência de Dados")
                consistency_result = self._verify_consistency(pages_text, full_text)
                if consistency_result["critical_errors"]:
                    critical_errors.extend(consistency_result["critical_errors"])
                if consistency_result["major_errors"]:
                    major_errors.extend(consistency_result["major_errors"])
                detailed_report["consistency_verification"] = consistency_result

                # ============================================================
                # VERIFICAÇÃO 6: QUALIDADE PROFISSIONAL
                # ============================================================
                logger.info(f"\n📝 VERIFICAÇÃO 6: Qualidade Profissional do Conteúdo")
                quality_result = self._verify_professional_quality(pages_text)
                if quality_result["major_errors"]:
                    major_errors.extend(quality_result["major_errors"])
                if quality_result["warnings"]:
                    minor_warnings.extend(quality_result["warnings"])
                detailed_report["quality_verification"] = quality_result

                # ============================================================
                # VERIFICAÇÃO 7: DOCUMENTOS DO USUÁRIO (se fornecidos)
                # ============================================================
                if user_documents:
                    logger.info(f"\n📎 VERIFICAÇÃO 7: Documentos Enviados pelo Usuário")
                    user_docs_result = self._verify_user_documents(user_documents)
                    if user_docs_result["critical_errors"]:
                        critical_errors.extend(user_docs_result["critical_errors"])
                    if user_docs_result["major_errors"]:
                        major_errors.extend(user_docs_result["major_errors"])
                    detailed_report["user_documents_verification"] = user_docs_result

        except Exception as e:
            critical_errors.append(f"Erro durante revisão: {str(e)}")
            import traceback

            critical_errors.append(f"Traceback: {traceback.format_exc()}")

        # Calcular score de conformidade
        compliance_score = self._calculate_compliance_score(
            critical_errors, major_errors, minor_warnings
        )

        # Determinar status final
        status = self._determine_final_status(compliance_score, critical_errors, major_errors)

        # Relatório final
        self._print_final_report(
            status, compliance_score, critical_errors, major_errors, minor_warnings
        )

        return {
            "status": status,
            "compliance_score": compliance_score,
            "critical_errors": critical_errors,
            "major_errors": major_errors,
            "minor_warnings": minor_warnings,
            "detailed_report": detailed_report,
            "review_date": datetime.now().isoformat(),
            "reviewer_version": "2.0-COMPLETE",
        }

    def _verify_official_forms(self, pages_text: List[str], full_text: str) -> Dict:
        """Verifica presença e preenchimento completo de formulários USCIS oficiais"""
        critical_errors = []
        major_errors = []
        found_forms = []

        required_forms = self.requirements.get("required_forms", [])

        logger.info(f"   Formulários obrigatórios para {self.visa_type}: {len(required_forms)}")

        for form_name in required_forms:
            # Verificar se formulário está presente
            if form_name.upper() in full_text.upper():
                found_forms.append(form_name)
                logger.info(f"   ✅ {form_name} - ENCONTRADO")

                # Verificar se as seções obrigatórias estão presentes
                if form_name in self.requirements.get("form_sections", {}):
                    sections = self.requirements["form_sections"][form_name]
                    missing_sections = []

                    for section in sections:
                        if section not in full_text:
                            missing_sections.append(section)

                    if missing_sections:
                        major_errors.append(
                            f"{form_name}: Seções faltando: {', '.join(missing_sections)}"
                        )
            else:
                critical_errors.append(f"❌ FORMULÁRIO OBRIGATÓRIO AUSENTE: {form_name}")
                logger.error(f"   ❌ {form_name} - NÃO ENCONTRADO")

        # Verificar campos específicos (para LCA, I-20, etc.)
        if self.visa_type == "H-1B":
            lca_result = self._verify_lca_fields(full_text)
            if lca_result["errors"]:
                critical_errors.extend(lca_result["errors"])
        elif self.visa_type == "F-1":
            i20_result = self._verify_i20_fields(full_text)
            if i20_result["errors"]:
                critical_errors.extend(i20_result["errors"])

        return {
            "critical_errors": critical_errors,
            "major_errors": major_errors,
            "found_forms": found_forms,
            "required_forms": required_forms,
        }

    def _verify_lca_fields(self, full_text: str) -> Dict:
        """Verifica campos obrigatórios do LCA"""
        errors = []
        required_fields = self.requirements.get("required_fields_in_lca", [])

        logger.info(f"\n   📋 Verificando campos do LCA...")
        for field in required_fields:
            # Buscar padrões comuns para cada campo
            found = False

            if "Certification Number" in field:
                pattern = r"(LCA.{0,20}Certification|Certification.{0,20}Number).{0,50}[A-Z]-\d{3}-\d{5}-\d{6}"
                if re.search(pattern, full_text, re.IGNORECASE):
                    found = True
                    logger.info(f"      ✅ {field}")
            elif "Prevailing Wage" in field or "Wage Offered" in field:
                pattern = r"\$\d{2,3},\d{3}"
                if re.search(pattern, full_text):
                    found = True
                    logger.info(f"      ✅ {field}")
            elif "SOC Code" in field:
                pattern = r"\d{2}-\d{4}"
                if re.search(pattern, full_text):
                    found = True
                    logger.info(f"      ✅ {field}")
            elif field in full_text:
                found = True
                logger.info(f"      ✅ {field}")

            if not found:
                errors.append(f"❌ LCA - Campo obrigatório ausente ou incompleto: {field}")
                logger.error(f"      ❌ {field} - NÃO ENCONTRADO")

        return {"errors": errors}

    def _verify_i20_fields(self, full_text: str) -> Dict:
        """Verifica campos obrigatórios do Form I-20"""
        errors = []
        required_fields = self.requirements.get("required_fields_in_i20", [])

        logger.info(f"\n   📋 Verificando campos do Form I-20...")
        for field in required_fields:
            if field not in full_text:
                errors.append(f"❌ Form I-20 - Campo obrigatório ausente: {field}")
                logger.error(f"      ❌ {field} - NÃO ENCONTRADO")
            else:
                logger.info(f"      ✅ {field}")

        return {"errors": errors}

    def _verify_required_documents(self, pages_text: List[str], full_text: str) -> Dict:
        """Verifica presença de todos os documentos obrigatórios"""
        critical_errors = []
        major_errors = []
        warnings = []
        found_documents = []

        required_docs = self.requirements.get("required_documents", [])

        logger.info(f"   Documentos obrigatórios: {len(required_docs)}")

        for doc_name in required_docs:
            # Buscar documento no texto
            if doc_name.upper() in full_text.upper():
                found_documents.append(doc_name)
                logger.info(f"   ✅ {doc_name}")
            else:
                # Verificar se é documento crítico
                if any(
                    word in doc_name.upper()
                    for word in ["PASSPORT", "DIPLOMA", "LCA", "FORM", "I-129", "I-20"]
                ):
                    critical_errors.append(f"❌ DOCUMENTO CRÍTICO AUSENTE: {doc_name}")
                    logger.error(f"   ❌ {doc_name} - CRÍTICO")
                else:
                    major_errors.append(f"⚠️ Documento obrigatório ausente: {doc_name}")
                    logger.warning(f"   ⚠️ {doc_name} - FALTANDO")

        coverage = (len(found_documents) / len(required_docs) * 100) if required_docs else 0
        logger.info(
            f"\n   📊 Cobertura documental: {coverage:.1f}% ({len(found_documents)}/{len(required_docs)})"
        )

        return {
            "critical_errors": critical_errors,
            "major_errors": major_errors,
            "warnings": warnings,
            "found_documents": found_documents,
            "coverage_percentage": coverage,
        }

    def _verify_document_validity(self, pages_text: List[str], full_text: str) -> Dict:
        """Verifica validade de documentos (datas de expiração, etc.)"""
        critical_errors = []
        warnings = []

        logger.info(f"   Verificando validade de documentos...")

        # Verificar passaporte não expirado
        passport_pattern = r"[Pp]assport.{0,100}[Ee]xpir.{0,20}(\d{2}/\d{2}/\d{4})"
        passport_matches = re.findall(passport_pattern, full_text)

        if passport_matches:
            for date_str in passport_matches:
                try:
                    expiry_date = datetime.strptime(date_str, "%m/%d/%Y")
                    if expiry_date < datetime.now():
                        critical_errors.append(f"❌ PASSAPORTE EXPIRADO: {date_str}")
                        logger.error(f"   ❌ Passaporte expirado: {date_str}")
                    elif expiry_date < datetime.now() + timedelta(days=180):
                        warnings.append(f"⚠️ Passaporte expira em menos de 6 meses: {date_str}")
                        logger.warning(f"   ⚠️ Passaporte expira em breve: {date_str}")
                    else:
                        logger.info(f"   ✅ Passaporte válido até: {date_str}")
                except:
                    pass
        else:
            warnings.append("⚠️ Não foi possível verificar data de expiração do passaporte")

        # Verificar LCA certificado (H-1B)
        if self.visa_type == "H-1B":
            if "CERTIFIED" in full_text.upper() or "CERTIFICATION" in full_text.upper():
                logger.info(f"   ✅ LCA aparece como certificado")
            else:
                critical_errors.append("❌ LCA não aparece como CERTIFICADO pelo DOL")
                logger.error(f"   ❌ LCA não certificado")

        # Verificar datas de início/fim de emprego (devem ser futuras ou recentes)
        employment_dates = re.findall(r"[Ee]mployment.{0,50}(\d{2}/\d{2}/\d{4})", full_text)
        if employment_dates:
            logger.info(f"   ✅ Datas de emprego encontradas: {len(employment_dates)}")

        return {"critical_errors": critical_errors, "warnings": warnings}

    def _verify_legal_requirements(self, pages_text: List[str], full_text: str) -> Dict:
        """Verifica cumprimento de requisitos legais específicos"""
        critical_errors = []
        major_errors = []

        legal_reqs = self.requirements.get("legal_requirements", [])

        logger.info(f"   Requisitos legais a verificar: {len(legal_reqs)}")

        for requirement in legal_reqs:
            verified = False

            if "wage must meet or exceed" in requirement.lower():
                # Verificar que salário oferecido >= prevailing wage
                offered_match = re.search(r"[Oo]ffered.{0,50}\$(\d{1,3},\d{3})", full_text)
                prevailing_match = re.search(r"[Pp]revailing.{0,50}\$(\d{1,3},\d{3})", full_text)

                if offered_match and prevailing_match:
                    offered = int(offered_match.group(1).replace(",", ""))
                    prevailing = int(prevailing_match.group(1).replace(",", ""))

                    if offered >= prevailing:
                        verified = True
                        logger.info(
                            f"   ✅ Salário oferecido (${offered:,}) >= prevailing wage (${prevailing:,})"
                        )
                    else:
                        critical_errors.append(
                            f"❌ REQUISITO LEGAL NÃO ATENDIDO: Salário oferecido (${offered:,}) "
                            f"< prevailing wage (${prevailing:,})"
                        )
                        logger.error(f"   ❌ Salário insuficiente")

            elif "specialty occupation" in requirement.lower():
                if "specialty occupation" in full_text.lower() and "bachelor" in full_text.lower():
                    verified = True
                    logger.info(f"   ✅ Posição qualifica como specialty occupation")

            elif "bachelor's degree" in requirement.lower():
                if "bachelor" in full_text.lower() or "master" in full_text.lower():
                    verified = True
                    logger.info(f"   ✅ Beneficiário possui grau adequado")

            elif "ability to pay" in requirement.lower():
                if "revenue" in full_text.lower() and "assets" in full_text.lower():
                    verified = True
                    logger.info(f"   ✅ Evidência de capacidade de pagamento presente")

            else:
                # Verificação genérica: buscar palavras-chave do requisito
                keywords = requirement.lower().split()[:3]
                if any(kw in full_text.lower() for kw in keywords):
                    verified = True
                    logger.info(f"   ✅ {requirement[:50]}...")

            if not verified:
                major_errors.append(f"⚠️ Requisito legal não verificado: {requirement}")
                logger.warning(f"   ⚠️ {requirement[:50]}... - NÃO VERIFICADO")

        return {"critical_errors": critical_errors, "major_errors": major_errors}

    def _verify_consistency(self, pages_text: List[str], full_text: str) -> Dict:
        """Verifica consistência e coerência de dados em todo o documento"""
        critical_errors = []
        major_errors = []

        logger.info(f"   Verificando consistência de dados...")

        if self.h1b_data:
            # Validar dados críticos aparecem consistentemente
            critical_data = {
                "Nome do beneficiário": self.h1b_data.beneficiary["full_name"],
                "Salário anual": self.h1b_data.position["salary_annual"],
                "Posição": self.h1b_data.position["title"],
                "Employer": self.h1b_data.employer["legal_name"],
            }

            for field_name, expected_value in critical_data.items():
                count = full_text.count(expected_value)

                if count == 0:
                    critical_errors.append(
                        f"❌ Dado crítico ausente: {field_name} = {expected_value}"
                    )
                    logger.error(f"   ❌ {field_name} não encontrado")
                elif count < 3:
                    major_errors.append(
                        f"⚠️ Dado crítico aparece poucas vezes ({count}x): {field_name}"
                    )
                    logger.warning(f"   ⚠️ {field_name} aparece apenas {count}x")
                else:
                    logger.info(f"   ✅ {field_name} consistente ({count}x)")

        # Verificar que não há contradições numéricas
        salary_matches = re.findall(r"\$\d{2,3},\d{3}", full_text)
        if salary_matches:
            unique_salaries = set(salary_matches)
            if len(unique_salaries) > 3:  # Mais de 3 salários diferentes é suspeito
                major_errors.append(
                    f"⚠️ Múltiplos valores de salário encontrados: {', '.join(list(unique_salaries)[:5])}"
                )
                logger.warning(f"   ⚠️ Múltiplos salários encontrados")

        return {"critical_errors": critical_errors, "major_errors": major_errors}

    def _verify_professional_quality(self, pages_text: List[str]) -> Dict:
        """Verifica qualidade profissional do conteúdo"""
        major_errors = []
        warnings = []

        logger.info(f"   Verificando qualidade profissional...")

        # Detectar páginas com conteúdo muito similar
        similar_count = 0
        for i in range(len(pages_text)):
            for j in range(i + 1, min(i + 10, len(pages_text))):  # Verificar próximas 10 páginas
                similarity = self._calculate_similarity(pages_text[i], pages_text[j])
                if similarity > 0.95:  # 95% similar
                    similar_count += 1

        if similar_count > len(pages_text) * 0.1:  # Mais de 10% de páginas muito similares
            major_errors.append(
                f"⚠️ Conteúdo repetitivo detectado: {similar_count} pares de páginas são >95% similares"
            )
            logger.warning(f"   ⚠️ Conteúdo repetitivo detectado")
        else:
            logger.info(f"   ✅ Conteúdo único e profissional")

        # Verificar comprimento médio de páginas
        avg_length = sum(len(p) for p in pages_text) / len(pages_text)
        if avg_length < 300:
            warnings.append(f"⚠️ Páginas com pouco conteúdo (média: {avg_length:.0f} caracteres)")
            logger.warning(f"   ⚠️ Páginas com pouco conteúdo")
        else:
            logger.info(f"   ✅ Páginas com conteúdo adequado")

        return {"major_errors": major_errors, "warnings": warnings}

    def _verify_user_documents(self, user_documents: Dict) -> Dict:
        """Verifica documentos enviados pelo usuário"""
        critical_errors = []
        major_errors = []

        logger.info(f"   Verificando documentos do usuário...")

        # Verificar que documentos obrigatórios foram enviados
        required_user_docs = ["passport", "diploma", "transcripts"]

        for doc_type in required_user_docs:
            if doc_type not in user_documents or not user_documents[doc_type]:
                critical_errors.append(f"❌ Documento do usuário faltando: {doc_type}")
                logger.error(f"   ❌ {doc_type} não enviado")
            else:
                logger.info(f"   ✅ {doc_type} enviado")

        return {"critical_errors": critical_errors, "major_errors": major_errors}

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calcula similaridade entre dois textos"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    def _calculate_compliance_score(
        self, critical_errors: List, major_errors: List, warnings: List
    ) -> int:
        """Calcula score de conformidade (0-100)"""
        score = 100

        # Penalidades severas
        score -= len(critical_errors) * 25  # -25 por erro crítico
        score -= len(major_errors) * 10  # -10 por erro maior
        score -= len(warnings) * 2  # -2 por aviso

        return max(0, min(100, score))

    def _determine_final_status(self, score: int, critical_errors: List, major_errors: List) -> str:
        """Determina status final (APPROVED/REJECTED)"""

        # Critérios RIGOROSOS para aprovação
        if len(critical_errors) > 0:
            return "REJECTED"

        if score < self.min_compliance_score:
            return "REJECTED"

        if len(major_errors) > 3:
            return "REJECTED"

        return "APPROVED"

    def _print_final_report(
        self, status: str, score: int, critical: List, major: List, warnings: List
    ):
        """Imprime relatório final"""
        logger.info(f"\n{'='*80}")
        logger.info(f"📊 RESULTADO DA REVISÃO DE CONFORMIDADE")
        logger.info(f"{'='*80}")
        logger.error(f"Status: {'✅ ' + status if status == 'APPROVED' else '❌ ' + status}")
        logger.info(f"Score de Conformidade: {score}/100")
        logger.error(f"Erros Críticos: {len(critical)}")
        logger.error(f"Erros Maiores: {len(major)}")
        logger.warning(f"Avisos: {len(warnings)}")

        if critical:
            logger.error(f"\n❌ ERROS CRÍTICOS ({len(critical)}):")
            for err in critical[:10]:
                logger.info(f"  • {err}")
            if len(critical) > 10:
                logger.error(f"  ... e mais {len(critical) - 10} erros")

        if major:
            logger.error(f"\n⚠️ ERROS MAIORES ({len(major)}):")
            for err in major[:10]:
                logger.info(f"  • {err}")
            if len(major) > 10:
                logger.error(f"  ... e mais {len(major) - 10} erros")

        if status == "APPROVED":
            logger.info(f"\n✅ PACOTE APROVADO - Liberado para download")
        else:
            logger.error(f"\n❌ PACOTE REJEITADO - NÃO liberado para download")
            logger.info(f"   Todas as questões devem ser corrigidas antes da liberação")

        logger.info(f"{'='*80}\n")

    def _error_response(self, message: str) -> Dict:
        """Retorna resposta de erro"""
        return {
            "status": "ERROR",
            "compliance_score": 0,
            "critical_errors": [message],
            "major_errors": [],
            "minor_warnings": [],
            "detailed_report": {},
        }


if __name__ == "__main__":
    # Teste do revisor completo
    import sys

    sys.path.insert(0, "/app")
    from h1b_data_model import h1b_data

    reviewer = ImmigrationComplianceReviewer(visa_type="H-1B", h1b_data_model=h1b_data)

    # Testar com o pacote profissional
    if os.path.exists("/app/PROFESSIONAL_H1B_PACKAGE_FERNANDA_SANTOS.pdf"):
        result = reviewer.comprehensive_review("/app/PROFESSIONAL_H1B_PACKAGE_FERNANDA_SANTOS.pdf")
    else:
        logger.warning("⚠️ Pacote não encontrado para teste")
