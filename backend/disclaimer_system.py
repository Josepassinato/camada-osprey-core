"""
Sistema de Disclaimer e Aceite de Responsabilidade
Gerencia aceites de responsabilidade por etapa do processo
"""

from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid
import logging

logger = logging.getLogger(__name__)

class DisclaimerStage(str, Enum):
    """Estágios do processo que requerem aceite"""
    DOCUMENTS = "documents"
    FORMS = "forms" 
    COVER_LETTER = "cover_letter"
    REVIEW = "review"
    FINAL = "final"

class DisclaimerAcceptance(BaseModel):
    """Modelo de aceite de disclaimer"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    case_id: str
    user_id: Optional[str] = None
    stage: DisclaimerStage
    consent_hash: str
    consent_text: str
    
    # Metadata do aceite
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Dados adicionais
    stage_data: Optional[Dict[str, Any]] = None
    is_required: bool = True
    accepted: bool = True

class DisclaimerValidation(BaseModel):
    """Resultado da validação de disclaimers"""
    case_id: str
    all_required_accepted: bool
    missing_stages: List[DisclaimerStage]
    accepted_stages: List[DisclaimerStage]
    total_acceptances: int
    latest_acceptance: Optional[datetime] = None

class DisclaimerSystem:
    """Sistema de gerenciamento de disclaimers"""
    
    def __init__(self, db):
        self.db = db
        self.collection = db.disclaimer_acceptances
        
        # Textos padrão dos disclaimers por estágio
        self.disclaimer_texts = {
            DisclaimerStage.DOCUMENTS: """
ACEITE DE RESPONSABILIDADE - DOCUMENTAÇÃO

Ao prosseguir com o upload e validação de documentos, você confirma que:

1. AUTENTICIDADE DOS DOCUMENTOS
   • Todos os documentos enviados são ORIGINAIS e AUTÊNTICOS
   • Não foram alterados, modificados ou falsificados de qualquer forma
   • Você possui legal autoridade para fornecer estes documentos

2. RESPONSABILIDADE LEGAL
   • Você é TOTALMENTE RESPONSÁVEL pela veracidade de todos os documentos
   • Entende que documentos falsos podem resultar em negação permanente de vistos
   • Assume todas as consequências legais por documentos inadequados

3. SISTEMA INFORMATIVO
   • Este sistema oferece validação INFORMATIVA baseada em padrões públicos
   • NÃO substitui revisão profissional por advogado de imigração
   • Recomendamos consulta jurídica para casos complexos

4. ISENÇÃO DE RESPONSABILIDADE
   • O sistema não garante aprovação pelo USCIS
   • Você é responsável por verificar todos os requisitos oficiais
   • Este serviço não constitui aconselhamento jurídico
            """,
            
            DisclaimerStage.FORMS: """
ACEITE DE RESPONSABILIDADE - FORMULÁRIOS USCIS

Ao prosseguir com o preenchimento de formulários, você confirma que:

1. VERACIDADE DAS INFORMAÇÕES
   • Todas as informações fornecidas são VERDADEIRAS e COMPLETAS
   • Não omitiu nenhuma informação relevante solicitada
   • Entende que informações falsas podem resultar em consequências legais

2. FORMULÁRIOS OFICIAIS
   • Os formulários gerados seguem padrões públicos do USCIS
   • Você deve revisar TODA informação antes de submeter ao USCIS
   • Este sistema facilita o preenchimento mas NÃO garante aprovação

3. RESPONSABILIDADE FINAL
   • Você é RESPONSÁVEL por revisar e validar todos os dados
   • Deve verificar requisitos atuais no site oficial do USCIS
   • Recomendamos revisão por advogado especializado

4. LIMITAÇÕES DO SISTEMA
   • Este é um sistema de apoio informativo
   • Não substitui consultoria jurídica profissional
   • Para casos complexos, consulte sempre um advogado de imigração
            """,
            
            DisclaimerStage.COVER_LETTER: """
ACEITE DE RESPONSABILIDADE - CARTA DE APRESENTAÇÃO

Ao prosseguir com a geração da carta de apresentação, você confirma que:

1. CONTEÚDO BASEADO EM FATOS
   • A carta será baseada nas informações que VOCÊ forneceu
   • Você garante que todos os fatos mencionados são VERDADEIROS
   • Não há invenção ou exagero de qualificações ou experiências

