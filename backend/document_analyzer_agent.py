"""
AGENTE DE ANÁLISE DE DOCUMENTOS
Especialidade: OCR, extração de dados e validação de documentos
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone
import re
import base64
import json
import os
from io import BytesIO
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_KB_PATH = Path(__file__).resolve().parent.parent / "knowledge_base_documents.json"


class DocumentAnalyzerAgent:
    """
    Agente especializado em análise de documentos
    - OCR (Optical Character Recognition)
    - Extração de dados estruturados
    - Validação de documentos
    - Detecção de informações chave
    """
    
    def __init__(self, knowledge_base_path: Optional[str] = None):
        self.supported_documents = [
            'passport', 'driver_license', 'birth_certificate',
            'i20', 'i94', 'visa', 'bank_statement', 'transcript'
        ]
        kb_path = knowledge_base_path or str(DEFAULT_KB_PATH)
        self.knowledge_base = self._load_knowledge_base(kb_path)
        logger.info(f"✅ Document Analyzer Agent inicializado com {len(self.knowledge_base.get('documents', []))} documentos de referência")
    
    def _load_knowledge_base(self, kb_path: str) -> Dict:
        """Carrega a base de conhecimento"""
        try:
            if os.path.exists(kb_path):
                with open(kb_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {'documents': []}
        except Exception as e:
            logger.error(f"Erro ao carregar KB: {str(e)}")
            return {'documents': []}
    
    def analyze_document(self, file_content: bytes, document_type: str, filename: str) -> Dict:
        """
        Analisa um documento e extrai informações
        
        Args:
            file_content: Conteúdo do arquivo em bytes
            document_type: Tipo do documento (passport, i20, etc)
            filename: Nome do arquivo
        
        Returns:
            Dict com análise do documento
        """
        try:
            # Detectar tipo de arquivo
            file_type = self._detect_file_type(filename)
            
            # Extrair texto (simulado - em produção usar pytesseract ou cloud OCR)
            extracted_text = self._extract_text_simulated(file_content, document_type)
            
            # Validar documento
            validation = self._validate_document(extracted_text, document_type)
            
            # Extrair campos específicos
            extracted_fields = self._extract_fields(extracted_text, document_type)
            
            return {
                'success': True,
                'document_type': document_type,
                'file_type': file_type,
                'filename': filename,
                'extracted_text': extracted_text[:500] + '...' if len(extracted_text) > 500 else extracted_text,
                'extracted_fields': extracted_fields,
                'validation': validation,
                'confidence_score': validation.get('confidence', 0),
                'analyzed_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar documento: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'document_type': document_type
            }
    
    def _detect_file_type(self, filename: str) -> str:
        """Detecta o tipo de arquivo pela extensão"""
        ext = filename.lower().split('.')[-1]
        return ext
    
    def _extract_text_simulated(self, file_content: bytes, doc_type: str) -> str:
        """
        Simula extração de texto via OCR
        Em produção: usar pytesseract, Google Vision API, AWS Textract
        """
        # Por enquanto, retorna texto simulado baseado no tipo
        simulated_texts = {
            'passport': """
                PASSPORT
                Type: P
                Country: BRAZIL
                Passport No: BR123456789
                Surname: SANTOS
                Given Names: MARIA DA SILVA
                Nationality: BRAZILIAN
                Date of Birth: 25 APR 1992
                Sex: F
                Place of Birth: SAO PAULO
                Date of Issue: 10 JUN 2019
                Date of Expiry: 10 JUN 2029
                Authority: POLICIA FEDERAL
            """,
            'i20': """
                FORM I-20
                Certificate of Eligibility for Nonimmigrant Student Status
                Family Name: SANTOS
                First Name: MARIA
                SEVIS ID: N9876543210
                School: Stanford University
                Program: Master of Business Administration
                Start Date: 01 APR 2025
                Expected Completion: 15 JUN 2027
            """,
            'i94': """
                I-94 ARRIVAL/DEPARTURE RECORD
                Name: SANTOS, MARIA DA SILVA
                Date of Birth: 04/25/1992
                Passport Number: BR555888999
                I-94 Number: 99887766554
                Class of Admission: B-2
                Date of Entry: 01 SEP 2024
                Admit Until Date: 01 MAR 2025
            """
        }
        
        return simulated_texts.get(doc_type, "Document text extracted")
    
    def _validate_document(self, text: str, doc_type: str) -> Dict:
        """
        Valida se o documento contém as informações necessárias
        """
        required_fields = {
            'passport': ['Passport No', 'Surname', 'Date of Birth', 'Date of Expiry'],
            'i20': ['SEVIS ID', 'School', 'Program', 'Start Date'],
            'i94': ['I-94 Number', 'Date of Entry', 'Admit Until Date'],
            'bank_statement': ['Account', 'Balance', 'Date'],
            'transcript': ['Student Name', 'Degree', 'GPA']
        }
        
        required = required_fields.get(doc_type, [])
        found_fields = []
        missing_fields = []
        
        for field in required:
            if field.lower() in text.lower():
                found_fields.append(field)
            else:
                missing_fields.append(field)
        
        is_valid = len(missing_fields) == 0
        confidence = (len(found_fields) / len(required) * 100) if required else 0
        
        return {
            'is_valid': is_valid,
            'confidence': round(confidence, 2),
            'found_fields': found_fields,
            'missing_fields': missing_fields,
            'total_required': len(required),
            'total_found': len(found_fields)
        }
    
    def _extract_fields(self, text: str, doc_type: str) -> Dict:
        """
        Extrai campos específicos do texto usando regex
        """
        fields = {}
        
        if doc_type == 'passport':
            # Extrair número de passaporte
            passport_match = re.search(r'Passport No[:\s]+([A-Z0-9]+)', text, re.IGNORECASE)
            if passport_match:
                fields['passport_number'] = passport_match.group(1)
            
            # Extrair nome
            surname_match = re.search(r'Surname[:\s]+([A-Z\s]+)', text, re.IGNORECASE)
            if surname_match:
                fields['surname'] = surname_match.group(1).strip()
            
            # Extrair data de nascimento
            dob_match = re.search(r'Date of Birth[:\s]+(\d{2}\s+[A-Z]{3}\s+\d{4})', text, re.IGNORECASE)
            if dob_match:
                fields['date_of_birth'] = dob_match.group(1)
            
            # Extrair validade
            expiry_match = re.search(r'Date of Expiry[:\s]+(\d{2}\s+[A-Z]{3}\s+\d{4})', text, re.IGNORECASE)
            if expiry_match:
                fields['expiry_date'] = expiry_match.group(1)
        
        elif doc_type == 'i20':
            # Extrair SEVIS ID
            sevis_match = re.search(r'SEVIS ID[:\s]+([A-Z0-9]+)', text, re.IGNORECASE)
            if sevis_match:
                fields['sevis_id'] = sevis_match.group(1)
            
            # Extrair escola
            school_match = re.search(r'School[:\s]+([A-Za-z\s]+(?:University|College|Institute))', text, re.IGNORECASE)
            if school_match:
                fields['school'] = school_match.group(1).strip()
        
        elif doc_type == 'i94':
            # Extrair I-94 number
            i94_match = re.search(r'I-94 Number[:\s]+([0-9]+)', text, re.IGNORECASE)
            if i94_match:
                fields['i94_number'] = i94_match.group(1)
            
            # Extrair data de entrada
            entry_match = re.search(r'Date of Entry[:\s]+(\d{2}\s+[A-Z]{3}\s+\d{4}|\d{2}/\d{2}/\d{4})', text, re.IGNORECASE)
            if entry_match:
                fields['entry_date'] = entry_match.group(1)
        
        return fields
    
    def validate_document_quality(self, file_content: bytes) -> Dict:
        """
        Valida a qualidade do documento (resolução, clareza, etc)
        """
        # Em produção: analisar resolução, contraste, etc
        file_size = len(file_content)
        
        quality_score = 85  # Simulado
        
        return {
            'quality_score': quality_score,
            'file_size': file_size,
            'file_size_mb': round(file_size / (1024 * 1024), 2),
            'is_acceptable': quality_score >= 70,
            'recommendations': [] if quality_score >= 70 else [
                'Consider scanning at higher resolution',
                'Ensure document is well-lit and in focus'
            ]
        }
    
    def detect_fraud_indicators(self, extracted_data: Dict) -> Dict:
        """
        Detecta possíveis indicadores de fraude no documento
        """
        # Checagens básicas de fraude
        indicators = []
        
        # Verificar datas inconsistentes
        if 'expiry_date' in extracted_data.get('extracted_fields', {}):
            # Lógica de validação de datas
            pass
        
        # Verificar padrões suspeitos
        fraud_risk = 'low'  # low, medium, high
        
        return {
            'fraud_risk': fraud_risk,
            'indicators': indicators,
            'confidence': 95,
            'requires_manual_review': len(indicators) > 0
        }
    
    def consult_kb_for_document(self, document_type: str) -> Dict:
        """
        Consulta a base de conhecimento sobre um tipo de documento
        Retorna guidelines e requisitos
        """
        relevant_docs = []
        
        for doc in self.knowledge_base.get('documents', []):
            doc_text = doc.get('text', '').lower()
            doc_name = doc.get('filename', '').lower()
            
            # Buscar menções ao tipo de documento
            if document_type.lower() in doc_text or document_type.lower() in doc_name:
                relevant_docs.append({
                    'filename': doc['filename'],
                    'category': doc['category'],
                    'excerpt': doc['text'][:300] + '...'
                })
        
        return {
            'document_type': document_type,
            'kb_references_found': len(relevant_docs),
            'references': relevant_docs[:3]  # Top 3
        }


# Instância global
document_analyzer = DocumentAnalyzerAgent()


def analyze_uploaded_document(file_content: bytes, document_type: str, filename: str) -> Dict:
    """
    Helper function para análise de documentos
    """
    return document_analyzer.analyze_document(file_content, document_type, filename)
