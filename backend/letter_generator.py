"""
Letter Generator for Imigrai B2B
Generates professional USCIS cover letters using Google Gemini 2.0 Flash.
"""

import os
from datetime import datetime

import google.generativeai as genai

GEMINI_API_KEY = (
    os.environ.get("GEMINI_API_KEY")
    or os.environ.get("EMERGENT_LLM_KEY")
    or os.environ.get("GOOGLE_API_KEY")
)

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """You are a senior U.S. immigration attorney with 15 years of experience filing petitions with USCIS.
Generate a professional, complete cover letter for submission to USCIS.
The letter must be formal, legally precise, and properly structured.
Respond ONLY with the letter text, no additional explanations."""


class LetterGenerator:
    @staticmethod
    async def generate_cover_letter(
        case: dict, letter_type: str, special_instructions: str = ""
    ) -> str:
        if not GEMINI_API_KEY:
            raise RuntimeError("Gemini API key not configured")

        visa_type = case.get("visa_type", "Unknown")
        client_name = case.get("client_name", "Unknown")
        office_name = case.get("office_name", "Immigration Law Office")
        notes = case.get("notes", "N/A")
        status = case.get("status", "intake")
        date_str = datetime.now().strftime("%B %d, %Y")

        user_prompt = f"""Generate a complete cover letter for USCIS submission with the following data:

PETITION TYPE: {visa_type}
LETTER TYPE: {letter_type}
CLIENT/PETITIONER NAME: {client_name}
LAW OFFICE: {office_name}
DATE: {date_str}
CASE NOTES: {notes}
CURRENT STATUS: {status}
{"SPECIAL INSTRUCTIONS: " + special_instructions if special_instructions else ""}

Required letter structure:
1. Header with date and recipient (USCIS + appropriate service center for the visa type)
2. RE: line with petition type and beneficiary name
3. Formal salutation
4. Opening paragraph: identification of the firm and nature of the petition
5. Body: legal arguments specific to {visa_type}
6. List of documents included in the package
7. Conclusion requesting approval
8. Signature block (space for attorney signature)

For {visa_type}, include the correct legal arguments:
- H-1B: specialty occupation, LCA compliance, employer-employee relationship
- EB-1A: extraordinary ability evidence, 3+ criteria met, final merits determination
- EB-2 NIW: Dhanasar 3-prong framework
- I-130: bona fide relationship, petitioner eligibility
- F-1: academic program, financial support, ties to home country
- B-2: temporary intent, ties to home country, purpose of visit
- I-765: eligibility category, basis for EAD
- O-1: extraordinary achievement, itinerary, advisory opinion"""

        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=SYSTEM_PROMPT,
        )
        response = model.generate_content(user_prompt)
        return response.text
