"""
Google Cloud Vision OCR Engine - Production Grade
Engine OCR de alta precisão usando Google Cloud Vision API
"""

import os
import re
import base64
import logging
import asyncio
import requests
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
import time
import json

logger = logging.getLogger(__name__)

@dataclass
class VisionOCRResult:
    """Result from Google Vision OCR"""
    text: str
    confidence: float
    bounding_boxes: List[Dict]
    language: str
    processing_time: float
    detected_break_type: str = "UNKNOWN"
    word_count: int = 0

class GoogleVisionOCR:
    """
    Google Cloud Vision OCR Engine
    Provides highest accuracy OCR using Google's ML models
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("Google API Key is required")
        
        self.base_url = "https://vision.googleapis.com/v1/images:annotate"
        self.session = requests.Session()
        
        # Configure session for better performance
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Immigration-Document-Processor/1.0'
        })
    
    async def detect_text(self, 
                         image_data: Union[str, bytes],
                         detection_type: str = "TEXT_DETECTION",
                         language_hints: List[str] = None) -> VisionOCRResult:
        """
        Detect text in image using Google Vision API
        
        Args:
            image_data: Base64 string or bytes
            detection_type: TEXT_DETECTION or DOCUMENT_TEXT_DETECTION
            language_hints: Language codes like ['en', 'pt']
        
        Returns:
            VisionOCRResult with extracted text and metadata
        """
        start_time = time.time()
        
        try:
            # Prepare image data
            if isinstance(image_data, bytes):
                encoded_image = base64.b64encode(image_data).decode('utf-8')
            elif isinstance(image_data, str):
                # Remove data URL prefix if present
                if image_data.startswith('data:'):
                    encoded_image = image_data.split(',')[1]
                else:
                    encoded_image = image_data
            else:
                raise ValueError(f"Unsupported image data type: {type(image_data)}")
            
            # Prepare request payload
            feature = {
                'type': detection_type,
                'maxResults': 50  # Get detailed results
            }
            
            # Add language hints if provided
            image_context = {}
            if language_hints:
                image_context['languageHints'] = language_hints
            
            payload = {
                'requests': [{
                    'image': {
                        'content': encoded_image
                    },
                    'features': [feature]
                }]
            }
            
            if image_context:
                payload['requests'][0]['imageContext'] = image_context
            
            # Make API request
            url = f"{self.base_url}?key={self.api_key}"
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: self.session.post(url, json=payload, timeout=30)
            )
            
            processing_time = time.time() - start_time
            
            if response.status_code != 200:
                logger.error(f"Google Vision API error: {response.status_code} - {response.text}")
                raise Exception(f"API error: {response.status_code}")
            
            result = response.json()
            
            # Parse response
            return self._parse_vision_response(result, processing_time, detection_type)
            
        except Exception as e:
            logger.error(f"Google Vision OCR failed: {e}")
            return VisionOCRResult(
                text="",
                confidence=0.0,
                bounding_boxes=[],
                language="unknown",
                processing_time=time.time() - start_time
            )
    
    def _parse_vision_response(self, 
                             response: Dict, 
                             processing_time: float,
                             detection_type: str) -> VisionOCRResult:
        """Parse Google Vision API response"""
        
        try:
            responses = response.get('responses', [])
            if not responses:
                return self._empty_result(processing_time)
            
            vision_response = responses[0]
            
            # Check for errors
            if 'error' in vision_response:
                error = vision_response['error']
                logger.error(f"Vision API error: {error}")
                return self._empty_result(processing_time)
            
            # Extract text based on detection type
            if detection_type == "DOCUMENT_TEXT_DETECTION":
                return self._parse_document_text(vision_response, processing_time)
            else:
                return self._parse_text_annotations(vision_response, processing_time)
                
        except Exception as e:
            logger.error(f"Failed to parse Vision response: {e}")
            return self._empty_result(processing_time)
    
    def _parse_document_text(self, response: Dict, processing_time: float) -> VisionOCRResult:
        """Parse DOCUMENT_TEXT_DETECTION response (more structured)"""
        
        full_text_annotation = response.get('fullTextAnnotation', {})
        text = full_text_annotation.get('text', '')
        
        # Extract pages and blocks
        pages = full_text_annotation.get('pages', [])
        
        bounding_boxes = []
        total_confidence = 0.0
        confidence_count = 0
        word_count = 0
        
        for page in pages:
            blocks = page.get('blocks', [])
            for block in blocks:
                block_confidence = block.get('confidence', 0.0)
                paragraphs = block.get('paragraphs', [])
                
                for paragraph in paragraphs:
                    para_confidence = paragraph.get('confidence', block_confidence)
                    words = paragraph.get('words', [])
                    
                    for word in words:
                        word_confidence = word.get('confidence', para_confidence)
                        symbols = word.get('symbols', [])
                        
                        # Extract word text
                        word_text = ''.join([s.get('text', '') for s in symbols])
                        
                        if word_text.strip():
                            word_count += 1
                            
                            # Get bounding box
                            bounding_poly = word.get('boundingBox', {})
                            vertices = bounding_poly.get('vertices', [])
                            
                            if vertices:
                                x_coords = [v.get('x', 0) for v in vertices]
                                y_coords = [v.get('y', 0) for v in vertices]
                                
                                bounding_boxes.append({
                                    'text': word_text,
                                    'confidence': word_confidence * 100,
                                    'x': min(x_coords),
                                    'y': min(y_coords),
                                    'width': max(x_coords) - min(x_coords),
                                    'height': max(y_coords) - min(y_coords),
                                    'vertices': vertices
                                })
                                
                                total_confidence += word_confidence
                                confidence_count += 1
        
        # Calculate average confidence
        avg_confidence = (total_confidence / confidence_count) if confidence_count > 0 else 0.0
        
        # Detect language
        text_language = self._detect_language_from_text(text)
        
        return VisionOCRResult(
            text=text,
            confidence=avg_confidence,
            bounding_boxes=bounding_boxes,
            language=text_language,
            processing_time=processing_time,
            detected_break_type="DOCUMENT",
            word_count=word_count
        )
    
    def _parse_text_annotations(self, response: Dict, processing_time: float) -> VisionOCRResult:
        """Parse TEXT_DETECTION response (simpler format)"""
        
        text_annotations = response.get('textAnnotations', [])
        
        if not text_annotations:
            return self._empty_result(processing_time)
        
        # First annotation contains full text
        full_text = text_annotations[0].get('description', '')
        
        # Calculate confidence from individual words
        bounding_boxes = []
        total_confidence = 0.0
        confidence_count = 0
        
        # Skip first annotation (full text) and process individual words
        for annotation in text_annotations[1:]:
            text = annotation.get('description', '')
            bounding_poly = annotation.get('boundingPoly', {})
            vertices = bounding_poly.get('vertices', [])
            
            if vertices and text.strip():
                x_coords = [v.get('x', 0) for v in vertices]
                y_coords = [v.get('y', 0) for v in vertices]
                
                # Estimate confidence based on text characteristics
                confidence = self._estimate_text_confidence(text)
                
                bounding_boxes.append({
                    'text': text,
                    'confidence': confidence * 100,
                    'x': min(x_coords),
                    'y': min(y_coords),
                    'width': max(x_coords) - min(x_coords),
                    'height': max(y_coords) - min(y_coords),
                    'vertices': vertices
                })
                
                total_confidence += confidence
                confidence_count += 1
        
        avg_confidence = (total_confidence / confidence_count) if confidence_count > 0 else 0.9
        
        # Detect language
        text_language = self._detect_language_from_text(full_text)
        
        return VisionOCRResult(
            text=full_text,
            confidence=avg_confidence,
            bounding_boxes=bounding_boxes,
            language=text_language,
            processing_time=processing_time,
            detected_break_type="TEXT",
            word_count=len(bounding_boxes)
        )
    
    def _estimate_text_confidence(self, text: str) -> float:
        """Estimate confidence based on text characteristics"""
        if not text:
            return 0.0
        
        confidence = 0.85  # Base confidence for Google Vision
        
        # Adjust based on text length
        if len(text) >= 3:
            confidence += 0.05
        
        # Adjust based on character types
        if text.isalnum():
            confidence += 0.05
        elif text.isalpha():
            confidence += 0.03
        elif text.isdigit():
            confidence += 0.07  # Numbers usually more confident
        
        # Penalize special characters (might be OCR artifacts)
        special_chars = len(re.findall(r'[^A-Za-z0-9\s<>]', text))
        if special_chars > 0:
            confidence -= special_chars * 0.01
        
        return max(0.5, min(0.98, confidence))
    
    def _detect_language_from_text(self, text: str) -> str:
        """Simple language detection from text patterns"""
        if not text:
            return "unknown"
        
        # Common Portuguese words
        portuguese_patterns = ['de', 'da', 'do', 'em', 'para', 'com', 'por', 'uma', 'um', 'não']
        # Common English words  
        english_patterns = ['the', 'and', 'of', 'to', 'in', 'is', 'was', 'for', 'with', 'on']
        
        text_lower = text.lower()
        
        portuguese_count = sum(1 for word in portuguese_patterns if f' {word} ' in f' {text_lower} ')
        english_count = sum(1 for word in english_patterns if f' {word} ' in f' {text_lower} ')
        
        if portuguese_count > english_count:
            return "pt"
        elif english_count > 0:
            return "en"
        else:
            return "unknown"
    
    def _empty_result(self, processing_time: float) -> VisionOCRResult:
        """Return empty result"""
        return VisionOCRResult(
            text="",
            confidence=0.0,
            bounding_boxes=[],
            language="unknown",
            processing_time=processing_time
        )
    
    async def extract_mrz_from_passport(self, image_data: Union[str, bytes]) -> Dict[str, Any]:
        """
        Specialized MRZ extraction using Google Vision
        """
        try:
            # Use DOCUMENT_TEXT_DETECTION for better structured output
            result = await self.detect_text(
                image_data, 
                detection_type="DOCUMENT_TEXT_DETECTION",
                language_hints=['en']  # MRZ is always in English characters
            )
            
            # Extract and clean MRZ from full text
            mrz_text = self._extract_mrz_from_text(result.text)
            
            return {
                'mrz_text': mrz_text,
                'full_text': result.text,
                'confidence': result.confidence,
                'word_count': result.word_count,
                'processing_time': result.processing_time,
                'language': result.language,
                'method': 'google_vision_document',
                'region_detected': len(mrz_text) > 0
            }
            
        except Exception as e:
            logger.error(f"Google Vision MRZ extraction failed: {e}")
            return {
                'mrz_text': "",
                'full_text': "",
                'confidence': 0.0,
                'method': 'google_vision_failed',
                'error': str(e),
                'region_detected': False
            }
    
    def _extract_mrz_from_text(self, full_text: str) -> str:
        """Extract MRZ lines from full OCR text"""
        if not full_text:
            return ""
        
        lines = full_text.split('\n')
        mrz_candidates = []
        
        for line in lines:
            # Clean line
            cleaned = re.sub(r'[^A-Z0-9<]', '', line.upper())
            
            # MRZ lines are typically 44 characters and contain specific patterns
            if len(cleaned) >= 30:  # More lenient initially
                # Check for MRZ-like patterns
                if (cleaned.startswith('P<') or  # Passport first line
                    re.match(r'^[A-Z0-9<]{30,}$', cleaned)):  # Second line pattern
                    
                    # Ensure exactly 44 characters
                    if len(cleaned) < 44:
                        cleaned = cleaned.ljust(44, '<')
                    elif len(cleaned) > 44:
                        cleaned = cleaned[:44]
                    
                    mrz_candidates.append(cleaned)
        
        # Return first 2 candidates (MRZ has 2 lines)
        if len(mrz_candidates) >= 2:
            return '\n'.join(mrz_candidates[:2])
        elif len(mrz_candidates) == 1:
            return mrz_candidates[0]
        else:
            return ""
    
    def get_engine_info(self) -> Dict[str, Any]:
        """Get information about the Vision OCR engine"""
        return {
            'engine_name': 'Google Cloud Vision API',
            'api_key_configured': bool(self.api_key),
            'supported_features': [
                'TEXT_DETECTION',
                'DOCUMENT_TEXT_DETECTION', 
                'Multi-language support',
                'High accuracy MRZ reading',
                'Structured text extraction',
                'Confidence scoring'
            ],
            'supported_languages': ['en', 'pt', 'es', 'fr', 'de', 'auto'],
            'max_image_size': '20MB',
            'formats_supported': ['JPEG', 'PNG', 'GIF', 'BMP', 'WEBP', 'RAW', 'ICO', 'PDF', 'TIFF']
        }

# Global instance - only create if API key is available
google_vision_ocr = None

def get_google_vision_ocr():
    """Get Google Vision OCR instance, creating it if needed and API key is available"""
    global google_vision_ocr
    if google_vision_ocr is None:
        api_key = os.getenv('GOOGLE_API_KEY')
        if api_key:
            try:
                google_vision_ocr = GoogleVisionOCR(api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize Google Vision OCR: {e}")
                google_vision_ocr = False  # Mark as failed
        else:
            logger.warning("Google Vision API key not configured")
            google_vision_ocr = False
    
    return google_vision_ocr if google_vision_ocr is not False else None

# Initialize on import if possible
try:
    google_vision_ocr = get_google_vision_ocr()
except Exception as e:
    logger.warning(f"Google Vision OCR initialization failed: {e}")
    google_vision_ocr = None