2. REVISÃO OBRIGATÓRIA
   • Você DEVE revisar completamente a carta antes de usar
   • É sua responsabilidade corrigir qualquer erro ou imprecisão
   • O sistema gera sugestões baseadas em suas informações

3. USO APROPRIADO
   • A carta é um apoio ao seu processo de aplicação
   • Não garante aprovação pelo USCIS
   • Deve ser usada como base, podendo ser personalizada

4. CONSULTORIA JURÍDICA
   • Para casos complexos, consulte um advogado especializado
   • Este sistema não oferece aconselhamento jurídico
   • Recomendamos revisão profissional antes da submissão final
            """,
            
            DisclaimerStage.REVIEW: """
ACEITE DE RESPONSABILIDADE - REVISÃO FINAL

Ao prosseguir com a revisão final do seu processo, você confirma que:

1. REVISÃO COMPLETA
   • Revisou TODOS os documentos, formulários e cartas gerados
   • Verificou a precisão de todas as informações fornecidas
   • Confirma que tudo está correto e atualizado

2. RESPONSABILIDADE INTEGRAL
   • Assume TOTAL responsabilidade por todo o conteúdo do processo
   • Entende que você é o único responsável pela submissão ao USCIS
   • Qualquer erro ou omissão é de sua responsabilidade

3. NATUREZA INFORMATIVA
   • Este sistema oferece orientação baseada em requisitos públicos
   • NÃO constitui aconselhamento jurídico profissional
   • Não garante aprovação ou sucesso no processo

4. RECOMENDAÇÕES FINAIS
   • Verifique requisitos atuais no site oficial do USCIS (uscis.gov)
   • Consulte um advogado de imigração para casos complexos
   • Mantenha cópias de todos os documentos enviados
            """,
            
            DisclaimerStage.FINAL: """
ACEITE FINAL DE RESPONSABILIDADE - ANTES DO DOWNLOAD

IMPORTANTE: Leia cuidadosamente antes de prosseguir com o pagamento e download.

Ao finalizar este processo e fazer o download dos documentos, você declara e concorda que:

1. RESPONSABILIDADE TOTAL
   • Você é ÚNICA E EXCLUSIVAMENTE responsável por todas as informações fornecidas
   • Assume total responsabilidade pela veracidade de todos os documentos
   • Entende que este sistema é APENAS informativo e educacional

2. NATUREZA DO SERVIÇO
   • Este sistema NÃO constitui aconselhamento jurídico
   • NÃO somos escritório de advocacia ou consultoria jurídica
   • Os documentos gerados são baseados em informações públicas do USCIS

3. LIMITAÇÕES E ISENÇÕES
   • NÃO garantimos aprovação pelo USCIS
   • NÃO nos responsabilizamos por negações ou problemas no processo
   • Requisitos podem mudar - sempre verifique o site oficial do USCIS

4. RECOMENDAÇÕES IMPORTANTES
   • SEMPRE consulte um advogado de imigração qualificado
   • Verifique todos os requisitos atuais no site oficial (uscis.gov)
   • Revise TODOS os documentos antes de enviar ao USCIS

5. CONCORDÂNCIA FINAL
   • Ao prosseguir, você ISENTA nossa plataforma de qualquer responsabilidade
   • Entende que todo o processo é de sua responsabilidade
   • Concorda em não nos responsabilizar por qualquer resultado

