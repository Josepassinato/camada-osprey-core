"""
Letter Generator for Imigrai B2B
Generates professional USCIS cover letters using Google Gemini 2.0 Flash.
Each letter is unique — built from the actual case data, never generic.
"""

import os
import json
from datetime import datetime

import google.generativeai as genai

GEMINI_API_KEY = (
    os.environ.get("GEMINI_API_KEY")
    or os.environ.get("EMERGENT_LLM_KEY")
    or os.environ.get("GOOGLE_API_KEY")
)

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """You are a senior U.S. immigration attorney with 15+ years of experience filing petitions with USCIS.

ABSOLUTE RULES:
1. NEVER use placeholders like [área de atuação], [field], [specific detail], [company name], [X years], etc.
   If a piece of information is not available in the case data, DO NOT invent it and DO NOT put a placeholder.
   Instead, STOP and include a note at the end: "⚠️ MISSING DATA — the following information is needed: ..."
2. Every letter must be UNIQUE to this specific client. Use their real name, real qualifications, real documents, real achievements.
3. Minimum 3 FULL pages of content. This is a professional legal submission, not a summary.
4. Use formal legal language appropriate for USCIS adjudicators.
5. Cite relevant AAO precedent decisions where applicable.
6. Respond ONLY with the letter text (and any missing data warnings at the end)."""

# Visa-specific legal frameworks
VISA_FRAMEWORKS = {
    "EB-1A": """
EB-1A EXTRAORDINARY ABILITY — Legal Framework:

Apply the TWO-STEP Kazarian analysis (Kazarian v. USCIS, 596 F.3d 1115):
  Step 1: Determine if at least 3 of the 10 regulatory criteria are met with evidence
  Step 2: Final merits determination — does the totality of evidence demonstrate sustained national/international acclaim?

The 10 criteria (8 CFR 235.204(h)(3)):
  1. Awards — nationally/internationally recognized prizes for excellence
  2. Membership — in associations requiring outstanding achievements (judged by experts)
  3. Published material — about the beneficiary in professional/major trade publications
  4. Judging — participation as a judge of others' work in the field
  5. Original contributions — of major significance to the field
  6. Scholarly articles — in professional journals or major media
  7. Exhibitions/Showcases — display of work at artistic exhibitions or showcases
  8. Leading/critical role — in distinguished organizations
  9. High salary — commanding a high salary or remuneration relative to others in the field
  10. Commercial success — in the performing arts

MAP EACH CRITERION to the specific evidence from this case. Only claim criteria that are supported by actual documents/evidence in the case.
Cite: Kazarian v. USCIS, Matter of [the beneficiary], AAO precedent decisions.
""",
    "EB-2 NIW": """
EB-2 NIW (NATIONAL INTEREST WAIVER) — Legal Framework:

Apply the THREE-PRONG Dhanasar framework (Matter of Dhanasar, 26 I&N Dec. 884 (AAO 2016)):

  Prong 1: The proposed endeavor has both SUBSTANTIAL MERIT and NATIONAL IMPORTANCE.
    - Describe the specific endeavor (not just a job description)
    - Explain why it matters nationally (economic impact, public health, technology advancement, etc.)
    - Use concrete data: numbers, statistics, scope of impact

  Prong 2: The beneficiary is WELL POSITIONED to advance the proposed endeavor.
    - Education and qualifications (degrees, certifications)
    - Track record of success (publications, projects, results)
    - Specific plan to advance the endeavor
    - Resources, support, or partnerships in place

  Prong 3: On balance, it would be BENEFICIAL to the United States to waive the job offer and labor certification requirements.
    - Explain why requiring labor certification would be impractical or contrary to national interest
    - Show urgency or unique positioning
    - Compare to NYSDOT precedent (Matter of New York State DOT, 22 I&N Dec. 215 (AAO 1998))

Also cite: Dhanasar, NYSDOT, and any relevant AAO precedent decisions.
Requirement: Advanced degree OR Bachelor's + 5 years progressive experience in the specialty.
""",
    "O-1A": """
O-1A EXTRAORDINARY ABILITY — Legal Framework:

The beneficiary must demonstrate EXTRAORDINARY ABILITY by sustained national or international acclaim,
and must be coming to the US to continue work in the area of extraordinary ability.

Apply the 8 criteria (must meet at least 3):
  1. Awards — nationally/internationally recognized prizes or awards for excellence
  2. Membership — in associations requiring outstanding achievements (judged by recognized experts)
  3. Published material — in professional or major trade publications or media about the beneficiary
  4. Judging — original scientific, scholarly, or business-related contributions of major significance
  5. Original contributions — of major significance in the field
  6. Scholarly articles — authorship of scholarly articles in the field
  7. Employment in critical/essential capacity — for organizations with distinguished reputation
  8. High salary — commanding a high salary or remuneration evidenced by contracts or other reliable evidence

MAP EACH CRITERION to actual evidence from this case.
Cite: Kazarian v. USCIS, 596 F.3d 1115 (9th Cir. 2010).
Note: O-1A also requires an advisory opinion from a peer group or labor organization.
""",
    "H-1B": """
H-1B SPECIALTY OCCUPATION — Legal Framework:
  - The position must qualify as a "specialty occupation" (8 CFR 214.2(h)(4)(ii))
  - Bachelor's degree or higher in a specific specialty is normally required
  - LCA (Labor Condition Application) compliance
  - Valid employer-employee relationship
  - Beneficiary's qualifications match the specialty occupation requirements
""",
    "I-130": """
I-130 FAMILY-BASED PETITION — Legal Framework:
  - Bona fide relationship between petitioner and beneficiary
  - Petitioner's eligibility (US citizen or LPR status)
  - Proper family relationship category (IR, F1, F2A, F2B, F3, F4)
  - Evidence of relationship (marriage certificate, birth certificate, etc.)
""",
    "F-1": """
F-1 STUDENT VISA — Legal Framework:
  - Acceptance by SEVP-certified school
  - Sufficient financial support for entire program
  - Ties to home country demonstrating non-immigrant intent
  - Academic preparedness
""",
    "I-765": """
I-765 EAD (Employment Authorization Document) — Legal Framework:
  - Eligibility category code
  - Basis for employment authorization
  - Supporting evidence per category
""",
}


