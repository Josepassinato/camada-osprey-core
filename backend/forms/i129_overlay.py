"""
I-129 Widget-Based Form Filler
Preenche formulário I-129 oficial do USCIS (Edition 02/27/26) usando widgets PDF nativos.
38 páginas, 218+ campos preenchíveis.
"""

import logging
from typing import Any, Dict

import fitz  # PyMuPDF

logger = logging.getLogger(__name__)


# Mapping: friendly key -> PDF widget field name (full path)
FIELD_MAP = {
    # === PAGE 1: Part 1 - Petitioner Information ===
    "petitioner_family_name": "form1[0].#subform[0].Line1_FamilyName[0]",
    "petitioner_given_name": "form1[0].#subform[0].Line1_GivenName[0]",
    "petitioner_middle_name": "form1[0].#subform[0].Line1_MiddleName[0]",
    "petitioner_company": "form1[0].#subform[0].Line3_CompanyorOrgName[0]",
    "petitioner_street": "form1[0].#subform[0].Line7b_StreetNumberName[0]",
    "petitioner_city": "form1[0].#subform[0].Line_CityTown[0]",
    "petitioner_state": "form1[0].#subform[0].P1_Line3_State[0]",
    "petitioner_zip": "form1[0].#subform[0].P1_Line3_ZipCode[0]",
    "petitioner_country": "form1[0].#subform[0].P1_Line3_Country[0]",
    "petitioner_ein": "form1[0].#subform[0].TextField1[0]",
    "petitioner_phone": "form1[0].#subform[0].Line2_DaytimePhoneNumber1_Part8[0]",
    "petitioner_email": "form1[0].#subform[0].Line9_EmailAddress[0]",
    "petitioner_in_care_of": "form1[0].#subform[0].Line7a_InCareofName[0]",

    # === PAGE 2: Part 2 & Part 3 - Petition Info & Beneficiary ===
    "classification_symbol": "form1[0].#subform[1].Part2_ClassificationSymbol[0]",
    "total_workers": "form1[0].#subform[1].TtlNumbersofWorker[0]",
    "beneficiary_family_name": "form1[0].#subform[1].Part3_Line2_FamilyName[0]",
    "beneficiary_given_name": "form1[0].#subform[1].Part3_Line2_GivenName[0]",
    "beneficiary_middle_name": "form1[0].#subform[1].Part3_Line2_MiddleName[0]",
    "receipt_number": "form1[0].#subform[1].Line1_ReceiptNumber[0]",
    "beneficiary_ssn": "form1[0].#subform[1].Line4_SSN[0]",
    "beneficiary_ein": "form1[0].#subform[1].Line3_TaxNumber[0]",

    # === PAGE 3: Beneficiary details ===
    "beneficiary_dob": "form1[0].#subform[2].Line6_DateOfBirth[0]",
    "beneficiary_country_birth": "form1[0].#subform[2].Part3Line4_CountryOfBirth[0]",
    "beneficiary_country_citizen": "form1[0].#subform[2].Part3Line4_CountryOfCitizenship[0]",
    "beneficiary_alien_number": "form1[0].#subform[2].Line1_AlienNumber[0]",
    "beneficiary_passport_number": "form1[0].#subform[2].Part3Line5_PassportorTravDoc[0]",
    "beneficiary_passport_country": "form1[0].#subform[2].Line_CountryOfIssuance[0]",
    "beneficiary_passport_expiry": "form1[0].#subform[2].Line11e_ExpDate[0]",
    "beneficiary_i94_number": "form1[0].#subform[2].Part3Line5_ArrivalDeparture[0]",
    "beneficiary_arrival_date": "form1[0].#subform[2].Part3Line5_DateofArrival[0]",
    "beneficiary_status_expires": "form1[0].#subform[2].Line11h_DateStatusExpires[0]",
    "beneficiary_sevis": "form1[0].#subform[2].Line5_SEVIS[0]",
    "beneficiary_ead": "form1[0].#subform[2].Line5_EAD[0]",
    "beneficiary_us_street": "form1[0].#subform[2].Line8a_StreetNumberName[0]",
    "beneficiary_us_city": "form1[0].#subform[2].Line8d_CityTown[0]",
    "beneficiary_us_state": "form1[0].#subform[2].Line8e_State[0]",
    "beneficiary_us_zip": "form1[0].#subform[2].Line8f_ZipCode[0]",
    "beneficiary_ssn_p3": "form1[0].#subform[2].Line5_SSN[0]",

    # === PAGE 5: Part 5 - Employment Info ===
    "job_title": "form1[0].#subform[4].Part5_Q1_JobTitle[0]",
    "lca_number": "form1[0].#subform[4].Part5_Q2_LCAorETA[0]",
    "work_street": "form1[0].#subform[4].P5Line3a_StreetNumberName[0]",
    "work_city": "form1[0].#subform[4].P5Line3a_CityTown[0]",
    "work_state": "form1[0].#subform[4].P5Line3a_State[0]",
    "work_zip": "form1[0].#subform[4].P5Line3a_ZipCode[0]",
    "wage_amount": "form1[0].#subform[4].Line8_Wages[0]",
    "wage_per": "form1[0].#subform[4].Line8_Per[0]",
    "hours_per_week": "form1[0].#subform[4].P5Line9_Hours[0]",
    "employment_start": "form1[0].#subform[4].Part5_Q10_DateFrom[0]",
    "employment_end": "form1[0].#subform[4].Part5_Q10_DateTo[0]",

    # === PAGE 6: Part 5 continued - Employer details ===
    "business_type": "form1[0].#subform[5].Part5Line12_TypeofBusiness[0]",
    "year_established": "form1[0].#subform[5].P5Line13_YearEstablished[0]",
    "num_employees": "form1[0].#subform[5].P5Line14_NumberofEmployees[0]",
    "gross_income": "form1[0].#subform[5].Line15_GrossAnnualIncome[0]",
    "net_income": "form1[0].#subform[5].Line16_NetAnnualIncome[0]",
}


