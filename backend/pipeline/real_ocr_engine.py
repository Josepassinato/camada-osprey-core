"""
Real OCR Engine - Production Implementation
Engine OCR real para produção com múltiplas tecnologias
Integra Google Vision API, Tesseract e EasyOCR para máxima precisão
"""

import os
import re
import base64
import logging
import asyncio
import tempfile
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import io
import time

# Core OCR libraries
import pytesseract
import easyocr
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

# Google Vision OCR (highest accuracy)
from .google_vision_ocr import get_google_vision_ocr, VisionOCRResult

logger = logging.getLogger(__name__)

@dataclass
class OCRResult:
    """Structured OCR result with metadata"""
    text: str
    confidence: float
    engine: str
    processing_time: float
    language: str
    bounding_boxes: List[Dict] = None
    preprocessing_method: str = "standard"

class OCREngine:
    """
    Production OCR Engine with multiple backend support
    Priority: Google Vision API > EasyOCR > Tesseract
    """
    
    def __init__(self):
        self.google_vision_available = self._check_google_vision()
        self.tesseract_available = self._check_tesseract()
        self.easyocr_reader = None
        self.executor = ThreadPoolExecutor(max_workers=3)
        
        # Initialize EasyOCR reader
        try:
            self.easyocr_reader = easyocr.Reader(['en'], gpu=False)
            logger.info("EasyOCR initialized successfully")
        except Exception as e:
            logger.warning(f"EasyOCR initialization failed: {e}")
        
        # Tesseract configuration for different use cases
        self.tesseract_configs = {
            'default': '--oem 3 --psm 6',
            'mrz': '--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<',
            'single_line': '--oem 3 --psm 7',
            'single_word': '--oem 3 --psm 8',
            'sparse_text': '--oem 3 --psm 11',
            'dense_text': '--oem 3 --psm 6'
        }
        
        logger.info(f"OCR Engine initialized - Google Vision: {self.google_vision_available}, "
                   f"Tesseract: {self.tesseract_available}, EasyOCR: {bool(self.easyocr_reader)}")
    
    def _check_google_vision(self) -> bool:
        """Check if Google Vision API is available and configured"""
        try:
            api_key = os.getenv('GOOGLE_API_KEY')
            if api_key and google_vision_ocr:
                logger.info("Google Vision API available and configured")
                return True
            else:
                logger.warning("Google Vision API not configured")
                return False
        except Exception as e:
            logger.error(f"Google Vision API check failed: {e}")
            return False
    
    def _check_tesseract(self) -> bool:
        """Check if Tesseract is available"""
        try:
            version = pytesseract.get_tesseract_version()
            logger.info(f"Tesseract available: {version}")
            return True
        except Exception as e:
            logger.error(f"Tesseract not available: {e}")
            return False
    
    async def extract_text_from_image(self, 
                                    image_data: Union[str, bytes, np.ndarray],
                                    mode: str = "auto",
                                    language: str = "eng") -> OCRResult:
        """
        Extract text from image using best available engine
        Priority: Google Vision API > EasyOCR > Tesseract
        
        Args:
            image_data: Base64 string, bytes, or numpy array
            mode: OCR mode (auto, mrz, document, single_line, etc.)
            language: Language code (eng, por, etc.)
        
        Returns:
            OCRResult with text and metadata
        """
        start_time = time.time()
        
        try:
            # Try Google Vision API first (highest accuracy)
            if self.google_vision_available:
                try:
                    result = await self._extract_with_google_vision(image_data, mode, language)
                    if result.confidence > 0.5:  # Good confidence threshold
                        result.processing_time = time.time() - start_time
                        return result
                    else:
                        logger.warning("Google Vision low confidence, trying fallback")
                except Exception as e:
                    logger.warning(f"Google Vision failed, using fallback: {e}")
            
            # Fallback to traditional OCR engines
            # Convert input to PIL Image for traditional engines
            image = self._prepare_image(image_data)
            processed_image = self._preprocess_image(image, mode)
            
            # Choose best traditional engine
            if mode == "mrz" and self.tesseract_available:
                result = await self._extract_with_tesseract(processed_image, mode, language)
            elif self.easyocr_reader and mode in ["auto", "document"]:
                result = await self._extract_with_easyocr(processed_image, language)
            elif self.tesseract_available:
                result = await self._extract_with_tesseract(processed_image, mode, language)
            else:
                raise RuntimeError("No OCR engine available")
            
            # Update processing time
            result.processing_time = time.time() - start_time
            
            return result
            
        except Exception as e:
            logger.error(f"All OCR engines failed: {e}")
            return OCRResult(
                text="",
                confidence=0.0,
                engine="error",
                processing_time=time.time() - start_time,
                language=language,
                preprocessing_method="failed"
            )
    
    def _prepare_image(self, image_data: Union[str, bytes, np.ndarray]) -> Image.Image:
        """Convert various image formats to PIL Image"""
        if isinstance(image_data, str):
            # Base64 string
            try:
                # Remove data URL prefix if present
                if image_data.startswith('data:'):
                    image_data = image_data.split(',')[1]
                
                image_bytes = base64.b64decode(image_data)
                return Image.open(io.BytesIO(image_bytes))
            except Exception as e:
                raise ValueError(f"Invalid base64 image data: {e}")
        
        elif isinstance(image_data, bytes):
            # Raw bytes
            return Image.open(io.BytesIO(image_data))
        
        elif isinstance(image_data, np.ndarray):
            # NumPy array
            if len(image_data.shape) == 3:
                # Color image (BGR to RGB)
                image_data = cv2.cvtColor(image_data, cv2.COLOR_BGR2RGB)
            return Image.fromarray(image_data)
        
        else:
            raise ValueError(f"Unsupported image data type: {type(image_data)}")
    
    def _preprocess_image(self, image: Image.Image, mode: str) -> Image.Image:
        """
        Preprocess image for optimal OCR performance
        """
        try:
            # Convert to numpy for OpenCV operations
            img_array = np.array(image)
            
            # Resize if image is too large (max 2000px width)
            height, width = img_array.shape[:2]
            if width > 2000:
                scale = 2000 / width
                new_width = int(width * scale)
                new_height = int(height * scale)
                img_array = cv2.resize(img_array, (new_width, new_height), interpolation=cv2.INTER_AREA)
            
            # Convert to grayscale if needed
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # Mode-specific preprocessing
            if mode == "mrz":
                processed = self._preprocess_mrz(gray)
            elif mode in ["document", "auto"]:
                processed = self._preprocess_document(gray)
            else:
                processed = self._preprocess_general(gray)
            
            return Image.fromarray(processed)
            
        except Exception as e:
            logger.warning(f"Preprocessing failed, using original: {e}")
            return image
    
    def _preprocess_mrz(self, gray: np.ndarray) -> np.ndarray:
        """Specialized preprocessing for MRZ regions"""
        # Enhance contrast for MRZ text
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # Denoise
        denoised = cv2.bilateralFilter(enhanced, 9, 75, 75)
        
        # Morphological operations to clean up text
        kernel = np.ones((2,2), np.uint8)
        cleaned = cv2.morphologyEx(denoised, cv2.MORPH_CLOSE, kernel)
        
        # Sharpen text
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(cleaned, -1, kernel)
        
        return sharpened
    
    def _preprocess_document(self, gray: np.ndarray) -> np.ndarray:
        """General document preprocessing"""
        # Adaptive histogram equalization
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(enhanced, (1,1), 0)
        
        # Threshold to binary image
        _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return binary
    
    def _preprocess_general(self, gray: np.ndarray) -> np.ndarray:
        """General purpose preprocessing"""
        # Enhance contrast
        enhanced = cv2.equalizeHist(gray)
        
        # Light denoising
        denoised = cv2.medianBlur(enhanced, 3)
        
        return denoised
    
    async def _extract_with_tesseract(self, 
                                    image: Image.Image,
                                    mode: str,
                                    language: str) -> OCRResult:
        """Extract text using Tesseract OCR"""
        def _run_tesseract():
            try:
                # Get appropriate configuration
                config = self.tesseract_configs.get(mode, self.tesseract_configs['default'])
                
                # Extract text and confidence
                text = pytesseract.image_to_string(image, lang=language, config=config)
                
                # Get word-level confidence data
                data = pytesseract.image_to_data(image, lang=language, config=config, output_type=pytesseract.Output.DICT)
                
                # Calculate overall confidence
                confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                
                # Extract bounding boxes
                bounding_boxes = []
                for i in range(len(data['text'])):
                    if int(data['conf'][i]) > 0:
                        bounding_boxes.append({
                            'text': data['text'][i],
                            'confidence': int(data['conf'][i]),
                            'x': data['left'][i],
                            'y': data['top'][i],
                            'width': data['width'][i],
                            'height': data['height'][i]
                        })
                
                return OCRResult(
                    text=text.strip(),
                    confidence=avg_confidence / 100.0,  # Convert to 0-1 scale
                    engine="tesseract",
                    processing_time=0.0,  # Will be set by caller
                    language=language,
                    bounding_boxes=bounding_boxes,
                    preprocessing_method=mode
                )
                
            except Exception as e:
                logger.error(f"Tesseract extraction failed: {e}")
                raise
        
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _run_tesseract)
    
    async def _extract_with_easyocr(self, 
                                  image: Image.Image,
                                  language: str) -> OCRResult:
        """Extract text using EasyOCR"""
        def _run_easyocr():
            try:
                # Convert PIL to numpy array
                img_array = np.array(image)
                
                # Run EasyOCR
                results = self.easyocr_reader.readtext(img_array, detail=1)
                
                # Process results
                text_parts = []
                bounding_boxes = []
                confidences = []
                
                for (bbox, text, confidence) in results:
                    text_parts.append(text)
                    confidences.append(confidence)
                    
                    # Convert bounding box format
                    x_coords = [point[0] for point in bbox]
                    y_coords = [point[1] for point in bbox]
                    
                    bounding_boxes.append({
                        'text': text,
                        'confidence': confidence * 100,  # Convert to 0-100 scale
                        'x': int(min(x_coords)),
                        'y': int(min(y_coords)),
                        'width': int(max(x_coords) - min(x_coords)),
                        'height': int(max(y_coords) - min(y_coords))
                    })
                
                # Combine text and calculate average confidence
                combined_text = '\n'.join(text_parts)
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                
                return OCRResult(
                    text=combined_text,
                    confidence=avg_confidence,
                    engine="easyocr",
                    processing_time=0.0,  # Will be set by caller
                    language=language,
                    bounding_boxes=bounding_boxes,
                    preprocessing_method="easyocr_standard"
                )
                
            except Exception as e:
                logger.error(f"EasyOCR extraction failed: {e}")
                raise
        
        # Run in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _run_easyocr)
    
    async def _extract_with_google_vision(self, 
                                        image_data: Union[str, bytes, np.ndarray],
                                        mode: str,
                                        language: str) -> OCRResult:
        """Extract text using Google Cloud Vision API"""
        try:
            # Convert numpy array to bytes if needed
            if isinstance(image_data, np.ndarray):
                from PIL import Image
                pil_image = Image.fromarray(image_data)
                buffer = io.BytesIO()
                pil_image.save(buffer, format='PNG')
                image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            # Choose detection type based on mode
            detection_type = "DOCUMENT_TEXT_DETECTION" if mode in ["document", "mrz"] else "TEXT_DETECTION"
            
            # Set language hints
            language_hints = []
            if language == "eng":
                language_hints = ["en"]
            elif language == "por":
                language_hints = ["pt"]
            
            # Call Google Vision API
            vision_result = await google_vision_ocr.detect_text(
                image_data,
                detection_type=detection_type,
                language_hints=language_hints
            )
            
            # Convert to OCRResult format
            return OCRResult(
                text=vision_result.text,
                confidence=vision_result.confidence,
                engine="google_vision",
                processing_time=vision_result.processing_time,
                language=vision_result.language,
                bounding_boxes=vision_result.bounding_boxes,
                preprocessing_method=f"google_vision_{mode}"
            )
            
        except Exception as e:
            logger.error(f"Google Vision extraction failed: {e}")
            # Return low confidence result to trigger fallback
            return OCRResult(
                text="",
                confidence=0.0,
                engine="google_vision_failed",
                processing_time=0.0,
                language=language,
                preprocessing_method="failed"
            )
    
    async def extract_mrz_from_passport(self, image_data: Union[str, bytes]) -> Dict[str, Any]:
        """
        Specialized MRZ extraction with Google Vision API priority
        """
        try:
            # Try Google Vision first for highest accuracy
            if self.google_vision_available:
                try:
                    vision_result = await google_vision_ocr.extract_mrz_from_passport(image_data)
                    if vision_result['confidence'] > 0.6:  # Good confidence
                        logger.info(f"Google Vision MRZ success: {vision_result['confidence']:.2f} confidence")
                        return vision_result
                    else:
                        logger.warning("Google Vision MRZ low confidence, trying Tesseract")
                except Exception as e:
                    logger.warning(f"Google Vision MRZ failed, using Tesseract: {e}")
            
            # Fallback to Tesseract MRZ extraction
            if self.tesseract_available:
                # Prepare image
                image = self._prepare_image(image_data)
                img_array = np.array(image)
                
                # Convert to grayscale
                if len(img_array.shape) == 3:
                    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
                else:
                    gray = img_array
                
                # Detect MRZ region (bottom portion of passport)
                height, width = gray.shape
                mrz_region = gray[int(height * 0.65):, :]  # Bottom 35% of image
                
                # Preprocess MRZ region
                processed_mrz = self._preprocess_mrz(mrz_region)
                
                # Extract text using Tesseract with MRZ config
                mrz_text = pytesseract.image_to_string(
                    processed_mrz,
                    lang='eng',
                    config=self.tesseract_configs['mrz']
                )
                
                # Clean and validate MRZ format
                mrz_lines = self._clean_mrz_text(mrz_text)
                
                return {
                    'mrz_text': mrz_lines,
                    'region_detected': True,
                    'confidence': self._estimate_mrz_confidence(mrz_lines),
                    'method': 'tesseract_specialized'
                }
            else:
                raise RuntimeError("No MRZ extraction engine available")
            
        except Exception as e:
            logger.error(f"MRZ extraction failed: {e}")
            return {
                'mrz_text': "",
                'region_detected': False,
                'confidence': 0.0,
                'method': 'failed',
                'error': str(e)
            }
    
    def _clean_mrz_text(self, raw_text: str) -> str:
        """Clean and format MRZ text to standard format"""
        if not raw_text:
            return ""
        
        # Split into lines and clean
        lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
        
        # Filter to potential MRZ lines (should be around 44 characters)
        mrz_lines = []
        for line in lines:
            # Remove spaces and special characters except < 
            cleaned = re.sub(r'[^A-Z0-9<]', '', line.upper())
            
            # Check if line looks like MRZ (length between 40-44 chars)
            if 40 <= len(cleaned) <= 44:
                # Ensure exactly 44 characters
                if len(cleaned) < 44:
                    cleaned = cleaned.ljust(44, '<')
                elif len(cleaned) > 44:
                    cleaned = cleaned[:44]
                mrz_lines.append(cleaned)
        
        # MRZ should have exactly 2 lines
        if len(mrz_lines) >= 2:
            return '\n'.join(mrz_lines[:2])
        elif len(mrz_lines) == 1:
            # Try to find second line in remaining text
            remaining_lines = [line for line in lines if line not in mrz_lines]
            for line in remaining_lines:
                cleaned = re.sub(r'[^A-Z0-9<]', '', line.upper())
                if 35 <= len(cleaned) <= 50:  # More lenient for second line
                    if len(cleaned) < 44:
                        cleaned = cleaned.ljust(44, '<')
                    elif len(cleaned) > 44:
                        cleaned = cleaned[:44]
                    mrz_lines.append(cleaned)
                    break
        
        return '\n'.join(mrz_lines) if len(mrz_lines) >= 2 else ""
    
    def _estimate_mrz_confidence(self, mrz_text: str) -> float:
        """Estimate confidence based on MRZ format compliance"""
        if not mrz_text:
            return 0.0
        
        lines = mrz_text.split('\n')
        if len(lines) != 2:
            return 0.2
        
        confidence = 0.5  # Base confidence
        
        # Check first line format (should start with P<)
        if lines[0].startswith('P<'):
            confidence += 0.2
        
        # Check line lengths (should be exactly 44)
        if all(len(line) == 44 for line in lines):
            confidence += 0.2
        
        # Check character compliance (only A-Z, 0-9, <)
        valid_chars = re.match(r'^[A-Z0-9<\n]+$', mrz_text)
        if valid_chars:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def get_engine_status(self) -> Dict[str, Any]:
        """Get status of available OCR engines"""
        return {
            'google_vision_available': self.google_vision_available,
            'tesseract_available': self.tesseract_available,
            'easyocr_available': self.easyocr_reader is not None,
            'engine_priority': ['Google Vision API', 'EasyOCR', 'Tesseract'],
            'tesseract_version': pytesseract.get_tesseract_version() if self.tesseract_available else None,
            'supported_modes': list(self.tesseract_configs.keys()) + ['google_vision_document', 'google_vision_text'],
            'supported_languages': ['eng', 'por', 'es', 'auto'],
            'google_api_key_configured': bool(os.getenv('GOOGLE_API_KEY')),
            'recommended_engine': 'Google Vision API' if self.google_vision_available else ('EasyOCR' if self.easyocr_reader else 'Tesseract')
        }

# Global instance
real_ocr_engine = OCREngine()