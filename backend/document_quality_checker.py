"""
Document Quality Checker - Fase 1
Análise básica de qualidade de documentos conforme especificação técnica
"""
import os
import mimetypes
from PIL import Image, ImageStat
import PyPDF2
from typing import Dict, Any, List
import logging
import io

logger = logging.getLogger(__name__)

class DocumentQualityChecker:
    """
    Classe para análise de qualidade básica de documentos
    """
    
    def __init__(self):
        self.supported_formats = {
            'application/pdf': ['.pdf'],
            'image/jpeg': ['.jpg', '.jpeg'],
            'image/png': ['.png'],
            'image/tiff': ['.tiff', '.tif']
        }
    
    def analyze_quality(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Analisa qualidade básica do documento
        """
        try:
            result = {
                "status": "ok",
                "checks": {},
                "warnings": [],
                "errors": [],
                "metadata": {}
            }
            
            # 1. Análise de tamanho de arquivo
            file_size_check = self._check_file_size(file_content, filename)
            result["checks"]["file_size"] = file_size_check
            
            # 2. Análise de formato
            format_check = self._check_file_format(file_content, filename)
            result["checks"]["format"] = format_check
            
            # 3. Análise específica por tipo
            if format_check["mime_type"] == "application/pdf":
                pdf_check = self._check_pdf_quality(file_content)
                result["checks"]["pdf_specific"] = pdf_check
            elif format_check["mime_type"].startswith("image/"):
                image_check = self._check_image_quality(file_content)
                result["checks"]["image_specific"] = image_check
            
            # 4. Determinar status geral
            result["status"] = self._determine_overall_status(result["checks"])
            
            return result
            
        except Exception as e:
            logger.error(f"Error in quality analysis: {e}")
            return {
                "status": "fail",
                "checks": {},
                "warnings": [],
                "errors": [f"Erro na análise de qualidade: {str(e)}"],
                "metadata": {}
            }
    
    def _check_file_size(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Verifica tamanho do arquivo
        """
        size_bytes = len(file_content)
        size_kb = size_bytes / 1024
        size_mb = size_kb / 1024
        
        # Limites padrão (podem ser customizados por política)
        min_size_kb = 10  # 10KB mínimo
        max_size_mb = 20  # 20MB máximo
        
        status = "pass"
        message = f"Arquivo: {size_kb:.1f}KB ({size_mb:.1f}MB)"
        
        if size_kb < min_size_kb:
            status = "fail"
            message = f"Arquivo muito pequeno: {size_kb:.1f}KB (mínimo: {min_size_kb}KB)"
        elif size_mb > max_size_mb:
            status = "fail"
            message = f"Arquivo muito grande: {size_mb:.1f}MB (máximo: {max_size_mb}MB)"
        
        return {
            "status": status,
            "message": message,
            "size_bytes": size_bytes,
            "size_kb": size_kb,
            "size_mb": size_mb
        }
    
    def _check_file_format(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Verifica formato do arquivo
        """
        # Detectar MIME type
        mime_type, _ = mimetypes.guess_type(filename)
        
        # Verificar magic bytes para confirmação
        magic_bytes_check = self._check_magic_bytes(file_content)
        
        supported = mime_type in self.supported_formats
        
        status = "pass" if supported else "fail"
        message = f"Formato: {mime_type}" if supported else f"Formato não suportado: {mime_type}"
        
        return {
            "status": status,
            "message": message,
            "mime_type": mime_type,
            "supported": supported,
            "magic_bytes_detected": magic_bytes_check
        }
    
    def _check_magic_bytes(self, file_content: bytes) -> str:
        """
        Detecta tipo de arquivo pelos magic bytes
        """
        if file_content.startswith(b'%PDF'):
            return "pdf"
        elif file_content.startswith(b'\xff\xd8\xff'):
            return "jpeg"
        elif file_content.startswith(b'\x89PNG\r\n\x1a\n'):
            return "png"
        elif file_content.startswith(b'II*') or file_content.startswith(b'MM\x00*'):
            return "tiff"
        else:
            return "unknown"
    
    def _check_pdf_quality(self, file_content: bytes) -> Dict[str, Any]:
        """
        Análise específica para PDFs
        """
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            
            num_pages = len(pdf_reader.pages)
            is_encrypted = pdf_reader.is_encrypted
            
            status = "pass"
            warnings = []
            
            if is_encrypted:
                status = "alert"
                warnings.append("PDF está criptografado")
            
            if num_pages > 20:
                status = "alert"
                warnings.append(f"PDF tem muitas páginas ({num_pages})")
            
            return {
                "status": status,
                "message": f"PDF válido com {num_pages} página(s)",
                "pages": num_pages,
                "encrypted": is_encrypted,
                "warnings": warnings
            }
            
        except Exception as e:
            return {
                "status": "fail",
                "message": f"PDF corrompido ou inválido: {str(e)}",
                "pages": 0,
                "encrypted": False,
                "warnings": []
            }
    
    def _check_image_quality(self, file_content: bytes) -> Dict[str, Any]:
        """
        Análise específica para imagens
        """
        try:
            image = Image.open(io.BytesIO(file_content))
            
            width, height = image.size
            mode = image.mode
            
            # Calcular DPI estimado (assumindo tamanho padrão de documento)
            estimated_dpi = min(width, height) / 8.5 if min(width, height) > 0 else 0
            
            # Análise de qualidade básica
            status = "pass"
            warnings = []
            
            # Verificar resolução mínima
            if estimated_dpi < 150:
                status = "alert"
                warnings.append(f"Resolução baixa (est. {estimated_dpi:.0f} DPI)")
            
            # Verificar tamanho mínimo
            if width < 800 or height < 600:
                status = "alert"
                warnings.append(f"Dimensões pequenas ({width}x{height})")
            
            # Análise de blur básica (usando variância)
            if mode in ['RGB', 'L']:
                blur_score = self._estimate_blur(image)
                if blur_score < 100:
                    status = "alert"
                    warnings.append(f"Imagem pode estar desfocada (score: {blur_score:.1f})")
            else:
                blur_score = None
            
            return {
                "status": status,
                "message": f"Imagem {width}x{height}, {mode}",
                "width": width,
                "height": height,
                "mode": mode,
                "estimated_dpi": estimated_dpi,
                "blur_score": blur_score,
                "warnings": warnings
            }
            
        except Exception as e:
            return {
                "status": "fail",
                "message": f"Imagem corrompida ou inválida: {str(e)}",
                "width": 0,
                "height": 0,
                "mode": None,
                "estimated_dpi": 0,
                "blur_score": None,
                "warnings": []
            }
    
    def _estimate_blur(self, image: Image) -> float:
        """
        Estimativa básica de blur usando variância dos pixels
        """
        try:
            # Converter para escala de cinza se necessário
            if image.mode != 'L':
                image = image.convert('L')
            
            # Calcular variância dos pixels como indicador de nitidez
            stat = ImageStat.Stat(image)
            return stat.var[0]
            
        except Exception:
            return 0.0
    
    def _determine_overall_status(self, checks: Dict[str, Any]) -> str:
        """
        Determina status geral baseado nas verificações
        """
        statuses = []
        for check_name, check_result in checks.items():
            if isinstance(check_result, dict) and "status" in check_result:
                statuses.append(check_result["status"])
        
        if "fail" in statuses:
            return "fail"
        elif "alert" in statuses:
            return "alert"
        else:
            return "ok"
    
    def get_quality_requirements(self, doc_type: str) -> Dict[str, Any]:
        """
        Retorna requisitos de qualidade para um tipo específico de documento
        Pode ser expandido para usar as políticas YAML
        """
        # Requisitos padrão (podem ser customizados por doc_type)
        return {
            "min_dpi": 150,
            "max_skew_deg": 5,
            "min_blur_var": 100,
            "min_file_size_kb": 20,
            "max_file_size_mb": 15,
            "supported_formats": ["pdf", "jpg", "jpeg", "png"]
        }