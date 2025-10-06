"""
Consistency Engine - Advanced Cross-Document Validation
Sistema avançado de validação cruzada entre múltiplos documentos
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, date
import asyncio
from difflib import SequenceMatcher
import jellyfish  # For phonetic matching

logger = logging.getLogger(__name__)

@dataclass
class DocumentInfo:
    """Information extracted from a single document"""
    document_type: str
    document_id: str
    
    # Personal Information
    full_name: str = ""
    first_name: str = ""
    last_name: str = ""
    date_of_birth: Optional[date] = None
    place_of_birth: str = ""
    nationality: str = ""
    
    # Document Numbers
    passport_number: str = ""
    alien_number: str = ""
    social_security: str = ""
    document_number: str = ""
    
    # Dates
    issue_date: Optional[date] = None
    expiration_date: Optional[date] = None
    
    # Additional fields
    country_issued: str = ""
    parents_names: List[str] = field(default_factory=list)
    spouse_name: str = ""
    
    # Metadata
    confidence_score: float = 0.0
    extraction_method: str = ""

@dataclass
class ConsistencyIssue:
    """Represents a consistency issue between documents"""
    issue_type: str  # NAME_MISMATCH, DATE_MISMATCH, NUMBER_MISMATCH, etc.
    severity: str    # CRITICAL, WARNING, INFO
    field_name: str
    document1_id: str
    document2_id: str
    value1: Any
    value2: Any
    similarity_score: float = 0.0
    description: str = ""
    recommendation: str = ""

@dataclass
class ConsistencyReport:
    """Complete consistency validation report"""
    overall_status: str = "PENDING"  # CONSISTENT, INCONSISTENT, SUSPICIOUS
    confidence_score: float = 0.0
    documents_analyzed: int = 0
    
    issues: List[ConsistencyIssue] = field(default_factory=list)
    critical_issues: int = 0
    warning_issues: int = 0
    info_issues: int = 0
    
    recommendations: List[str] = field(default_factory=list)
    processing_time: float = 0.0

class ConsistencyEngine:
    """
    Advanced engine for cross-document consistency validation
    Performs intelligent matching with fuzzy logic and phonetic similarity
    """
    
    def __init__(self):
        self.similarity_thresholds = {
            'name_exact': 0.95,
            'name_similar': 0.85,
            'name_phonetic': 0.80,
            'date_exact': 1.0,
            'number_exact': 1.0,
            'place_similar': 0.75
        }
        
        # Common name variations and nicknames
        self.name_variations = {
            'john': ['jon', 'johnny', 'jack'],
            'michael': ['mike', 'mick', 'mickey'],
            'william': ['bill', 'billy', 'will', 'willie'],
            'robert': ['rob', 'bob', 'bobby', 'robbie'],
            'james': ['jim', 'jimmy', 'jamie'],
            'richard': ['rick', 'ricky', 'dick'],
            'maria': ['mary', 'marie'],
            'jose': ['joseph', 'joe'],
            'antonio': ['anthony', 'tony'],
            'francisco': ['frank', 'francis']
        }
        
        # Common document type relationships
        self.document_relationships = {
            'passport': ['birth_certificate', 'i765', 'i797'],
            'birth_certificate': ['passport', 'i765', 'i797'],
            'i765': ['passport', 'i797'],
            'i797': ['passport', 'i765', 'birth_certificate']
        }
    
    async def validate_consistency(self, documents: List[DocumentInfo]) -> ConsistencyReport:
        """
        Validate consistency across multiple documents
        
        Args:
            documents: List of DocumentInfo objects to validate
        
        Returns:
            ConsistencyReport with detailed analysis
        """
        start_time = datetime.now()
        
        try:
            report = ConsistencyReport()
            report.documents_analyzed = len(documents)
            
            if len(documents) < 2:
                report.overall_status = "INSUFFICIENT_DOCUMENTS"
                report.recommendations.append("At least 2 documents required for consistency validation")
                return report
            
            # Perform pairwise consistency checks
            for i in range(len(documents)):
                for j in range(i + 1, len(documents)):
                    doc1, doc2 = documents[i], documents[j]
                    
                    # Check if these document types should be cross-validated
                    if self._should_validate_pair(doc1.document_type, doc2.document_type):
                        issues = await self._validate_document_pair(doc1, doc2)
                        report.issues.extend(issues)
            
            # Analyze issues and determine overall status
            report = self._analyze_issues(report)
            
            # Generate recommendations
            report.recommendations.extend(self._generate_recommendations(report))
            
            # Calculate processing time
            report.processing_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"Consistency validation completed: {report.overall_status}, "
                       f"{len(report.issues)} issues found")
            
            return report
            
        except Exception as e:
            logger.error(f"Consistency validation failed: {e}")
            report = ConsistencyReport()
            report.overall_status = "ERROR"
            report.recommendations.append(f"Validation error: {str(e)}")
            return report
    
    def _should_validate_pair(self, doc_type1: str, doc_type2: str) -> bool:
        """Check if two document types should be cross-validated"""
        return (doc_type2.lower() in self.document_relationships.get(doc_type1.lower(), []) or
                doc_type1.lower() in self.document_relationships.get(doc_type2.lower(), []))
    
    async def _validate_document_pair(self, doc1: DocumentInfo, doc2: DocumentInfo) -> List[ConsistencyIssue]:
        """Validate consistency between a pair of documents"""
        issues = []
        
        # Name consistency
        issues.extend(self._check_name_consistency(doc1, doc2))
        
        # Date of birth consistency  
        issues.extend(self._check_date_consistency(doc1, doc2))
        
        # Document numbers consistency
        issues.extend(self._check_number_consistency(doc1, doc2))
        
        # Place of birth consistency
        issues.extend(self._check_place_consistency(doc1, doc2))
        
        # Nationality consistency
        issues.extend(self._check_nationality_consistency(doc1, doc2))
        
        # Document dates consistency
        issues.extend(self._check_document_dates_consistency(doc1, doc2))
        
        return issues
    
    def _check_name_consistency(self, doc1: DocumentInfo, doc2: DocumentInfo) -> List[ConsistencyIssue]:
        """Check name consistency between documents"""
        issues = []
        
        if not doc1.full_name or not doc2.full_name:
            return issues
        
        # Normalize names
        name1 = self._normalize_name(doc1.full_name)
        name2 = self._normalize_name(doc2.full_name)
        
        # Exact match
        if name1 == name2:
            return issues
        
        # Calculate similarity scores
        similarity = SequenceMatcher(None, name1, name2).ratio()
        phonetic_similarity = self._phonetic_similarity(name1, name2)
        
        # Check for name variations
        variation_match = self._check_name_variations(name1, name2)
        
        # Determine issue severity
        if similarity >= self.similarity_thresholds['name_exact']:
            # Very similar - likely minor spelling differences
            pass
        elif (similarity >= self.similarity_thresholds['name_similar'] or 
              phonetic_similarity >= self.similarity_thresholds['name_phonetic'] or
              variation_match):
            # Moderately similar - possible nickname or variation
            issues.append(ConsistencyIssue(
                issue_type="NAME_VARIATION",
                severity="WARNING",
                field_name="full_name",
                document1_id=doc1.document_id,
                document2_id=doc2.document_id,
                value1=doc1.full_name,
                value2=doc2.full_name,
                similarity_score=max(similarity, phonetic_similarity),
                description=f"Name variation detected between documents",
                recommendation="Verify if this is the same person with name variation or nickname"
            ))
        else:
            # Very different names - likely different people
            issues.append(ConsistencyIssue(
                issue_type="NAME_MISMATCH",
                severity="CRITICAL",
                field_name="full_name",
                document1_id=doc1.document_id,
                document2_id=doc2.document_id,
                value1=doc1.full_name,
                value2=doc2.full_name,
                similarity_score=similarity,
                description=f"Significant name mismatch between documents",
                recommendation="Verify identity - documents may belong to different people"
            ))
        
        return issues
    
    def _check_date_consistency(self, doc1: DocumentInfo, doc2: DocumentInfo) -> List[ConsistencyIssue]:
        """Check date of birth consistency"""
        issues = []
        
        if not doc1.date_of_birth or not doc2.date_of_birth:
            return issues
        
        if doc1.date_of_birth != doc2.date_of_birth:
            # Calculate date difference
            diff_days = abs((doc1.date_of_birth - doc2.date_of_birth).days)
            
            if diff_days <= 1:
                # Minor difference - possibly date format issue
                issues.append(ConsistencyIssue(
                    issue_type="DATE_MINOR_MISMATCH",
                    severity="WARNING",
                    field_name="date_of_birth",
                    document1_id=doc1.document_id,
                    document2_id=doc2.document_id,
                    value1=doc1.date_of_birth,
                    value2=doc2.date_of_birth,
                    description=f"Minor date of birth difference ({diff_days} day)",
                    recommendation="Check if this is a date format issue"
                ))
            else:
                # Significant difference
                issues.append(ConsistencyIssue(
                    issue_type="DATE_MISMATCH",
                    severity="CRITICAL",
                    field_name="date_of_birth",
                    document1_id=doc1.document_id,
                    document2_id=doc2.document_id,
                    value1=doc1.date_of_birth,
                    value2=doc2.date_of_birth,
                    description=f"Date of birth mismatch ({diff_days} days difference)",
                    recommendation="Verify identity - different birth dates suggest different people"
                ))
        
        return issues
    
    def _check_number_consistency(self, doc1: DocumentInfo, doc2: DocumentInfo) -> List[ConsistencyIssue]:
        """Check document number consistency"""
        issues = []
        
        # Check passport numbers
        if doc1.passport_number and doc2.passport_number:
            if doc1.passport_number != doc2.passport_number:
                issues.append(ConsistencyIssue(
                    issue_type="PASSPORT_NUMBER_MISMATCH",
                    severity="CRITICAL",
                    field_name="passport_number",
                    document1_id=doc1.document_id,
                    document2_id=doc2.document_id,
                    value1=doc1.passport_number,
                    value2=doc2.passport_number,
                    description="Passport numbers do not match",
                    recommendation="Verify if documents belong to same person"
                ))
        
        # Check alien numbers
        if doc1.alien_number and doc2.alien_number:
            if doc1.alien_number != doc2.alien_number:
                issues.append(ConsistencyIssue(
                    issue_type="ALIEN_NUMBER_MISMATCH",
                    severity="CRITICAL",
                    field_name="alien_number",
                    document1_id=doc1.document_id,
                    document2_id=doc2.document_id,
                    value1=doc1.alien_number,
                    value2=doc2.alien_number,
                    description="Alien registration numbers do not match",
                    recommendation="Verify A-numbers - should be identical for same person"
                ))
        
        return issues
    
    def _check_place_consistency(self, doc1: DocumentInfo, doc2: DocumentInfo) -> List[ConsistencyIssue]:
        """Check place of birth consistency"""
        issues = []
        
        if not doc1.place_of_birth or not doc2.place_of_birth:
            return issues
        
        # Normalize places
        place1 = self._normalize_place(doc1.place_of_birth)
        place2 = self._normalize_place(doc2.place_of_birth)
        
        if place1 != place2:
            similarity = SequenceMatcher(None, place1, place2).ratio()
            
            if similarity >= self.similarity_thresholds['place_similar']:
                issues.append(ConsistencyIssue(
                    issue_type="PLACE_VARIATION",
                    severity="INFO",
                    field_name="place_of_birth",
                    document1_id=doc1.document_id,
                    document2_id=doc2.document_id,
                    value1=doc1.place_of_birth,
                    value2=doc2.place_of_birth,
                    similarity_score=similarity,
                    description="Minor place of birth variation",
                    recommendation="Verify if referring to same location"
                ))
            else:
                issues.append(ConsistencyIssue(
                    issue_type="PLACE_MISMATCH",
                    severity="WARNING",
                    field_name="place_of_birth",
                    document1_id=doc1.document_id,
                    document2_id=doc2.document_id,
                    value1=doc1.place_of_birth,
                    value2=doc2.place_of_birth,
                    similarity_score=similarity,
                    description="Place of birth mismatch",
                    recommendation="Verify birth location - may indicate document inconsistency"
                ))
        
        return issues
    
    def _check_nationality_consistency(self, doc1: DocumentInfo, doc2: DocumentInfo) -> List[ConsistencyIssue]:
        """Check nationality consistency"""
        issues = []
        
        if not doc1.nationality or not doc2.nationality:
            return issues
        
        # Normalize nationalities
        nat1 = doc1.nationality.upper().strip()
        nat2 = doc2.nationality.upper().strip()
        
        # Common nationality variations
        nationality_map = {
            'US': ['USA', 'UNITED STATES', 'AMERICAN'],
            'BR': ['BRAZIL', 'BRAZILIAN', 'BRASIL'],
            'UK': ['UNITED KINGDOM', 'BRITISH', 'ENGLAND'],
            'DE': ['GERMANY', 'GERMAN', 'DEUTSCHLAND']
        }
        
        # Check if they're the same after normalization
        same_nationality = False
        for code, variations in nationality_map.items():
            if (nat1 in variations or nat1 == code) and (nat2 in variations or nat2 == code):
                same_nationality = True
                break
        
        if not same_nationality and nat1 != nat2:
            issues.append(ConsistencyIssue(
                issue_type="NATIONALITY_MISMATCH",
                severity="WARNING",
                field_name="nationality",
                document1_id=doc1.document_id,
                document2_id=doc2.document_id,
                value1=doc1.nationality,
                value2=doc2.nationality,
                description="Nationality mismatch between documents",
                recommendation="Verify nationality - may indicate dual citizenship or error"
            ))
        
        return issues
    
    def _check_document_dates_consistency(self, doc1: DocumentInfo, doc2: DocumentInfo) -> List[ConsistencyIssue]:
        """Check document dates for logical consistency"""
        issues = []
        
        # Check if document dates make logical sense
        if doc1.issue_date and doc2.issue_date:
            # Documents should not be issued before birth
            if doc1.date_of_birth:
                if doc1.issue_date < doc1.date_of_birth:
                    issues.append(ConsistencyIssue(
                        issue_type="LOGICAL_DATE_ERROR",
                        severity="CRITICAL",
                        field_name="issue_date",
                        document1_id=doc1.document_id,
                        document2_id="",
                        value1=doc1.issue_date,
                        value2=doc1.date_of_birth,
                        description="Document issued before birth date",
                        recommendation="Check date accuracy - document cannot be issued before birth"
                    ))
        
        return issues
    
    def _normalize_name(self, name: str) -> str:
        """Normalize name for comparison"""
        if not name:
            return ""
        
        # Remove common prefixes/suffixes
        name = re.sub(r'\b(Mr|Mrs|Ms|Dr|Jr|Sr|III|IV)\b\.?', '', name, flags=re.IGNORECASE)
        
        # Remove extra spaces and punctuation
        name = re.sub(r'[^\w\s]', '', name)
        name = re.sub(r'\s+', ' ', name).strip().upper()
        
        return name
    
    def _normalize_place(self, place: str) -> str:
        """Normalize place name for comparison"""
        if not place:
            return ""
        
        # Common place abbreviations
        place = place.upper().strip()
        place = place.replace(' ST ', ' STATE ')
        place = place.replace(' USA', '')
        place = place.replace(' US', '')
        place = place.replace(' UNITED STATES', '')
        
        return place
    
    def _phonetic_similarity(self, name1: str, name2: str) -> float:
        """Calculate phonetic similarity between names"""
        try:
            # Use Soundex for phonetic comparison
            soundex1 = jellyfish.soundex(name1)
            soundex2 = jellyfish.soundex(name2)
            
            if soundex1 == soundex2:
                return 1.0
            
            # Use Jaro-Winkler for more nuanced similarity
            return jellyfish.jaro_winkler_similarity(name1, name2)
            
        except:
            # Fallback to simple string similarity
            return SequenceMatcher(None, name1, name2).ratio()
    
    def _check_name_variations(self, name1: str, name2: str) -> bool:
        """Check if names are known variations of each other"""
        words1 = set(name1.lower().split())
        words2 = set(name2.lower().split())
        
        for word1 in words1:
            for word2 in words2:
                if word1 in self.name_variations:
                    if word2 in self.name_variations[word1]:
                        return True
                if word2 in self.name_variations:
                    if word1 in self.name_variations[word2]:
                        return True
        
        return False
    
    def _analyze_issues(self, report: ConsistencyReport) -> ConsistencyReport:
        """Analyze issues and determine overall status"""
        
        # Count issues by severity
        for issue in report.issues:
            if issue.severity == "CRITICAL":
                report.critical_issues += 1
            elif issue.severity == "WARNING":
                report.warning_issues += 1
            else:
                report.info_issues += 1
        
        # Determine overall status
        if report.critical_issues > 0:
            report.overall_status = "INCONSISTENT"
            report.confidence_score = 0.3
        elif report.warning_issues > 2:
            report.overall_status = "SUSPICIOUS"
            report.confidence_score = 0.6
        elif report.warning_issues > 0:
            report.overall_status = "SUSPICIOUS" 
            report.confidence_score = 0.8
        else:
            report.overall_status = "CONSISTENT"
            report.confidence_score = 0.95
        
        return report
    
    def _generate_recommendations(self, report: ConsistencyReport) -> List[str]:
        """Generate recommendations based on consistency analysis"""
        recommendations = []
        
        if report.critical_issues > 0:
            recommendations.append("CRITICAL: Manual review required due to significant inconsistencies")
            recommendations.append("Verify that all documents belong to the same person")
        
        if report.warning_issues > 0:
            recommendations.append("Review flagged discrepancies for accuracy")
            recommendations.append("Consider requesting additional documentation for verification")
        
        # Specific recommendations based on issue types
        issue_types = {issue.issue_type for issue in report.issues}
        
        if "NAME_MISMATCH" in issue_types:
            recommendations.append("Verify identity through additional identification documents")
        
        if "DATE_MISMATCH" in issue_types:
            recommendations.append("Confirm birth date with official birth certificate")
        
        if "PASSPORT_NUMBER_MISMATCH" in issue_types or "ALIEN_NUMBER_MISMATCH" in issue_types:
            recommendations.append("Verify document authenticity and check for clerical errors")
        
        return recommendations

# Global instance
consistency_engine = ConsistencyEngine()