def _build_case_summary(case: dict) -> str:
    """Extract and format ALL available case data for the prompt."""
    sections = []

    # Basic identification
    sections.append("=== CLIENT & CASE IDENTIFICATION ===")
    sections.append(f"Client/Beneficiary Name: {case.get('client_name', 'NOT PROVIDED')}")
    sections.append(f"Case ID: {case.get('case_id', 'N/A')}")
    sections.append(f"Visa/Petition Type: {case.get('visa_type', 'NOT PROVIDED')}")
    sections.append(f"Current Case Status: {case.get('status', 'N/A')}")
    sections.append(f"Law Office: {case.get('office_name', 'NOT PROVIDED')}")

    # Basic data (if present — structured client info)
    basic = case.get("basic_data") or case.get("client_data") or case.get("beneficiary_data") or {}
    if basic:
        sections.append("\n=== CLIENT BIOGRAPHICAL DATA ===")
        if isinstance(basic, dict):
            for k, v in basic.items():
                if v:
                    sections.append(f"  {k}: {v}")
        elif isinstance(basic, str):
            sections.append(basic)

    # Qualifications
    quals = case.get("qualifications") or case.get("education") or case.get("credentials") or {}
    if quals:
        sections.append("\n=== QUALIFICATIONS & EDUCATION ===")
        if isinstance(quals, list):
            for q in quals:
                sections.append(f"  - {q}" if isinstance(q, str) else f"  - {json.dumps(q, ensure_ascii=False)}")
        elif isinstance(quals, dict):
            for k, v in quals.items():
                if v:
                    sections.append(f"  {k}: {v}")
        elif isinstance(quals, str):
            sections.append(quals)

    # Experience / Employment
    exp = case.get("experience") or case.get("employment") or case.get("work_history") or {}
    if exp:
        sections.append("\n=== PROFESSIONAL EXPERIENCE ===")
        if isinstance(exp, list):
            for e in exp:
                sections.append(f"  - {e}" if isinstance(e, str) else f"  - {json.dumps(e, ensure_ascii=False)}")
        elif isinstance(exp, dict):
            for k, v in exp.items():
                if v:
                    sections.append(f"  {k}: {v}")
        elif isinstance(exp, str):
            sections.append(exp)

    # Documents received
    docs = case.get("documents", [])
    if docs:
        sections.append(f"\n=== DOCUMENTS RECEIVED ({len(docs)}) ===")
        for d in docs:
            doc_type = d.get("document_type", "unknown")
            filename = d.get("filename", "")
            notes = d.get("notes", "")
            label = f"  - {doc_type}"
            if filename:
                label += f" ({filename})"
            if notes:
                label += f" — {notes}"
            sections.append(label)

    # Case notes (often contain critical details from the attorney)
    notes = case.get("notes", "")
    if notes and notes.strip():
        sections.append("\n=== ATTORNEY NOTES & CASE DETAILS ===")
        sections.append(notes)

    # Achievements / Publications / Awards (common for EB-1A, O-1A, NIW)
    for field_name in ["achievements", "awards", "publications", "citations",
                       "memberships", "contributions", "patents", "media_coverage",
                       "judging_experience", "exhibitions", "recommendation_letters"]:
        val = case.get(field_name)
        if val:
            sections.append(f"\n=== {field_name.upper().replace('_', ' ')} ===")
            if isinstance(val, list):
                for item in val:
                    sections.append(f"  - {item}" if isinstance(item, str) else f"  - {json.dumps(item, ensure_ascii=False)}")
            elif isinstance(val, dict):
                for k, v in val.items():
                    sections.append(f"  {k}: {v}")
            else:
                sections.append(str(val))

    # Proposed endeavor (critical for NIW)
    endeavor = case.get("proposed_endeavor") or case.get("endeavor") or case.get("research_plan")
    if endeavor:
        sections.append("\n=== PROPOSED ENDEAVOR ===")
        sections.append(str(endeavor) if not isinstance(endeavor, (dict, list)) else json.dumps(endeavor, ensure_ascii=False, indent=2))

    # Employer / Sponsor info
    employer = case.get("employer") or case.get("petitioner") or case.get("sponsor")
    if employer:
        sections.append("\n=== EMPLOYER / PETITIONER / SPONSOR ===")
        if isinstance(employer, dict):
            for k, v in employer.items():
                if v:
                    sections.append(f"  {k}: {v}")
        else:
            sections.append(str(employer))

    # Deadlines
    deadlines = case.get("deadlines", [])
    if deadlines:
        sections.append(f"\n=== DEADLINES ({len(deadlines)}) ===")
        for dl in deadlines:
            sections.append(f"  - {dl.get('title', 'N/A')}: {dl.get('due_date', 'N/A')}")

    # Any other fields we haven't captured
    known_fields = {
        "case_id", "office_id", "client_name", "visa_type", "status", "notes",
        "documents", "deadlines", "history", "created_at", "updated_at",
        "office_name", "basic_data", "client_data", "beneficiary_data",
        "qualifications", "education", "credentials", "experience", "employment",
        "work_history", "achievements", "awards", "publications", "citations",
        "memberships", "contributions", "patents", "media_coverage",
        "judging_experience", "exhibitions", "recommendation_letters",
        "proposed_endeavor", "endeavor", "research_plan", "employer",
        "petitioner", "sponsor", "qa_review", "qa_approved", "qa_score",
        "qa_review_date", "package_generated", "package_id", "package_path",
        "package_generated_at", "package_files_count", "form_code",
    }
    extra = {k: v for k, v in case.items() if k not in known_fields and v and k != "_id"}
    if extra:
        sections.append("\n=== ADDITIONAL CASE DATA ===")
        for k, v in extra.items():
            if isinstance(v, (dict, list)):
                sections.append(f"  {k}: {json.dumps(v, ensure_ascii=False)}")
            else:
                sections.append(f"  {k}: {v}")

    return "\n".join(sections)


