"""
Fraud Detection AI System - Phase 4C
Sistema de detecção de fraudes usando IA para aplicações de imigração
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
import hashlib
import json
import statistics
from collections import defaultdict
import uuid

# Import AI services
from immigration_expert import create_immigration_expert

logger = logging.getLogger(__name__)

@dataclass
class FraudAlert:
    """Alerta de fraude detectado"""
    alert_id: str
    case_id: str
    user_id: Optional[str]
    fraud_type: str
    severity: str  # low, medium, high, critical
    confidence_score: float
    evidence: List[str]
    timestamp: datetime
    status: str = "pending"  # pending, investigating, resolved, false_positive
    investigator: Optional[str] = None
    resolution_notes: Optional[str] = None

@dataclass
class FraudPattern:
    """Padrão de fraude detectado"""
    pattern_id: str
    pattern_name: str
    description: str
    indicators: List[str]
    threshold_score: float
    last_detected: Optional[datetime]
    detection_count: int
    false_positive_rate: float

@dataclass
class RiskScore:
    """Score de risco calculado para um caso"""
    case_id: str
    overall_score: float
    risk_factors: Dict[str, float]
    risk_level: str  # low, medium, high, critical
    recommendations: List[str]
    calculated_at: datetime

class FraudDetectionAI:
    """
    Sistema de detecção de fraudes usando IA
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.fraud_alerts: List[FraudAlert] = []
        
        # Initialize AI expert for fraud analysis
        self.fraud_expert = create_immigration_expert(
            model="gpt-4o",
            custom_prompt="""
            Você é um especialista em detecção de fraudes em aplicações de imigração.
            Analise documentos e dados fornecidos para identificar possíveis fraudes.
            
            Foque em:
            - Inconsistências entre documentos
            - Dados irreais ou impossíveis
            - Padrões suspeitos de comportamento
            - Documentos falsificados ou alterados
            - Informações contraditórias
            
            Sempre forneça evidências específicas e score de confiança.
            """
        )
        
        # Padrões de fraude conhecidos
        self.fraud_patterns = {
            "document_inconsistency": FraudPattern(
                pattern_id="doc_inconsistency",
                pattern_name="Inconsistência entre Documentos",
                description="Dados contraditórios entre diferentes documentos",
                indicators=[
                    "Nomes diferentes em documentos",
                    "Datas de nascimento divergentes",
                    "Informações de endereço contraditórias"
                ],
                threshold_score=0.7,
                last_detected=None,
                detection_count=0,
                false_positive_rate=0.15
            ),
            
            "unrealistic_data": FraudPattern(
                pattern_id="unrealistic_data",
                pattern_name="Dados Não Realistas",
                description="Informações que não são plausíveis",
                indicators=[
                    "Salários extremamente altos ou baixos",
                    "Idades impossíveis",
                    "Datas futuras ou muito antigas"
                ],
                threshold_score=0.8,
                last_detected=None,
                detection_count=0,
                false_positive_rate=0.10
            ),
            
            "duplicate_submission": FraudPattern(
                pattern_id="duplicate_submission",
                pattern_name="Submissão Duplicada",
                description="Múltiplas submissões idênticas ou similares",
                indicators=[
                    "Documentos idênticos em casos diferentes",
                    "Dados pessoais duplicados",
                    "IPs ou dispositivos reutilizados"
                ],
                threshold_score=0.9,
                last_detected=None,
                detection_count=0,
                false_positive_rate=0.05
            ),
            
            "rapid_submission": FraudPattern(
                pattern_id="rapid_submission",
                pattern_name="Submissão Muito Rápida",
                description="Preenchimento suspeitamente rápido",
                indicators=[
                    "Formulário preenchido em menos de 2 minutos",
                    "Upload de múltiplos documentos simultaneamente",
                    "Sem tempo de revisão"
                ],
                threshold_score=0.6,
                last_detected=None,
                detection_count=0,
                false_positive_rate=0.25
            ),
            
            "suspicious_ip_patterns": FraudPattern(
                pattern_id="suspicious_ip",
                pattern_name="Padrões Suspeitos de IP",
                description="Atividade suspeita de IP ou geolocalização",
                indicators=[
                    "Múltiplos casos do mesmo IP",
                    "IPs de países não relacionados ao visto",
                    "Uso de VPN/proxy detectado"
                ],
                threshold_score=0.7,
                last_detected=None,
                detection_count=0,
                false_positive_rate=0.30
            ),
            
            "document_quality_fraud": FraudPattern(
                pattern_id="doc_quality_fraud",
                pattern_name="Qualidade Suspeita de Documento",
                description="Documentos com sinais de falsificação",
                indicators=[
                    "Qualidade de OCR muito baixa",
                    "Padrões de pixel suspeitos",
                    "Metadados de arquivo inconsistentes"
                ],
                threshold_score=0.8,
                last_detected=None,
                detection_count=0,
                false_positive_rate=0.12
            )
        }
        
        # Thresholds de risco
        self.risk_thresholds = {
            "low": 0.3,
            "medium": 0.5,
            "high": 0.7,
            "critical": 0.85
        }
        
        # Start background monitoring
        asyncio.create_task(self._monitor_fraud_patterns())
    
    async def analyze_case_for_fraud(self, case_id: str) -> RiskScore:
        """
        Analisa um caso completo para detecção de fraudes
        """
        try:
            logger.info(f"🔍 Starting fraud analysis for case: {case_id}")
            
            # Recuperar dados do caso
            case_data = await self._get_case_complete_data(case_id)
            
            if not case_data:
                return RiskScore(
                    case_id=case_id,
                    overall_score=0.0,
                    risk_factors={},
                    risk_level="unknown",
                    recommendations=["Dados do caso não encontrados"],
                    calculated_at=datetime.now(timezone.utc)
                )
            
            # Executar diferentes tipos de análise
            risk_factors = {}
            
            # 1. Análise de documentos
            document_risk = await self._analyze_document_fraud(case_data)
            risk_factors.update(document_risk)
            
            # 2. Análise de dados pessoais
            personal_risk = await self._analyze_personal_data_fraud(case_data)
            risk_factors.update(personal_risk)
            
            # 3. Análise comportamental
            behavioral_risk = await self._analyze_behavioral_fraud(case_data)
            risk_factors.update(behavioral_risk)
            
            # 4. Análise de padrões
            pattern_risk = await self._analyze_fraud_patterns(case_data)
            risk_factors.update(pattern_risk)
            
            # 5. Análise de IA especializada
            ai_risk = await self._analyze_with_ai_expert(case_data)
            risk_factors.update(ai_risk)
            
            # Calcular score geral (média ponderada)
            weights = {
                "document_risk": 0.25,
                "personal_data_risk": 0.20,
                "behavioral_risk": 0.20,
                "pattern_risk": 0.20,
                "ai_expert_risk": 0.15
            }
            
            overall_score = sum(
                risk_factors.get(factor, 0) * weight
                for factor, weight in weights.items()
            )
            
            # Determinar nível de risco
            risk_level = self._calculate_risk_level(overall_score)
            
            # Gerar recomendações
            recommendations = self._generate_fraud_recommendations(risk_factors, risk_level)
            
            # Criar alerts se necessário
            if overall_score >= self.risk_thresholds["high"]:
                await self._create_fraud_alert(case_id, risk_factors, overall_score)
            
            risk_score = RiskScore(
                case_id=case_id,
                overall_score=overall_score,
                risk_factors=risk_factors,
                risk_level=risk_level,
                recommendations=recommendations,
                calculated_at=datetime.now(timezone.utc)
            )
            
            # Salvar no banco
            await self._save_risk_score(risk_score)
            
            logger.info(f"✅ Fraud analysis completed for {case_id}: {risk_level} risk ({overall_score:.2f})")
            
            return risk_score
            
        except Exception as e:
            logger.error(f"❌ Error in fraud analysis for {case_id}: {e}")
            return RiskScore(
                case_id=case_id,
                overall_score=0.0,
                risk_factors={"error": 1.0},
                risk_level="error",
                recommendations=[f"Erro na análise: {str(e)}"],
                calculated_at=datetime.now(timezone.utc)
            )
    
    async def _get_case_complete_data(self, case_id: str) -> Optional[Dict[str, Any]]:
        """
        Recupera dados completos do caso para análise
        """
        try:
            # Dados básicos do caso
            case = await self.db.cases.find_one({"case_id": case_id})
            if not case:
                return None
            
            # Documentos
            documents = await self.db.documents.find({"case_id": case_id}).to_list(None)
            
            # Dados do formulário
            form_data = await self.db.friendly_forms.find_one({"case_id": case_id})
            
            # Dados de sessão/comportamento
            journey_data = await self.db.user_journey_metrics.find_one({"case_id": case_id})
            
            # Analytics events do caso
            events = await self.db.analytics_events.find({"case_id": case_id}).to_list(None)
            
            return {
                "case": case,
                "documents": documents,
                "form_data": form_data,
                "journey_data": journey_data,
                "events": events
            }
            
        except Exception as e:
            logger.error(f"Error getting case data for fraud analysis: {e}")
            return None
    
    async def _analyze_document_fraud(self, case_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Analisa documentos para sinais de fraude
        """
        try:
            documents = case_data.get("documents", [])
            risk_score = 0.0
            
            if not documents:
                return {"document_risk": 0.2}  # Risco baixo por falta de documentos
            
            document_issues = []
            
            # Verificar consistência entre documentos
            names_found = set()
            dates_of_birth = set()
            addresses = set()
            
            for doc in documents:
                extracted_data = doc.get("extracted_data", {})
                
                # Coletar nomes
                if extracted_data.get("name"):
                    names_found.add(extracted_data["name"].lower().strip())
                
                # Coletar datas de nascimento
                if extracted_data.get("date_of_birth"):
                    dates_of_birth.add(extracted_data["date_of_birth"])
                
                # Coletar endereços
                if extracted_data.get("address"):
                    addresses.add(extracted_data["address"].lower().strip())
                
                # Verificar qualidade do documento
                confidence_score = doc.get("confidence_score", 1.0)
                if confidence_score < 0.5:
                    document_issues.append(f"Documento de baixa qualidade: {doc.get('filename', 'unknown')}")
                    risk_score += 0.1
                
                # Verificar se há issues críticos
                issues = doc.get("issues", [])
                critical_issues = [issue for issue in issues if "falsificado" in issue.lower() or "alterado" in issue.lower()]
                if critical_issues:
                    document_issues.append(f"Possível falsificação detectada: {doc.get('filename', 'unknown')}")
                    risk_score += 0.3
            
            # Verificar inconsistências
            if len(names_found) > 2:  # Tolerância para pequenas variações
                document_issues.append(f"Múltiplos nomes encontrados: {list(names_found)}")
                risk_score += 0.4
            
            if len(dates_of_birth) > 1:
                document_issues.append(f"Datas de nascimento conflitantes: {list(dates_of_birth)}")
                risk_score += 0.5
            
            # Normalizar score
            risk_score = min(risk_score, 1.0)
            
            return {"document_risk": risk_score}
            
        except Exception as e:
            logger.error(f"Error in document fraud analysis: {e}")
            return {"document_risk": 0.0}
    
    async def _analyze_personal_data_fraud(self, case_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Analisa dados pessoais para sinais de fraude
        """
        try:
            form_data = case_data.get("form_data", {})
            risk_score = 0.0
            
            if not form_data:
                return {"personal_data_risk": 0.1}
            
            personal_info = form_data.get("personal_info", {})
            employment_info = form_data.get("employment_info", {})
            
            # Verificar dados irreais
            # Idade suspeita
            if personal_info.get("age"):
                age = int(personal_info.get("age", 0))
                if age < 18 or age > 80:
                    risk_score += 0.2
                elif age < 21 and employment_info.get("years_experience", 0) > 5:
                    risk_score += 0.3  # Experiência incompatível com idade
            
            # Salário suspeito
            if employment_info.get("salary"):
                try:
                    salary = float(employment_info.get("salary", 0))
                    if salary > 500000:  # Salário muito alto
                        risk_score += 0.2
                    elif salary < 30000:  # Salário muito baixo para visto H-1B
                        risk_score += 0.1
                except (ValueError, TypeError):
                    risk_score += 0.1
            
            # Verificar campos obrigatórios vazios ou suspeitos
            required_fields = ["full_name", "email", "phone"]
            empty_required = [field for field in required_fields if not personal_info.get(field)]
            
            if empty_required:
                risk_score += len(empty_required) * 0.1
            
            # Verificar padrões de email suspeitos
            email = personal_info.get("email", "")
            if email:
                suspicious_domains = ["10minutemail", "tempmail", "guerrillamail", "mailinator"]
                if any(domain in email.lower() for domain in suspicious_domains):
                    risk_score += 0.4
            
            return {"personal_data_risk": min(risk_score, 1.0)}
            
        except Exception as e:
            logger.error(f"Error in personal data fraud analysis: {e}")
            return {"personal_data_risk": 0.0}
    
    async def _analyze_behavioral_fraud(self, case_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Analisa comportamento do usuário para sinais de fraude
        """
        try:
            journey_data = case_data.get("journey_data", {})
            events = case_data.get("events", [])
            
            risk_score = 0.0
            
            # Analisar tempo de preenchimento
            if journey_data:
                journey_start = journey_data.get("journey_start")
                case_completion = journey_data.get("case_completion_time")
                
                if journey_start and case_completion:
                    if isinstance(journey_start, str):
                        journey_start = datetime.fromisoformat(journey_start.replace('Z', '+00:00'))
                    if isinstance(case_completion, str):
                        case_completion = datetime.fromisoformat(case_completion.replace('Z', '+00:00'))
                    
                    total_time_minutes = (case_completion - journey_start).total_seconds() / 60
                    
                    # Preenchimento muito rápido (menos de 5 minutos)
                    if total_time_minutes < 5:
                        risk_score += 0.4
                    # Preenchimento muito lento (mais de 24 horas sem pausas)
                    elif total_time_minutes > 1440:
                        risk_score += 0.2
            
            # Analisar padrões de eventos
            if events:
                # Verificar eventos duplicados ou suspeitos
                event_times = [datetime.fromisoformat(e["timestamp"].replace('Z', '+00:00')) for e in events if e.get("timestamp")]
                
                if len(event_times) > 1:
                    # Calcular intervalos entre eventos
                    intervals = []
                    for i in range(1, len(event_times)):
                        interval = (event_times[i] - event_times[i-1]).total_seconds()
                        intervals.append(interval)
                    
                    # Intervalos muito regulares podem indicar bot
                    if len(intervals) > 5:
                        interval_variance = statistics.variance(intervals)
                        if interval_variance < 1.0:  # Intervalos muito regulares
                            risk_score += 0.3
                
                # Verificar múltiplas tentativas rápidas
                error_events = [e for e in events if not e.get("success", True)]
                if len(error_events) > 10:
                    risk_score += 0.2
            
            # Verificar tentativas de retry excessivas
            retry_attempts = journey_data.get("retry_attempts", {})
            if retry_attempts:
                total_retries = sum(retry_attempts.values())
                if total_retries > 20:
                    risk_score += 0.3
            
            return {"behavioral_risk": min(risk_score, 1.0)}
            
        except Exception as e:
            logger.error(f"Error in behavioral fraud analysis: {e}")
            return {"behavioral_risk": 0.0}
    
    async def _analyze_fraud_patterns(self, case_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Compara caso contra padrões de fraude conhecidos
        """
        try:
            risk_score = 0.0
            matched_patterns = []
            
            case_id = case_data.get("case", {}).get("case_id", "")
            
            # Verificar padrão de submissão duplicada
            similar_cases = await self._find_similar_cases(case_data)
            if len(similar_cases) > 0:
                risk_score += 0.3
                matched_patterns.append("duplicate_submission")
            
            # Verificar padrão de IP suspeito
            case_ip = case_data.get("case", {}).get("client_ip", "")
            if case_ip:
                ip_cases_count = await self.db.cases.count_documents({"client_ip": case_ip})
                if ip_cases_count > 5:  # Muitos casos do mesmo IP
                    risk_score += 0.2
                    matched_patterns.append("suspicious_ip_patterns")
            
            # Verificar documentos de qualidade muito baixa
            documents = case_data.get("documents", [])
            low_quality_docs = [d for d in documents if d.get("confidence_score", 1.0) < 0.3]
            if len(low_quality_docs) > len(documents) * 0.5:  # Mais da metade com baixa qualidade
                risk_score += 0.4
                matched_patterns.append("document_quality_fraud")
            
            # Atualizar contadores de padrões
            for pattern_id in matched_patterns:
                if pattern_id in self.fraud_patterns:
                    self.fraud_patterns[pattern_id].detection_count += 1
                    self.fraud_patterns[pattern_id].last_detected = datetime.now(timezone.utc)
            
            return {"pattern_risk": min(risk_score, 1.0)}
            
        except Exception as e:
            logger.error(f"Error in fraud pattern analysis: {e}")
            return {"pattern_risk": 0.0}
    
    async def _analyze_with_ai_expert(self, case_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Usa IA especializada para análise avançada de fraudes
        """
        try:
            # Preparar dados para análise da IA
            analysis_prompt = self._prepare_fraud_analysis_prompt(case_data)
            
            # Solicitar análise da IA especializada
            ai_response = await self.fraud_expert.analyze_case_data(
                case_data=analysis_prompt,
                analysis_type="fraud_detection"
            )
            
            if ai_response and ai_response.get("success"):
                analysis_result = ai_response.get("analysis", {})
                
                # Extrair score de risco da resposta da IA
                ai_risk_score = analysis_result.get("fraud_risk_score", 0.0)
                
                # Normalizar se necessário
                if ai_risk_score > 1.0:
                    ai_risk_score = ai_risk_score / 100  # Se veio como percentual
                
                return {"ai_expert_risk": min(ai_risk_score, 1.0)}
            else:
                return {"ai_expert_risk": 0.0}
            
        except Exception as e:
            logger.warning(f"AI expert analysis failed, using fallback: {e}")
            return {"ai_expert_risk": 0.0}
    
    def _prepare_fraud_analysis_prompt(self, case_data: Dict[str, Any]) -> str:
        """
        Prepara prompt para análise de fraude pela IA
        """
        case = case_data.get("case", {})
        documents = case_data.get("documents", [])
        form_data = case_data.get("form_data", {})
        
        prompt = f"""
ANÁLISE DE FRAUDE - CASO {case.get('case_id', 'unknown')}

DADOS DO CASO:
- Tipo de visto: {case.get('form_code', 'unknown')}
- Status: {case.get('status', 'unknown')}
- Data de criação: {case.get('created_at', 'unknown')}

DOCUMENTOS ({len(documents)}):
"""
        
        for i, doc in enumerate(documents, 1):
            prompt += f"""
{i}. {doc.get('filename', 'unknown')}
   - Tipo: {doc.get('document_type', 'unknown')}
   - Confiança: {doc.get('confidence_score', 0):.2f}
   - Status: {doc.get('validation_status', 'unknown')}
   - Issues: {', '.join(doc.get('issues', [])) if doc.get('issues') else 'None'}
"""
        
        if form_data:
            personal = form_data.get("personal_info", {})
            employment = form_data.get("employment_info", {})
            
            prompt += f"""
DADOS PESSOAIS:
- Nome: {personal.get('full_name', 'N/A')}
- Idade: {personal.get('age', 'N/A')}
- Email: {personal.get('email', 'N/A')}
- Telefone: {personal.get('phone', 'N/A')}

DADOS DE EMPREGO:
- Cargo: {employment.get('job_title', 'N/A')}
- Empresa: {employment.get('company', 'N/A')}
- Salário: {employment.get('salary', 'N/A')}
- Experiência: {employment.get('years_experience', 'N/A')} anos

ANÁLISE SOLICITADA:
Identifique possíveis sinais de fraude e forneça um score de 0.0 a 1.0.
Considere: inconsistências, dados irreais, padrões suspeitos.
Responda em JSON: {{"fraud_risk_score": 0.0, "evidence": [], "confidence": 0.0}}
"""
        
        return prompt
    
    async def _find_similar_cases(self, case_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Encontra casos similares que podem indicar duplicação
        """
        try:
            form_data = case_data.get("form_data", {})
            personal_info = form_data.get("personal_info", {})
            
            if not personal_info:
                return []
            
            # Buscar casos com dados similares
            similar_filters = []
            
            if personal_info.get("full_name"):
                similar_filters.append({"personal_info.full_name": personal_info["full_name"]})
            
            if personal_info.get("email"):
                similar_filters.append({"personal_info.email": personal_info["email"]})
            
            if personal_info.get("phone"):
                similar_filters.append({"personal_info.phone": personal_info["phone"]})
            
            if not similar_filters:
                return []
            
            # Buscar casos similares (excluindo o caso atual)
            current_case_id = case_data.get("case", {}).get("case_id", "")
            
            similar_cases = []
            for filter_criteria in similar_filters:
                filter_criteria["case_id"] = {"$ne": current_case_id}
                cases = await self.db.friendly_forms.find(filter_criteria).to_list(10)  # Máximo 10
                similar_cases.extend(cases)
            
            # Remover duplicatas
            unique_cases = {}
            for case in similar_cases:
                case_id = case.get("case_id")
                if case_id and case_id not in unique_cases:
                    unique_cases[case_id] = case
            
            return list(unique_cases.values())
            
        except Exception as e:
            logger.error(f"Error finding similar cases: {e}")
            return []
    
    def _calculate_risk_level(self, overall_score: float) -> str:
        """
        Calcula nível de risco baseado no score
        """
        if overall_score >= self.risk_thresholds["critical"]:
            return "critical"
        elif overall_score >= self.risk_thresholds["high"]:
            return "high"
        elif overall_score >= self.risk_thresholds["medium"]:
            return "medium"
        else:
            return "low"
    
    def _generate_fraud_recommendations(self, risk_factors: Dict[str, float], risk_level: str) -> List[str]:
        """
        Gera recomendações baseadas nos fatores de risco
        """
        recommendations = []
        
        # Recomendações baseadas em fatores específicos
        if risk_factors.get("document_risk", 0) > 0.5:
            recommendations.append("🔍 Revisar manualmente documentos com baixa confiança")
            recommendations.append("📋 Solicitar documentos adicionais para verificação")
        
        if risk_factors.get("personal_data_risk", 0) > 0.5:
            recommendations.append("☎️ Verificar dados pessoais por telefone")
            recommendations.append("📧 Confirmar informações via email oficial")
        
        if risk_factors.get("behavioral_risk", 0) > 0.5:
            recommendations.append("⏱️ Analisar padrões de preenchimento suspeitos")
            recommendations.append("🤖 Verificar se não é automação/bot")
        
        if risk_factors.get("pattern_risk", 0) > 0.5:
            recommendations.append("🔄 Comparar com casos similares históricos")
            recommendations.append("🚩 Investigar possível padrão de fraude organizada")
        
        # Recomendações baseadas no nível de risco
        if risk_level == "critical":
            recommendations.extend([
                "🚨 AÇÃO IMEDIATA: Suspender processamento do caso",
                "👮‍♂️ Escalar para equipe de investigação especializada",
                "📞 Contato direto com o cliente para verificação"
            ])
        elif risk_level == "high":
            recommendations.extend([
                "⚠️ Revisão manual obrigatória antes de prosseguir",
                "📋 Solicitar documentação adicional",
                "🔍 Verificação em múltiplas fontes"
            ])
        elif risk_level == "medium":
            recommendations.extend([
                "👀 Revisão recomendada por supervisor",
                "✅ Verificação adicional de dados principais"
            ])
        
        return recommendations[:8]  # Máximo 8 recomendações
    
    async def _create_fraud_alert(self, case_id: str, risk_factors: Dict[str, float], score: float):
        """
        Cria alerta de fraude para casos de alto risco
        """
        try:
            # Determinar tipo de fraude mais provável
            max_risk_factor = max(risk_factors.items(), key=lambda x: x[1])
            fraud_type = max_risk_factor[0].replace("_risk", "")
            
            # Gerar evidências
            evidence = []
            for factor, risk in risk_factors.items():
                if risk > 0.3:
                    evidence.append(f"{factor}: {risk:.2f}")
            
            alert = FraudAlert(
                alert_id=str(uuid.uuid4()),
                case_id=case_id,
                user_id=None,  # Seria preenchido com dados do usuário
                fraud_type=fraud_type,
                severity="high" if score >= 0.7 else "medium",
                confidence_score=score,
                evidence=evidence,
                timestamp=datetime.now(timezone.utc)
            )
            
            self.fraud_alerts.append(alert)
            
            # Salvar no banco
            await self.db.fraud_alerts.insert_one(alert.__dict__)
            
            logger.warning(f"🚨 FRAUD ALERT created for case {case_id}: {fraud_type} (score: {score:.2f})")
            
        except Exception as e:
            logger.error(f"Error creating fraud alert: {e}")
    
    async def _save_risk_score(self, risk_score: RiskScore):
        """
        Salva score de risco no banco
        """
        try:
            await self.db.fraud_risk_scores.replace_one(
                {"case_id": risk_score.case_id},
                risk_score.__dict__,
                upsert=True
            )
        except Exception as e:
            logger.error(f"Error saving risk score: {e}")
    
    async def _monitor_fraud_patterns(self):
        """
        Monitora padrões de fraude em background
        """
        while True:
            try:
                # Analisar casos recentes para novos padrões
                recent_cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
                
                # Buscar casos com scores de risco alto
                high_risk_cases = await self.db.fraud_risk_scores.find({
                    "calculated_at": {"$gte": recent_cutoff},
                    "risk_level": {"$in": ["high", "critical"]}
                }).to_list(None)
                
                # Identificar padrões emergentes
                if len(high_risk_cases) > 5:
                    logger.info(f"🔍 Analyzing {len(high_risk_cases)} high-risk cases for new patterns")
                    await self._identify_new_fraud_patterns(high_risk_cases)
                
                await asyncio.sleep(3600)  # Análise a cada hora
                
            except Exception as e:
                logger.error(f"Error in fraud pattern monitoring: {e}")
                await asyncio.sleep(3600)
    
    async def _identify_new_fraud_patterns(self, high_risk_cases: List[Dict]):
        """
        Identifica novos padrões de fraude emergentes
        """
        try:
            # Analisar fatores de risco comuns
            common_factors = defaultdict(list)
            
            for case in high_risk_cases:
                risk_factors = case.get("risk_factors", {})
                for factor, score in risk_factors.items():
                    if score > 0.5:
                        common_factors[factor].append(score)
            
            # Identificar padrões com frequência alta
            for factor, scores in common_factors.items():
                if len(scores) >= 3:  # Aparece em pelo menos 3 casos
                    avg_score = statistics.mean(scores)
                    logger.warning(f"🔍 New fraud pattern detected: {factor} (avg score: {avg_score:.2f}, frequency: {len(scores)})")
            
        except Exception as e:
            logger.error(f"Error identifying new fraud patterns: {e}")
    
    # ===========================================
    # PUBLIC METHODS
    # ===========================================
    
    async def get_fraud_statistics(self) -> Dict[str, Any]:
        """
        Obtém estatísticas de fraude do sistema
        """
        try:
            # Contar alertas por severidade
            alerts_by_severity = defaultdict(int)
            for alert in self.fraud_alerts:
                alerts_by_severity[alert.severity] += 1
            
            # Casos analisados recentemente
            recent_cutoff = datetime.now(timezone.utc) - timedelta(days=7)
            recent_analyses = await self.db.fraud_risk_scores.count_documents({
                "calculated_at": {"$gte": recent_cutoff}
            })
            
            # Distribuição de níveis de risco
            risk_distribution = await self.db.fraud_risk_scores.aggregate([
                {"$match": {"calculated_at": {"$gte": recent_cutoff}}},
                {"$group": {"_id": "$risk_level", "count": {"$sum": 1}}}
            ]).to_list(None)
            
            risk_dist_dict = {item["_id"]: item["count"] for item in risk_distribution}
            
            # Padrões mais detectados
            pattern_stats = {
                pattern_id: {
                    "name": pattern.pattern_name,
                    "detection_count": pattern.detection_count,
                    "false_positive_rate": pattern.false_positive_rate,
                    "last_detected": pattern.last_detected.isoformat() if pattern.last_detected else None
                }
                for pattern_id, pattern in self.fraud_patterns.items()
            }
            
            return {
                "total_alerts": len(self.fraud_alerts),
                "alerts_by_severity": dict(alerts_by_severity),
                "recent_analyses": recent_analyses,
                "risk_level_distribution": risk_dist_dict,
                "fraud_patterns": pattern_stats,
                "system_status": "operational",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting fraud statistics: {e}")
            return {"error": str(e)}
    
    async def get_case_risk_score(self, case_id: str) -> Optional[RiskScore]:
        """
        Obtém score de risco de um caso
        """
        try:
            risk_data = await self.db.fraud_risk_scores.find_one({"case_id": case_id})
            
            if risk_data:
                return RiskScore(
                    case_id=risk_data["case_id"],
                    overall_score=risk_data["overall_score"],
                    risk_factors=risk_data["risk_factors"],
                    risk_level=risk_data["risk_level"],
                    recommendations=risk_data["recommendations"],
                    calculated_at=risk_data["calculated_at"]
                )
            return None
            
        except Exception as e:
            logger.error(f"Error getting risk score for case {case_id}: {e}")
            return None
    
    async def update_alert_status(self, alert_id: str, status: str, investigator: str = None, notes: str = None) -> bool:
        """
        Atualiza status de um alerta de fraude
        """
        try:
            # Atualizar em memória
            for alert in self.fraud_alerts:
                if alert.alert_id == alert_id:
                    alert.status = status
                    alert.investigator = investigator
                    alert.resolution_notes = notes
                    break
            
            # Atualizar no banco
            update_data = {"status": status}
            if investigator:
                update_data["investigator"] = investigator
            if notes:
                update_data["resolution_notes"] = notes
            
            result = await self.db.fraud_alerts.update_one(
                {"alert_id": alert_id},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating alert status: {e}")
            return False

# Instância global
fraud_detection_system: Optional[FraudDetectionAI] = None