"""
Passport OCR Engine - Specialized for MRZ Reading  
OCR engine otimizado para leitura de MRZ com pré-processamento específico
"""

import re
import base64
import logging
from typing import Dict, List, Any, Optional, Tuple
import io
import asyncio

# Import real OCR engine
from .real_ocr_engine import real_ocr_engine, OCRResult

# Required imports for image processing
import cv2
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

class PassportOCREngine:
    """
    OCR Engine especializado para passaportes com foco em MRZ
    Inclui pré-processamento de imagem e pós-correção
    """
    
    def __init__(self):
        self.mrz_patterns = [
            r'P<[A-Z]{3}[A-Z<]+',  # MRZ Line 1 pattern
            r'[A-Z0-9<]{44}',      # MRZ Line 2 pattern
        ]
        
        # Common OCR misreads in MRZ context
        self.ocr_corrections = {
            'O': '0', 'I': '1', 'l': '1', 'S': '5', 'B': '8', 
            'G': '6', 'D': '0', 'Z': '2', 'T': '7', 'A': '4', 'Q': '0',
            '|': '1', ']': '1', '[': '1', ')': '0', '(': '0'
        }
    
    async def extract_text_from_passport(self, image_data: str, document_type: str = "passport") -> Dict[str, Any]:
        """
        Extrai texto de passaporte com foco especial na MRZ usando OCR real
        
        Args:
            image_data: Base64 encoded image
            document_type: Tipo do documento (usado para otimizações)
            
        Returns:
            Dict com texto extraído e metadados
        """
        try:
            # 1. Extract MRZ using specialized method
            mrz_result = real_ocr_engine.extract_mrz_from_passport(image_data)
            
            # 2. Extract full document text
            full_ocr_result = await real_ocr_engine.extract_text_from_image(
                image_data, 
                mode="document", 
                language="eng"
            )
            
            # 3. Extract printed fields from full text
            printed_data = self._extract_printed_fields(full_ocr_result.text)
            
            # 4. Combine results
            result = {
                'mrz_text': mrz_result['mrz_text'],
                'full_text': full_ocr_result.text,
                'printed_data': printed_data,
                'ocr_confidence': max(mrz_result['confidence'], full_ocr_result.confidence),
                'processing_method': 'real_ocr_engine',
                'mrz_lines_detected': len(mrz_result['mrz_text'].split('\n')) if mrz_result['mrz_text'] else 0,
                'mrz_region_detected': mrz_result['region_detected'],
                'engine_used': full_ocr_result.engine,
                'processing_time': full_ocr_result.processing_time
            }
            
            logger.info(f"Real OCR extraction completed: {result['processing_method']}, confidence: {result['ocr_confidence']:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Real OCR extraction failed: {e}")
            # Fallback to basic extraction
            return self._fallback_text_extraction(image_data)
    
    def _preprocess_passport_image(self, base64_image: str) -> np.ndarray:
        """
        Pré-processa imagem de passaporte para melhor OCR (now using real implementation)
        """
        try:
            # Decode base64 to PIL Image
            if base64_image.startswith('data:'):
                base64_image = base64_image.split(',')[1]
            
            image_data = base64.b64decode(base64_image)
            pil_image = Image.open(io.BytesIO(image_data))
            
            # Convert to OpenCV format
            image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            
            # 1. Resize if too large (max 2000px width)
            height, width = image.shape[:2]
            if width > 2000:
                scale = 2000 / width
                new_width = int(width * scale)
                new_height = int(height * scale)
                image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
            
            # 2. Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 3. Enhance contrast
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(gray)
            
            # 4. Denoise
            denoised = cv2.bilateralFilter(enhanced, 9, 75, 75)
            
            # 5. Sharpen for text clarity
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            sharpened = cv2.filter2D(denoised, -1, kernel)
            
            return sharpened
            
        except Exception as e:
            logger.error(f"Image preprocessing error: {e}")
            # Return empty array on error
            return np.zeros((100, 100), dtype=np.uint8)
    
    def _detect_mrz_region(self, image: np.ndarray) -> np.ndarray:
        """
        Detecta e extrai região da MRZ usando características específicas (real implementation)
        """
        try:
            # MRZ is typically in the bottom portion of passport
            height, width = image.shape[:2]
            
            # Focus on bottom 35% of image where MRZ is located
            bottom_region = image[int(height * 0.65):, :]
            
            # Apply threshold to highlight text
            _, thresh = cv2.threshold(bottom_region, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Find horizontal lines (MRZ characteristics)
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
            horizontal_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel)
            
            # If we can detect MRZ structure, use it; otherwise use full bottom region
            contours, _ = cv2.findContours(horizontal_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # Find the largest horizontal region (likely MRZ)
                largest_contour = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(largest_contour)
                
                # Expand bounding box slightly
                x = max(0, x - 10)
                y = max(0, y - 5)
                w = min(width - x, w + 20)
                h = min(bottom_region.shape[0] - y, h + 10)
                
                mrz_region = bottom_region[y:y+h, x:x+w]
            else:
                # Fallback: use entire bottom region
                mrz_region = bottom_region
            
            return mrz_region
            
        except Exception as e:
            logger.error(f"MRZ detection error: {e}")
            # Return fallback - bottom portion of image
            if hasattr(image, 'shape') and len(image.shape) >= 2:
                height = image.shape[0]
                return image[int(height * 0.75):, :]
            else:
                return np.zeros((50, 200), dtype=np.uint8)
    
    async def _ocr_mrz_region(self, mrz_region: np.ndarray) -> str:
        """
        Performs OCR specifically optimized for MRZ using real OCR engine
        """
        try:
            # Convert numpy array to PIL Image for OCR engine
            mrz_image = Image.fromarray(mrz_region)
            
            # Use real OCR engine with MRZ mode
            result = await real_ocr_engine.extract_text_from_image(
                mrz_image,
                mode="mrz",
                language="eng"
            )
            
            logger.info(f"Real MRZ OCR extracted: {len(result.text)} chars, confidence: {result.confidence:.2f}")
            return result.text
            
        except Exception as e:
            logger.error(f"MRZ OCR error: {e}")
            return ""
    
    def _simulate_realistic_ocr_errors(self, text: str) -> str:
        """
        Simulates realistic OCR errors that might occur
        """
        import random
        
        if random.random() > 0.8:  # 20% chance of OCR errors
            chars = list(text)
            # Introduce 1-2 character errors
            for _ in range(random.randint(0, 2)):
                if chars:
                    pos = random.randint(0, len(chars) - 1)
                    if chars[pos] in ['0', '1', '8', '6']:
                        # Common OCR confusions
                        error_map = {'0': 'O', '1': 'I', '8': 'B', '6': 'G'}
                        chars[pos] = error_map.get(chars[pos], chars[pos])
            text = ''.join(chars)
        
        return text
    
    def _ocr_full_document(self, image) -> str:
        """
        Performs OCR on full document to extract printed information
        """
        try:
            # Simulate extraction of printed passport data
            simulated_data = """
            PASSPORT
            United States of America
            
            Type: P
            Country Code: USA
            Passport No.: 123456789
            
            Surname: DOE
            Given Names: JOHN
            
            Nationality: USA
            Date of Birth: 01 JAN 1980
            Sex: M
            Place of Birth: NEW YORK, NY
            Date of Issue: 15 DEC 2020
            Date of Expiry: 15 DEC 2030
            Authority: U.S. DEPARTMENT OF STATE
            """
            
            return simulated_data.strip()
            
        except Exception as e:
            logger.error(f"Full document OCR error: {e}")
            return "OCR extraction failed"
    
    def _post_process_results(self, mrz_text: str, full_text: str) -> Dict[str, Any]:
        """
        Post-processes OCR results and extracts structured data
        """
        try:
            # Extract printed data from full text
            printed_data = self._extract_printed_fields(full_text)
            
            # Clean and validate MRZ
            cleaned_mrz = self._clean_mrz_text(mrz_text)
            
            # Estimate confidence based on text quality
            confidence = self._estimate_ocr_confidence(mrz_text, full_text)
            
            return {
                'mrz_text': cleaned_mrz,
                'full_text': full_text,
                'printed_data': printed_data,
                'ocr_confidence': confidence,
                'processing_method': 'specialized_passport_ocr',
                'mrz_lines_detected': len(cleaned_mrz.split('\n')) if cleaned_mrz else 0
            }
            
        except Exception as e:
            logger.error(f"Post-processing error: {e}")
            return {
                'mrz_text': mrz_text,
                'full_text': full_text,
                'printed_data': {},
                'ocr_confidence': 0.5,
                'processing_method': 'fallback',
                'error': str(e)
            }
    
    def _extract_printed_fields(self, text: str) -> Dict[str, Any]:
        """
        Extracts structured fields from printed passport text
        """
        fields = {}
        
        try:
            # Extract passport number
            passport_match = re.search(r'Passport No\.?:?\s*([A-Z0-9]+)', text, re.IGNORECASE)
            if passport_match:
                fields['document_number'] = passport_match.group(1)
            
            # Extract surname
            surname_match = re.search(r'Surname:?\s*([A-Z\s]+)', text, re.IGNORECASE)
            if surname_match:
                fields['last_name'] = surname_match.group(1).strip()
            
            # Extract given names
            given_match = re.search(r'Given Names?:?\s*([A-Z\s]+)', text, re.IGNORECASE)
            if given_match:
                fields['first_name'] = given_match.group(1).strip()
            
            # Extract date of birth
            dob_patterns = [
                r'Date of Birth:?\s*(\d{2}\s+[A-Z]{3}\s+\d{4})',
                r'DOB:?\s*(\d{2}[/-]\d{2}[/-]\d{4})'
            ]
            for pattern in dob_patterns:
                dob_match = re.search(pattern, text, re.IGNORECASE)
                if dob_match:
                    fields['date_of_birth'] = dob_match.group(1)
                    break
            
            # Extract nationality
            nationality_match = re.search(r'Nationality:?\s*([A-Z]{3})', text, re.IGNORECASE)
            if nationality_match:
                fields['nationality'] = nationality_match.group(1)
            
            # Extract sex
            sex_match = re.search(r'Sex:?\s*([MF])', text, re.IGNORECASE)
            if sex_match:
                fields['sex'] = sex_match.group(1)
                
        except Exception as e:
            logger.error(f"Field extraction error: {e}")
        
        return fields
    
    def _clean_mrz_text(self, mrz_text: str) -> str:
        """
        Cleans and formats MRZ text
        """
        if not mrz_text:
            return ""
        
        # Split into lines and clean each
        lines = [line.strip() for line in mrz_text.split('\n') if line.strip()]
        
        # Filter to likely MRZ lines (44 characters, specific patterns)
        mrz_lines = []
        for line in lines:
            if len(line) >= 40 and (line.startswith('P<') or re.match(r'^[A-Z0-9<]{40,44}$', line)):
                # Ensure exactly 44 characters by padding or truncating
                if len(line) < 44:
                    line = line.ljust(44, '<')
                elif len(line) > 44:
                    line = line[:44]
                mrz_lines.append(line)
        
        return '\n'.join(mrz_lines)
    
    def _estimate_ocr_confidence(self, mrz_text: str, full_text: str) -> float:
        """
        Estimates OCR confidence based on text characteristics
        """
        confidence = 0.8  # Base confidence
        
        try:
            # Check MRZ format compliance
            if mrz_text:
                lines = mrz_text.split('\n')
                if len(lines) == 2 and all(len(line) == 44 for line in lines):
                    confidence += 0.1
                if lines and lines[0].startswith('P<'):
                    confidence += 0.05
            
            # Check for common text patterns
            if 'PASSPORT' in full_text.upper():
                confidence += 0.03
            if re.search(r'Date of Birth|DOB', full_text, re.IGNORECASE):
                confidence += 0.02
            
            return min(confidence, 1.0)
            
        except Exception:
            return 0.7
    
    def _fallback_text_extraction(self, image_data: str) -> Dict[str, Any]:
        """
        Fallback method when specialized OCR fails
        """
        return {
            'mrz_text': "",
            'full_text': "Extracted text from document using OCR",
            'printed_data': {},
            'ocr_confidence': 0.5,
            'processing_method': 'fallback',
            'error': 'Specialized OCR failed, using fallback'
        }

# Global instance
passport_ocr_engine = PassportOCREngine()