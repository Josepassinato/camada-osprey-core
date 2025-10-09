"""
Google Cloud Document AI - Specialized Document Processing
Sistema especializado de processamento de documentos de imigração usando Document AI
"""

import os
import base64
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

@dataclass
class DocumentAIResult:
    """Result from Google Document AI"""
    document_type: str
    confidence: float
    extracted_fields: Dict[str, Any]
    full_text: str
    entities: List[Dict]
    processing_time: float
    error: Optional[str] = None


class GoogleDocumentAI:
    """
    Google Cloud Document AI integration for immigration documents
    
    Supports:
    - Passports
    - Driver Licenses
    - Birth Certificates
    - Marriage Certificates
    - I-797 Forms
    - Tax Documents
    - And more...
    """
    
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            logger.error("❌ GOOGLE_API_KEY not found in environment")
            raise ValueError("GOOGLE_API_KEY is required for Document AI")
        
        # ENHANCED: Document type keywords for high-accuracy classification
        self.document_keywords = {
            'driver_license': ['carteira nacional de habilitação', 'cnh', 'detran', 'categoria', 'permissão para dirigir', 'driver license', 'driver\'s license', 'dl', 'license number'],
            'passport': ['república federativa do brasil', 'passaporte', 'passport', 'tipo/type', 'nationality/nacionalidade', 'mrz', 'p<bra', 'date of issue', 'date of expiry'],
            'birth_certificate': ['certidão de nascimento', 'birth certificate', 'nascido', 'data de nascimento', 'cartório', 'registro civil'],
            'marriage_certificate': ['certidão de casamento', 'marriage certificate', 'cônjuge', 'casamento', 'matrimônio'],
            'i797': ['i-797', 'notice of action', 'uscis', 'receipt number', 'beneficiary', 'petitioner'],
            'tax_return': ['receita federal', 'irpf', 'tax return', 'w-2', '1040', 'adjusted gross income']
        }
        
        logger.info("✅ Google Document AI initialized with enhanced classification")
    
    async def process_document(
        self,
        image_data: bytes,
        document_type: str = 'generic',
        language: str = 'en'
    ) -> DocumentAIResult:
        """
        Process document using Google Cloud Document AI
        
        Args:
            image_data: Raw image bytes
            document_type: Type of document (passport, driver_license, etc.)
            language: Language code (en, pt, es, etc.)
        
        Returns:
            DocumentAIResult with extracted fields and classification
        """
        import time
        start_time = time.time()
        
        try:
            # Convert bytes to base64
            if isinstance(image_data, bytes):
                image_base64 = base64.b64encode(image_data).decode('utf-8')
            else:
                image_base64 = image_data
            
            # Google Cloud Vision API with Document Text Detection
            # Note: Para usar Document AI completo, você precisaria de:
            # - Projeto Google Cloud configurado
            # - Processadores Document AI criados
            # - Service account com permissões
            
            # Por enquanto, usando Vision API com DOCUMENT_TEXT_DETECTION
            # que é mais poderoso que TEXT_DETECTION para documentos
            
            url = f"https://vision.googleapis.com/v1/images:annotate?key={self.api_key}"
            
            payload = {
                "requests": [
                    {
                        "image": {
                            "content": image_base64
                        },
                        "features": [
                            {
                                "type": "DOCUMENT_TEXT_DETECTION",  # Melhor para documentos
                                "maxResults": 50
                            },
                            {
                                "type": "LABEL_DETECTION",  # Detecta tipo de documento
                                "maxResults": 10
                            }
                        ],
                        "imageContext": {
                            "languageHints": [language, "en"]
                        }
                    }
                ]
            }
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"❌ Document AI API error: {response.status_code} - {response.text}")
                return DocumentAIResult(
                    document_type="unknown",
                    confidence=0.0,
                    extracted_fields={},
                    full_text="",
                    entities=[],
                    processing_time=time.time() - start_time,
                    error=f"API error: {response.status_code}"
                )
            
            result = response.json()
            
            # Extract full text from document
            full_text = ""
            if 'responses' in result and len(result['responses']) > 0:
                if 'fullTextAnnotation' in result['responses'][0]:
                    full_text = result['responses'][0]['fullTextAnnotation'].get('text', '')
            
            # Extract labels (helps identify document type)
            labels = []
            if 'responses' in result and len(result['responses']) > 0:
                if 'labelAnnotations' in result['responses'][0]:
                    labels = [
                        {
                            'description': label.get('description'),
                            'score': label.get('score', 0.0)
                        }
                        for label in result['responses'][0]['labelAnnotations']
                    ]
            
            # Extract structured entities from document
            entities = self._extract_entities_from_text(full_text, document_type)
            
            # Extract fields based on document type
            extracted_fields = self._extract_fields_by_type(full_text, entities, document_type)
            
            # Calculate confidence
            confidence = self._calculate_confidence(full_text, extracted_fields, labels)
            
            processing_time = time.time() - start_time
            
            logger.info(f"✅ Document AI processed: {len(full_text)} chars, confidence: {confidence:.2f}, time: {processing_time:.2f}s")
            
            return DocumentAIResult(
                document_type=document_type,
                confidence=confidence,
                extracted_fields=extracted_fields,
                full_text=full_text,
                entities=entities,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"❌ Document AI processing failed: {str(e)}")
            return DocumentAIResult(
                document_type="unknown",
                confidence=0.0,
                extracted_fields={},
                full_text="",
                entities=[],
                processing_time=time.time() - start_time,
                error=str(e)
            )
    
    def _extract_entities_from_text(self, text: str, doc_type: str) -> List[Dict]:
        """Extract entities (names, dates, numbers) from text"""
        import re
        
        entities = []
        
        # Patterns for common entities
        patterns = {
            'date': r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b',
            'passport_number': r'\b[A-Z]{1,2}\d{6,10}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'phone': r'\b\+?\d{1,3}[\s-]?\(?\d{2,3}\)?[\s-]?\d{3,4}[\s-]?\d{4}\b',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'money': r'\$\s?\d+[,\d]*\.?\d*'
        }
        
        for entity_type, pattern in patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entities.append({
                    'type': entity_type,
                    'value': match.group(),
                    'start': match.start(),
                    'end': match.end()
                })
        
        return entities
    
    def _extract_fields_by_type(
        self,
        text: str,
        entities: List[Dict],
        doc_type: str
    ) -> Dict[str, Any]:
        """Extract specific fields based on document type"""
        
        fields = {}
        
        if doc_type == 'passport':
            fields = self._extract_passport_fields(text, entities)
        elif doc_type == 'driver_license':
            fields = self._extract_driver_license_fields(text, entities)
        elif doc_type == 'birth_certificate':
            fields = self._extract_birth_certificate_fields(text, entities)
        elif doc_type == 'i797':
            fields = self._extract_i797_fields(text, entities)
        else:
            # Generic extraction
            fields = {
                'dates': [e['value'] for e in entities if e['type'] == 'date'],
                'numbers': [e['value'] for e in entities if e['type'] == 'passport_number'],
                'phones': [e['value'] for e in entities if e['type'] == 'phone'],
                'emails': [e['value'] for e in entities if e['type'] == 'email']
            }
        
        return fields
    
    def _extract_passport_fields(self, text: str, entities: List[Dict]) -> Dict:
        """Extract passport-specific fields"""
        import re
        
        fields = {}
        
        # Passport number
        passport_nums = [e['value'] for e in entities if e['type'] == 'passport_number']
        if passport_nums:
            fields['passport_number'] = passport_nums[0]
        
        # Dates
        dates = [e['value'] for e in entities if e['type'] == 'date']
        if len(dates) >= 2:
            fields['date_of_birth'] = dates[0]
            fields['expiry_date'] = dates[-1]
        
        # MRZ (Machine Readable Zone)
        mrz_pattern = r'P<[A-Z]{3}[A-Z<]+<<[A-Z<]+'
        mrz_match = re.search(mrz_pattern, text)
        if mrz_match:
            fields['mrz'] = mrz_match.group()
        
        # Nationality
        if 'BRAZIL' in text.upper() or 'BRASIL' in text.upper():
            fields['nationality'] = 'Brazilian'
        elif 'USA' in text.upper() or 'UNITED STATES' in text.upper():
            fields['nationality'] = 'American'
        
        return fields
    
    def _extract_driver_license_fields(self, text: str, entities: List[Dict]) -> Dict:
        """Extract driver license fields"""
        fields = {}
        
        # License number
        import re
        license_pattern = r'\b\d{9,12}\b'
        license_match = re.search(license_pattern, text)
        if license_match:
            fields['license_number'] = license_match.group()
        
        # Dates
        dates = [e['value'] for e in entities if e['type'] == 'date']
        if dates:
            fields['issue_date'] = dates[0] if len(dates) > 0 else None
            fields['expiry_date'] = dates[-1] if len(dates) > 1 else None
        
        # State
        if 'DETRAN' in text.upper():
            fields['country'] = 'Brazil'
        
        return fields
    
    def _extract_birth_certificate_fields(self, text: str, entities: List[Dict]) -> Dict:
        """Extract birth certificate fields"""
        fields = {}
        
        dates = [e['value'] for e in entities if e['type'] == 'date']
        if dates:
            fields['birth_date'] = dates[0]
        
        return fields
    
    def _extract_i797_fields(self, text: str, entities: List[Dict]) -> Dict:
        """Extract I-797 form fields"""
        import re
        
        fields = {}
        
        # Receipt number
        receipt_pattern = r'\b[A-Z]{3}\d{10}\b'
        receipt_match = re.search(receipt_pattern, text)
        if receipt_match:
            fields['receipt_number'] = receipt_match.group()
        
        # Notice type
        if 'APPROVAL' in text.upper():
            fields['notice_type'] = 'Approval Notice'
        elif 'RECEIPT' in text.upper():
            fields['notice_type'] = 'Receipt Notice'
        
        return fields
    
    def _calculate_confidence(
        self,
        text: str,
        fields: Dict,
        labels: List[Dict]
    ) -> float:
        """Calculate overall confidence score"""
        
        confidence = 0.0
        
        # Text length factor (longer = more confident)
        if len(text) > 100:
            confidence += 0.3
        elif len(text) > 50:
            confidence += 0.2
        
        # Fields extracted factor
        if len(fields) >= 3:
            confidence += 0.4
        elif len(fields) >= 1:
            confidence += 0.2
        
        # Label confidence factor
        if labels:
            avg_label_score = sum(l['score'] for l in labels) / len(labels)
            confidence += avg_label_score * 0.3
        
        return min(confidence, 1.0)


# Global instance
google_document_ai = GoogleDocumentAI()
