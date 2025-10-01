"""
Google Document AI Integration + Dr. Miguel Enhanced Validation
Professional OCR and data extraction with AI-powered fraud detection
"""

import os
import logging
import asyncio
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import base64
from google.cloud import documentai
from google.cloud import vision
from google.api_core import exceptions as google_exceptions
import requests

logger = logging.getLogger(__name__)

class GoogleDocumentAIProcessor:
    """Professional document analysis using Google Cloud Document AI"""
    
    def __init__(self):
        # Configuration from environment variables  
        self.api_key = os.environ.get('GOOGLE_API_KEY')
        self.client_id = os.environ.get('GOOGLE_CLIENT_ID')
        self.project_id = os.environ.get('GOOGLE_CLOUD_PROJECT_ID', '891629358081')
        self.location = os.environ.get('GOOGLE_DOCUMENT_AI_LOCATION', 'us')
        
        # Check if we have credentials for real mode
        self.is_mock_mode = not (self.api_key or self.client_id)
        
        if self.is_mock_mode:
            logger.warning("🧪 Google Document AI in MOCK MODE - No credentials provided")
        else:
            if self.api_key:
                logger.info(f"🔗 Google Document AI initialized with API key for project {self.project_id}")
                
                # Document AI REST endpoint
                self.document_ai_endpoint = f"https://{self.location}-documentai.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/processors/GENERAL_PROCESSOR:process"
                
                # Fallback Vision API endpoint
                self.vision_endpoint = f"https://vision.googleapis.com/v1/images:annotate?key={self.api_key}"
                
            elif self.client_id:
                logger.info(f"🔗 Google Document AI initialized with OAuth2 Client ID: {self.client_id}")
                self.document_ai_endpoint = f"https://{self.location}-documentai.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/processors/GENERAL_PROCESSOR:process"
                self.vision_endpoint = "https://vision.googleapis.com/v1/images:annotate"
            
        # Track authentication method
        self.auth_method = "api_key" if self.api_key else "oauth2" if self.client_id else "mock"
    
    def _create_mock_response(self, filename: str, content_length: int) -> Dict[str, Any]:
        """Create realistic mock response for testing"""
        mock_data = {
            "text": """
            PASSPORT
            UNITED STATES OF AMERICA
            
            Type: P
            Country Code: USA
            Passport No: 123456789
            
            Surname: SMITH
            Given Names: JOHN MICHAEL
            Nationality: UNITED STATES OF AMERICA
            Date of Birth: 15 JAN 1990
            Sex: M
            Place of Birth: NEW YORK, NY, USA
            Date of Issue: 10 MAR 2020
            Date of Expiry: 09 MAR 2030
            Authority: U.S. DEPARTMENT OF STATE
            """,
            "entities": [
                {"type": "passport_number", "value": "123456789", "confidence": 0.98},
                {"type": "surname", "value": "SMITH", "confidence": 0.99},
                {"type": "given_names", "value": "JOHN MICHAEL", "confidence": 0.99},
                {"type": "nationality", "value": "UNITED STATES OF AMERICA", "confidence": 0.99},
                {"type": "date_of_birth", "value": "15 JAN 1990", "confidence": 0.97},
                {"type": "date_of_expiry", "value": "09 MAR 2030", "confidence": 0.98},
                {"type": "sex", "value": "M", "confidence": 0.99},
                {"type": "place_of_birth", "value": "NEW YORK, NY, USA", "confidence": 0.95}
            ],
            "confidence": 0.94,
            "pages": 1,
            "processing_time_ms": 1250
        }
        
        return {
            "success": True,
            "mock_mode": True,
            "extracted_text": mock_data["text"],
            "extracted_entities": mock_data["entities"],
            "overall_confidence": mock_data["confidence"],
            "page_count": mock_data["pages"],
            "processing_time": mock_data["processing_time_ms"],
            "file_info": {
                "filename": filename,
                "size_bytes": content_length,
                "processed_at": datetime.now().isoformat()
            }
        }
    
    async def process_document(self, file_content: bytes, filename: str, 
                             mime_type: str = "application/pdf") -> Dict[str, Any]:
        """Process document with Google Document AI (with Vision API fallback)"""
        
        if self.is_mock_mode:
            # Return mock response for testing
            await asyncio.sleep(0.5)  # Simulate processing time
            return self._create_mock_response(filename, len(file_content))
        
        try:
            # First try Document AI, then fallback to Vision API
            return await self._try_document_ai(file_content, filename, mime_type)
            
        except Exception as doc_ai_error:
            logger.warning(f"⚠️ Document AI failed: {doc_ai_error}, falling back to Vision API")
            return await self._try_vision_api(file_content, filename, mime_type)
    
    async def _try_document_ai(self, file_content: bytes, filename: str, mime_type: str) -> Dict[str, Any]:
        """Try Google Document AI first (specialized for documents)"""
        
        try:
            # Convert file content to base64
            import base64
            encoded_content = base64.b64encode(file_content).decode('utf-8')
            
            # Prepare Document AI request
            request_data = {
                "rawDocument": {
                    "content": encoded_content,
                    "mimeType": mime_type
                }
            }
            
            # Make Document AI API request
            headers = {'Content-Type': 'application/json'}
            
            if self.auth_method == "api_key":
                # Use API key authentication
                doc_ai_url = f"{self.document_ai_endpoint}?key={self.api_key}"
                response = requests.post(
                    doc_ai_url,
                    json=request_data,
                    headers=headers,
                    timeout=30
                )
            else:
                # OAuth2 would need access token - fallback to Vision API
                raise Exception("OAuth2 not implemented for Document AI, using Vision API fallback")
            
            if response.status_code != 200:
                logger.error(f"❌ Document AI API error: {response.status_code} - {response.text}")
                raise Exception(f"Document AI failed: {response.status_code}")
            
            result = response.json()
            
            # Parse Document AI response
            document = result.get("document", {})
            extracted_text = document.get("text", "")
            
            # Extract entities from Document AI
            entities = self._extract_document_ai_entities(document)
            
            # Calculate confidence based on text quality and entities
            confidence = min((len(extracted_text) / 200.0) + (len(entities) * 0.1), 1.0)
            
            return {
                "success": True,
                "mock_mode": False,
                "extracted_text": extracted_text,
                "extracted_entities": entities,
                "overall_confidence": confidence,
                "page_count": len(document.get("pages", [])),
                "processing_time": None,
                "processor_type": "document_ai",
                "file_info": {
                    "filename": filename,
                    "size_bytes": len(file_content),
                    "processed_at": datetime.now().isoformat(),
                    "mime_type": mime_type
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Document AI processing error: {e}")
            raise e
    
    async def _try_vision_api(self, file_content: bytes, filename: str, mime_type: str) -> Dict[str, Any]:
        """Fallback to Google Vision API"""
        
        try:
            # Convert file content to base64
            import base64
            encoded_content = base64.b64encode(file_content).decode('utf-8')
            
            # Prepare Vision API request
            request_data = {
                "requests": [
                    {
                        "image": {
                            "content": encoded_content
                        },
                        "features": [
                            {
                                "type": "DOCUMENT_TEXT_DETECTION",
                                "maxResults": 50
                            }
                        ]
                    }
                ]
            }
            
            # Make Vision API request
            headers = {'Content-Type': 'application/json'}
            
            if self.auth_method == "api_key":
                response = requests.post(
                    self.vision_endpoint,
                    json=request_data,
                    headers=headers,
                    timeout=30
                )
            else:
                raise Exception("OAuth2 not implemented for Vision API fallback")
            
            if response.status_code != 200:
                logger.error(f"❌ Vision API error: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"Vision API failed: {response.text}",
                    "error_type": "vision_api_error"
                }
            
            result = response.json()
            
            # Parse Vision API response
            responses = result.get("responses", [{}])
            annotation = responses[0] if responses else {}
            
            # Get full text
            text_annotations = annotation.get("textAnnotations", [])
            extracted_text = text_annotations[0]["description"] if text_annotations else ""
            
            # Extract entities from text (simulate structured data extraction)
            entities = self._extract_entities_from_text(extracted_text)
            
            # Calculate confidence based on text quality
            confidence = min(len(extracted_text) / 100.0, 1.0) if extracted_text else 0.0
            
            return {
                "success": True,
                "mock_mode": False,
                "extracted_text": extracted_text,
                "extracted_entities": entities,
                "overall_confidence": confidence,
                "page_count": 1,
                "processing_time": None,
                "processor_type": "vision_api",
                "file_info": {
                    "filename": filename,
                    "size_bytes": len(file_content),
                    "processed_at": datetime.now().isoformat(),
                    "mime_type": mime_type
                }
            }
            
            if response.status_code != 200:
                logger.error(f"❌ Google Vision API error: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"API request failed: {response.text}",
                    "error_type": "api_error"
                }
            
            result = response.json()
            
            # Check for errors in response
            if "error" in result:
                logger.error(f"❌ Google Vision API error: {result['error']}")
                return {
                    "success": False,
                    "error": result["error"]["message"],
                    "error_type": "vision_api_error"
                }
            
            # Extract text and entities
            responses = result.get("responses", [{}])
            annotation = responses[0] if responses else {}
            
            # Get full text
            text_annotations = annotation.get("textAnnotations", [])
            extracted_text = text_annotations[0]["description"] if text_annotations else ""
            
            # Extract entities from text (simulate structured data extraction)
            entities = self._extract_entities_from_text(extracted_text)
            
            # Calculate confidence based on text quality
            confidence = min(len(extracted_text) / 100.0, 1.0) if extracted_text else 0.0
            
            return {
                "success": True,
                "mock_mode": False,
                "extracted_text": extracted_text,
                "extracted_entities": entities,
                "overall_confidence": confidence,
                "page_count": 1,
                "processing_time": None,
                "file_info": {
                    "filename": filename,
                    "size_bytes": len(file_content),
                    "processed_at": datetime.now().isoformat(),
                    "mime_type": mime_type
                }
            }
            
        except requests.exceptions.Timeout as e:
            logger.error(f"❌ Google Vision API timeout: {e}")
            return {
                "success": False,
                "error": "Request timeout",
                "error_type": "timeout"
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Google Vision API request error: {e}")
            return {
                "success": False,
                "error": f"Request failed: {e}",
                "error_type": "request_error"
            }
            
        except Exception as e:
                logger.error(f"❌ Vision API fallback error: {e}")
                return {
                    "success": False,
                    "error": f"Vision API processing failed: {e}",
                    "error_type": "vision_fallback_error"
                }
        
        except Exception as e:
            logger.error(f"❌ All API processing failed: {e}")
            return {
                "success": False,
                "error": f"Document processing failed: {e}",
                "error_type": "processing_error"
            }
    
    def _extract_document_ai_entities(self, document: Dict) -> List[Dict[str, Any]]:
        """Extract structured entities from Document AI response"""
        
        entities = []
        
        # Extract from Document AI entities (if available)
        doc_entities = document.get("entities", [])
        for entity in doc_entities:
            entities.append({
                "type": entity.get("type", "unknown"),
                "value": entity.get("textAnchor", {}).get("content", entity.get("mention_text", "")),
                "confidence": entity.get("confidence", 0.0),
                "normalized_value": entity.get("normalized_value", {}).get("text", "")
            })
        
        # Extract from pages and form fields
        pages = document.get("pages", [])
        for page in pages:
            # Form fields
            form_fields = page.get("formFields", [])
            for field in form_fields:
                field_name = field.get("fieldName", {}).get("textAnchor", {}).get("content", "")
                field_value = field.get("fieldValue", {}).get("textAnchor", {}).get("content", "")
                
                if field_name and field_value:
                    entities.append({
                        "type": f"form_field_{field_name.lower().replace(' ', '_')}",
                        "value": field_value,
                        "confidence": 0.9,
                        "normalized_value": field_value.strip()
                    })
        
        # If no structured entities, extract from text using regex
        if not entities and document.get("text"):
            entities = self._extract_entities_from_text(document["text"])
        
        return entities
    
    def _extract_entities_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract structured entities from OCR text using regex patterns"""
        import re
        
        entities = []
        text_upper = text.upper()
        
        # Passport number patterns
        passport_patterns = [
            r'PASSPORT\s*N[O°]?\:?\s*([A-Z0-9]{6,15})',
            r'DOCUMENT\s*N[O°]?\:?\s*([A-Z0-9]{6,15})',
            r'N[O°]\s*([A-Z0-9]{6,15})',
        ]
        
        for pattern in passport_patterns:
            matches = re.findall(pattern, text_upper)
            for match in matches:
                entities.append({
                    "type": "passport_number",
                    "value": match.strip(),
                    "confidence": 0.9,
                    "normalized_value": match.strip()
                })
                break
        
        # Name patterns
        name_patterns = [
            r'SURNAME[:\s]+([A-Z\s]{2,30})',
            r'FAMILY\s*NAME[:\s]+([A-Z\s]{2,30})',
            r'GIVEN\s*NAMES?[:\s]+([A-Z\s]{2,30})',
        ]
        
        for pattern in name_patterns:
            matches = re.findall(pattern, text_upper)
            for match in matches:
                entity_type = "surname" if "SURNAME" in pattern or "FAMILY" in pattern else "given_names"
                entities.append({
                    "type": entity_type,
                    "value": match.strip(),
                    "confidence": 0.85,
                    "normalized_value": match.strip()
                })
        
        # Date patterns
        date_patterns = [
            r'DATE\s*OF\s*BIRTH[:\s]+(\d{1,2}\s*[A-Z]{3}\s*\d{4})',
            r'DATE\s*OF\s*EXPIRY[:\s]+(\d{1,2}\s*[A-Z]{3}\s*\d{4})',
            r'EXPIRY[:\s]+(\d{1,2}\s*[A-Z]{3}\s*\d{4})',
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text_upper)
            for match in matches:
                entity_type = "date_of_birth" if "BIRTH" in pattern else "date_of_expiry"
                entities.append({
                    "type": entity_type,
                    "value": match.strip(),
                    "confidence": 0.8,
                    "normalized_value": match.strip()
                })
        
        # Nationality
        nationality_patterns = [
            r'NATIONALITY[:\s]+([A-Z\s]{5,30})',
        ]
        
        for pattern in nationality_patterns:
            matches = re.findall(pattern, text_upper)
            for match in matches:
                entities.append({
                    "type": "nationality",
                    "value": match.strip(),
                    "confidence": 0.9,
                    "normalized_value": match.strip()
                })
        
        return entities
    
    def extract_passport_fields(self, entities: List[Dict]) -> Dict[str, Any]:
        """Extract specific passport fields from entities"""
        
        passport_fields = {
            "passport_number": None,
            "surname": None,
            "given_names": None,
            "nationality": None,
            "date_of_birth": None,
            "date_of_expiry": None,
            "place_of_birth": None,
            "sex": None,
            "issuing_authority": None
        }
        
        # Map entity types to passport fields
        entity_mapping = {
            "passport_number": "passport_number",
            "document_number": "passport_number",
            "surname": "surname",
            "family_name": "surname",
            "given_names": "given_names",
            "first_name": "given_names",
            "nationality": "nationality",
            "date_of_birth": "date_of_birth",
            "birth_date": "date_of_birth",
            "date_of_expiry": "date_of_expiry",
            "expiry_date": "date_of_expiry",
            "place_of_birth": "place_of_birth",
            "sex": "sex",
            "gender": "sex",
            "issuing_authority": "issuing_authority",
            "authority": "issuing_authority"
        }
        
        # Extract fields from entities
        for entity in entities:
            entity_type = entity["type"].lower()
            if entity_type in entity_mapping:
                field_name = entity_mapping[entity_type]
                passport_fields[field_name] = {
                    "value": entity["value"],
                    "confidence": entity["confidence"],
                    "normalized": entity.get("normalized_value", "")
                }
        
        return passport_fields


class HybridDocumentValidator:
    """Hybrid validator combining Google Document AI + Dr. Miguel"""
    
    def __init__(self):
        self.google_processor = GoogleDocumentAIProcessor()
        self.dr_miguel = None
        
    async def _get_dr_miguel(self):
        """Lazy load Dr. Miguel to avoid circular imports"""
        if self.dr_miguel is None:
            from specialized_agents import DocumentValidationAgent
            self.dr_miguel = DocumentValidationAgent()
        return self.dr_miguel
    
    async def analyze_document(self, file_content: bytes, filename: str, 
                             document_type: str, applicant_name: str,
                             visa_type: str, case_id: str) -> Dict[str, Any]:
        """
        Complete document analysis using Google Document AI + Dr. Miguel
        """
        
        start_time = datetime.now()
        logger.info("🔬 Starting HYBRID analysis - Google AI + Dr. Miguel")
        
        try:
            # Determine MIME type
            mime_type = "application/pdf"
            if filename.lower().endswith(('.jpg', '.jpeg')):
                mime_type = "image/jpeg"
            elif filename.lower().endswith('.png'):
                mime_type = "image/png"
            elif filename.lower().endswith('.webp'):
                mime_type = "image/webp"
            
            # STEP 1: Google Vision API - Professional OCR and Data Extraction
            logger.info("📋 Step 1: Google Vision API processing")
            
            google_result = await self.google_processor.process_document(
                file_content, filename, mime_type
            )
            
            if not google_result["success"]:
                return {
                    "valid": False,
                    "legible": False,
                    "completeness": 0,
                    "issues": [f"❌ Google Vision API falhou: {google_result.get('error', 'Unknown error')}"],
                    "extracted_data": {
                        "document_type": document_type,
                        "file_name": filename,
                        "validation_status": "FAILED",
                        "error": google_result.get('error')
                    },
                    "dra_paula_assessment": f"❌ Processamento OCR falhou: {google_result.get('error_type', 'unknown')}"
                }
            
            # STEP 2: Dr. Miguel - AI-powered validation and fraud detection
            logger.info("🧠 Step 2: Dr. Miguel AI validation")
            
            dr_miguel = await self._get_dr_miguel()
            
            # Enhanced validation with extracted text context
            # Convert file content to string for Dr. Miguel
            document_data = google_result.get("extracted_text", str(file_content)[:1000])
            
            miguel_result = await dr_miguel.validate_document(
                document_data=document_data,
                document_type=document_type,
                case_context={
                    "applicant_name": applicant_name,
                    "visa_type": visa_type,
                    "case_id": case_id,
                    "filename": filename,
                    "google_extracted_text": google_result.get("extracted_text", ""),
                    "google_entities": google_result.get("extracted_entities", []),
                    "google_confidence": google_result.get("overall_confidence", 0)
                }
            )
            
            # STEP 3: Combine and enhance results
            logger.info("🔀 Step 3: Combining results")
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return self._create_hybrid_response(
                google_result, miguel_result, document_type, filename,
                visa_type, case_id, processing_time
            )
            
        except Exception as e:
            logger.error(f"❌ Hybrid analysis failed: {e}")
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return {
                "valid": False,
                "legible": False,
                "completeness": 0,
                "issues": [f"❌ Análise híbrida falhou: {str(e)}"],
                "extracted_data": {
                    "document_type": document_type,
                    "file_name": filename,
                    "validation_status": "ERROR",
                    "error": str(e)
                },
                "dra_paula_assessment": f"❌ Erro na análise híbrida: {str(e)}",
                "hybrid_analysis": {
                    "google_ai": "failed",
                    "dr_miguel": "failed",
                    "processing_time_ms": processing_time
                }
            }
    
    def _create_hybrid_response(self, google_result: Dict, miguel_result: Dict,
                              document_type: str, filename: str, visa_type: str,
                              case_id: str, processing_time: float) -> Dict[str, Any]:
        """Create comprehensive response combining Google AI and Dr. Miguel results"""
        
        # Extract key data
        google_confidence = google_result.get("overall_confidence", 0) * 100
        
        # Parse Dr. Miguel's string response
        miguel_confidence = 50  # Default confidence
        miguel_verdict = "NECESSITA_REVISÃO"  # Default verdict
        
        if isinstance(miguel_result, str):
            # Try to extract confidence and verdict from string response
            miguel_text = miguel_result.lower()
            if "aprovado" in miguel_text:
                miguel_verdict = "APROVADO"
                miguel_confidence = 85
            elif "rejeitado" in miguel_text:
                miguel_verdict = "REJEITADO"
                miguel_confidence = 15
            else:
                miguel_verdict = "NECESSITA_REVISÃO"
                miguel_confidence = 50
        else:
            # If it's a dict (shouldn't happen with current implementation)
            miguel_confidence = miguel_result.get("confidence_score", 50)
            miguel_verdict = miguel_result.get("verdict", "NECESSITA_REVISÃO")
        
        # Calculate combined confidence (weighted average)
        # Google AI: 40% weight (OCR accuracy)
        # Dr. Miguel: 60% weight (validation and fraud detection)
        combined_confidence = (google_confidence * 0.4) + (miguel_confidence * 0.6)
        
        # Determine overall validity
        is_valid = (
            miguel_verdict == "APROVADO" and 
            combined_confidence >= 75 and 
            google_confidence >= 50
        )
        
        # Combine issues
        issues = []
        
        # Add Google AI issues
        if google_confidence < 70:
            issues.append(f"⚠️ Qualidade de OCR baixa: {google_confidence:.1f}%")
        
        # Add Dr. Miguel issues
        if isinstance(miguel_result, str):
            # Extract issues from string response
            if "problema" in miguel_result.lower() or "erro" in miguel_result.lower():
                issues.append(f"Dr. Miguel: {miguel_result[:200]}...")
        else:
            miguel_issues = miguel_result.get("issues", [])
            if isinstance(miguel_issues, list):
                issues.extend(miguel_issues)
            elif isinstance(miguel_issues, str):
                issues.append(miguel_issues)
        
        # Extract structured data from Google AI
        extracted_entities = google_result.get("extracted_entities", [])
        passport_fields = self.google_processor.extract_passport_fields(extracted_entities)
        
        # Create enhanced extracted data
        extracted_data = {
            "document_type": document_type,
            "file_name": filename,
            "validation_status": "APPROVED" if is_valid else "REQUIRES_REVIEW" if combined_confidence >= 50 else "REJECTED",
            "visa_context": visa_type,
            "case_id": case_id,
            "google_vision_data": {
                "extracted_text": google_result.get("extracted_text", "")[:500] + "...",  # Truncate for storage
                "entities_count": len(extracted_entities),
                "ocr_confidence": google_confidence,
                "page_count": google_result.get("page_count", 0),
                "mock_mode": google_result.get("mock_mode", False),
                "api_enabled": not self.google_processor.is_mock_mode,
                "auth_method": self.google_processor.auth_method,
                "project_id": self.google_processor.project_id
            },
            "passport_fields": passport_fields,
            "dr_miguel_analysis": {
                "verdict": miguel_verdict,
                "confidence": miguel_confidence,
                "agent_version": "Dr. Miguel - Validador de Documentos",
                "raw_response": miguel_result[:200] + "..." if isinstance(miguel_result, str) and len(miguel_result) > 200 else miguel_result
            },
            "processing_stats": {
                "total_time_ms": processing_time,
                "google_time_ms": google_result.get("processing_time"),
                "combined_confidence": round(combined_confidence, 1)
            }
        }
        
        # Create professional assessment
        api_status = "API Real" if not self.google_processor.is_mock_mode else "Mock Mode"
        
        if is_valid:
            assessment = f"✅ HÍBRIDO: Documento aprovado (Google Vision {api_status}: {google_confidence:.1f}% + Dr. Miguel: {miguel_confidence:.1f}% = {combined_confidence:.1f}%)"
        elif combined_confidence >= 50:
            assessment = f"⚠️ HÍBRIDO: Documento requer revisão manual (Confiança: {combined_confidence:.1f}%)"
        else:
            assessment = f"❌ HÍBRIDO: Documento rejeitado (Confiança insuficiente: {combined_confidence:.1f}%)"
        
        return {
            "valid": is_valid,
            "legible": google_confidence >= 30,  # If Google AI can extract text, it's legible
            "completeness": round(combined_confidence, 0),
            "issues": issues if issues else ["Nenhum problema detectado"],
            "extracted_data": extracted_data,
            "dra_paula_assessment": assessment,
            "hybrid_powered": True,
            "google_vision_enabled": True,
            "dr_miguel_enabled": True,
            "professional_grade": True,
            "real_api_active": not self.google_processor.is_mock_mode
        }


# Global instance
hybrid_validator = HybridDocumentValidator()