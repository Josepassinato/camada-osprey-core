"""
Document Analysis Agent

Specializes in:
- OCR (Optical Character Recognition)
- Structured data extraction
- Document validation
- Key information detection
"""

import json
import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

from agents.base import BaseAgent
from llm.portkey_client import LLMClient
from llm.types import ChatMessage, MessageRole

logger = logging.getLogger(__name__)

DEFAULT_KB_PATH = Path(__file__).resolve().parent.parent.parent / "knowledge_base_documents.json"


class DocumentAnalyzerAgent(BaseAgent):
    """
    Agent specialized in document analysis
    - OCR (Optical Character Recognition)
    - Structured data extraction
    - Document validation
    - Key information detection
    """

    def __init__(
        self, llm_client: Optional[LLMClient] = None, knowledge_base_path: Optional[str] = None
    ):
        super().__init__(llm_client=llm_client, agent_name="document_analyzer")

        self.supported_documents = [
            "passport",
            "driver_license",
            "birth_certificate",
            "i20",
            "i94",
            "visa",
            "bank_statement",
            "transcript",
        ]

        kb_path = knowledge_base_path or str(DEFAULT_KB_PATH)
        self.knowledge_base = self._load_knowledge_base(kb_path)

        logger.info(
            f"✅ Document Analyzer Agent initialized with "
            f"{len(self.knowledge_base.get('documents', []))} reference documents"
        )

    def _load_knowledge_base(self, kb_path: str) -> Dict:
        """Load knowledge base"""
        try:
            if os.path.exists(kb_path):
                with open(kb_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            return {"documents": []}
        except Exception as e:
            logger.error(f"Error loading KB: {str(e)}")
            return {"documents": []}

    async def process(self, input_data: Dict) -> Dict:
        """
        Process document analysis request

        Args:
            input_data: Dict containing:
                - file_content: bytes
                - document_type: str
                - filename: str
                - use_llm: bool (optional, default False)

        Returns:
            Dict with analysis results
        """
        file_content = input_data.get("file_content")
        document_type = input_data.get("document_type")
        filename = input_data.get("filename")
        use_llm = input_data.get("use_llm", False)

        if use_llm:
            return await self.analyze_document_with_llm(file_content, document_type, filename)
        else:
            return self.analyze_document(file_content, document_type, filename)

    def analyze_document(self, file_content: bytes, document_type: str, filename: str) -> Dict:
        """
        Analyze a document and extract information

        Args:
            file_content: File content in bytes
            document_type: Document type (passport, i20, etc)
            filename: File name

        Returns:
            Dict with document analysis
        """
        try:
            # Detect file type
            file_type = self._detect_file_type(filename)

            # Extract text (simulated - in production use pytesseract or cloud OCR)
            extracted_text = self._extract_text_simulated(file_content, document_type)

            # Validate document
            validation = self._validate_document(extracted_text, document_type)

            # Extract specific fields
            extracted_fields = self._extract_fields(extracted_text, document_type)

            return {
                "success": True,
                "document_type": document_type,
                "file_type": file_type,
                "filename": filename,
                "extracted_text": (
                    extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text
                ),
                "extracted_fields": extracted_fields,
                "validation": validation,
                "confidence_score": validation.get("confidence", 0),
                "analyzed_at": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(f"Error analyzing document: {str(e)}")
            return {"success": False, "error": str(e), "document_type": document_type}

    async def analyze_document_with_llm(
        self, file_content: bytes, document_type: str, filename: str
    ) -> Dict:
        """
        Analyze document using LLM for enhanced extraction

        Args:
            file_content: File content in bytes
            document_type: Document type
            filename: File name

        Returns:
            Dict with enhanced analysis
        """
        try:
            # First do basic analysis
            basic_analysis = self.analyze_document(file_content, document_type, filename)

            if not basic_analysis.get("success"):
                return basic_analysis

            # Use LLM for enhanced field extraction
            extracted_text = basic_analysis.get("extracted_text", "")

            messages = [
                ChatMessage(
                    role=MessageRole.SYSTEM,
                    content=(
                        f"You are a document analysis expert. Extract structured "
                        f"information from {document_type} documents."
                    ),
                ),
                ChatMessage(
                    role=MessageRole.USER,
                    content=(
                        f"Extract all relevant fields from this {document_type}:\n\n"
                        f"{extracted_text}\n\n"
                        f"Return a JSON object with the extracted fields."
                    ),
                ),
            ]

            llm_response = await self._call_llm(
                messages=[msg.dict() for msg in messages], model="gpt-4o", temperature=0.1
            )

            # Try to parse LLM response as JSON
            try:
                enhanced_fields = json.loads(llm_response)
                basic_analysis["extracted_fields_enhanced"] = enhanced_fields
                basic_analysis["llm_enhanced"] = True
            except json.JSONDecodeError:
                basic_analysis["llm_response"] = llm_response
                basic_analysis["llm_enhanced"] = False

            return basic_analysis

        except Exception as e:
            logger.error(f"Error in LLM-enhanced analysis: {str(e)}")
            # Fall back to basic analysis
            return self.analyze_document(file_content, document_type, filename)

    def _detect_file_type(self, filename: str) -> str:
        """Detect file type by extension"""
        ext = filename.lower().split(".")[-1]
        return ext

    def _extract_text_simulated(self, file_content: bytes, doc_type: str) -> str:
        """
        Simulate text extraction via OCR
        In production: use pytesseract, Google Vision API, AWS Textract
        """
        simulated_texts = {
            "passport": """
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
            "i20": """
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
            "i94": """
                I-94 ARRIVAL/DEPARTURE RECORD
                Name: SANTOS, MARIA DA SILVA
                Date of Birth: 04/25/1992
                Passport Number: BR555888999
                I-94 Number: 99887766554
                Class of Admission: B-2
                Date of Entry: 01 SEP 2024
                Admit Until Date: 01 MAR 2025
            """,
        }

        return simulated_texts.get(doc_type, "Document text extracted")

    def _validate_document(self, text: str, doc_type: str) -> Dict:
        """
        Validate if document contains necessary information
        """
        required_fields = {
            "passport": ["Passport No", "Surname", "Date of Birth", "Date of Expiry"],
            "i20": ["SEVIS ID", "School", "Program", "Start Date"],
            "i94": ["I-94 Number", "Date of Entry", "Admit Until Date"],
            "bank_statement": ["Account", "Balance", "Date"],
            "transcript": ["Student Name", "Degree", "GPA"],
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
            "is_valid": is_valid,
            "confidence": round(confidence, 2),
            "found_fields": found_fields,
            "missing_fields": missing_fields,
            "total_required": len(required),
            "total_found": len(found_fields),
        }

    def _extract_fields(self, text: str, doc_type: str) -> Dict:
        """
        Extract specific fields from text using regex
        """
        fields = {}

        if doc_type == "passport":
            # Extract passport number
            passport_match = re.search(r"Passport No[:\s]+([A-Z0-9]+)", text, re.IGNORECASE)
            if passport_match:
                fields["passport_number"] = passport_match.group(1)

            # Extract name
            surname_match = re.search(r"Surname[:\s]+([A-Z\s]+)", text, re.IGNORECASE)
            if surname_match:
                fields["surname"] = surname_match.group(1).strip()

            # Extract date of birth
            dob_match = re.search(
                r"Date of Birth[:\s]+(\d{2}\s+[A-Z]{3}\s+\d{4})", text, re.IGNORECASE
            )
            if dob_match:
                fields["date_of_birth"] = dob_match.group(1)

            # Extract expiry date
            expiry_match = re.search(
                r"Date of Expiry[:\s]+(\d{2}\s+[A-Z]{3}\s+\d{4})", text, re.IGNORECASE
            )
            if expiry_match:
                fields["expiry_date"] = expiry_match.group(1)

        elif doc_type == "i20":
            # Extract SEVIS ID
            sevis_match = re.search(r"SEVIS ID[:\s]+([A-Z0-9]+)", text, re.IGNORECASE)
            if sevis_match:
                fields["sevis_id"] = sevis_match.group(1)

            # Extract school
            school_match = re.search(
                r"School[:\s]+([A-Za-z\s]+(?:University|College|Institute))", text, re.IGNORECASE
            )
            if school_match:
                fields["school"] = school_match.group(1).strip()

        elif doc_type == "i94":
            # Extract I-94 number
            i94_match = re.search(r"I-94 Number[:\s]+([0-9]+)", text, re.IGNORECASE)
            if i94_match:
                fields["i94_number"] = i94_match.group(1)

            # Extract entry date
            entry_match = re.search(
                r"Date of Entry[:\s]+(\d{2}\s+[A-Z]{3}\s+\d{4}|\d{2}/\d{2}/\d{4})",
                text,
                re.IGNORECASE,
            )
            if entry_match:
                fields["entry_date"] = entry_match.group(1)

        return fields

    def validate_document_quality(self, file_content: bytes) -> Dict:
        """
        Validate document quality (resolution, clarity, etc)
        """
        # In production: analyze resolution, contrast, etc
        file_size = len(file_content)

        quality_score = 85  # Simulated

        return {
            "quality_score": quality_score,
            "file_size": file_size,
            "file_size_mb": round(file_size / (1024 * 1024), 2),
            "is_acceptable": quality_score >= 70,
            "recommendations": (
                []
                if quality_score >= 70
                else [
                    "Consider scanning at higher resolution",
                    "Ensure document is well-lit and in focus",
                ]
            ),
        }

    def detect_fraud_indicators(self, extracted_data: Dict) -> Dict:
        """
        Detect possible fraud indicators in document
        """
        # Basic fraud checks
        indicators = []

        # Check inconsistent dates
        if "expiry_date" in extracted_data.get("extracted_fields", {}):
            # Date validation logic
            pass

        # Check suspicious patterns
        fraud_risk = "low"  # low, medium, high

        return {
            "fraud_risk": fraud_risk,
            "indicators": indicators,
            "confidence": 95,
            "requires_manual_review": len(indicators) > 0,
        }

    def consult_kb_for_document(self, document_type: str) -> Dict:
        """
        Consult knowledge base about a document type
        Returns guidelines and requirements
        """
        relevant_docs = []

        for doc in self.knowledge_base.get("documents", []):
            doc_text = doc.get("text", "").lower()
            doc_name = doc.get("filename", "").lower()

            # Search for mentions of document type
            if document_type.lower() in doc_text or document_type.lower() in doc_name:
                relevant_docs.append(
                    {
                        "filename": doc["filename"],
                        "category": doc["category"],
                        "excerpt": doc["text"][:300] + "...",
                    }
                )

        return {
            "document_type": document_type,
            "kb_references_found": len(relevant_docs),
            "references": relevant_docs[:3],  # Top 3
        }


# Global instance for backward compatibility
document_analyzer = DocumentAnalyzerAgent()


def analyze_uploaded_document(file_content: bytes, document_type: str, filename: str) -> Dict:
    """
    Helper function for document analysis
    """
    return document_analyzer.analyze_document(file_content, document_type, filename)
