"""
Utility Bills Validator - Specific Document Validator
Validador especializado para contas de utilidades públicas
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, date
import asyncio

from .pipeline_framework import PipelineStage, PipelineContext
from .real_ocr_engine import real_ocr_engine

logger = logging.getLogger(__name__)

@dataclass
class UtilityBillData:
    """Structured data from utility bills"""
    # Account Information
    account_holder_name: str = ""
    service_address: str = ""
    billing_address: str = ""
    account_number: str = ""
    
    # Utility Information
    utility_type: str = ""  # Electric, Gas, Water, Internet, Phone, etc.
    utility_company: str = ""
    company_address: str = ""
    customer_service_number: str = ""
    
    # Billing Information
    bill_date: Optional[date] = None
    due_date: Optional[date] = None
    service_period_start: Optional[date] = None
    service_period_end: Optional[date] = None
    
    # Financial Information
    current_charges: Optional[float] = None
    previous_balance: Optional[float] = None
    total_amount_due: Optional[float] = None
    payment_received: Optional[float] = None
    
    # Usage Information
    current_usage: str = ""
    previous_usage: str = ""
    usage_unit: str = ""  # kWh, cubic feet, gallons, etc.
    
    # Billing Details
    rate_schedule: str = ""
    meter_number: str = ""
    
    # Validation
    confidence_score: float = 0.0
    validation_status: str = "PENDING"  # VALID, INVALID, SUSPICIOUS
    issues: List[str] = None
    
    def __post_init__(self):
        if self.issues is None:
            self.issues = []

class UtilityBillsValidator:
    """
    Specialized validator for utility bills
    Handles electric, gas, water, internet, phone, and other utility bills
    """
    
    def __init__(self):
        # Utility type patterns
        self.utility_type_patterns = {
            'electric': [
                r'electric\s+bill',
                r'electricity\s+bill',
                r'power\s+bill',
                r'energy\s+bill',
                r'electric\s+utility',
                r'conta\s+de\s+luz',
                r'energia\s+elétrica',
                r'kwh'
            ],
            'gas': [
                r'gas\s+bill',
                r'natural\s+gas',
                r'gas\s+utility',
                r'conta\s+de\s+gás',
                r'therms?',
                r'cubic\s+feet'
            ],
            'water': [
                r'water\s+bill',
                r'water\s+utility',
                r'water\s+and\s+sewer',
                r'conta\s+de\s+água',
                r'gallons?',
                r'water\s+department'
            ],
            'internet': [
                r'internet\s+bill',
                r'broadband\s+bill',
                r'cable\s+bill',
                r'telecommunications?',
                r'conta\s+de\s+internet',
                r'mbps'
            ],
            'phone': [
                r'phone\s+bill',
                r'telephone\s+bill',
                r'wireless\s+bill',
                r'mobile\s+bill',
                r'conta\s+de\s+telefone',
                r'cellular\s+service'
            ],
            'waste': [
                r'waste\s+management',
                r'garbage\s+bill',
                r'trash\s+bill',
                r'recycling\s+bill',
                r'conta\s+de\s+lixo'
            ]
        }
        
        # Common utility bill patterns
        self.patterns = {
            'account_holder': [
                r'(?:account\s+holder|customer\s+name|nome\s+do\s+cliente)[:\s]*([A-Z][A-Za-z\s\-\']{3,50})',
                r'(?:name|nome)[:\s]*([A-Z][A-Za-z\s\-\']{3,50})',
                r'(?:bill\s+to|fatura\s+para)[:\s]*([A-Z][A-Za-z\s\-\']{3,50})',
            ],
            'service_address': [
                r'(?:service\s+address|endereço\s+de\s+serviço)[:\s]*([A-Za-z0-9\s,\-\.#]{10,80})',
                r'(?:property\s+address|endereço\s+do\s+imóvel)[:\s]*([A-Za-z0-9\s,\-\.#]{10,80})',
                r'(?:installation\s+address)[:\s]*([A-Za-z0-9\s,\-\.#]{10,80})',
            ],
            'billing_address': [
                r'(?:billing\s+address|endereço\s+de\s+cobrança)[:\s]*([A-Za-z0-9\s,\-\.#]{10,80})',
                r'(?:mailing\s+address|endereço\s+de\s+correspondência)[:\s]*([A-Za-z0-9\s,\-\.#]{10,80})',
            ],
            'account_number': [
                r'(?:account\s+number|número\s+da\s+conta)[:\s#]*([A-Z0-9\-]{6,20})',
                r'(?:customer\s+number|número\s+do\s+cliente)[:\s#]*([A-Z0-9\-]{6,20})',
                r'(?:acct\s*#?)[:\s]*([A-Z0-9\-]{6,20})',
            ],
            'utility_company': [
                r'([A-Z][A-Za-z\s&,\-\.]{3,50})\s*(?:electric|gas|water|power|energy|utility)',
                r'(?:utility\s+company|empresa\s+de\s+utilidade)[:\s]*([A-Z][A-Za-z\s&,\-\.]{3,50})',
                r'(?:provider|provedor)[:\s]*([A-Z][A-Za-z\s&,\-\.]{3,50})',
            ],
            'bill_date': [
                r'(?:bill\s+date|data\s+da\s+fatura)[:\s]*(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})',
                r'(?:statement\s+date|data\s+do\s+extrato)[:\s]*(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})',
                r'(?:invoice\s+date)[:\s]*(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})',
            ],
            'due_date': [
                r'(?:due\s+date|data\s+de\s+vencimento)[:\s]*(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})',
                r'(?:payment\s+due|pagamento\s+devido)[:\s]*(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})',
                r'(?:please\s+pay\s+by)[:\s]*(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})',
            ],
            'service_period': [
                r'(?:service\s+period|período\s+de\s+serviço)[:\s]*(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})\s*(?:to|até|a)\s*(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})',
                r'(?:billing\s+period|período\s+de\s+faturamento)[:\s]*(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})\s*(?:to|até|a)\s*(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})',
                r'(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})\s*(?:through|até|a)\s*(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})',
            ],
            'current_charges': [
                r'(?:current\s+charges|encargos\s+atuais)[:\s]*\$?([0-9,]+\.?\d{0,2})',
                r'(?:new\s+charges|novos\s+encargos)[:\s]*\$?([0-9,]+\.?\d{0,2})',
                r'(?:usage\s+charges)[:\s]*\$?([0-9,]+\.?\d{0,2})',
            ],
            'total_amount_due': [
                r'(?:total\s+amount\s+due|valor\s+total\s+devido)[:\s]*\$?([0-9,]+\.?\d{0,2})',
                r'(?:amount\s+due|valor\s+devido)[:\s]*\$?([0-9,]+\.?\d{0,2})',
                r'(?:balance\s+due|saldo\s+devedor)[:\s]*\$?([0-9,]+\.?\d{0,2})',
            ],
            'previous_balance': [
                r'(?:previous\s+balance|saldo\s+anterior)[:\s]*\$?([0-9,]+\.?\d{0,2})',
                r'(?:carried\s+forward|saldo\s+anterior)[:\s]*\$?([0-9,]+\.?\d{0,2})',
            ],
            'current_usage': [
                r'(?:current\s+usage|uso\s+atual)[:\s]*([0-9,]+\.?\d{0,2})',
                r'(?:this\s+month\s+usage|uso\s+deste\s+mês)[:\s]*([0-9,]+\.?\d{0,2})',
                r'(?:usage\s+amount)[:\s]*([0-9,]+\.?\d{0,2})',
            ],
            'meter_number': [
                r'(?:meter\s+number|número\s+do\s+medidor)[:\s#]*([A-Z0-9\-]{4,15})',
                r'(?:meter\s+id)[:\s#]*([A-Z0-9\-]{4,15})',
            ],
            'customer_service': [
                r'(?:customer\s+service|atendimento\s+ao\s+cliente)[:\s]*(\d{3}[-\.\s]?\d{3}[-\.\s]?\d{4})',
                r'(?:phone|telefone)[:\s]*(\d{3}[-\.\s]?\d{3}[-\.\s]?\d{4})',
                r'(\d{3}[-\.\s]\d{3}[-\.\s]\d{4})',
            ]
        }
        
        # Common utility company names (for validation)
        self.known_utility_companies = [
            'pacific gas & electric', 'pge', 'southern california edison', 'sce',
            'con edison', 'consolidated edison', 'georgia power', 'florida power & light',
            'duke energy', 'american electric power', 'dominion energy', 'entergy',
            'xcel energy', 'northeast utilities', 'pepco', 'baltimore gas & electric',
            'commonwealth edison', 'comed', 'national grid', 'pseg',
            'verizon', 'att', 'at&t', 'comcast', 'spectrum', 'cox communications',
            'time warner cable', 'century link', 'frontier communications'
        ]
        
        # Utility bill indicators
        self.bill_indicators = [
            'utility bill', 'electric bill', 'gas bill', 'water bill', 'phone bill',
            'internet bill', 'account number', 'due date', 'service period',
            'current charges', 'usage', 'meter reading', 'billing address',
            'customer service', 'payment due', 'kilowatt', 'therms', 'gallons'
        ]
    
    async def validate_utility_bill(self, 
                                   document_content: str,
                                   document_type: str = "utility_bill") -> UtilityBillData:
        """
        Validate and extract data from utility bill
        
        Args:
            document_content: Base64 image or text content
            document_type: Document type identifier
        
        Returns:
            UtilityBillData with extracted and validated information
        """
        try:
            result = UtilityBillData()
            
            # 1. Extract text if image provided
            if self._is_base64_image(document_content):
                ocr_result = await real_ocr_engine.extract_text_from_image(
                    document_content, 
                    mode="document",
                    language="eng"  # Utility bills typically in English
                )
                text_content = ocr_result.text
                base_confidence = ocr_result.confidence
            else:
                text_content = document_content
                base_confidence = 0.9
            
            # 2. Verify this is actually a utility bill
            if not self._verify_utility_bill(text_content):
                result.validation_status = "INVALID"
                result.issues.append("Document does not appear to be a utility bill")
                return result
            
            # 3. Identify specific utility type
            result.utility_type = self._identify_utility_type(text_content)
            
            # 4. Extract structured data
            result = await self._extract_utility_data(text_content, result)
            
            # 5. Validate extracted data
            validation_result = self._validate_utility_data(result)
            result.validation_status = validation_result['status']
            result.issues.extend(validation_result['issues'])
            
            # 6. Calculate confidence score
            result.confidence_score = self._calculate_confidence(result, base_confidence)
            
            logger.info(f"Utility bill validation completed: type={result.utility_type}, status={result.validation_status}, confidence={result.confidence_score:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Utility bill validation failed: {e}")
            result = UtilityBillData()
            result.validation_status = "INVALID"
            result.issues.append(f"Validation error: {str(e)}")
            return result
    
    def _is_base64_image(self, content: str) -> bool:
        """Check if content is base64 encoded image"""
        return (content.startswith('data:image/') or 
                (len(content) > 100 and content.replace('+', '').replace('/', '').replace('=', '').isalnum()))
    
    def _verify_utility_bill(self, text: str) -> bool:
        """Verify this is a utility bill document"""
        text_lower = text.lower()
        
        found_indicators = sum(1 for indicator in self.bill_indicators 
                             if indicator in text_lower)
        
        # Also check for specific utility type patterns
        utility_pattern_found = any(
            any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)
            for patterns in self.utility_type_patterns.values()
        )
        
        return found_indicators >= 3 or utility_pattern_found
    
    def _identify_utility_type(self, text: str) -> str:
        """Identify specific type of utility bill"""
        for utility_type, patterns in self.utility_type_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return utility_type.upper()
        
        return "GENERAL_UTILITY"
    
    async def _extract_utility_data(self, text: str, result: UtilityBillData) -> UtilityBillData:
        """Extract structured data from utility bill text"""
        
        # Extract account holder name
        for pattern in self.patterns['account_holder']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name_candidate = match.group(1).strip()
                # Filter out obvious company names in name field
                if not any(word in name_candidate.lower() for word in ['company', 'corporation', 'electric', 'gas', 'water']):
                    result.account_holder_name = name_candidate
                    break
        
        # Extract service address
        for pattern in self.patterns['service_address']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result.service_address = match.group(1).strip()
                break
        
        # Extract billing address
        for pattern in self.patterns['billing_address']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result.billing_address = match.group(1).strip()
                break
        
        # Extract account number
        for pattern in self.patterns['account_number']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result.account_number = match.group(1).strip()
                break
        
        # Extract utility company
        for pattern in self.patterns['utility_company']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                company_candidate = match.group(1).strip()
                # Validate against known companies or accept if looks like a company name
                if (company_candidate.lower() in [name.lower() for name in self.known_utility_companies] or
                    any(word in company_candidate.lower() for word in ['electric', 'gas', 'water', 'power', 'energy', 'communications'])):
                    result.utility_company = company_candidate
                    break
        
        # Extract bill date
        for pattern in self.patterns['bill_date']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    result.bill_date = self._parse_date(match.group(1))
                    break
                except:
                    continue
        
        # Extract due date
        for pattern in self.patterns['due_date']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    result.due_date = self._parse_date(match.group(1))
                    break
                except:
                    continue
        
        # Extract service period
        for pattern in self.patterns['service_period']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    result.service_period_start = self._parse_date(match.group(1))
                    result.service_period_end = self._parse_date(match.group(2))
                    break
                except:
                    continue
        
        # Extract financial information
        financial_fields = {
            'current_charges': 'current_charges',
            'total_amount_due': 'total_amount_due',
            'previous_balance': 'previous_balance'
        }
        
        for field_name, result_attr in financial_fields.items():
            for pattern in self.patterns[field_name]:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    try:
                        amount_str = match.group(1).replace(',', '')
                        amount = float(amount_str)
                        setattr(result, result_attr, amount)
                        break
                    except ValueError:
                        continue
        
        # Extract usage information
        for pattern in self.patterns['current_usage']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result.current_usage = match.group(1)
                # Try to identify usage unit
                usage_context = text[max(0, match.start()-50):min(len(text), match.end()+50)]
                if 'kwh' in usage_context.lower():
                    result.usage_unit = "kWh"
                elif 'therm' in usage_context.lower():
                    result.usage_unit = "therms"
                elif 'gallon' in usage_context.lower():
                    result.usage_unit = "gallons"
                elif 'cubic' in usage_context.lower():
                    result.usage_unit = "cubic feet"
                break
        
        # Extract meter number
        for pattern in self.patterns['meter_number']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result.meter_number = match.group(1).strip()
                break
        
        # Extract customer service number
        for pattern in self.patterns['customer_service']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result.customer_service_number = match.group(1)
                break
        
        return result
    
    def _parse_date(self, date_str: str) -> date:
        """Parse date string in various formats"""
        date_str = date_str.strip()
        formats = ['%m/%d/%Y', '%d/%m/%Y', '%m-%d-%Y', '%d-%m-%Y', '%Y-%m-%d']
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        raise ValueError(f"Unable to parse date: {date_str}")
    
    def _validate_utility_data(self, result: UtilityBillData) -> Dict[str, Any]:
        """Validate extracted utility bill data"""
        issues = []
        
        # Check required fields
        if not result.account_holder_name:
            issues.append("Account holder name not found")
        elif len(result.account_holder_name) < 3:
            issues.append("Account holder name appears incomplete")
        
        if not result.service_address:
            issues.append("Service address not found")
        elif len(result.service_address) < 10:
            issues.append("Service address appears incomplete")
        
        if not result.account_number:
            issues.append("Account number not found")
        elif len(result.account_number) < 6:
            issues.append("Account number appears too short")
        
        if not result.utility_company:
            issues.append("Utility company name not found")
        
        # Check dates
        if not result.bill_date:
            issues.append("Bill date not found")
        else:
            # Check if bill date is reasonable
            today = date.today()
            if result.bill_date > today:
                issues.append("Bill date is in the future")
            elif result.bill_date < date(2000, 1, 1):
                issues.append("Bill date is unreasonably old")
        
        if not result.due_date:
            issues.append("Due date not found")
        else:
            # Check if due date makes sense
            if result.bill_date and result.due_date < result.bill_date:
                issues.append("Due date is before bill date")
        
        # Check service period
        if result.service_period_start and result.service_period_end:
            if result.service_period_start >= result.service_period_end:
                issues.append("Service period start date is not before end date")
        
        # Check financial information
        financial_amounts = [result.current_charges, result.total_amount_due, result.previous_balance]
        valid_amounts = [amount for amount in financial_amounts if amount is not None]
        
        if not valid_amounts:
            issues.append("No financial information found")
        else:
            # Check for unreasonable amounts
            for amount in valid_amounts:
                if amount < 0:
                    issues.append(f"Negative amount found: ${amount}")
                elif amount > 10000:
                    issues.append(f"Unusually high amount: ${amount}")
        
        # Check utility type identification
        if not result.utility_type or result.utility_type == "GENERAL_UTILITY":
            issues.append("Could not identify specific utility type")
        
        # Determine status
        critical_issues = len([i for i in issues if any(word in i.lower() 
                              for word in ['not found', 'future', 'negative', 'before'])])
        
        if critical_issues == 0:
            status = "VALID"
        elif critical_issues <= 3:
            status = "SUSPICIOUS"
        else:
            status = "INVALID"
        
        return {
            'status': status,
            'issues': issues,
            'critical_issues_count': critical_issues
        }
    
    def _calculate_confidence(self, result: UtilityBillData, base_confidence: float) -> float:
        """Calculate overall confidence score"""
        confidence = base_confidence * 0.25  # Base OCR confidence (25%)
        
        # Account identification (25%)
        account_score = 0.0
        if result.account_holder_name:
            account_score += 0.10
        if result.account_number:
            account_score += 0.08
        if result.service_address:
            account_score += 0.07
        
        confidence += account_score
        
        # Utility company and type (20%)
        utility_score = 0.0
        if result.utility_company:
            utility_score += 0.12
        if result.utility_type and result.utility_type != "GENERAL_UTILITY":
            utility_score += 0.08
        
        confidence += utility_score
        
        # Billing information (20%)
        billing_score = 0.0
        if result.bill_date:
            billing_score += 0.08
        if result.due_date:
            billing_score += 0.06
        if result.total_amount_due is not None:
            billing_score += 0.06
        
        confidence += billing_score
        
        # Additional details (10%)
        details_score = 0.0
        if result.current_usage:
            details_score += 0.03
        if result.meter_number:
            details_score += 0.03
        if result.service_period_start and result.service_period_end:
            details_score += 0.04
        
        confidence += details_score
        
        # Validation status (10%)
        status_scores = {'VALID': 0.10, 'SUSPICIOUS': 0.05, 'INVALID': 0.0}
        confidence += status_scores.get(result.validation_status, 0.0)
        
        return min(confidence, 1.0)

class UtilityBillsValidationStage(PipelineStage):
    """
    Pipeline stage for utility bills validation
    """
    
    def __init__(self):
        super().__init__("utility_bills_validation", enabled=True)
        self.validator = UtilityBillsValidator()
    
    async def process(self, context: PipelineContext) -> PipelineContext:
        """Process utility bill validation"""
        try:
            # Only process if document is classified as utility bill
            if context.document_type.lower() not in ['utility_bill', 'electric_bill', 'gas_bill', 'water_bill', 'phone_bill', 'internet_bill', 'conta_utilidade']:
                logger.info(f"Skipping utility bill validation for document type: {context.document_type}")
                return context
            
            # Validate utility bill
            result = await self.validator.validate_utility_bill(
                context.content_base64,
                context.document_type
            )
            
            # Add results to context
            context.validation_results['utility_bill'] = {
                'account_holder_name': result.account_holder_name,
                'service_address': result.service_address,
                'billing_address': result.billing_address,
                'account_number': result.account_number,
                'utility_type': result.utility_type,
                'utility_company': result.utility_company,
                'company_address': result.company_address,
                'customer_service_number': result.customer_service_number,
                'bill_date': result.bill_date.isoformat() if result.bill_date else None,
                'due_date': result.due_date.isoformat() if result.due_date else None,
                'service_period_start': result.service_period_start.isoformat() if result.service_period_start else None,
                'service_period_end': result.service_period_end.isoformat() if result.service_period_end else None,
                'current_charges': result.current_charges,
                'previous_balance': result.previous_balance,
                'total_amount_due': result.total_amount_due,
                'payment_received': result.payment_received,
                'current_usage': result.current_usage,
                'previous_usage': result.previous_usage,
                'usage_unit': result.usage_unit,
                'rate_schedule': result.rate_schedule,
                'meter_number': result.meter_number,
                'confidence_score': result.confidence_score,
                'validation_status': result.validation_status,
                'issues': result.issues
            }
            
            # Update overall confidence
            if result.confidence_score > context.final_confidence:
                context.final_confidence = result.confidence_score
            
            # Update verdict based on validation
            if result.validation_status == "VALID":
                context.final_verdict = "APROVADO"
            elif result.validation_status == "SUSPICIOUS":
                context.final_verdict = "NECESSITA_REVISÃO"
            else:
                context.final_verdict = "REJEITADO"
                context.errors.extend(result.issues)
            
            logger.info(f"Utility bill validation completed: {result.validation_status}, confidence: {result.confidence_score:.2f}")
            
            return context
            
        except Exception as e:
            error_msg = f"Utility bill validation stage failed: {str(e)}"
            logger.error(error_msg)
            context.errors.append(error_msg)
            return context

# Global instances
utility_bills_validator = UtilityBillsValidator()
utility_bills_validation_stage = UtilityBillsValidationStage()