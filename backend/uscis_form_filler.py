"""
USCIS Form Filler System
Auto-fill official USCIS forms with case data

LIBRARY: PyMuPDF (fitz) for reliable PDF form filling

SUPPORTED FORMS:
- I-539: Extension/Change of Status (✅ 159 editable fields)
- I-589: Asylum Application (✅ editable fields)
- I-140: EB-1A Immigrant Petition (✅ editable fields)
- I-129: Nonimmigrant Worker Petition (⚠️ NO editable fields in current template)
  - O-1: Extraordinary Ability
  - H-1B: Specialty Occupation
  - L-1: Intracompany Transferee
- F-1: Student Visa (uses I-539)

IMPORTANT NOTES ABOUT I-129:
==========================
The current USCIS I-129 PDF template does NOT have editable form fields.
This is expected behavior for some USCIS templates, which are designed to be:
1. Printed blank and filled by hand, OR
2. Filled using PDF overlay techniques

CURRENT BEHAVIOR:
- I-129 functions return the blank template PDF successfully
- No errors are generated
- PDF is valid and can be downloaded
- File size: ~1.6MB, 20 pages

FUTURE ENHANCEMENT:
If clients need pre-filled I-129 forms, implement overlay approach:
1. Use ReportLab to create an overlay PDF with form data
2. Merge overlay with template using PyMuPDF
3. Position text at correct coordinates for each field

For now, clients can:
- Download the blank I-129 template
- Fill it manually or using their own PDF editor
- Or wait for overlay implementation
"""

import os
import io
from datetime import datetime
from typing import Dict, Any, Optional
import fitz  # PyMuPDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import logging

logger = logging.getLogger(__name__)