class I129WidgetFiller:
    """Fill I-129 using native PDF widget fields."""

    def fill_i129(
        self, template_path: str, output_path: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        try:
            logger.info("🖊️ Filling I-129 via widget fields...")
            doc = fitz.open(template_path)

            filled = 0
            total = len(FIELD_MAP)

            for friendly_key, widget_name in FIELD_MAP.items():
                value = data.get(friendly_key)
                if not value:
                    continue

                # Find the widget across all pages
                found = False
                for page in doc:
                    for widget in page.widgets():
                        if widget.field_name == widget_name:
                            widget.field_value = str(value)
                            widget.update()
                            filled += 1
                            found = True
                            break
                    if found:
                        break

                if not found:
                    logger.debug(f"Widget not found: {widget_name} for key {friendly_key}")

            doc.save(output_path)
            doc.close()

            fill_rate = (filled / total * 100) if total > 0 else 0
            logger.info(f"✅ I-129 filled: {filled}/{total} fields ({fill_rate:.1f}%)")

            return {
                "success": True,
                "filled_fields": filled,
                "total_fields": total,
                "fill_rate": fill_rate,
                "output_path": output_path,
            }

        except Exception as e:
            logger.error(f"❌ Error filling I-129: {e}")
            return {"success": False, "error": str(e)}


# Global instance
i129_filler = I129WidgetFiller()


def fill_i129_form(
    template_path: str, output_path: str, friendly_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Fill I-129 from friendly data dict.

    Accepts flat keys matching FIELD_MAP or nested basic_data structure.
    """
    mapped = _map_data(friendly_data)
    return i129_filler.fill_i129(template_path, output_path, mapped)


def _map_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Map incoming data (flat or nested) to FIELD_MAP keys."""
    m = {}

    # Visa classification
    visa = (data.get("visa_type") or "").upper()
    if "H-1B" in visa or "H1B" in visa:
        m["classification_symbol"] = "H-1B"
    elif "O-1" in visa or "O1" in visa:
        m["classification_symbol"] = "O-1"
    elif "L-1" in visa or "L1" in visa:
        m["classification_symbol"] = "L-1"

    m["total_workers"] = "1"

    # Direct flat keys (from filler.py flatten)
    m["petitioner_company"] = data.get("employer_name")
    m["petitioner_street"] = data.get("employer_address")
    m["petitioner_city"] = data.get("employer_city")
    m["petitioner_state"] = data.get("employer_state")
    m["petitioner_zip"] = data.get("employer_zip")
    m["petitioner_ein"] = data.get("employer_ein")
    m["petitioner_phone"] = data.get("employer_phone")

    m["beneficiary_family_name"] = data.get("last_name")
    m["beneficiary_given_name"] = data.get("first_name")
    m["beneficiary_dob"] = data.get("date_of_birth")
    m["beneficiary_country_birth"] = data.get("country_of_birth")
    m["beneficiary_country_citizen"] = data.get("citizenship")
    m["beneficiary_passport_number"] = data.get("passport_number")
    m["beneficiary_passport_country"] = data.get("passport_country")
    m["beneficiary_passport_expiry"] = data.get("passport_expiry")
    m["beneficiary_us_street"] = data.get("us_address")
    m["beneficiary_us_city"] = data.get("us_city")
    m["beneficiary_us_state"] = data.get("us_state")
    m["beneficiary_us_zip"] = data.get("us_zip")

    m["job_title"] = data.get("job_title")
    m["lca_number"] = data.get("lca_number")
    m["wage_amount"] = data.get("salary")
    m["wage_per"] = "Year"
    m["hours_per_week"] = str(data.get("hours_per_week", ""))
    m["employment_start"] = data.get("job_start_date")
    m["employment_end"] = data.get("job_end_date")

    m["work_street"] = data.get("work_address")
    m["work_city"] = data.get("work_city")
    m["work_state"] = data.get("work_state")
    m["work_zip"] = data.get("work_zip")

    # Remove None values
    return {k: v for k, v in m.items() if v}
