"""
USCIS Form Filler System
Auto-fill official USCIS forms with case data
FIXED: Now uses pypdf for reliable PDF form filling
"""

import os
import io
from datetime import datetime
from typing import Dict, Any, Optional
import pypdf
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
        FIXED: Uses pypdf for reliable form filling
        
        Args:
            case_data: Dictionary with applicant information
                       - basic_data: Basic applicant info
                       - simplified_form_responses: Data from user-friendly form (in Portuguese)
            
        Returns:
            bytes: PDF file content
        """
        try:
            logger.info("🔧 Filling Form I-539 with pypdf...")
            
            # Extract data from both sources
            basic_data = case_data.get("basic_data", {})
            simplified_form = case_data.get("simplified_form_responses", {})
            
            logger.info(f"📝 Using basic_data: {len(basic_data)} fields")
            logger.info(f"📝 Using simplified_form_responses: {len(simplified_form)} fields")
            
            # Read template
            template_path = os.path.join(self.forms_dir, "I-539.pdf")
            reader = pypdf.PdfReader(template_path)
            writer = pypdf.PdfWriter()
            
            # Get form fields count
            field_count = 0
            if reader.get_form_text_fields():
                field_count = len(reader.get_form_text_fields())
                logger.info(f"📋 Found {field_count} form fields in I-539")
            
            # Map data to form fields - NOW USES BOTH basic_data AND simplified_form
            field_mapping = self._get_i539_mapping(basic_data, simplified_form)
            
            # Clone all pages
            for page in reader.pages:
                writer.add_page(page)
            
            # Fill form fields using pypdf
            writer.update_page_form_field_values(
                writer.pages[0],  # Update fields on first page (they apply to all)
                field_mapping
            )
            
            filled_count = len([v for v in field_mapping.values() if v])
            logger.info(f"✅ Mapped {filled_count} non-empty fields in Form I-539")
            
            # Generate PDF
            output = io.BytesIO()
            writer.write(output)
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
        FIXED: Uses pdfrw for reliable form filling
        
        Args:
            case_data: Dictionary with applicant and asylum information
                       - basic_data: Basic applicant info
                       - simplified_form_responses: Data from user-friendly form
                       - letters: Cover letters and personal statements
            
        Returns:
            bytes: PDF file content
        """
        try:
            logger.info("🔧 Filling Form I-589 with pdfrw...")
            
            # Extract data from all sources
            basic_data = case_data.get("basic_data", {})
            simplified_form = case_data.get("simplified_form_responses", {})
            letters = case_data.get("letters", {})
            
            logger.info(f"📝 Using basic_data: {len(basic_data)} fields")
            logger.info(f"📝 Using simplified_form_responses: {len(simplified_form)} fields")
            
            # Read template
            template_path = os.path.join(self.forms_dir, "I-589.pdf")
            template = PdfrwReader(template_path)
            
            # Get form fields count
            field_count = 0
            if template.Root.AcroForm:
                field_count = len(template.Root.AcroForm.Fields) if template.Root.AcroForm.Fields else 0
                logger.info(f"📋 Found {field_count} form fields in I-589")
            
            # Map data to form fields - NOW USES simplified_form too
            field_mapping = self._get_i589_mapping(basic_data, simplified_form, letters)
            
            # Fill form fields using pdfrw
            filled_count = self._fill_pdf_fields_pdfrw(template, field_mapping)
            
            logger.info(f"✅ Filled {filled_count} fields in Form I-589")
            
            # Generate PDF
            output = io.BytesIO()
            PdfrwWriter().write(output, template)
            output.seek(0)
            
            logger.info("✅ Form I-589 filled successfully")
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"❌ Error filling I-589: {str(e)}")
            raise
    
    def fill_i140(self, case_data: Dict[str, Any]) -> bytes:
        """
        Fill Form I-140 (Immigrant Petition for Extraordinary Ability)
        FIXED: Uses pdfrw for reliable form filling
        
        Args:
            case_data: Dictionary with petition information
            
        Returns:
            bytes: PDF file content
        """
        try:
            logger.info("🔧 Filling Form I-140 with pdfrw...")
            
            # Extract data
            basic_data = case_data.get("basic_data", {})
            forms = case_data.get("forms", {})
            eb1a_data = forms.get("eb1a", {})
            
            # Read template
            template_path = os.path.join(self.forms_dir, "I-140.pdf")
            template = PdfrwReader(template_path)
            
            # Get form fields count
            field_count = 0
            if template.Root.AcroForm:
                field_count = len(template.Root.AcroForm.Fields) if template.Root.AcroForm.Fields else 0
                logger.info(f"📋 Found {field_count} form fields in I-140")
            
            # Map data to form fields
            field_mapping = self._get_i140_mapping(basic_data, eb1a_data)
            
            # Fill form fields using pdfrw
            filled_count = self._fill_pdf_fields_pdfrw(template, field_mapping)
            
            logger.info(f"✅ Filled {filled_count} fields in Form I-140")
            
            # Generate PDF
            output = io.BytesIO()
            PdfrwWriter().write(output, template)
            output.seek(0)
            
            logger.info("✅ Form I-140 filled successfully")
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"❌ Error filling I-140: {str(e)}")
            raise
    
    
    def _fill_pdf_fields_pdfrw(self, template, field_mapping: Dict[str, str]) -> int:
        """
        Fill PDF form fields using pdfrw library
        This is more reliable than PyPDF2 for form filling
        
        Args:
            template: PDF template loaded with pdfrw
            field_mapping: Dictionary mapping field names to values
            
        Returns:
            int: Number of fields filled
        """
        filled_count = 0
        
        if not template.Root.AcroForm:
            logger.warning("PDF template has no AcroForm")
            return 0
        
        if not template.Root.AcroForm.Fields:
            logger.warning("PDF AcroForm has no Fields")
            return 0
        
        # Iterate through all fields in the PDF
        for field in template.Root.AcroForm.Fields:
            field_name = field.T
            if field_name:
                # Remove parentheses from field name (pdfrw format)
                field_name_str = str(field_name)[1:-1] if str(field_name).startswith('(') else str(field_name)
                
                # Check if we have a value for this field
                if field_name_str in field_mapping:
                    field_value = field_mapping[field_name_str]
                    if field_value:
                        # Set the field value
                        field.V = PdfString.from_unicode(str(field_value))
                        # Also set the appearance stream
                        field.AP = PdfDict(N=PdfDict())
                        # Mark field as filled
                        filled_count += 1
                        
                        logger.debug(f"  ✓ Filled field '{field_name_str}' = '{field_value}'")
        
        # Update the PDF to reflect the filled fields
        if template.Root.AcroForm:
            template.Root.AcroForm.update(PdfDict(NeedAppearances=PdfString('true')))
        
        return filled_count

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
            # Part 1: Information About You
            "Pt1Line1a_FamilyName": family_name,
            "Pt1Line1b_GivenName": given_name,
            "Pt1Line2_MiddleName": "",
            "Pt1Line3a_DateOfBirth_Month": dob_parts[1] if len(dob_parts) > 1 else "",
            "Pt1Line3a_DateOfBirth_Day": dob_parts[2] if len(dob_parts) > 2 else "",
            "Pt1Line3a_DateOfBirth_Year": dob_parts[0] if len(dob_parts) > 0 else "",
            "Pt1Line4_CountryOfBirth": country_of_birth,
            "Pt1Line5_CountryOfCitizenship": country_of_birth,
            "Pt1Line6_PassportNumber": passport,
            "Pt1Line7a_StreetNumberName": address,
            "Pt1Line7b_AptSteFlrNumber": "",
            "Pt1Line7c_CityOrTown": city,
            "Pt1Line7d_State": state,
            "Pt1Line7e_ZipCode": zip_code,
            "Pt1Line8_Email": email,
            "Pt1Line9_DaytimeTelephone": phone,
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


# Singleton instance
form_filler = USCISFormFiller()