class LetterGenerator:
    @staticmethod
    async def generate_cover_letter(
        case: dict, letter_type: str, special_instructions: str = ""
    ) -> str:
        if not GEMINI_API_KEY:
            raise RuntimeError("Gemini API key not configured")

        visa_type = case.get("visa_type", "Unknown")
        client_name = case.get("client_name", "Unknown")
        date_str = datetime.now().strftime("%B %d, %Y")

        # Build complete case summary from ALL available data
        case_summary = _build_case_summary(case)

        # Get visa-specific legal framework
        framework = ""
        visa_upper = visa_type.upper().replace(" ", "")
        for key, value in VISA_FRAMEWORKS.items():
            if key.replace("-", "").replace(" ", "") in visa_upper or visa_upper in key.replace("-", "").replace(" ", ""):
                framework = value
                break
        if "NIW" in visa_upper:
            framework = VISA_FRAMEWORKS["EB-2 NIW"]
        elif "EB1" in visa_upper or "EB-1A" in visa_upper:
            framework = VISA_FRAMEWORKS["EB-1A"]
        elif "O-1" in visa_upper or "O1" in visa_upper:
            framework = VISA_FRAMEWORKS["O-1A"]

        user_prompt = f"""Generate a COMPLETE, UNIQUE cover letter for USCIS submission.
This letter is for {client_name} — use ONLY the real data provided below. No placeholders.

DATE: {date_str}
LETTER TYPE: {letter_type}

{framework}

===================================================================
COMPLETE CASE DATA (use this to build every argument in the letter):
===================================================================

{case_summary}

===================================================================
LETTER REQUIREMENTS:
===================================================================

1. HEADER: Date, recipient (USCIS + correct service center for {visa_type})
2. RE: line with petition type ({visa_type}) and beneficiary name ({client_name})
3. Formal salutation ("Dear Sir or Madam" or "Dear USCIS Officer")
4. OPENING (1 paragraph): Identify the law firm, state the nature of the petition, introduce the beneficiary with their REAL qualifications
5. BODY (multiple paragraphs, minimum 2+ pages of argumentation):
   - For EB-1A: Map at least 3 of the 10 criteria to ACTUAL evidence from this case. Apply Kazarian two-step analysis.
   - For EB-2 NIW: Address ALL 3 Dhanasar prongs with CONCRETE data from this case. Cite Dhanasar and NYSDOT.
   - For O-1A: Map at least 3 of the 8 criteria to ACTUAL evidence from this case. Cite Kazarian.
   - For other types: Build arguments using the specific legal requirements with real case data.
   - Cite relevant AAO precedent decisions (Dhanasar, Kazarian, NYSDOT, etc.) where applicable.
   - Reference SPECIFIC documents from the case that support each argument.
6. DOCUMENT LIST: List all documents included in the filing package (based on documents received above)
7. CONCLUSION: Request favorable adjudication, offer to provide additional evidence if needed
8. SIGNATURE BLOCK: Attorney signature line with firm name

CRITICAL REMINDERS:
- Minimum 3 FULL pages. This is a real USCIS submission.
- NEVER use brackets [] or placeholders. If data is missing, note it at the end under "⚠️ MISSING DATA".
- Every claim must be backed by actual case data or documents listed above.
- Use formal legal prose. This letter will be read by a USCIS adjudicator.
{"- SPECIAL INSTRUCTIONS FROM ATTORNEY: " + special_instructions if special_instructions else ""}"""

        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=SYSTEM_PROMPT,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=8192,
                temperature=0.3,
            ),
        )
        response = model.generate_content(user_prompt)
        return response.text
