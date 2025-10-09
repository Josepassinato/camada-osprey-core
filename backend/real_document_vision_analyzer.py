"""
Real Document Vision Analyzer
Sistema REAL de análise de documentos usando OpenAI Vision API
Substitui o sistema de simulação por análise real de imagens
"""

import logging
import base64
import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timezone
import re
from dotenv import load_dotenv

load_dotenv()

# Import emergentintegrations for real LLM analysis
try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent
    EMERGENT_AVAILABLE = True
except ImportError:
    EMERGENT_AVAILABLE = False
    logging.warning("emergentintegrations not available - falling back to simulation")

logger = logging.getLogger(__name__)

@dataclass
class RealDocumentAnalysisResult:
    """Resultado da análise real de documento"""
    document_type: str
    confidence: float
    extracted_fields: Dict[str, Any]
    full_text_content: str
    validation_issues: List[str]
    is_valid: bool
    quality_assessment: Dict[str, Any]
    security_features: List[str]

class RealDocumentVisionAnalyzer:
    """
    Analisador REAL de documentos usando OpenAI Vision API
    Substitui completamente o sistema de simulação
    """
    
    def __init__(self):
        self.supported_types = [
            'passport', 'driver_license', 'birth_certificate', 
            'marriage_certificate', 'diploma', 'transcript',
            'employment_letter', 'tax_return', 'i94', 'i797',
            'i20', 'social_security_card', 'medical_exam',
            'police_clearance', 'bank_statement', 'pay_stub'
        ]
        
        # Get API key - use user's OPENAI_API_KEY directly (has no budget limits)
        self.api_key = os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            logger.error("No API key found for document analysis")
            raise ValueError("EMERGENT_LLM_KEY or OPENAI_API_KEY is required")
        
        logger.info(f"🔧 Real Document Vision Analyzer initialized with {'EMERGENT_LLM_KEY' if os.getenv('EMERGENT_LLM_KEY') else 'OPENAI_API_KEY'}")
    
    async def analyze_document_with_real_vision(
        self,
        image_data: bytes,
        document_type: str,
        applicant_name: str,
        visa_type: str,
        case_id: str
    ) -> Dict[str, Any]:
        """
        Análise REAL de documento usando OpenAI Vision API
        Substitui completamente a simulação anterior
        """
        try:
            logger.info(f"🔍 Starting REAL vision analysis for document type: {document_type}")
            
            if not EMERGENT_AVAILABLE:
                logger.error("emergentintegrations not available - cannot perform real analysis")
                return await self._fallback_analysis(image_data, document_type, applicant_name)
            
            # Convert bytes to base64 for OpenAI Vision API
            if isinstance(image_data, bytes):
                image_base64 = base64.b64encode(image_data).decode('utf-8')
            elif isinstance(image_data, str):
                image_base64 = image_data
            else:
                logger.error(f"Invalid image_data type: {type(image_data)}")
                return await self._fallback_analysis(b"", document_type, applicant_name)
            
            # Create LLM chat instance for vision analysis
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"doc_analysis_{case_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                system_message=self._get_analysis_system_prompt(document_type, visa_type)
            ).with_model("openai", "gpt-4o")  # gpt-4o has vision capabilities
            
            # Create image content for analysis
            image_content = ImageContent(image_base64=image_base64)
            
            # Create analysis prompt
            analysis_prompt = self._create_analysis_prompt(document_type, applicant_name, visa_type)
            
            # Send message with image for analysis
            user_message = UserMessage(
                text=analysis_prompt,
                file_contents=[image_content]
            )
            
            logger.info("🤖 Sending image to OpenAI Vision API for real analysis...")
            
            # Get real analysis from OpenAI Vision
            response = await chat.send_message(user_message)
            
            logger.info(f"✅ Real vision analysis completed - response length: {len(response)}")
            
            # Parse the AI response into structured data
            analysis_result = await self._parse_vision_response(response, document_type, image_base64)
            
            logger.info(f"📊 Parsed analysis result - detected type: {analysis_result.get('detected_type', 'unknown')}")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"❌ Real vision analysis failed: {str(e)}")
            # Return fallback analysis on error
            return await self._fallback_analysis(image_data, document_type, applicant_name)
    
    def _get_analysis_system_prompt(self, document_type: str, visa_type: str) -> str:
        """Sistema prompt para análise de documentos"""
        return f"""Você é um especialista em análise de documentos de imigração brasileiros e internacionais.

TAREFA CRÍTICA: Analyze a imagem de documento enviada e extraia TODAS as informações visíveis de forma precisa.

TIPO DE DOCUMENTO ESPERADO: {document_type}
TIPO DE VISTO: {visa_type}

INSTRUÇÕES:
1. Examine a imagem cuidadosamente
2. Identifique o tipo real do documento na imagem
3. Extraia TODOS os textos, números, datas visíveis
4. Determine se o documento corresponde ao tipo esperado
5. Avalie a qualidade e autenticidade do documento
6. Identifique elementos de segurança visíveis

RESPONDA EM PORTUGUÊS BRASILEIRO com análise detalhada e precisa baseada na imagem real."""
    
    def _create_analysis_prompt(self, document_type: str, applicant_name: str, visa_type: str) -> str:
        """Cria prompt específico para análise do documento"""
        return f"""Analise esta imagem de documento cuidadosamente e forneça uma análise completa:

ANÁLISE SOLICITADA:
1. **Tipo de Documento**: Qual tipo de documento está na imagem? (passaporte, CNH, certidão, etc.)
2. **Correspondência de Tipo**: Este documento corresponde ao tipo esperado "{document_type}"?
3. **Extração de Texto**: Extraia TODOS os textos visíveis no documento
4. **Campos Específicos**: Identifique e extraia:
   - Nome completo
   - Número do documento  
   - Data de nascimento
   - Data de emissão
   - Data de validade/expiração
   - Nacionalidade
   - Local de nascimento
   - Qualquer outro campo relevante

5. **Validação**: 
   - O documento parece autêntico?
   - Está em boa qualidade?
   - Está vencido?
   - Há elementos de segurança visíveis?

6. **Correspondência de Nome**: O nome no documento corresponde a "{applicant_name}"?

FORMATO DE RESPOSTA:
Forneça a análise em formato estruturado, sendo específico sobre o que você vê na imagem real.
Seja preciso - extraia apenas informações que você pode ver claramente na imagem.
"""
    
    async def _parse_vision_response(self, response: str, expected_type: str, image_base64: str) -> Dict[str, Any]:
        """Parse da resposta da análise visual em dados estruturados"""
        try:
            logger.info("🔍 Parsing vision analysis response...")
            
            # Create structured analysis result from AI response
            analysis_result = {
                "detected_type": self._extract_detected_type(response),
                "confidence": self._extract_confidence(response),
                "text_content": response,  # Full AI analysis
                "extracted_fields": self._extract_fields(response),
                "quality_score": self._extract_quality_score(response),
                "security_features": self._extract_security_features(response),
                "issues_found": self._extract_issues(response, expected_type),
                "valid": self._determine_validity(response, expected_type),
                "legible": True,  # If AI could analyze it, it's legible
                "completeness": self._calculate_completeness(response),
                "analysis_method": "real_vision_openai",
                "full_text_extracted": response,
                "dra_paula_assessment": self._create_assessment(response, expected_type)
            }
            
            logger.info(f"✅ Vision response parsed - type: {analysis_result['detected_type']}, confidence: {analysis_result['confidence']}")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"❌ Error parsing vision response: {str(e)}")
            return await self._create_error_result(expected_type)
    
    def _extract_detected_type(self, response: str) -> str:
        """Extrai o tipo de documento detectado da resposta"""
        response_lower = response.lower()
        
        # Map common document types
        if any(word in response_lower for word in ['passaporte', 'passport', 'república federativa']):
            return 'passport'
        elif any(word in response_lower for word in ['cnh', 'carteira nacional', 'habilitação', 'detran', 'motorista']):
            return 'driver_license' 
        elif any(word in response_lower for word in ['certidão de nascimento', 'birth certificate', 'nascimento']):
            return 'birth_certificate'
        elif any(word in response_lower for word in ['i-797', 'uscis', 'approval notice']):
            return 'i797'
        elif any(word in response_lower for word in ['social security', 'seguro social']):
            return 'social_security_card'
        else:
            return 'unknown'
    
    def _extract_confidence(self, response: str) -> float:
        """Extrai nível de confiança baseado na análise"""
        response_lower = response.lower()
        
        # High confidence indicators
        if any(word in response_lower for word in ['claro', 'nítido', 'bem definido', 'legível']):
            return 0.95
        elif any(word in response_lower for word in ['boa qualidade', 'autêntico', 'completo']):
            return 0.90
        elif any(word in response_lower for word in ['visível', 'identificável']):
            return 0.85
        else:
            return 0.80
    
    def _extract_fields(self, response: str) -> Dict[str, str]:
        """Extrai campos específicos da análise"""
        fields = {}
        
        # Extract common fields using regex patterns
        patterns = {
            'full_name': [r'nome[:\s]*([^\n,]+)', r'name[:\s]*([^\n,]+)'],
            'document_number': [r'número[:\s]*([A-Z0-9\-\s]+)', r'number[:\s]*([A-Z0-9\-\s]+)'],
            'date_of_birth': [r'nascimento[:\s]*([0-9\/\-\.]+)', r'birth[:\s]*([0-9\/\-\.]+)'],
            'issue_date': [r'emissão[:\s]*([0-9\/\-\.]+)', r'issue[:\s]*([0-9\/\-\.]+)'],
            'expiry_date': [r'validade[:\s]*([0-9\/\-\.]+)', r'expir[:\s]*([0-9\/\-\.]+)'],
            'nationality': [r'nacionalidade[:\s]*([^\n,]+)', r'nationality[:\s]*([^\n,]+)']
        }
        
        for field, regex_list in patterns.items():
            for pattern in regex_list:
                match = re.search(pattern, response, re.IGNORECASE)
                if match:
                    fields[field] = match.group(1).strip()
                    break
        
        return fields
    
    def _extract_quality_score(self, response: str) -> float:
        """Extrai score de qualidade baseado na análise"""
        response_lower = response.lower()
        
        if any(word in response_lower for word in ['excelente', 'perfeita', 'ótima']):
            return 0.95
        elif any(word in response_lower for word in ['boa', 'clara', 'nítida']):
            return 0.85
        elif any(word in response_lower for word in ['regular', 'aceitável']):
            return 0.75
        elif any(word in response_lower for word in ['baixa', 'ruim', 'ilegível']):
            return 0.50
        else:
            return 0.80
    
    def _extract_security_features(self, response: str) -> List[str]:
        """Extrai elementos de segurança identificados"""
        features = []
        response_lower = response.lower()
        
        security_keywords = {
            'holograma': 'Holograma de segurança detectado',
            'marca d\'água': 'Marca d\'água presente',
            'mrz': 'Zona de leitura mecânica (MRZ) presente',
            'código de barras': 'Código de barras identificado',
            'foto': 'Fotografia integrada presente',
            'assinatura': 'Assinatura do portador presente'
        }
        
        for keyword, description in security_keywords.items():
            if keyword in response_lower:
                features.append(description)
        
        return features
    
    def _extract_issues(self, response: str, expected_type: str) -> List[str]:
        """Extrai problemas identificados na análise"""
        issues = []
        response_lower = response.lower()
        
        # Check for type mismatch
        detected_type = self._extract_detected_type(response)
        if detected_type != expected_type and detected_type != 'unknown':
            type_names = {
                'passport': 'Passaporte',
                'driver_license': 'CNH/Carteira de Motorista', 
                'birth_certificate': 'Certidão de Nascimento'
            }
            detected_name = type_names.get(detected_type, detected_type)
            expected_name = type_names.get(expected_type, expected_type)
            issues.append(f"❌ TIPO DE DOCUMENTO INCORRETO: Detectado {detected_name}, mas esperado {expected_name}")
        
        # Check for quality issues
        if any(word in response_lower for word in ['ilegível', 'borrado', 'danificado']):
            issues.append("❌ QUALIDADE COMPROMETIDA: Documento com problemas de legibilidade")
        
        # Check for expiration
        if any(word in response_lower for word in ['vencido', 'expirado', 'expired']):
            issues.append("❌ DOCUMENTO VENCIDO: Documento fora da validade")
        
        return issues
    
    def _determine_validity(self, response: str, expected_type: str) -> bool:
        """Determina se o documento é válido"""
        issues = self._extract_issues(response, expected_type)
        detected_type = self._extract_detected_type(response)
        
        # Invalid if wrong type or has critical issues
        if detected_type != expected_type or any('❌' in issue for issue in issues):
            return False
        
        return True
    
    def _calculate_completeness(self, response: str) -> int:
        """Calcula score de completeness baseado na análise"""
        # Count how many fields were extracted
        fields = self._extract_fields(response)
        field_count = len([v for v in fields.values() if v.strip()])
        
        # Base score on field count and quality indicators
        base_score = min(90, field_count * 15)  # Up to 90% based on fields
        
        # Bonus for quality indicators
        if 'autêntico' in response.lower():
            base_score += 5
        if 'completo' in response.lower():
            base_score += 5
        
        return min(100, base_score)
    
    def _create_assessment(self, response: str, expected_type: str) -> str:
        """Cria avaliação da Dra. Paula baseada na análise"""
        detected_type = self._extract_detected_type(response)
        is_valid = self._determine_validity(response, expected_type)
        
        if is_valid:
            return f"✅ DOCUMENTO APROVADO: {response[:200]}... (Análise completa realizada com IA de visão real)"
        else:
            issues = self._extract_issues(response, expected_type)
            main_issue = issues[0] if issues else "Documento não atende aos requisitos"
            return f"❌ DOCUMENTO REJEITADO: {main_issue}. Análise detalhada: {response[:150]}..."
    
    async def _fallback_analysis(self, image_data: bytes, document_type: str, applicant_name: str) -> Dict[str, Any]:
        """Análise de fallback quando visão real não está disponível"""
        logger.warning("🔄 Using fallback analysis - real vision not available")
        
        return {
            "detected_type": document_type,
            "confidence": 0.60,
            "text_content": f"Análise de fallback para {document_type}",
            "extracted_fields": {
                "full_name": applicant_name or "Nome não extraído",
                "document_type": document_type
            },
            "quality_score": 0.60,
            "security_features": [],
            "issues_found": ["⚠️ ANÁLISE LIMITADA: Sistema de visão real não disponível"],
            "valid": False,
            "legible": True,
            "completeness": 60,
            "analysis_method": "fallback_simulation",
            "dra_paula_assessment": "⚠️ ANÁLISE LIMITADA: Sistema realizou análise de fallback. Para análise precisa, verifique configuração do sistema de visão."
        }
    
    async def _create_error_result(self, expected_type: str) -> Dict[str, Any]:
        """Cria resultado de erro quando análise falha"""
        return {
            "detected_type": "error",
            "confidence": 0.0,
            "text_content": "Erro na análise do documento",
            "extracted_fields": {},
            "quality_score": 0.0,
            "security_features": [],
            "issues_found": ["❌ ERRO TÉCNICO: Falha na análise de visão"],
            "valid": False,
            "legible": False,
            "completeness": 0,
            "analysis_method": "error",
            "dra_paula_assessment": "❌ ERRO TÉCNICO: Falha na análise do documento. Tente enviar novamente."
        }

# Global function for easy import
async def analyze_document_with_real_vision(
    image_data: bytes,
    document_type: str, 
    applicant_name: str,
    visa_type: str,
    case_id: str
) -> Dict[str, Any]:
    """
    Função global para análise real de documentos
    Substitui a análise simulada por análise real usando OpenAI Vision
    """
    analyzer = RealDocumentVisionAnalyzer()
    return await analyzer.analyze_document_with_real_vision(
        image_data=image_data,
        document_type=document_type,
        applicant_name=applicant_name,
        visa_type=visa_type,
        case_id=case_id
    )