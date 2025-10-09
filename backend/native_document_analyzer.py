"""
Native Document Analyzer
Sistema de análise de documentos usando capacidade nativa do LLM
Substitui a integração complexa do Google Document AI
"""

import logging
import base64
import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timezone
import re

logger = logging.getLogger(__name__)

@dataclass
class NativeAnalysisResult:
    """Resultado da análise nativa de documento"""
    document_type: str
    confidence: float
    extracted_fields: Dict[str, Any]
    full_text: str
    validation_issues: List[str]
    is_valid: bool
    expiry_status: str
    name_match_status: str
    type_match_status: str

class NativeDocumentAnalyzer:
    """
    Analisador de documentos usando capacidade nativa do LLM
    Funciona com documentos brasileiros e internacionais
    """
    
    def __init__(self):
        self.supported_types = [
            'passport', 'driver_license', 'birth_certificate', 
            'marriage_certificate', 'diploma', 'transcript', 
            'employment_letter', 'tax_return', 'i94', 'i797'
        ]
        
    async def analyze_document(
        self, 
        file_content: bytes, 
        expected_type: str, 
        applicant_name: str = "",
        case_id: str = ""
    ) -> NativeAnalysisResult:
        """
        Analisa documento usando capacidade nativa
        
        Args:
            file_content: Conteúdo do arquivo em bytes
            expected_type: Tipo de documento esperado
            applicant_name: Nome do requerente para verificação
            case_id: ID do caso para contexto
            
        Returns:
            NativeAnalysisResult com análise completa
        """
        try:
            logger.info(f"🔍 Iniciando análise nativa para documento tipo: {expected_type}")
            
            # Converter arquivo para base64 para análise
            file_base64 = base64.b64encode(file_content).decode('utf-8')
            
            # Análise do documento usando capacidade nativa REAL do LLM
            analysis_prompt = self._create_analysis_prompt(expected_type, applicant_name)
            
            # RESTORED: Chamada real para o modelo LLM nativo (não simulação)
            result = await self._perform_real_llm_analysis(file_content, expected_type, applicant_name, analysis_prompt)
            
            logger.info(f"✅ Análise nativa concluída: {result.document_type} (confiança: {result.confidence})")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro na análise nativa: {str(e)}")
            return NativeAnalysisResult(
                document_type=expected_type,
                confidence=0.0,
                extracted_fields={},
                full_text="Erro na análise",
                validation_issues=[f"❌ ERRO INTERNO: {str(e)}"],
                is_valid=False,
                expiry_status="unknown",
                name_match_status="error",
                type_match_status="error"
            )
    
    def _create_analysis_prompt(self, expected_type: str, applicant_name: str) -> str:
        """Cria prompt para análise do documento"""
        return f"""
        Analise este documento e forneça:
        
        1. TIPO DE DOCUMENTO: Identifique se é {expected_type} ou outro tipo
        2. VALIDADE: Verifique se o documento está vencido
        3. NOME: Se o nome no documento corresponde a "{applicant_name}"
        4. LEGIBILIDADE: Se o documento está claro e legível
        5. DADOS EXTRAÍDOS: Extraia informações chave do documento
        
        Responda em português brasileiro com foco em documentos de imigração.
        """
    
    async def _perform_real_llm_analysis(
        self, 
        file_content: bytes, 
        expected_type: str, 
        applicant_name: str,
        analysis_prompt: str
    ) -> NativeAnalysisResult:
        """
        RESTORED: Análise REAL usando LLM nativo (não simulação)
        Sistema original que funcionava com precisão
        """
        
        try:
            # Import OpenAI directly (NO EMERGENT DEPENDENCIES)
            import openai
            import base64
            
            # Convert bytes to base64 for OpenAI Vision analysis
            file_base64 = base64.b64encode(file_content).decode('utf-8')
            
            # Create OpenAI client using ONLY user's personal API key
            openai_api_key = os.getenv('OPENAI_API_KEY')
            if not openai_api_key:
                raise ValueError("OPENAI_API_KEY is required for native analysis")
            
            client = openai.OpenAI(api_key=openai_api_key)
            
            logger.info(f"🤖 Executando análise OpenAI REAL nativa para {expected_type} usando sua chave pessoal")
            
            # Create system message
            system_message = f"""Você é um especialista em análise de documentos de imigração brasileiros e internacionais.
                
TAREFA: Analise o documento enviado e extraia informações precisas.

TIPO ESPERADO: {expected_type}
NOME DO APLICANTE: {applicant_name}

Forneça análise detalhada em português brasileiro com dados REAIS extraídos do documento."""
            
            # Send image to OpenAI Vision API directly
            response = client.chat.completions.create(
                model="gpt-4o",  # gpt-4o has vision capabilities
                messages=[
                    {
                        "role": "system", 
                        "content": system_message
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": analysis_prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{file_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            # Get LLM response
            llm_response = response.choices[0].message.content
            
            logger.info(f"✅ Análise OpenAI nativa concluída - resposta: {len(llm_response)} chars")
            
            # Parse LLM response into structured result
            result = self._parse_llm_response(llm_response, expected_type, applicant_name, file_content)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro na análise LLM nativa: {str(e)}")
            # Fallback to basic analysis if LLM fails
            return self._create_fallback_analysis(file_content, expected_type, applicant_name, str(e))
    
    def _parse_llm_response(
        self,
        llm_response: str,
        expected_type: str,
        applicant_name: str,
        file_content: bytes
    ) -> NativeAnalysisResult:
        """
        Parse da resposta do LLM em resultado estruturado
        """
        validation_issues = []
        
        # Extract information from LLM response
        detected_type = self._extract_document_type_from_llm(llm_response)
        confidence = self._extract_confidence_from_llm(llm_response)
        extracted_fields = self._extract_fields_from_llm(llm_response)
        
        # Check type match
        if detected_type != expected_type:
            validation_issues.append(f"❌ TIPO DE DOCUMENTO INCORRETO: Detectado '{self._get_document_name(detected_type)}' mas esperado '{self._get_document_name(expected_type)}'")
        
        # Check for issues mentioned in LLM response
        if any(word in llm_response.lower() for word in ['vencido', 'expirado', 'expired']):
            validation_issues.append("❌ DOCUMENTO VENCIDO: Documento fora da validade")
        
        if any(word in llm_response.lower() for word in ['ilegível', 'borrado', 'danificado']):
            validation_issues.append("❌ QUALIDADE COMPROMETIDA: Documento com problemas de legibilidade")
        
        # Determine validity
        is_valid = len(validation_issues) == 0 and detected_type == expected_type
        
        # Create structured result
        return NativeAnalysisResult(
            document_type=detected_type,
            confidence=confidence,
            extracted_fields=extracted_fields,
            full_text=llm_response,
            validation_issues=validation_issues,
            is_valid=is_valid,
            expiry_status="valid" if is_valid else "invalid",
            name_match_status=self._check_name_match_from_llm(llm_response, applicant_name),
            type_match_status="match" if detected_type == expected_type else "mismatch"
        )
    
    def _extract_document_type_from_llm(self, response: str) -> str:
        """Extrai tipo de documento da resposta do LLM"""
        response_lower = response.lower()
        
        if any(word in response_lower for word in ['passaporte', 'passport']):
            return 'passport'
        elif any(word in response_lower for word in ['cnh', 'carteira nacional', 'habilitação', 'motorista']):
            return 'driver_license'
        elif any(word in response_lower for word in ['certidão de nascimento', 'birth certificate']):
            return 'birth_certificate'
        elif any(word in response_lower for word in ['casamento', 'marriage']):
            return 'marriage_certificate'
        else:
            return 'unknown'
    
    def _extract_confidence_from_llm(self, response: str) -> float:
        """Extrai nível de confiança da resposta do LLM"""
        response_lower = response.lower()
        
        if any(word in response_lower for word in ['muito claro', 'excelente', 'perfeito']):
            return 0.95
        elif any(word in response_lower for word in ['claro', 'boa qualidade', 'legível']):
            return 0.85
        elif any(word in response_lower for word in ['aceitável', 'regular']):
            return 0.75
        else:
            return 0.80
    
    def _extract_fields_from_llm(self, response: str) -> Dict[str, str]:
        """Extrai campos estruturados da resposta do LLM"""
        fields = {}
        
        # Use regex to extract common fields
        import re
        
        patterns = {
            'full_name': [r'nome[:\s]*([^\n,]+)', r'name[:\s]*([^\n,]+)'],
            'document_number': [r'número[:\s]*([A-Z0-9\-\s]+)', r'number[:\s]*([A-Z0-9\-\s]+)'],
            'date_of_birth': [r'nascimento[:\s]*([0-9\/\-\.]+)', r'birth[:\s]*([0-9\/\-\.]+)'],
            'issue_date': [r'emissão[:\s]*([0-9\/\-\.]+)', r'issue[:\s]*([0-9\/\-\.]+)'],
            'expiry_date': [r'validade[:\s]*([0-9\/\-\.]+)', r'expir[:\s]*([0-9\/\-\.]+)'],
        }
        
        for field, regex_list in patterns.items():
            for pattern in regex_list:
                match = re.search(pattern, response, re.IGNORECASE)
                if match:
                    fields[field] = match.group(1).strip()
                    break
        
        return fields
    
    def _check_name_match_from_llm(self, response: str, applicant_name: str) -> str:
        """Verifica correspondência de nome baseado na resposta do LLM"""
        if not applicant_name:
            return "no_applicant_name"
        
        response_lower = response.lower()
        applicant_lower = applicant_name.lower()
        
        # Check if LLM mentions name match/mismatch
        if 'corresponde' in response_lower or 'match' in response_lower:
            return "match"
        elif 'não corresponde' in response_lower or 'não match' in response_lower:
            return "mismatch"
        elif applicant_lower in response_lower:
            return "likely_match"
        else:
            return "cannot_verify"
    
    def _create_fallback_analysis(
        self, 
        file_content: bytes, 
        expected_type: str, 
        applicant_name: str,
        error_message: str
    ) -> NativeAnalysisResult:
        """
        Análise de fallback quando LLM real falha
        """
        validation_issues = [f"⚠️ ANÁLISE LIMITADA: {error_message}"]
        
        # Basic file size analysis
        file_size = len(file_content)
        
        return NativeAnalysisResult(
            document_type=expected_type,
            confidence=0.60,
            extracted_fields={
                "file_size": file_size,
                "analysis_method": "fallback_native",
                "error": error_message,
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            full_text=f"Análise de fallback devido a erro: {error_message}",
            validation_issues=validation_issues,
            is_valid=False,
            expiry_status="unknown",
            name_match_status="error",
            type_match_status="error"
        )
    
    def _detect_document_type(self, file_content: bytes, expected_type: str) -> str:
        """
        Detecta o tipo de documento baseado em características do arquivo
        Em produção, usaria análise de imagem real
        """
        file_size = len(file_content)
        
        # Simulação de detecção baseada em tamanho e padrões
        # Em produção, usaria análise de imagem com AI
        
        if expected_type == 'passport':
            # Se o arquivo for muito diferente do esperado para passaporte,
            # simula detecção de outros tipos comuns
            if file_size < 200000:  # Muito pequeno para passaporte
                return 'driver_license'  # Provavelmente CNH
            elif file_size > 4000000:  # Muito grande
                return 'birth_certificate'  # Provavelmente certidão
                
        elif expected_type == 'driver_license':
            if file_size > 2500000:  # Muito grande para CNH
                return 'passport'  # Provavelmente passaporte
                
        # Por padrão, retorna o tipo esperado se não detectar problema óbvio
        return expected_type
    
    def _get_document_name(self, doc_type: str) -> str:
        """Converte código do documento para nome em português"""
        names = {
            'passport': 'Passaporte',
            'driver_license': 'Carteira de Motorista/CNH', 
            'birth_certificate': 'Certidão de Nascimento',
            'marriage_certificate': 'Certidão de Casamento',
            'diploma': 'Diploma',
            'transcript': 'Histórico Escolar',
            'employment_letter': 'Carta de Trabalho',
            'tax_return': 'Declaração de Imposto de Renda',
            'i94': 'Formulário I-94',
            'i797': 'Formulário I-797'
        }
        return names.get(doc_type, doc_type.title())


# Função helper para integração fácil
async def analyze_document_native(
    file_content: bytes,
    document_type: str,
    applicant_name: str = "",
    case_id: str = ""
) -> Dict[str, Any]:
    """
    Função helper para análise de documento nativa
    Retorna resultado no formato esperado pelo endpoint
    """
    
    analyzer = NativeDocumentAnalyzer()
    result = await analyzer.analyze_document(
        file_content=file_content,
        expected_type=document_type,
        applicant_name=applicant_name,
        case_id=case_id
    )
    
    # Converter para formato esperado pelo endpoint
    return {
        "valid": result.is_valid,
        "legible": True,  # Assume legível se conseguiu analisar
        "completeness": 85 if result.is_valid else 30,
        "issues": result.validation_issues,
        "extracted_data": {
            **result.extracted_fields,
            "detected_type": result.document_type,
            "confidence": result.confidence,
            "analysis_method": "native_llm"
        },
        "dra_paula_assessment": _generate_assessment(result)
    }


def _generate_assessment(result: NativeAnalysisResult) -> str:
    """Gera avaliação da Dra. Paula baseada no resultado"""
    
    # Casos específicos de erro de tipo de documento
    if result.type_match_status == "mismatch":
        expected_name = NativeDocumentAnalyzer()._get_document_name(result.extracted_fields.get('expected_type', ''))
        detected_name = NativeDocumentAnalyzer()._get_document_name(result.document_type)
        return f"🚨 TIPO DE DOCUMENTO INCORRETO: Você enviou um(a) {detected_name}, mas é necessário um(a) {expected_name}. Por favor, carregue o documento correto."
    
    # Outros problemas de validação
    if not result.is_valid:
        main_issues = []
        for issue in result.validation_issues:
            if "TIPO DE DOCUMENTO INCORRETO" in issue:
                continue  # Já tratado acima
            main_issues.append(issue)
        
        if main_issues:
            return f"❌ DOCUMENTO COM PROBLEMAS: {'; '.join(main_issues)}. Verifique o arquivo e tente novamente."
    
    # Documento válido com boa confiança
    if result.confidence > 0.8:
        doc_name = NativeDocumentAnalyzer()._get_document_name(result.document_type)
        return f"✅ DOCUMENTO APROVADO: {doc_name} válido e em ordem (confiança: {result.confidence:.0%})"
    
    # Documento com ressalvas
    elif result.confidence > 0.5:
        doc_name = NativeDocumentAnalyzer()._get_document_name(result.document_type)
        return f"⚠️ DOCUMENTO COM RESSALVAS: {doc_name} parcialmente válido (confiança: {result.confidence:.0%}). Recomendo verificar qualidade da imagem."
    
    # Baixa confiança
    else:
        return f"❌ DOCUMENTO REJEITADO: Não foi possível validar adequadamente (confiança: {result.confidence:.0%}). Verifique se o arquivo está legível e no formato correto."