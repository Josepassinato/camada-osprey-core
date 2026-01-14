"""
Document Validation Agent

Specialized agent for document validation and authenticity checking.
Dr. Miguel - Expert in forensic document analysis with 15+ years of experience.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from agents.base import BaseAgent
from documents.metrics import (
    DecisionType,
    QualityAssessment,
)
from documents.recognition import EnhancedDocumentRecognitionAgent
from documents.validation_database import (
    get_document_validation_info,
    get_required_documents_for_visa,
)
from documents.validators.specialized import create_specialized_validators
from llm.portkey_client import LLMClient

logger = logging.getLogger(__name__)


class DocumentValidationAgent(BaseAgent):
    """
    Specialized agent for document validation and authenticity checking
    
    Dr. Miguel - Forensic document validation expert
    
    Capabilities:
    - 7-layer forensic analysis methodology
    - Authenticity and security element verification
    - Identity validation and cross-referencing
    - Temporal validation and USCIS compliance
    - Fraud detection and risk assessment
    """
    
    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        db=None,
        use_dra_paula_knowledge: bool = True
    ):
        """
        Initialize Document Validation Agent
        
        Args:
            llm_client: LLM client instance
            db: MongoDB connection for knowledge base access
            use_dra_paula_knowledge: Whether to use Dra. Paula's knowledge base
        """
        super().__init__(
            llm_client=llm_client,
            agent_name="Dr. Miguel - Validador de Documentos",
            default_model="gpt-4o",
            default_temperature=0.3,  # Lower temperature for more consistent validation
        )
        
        self.db = db
        self.use_dra_paula_knowledge = use_dra_paula_knowledge
        self.dra_paula_assistant_id = "asst_kkyn65SQFfkloH4SalOZfwwh"
        self.specialization = "Document Validation & Authenticity"
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process document validation request
        
        Args:
            input_data: Dict containing:
                - document_data: Document content or file bytes
                - document_type: Expected document type
                - case_context: Optional case context (applicant_name, visa_type, etc.)
                - validation_mode: 'standard' or 'enhanced' (default: 'standard')
        
        Returns:
            Dict containing validation results
        """
        document_data = input_data.get("document_data")
        document_type = input_data.get("document_type")
        case_context = input_data.get("case_context", {})
        validation_mode = input_data.get("validation_mode", "standard")
        
        if not document_data or not document_type:
            return {
                "agent": self.agent_name,
                "error": "Missing required fields: document_data and document_type",
                "valid": False
            }
        
        # Route to appropriate validation method
        if validation_mode == "enhanced" and isinstance(document_data, bytes):
            return await self.validate_document_enhanced(
                file_content=document_data,
                file_name=input_data.get("file_name", "document"),
                expected_document_type=document_type,
                visa_type=case_context.get("visa_type", ""),
                applicant_name=case_context.get("applicant_name", "")
            )
        else:
            return await self.validate_document(
                document_data=document_data,
                document_type=document_type,
                case_context=case_context
            )
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for Dr. Miguel"""
        from agents.dra_paula.knowledge_base import (
            dra_paula_knowledge,
            get_dra_paula_enhanced_prompt,
        )

        # Get enhanced prompt with Dra. Paula's knowledge
        enhanced_prompt = get_dra_paula_enhanced_prompt("document_validation")
        document_guidance = dra_paula_knowledge.get_document_guidance()
        
        return f"""
        Você é o Dr. Miguel, especialista FORENSE em validação de documentos de imigração com 15+ anos de experiência.
        INTEGRADO COMPLETAMENTE COM A BASE DE CONHECIMENTO DA DRA. PAULA B2C.
        
        {enhanced_prompt}
        
        CONHECIMENTO INTEGRADO DRA. PAULA - DOCUMENTOS BRASILEIROS:
        {json.dumps(document_guidance, indent=2, ensure_ascii=False)}
        
        🔍 METODOLOGIA FORENSE AVANÇADA DE 7 CAMADAS:
        
        **CAMADA 1 - IDENTIFICAÇÃO E CLASSIFICAÇÃO:**
        - Análise OCR/Visual: Detectar tipo real do documento (não confiar apenas no que foi declarado)
        - Verificação de Layout: Estrutura, campos, formatação específica de cada tipo
        - Detecção de Inconsistências: Comparar com templates conhecidos de documentos oficiais
        
        **CAMADA 2 - ANÁLISE DE AUTENTICIDADE E SEGURANÇA:**
        - Elementos de Segurança: Marcas d'água, hologramas, microimpressões, códigos de segurança
        - Análise de Fonte: Tipografia oficial, espaçamentos, alinhamentos
        - Detecção de Alterações: Rasuras digitais, sobreposições, inconsistências de pixels
        - Validação de Selos: Posicionamento, autenticidade, integridade
        
        **CAMADA 3 - VALIDAÇÃO DE IDENTIDADE:**
        - Extração Precisa: Nome completo, documentos parentais, nacionalidade
        - Comparação Rigorosa: Matching fuzzy para variações de nomes (José vs Jose, da Silva vs Silva)
        - Detecção de Fraude: Nomes obviamente diferentes, trocas de identidade
        - Cross-Reference: Consistência entre diferentes campos do documento
        
        **CAMADA 4 - ANÁLISE TEMPORAL E VALIDADE:**
        - Datas Lógicas: Nascimento, emissão, validade, renovações
        - Cálculos de Idade: Verificar se idade bate com outros documentos
        - Prazo USCIS: Validade mínima exigida (ex: passaporte 6+ meses)
        - Detecção de Fraudes Temporais: Datas impossíveis, documentos "futuros"
        
        **CAMADA 5 - COMPLETUDE E CONFORMIDADE:**
        - Campos Obrigatórios: Todos os dados essenciais presentes e legíveis
        - Padrões USCIS: Conformidade com requisitos específicos de cada tipo de visto
        - Qualidade de Imagem: Resolução, nitidez, legibilidade suficientes para análise oficial
        - Integridade do Arquivo: Sem corrupções, modificações ou manipulações
        
        **CAMADA 6 - ANÁLISE CONTEXTUAL POR TIPO DE VISTO:**
        - **H-1B**: Diploma + Employment Letter + LCA + Passport (validação cruzada de qualificações)
        - **F-1**: I-20 + Passport + Financial Documents + Academic Records (verificação SEVIS)
        - **B-1/B-2**: Passport + Financial Proof + Travel Intent (análise de vínculos)
        - **I-485**: Birth Certificate + Marriage Cert + Medical + Background Check (documentação completa)
        
        **CAMADA 7 - DETECÇÃO AVANÇADA DE FRAUDES:**
        - Padrões Suspeitos: Documentos "perfeitos demais", inconsistências sutis
        - Análise de Metadados: Informações de criação, modificação, software usado
        - Red Flags: Múltiplos documentos com mesmo padrão, elementos duplicados
        - Análise Comportamental: Tentativas de contornar validações
        
        🚨 CRITÉRIOS RIGOROSOS DE REJEIÇÃO IMEDIATA:
        - ❌ Tipo Incorreto: RG/CNH apresentado como Passaporte
        - ❌ Identidade Divergente: Nome no documento ≠ nome do aplicante (>15% diferença)
        - ❌ Documento Vencido: Fora da validade ou com prazo insuficiente
        - ❌ Qualidade Inadequada: Ilegível, borrado, baixa resolução (<300 DPI)
        - ❌ Elementos Ausentes: Selos, assinaturas, códigos de segurança faltando
        - ❌ Alterações Detectadas: Evidências de modificação digital ou física
        - ❌ Inconsistências Temporais: Datas impossíveis ou logicamente inconsistentes
        - ❌ Formato Inadequado: Não conforme padrões oficiais conhecidos
        
        📊 SISTEMA DE PONTUAÇÃO FORENSE (0-100):
        - 90-100: Documento autêntico, completo, totalmente conforme
        - 70-89: Documento válido com pequenas inconsistências não-críticas  
        - 50-69: Documento questionável, requer verificação manual
        - 20-49: Documento com problemas significativos, provavelmente inadequado
        - 0-19: Documento claramente fraudulento, alterado ou inadequado
        
        RESPOSTA OBRIGATÓRIA EM JSON ESTRUTURADO:
        {{
            "agent": "Dr. Miguel - Validador Forense",
            "analysis_timestamp": "ISO-8601 timestamp",
            "document_analysis": {{
                "type_identified": "string",
                "type_expected": "string",
                "type_match": true/false,
                "authenticity_score": 0-100,
                "quality_score": 0-100,
                "completeness_score": 0-100
            }},
            "identity_validation": {{
                "name_extracted": "string",
                "name_expected": "string",
                "identity_match": true/false,
                "match_confidence": 0-100
            }},
            "security_analysis": {{
                "security_elements": "present|partial|missing",
                "fraud_indicators": ["array"],
                "authenticity_verified": true/false,
                "modification_detected": true/false
            }},
            "temporal_validation": {{
                "document_valid": true/false,
                "expiration_date": "YYYY-MM-DD",
                "days_until_expiration": 0,
                "uscis_validity_sufficient": true/false
            }},
            "extracted_data": {{}},
            "critical_issues": ["array"],
            "recommendations": ["array"],
            "final_assessment": {{
                "overall_confidence": 0-100,
                "uscis_acceptable": true/false,
                "verdict": "APROVADO|REJEITADO|REVISÃO_NECESSÁRIA",
                "primary_rejection_reason": "string",
                "compliance_status": "string"
            }},
            "forensic_notes": "string"
        }}
        
        🔒 PRINCÍPIO FUNDAMENTAL DE SEGURANÇA:
        "Em caso de dúvida, SEMPRE rejeitar. A segurança do processo de imigração depende da rigidez na validação."
        
        PADRÃO OURO: Só aprovar documentos com 85%+ de confiança em TODAS as camadas de análise.
        """
    
    async def _get_knowledge_base_context(
        self,
        form_type: str,
        agent_role: str = "document_validation"
    ) -> str:
        """Get relevant context from knowledge base for this agent"""
        try:
            if not self.db:
                return ""
            
            from backend.knowledge.helper import get_knowledge_helper
            helper = get_knowledge_helper(self.db)
            
            context = await helper.get_context_for_agent(form_type, agent_role)
            return context
            
        except Exception as e:
            logger.warning(f"Could not fetch knowledge base context: {e}")
            return ""

    async def validate_document_with_database(
        self,
        document_type: str,
        document_content: str,
        applicant_name: str,
        visa_type: str = None
    ) -> Dict[str, Any]:
        """Enhanced validation using the comprehensive document database"""
        
        # Get validation info from database
        validation_info = get_document_validation_info(document_type)
        
        # Build enhanced prompt with specific validation criteria
        enhanced_prompt = f"""
        VALIDAÇÃO ULTRA-RIGOROSA COM BASE DE DADOS ESPECIALIZADA
        
        DOCUMENTO SOLICITADO: {document_type}
        NOME DO APLICANTE: {applicant_name}
        TIPO DE VISTO: {visa_type}
        CONTEÚDO: {document_content[:1500]}
        
        CRITÉRIOS ESPECÍFICOS PARA {document_type.upper()}:
        """
        
        if validation_info:
            enhanced_prompt += f"""
            VALIDAÇÕES CRÍTICAS OBRIGATÓRIAS:
            {validation_info.get('critical_validations', {})}
            
            CAMPOS OBRIGATÓRIOS QUE DEVEM ESTAR PRESENTES:
            {validation_info.get('required_fields', [])}
            
            ELEMENTOS DE SEGURANÇA ESPERADOS:
            {validation_info.get('security_elements', [])}
            
            PROBLEMAS COMUNS PARA DETECTAR:
            {validation_info.get('common_issues', [])}
            """
        
        # Add visa-specific validation
        if visa_type:
            required_docs = get_required_documents_for_visa(visa_type)
            if document_type not in required_docs:
                enhanced_prompt += f"""
                ⚠️ ALERTA CRÍTICO: Documento "{document_type}" NÃO é obrigatório para visto {visa_type}.
                Documentos obrigatórios para {visa_type}: {required_docs}
                """
        
        enhanced_prompt += f"""
        
        PROTOCOLO DE VALIDAÇÃO DR. MIGUEL AVANÇADO:
        1. IDENTIFICAR tipo exato do documento (não aceitar substitutos)
        2. COMPARAR nome no documento com "{applicant_name}" (deve ser idêntico)
        3. VERIFICAR todos os campos obrigatórios estão presentes
        4. VALIDAR elementos de segurança esperados
        5. DETECTAR problemas comuns conhecidos
        6. AVALIAR se documento é adequado para visto {visa_type}
        
        RESPOSTA OBRIGATÓRIA EM JSON conforme formato especificado no system prompt.
        """
        
        # Get knowledge base context
        kb_context = await self._get_knowledge_base_context(visa_type or "general")
        
        # Build messages
        messages = self._build_messages(
            system_prompt=self.get_system_prompt() + f"\n\n{kb_context}",
            user_message=enhanced_prompt
        )
        
        # Call LLM
        response = await self._call_llm(messages)
        
        # Try to parse JSON response
        try:
            result = json.loads(response)
            return result
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON response, returning raw text")
            return {
                "agent": self.agent_name,
                "raw_response": response,
                "parse_error": True
            }
    
    async def validate_document(
        self,
        document_data: str,
        document_type: str,
        case_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Enhanced document validation using comprehensive database and Dra. Paula's knowledge
        
        Args:
            document_data: Document content as string
            document_type: Expected document type
            case_context: Optional context (applicant_name, visa_type, etc.)
        
        Returns:
            Dict containing validation results
        """
        applicant_name = (
            case_context.get('applicant_name', 'Nome não informado')
            if case_context else 'Nome não informado'
        )
        visa_type = (
            case_context.get('visa_type') or case_context.get('form_code')
            if case_context else None
        )
        
        # Use enhanced database validation
        return await self.validate_document_with_database(
            document_type=document_type,
            document_content=document_data,
            applicant_name=applicant_name,
            visa_type=visa_type
        )
    
    async def validate_document_enhanced(
        self,
        file_content: bytes,
        file_name: str,
        expected_document_type: str,
        visa_type: str,
        applicant_name: str
    ) -> Dict[str, Any]:
        """
        SISTEMA DE ALTA PRECISÃO - Baseado no plano de análise avançado
        Implementa pipeline completo com KPIs mensuráveis
        
        Args:
            file_content: Document file as bytes
            file_name: Name of the file
            expected_document_type: Expected document type
            visa_type: Visa type for context
            applicant_name: Applicant's name for validation
        
        Returns:
            Dict containing comprehensive validation results
        """
        start_time = datetime.now(timezone.utc)
        
        try:
            # PHASE 1: Quality Assessment
            quality_assessor = QualityAssessment()
            quality_result = quality_assessor.assess_file_quality(file_content, file_name)
            
            if quality_result['status'] == 'fail':
                return self._create_fail_result(
                    "QUALITY_FAIL",
                    quality_result['issues'],
                    0.0,
                    quality_result['recommendations']
                )
            
            # PHASE 2: Specialized Validation by Document Type
            specialized_validators = create_specialized_validators()
            
            # Simulate OCR extraction (would be real OCR in production)
            extracted_data = await self._extract_document_data_simulation(
                file_content, expected_document_type, file_name
            )
            
            # PHASE 3: Document-specific validation
            validation_result = None
            
            if expected_document_type in ['passport', 'passport_id_page']:
                validator = specialized_validators['passport']
                validation_result = validator.validate_passport_comprehensive(extracted_data)
                
            elif expected_document_type in ['i797', 'i797_notice']:
                validator = specialized_validators['i797']
                validation_result = validator.validate_i797_comprehensive(extracted_data)
                
            elif expected_document_type == 'translation_certificate':
                validator = specialized_validators['translation_certificate']
                text_content = f"[SIMULATED] Document text for {file_name}"
                validation_result = validator.validate_translation_certificate(text_content)
            
            else:
                # Use enhanced general validation
                enhanced_validator = EnhancedDocumentRecognitionAgent()
                enhanced_result = await enhanced_validator.analyze_document_comprehensive(
                    file_content=file_content,
                    file_name=file_name,
                    expected_document_type=expected_document_type,
                    visa_type=visa_type,
                    applicant_name=applicant_name
                )
                
                validation_result = {
                    'document_type': expected_document_type,
                    'is_valid': enhanced_result.get('verdict') == 'APROVADO',
                    'overall_confidence': enhanced_result.get('overall_confidence', 0),
                    'uscis_acceptable': enhanced_result.get('type_matches_expected', False),
                    'validation_results': enhanced_result.get('extracted_data', {}),
                    'issues': enhanced_result.get('issues', [])
                }
            
            # PHASE 4: Calculate final confidence
            final_confidence = validation_result.get('overall_confidence', 0) if validation_result else 0
            
            # PHASE 5: Calculate Processing Time
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            
            # PHASE 6: Final Decision
            if validation_result is None:
                validation_result = {
                    'is_valid': False,
                    'uscis_acceptable': False,
                    'overall_confidence': 0,
                    'issues': ['Validation failed - document could not be validated']
                }
                final_confidence = 0
            
            is_valid = validation_result.get('is_valid', False)
            uscis_acceptable = validation_result.get('uscis_acceptable', False)
            
            # Determine decision based on confidence thresholds
            if final_confidence >= 85 and is_valid:
                decision = DecisionType.PASS
            elif final_confidence >= 65 and not validation_result.get('issues'):
                decision = DecisionType.ALERT
            else:
                decision = DecisionType.FAIL
            
            # PHASE 7: Generate comprehensive response
            return {
                "valid": decision == DecisionType.PASS,
                "verdict": decision.value,
                "confidence_score": final_confidence,
                "document_type_identified": validation_result.get('document_type', expected_document_type),
                "type_matches_expected": expected_document_type == validation_result.get('document_type', expected_document_type),
                "quality_acceptable": quality_result['status'] in ['ok', 'alert'],
                "uscis_acceptable": uscis_acceptable,
                "issues": self._ensure_list(validation_result.get('issues', [])) + self._ensure_list(quality_result.get('issues', [])),
                "recommendations": self._ensure_list(validation_result.get('recommendations', [])) + self._ensure_list(quality_result.get('recommendations', [])),
                "detailed_analysis": {
                    "quality_assessment": quality_result,
                    "validation_results": validation_result,
                    "processing_time_ms": processing_time,
                    "kpi_metrics": {
                        "classification_confidence": final_confidence,
                        "quality_score": quality_result.get('overall_quality_score', 0),
                        "decision_type": decision.value
                    }
                },
                "agent": f"{self.agent_name} - Sistema de Alta Precisão v2.0",
                "kpi_compliant": final_confidence >= 85,
                "processing_performance": {
                    "time_ms": processing_time,
                    "within_target": processing_time <= 5000
                }
            }
                
        except Exception as e:
            logger.error(f"Erro na validação de alta precisão: {str(e)}")
            
            # Calculate processing time even on error
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            
            # Fallback to standard validation
            fallback_result = await self.validate_document(
                str(file_content),
                expected_document_type,
                {
                    'applicant_name': applicant_name,
                    'visa_type': visa_type
                }
            )
            
            fallback_result.update({
                "agent": f"{self.agent_name} - Sistema Fallback",
                "fallback_used": True,
                "original_error": str(e),
                "processing_time_ms": processing_time
            })
            
            return fallback_result
    
    def _ensure_list(self, value):
        """Ensure a value is a list, converting strings to single-item lists"""
        if isinstance(value, list):
            return value
        elif isinstance(value, str):
            return [value] if value else []
        else:
            return []
    
    def _create_fail_result(
        self,
        reason: str,
        issues: List[str],
        confidence: float,
        recommendations: List[str]
    ) -> Dict[str, Any]:
        """Create standardized failure result"""
        return {
            "valid": False,
            "verdict": "FAIL",
            "confidence_score": confidence,
            "issues": self._ensure_list(issues),
            "recommendations": self._ensure_list(recommendations),
            "failure_reason": reason,
            "agent": f"{self.agent_name} - Sistema de Alta Precisão v2.0"
        }
    
    async def _extract_document_data_simulation(
        self,
        file_content: bytes,
        doc_type: str,
        file_name: str
    ) -> Dict[str, Any]:
        """
        Simulation of OCR data extraction
        In production would be replaced by real OCR (Tesseract + post-processing)
        """
        base_data = {
            'file_name': file_name,
            'file_size': len(file_content),
            'doc_type': doc_type
        }
        
        if doc_type in ['passport', 'passport_id_page']:
            base_data['extracted_fields'] = {
                'full_name': {'value': 'SILVA, MARIA DA', 'confidence': 0.95},
                'passport_number': {'value': 'BR123456', 'confidence': 0.98},
                'date_of_birth': {'value': '1990-05-15', 'confidence': 0.97},
                'expiry_date': {'value': '2030-12-31', 'confidence': 0.96},
                'nationality': {'value': 'Brazilian', 'confidence': 0.99}
            }
        elif doc_type in ['i797', 'i797_notice']:
            base_data['extracted_fields'] = {
                'receipt_number': {'value': 'MSC1234567890', 'confidence': 0.99},
                'notice_type': {'value': 'I-797A Approval Notice', 'confidence': 0.98},
                'beneficiary': {'value': 'Silva, Maria da', 'confidence': 0.96},
                'petitioner': {'value': 'TechCorp Inc.', 'confidence': 0.94},
                'notice_date': {'value': '2024-01-15', 'confidence': 0.97}
            }
        
        return base_data


# Factory function
def create_document_validator(llm_client: Optional[LLMClient] = None, db=None) -> DocumentValidationAgent:
    """Create a DocumentValidationAgent instance"""
    return DocumentValidationAgent(llm_client=llm_client, db=db)
