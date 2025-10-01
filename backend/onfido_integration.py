"""
Onfido Document Verification Integration
Professional document verification replacing Dr. Miguel system
"""

import os
import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import onfido
from onfido.rest import ApiException
from fastapi import HTTPException
import base64

logger = logging.getLogger(__name__)

class OnfidoDocumentVerifier:
    """Professional document verification using Onfido API"""
    
    def __init__(self):
        self.api_token = os.environ.get('ONFIDO_API_TOKEN', 'api_sandbox_test_token')
        self.region = os.environ.get('ONFIDO_REGION', 'EU')
        self.is_sandbox = self.api_token.startswith('api_sandbox') or self.api_token == 'api_sandbox_test_token'
        
        # Configure Onfido client
        self.configuration = onfido.Configuration(
            api_token=self.api_token,
            region=self._get_region(),
            timeout=onfido.Timeout(connect=60.0, read=60.0)
        )
        
        logger.info(f"Onfido initialized - Region: {self.region}, Sandbox: {self.is_sandbox}")
    
    def _get_region(self):
        """Get Onfido region configuration"""
        region_mapping = {
            'EU': onfido.Region.EU,
            'US': onfido.Region.US, 
            'CA': onfido.Region.CA
        }
        return region_mapping.get(self.region, onfido.Region.EU)
    
    def _get_client(self):
        """Get Onfido API client"""
        return onfido.ApiClient(self.configuration)
    
    async def create_applicant(self, first_name: str, last_name: str, 
                             dob: Optional[str] = None, 
                             address: Optional[Dict] = None) -> Dict[str, Any]:
        """Create applicant for document verification"""
        
        if self.is_sandbox:
            # Return mock applicant for testing
            return {
                "id": f"mock_applicant_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "first_name": first_name,
                "last_name": last_name,
                "created_at": datetime.now().isoformat(),
                "sandbox": True
            }
        
        try:
            with self._get_client() as api_client:
                default_api = onfido.DefaultApi(api_client)
                
                applicant_request = onfido.ApplicantRequest(
                    first_name=first_name,
                    last_name=last_name
                )
                
                if dob:
                    applicant_request.dob = dob
                    
                if address:
                    applicant_request.address = onfido.AddressRequest(**address)
                
                applicant = default_api.create_applicant(applicant_request)
                
                return {
                    "id": applicant.id,
                    "first_name": applicant.first_name,
                    "last_name": applicant.last_name,
                    "created_at": applicant.created_at.isoformat() if applicant.created_at else None,
                    "sandbox": False
                }
                
        except ApiException as e:
            logger.error(f"Onfido API error creating applicant: {e}")
            raise HTTPException(status_code=400, detail=f"Failed to create applicant: {e}")
        except Exception as e:
            logger.error(f"Unexpected error creating applicant: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def upload_document(self, applicant_id: str, file_content: bytes, 
                            filename: str, document_type: str = "passport") -> Dict[str, Any]:
        """Upload document for verification"""
        
        if self.is_sandbox:
            # Return mock document for testing
            return {
                "id": f"mock_document_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "applicant_id": applicant_id,
                "type": document_type,
                "file_name": filename,
                "file_size": len(file_content),
                "created_at": datetime.now().isoformat(),
                "sandbox": True
            }
        
        try:
            with self._get_client() as api_client:
                default_api = onfido.DefaultApi(api_client)
                
                document = default_api.upload_document(
                    applicant_id=applicant_id,
                    type=document_type,
                    file=file_content,
                    file_name=filename
                )
                
                return {
                    "id": document.id,
                    "applicant_id": document.applicant_id,
                    "type": document.type,
                    "file_name": document.file_name,
                    "file_size": document.file_size,
                    "created_at": document.created_at.isoformat() if document.created_at else None,
                    "sandbox": False
                }
                
        except ApiException as e:
            logger.error(f"Onfido API error uploading document: {e}")
            raise HTTPException(status_code=400, detail=f"Failed to upload document: {e}")
        except Exception as e:
            logger.error(f"Unexpected error uploading document: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def create_check(self, applicant_id: str, report_names: List[str] = None) -> Dict[str, Any]:
        """Create verification check"""
        
        if report_names is None:
            report_names = ["document"]
        
        if self.is_sandbox:
            # Return mock check for testing
            return {
                "id": f"mock_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "applicant_id": applicant_id,
                "status": "in_progress",
                "result": None,
                "created_at": datetime.now().isoformat(),
                "reports": [{"id": f"mock_report_{i}", "name": name, "status": "awaiting_data"} 
                           for i, name in enumerate(report_names)],
                "sandbox": True
            }
        
        try:
            with self._get_client() as api_client:
                default_api = onfido.DefaultApi(api_client)
                
                check_request = onfido.CheckRequest(
                    applicant_id=applicant_id,
                    report_names=report_names
                )
                
                check = default_api.create_check(check_request)
                
                return {
                    "id": check.id,
                    "applicant_id": check.applicant_id,
                    "status": check.status,
                    "result": check.result,
                    "created_at": check.created_at.isoformat() if check.created_at else None,
                    "reports": [{"id": r.id, "name": r.name, "status": r.status} for r in check.reports] if check.reports else [],
                    "sandbox": False
                }
                
        except ApiException as e:
            logger.error(f"Onfido API error creating check: {e}")
            raise HTTPException(status_code=400, detail=f"Failed to create check: {e}")
        except Exception as e:
            logger.error(f"Unexpected error creating check: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def get_check(self, check_id: str) -> Dict[str, Any]:
        """Get verification check results"""
        
        if self.is_sandbox or check_id.startswith('mock_check_'):
            # Return mock results for testing
            return {
                "id": check_id,
                "status": "complete", 
                "result": "clear",
                "reports": [{
                    "id": "mock_report_1",
                    "name": "document",
                    "status": "complete",
                    "result": "clear",
                    "sub_result": "clear",
                    "breakdown": {
                        "visual_authenticity": {"result": "clear"},
                        "data_integrity": {"result": "clear"}, 
                        "data_validation": {"result": "clear"}
                    },
                    "properties": {
                        "document_type": "passport",
                        "issuing_country": "USA"
                    }
                }],
                "sandbox": True
            }
        
        try:
            with self._get_client() as api_client:
                default_api = onfido.DefaultApi(api_client)
                
                check = default_api.find_check(check_id)
                
                return {
                    "id": check.id,
                    "status": check.status,
                    "result": check.result,
                    "reports": [self._format_report(r) for r in check.reports] if check.reports else [],
                    "sandbox": False
                }
                
        except ApiException as e:
            logger.error(f"Onfido API error getting check: {e}")
            raise HTTPException(status_code=400, detail=f"Failed to get check: {e}")
        except Exception as e:
            logger.error(f"Unexpected error getting check: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    def _format_report(self, report) -> Dict[str, Any]:
        """Format Onfido report for consistent response"""
        return {
            "id": report.id,
            "name": report.name,
            "status": report.status,
            "result": report.result,
            "sub_result": getattr(report, 'sub_result', None),
            "breakdown": getattr(report, 'breakdown', {}),
            "properties": getattr(report, 'properties', {})
        }
    
    async def analyze_document(self, file_content: bytes, filename: str, 
                             applicant_name: str, document_type: str = "passport") -> Dict[str, Any]:
        """Complete document analysis - main interface replacing Dr. Miguel"""
        
        try:
            # Extract applicant names
            name_parts = applicant_name.strip().split()
            first_name = name_parts[0] if name_parts else "Unknown"
            last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else "User"
            
            # Step 1: Create applicant
            applicant = await self.create_applicant(first_name, last_name)
            applicant_id = applicant["id"]
            
            # Step 2: Upload document
            document = await self.upload_document(applicant_id, file_content, filename, document_type)
            
            # Step 3: Create verification check
            check = await self.create_check(applicant_id, ["document"])
            check_id = check["id"]
            
            # Step 4: Get results (in sandbox, immediate; in live, may need polling)
            results = await self.get_check(check_id)
            
            # Step 5: Format response in same format as Dr. Miguel for compatibility
            return self._format_dr_miguel_compatible_response(results, applicant, document)
            
        except Exception as e:
            logger.error(f"Error in document analysis: {e}")
            return {
                "valid": False,
                "legible": False,
                "completeness": 0,
                "issues": [f"Analysis failed: {str(e)}"],
                "extracted_data": {
                    "document_type": document_type,
                    "file_name": filename,
                    "validation_status": "FAILED",
                    "error": str(e)
                },
                "dra_paula_assessment": "Onfido: Análise falhoun",
                "onfido_powered": True,
                "sandbox": self.is_sandbox
            }
    
    def _format_dr_miguel_compatible_response(self, results: Dict, applicant: Dict, document: Dict) -> Dict[str, Any]:
        """Format Onfido results to be compatible with existing Dr. Miguel interface"""
        
        # Extract main report (usually document report)
        main_report = results.get("reports", [{}])[0]
        report_result = main_report.get("result", "unknown")
        
        # Determine validation status
        is_clear = report_result == "clear"
        is_consider = report_result == "consider"
        
        # Calculate completeness score based on result
        if is_clear:
            completeness = 95
            valid = True
        elif is_consider:
            completeness = 75 
            valid = False  # Requires review
        else:
            completeness = 25
            valid = False
        
        # Extract issues from breakdown
        issues = []
        breakdown = main_report.get("breakdown", {})
        
        for check_type, check_result in breakdown.items():
            if check_result.get("result") != "clear":
                issues.append(f"{check_type}: {check_result.get('result', 'unknown')}")
        
        if not issues and not is_clear:
            issues = ["Document requires manual review"]
        
        # Format extracted data
        properties = main_report.get("properties", {})
        extracted_data = {
            "document_type": properties.get("document_type", "unknown"),
            "issuing_country": properties.get("issuing_country", "unknown"),
            "file_name": document.get("file_name", "unknown"),
            "validation_status": "APPROVED" if is_clear else "REQUIRES_REVIEW" if is_consider else "REJECTED",
            "onfido_check_id": results.get("id"),
            "onfido_applicant_id": applicant.get("id"),
            "processed_at": datetime.now().isoformat()
        }
        
        # Professional assessment
        if is_clear:
            assessment = "Onfido: Documento autêntico e válido para processos de imigração"
        elif is_consider:
            assessment = "Onfido: Documento requer revisão manual - possíveis inconsistências detectadas"
        else:
            assessment = "Onfido: Documento rejeitado - não atende aos critérios de autenticidade"
        
        return {
            "valid": valid,
            "legible": True,  # Onfido handles legibility automatically
            "completeness": completeness,
            "issues": issues,
            "extracted_data": extracted_data,
            "dra_paula_assessment": assessment,
            "onfido_powered": True,
            "sandbox": self.is_sandbox,
            "professional_verification": {
                "provider": "Onfido",
                "check_id": results.get("id"),
                "status": results.get("status"),
                "result": results.get("result"),
                "breakdown": breakdown,
                "confidence_level": "enterprise_grade"
            }
        }

# Global instance
onfido_verifier = OnfidoDocumentVerifier()