PARA CASOS COMPLEXOS, SEMPRE CONSULTE UM ADVOGADO ESPECIALIZADO EM IMIGRAÇÃO.
            """
        }

    async def record_acceptance(
        self,
        case_id: str,
        stage: DisclaimerStage,
        consent_hash: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        stage_data: Optional[Dict[str, Any]] = None
    ) -> DisclaimerAcceptance:
        """Registra aceite de disclaimer"""
        try:
            # Buscar texto padrão para o estágio
            consent_text = self.disclaimer_texts.get(stage, "Aceite genérico de responsabilidade")
            
            # Criar registro de aceite
            acceptance = DisclaimerAcceptance(
                case_id=case_id,
                user_id=user_id,
                stage=stage,
                consent_hash=consent_hash,
                consent_text=consent_text,
                ip_address=ip_address,
                user_agent=user_agent,
                stage_data=stage_data or {}
            )
            
            # Salvar no banco
            await self.collection.insert_one(acceptance.dict())
            
            logger.info(f"Disclaimer acceptance recorded: {case_id} - {stage.value}")
            return acceptance
            
        except Exception as e:
            logger.error(f"Error recording disclaimer acceptance: {e}")
            raise

    async def validate_case_compliance(self, case_id: str) -> DisclaimerValidation:
        """Valida se caso tem todos os aceites obrigatórios"""
        try:
            # Buscar todos os aceites do caso
            acceptances = await self.collection.find(
                {"case_id": case_id}
            ).to_list(length=None)
            
            accepted_stages = [DisclaimerStage(acc["stage"]) for acc in acceptances]
            
            # Determinar estágios obrigatórios (todos exceto final até chegar lá)
            required_stages = [
                DisclaimerStage.DOCUMENTS,
                DisclaimerStage.FORMS,
                DisclaimerStage.COVER_LETTER,
                DisclaimerStage.REVIEW
            ]
            
            missing_stages = [stage for stage in required_stages if stage not in accepted_stages]
            
            # Buscar último aceite
            latest_acceptance = None
            if acceptances:
                latest_timestamp = max(acc["timestamp"] for acc in acceptances)
                latest_acceptance = datetime.fromisoformat(latest_timestamp.replace('Z', '+00:00'))
            
            validation = DisclaimerValidation(
                case_id=case_id,
                all_required_accepted=len(missing_stages) == 0,
                missing_stages=missing_stages,
                accepted_stages=accepted_stages,
                total_acceptances=len(acceptances),
                latest_acceptance=latest_acceptance
            )
            
            return validation
            
        except Exception as e:
            logger.error(f"Error validating case compliance: {e}")
            raise

    async def check_stage_required(self, case_id: str, stage: DisclaimerStage) -> bool:
        """Verifica se aceite é obrigatório para o estágio"""
        try:
            # Verificar se já foi aceito
            existing = await self.collection.find_one({
                "case_id": case_id,
                "stage": stage.value
            })
            
            # Se já foi aceito, não é mais obrigatório
            if existing:
                return False
            
            # Todos os estágios requerem aceite por padrão
            return True
            
        except Exception as e:
            logger.error(f"Error checking stage requirement: {e}")
            return True  # Em caso de erro, assume que é obrigatório

    async def get_case_acceptances(self, case_id: str) -> List[DisclaimerAcceptance]:
        """Busca todos os aceites de um caso"""
        try:
            acceptances = await self.collection.find(
                {"case_id": case_id}
            ).sort("timestamp", -1).to_list(length=None)
            
            return [DisclaimerAcceptance(**acc) for acc in acceptances]
            
        except Exception as e:
            logger.error(f"Error getting case acceptances: {e}")
            return []

    async def check_final_disclaimer_ready(self, case_id: str) -> bool:
        """Verifica se está pronto para disclaimer final"""
        try:
            validation = await self.validate_case_compliance(case_id)
            
            # Para estar pronto para disclaimer final, precisa ter todos os outros aceites
            required_before_final = [
                DisclaimerStage.DOCUMENTS,
                DisclaimerStage.FORMS, 
                DisclaimerStage.COVER_LETTER,
                DisclaimerStage.REVIEW
            ]
            
            missing_required = [
                stage for stage in required_before_final 
                if stage not in validation.accepted_stages
            ]
            
            return len(missing_required) == 0
            
        except Exception as e:
            logger.error(f"Error checking final disclaimer readiness: {e}")
            return False

    def get_disclaimer_text(self, stage: DisclaimerStage) -> str:
        """Retorna texto do disclaimer para um estágio"""
        return self.disclaimer_texts.get(stage, "Aceite genérico de responsabilidade")

    async def generate_compliance_report(self, case_id: str) -> Dict[str, Any]:
        """Gera relatório de compliance para auditoria"""
        try:
            acceptances = await self.get_case_acceptances(case_id)
            validation = await self.validate_case_compliance(case_id)
            
            report = {
                "case_id": case_id,
                "compliance_status": "compliant" if validation.all_required_accepted else "non_compliant",
                "total_acceptances": len(acceptances),
                "accepted_stages": [stage.value for stage in validation.accepted_stages],
                "missing_stages": [stage.value for stage in validation.missing_stages],
                "acceptance_timeline": [
                    {
                        "stage": acc.stage.value,
                        "timestamp": acc.timestamp.isoformat(),
                        "consent_hash": acc.consent_hash,
                        "ip_address": acc.ip_address
                    }
                    for acc in acceptances
                ],
                "ready_for_final": await self.check_final_disclaimer_ready(case_id),
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating compliance report: {e}")
            return {
                "case_id": case_id,
                "compliance_status": "error", 
                "error": str(e)
            }