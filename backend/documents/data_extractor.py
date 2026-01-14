"""
Document Data Extractor and Auto-Correction System
Extrai dados de documentos oficiais e corrige automaticamente o cadastro do usuário
"""

import logging
import json
import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class DocumentDataExtractor:
    """Extrai dados estruturados de documentos oficiais"""
    
    def __init__(self):
        self.supported_documents = {
            "passport": self._extract_passport_data,
            "birth_certificate": self._extract_birth_certificate_data,
            "national_id": self._extract_national_id_data,
            "driver_license": self._extract_driver_license_data,
        }
    
    async def extract_and_validate(
        self, 
        document_text: str, 
        document_type: str,
        current_user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extrai dados do documento e compara com dados atuais do usuário
        
        Returns:
            {
                "extracted_data": {...},
                "discrepancies": [...],
                "suggested_corrections": {...},
                "confidence": 0-1,
                "should_auto_correct": bool
            }
        """
        try:
            # Verificar se o tipo de documento é suportado
            if document_type not in self.supported_documents:
                return {
                    "success": False,
                    "error": f"Document type '{document_type}' not supported for auto-extraction"
                }
            
            # Extrair dados usando a função específica
            extractor_func = self.supported_documents[document_type]
            extracted_data = extractor_func(document_text)
            
            if not extracted_data:
                return {
                    "success": False,
                    "error": "Could not extract data from document"
                }
            
            # Comparar com dados atuais
            discrepancies = self._find_discrepancies(extracted_data, current_user_data)
            
            # Decidir se deve corrigir automaticamente
            should_auto_correct = self._should_auto_correct(
                document_type, 
                discrepancies, 
                extracted_data.get("confidence", 0)
            )
            
            # Gerar sugestões de correção
            suggested_corrections = self._generate_corrections(discrepancies, extracted_data)
            
            return {
                "success": True,
                "extracted_data": extracted_data,
                "discrepancies": discrepancies,
                "suggested_corrections": suggested_corrections,
                "confidence": extracted_data.get("confidence", 0),
                "should_auto_correct": should_auto_correct,
                "document_type": document_type
            }
            
        except Exception as e:
            logger.error(f"Error in extract_and_validate: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_passport_data(self, document_text: str) -> Dict[str, Any]:
        """Extrai dados do passaporte usando padrões comuns"""
        extracted = {
            "confidence": 0.0,
            "fields": {}
        }
        
        text_upper = document_text.upper()
        
        # Padrões para passaportes brasileiros e americanos
        patterns = {
            # Nome completo - geralmente após "NAME" ou "NOME"
            # Captura até encontrar número ou outra palavra-chave
            "full_name": [
                r"NAME[:\s]+([A-ZÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑ][A-ZÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑ\s]+?)(?=\n|DATE|PASSPORT|NATIONALITY|SEX|BIRTH)",
                r"NOME[:\s]+([A-ZÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑ][A-ZÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑ\s]+?)(?=\n|DATA|PASSAPORTE|NACIONALIDADE)",
                r"SURNAME[:\s]+([A-Z\s]+?)\s+GIVEN NAMES[:\s]+([A-Z\s]+?)(?=\n|DATE|PASSPORT)",
            ],
            # Número do passaporte - formato BR: XX123456 ou US: 123456789
            "passport_number": [
                r"PASSPORT\s*(?:NO|NUMBER)\.?\s*[:\s]*([A-Z]{2}\d{6,9})",
                r"PASSAPORTE\s*(?:N[°º]|NÚMERO)\.?\s*[:\s]*([A-Z]{2}\d{6,9})",
                r"P<[A-Z]{3}([A-Z0-9]{9})",
            ],
            # Data de nascimento - formatos DD/MM/YYYY, DD MMM YYYY
            "date_of_birth": [
                r"(?:DATE OF )?BIRTH[:\s]+(\d{2}[\s/\-\.]\w{3,9}[\s/\-\.]\d{4})",
                r"DATA DE NASCIMENTO[:\s]+(\d{2}[\s/\-\.]\d{2}[\s/\-\.]\d{4})",
                r"BIRTH[:\s]+(\d{2}[\s/\-\.]\d{2}[\s/\-\.]\d{4})",
            ],
            # Nacionalidade
            "nationality": [
                r"NATIONALITY[:\s]+([A-Z]+?)(?=\n|DATE|PASSPORT|SEX)",
                r"NACIONALIDADE[:\s]+([A-Z]+?)(?=\n|DATA|PASSAPORTE)",
            ],
            # Data de emissão
            "issue_date": [
                r"(?:DATE OF )?ISSUE[:\s]+(\d{2}[\s/\-\.]\w{3,9}[\s/\-\.]\d{4})",
                r"DATA DE EMISSÃO[:\s]+(\d{2}[\s/\-\.]\d{2}[\s/\-\.]\d{4})",
            ],
            # Data de expiração
            "expiry_date": [
                r"(?:DATE OF )?EXPIRY[:\s]+(\d{2}[\s/\-\.]\w{3,9}[\s/\-\.]\d{4})",
                r"VALIDADE[:\s]+(\d{2}[\s/\-\.]\d{2}[\s/\-\.]\d{4})",
            ],
        }
        
        confidence_count = 0
        total_fields = len(patterns)
        
        for field, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, text_upper)
                if match:
                    if field == "full_name" and len(match.groups()) > 1:
                        # Combinar surname + given names
                        extracted["fields"][field] = f"{match.group(1).strip()} {match.group(2).strip()}"
                    else:
                        extracted["fields"][field] = match.group(1).strip()
                    confidence_count += 1
                    break
        
        # Calcular confiança baseado em quantos campos foram extraídos
        extracted["confidence"] = confidence_count / total_fields
        
        # Limpar e formatar nome
        if "full_name" in extracted["fields"]:
            name = extracted["fields"]["full_name"]
            # Remover caracteres especiais e espaços extras
            name = re.sub(r'\s+', ' ', name)
            # Capitalizar corretamente
            name = name.title()
            extracted["fields"]["full_name"] = name
        
        logger.info(f"📋 Passport data extracted with {extracted['confidence']:.0%} confidence")
        logger.info(f"📋 Extracted fields: {list(extracted['fields'].keys())}")
        
        return extracted
    
    def _extract_birth_certificate_data(self, document_text: str) -> Dict[str, Any]:
        """Extrai dados da certidão de nascimento"""
        extracted = {
            "confidence": 0.0,
            "fields": {}
        }
        
        text_upper = document_text.upper()
        
        patterns = {
            "full_name": [
                r"NOME[:\s]+([A-Z\s]+)",
                r"NAME[:\s]+([A-Z\s]+)",
            ],
            "date_of_birth": [
                r"NASCIDO[:\s]+EM[:\s]+(\d{2}[\s/\-\.]\d{2}[\s/\-\.]\d{4})",
                r"BORN[:\s]+ON[:\s]+(\d{2}[\s/\-\.]\d{2}[\s/\-\.]\d{4})",
            ],
            "place_of_birth": [
                r"NATURALIDADE[:\s]+([A-Z\s,\-]+)",
                r"PLACE OF BIRTH[:\s]+([A-Z\s,\-]+)",
            ],
        }
        
        confidence_count = 0
        total_fields = len(patterns)
        
        for field, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, text_upper)
                if match:
                    extracted["fields"][field] = match.group(1).strip()
                    confidence_count += 1
                    break
        
        extracted["confidence"] = confidence_count / total_fields
        
        return extracted
    
    def _extract_national_id_data(self, document_text: str) -> Dict[str, Any]:
        """Extrai dados de RG/CNH"""
        extracted = {
            "confidence": 0.0,
            "fields": {}
        }
        
        text_upper = document_text.upper()
        
        patterns = {
            "full_name": [
                r"NOME[:\s]+([A-Z\s]+)",
            ],
            "id_number": [
                r"RG[:\s]+(\d{1,2}\.?\d{3}\.?\d{3}-?[0-9X])",
                r"CPF[:\s]+(\d{3}\.?\d{3}\.?\d{3}-?\d{2})",
            ],
            "date_of_birth": [
                r"DATA DE NASCIMENTO[:\s]+(\d{2}[\s/\-\.]\d{2}[\s/\-\.]\d{4})",
            ],
        }
        
        confidence_count = 0
        total_fields = len(patterns)
        
        for field, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, text_upper)
                if match:
                    extracted["fields"][field] = match.group(1).strip()
                    confidence_count += 1
                    break
        
        extracted["confidence"] = confidence_count / total_fields
        
        return extracted
    
    def _extract_driver_license_data(self, document_text: str) -> Dict[str, Any]:
        """Extrai dados da CNH"""
        # Similar ao RG, mas com campos específicos de CNH
        return self._extract_national_id_data(document_text)
    
    def _find_discrepancies(
        self, 
        extracted_data: Dict[str, Any], 
        current_user_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Encontra discrepâncias entre dados extraídos e dados atuais"""
        discrepancies = []
        
        field_mapping = {
            "full_name": ["first_name", "last_name", "name"],
            "date_of_birth": ["date_of_birth", "birth_date"],
            "nationality": ["nationality", "country_of_birth"],
            "passport_number": ["passport_number"],
        }
        
        for extracted_field, user_fields in field_mapping.items():
            if extracted_field not in extracted_data.get("fields", {}):
                continue
            
            extracted_value = extracted_data["fields"][extracted_field]
            
            # Verificar cada possível campo do usuário
            for user_field in user_fields:
                if user_field in current_user_data:
                    current_value = current_user_data[user_field]
                    
                    # Para nome, comparar como um todo ou partes
                    if extracted_field == "full_name":
                        is_different = self._compare_names(extracted_value, current_value, current_user_data)
                    else:
                        is_different = str(extracted_value).lower() != str(current_value).lower()
                    
                    if is_different:
                        discrepancies.append({
                            "field": user_field,
                            "current_value": current_value,
                            "document_value": extracted_value,
                            "severity": "high" if extracted_field in ["full_name", "date_of_birth"] else "medium",
                            "source": "official_document"
                        })
                        break
        
        return discrepancies
    
    def _compare_names(
        self, 
        extracted_name: str, 
        current_value: str, 
        user_data: Dict[str, Any]
    ) -> bool:
        """
        Compara nomes considerando formato completo vs. separado
        
        IMPORTANTE: Retorna True se o nome do documento é MELHOR/MAIS COMPLETO
        que o nome atual, mesmo que o nome atual seja subset do documento.
        Isso permite que nomes incompletos sejam atualizados para nomes completos.
        """
        # Normalizar texto: lowercase, remover acentos, espaços duplos
        import unicodedata
        
        def normalize(text):
            if not text:
                return ""
            # Convert to string and lowercase
            text = str(text).lower().strip()
            # Remove accents using unicodedata
            text = unicodedata.normalize('NFD', text)
            text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
            # Remove extra spaces
            text = re.sub(r'\s+', ' ', text)
            return text
        
        extracted_clean = normalize(extracted_name)
        
        # Se o campo atual é o nome completo
        if current_value:
            current_clean = normalize(current_value)
            # Exato match
            if extracted_clean == current_clean:
                return False
            # Nome extraído é MAIS COMPLETO que nome atual
            # Ex: "joao silva" (atual) vs "joao silva santos" (documento)
            if current_clean in extracted_clean and len(extracted_clean) > len(current_clean):
                parts_current = current_clean.split()
                parts_extracted = extracted_clean.split()
                # Se todas as partes do nome atual estão no extraído
                if len(parts_current) > 0 and all(any(p1 in p2 or p2 in p1 for p2 in parts_extracted) for p1 in parts_current):
                    # Nome do documento é mais completo - RETORNAR TRUE para indicar diferença
                    logger.info(f"Document name is more complete: '{current_clean}' → '{extracted_clean}'")
                    return True  # É diferente e deve ser atualizado!
        
        # Se há first_name e last_name separados
        first_name = normalize(user_data.get("first_name", ""))
        last_name = normalize(user_data.get("last_name", ""))
        
        if first_name or last_name:
            # Construir nome completo atual
            full_current = f"{first_name} {last_name}".strip()
            
            # Exato match
            if extracted_clean == full_current:
                return False
            
            # Nome extraído é MAIS COMPLETO
            if full_current and full_current in extracted_clean and len(extracted_clean) > len(full_current):
                parts_current = [p for p in full_current.split() if p]
                parts_extracted = extracted_clean.split()
                
                if parts_current and all(any(p1 in p2 or p2 in p1 for p2 in parts_extracted) for p1 in parts_current):
                    # Nome do documento é mais completo - RETORNAR TRUE
                    logger.info(f"Document name is more complete: '{full_current}' → '{extracted_clean}'")
                    return True  # É diferente e deve ser atualizado!
        
        # Nomes são completamente diferentes
        return True
    
    def _should_auto_correct(
        self, 
        document_type: str, 
        discrepancies: List[Dict[str, Any]], 
        confidence: float
    ) -> bool:
        """Decide se deve corrigir automaticamente"""
        # Apenas autocorrigir para documentos oficiais com alta confiança
        official_docs = ["passport", "birth_certificate", "national_id"]
        
        if document_type not in official_docs:
            return False
        
        # Não há discrepâncias, não há nada a corrigir
        if not discrepancies:
            return False
        
        # Exigir alta confiança (>70%)
        if confidence < 0.7:
            return False
        
        # Para passaportes, permitir mais discrepâncias (até 6)
        # Para outros documentos, limite de 4
        max_discrepancies = 6 if document_type == "passport" else 4
        
        # Não autocorrigir se houver muitas discrepâncias (pode indicar documento errado)
        if len(discrepancies) > max_discrepancies:
            logger.warning(f"Too many discrepancies ({len(discrepancies)} > {max_discrepancies})")
            return False
        
        # Verificar se há discrepâncias críticas (nome, data nascimento)
        critical_discrepancies = [d for d in discrepancies if d["severity"] == "high"]
        
        # Para passaporte com alta confiança, autocorrigir mesmo com múltiplas discrepâncias
        if document_type == "passport":
            # Passaporte com confiança muito alta (>80%)
            if confidence >= 0.8:
                logger.info(f"Auto-correcting based on passport with {confidence:.0%} confidence")
                return True
            # Passaporte com confiança boa (>70%) e apenas discrepâncias críticas
            elif confidence >= 0.7 and critical_discrepancies:
                logger.info(f"Auto-correcting critical fields based on passport with {confidence:.0%} confidence")
                return True
        
        # Para certidão de nascimento, apenas com confiança muito alta
        elif document_type == "birth_certificate" and confidence >= 0.8 and critical_discrepancies:
            logger.info(f"Auto-correcting based on birth certificate with {confidence:.0%} confidence")
            return True
        
        # Para outros documentos, exigir confiança muito alta
        elif confidence >= 0.85 and critical_discrepancies:
            logger.info(f"Auto-correcting based on {document_type} with {confidence:.0%} confidence")
            return True
        
        logger.info(f"Not auto-correcting: confidence={confidence:.0%}, discrepancies={len(discrepancies)}, type={document_type}")
        return False
    
    def _generate_corrections(
        self, 
        discrepancies: List[Dict[str, Any]], 
        extracted_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Gera objeto com correções sugeridas"""
        corrections = {}
        
        for discrepancy in discrepancies:
            field = discrepancy["field"]
            new_value = discrepancy["document_value"]
            
            # Se o campo é "name" ou referente a nome completo, dividir em first_name e last_name
            if field in ["name", "applicant_name", "full_name"] and new_value:
                parts = new_value.strip().split()
                if len(parts) >= 2:
                    corrections["first_name"] = parts[0]
                    corrections["last_name"] = " ".join(parts[1:])
                elif len(parts) == 1:
                    corrections["first_name"] = parts[0]
            else:
                corrections[field] = new_value
        
        return corrections


# Função helper para uso em rotas
async def process_document_and_update_user(
    document_text: str,
    document_type: str,
    user_id: str,
    db
) -> Dict[str, Any]:
    """
    Processa documento, extrai dados e atualiza usuário se necessário
    
    Returns:
        {
            "extraction_successful": bool,
            "auto_corrected": bool,
            "corrections_made": {...},
            "discrepancies_found": [...],
            "message": str
        }
    """
    try:
        # Buscar dados atuais do usuário
        user = await db.users.find_one({"id": user_id})
        if not user:
            return {
                "extraction_successful": False,
                "error": "User not found"
            }
        
        # Extrair e validar dados
        extractor = DocumentDataExtractor()
        result = await extractor.extract_and_validate(
            document_text, 
            document_type, 
            user
        )
        
        if not result.get("success"):
            return {
                "extraction_successful": False,
                "error": result.get("error", "Extraction failed")
            }
        
        # Se não houver discrepâncias, retornar sucesso
        if not result["discrepancies"]:
            return {
                "extraction_successful": True,
                "auto_corrected": False,
                "message": "Dados do documento correspondem ao cadastro",
                "confidence": result["confidence"]
            }
        
        # Se deve autocorrigir
        if result["should_auto_correct"]:
            # Aplicar correções
            corrections = result["suggested_corrections"]
            
            # Atualizar usuário no banco
            await db.users.update_one(
                {"id": user_id},
                {
                    "$set": {
                        **corrections,
                        "data_verified_by_document": True,
                        "verification_document_type": document_type,
                        "verification_date": datetime.now(timezone.utc),
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            
            logger.info(f"✅ Auto-corrected user {user_id} data based on {document_type}")
            logger.info(f"📝 Corrections made: {corrections}")
            
            return {
                "extraction_successful": True,
                "auto_corrected": True,
                "corrections_made": corrections,
                "discrepancies_found": result["discrepancies"],
                "message": f"Cadastro atualizado automaticamente com base no {document_type}",
                "confidence": result["confidence"]
            }
        else:
            # Não autocorrigir, mas retornar sugestões
            return {
                "extraction_successful": True,
                "auto_corrected": False,
                "suggested_corrections": result["suggested_corrections"],
                "discrepancies_found": result["discrepancies"],
                "message": "Discrepâncias encontradas. Revisão manual recomendada.",
                "confidence": result["confidence"],
                "reason_not_corrected": "Confidence too low or too many discrepancies"
            }
        
    except Exception as e:
        logger.error(f"Error in process_document_and_update_user: {str(e)}")
        return {
            "extraction_successful": False,
            "error": str(e)
        }
