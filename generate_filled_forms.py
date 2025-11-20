#!/usr/bin/env python3
"""
Gera versões preenchidas simuladas dos formulários oficiais
"""

import sys
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

sys.path.insert(0, '/app')
from simulated_case_data import simulated_case


def generate_filled_i129():
    """Gera Form I-129 preenchido simulado"""
    
    output_path = "/tmp/i129_filled_simulated.pdf"
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                           topMargin=0.5*inch, bottomMargin=0.5*inch,
                           leftMargin=0.75*inch, rightMargin=0.75*inch)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Header do formulário
    header_style = ParagraphStyle(
        'FormHeader',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    field_style = ParagraphStyle(
        'Field',
        parent=styles['Normal'],
        fontSize=9,
        spaceAfter=6
    )
    
    # Página 1 - Form I-129
    story.append(Paragraph("<b>Department of Homeland Security</b>", header_style))
    story.append(Paragraph("<b>U.S. Citizenship and Immigration Services</b>", header_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("<b>Form I-129, Petition for a Nonimmigrant Worker</b>", header_style))
    story.append(Paragraph("OMB No. 1615-0009", field_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Part 1 - Information about the employer
    story.append(Paragraph("<b>Part 1. Information About the Employer</b>", 
                          ParagraphStyle('SectionTitle', parent=styles['Heading3'], 
                                       fontSize=11, textColor=colors.HexColor('#1a237e'))))
    story.append(Spacer(1, 0.15*inch))
    
    employer_data = [
        ["1. Legal Name of Employer:", simulated_case.employer['legal_name']],
        ["2. Trade Name (if any):", simulated_case.employer['dba_name']],
        ["3. Employer's Mailing Address:", ""],
        ["   Street Number and Name:", simulated_case.employer['address']],
        ["   City:", simulated_case.employer['city']],
        ["   State:", simulated_case.employer['state']],
        ["   ZIP Code:", simulated_case.employer['zip']],
        ["4. Employer's Physical Address (if different):", "Same as above"],
        ["5. Employer's Telephone Number:", simulated_case.employer['phone']],
        ["6. Employer's Email Address:", simulated_case.employer['email']],
        ["7. Employer's FEIN:", simulated_case.employer['fein']],
        ["8. IRS Tax Number (if different from FEIN):", "Same as FEIN"],
        ["9. NAICS Code:", simulated_case.employer['naics_code']],
    ]
    
    for label, value in employer_data:
        story.append(Paragraph(f"<b>{label}</b> {value}", field_style))
    
    story.append(Spacer(1, 0.3*inch))
    
    # Part 2 - Information about the petition
    story.append(Paragraph("<b>Part 2. Information About This Petition</b>", 
                          ParagraphStyle('SectionTitle2', parent=styles['Heading3'], 
                                       fontSize=11, textColor=colors.HexColor('#1a237e'))))
    story.append(Spacer(1, 0.15*inch))
    
    petition_data = [
        ["1. Requested Nonimmigrant Classification:", "H-1B"],
        ["2. Basis for Classification:", "☑ Initial petition for new employment"],
        ["3. Prior Petition/Receipt Number (if any):", "N/A"],
        ["4. Requested Start Date:", simulated_case.position['start_date']],
        ["5. Requested End Date:", simulated_case.position['end_date']],
        ["6. Total Number of Workers in Petition:", "1"],
    ]
    
    for label, value in petition_data:
        story.append(Paragraph(f"<b>{label}</b> {value}", field_style))
    
    story.append(PageBreak())
    
    # Página 2 - Part 3
    story.append(Paragraph("<b>Part 3. Information About the Person You Are Filing For</b>", 
                          ParagraphStyle('SectionTitle3', parent=styles['Heading3'], 
                                       fontSize=11, textColor=colors.HexColor('#1a237e'))))
    story.append(Spacer(1, 0.15*inch))
    
    beneficiary_data = [
        ["1. Family Name (Last Name):", simulated_case.beneficiary['family_name']],
        ["2. Given Name (First Name):", simulated_case.beneficiary['given_name']],
        ["3. Full Middle Name:", "ANTONIO"],
        ["4. Date of Birth (mm/dd/yyyy):", simulated_case.beneficiary['dob_formatted']],
        ["5. Country of Birth:", simulated_case.beneficiary['pob_country']],
        ["6. Province/State of Birth:", simulated_case.beneficiary['pob_state']],
        ["7. City/Town of Birth:", simulated_case.beneficiary['pob_city']],
        ["8. Country of Citizenship/Nationality:", simulated_case.beneficiary['nationality']],
        ["9. Gender:", simulated_case.beneficiary['gender']],
        ["", ""],
        ["10. Social Security Number (if any):", "N/A (International applicant)"],
        ["11. Alien Registration Number (A-Number) (if any):", "N/A"],
        ["", ""],
        ["12. Passport Information:", ""],
        ["    Passport Number:", simulated_case.beneficiary['passport_number']],
        ["    Country of Issuance:", "Brazil"],
        ["    Expiration Date:", simulated_case.beneficiary['passport_expiry_date']],
        ["", ""],
        ["13. Current Immigration Status:", simulated_case.beneficiary['current_status']],
        ["14. Date Status Expires:", simulated_case.beneficiary['status_expiry']],
        ["15. I-94 Arrival/Departure Number:", simulated_case.beneficiary['i94_number']],
        ["16. Date of Last Arrival:", simulated_case.beneficiary['last_entry_date']],
        ["17. Port of Entry:", simulated_case.beneficiary['last_entry_port']],
        ["", ""],
        ["18. Current U.S. Address:", ""],
        ["    Street:", simulated_case.beneficiary['current_address']],
        ["    City:", simulated_case.beneficiary['current_city']],
        ["    State:", simulated_case.beneficiary['current_state']],
        ["    ZIP:", simulated_case.beneficiary['current_zip']],
        ["", ""],
        ["19. Beneficiary's Foreign Address:", ""],
        ["    City:", simulated_case.beneficiary['pob_city']],
        ["    Country:", simulated_case.beneficiary['pob_country']],
    ]
    
    for label, value in beneficiary_data:
        if label and value:
            story.append(Paragraph(f"<b>{label}</b> {value}", field_style))
        elif label:
            story.append(Paragraph(f"<b>{label}</b>", field_style))
        else:
            story.append(Spacer(1, 0.1*inch))
    
    story.append(PageBreak())
    
    # Página 3 - Part 4 - Processing Information
    story.append(Paragraph("<b>Part 4. Processing Information</b>", 
                          ParagraphStyle('SectionTitle4', parent=styles['Heading3'], 
                                       fontSize=11, textColor=colors.HexColor('#1a237e'))))
    story.append(Spacer(1, 0.15*inch))
    
    processing_data = [
        ["1. Is beneficiary in the United States?", "☑ Yes  ☐ No"],
        ["2. If Yes, provide:", ""],
        ["   a. I-94 Number:", simulated_case.beneficiary['i94_number']],
        ["   b. Current Status:", simulated_case.beneficiary['current_status']],
        ["   c. Date Status Expires:", simulated_case.beneficiary['status_expiry']],
        ["", ""],
        ["3. Is beneficiary applying for change of status?", "☑ Yes  ☐ No"],
        ["4. Is beneficiary in removal proceedings?", "☐ Yes  ☑ No"],
        ["5. Has beneficiary ever worked without authorization?", "☐ Yes  ☑ No"],
        ["", ""],
        ["6. If requesting premium processing:", "☑ Yes (Included)"],
        ["7. Attorney or Representative Information:", ""],
        ["   Name:", simulated_case.case_info['attorney_name']],
        ["   Law Firm:", simulated_case.case_info['law_firm']],
        ["   Bar Number:", simulated_case.case_info['attorney_bar']],
    ]
    
    for label, value in processing_data:
        if label and value:
            story.append(Paragraph(f"<b>{label}</b> {value}", field_style))
        elif label:
            story.append(Paragraph(f"<b>{label}</b>", field_style))
        else:
            story.append(Spacer(1, 0.1*inch))
    
    story.append(Spacer(1, 0.4*inch))
    
    # Signatures
    story.append(Paragraph("<b>Part 5. Petitioner's Certification</b>", 
                          ParagraphStyle('SectionTitle5', parent=styles['Heading3'], 
                                       fontSize=11, textColor=colors.HexColor('#1a237e'))))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph(
        "I certify, under penalty of perjury under the laws of the United States, that this petition and the evidence "
        "submitted with it are all true and correct. I authorize the release of any information from my records that "
        "USCIS needs to determine eligibility for the benefit being sought.",
        field_style
    ))
    
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(f"<b>Signature:</b> {simulated_case.employer['hr_contact_name']}", field_style))
    story.append(Paragraph(f"<b>Title:</b> {simulated_case.employer['hr_contact_title']}", field_style))
    story.append(Paragraph(f"<b>Date:</b> {simulated_case.case_info['petition_date']}", field_style))
    
    # Build PDF
    doc.build(story)
    
    print(f"✅ Form I-129 preenchido gerado: {output_path}")
    return output_path


def generate_filled_lca():
    """Gera LCA preenchido simulado"""
    
    output_path = "/tmp/lca_filled_simulated.pdf"
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                           topMargin=0.5*inch, bottomMargin=0.5*inch,
                           leftMargin=0.75*inch, rightMargin=0.75*inch)
    
    styles = getSampleStyleSheet()
    story = []
    
    header_style = ParagraphStyle(
        'LCAHeader',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    field_style = ParagraphStyle(
        'LCAField',
        parent=styles['Normal'],
        fontSize=9,
        spaceAfter=6
    )
    
    # Header
    story.append(Paragraph("<b>Labor Condition Application for Nonimmigrant Workers</b>", header_style))
    story.append(Paragraph("<b>ETA Form 9035 & 9035E</b>", header_style))
    story.append(Paragraph("<b>U.S. Department of Labor</b>", header_style))
    story.append(Paragraph("OMB Approval: 1205-0310", field_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Certification status
    cert_box = Table([
        ["<b>CERTIFICATION STATUS:</b>", "<b>CERTIFIED</b>"],
        ["Certification Date:", simulated_case.lca['certification_date']],
        ["Case Number:", simulated_case.lca['case_number']],
        ["Certification Number:", simulated_case.lca['certification_number']],
    ], colWidths=[2.5*inch, 3.5*inch])
    
    cert_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4caf50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    story.append(cert_box)
    story.append(Spacer(1, 0.3*inch))
    
    # Section A - Employer Information
    story.append(Paragraph("<b>Section A. Employer Information</b>", 
                          ParagraphStyle('LCASection', parent=styles['Heading3'], 
                                       fontSize=11, textColor=colors.HexColor('#1a237e'))))
    story.append(Spacer(1, 0.15*inch))
    
    employer_lca_data = [
        ["1. Legal Business Name:", simulated_case.employer['legal_name']],
        ["2. Trade Name/DBA (if any):", simulated_case.employer['dba_name']],
        ["3. Address:", simulated_case.employer['address']],
        ["4. City:", simulated_case.employer['city']],
        ["5. State:", simulated_case.employer['state']],
        ["6. ZIP Code:", simulated_case.employer['zip']],
        ["7. Country:", "United States"],
        ["8. Telephone Number:", simulated_case.employer['phone']],
        ["9. Email Address:", simulated_case.employer['email']],
        ["10. FEIN:", simulated_case.employer['fein']],
        ["11. NAICS Code:", simulated_case.employer['naics_code']],
    ]
    
    for label, value in employer_lca_data:
        story.append(Paragraph(f"<b>{label}</b> {value}", field_style))
    
    story.append(PageBreak())
    
    # Section B - Temporary Need Information
    story.append(Paragraph("<b>Section B. Temporary Need Information</b>", 
                          ParagraphStyle('LCASection2', parent=styles['Heading3'], 
                                       fontSize=11, textColor=colors.HexColor('#1a237e'))))
    story.append(Spacer(1, 0.15*inch))
    
    temp_need_data = [
        ["1. Job Title:", simulated_case.position['title']],
        ["2. SOC (ONET/OES) Code:", simulated_case.position['soc_code']],
        ["3. SOC (ONET/OES) Occupation Title:", simulated_case.position['soc_title']],
        ["4. Full-time Position:", "☑ Yes  ☐ No"],
        ["5. Begin Date:", simulated_case.position['start_date']],
        ["6. End Date:", simulated_case.position['end_date']],
        ["7. Worker Positions Needed:", "1"],
        ["", ""],
        ["8. Wage Information:", ""],
        ["   a. Rate of Pay:", simulated_case.position['salary_annual'] + " per year"],
        ["   b. Per (check one):", "☑ Year  ☐ Hour  ☐ Week  ☐ Bi-Weekly  ☐ Month"],
        ["   c. Prevailing Wage:", simulated_case.lca['prevailing_wage'] + " per year"],
        ["   d. Prevailing Wage Level:", simulated_case.position['prevailing_wage_level']],
        ["", ""],
        ["9. Worksite Information:", ""],
        ["   a. Address:", simulated_case.position['work_location_address']],
        ["   b. City:", simulated_case.position['work_location_city']],
        ["   c. State:", simulated_case.position['work_location_state']],
        ["   d. ZIP Code:", simulated_case.position['work_location_zip']],
        ["   e. County:", "King County"],
    ]
    
    for label, value in temp_need_data:
        if label and value:
            story.append(Paragraph(f"<b>{label}</b> {value}", field_style))
        elif label:
            story.append(Paragraph(f"<b>{label}</b>", field_style))
        else:
            story.append(Spacer(1, 0.1*inch))
    
    story.append(PageBreak())
    
    # Section D - Prevailing Wage Information
    story.append(Paragraph("<b>Section D. Prevailing Wage Information</b>", 
                          ParagraphStyle('LCASection3', parent=styles['Heading3'], 
                                       fontSize=11, textColor=colors.HexColor('#1a237e'))))
    story.append(Spacer(1, 0.15*inch))
    
    pw_data = [
        ["1. Prevailing Wage Source:", "☑ Online Wage Library (OWL)"],
        ["2. Prevailing Wage Tracking Number:", "PW-2025-098765"],
        ["3. Prevailing Wage:", simulated_case.lca['prevailing_wage'] + " per year"],
        ["4. Prevailing Wage Level:", simulated_case.position['prevailing_wage_level']],
        ["5. Wage Source Year:", "2025"],
    ]
    
    for label, value in pw_data:
        story.append(Paragraph(f"<b>{label}</b> {value}", field_style))
    
    story.append(Spacer(1, 0.4*inch))
    
    # Section E - Employer Labor Condition Statements
    story.append(Paragraph("<b>Section E. Employer Labor Condition Statements</b>", 
                          ParagraphStyle('LCASection4', parent=styles['Heading3'], 
                                       fontSize=11, textColor=colors.HexColor('#1a237e'))))
    story.append(Spacer(1, 0.15*inch))
    
    statements = [
        "☑ 1. The employer will pay the higher of the prevailing wage or the actual wage paid by the employer to workers with similar experience and qualifications.",
        "☑ 2. The employment of H-1B nonimmigrants will not adversely affect the working conditions of similarly employed U.S. workers.",
        "☑ 3. There is no strike, lockout, or work stoppage in the named occupation at the place of employment.",
        "☑ 4. The employer has provided notice of this filing to the collective bargaining representative or has posted notice at the place of employment.",
    ]
    
    for stmt in statements:
        story.append(Paragraph(stmt, field_style))
        story.append(Spacer(1, 0.1*inch))
    
    story.append(Spacer(1, 0.4*inch))
    
    # Section F - Signature
    story.append(Paragraph("<b>Section F. Employer/Attorney Signature and Date</b>", 
                          ParagraphStyle('LCASection5', parent=styles['Heading3'], 
                                       fontSize=11, textColor=colors.HexColor('#1a237e'))))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph(f"<b>Signature:</b> {simulated_case.employer['hr_contact_name']}", field_style))
    story.append(Paragraph(f"<b>Title:</b> {simulated_case.employer['hr_contact_title']}", field_style))
    story.append(Paragraph(f"<b>Date Signed:</b> {simulated_case.lca['filing_date']}", field_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(f"<b>Certification Date:</b> {simulated_case.lca['certification_date']}", field_style))
    story.append(Paragraph(f"<b>Valid From:</b> {simulated_case.lca['validity_start']}", field_style))
    story.append(Paragraph(f"<b>Valid To:</b> {simulated_case.lca['validity_end']}", field_style))
    
    # Build PDF
    doc.build(story)
    
    print(f"✅ LCA preenchido gerado: {output_path}")
    return output_path


if __name__ == "__main__":
    print("\n" + "="*80)
    print("GERANDO FORMULÁRIOS PREENCHIDOS SIMULADOS")
    print("="*80)
    
    i129_path = generate_filled_i129()
    lca_path = generate_filled_lca()
    
    print("\n" + "="*80)
    print("✅ FORMULÁRIOS GERADOS COM SUCESSO!")
    print("="*80)
    print(f"📄 I-129: {i129_path}")
    print(f"📄 LCA: {lca_path}")
    print("="*80)