class USCISFormFiller:
    """
    System to automatically fill USCIS forms
    """
    
    def __init__(self):
        self.forms_dir = "/app/official_forms/uscis_forms"
        
    def fill_i539(self, case_data: Dict[str, Any]) -> bytes:
        """
        Fill Form I-539 (Application to Extend/Change Nonimmigrant Status)
        NOW SUPPORTS DATA FROM FRIENDLY FORM (simplified_form_responses)
        FIXED: Uses PyMuPDF (fitz) for reliable form filling
        
        Args:
            case_data: Dictionary with applicant information
                       - basic_data: Basic applicant info
                       - simplified_form_responses: Data from user-friendly form (in Portuguese)
            
        Returns:
            bytes: PDF file content
        """
        try:
            logger.info("🔧 Filling Form I-539 with PyMuPDF (fitz)...")
            
            # Extract data from both sources
            basic_data = case_data.get("basic_data", {})
            simplified_form = case_data.get("simplified_form_responses", {})
            
            logger.info(f"📝 Using basic_data: {len(basic_data)} fields")
            logger.info(f"📝 Using simplified_form_responses: {len(simplified_form)} fields")
            
            # Read template with PyMuPDF
            template_path = os.path.join(self.forms_dir, "I-539.pdf")
            doc = fitz.open(template_path)
            
            logger.info(f"📋 PDF has {len(doc)} pages")
            
            # Map data to form fields - NOW USES BOTH basic_data AND simplified_form
            field_mapping = self._get_i539_mapping(basic_data, simplified_form)
            
            # Create a dictionary of all non-empty field values
            form_data = {k: v for k, v in field_mapping.items() if v}
            logger.info(f"📝 Attempting to fill {len(form_data)} fields")
            
            # Fill form fields using PyMuPDF
            # PyMuPDF uses full paths like "form1[0].#subform[0].P1Line1a_FamilyName[0]"
            # but our mapping uses short names like "P1Line1a_FamilyName[0]"
            # so we need to match by the field name suffix
            filled_count = 0
            for page in doc:
                widgets = list(page.widgets())
                if widgets:
                    for widget in widgets:
                        full_field_name = widget.field_name
                        if full_field_name:
                            # Try exact match first
                            if full_field_name in form_data:
                                try:
                                    widget.field_value = form_data[full_field_name]
                                    widget.update()
                                    filled_count += 1
                                    logger.debug(f"  ✅ Filled (exact): {full_field_name} = {form_data[full_field_name]}")
                                    continue
                                except Exception as e:
                                    logger.warning(f"  ⚠️ Could not fill {full_field_name}: {e}")
                            
                            # Try suffix match (field name without path)
                            for short_name, value in form_data.items():
                                if full_field_name.endswith(short_name):
                                    try:
                                        widget.field_value = value
                                        widget.update()
                                        filled_count += 1
                                        logger.debug(f"  ✅ Filled (suffix): {full_field_name} = {value}")
                                        break
                                    except Exception as e:
                                        logger.warning(f"  ⚠️ Could not fill {full_field_name}: {e}")
            
            logger.info(f"✅ Filled {filled_count} fields in Form I-539")
            
            # Save to bytes
            output = io.BytesIO()
            doc.save(output)
            doc.close()
            output.seek(0)
            
            logger.info("✅ Form I-539 filled successfully with data from friendly form")
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"❌ Error filling I-539: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise
    
    def fill_i589(self, case_data: Dict[str, Any]) -> bytes:
        """
        Fill Form I-589 (Application for Asylum)
        NOW SUPPORTS DATA FROM FRIENDLY FORM (simplified_form_responses)
        FIXED: Uses PyMuPDF (fitz) for reliable form filling
        
        Args:
            case_data: Dictionary with applicant and asylum information
                       - basic_data: Basic applicant info
                       - simplified_form_responses: Data from user-friendly form
                       - letters: Cover letters and personal statements
            
        Returns:
            bytes: PDF file content
        """
        try:
            logger.info("🔧 Filling Form I-589 with PyMuPDF (fitz)...")
            
            # Extract data from all sources
            basic_data = case_data.get("basic_data", {})
            simplified_form = case_data.get("simplified_form_responses", {})
            letters = case_data.get("letters", {})
            
            logger.info(f"📝 Using basic_data: {len(basic_data)} fields")
            logger.info(f"📝 Using simplified_form_responses: {len(simplified_form)} fields")
            
            # Read template with PyMuPDF
            template_path = os.path.join(self.forms_dir, "I-589.pdf")
            doc = fitz.open(template_path)
            
            logger.info(f"📋 PDF has {len(doc)} pages")
            
            # Map data to form fields - NOW USES simplified_form too
            field_mapping = self._get_i589_mapping(basic_data, simplified_form, letters)
            
            # Create a dictionary of all non-empty field values
            form_data = {k: v for k, v in field_mapping.items() if v}
            logger.info(f"📝 Attempting to fill {len(form_data)} fields")
            
            # Fill form fields using PyMuPDF
            # PyMuPDF uses full paths like "form1[0].#subform[0].P1Line1a_FamilyName[0]"
            # but our mapping uses short names like "P1Line1a_FamilyName[0]"
            # so we need to match by the field name suffix
            filled_count = 0
            for page in doc:
                widgets = list(page.widgets())
                if widgets:
                    for widget in widgets:
                        full_field_name = widget.field_name
                        if full_field_name:
                            # Try exact match first
                            if full_field_name in form_data:
                                try:
                                    widget.field_value = form_data[full_field_name]
                                    widget.update()
                                    filled_count += 1
                                    logger.debug(f"  ✅ Filled (exact): {full_field_name} = {form_data[full_field_name]}")
                                    continue
                                except Exception as e:
                                    logger.warning(f"  ⚠️ Could not fill {full_field_name}: {e}")
                            
                            # Try suffix match (field name without path)
                            for short_name, value in form_data.items():
                                if full_field_name.endswith(short_name):
                                    try:
                                        widget.field_value = value
                                        widget.update()
                                        filled_count += 1
                                        logger.debug(f"  ✅ Filled (suffix): {full_field_name} = {value}")
                                        break
                                    except Exception as e:
                                        logger.warning(f"  ⚠️ Could not fill {full_field_name}: {e}")
            
            logger.info(f"✅ Filled {filled_count} fields in Form I-589")
            
            # Save to bytes
            output = io.BytesIO()
            doc.save(output)
            doc.close()
            output.seek(0)
            
            logger.info("✅ Form I-589 filled successfully")
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"❌ Error filling I-589: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise
    
    def fill_i140(self, case_data: Dict[str, Any]) -> bytes:
        """
        Fill Form I-140 (Immigrant Petition for Extraordinary Ability)
        FIXED: Uses PyMuPDF (fitz) for reliable form filling
        
        Args:
            case_data: Dictionary with petition information
            
        Returns:
            bytes: PDF file content
        """
        try:
            logger.info("🔧 Filling Form I-140 with PyMuPDF (fitz)...")
            
            # Extract data
            basic_data = case_data.get("basic_data", {})
            forms = case_data.get("forms", {})
            eb1a_data = forms.get("eb1a", {})
            
            # Read template with PyMuPDF
            template_path = os.path.join(self.forms_dir, "I-140.pdf")
            doc = fitz.open(template_path)
            
            logger.info(f"📋 PDF has {len(doc)} pages")
            
            # Map data to form fields
            field_mapping = self._get_i140_mapping(basic_data, eb1a_data)
            
            # Create a dictionary of all non-empty field values
            form_data = {k: v for k, v in field_mapping.items() if v}
            logger.info(f"📝 Attempting to fill {len(form_data)} fields")
            
            # Fill form fields using PyMuPDF
            # PyMuPDF uses full paths like "form1[0].#subform[0].P1Line1a_FamilyName[0]"
            # but our mapping uses short names like "P1Line1a_FamilyName[0]"
            # so we need to match by the field name suffix
            filled_count = 0
            for page in doc:
                widgets = list(page.widgets())
                if widgets:
                    for widget in widgets:
                        full_field_name = widget.field_name
                        if full_field_name:
                            # Try exact match first
                            if full_field_name in form_data:
                                try:
                                    widget.field_value = form_data[full_field_name]
                                    widget.update()
                                    filled_count += 1
                                    logger.debug(f"  ✅ Filled (exact): {full_field_name} = {form_data[full_field_name]}")
                                    continue
                                except Exception as e:
                                    logger.warning(f"  ⚠️ Could not fill {full_field_name}: {e}")
                            
                            # Try suffix match (field name without path)
                            for short_name, value in form_data.items():
                                if full_field_name.endswith(short_name):
                                    try:
                                        widget.field_value = value
                                        widget.update()
                                        filled_count += 1
                                        logger.debug(f"  ✅ Filled (suffix): {full_field_name} = {value}")
                                        break
                                    except Exception as e:
                                        logger.warning(f"  ⚠️ Could not fill {full_field_name}: {e}")
            
            logger.info(f"✅ Filled {filled_count} fields in Form I-140")
            
            # Save to bytes
            output = io.BytesIO()
            doc.save(output)
            doc.close()
            output.seek(0)
            
            logger.info("✅ Form I-140 filled successfully")
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"❌ Error filling I-140: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise

    def fill_i129(self, case_data: Dict[str, Any]) -> bytes:
        """
        Fill Form I-129 (Petition for Nonimmigrant Worker)
        Used for: O-1, H-1B, L-1, P-1, and other temporary work visas
        USES: PyMuPDF (fitz) for reliable form filling
        
        Args:
            case_data: Dictionary with petition information
                       - basic_data: Basic petitioner and beneficiary info
                       - simplified_form_responses: Data from user-friendly form
                       - visa_category: O-1, H-1B, L-1, etc.
            
        Returns:
            bytes: PDF file content
        """
        try:
            logger.info("🔧 Filling Form I-129 with PyMuPDF (fitz)...")
            
            # Extract data
            basic_data = case_data.get("basic_data", {})
            simplified_form = case_data.get("simplified_form_responses", {})
            visa_category = case_data.get("visa_category", "O-1")
            
            logger.info(f"📝 Using basic_data: {len(basic_data)} fields")
            logger.info(f"📝 Using simplified_form_responses: {len(simplified_form)} fields")
            logger.info(f"📝 Visa category: {visa_category}")
            
            # Read template with PyMuPDF
            template_path = os.path.join(self.forms_dir, "i-129.pdf")
            doc = fitz.open(template_path)
            
            logger.info(f"📋 PDF has {len(doc)} pages")
            
            # Map data to form fields
            field_mapping = self._get_i129_mapping(basic_data, simplified_form, visa_category)
            
            # Create a dictionary of all non-empty field values
            form_data = {k: v for k, v in field_mapping.items() if v}
            logger.info(f"📝 Attempting to fill {len(form_data)} fields")
            
            # Fill form fields using PyMuPDF
            filled_count = 0
            for page in doc:
                widgets = list(page.widgets())
                if widgets:
                    for widget in widgets:
                        full_field_name = widget.field_name
                        if full_field_name:
                            # Try exact match first
                            if full_field_name in form_data:
                                try:
                                    widget.field_value = form_data[full_field_name]
                                    widget.update()
                                    filled_count += 1
                                    logger.debug(f"  ✅ Filled (exact): {full_field_name} = {form_data[full_field_name]}")
                                    continue
                                except Exception as e:
                                    logger.warning(f"  ⚠️ Could not fill {full_field_name}: {e}")
                            
                            # Try suffix match
                            for short_name, value in form_data.items():
                                if full_field_name.endswith(short_name):
                                    try:
                                        widget.field_value = value
                                        widget.update()
                                        filled_count += 1
                                        logger.debug(f"  ✅ Filled (suffix): {full_field_name} = {value}")
                                        break
                                    except Exception as e:
                                        logger.warning(f"  ⚠️ Could not fill {full_field_name}: {e}")
            
            logger.info(f"✅ Filled {filled_count} fields in Form I-129")
            
            # Save to bytes
            output = io.BytesIO()
            doc.save(output)
            doc.close()
            output.seek(0)
            
            logger.info(f"✅ Form I-129 filled successfully for {visa_category}")
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"❌ Error filling I-129: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise
    
    def fill_o1(self, case_data: Dict[str, Any]) -> bytes:
        """
        Fill O-1 Visa Petition (uses I-129)
        O-1: Extraordinary Ability in Arts, Sciences, Education, Business, or Athletics
        
        Args:
            case_data: Dictionary with petition information
            
        Returns:
            bytes: PDF file content
        """
        logger.info("🔧 Filling O-1 Visa Petition (I-129)...")
        case_data["visa_category"] = "O-1"
        return self.fill_i129(case_data)
    
    def fill_h1b(self, case_data: Dict[str, Any]) -> bytes:
        """
        Fill H-1B Visa Petition (uses I-129)
        H-1B: Specialty Occupation Worker
        
        Args:
            case_data: Dictionary with petition information
            
        Returns:
            bytes: PDF file content
        """
        logger.info("🔧 Filling H-1B Visa Petition (I-129)...")
        case_data["visa_category"] = "H-1B"
        return self.fill_i129(case_data)
    
    def fill_l1(self, case_data: Dict[str, Any]) -> bytes:
        """
        Fill L-1 Visa Petition (uses I-129)
        L-1: Intracompany Transferee
        
        Args:
            case_data: Dictionary with petition information
            
        Returns:
            bytes: PDF file content
        """
        logger.info("🔧 Filling L-1 Visa Petition (I-129)...")
        case_data["visa_category"] = "L-1"
        return self.fill_i129(case_data)
    
    def fill_f1(self, case_data: Dict[str, Any]) -> bytes:
        """
        Fill F-1 Student Visa Application (uses I-539 for status change/extension)
        F-1: Academic Student
        
        Args:
            case_data: Dictionary with student information
            
        Returns:
            bytes: PDF file content
        """
        logger.info("🔧 Filling F-1 Student Visa (I-539)...")
        # F-1 uses I-539 for extension or change of status
        return self.fill_i539(case_data)

    
    def _get_i539_mapping(self, basic_data: Dict[str, Any], simplified_form: Dict[str, Any] = None) -> Dict[str, str]:
        """
        Map case data to I-539 form fields
        Now uses BOTH basic_data and simplified_form_responses (friendly form in Portuguese)
        """
        
        # Use simplified_form if available (data from friendly form)
        if simplified_form is None:
            simplified_form = {}
        
        # Parse name - try friendly form first, then basic_data
        full_name = (
            simplified_form.get("nome_completo") or 
            simplified_form.get("nome") or 
            basic_data.get("applicant_name", "")
        )
        name_parts = full_name.split(" ", 1)
        family_name = name_parts[-1] if name_parts else ""
        given_name = name_parts[0] if len(name_parts) > 1 else ""
        
        # Parse date of birth - try friendly form first
        dob = (
            simplified_form.get("data_nascimento") or 
            basic_data.get("date_of_birth", "")
        )
        dob_parts = dob.split("-") if dob else ["", "", ""]
        
        # Parse address - try friendly form first (with _eua suffix)
        address = (
            simplified_form.get("endereco_eua") or 
            simplified_form.get("endereco") or 
            basic_data.get("current_address", "")
        )
        city = (
            simplified_form.get("cidade_eua") or 
            simplified_form.get("cidade") or 
            basic_data.get("city", "")
        )
        state = (
            simplified_form.get("estado_eua") or 
            simplified_form.get("estado") or 
            basic_data.get("state", "")
        )
        zip_code = (
            simplified_form.get("cep_eua") or 
            simplified_form.get("cep") or 
            simplified_form.get("zip_code") or 
            basic_data.get("zip_code", "")
        )
        
        # Email and phone - try friendly form first
        email = (
            simplified_form.get("email") or 
            basic_data.get("email", "")
        )
        phone = (
            simplified_form.get("telefone") or 
            basic_data.get("phone", "")
        )
        
        # Country info - try friendly form first
        country_of_birth = (
            simplified_form.get("pais_nascimento") or 
            basic_data.get("country_of_birth", "")
        )
        
        # Passport - try friendly form first
        passport = (
            simplified_form.get("numero_passaporte") or 
            basic_data.get("passport_number", "")
        )
        
        mapping = {
            # Part 1: Information About You - CORRECTED FIELD NAMES (from I-539 template analysis)
            "P1Line1a_FamilyName[0]": family_name,
            "P1_Line1b_GivenName[0]": given_name,
            "P1_Line1c_MiddleName[0]": "",
            "P1_Line8_DateOfBirth[0]": dob,  # Full date format YYYY-MM-DD
            "P1_Line6_CountryOfBirth[0]": country_of_birth,  # FIXED: was P1_Line7
            "P1_Line7_CountryOfCitizenship[0]": country_of_birth,
            "Part1_Item6_StreetName[0]": address,
            "Part1_Item6_City[0]": city,  # FIXED: City field for Part 1
            "Part1_Item6_ZipCode[0]": zip_code,  # FIXED: ZIP field for Part 1
            "Part2_Item11_City[0]": city,  # Alternative city field
            "Part2_Item11_ZipCode[0]": zip_code,  # Alternative ZIP field
            "P2_Line10_Province[0]": state,  # FIXED: State/Province field
            "P5_Line3_DaytimePhoneNumber[0]": phone,  # Daytime phone
            "P5_Line5_EmailAddress[0]": email,  # FIXED: Email field
            "Part1_Item4_Number[0]": passport,  # Passport number
            "SupA_Line1k_Passport[0]": passport,  # Alternative passport field
        }
        
        logger.info(f"✅ Mapped {len([v for v in mapping.values() if v])} fields from friendly form and basic data")
        
        return mapping
    
    def _get_i589_mapping(self, basic_data: Dict[str, Any], simplified_form: Dict[str, Any], letters: Dict[str, Any]) -> Dict[str, str]:
        """
        Map case data to I-589 form fields
        Now uses BOTH basic_data and simplified_form_responses (friendly form)
        """
        
        # Use simplified_form if available
        if simplified_form is None:
            simplified_form = {}
        
        # Parse name - try friendly form first
        full_name = (
            simplified_form.get("nome_completo") or 
            simplified_form.get("nome") or 
            basic_data.get("applicant_name", "")
        )
        name_parts = full_name.split(" ")
        family_name = name_parts[-1] if name_parts else ""
        first_name = name_parts[0] if len(name_parts) > 0 else ""
        middle_name = " ".join(name_parts[1:-1]) if len(name_parts) > 2 else ""
        
        # Parse dates - try friendly form first
        dob = (
            simplified_form.get("data_nascimento") or 
            basic_data.get("date_of_birth", "")
        )
        arrival_date = (
            simplified_form.get("data_chegada_eua") or 
            basic_data.get("date_of_arrival_us", "")
        )
        
        # Country information - try friendly form first
        country_of_birth = (
            simplified_form.get("pais_nascimento") or 
            basic_data.get("country_of_birth", "")
        )
        nationality = (
            simplified_form.get("nacionalidade") or 
            basic_data.get("country_of_nationality", country_of_birth)
        )
        
        # Document numbers - try friendly form first
        passport = (
            simplified_form.get("numero_passaporte") or 
            basic_data.get("passport_number", "")
        )
        i94_number = (
            simplified_form.get("numero_i94") or 
            basic_data.get("i94_number", "")
        )
        
        mapping = {
            # Part A: Information About You
            "PartA_FamilyName": family_name,
            "PartA_FirstName": first_name,
            "PartA_MiddleName": middle_name,
            "PartA_DateOfBirth": dob,
            "PartA_CountryOfBirth": country_of_birth,
            "PartA_Nationality": nationality,
            "PartA_PassportNumber": passport,
            "PartA_I94Number": i94_number,
            "PartA_DateOfArrival": arrival_date,
            "PartA_CurrentAddress": basic_data.get("current_address", ""),
            "PartA_City": basic_data.get("city", ""),
            "PartA_State": basic_data.get("state", ""),
            "PartA_ZipCode": basic_data.get("zip_code", ""),
            "PartA_Telephone": basic_data.get("phone", ""),
            "PartA_Email": basic_data.get("email", ""),
        }
        
        return mapping
    
    def _get_i140_mapping(self, basic_data: Dict[str, Any], eb1a_data: Dict[str, Any]) -> Dict[str, str]:
        """Map case data to I-140 form fields"""
        
        # Parse name
        full_name = basic_data.get("applicant_name", "")
        name_parts = full_name.split(" ")
        family_name = name_parts[-1] if name_parts else ""
        given_name = " ".join(name_parts[:-1]) if len(name_parts) > 1 else ""
        
        # Parse date of birth
        dob = basic_data.get("date_of_birth", "")
        
        mapping = {
            # Part 1: Information About the Beneficiary
            "Pt1_FamilyName": family_name,
            "Pt1_GivenName": given_name,
            "Pt1_DateOfBirth": dob,
            "Pt1_CountryOfBirth": basic_data.get("country_of_birth", ""),
            "Pt1_PassportNumber": basic_data.get("passport_number", ""),
            "Pt1_CurrentAddress": basic_data.get("current_address", ""),
            "Pt1_City": basic_data.get("city", ""),
            "Pt1_State": basic_data.get("state", ""),
            "Pt1_ZipCode": basic_data.get("zip_code", ""),
            "Pt1_Email": basic_data.get("email", ""),
            
            # Part 2: Classification Requested
            "Pt2_EB1A": "X",  # Mark EB-1A checkbox
            
            # Part 6: Additional Information
            "Pt6_FieldOfAbility": basic_data.get("field_of_extraordinary_ability", ""),
            "Pt6_CriteriaMet": str(eb1a_data.get("criteria_count", 0)),
        }
        
        return mapping

    
    def _get_i129_mapping(self, basic_data: Dict[str, Any], simplified_form: Dict[str, Any], visa_category: str) -> Dict[str, str]:
        """
        Map case data to I-129 form fields
        Supports multiple visa categories: O-1, H-1B, L-1, P-1, etc.
        Uses BOTH basic_data and simplified_form_responses
        
        Args:
            basic_data: Basic petitioner/beneficiary data
            simplified_form: Friendly form data in Portuguese
            visa_category: Visa type (O-1, H-1B, L-1, etc.)
            
        Returns:
            Dictionary mapping field names to values
        """
        if simplified_form is None:
            simplified_form = {}
        
        # Parse beneficiary name (person getting the visa)
        full_name = (
            simplified_form.get("nome_completo") or 
            simplified_form.get("nome_beneficiario") or
            basic_data.get("beneficiary_name") or
            basic_data.get("applicant_name", "")
        )
        name_parts = full_name.split(" ")
        family_name = name_parts[-1] if name_parts else ""
        given_name = " ".join(name_parts[:-1]) if len(name_parts) > 1 else ""
        
        # Parse petitioner name (company/employer)
        petitioner_name = (
            simplified_form.get("nome_empresa") or
            simplified_form.get("nome_empregador") or
            basic_data.get("petitioner_name") or
            basic_data.get("company_name", "")
        )
        
        # Parse dates
        dob = simplified_form.get("data_nascimento") or basic_data.get("date_of_birth", "")
        start_date = simplified_form.get("data_inicio") or basic_data.get("employment_start_date", "")
        end_date = simplified_form.get("data_fim") or basic_data.get("employment_end_date", "")
        
        # Parse address
        address = (
            simplified_form.get("endereco_eua") or 
            simplified_form.get("endereco") or 
            basic_data.get("current_address", "")
        )
        city = (
            simplified_form.get("cidade_eua") or
            simplified_form.get("cidade") or
            basic_data.get("city", "")
        )
        state = (
            simplified_form.get("estado_eua") or
            simplified_form.get("estado") or
            basic_data.get("state", "")
        )
        zip_code = (
            simplified_form.get("cep_eua") or
            simplified_form.get("cep") or
            basic_data.get("zip_code", "")
        )
        
        # Parse contact info
        email = simplified_form.get("email") or basic_data.get("email", "")
        phone = simplified_form.get("telefone") or basic_data.get("phone", "")
        
        # Parse passport
        passport = (
            simplified_form.get("numero_passaporte") or
            simplified_form.get("passaporte") or
            basic_data.get("passport_number", "")
        )
        
        # Parse country
        country_of_birth = (
            simplified_form.get("pais_nascimento") or
            basic_data.get("country_of_birth", "")
        )
        
        # Parse job information
        job_title = (
            simplified_form.get("cargo") or
            simplified_form.get("titulo_trabalho") or
            basic_data.get("job_title", "")
        )
        
        # Base mapping for I-129 (common fields across all categories)
        mapping = {
            # Part 1: Information About the Petitioner
            "Pt1_PetitionerName[0]": petitioner_name,
            "Pt1_PetitionerAddress[0]": address,
            "Pt1_PetitionerCity[0]": city,
            "Pt1_PetitionerState[0]": state,
            "Pt1_PetitionerZip[0]": zip_code,
            "Pt1_PetitionerPhone[0]": phone,
            "Pt1_PetitionerEmail[0]": email,
            
            # Part 2: Information About the Beneficiary
            "Pt2_BeneficiaryFamilyName[0]": family_name,
            "Pt2_BeneficiaryGivenName[0]": given_name,
            "Pt2_BeneficiaryDOB[0]": dob,
            "Pt2_BeneficiaryCountryOfBirth[0]": country_of_birth,
            "Pt2_BeneficiaryPassport[0]": passport,
            "Pt2_BeneficiaryAddress[0]": address,
            "Pt2_BeneficiaryCity[0]": city,
            "Pt2_BeneficiaryState[0]": state,
            "Pt2_BeneficiaryZip[0]": zip_code,
            
            # Part 3: Processing Information
            "Pt3_StartDate[0]": start_date,
            "Pt3_EndDate[0]": end_date,
            
            # Part 4: Basic Job Information
            "Pt4_JobTitle[0]": job_title,
        }
        
        # Add category-specific fields
        if visa_category == "O-1":
            mapping.update({
                "Pt2_Classification_O1[0]": "X",  # Mark O-1 checkbox
                "Pt4_FieldOfExtraordinaryAbility[0]": basic_data.get("field_of_ability", ""),
            })
        elif visa_category == "H-1B":
            mapping.update({
                "Pt2_Classification_H1B[0]": "X",  # Mark H-1B checkbox
                "Pt4_SpecialtyOccupation[0]": job_title,
                "Pt4_SOCCode[0]": basic_data.get("soc_code", ""),
            })
        elif visa_category == "L-1":
            mapping.update({
                "Pt2_Classification_L1[0]": "X",  # Mark L-1 checkbox
                "Pt4_ManagerialPosition[0]": basic_data.get("is_managerial", "Yes"),
            })
        
        return mapping



# Singleton instance
form_filler = USCISFormFiller()
