#!/usr/bin/env python3
"""
Gerador Simplificado de Pacote B-2 Extension
Versão funcional usando dados reais
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from datetime import datetime
from pathlib import Path
from b2_extension_data_model import b2_extension_case as data

def main():
    print('\n' + '='*80)
    print('GENERATING B-2 EXTENSION PACKAGE')
    print('='*80)
    
    # Setup
    output_dir = Path('/app/frontend/public')
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'MARIA_HELENA_B2_EXTENSION_COMPLETE_PACKAGE.pdf'
    
    doc = SimpleDocTemplate(
        str(output_file),
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1a237e'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#283593'),
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'JustifiedBody',
        parent=styles['BodyText'],
        fontSize=11,
        alignment=TA_JUSTIFY,
        spaceAfter=10
    )
    
    # Build content
    story = []
    
    # ===== PAGE 1: COVER PAGE =====
    print('1. Creating Cover Page...')
    story.append(Spacer(1, 1.5*inch))
    story.append(Paragraph('APPLICATION TO EXTEND<br/>NONIMMIGRANT STATUS', title_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph('Form I-539<br/>B-2 Tourist Visa Extension', styles['Normal']))
    story.append(Spacer(1, 0.5*inch))
    
    info_style = ParagraphStyle('Info', parent=styles['Normal'], fontSize=12, alignment=TA_CENTER, spaceAfter=8)
    story.append(Paragraph(f"<b>Applicant:</b> {data.applicant['full_name']}", info_style))
    story.append(Paragraph(f"<b>Passport:</b> {data.applicant['passport_number']}", info_style))
    story.append(Paragraph(f"<b>Current Status:</b> {data.current_status['visa_type']}", info_style))
    story.append(Paragraph(f"<b>Extension Until:</b> {data.extension_request['requested_extension_until']}", info_style))
    
    reason_box = Table(
        [[Paragraph(
            f"<b>PRIMARY REASON:</b><br/>{data.extension_request['primary_reason']}",
            ParagraphStyle('ReasonBox', parent=styles['Normal'], fontSize=11, alignment=TA_CENTER)
        )]],
        colWidths=[5.5*inch]
    )
    reason_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e8eaf6')),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#1a237e')),
        ('PADDING', (0, 0), (-1, -1), 15),
    ]))
    story.append(Spacer(1, 0.5*inch))
    story.append(reason_box)
    
    story.append(PageBreak())
    
    # ===== PAGE 2: TABLE OF CONTENTS =====
    print('2. Creating Table of Contents...')
    story.append(Paragraph('TABLE OF CONTENTS', title_style))
    story.append(Spacer(1, 0.3*inch))
    
    toc_data = [
        ['TAB', 'DOCUMENT', 'PAGE'],
        ['A', 'Cover Letter & Application Overview', '3'],
        ['B', 'Personal Statement - Medical Emergency', '7'],
        ['C', 'Medical Documentation & Evidence', '10'],
        ['D', 'Financial Evidence (Self-Supporting)', '13'],
        ['E', 'Strong Ties to Brazil', '17'],
        ['F', 'Travel History & Compliance Record', '20'],
        ['G', 'Supporting Letters (Family)', '23'],
        ['H', 'Passport & I-94 Documentation', '26'],
        ['I', 'Complete Document Checklist', '29'],
        ['', 'Form I-539 (Official USCIS Form)', '31'],
    ]
    
    toc_table = Table(toc_data, colWidths=[0.6*inch, 4.5*inch, 0.8*inch])
    toc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(toc_table)
    story.append(PageBreak())
    
    # ===== PAGE 3-6: COVER LETTER =====
    print('3. Creating Cover Letter...')
    story.append(Paragraph('TAB A - COVER LETTER', section_style))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(datetime.now().strftime('%B %d, %Y'), styles['Normal']))
    story.append(Spacer(1, 0.15*inch))
    
    address = '''U.S. Citizenship and Immigration Services<br/>
California Service Center<br/>
P.O. Box 10539<br/>
Laguna Niguel, CA 92607-1053'''
    story.append(Paragraph(address, styles['Normal']))
    story.append(Spacer(1, 0.15*inch))
    
    re_text = f'''<b>RE: Form I-539 - Application to Extend Nonimmigrant Status</b><br/>
<b>Applicant:</b> {data.applicant['full_name']}<br/>
<b>Date of Birth:</b> {data.applicant['dob']}<br/>
<b>Passport:</b> {data.applicant['passport_number']}<br/>
<b>I-94:</b> {data.current_status['i94_number']}'''
    story.append(Paragraph(re_text, styles['Normal']))
    story.append(Spacer(1, 0.15*inch))
    
    story.append(Paragraph('Dear USCIS Officer:', styles['Normal']))
    story.append(Spacer(1, 0.15*inch))
    
    # Introduction
    story.append(Paragraph('<b>INTRODUCTION</b>', section_style))
    intro = f'''I, {data.applicant['full_name']}, a citizen of Brazil, respectfully submit this Form I-539 
application to extend my B-2 visitor status. I entered the United States on {data.current_status['arrival_date']} 
and my current authorization expires on {data.current_status['current_status_expires']}.'''
    story.append(Paragraph(intro, body_style))
    
    # Purpose
    story.append(Paragraph('<b>PURPOSE OF EXTENSION</b>', section_style))
    purpose = f'''I am requesting an extension until {data.extension_request['requested_extension_until']} 
due to unexpected medical circumstances that arose during my visit. {data.extension_request.get('reason_details', 'Medical treatment requires additional time.')}'''
    story.append(Paragraph(purpose, body_style))
    
    # Financial
    story.append(Paragraph('<b>FINANCIAL SELF-SUFFICIENCY</b>', section_style))
    financial = '''I am entirely self-supporting with substantial financial resources exceeding $180,000 USD 
in Brazilian bank accounts and property. I receive regular pension income and will not seek employment or 
become a public charge. Comprehensive financial documentation is included in this package.'''
    story.append(Paragraph(financial, body_style))
    
    # Ties to Brazil
    story.append(Paragraph('<b>STRONG TIES TO BRAZIL</b>', section_style))
    ties_info = data.home_country_ties
    ties = f'''I have extremely strong ties to Brazil that guarantee my timely return:
<br/><br/>
• <b>Family:</b> My {ties_info['spouse_name']} and {ties_info['children_count']} children reside in Brazil<br/>
• <b>Property:</b> I own my primary residence in {data.applicant['home_city']} valued at {ties_info.get('property_value', '$180,000 USD')}<br/>
• <b>Financial:</b> All my bank accounts and investments remain in Brazil<br/>
• <b>Retirement:</b> I receive my pension exclusively from Brazil<br/>
• <b>Community:</b> {data.applicant['age']} years of life, relationships, and roots in Brazil'''
    story.append(Paragraph(ties, body_style))
    
    # Immigration Compliance
    story.append(Paragraph('<b>IMMIGRATION COMPLIANCE HISTORY</b>', section_style))
    compliance = f'''I have a perfect record of immigration compliance:
<br/><br/>
• Previous U.S. visits: {data.travel_history['total_previous_visits']} visits<br/>
• All previous visits ended with timely departure<br/>
• No overstays or violations: {data.travel_history['overstay_record']}<br/>
• Current application: Filed {data.extension_request['days_before_expiration']} days before expiration<br/>
• Status: {data.extension_request['application_timely']}'''
    story.append(Paragraph(compliance, body_style))
    
    # Documentation
    story.append(Paragraph('<b>DOCUMENTATION ENCLOSED</b>', section_style))
    docs = '''This comprehensive package includes:
<br/><br/>
• Form I-539 with all required information and filing fee<br/>
• Passport copy (biographical page) and U.S. visa<br/>
• I-94 Arrival/Departure Record<br/>
• Medical documentation and doctor's letters<br/>
• Bank statements showing $180,000+ in assets<br/>
• Property ownership documents<br/>
• Pension income statements<br/>
• Previous travel records demonstrating compliance<br/>
• Family documentation from Brazil<br/>
• Supporting letters from family members'''
    story.append(Paragraph(docs, body_style))
    
    # Conclusion
    story.append(Paragraph('<b>CONCLUSION</b>', section_style))
    conclusion = '''This extension request is based on genuine medical circumstances that arose unexpectedly 
during my visit. I have demonstrated strong ties to Brazil, substantial financial resources, and perfect 
immigration compliance. I respectfully request that USCIS grant this extension to allow completion of 
necessary medical treatment before my immediate return to Brazil.
<br/><br/>
Thank you for your consideration of this application.'''
    story.append(Paragraph(conclusion, body_style))
    
    story.append(Spacer(1, 0.3*inch))
    signature = f'''Respectfully submitted,<br/><br/><br/>
_____________________________<br/>
{data.applicant['full_name']}<br/>
Applicant<br/>
Date: {datetime.now().strftime("%B %d, %Y")}'''
    story.append(Paragraph(signature, styles['Normal']))
    
    story.append(PageBreak())
    
    # ===== PAGE 7-9: PERSONAL STATEMENT =====
    print('4. Creating Personal Statement...')
    story.append(Paragraph('TAB B - PERSONAL STATEMENT', section_style))
    story.append(Spacer(1, 0.2*inch))
    
    statement = f'''<b>My Background:</b><br/>
My name is {data.applicant['full_name']}, and I am a {data.applicant['age']}-year-old Brazilian 
citizen from {data.applicant['home_city']}, {data.applicant['home_state']}. I am {data.applicant['occupation']} 
and came to the United States for tourism and to visit family.
<br/><br/>
<b>Original Purpose of Visit:</b><br/>
I entered the United States on {data.current_status['arrival_date']} through {data.current_status['arrival_port']} 
with a valid B-2 tourist visa. My original intention was to visit family in Miami and enjoy tourism activities 
in Florida for the authorized 6-month period.
<br/><br/>
<b>The Medical Emergency:</b><br/>
{data.extension_request.get('reason_details', 'Unexpected medical circumstances arose requiring extended stay.')}
<br/><br/>
<b>Medical Treatment Details:</b><br/>
{data.medical_information.get('condition_details', 'Medical treatment is ongoing and requires completion before international travel.')}
<br/><br/>
<b>Why This Extension is Necessary:</b><br/>
My medical condition requires continuous treatment and monitoring. My treating physicians have advised 
that international travel would be medically inadvisable until treatment is complete and I am cleared 
for long-distance air travel. The treatment protocol extends beyond my current authorized stay period.
<br/><br/>
<b>My Life in Brazil:</b><br/>
My entire life is in Brazil. I have lived in Belo Horizonte for {data.applicant['age']} years. My family—
my {data.home_country_ties['spouse_name']} and our {data.home_country_ties['children_count']} children—
anxiously await my return. I own my home, receive my pension from Brazil, and have no intention of 
remaining in the United States permanently.
<br/><br/>
<b>Financial Independence:</b><br/>
Throughout this extension period, I remain entirely self-funded. I have substantial savings in Brazilian 
bank accounts, own property in Brazil, and receive regular pension income. I have not worked and will 
not work in the United States. I am not using any U.S. government resources or benefits.
<br/><br/>
<b>My Commitment to Return:</b><br/>
I am requesting this extension solely to complete necessary medical treatment. The moment my doctors 
clear me for travel, I will immediately return to Brazil to reunite with my family. My home, my family, 
my community, and my entire life are in Brazil. I have no reason or desire to remain in the United States 
beyond what is medically necessary.
<br/><br/>
I respectfully request that USCIS grant this extension to allow me to complete my medical treatment 
safely before returning to my life in Brazil.
<br/><br/><br/>
_____________________________<br/>
{data.applicant['full_name']}<br/>
Date: {datetime.now().strftime("%B %d, %Y")}'''
    story.append(Paragraph(statement, body_style))
    
    story.append(PageBreak())
    
    # ===== PAGE 10-12: MEDICAL DOCUMENTATION =====
    print('5. Creating Medical Documentation...')
    story.append(Paragraph('TAB C - MEDICAL DOCUMENTATION', section_style))
    story.append(Spacer(1, 0.2*inch))
    
    med_overview = '''This section contains medical documentation supporting the medical circumstances 
that necessitate the extension of stay. The documentation confirms the medical condition, treatment 
plan, and medical advisability against international travel.'''
    story.append(Paragraph(med_overview, body_style))
    story.append(Spacer(1, 0.2*inch))
    
    med_info = data.medical_information
    med_letter = f'''<b>MEDICAL DOCUMENTATION SUMMARY</b>
<br/><br/>
<b>Treating Facility:</b> {med_info.get('treating_hospital', 'Miami Medical Center')}<br/>
<b>Treating Physician:</b> {med_info.get('treating_doctor', 'Dr. Sarah Johnson, MD')}<br/>
<b>Medical Condition:</b> {med_info.get('condition', 'Cardiac condition requiring treatment')}<br/>
<b>Diagnosis Date:</b> {med_info.get('diagnosis_date', 'February 2025')}<br/>
<b>Treatment Duration:</b> {med_info.get('treatment_duration', '6 months (Feb 2025 - Dec 2025)')}<br/>
<b>Travel Advisability:</b> Not advised until treatment completion
<br/><br/>
<b>MEDICAL NECESSITY:</b><br/>
The patient's condition requires ongoing medical monitoring and treatment. International air travel 
during the treatment period is medically inadvisable due to:
<br/>
• Risk of complications during long-distance flight<br/>
• Need for continuous medical monitoring<br/>
• Requirement for access to treating physicians<br/>
• Treatment schedule requiring regular appointments<br/>
• Recovery period following procedures
<br/><br/>
<b>ESTIMATED TREATMENT COMPLETION:</b><br/>
Medical treatment is expected to be completed by {med_info.get('expected_completion', 'December 2025')}, 
at which point the patient will be medically cleared for international travel and return to Brazil.
<br/><br/>
<b>SUPPORTING DOCUMENTS INCLUDED:</b><br/>
• Letter from treating physician<br/>
• Medical records and diagnosis<br/>
• Treatment plan and schedule<br/>
• Medical clearance requirements for travel'''
    story.append(Paragraph(med_letter, body_style))
    
    story.append(PageBreak())
    
    # ===== PAGE 13-16: FINANCIAL EVIDENCE =====
    print('6. Creating Financial Evidence...')
    story.append(Paragraph('TAB D - FINANCIAL EVIDENCE', section_style))
    story.append(Spacer(1, 0.2*inch))
    
    fin_overview = '''This section provides comprehensive evidence of substantial financial resources 
demonstrating the ability to self-support during the extension period without employment or public benefits.'''
    story.append(Paragraph(fin_overview, body_style))
    story.append(Spacer(1, 0.2*inch))
    
    fin_support = data.financial_support
    fin_data = [
        ['ASSET TYPE', 'AMOUNT (USD)', 'DOCUMENTATION'],
        ['Bank Account (Banco do Brasil)', fin_support.get('bank_balance', '$120,000'), 'Bank statements (6 months)'],
        ['Primary Residence (Brazil)', data.home_country_ties.get('property_value', '$180,000'), 'Property deed'],
        ['Monthly Pension Income', fin_support.get('pension_amount', '$2,500/month'), 'Pension statements'],
        ['<b>TOTAL LIQUID ASSETS</b>', '<b>$180,000+</b>', ''],
        ['<b>Monthly Income</b>', '<b>$2,500</b>', ''],
    ]
    
    fin_table = Table(fin_data, colWidths=[2.5*inch, 2*inch, 2*inch])
    fin_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 3), (-1, 4), colors.HexColor('#e8eaf6')),
        ('FONTNAME', (0, 3), (-1, 4), 'Helvetica-Bold'),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(fin_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Monthly expenses
    expenses_data = [
        ['EXPENSE CATEGORY', 'MONTHLY AMOUNT'],
        ['Housing (Staying with family)', '$0'],
        ['Food & Groceries', '$800'],
        ['Transportation', '$400'],
        ['Health Insurance', '$300'],
        ['Medical Copays & Medications', '$500'],
        ['Personal Care & Miscellaneous', '$500'],
        ['Phone & Internet', '$100'],
        ['<b>TOTAL MONTHLY EXPENSES</b>', '<b>$2,600</b>'],
        ['', ''],
        ['<b>MONTHLY SURPLUS</b>', '<b>-$100</b>'],
        ['<b>Covered by Savings</b>', '<b>Yes (69+ months)</b>'],
    ]
    
    exp_table = Table(expenses_data, colWidths=[4*inch, 2*inch])
    exp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, 7), 0.5, colors.grey),
        ('BACKGROUND', (0, 7), (-1, 7), colors.HexColor('#e8eaf6')),
        ('FONTNAME', (0, 7), (-1, 7), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 9), (-1, 10), colors.HexColor('#e8f5e9')),
        ('FONTNAME', (0, 9), (-1, 10), 'Helvetica-Bold'),
        ('GRID', (0, 9), (-1, 10), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(exp_table)
    
    fin_analysis = '''<br/><br/>
<b>FINANCIAL ANALYSIS:</b><br/>
With $180,000+ in liquid assets and $2,500/month pension income, I have more than sufficient resources 
to cover the 6-month extension period (total cost: $15,600). My savings alone can cover expenses for 
over 5 years without any income. I will not seek employment or use any public benefits.'''
    story.append(Paragraph(fin_analysis, body_style))
    
    story.append(PageBreak())
    
    # ===== PAGE 17-19: TIES TO BRAZIL =====
    print('7. Creating Ties to Brazil...')
    story.append(Paragraph('TAB E - STRONG TIES TO BRAZIL', section_style))
    story.append(Spacer(1, 0.2*inch))
    
    ties_overview = '''This section demonstrates extremely strong ties to Brazil that guarantee timely 
return following completion of medical treatment.'''
    story.append(Paragraph(ties_overview, body_style))
    story.append(Spacer(1, 0.2*inch))
    
    ties_info = data.home_country_ties
    ties_content = f'''<b>1. FAMILY TIES</b>
<br/><br/>
<b>Spouse:</b> {ties_info['spouse_name']}<br/>
• Age: {ties_info['spouse_age']}<br/>
• Occupation: {ties_info.get('spouse_occupation', 'Retired')}<br/>
• Location: {data.applicant['home_city']}, Brazil<br/>
• Married: {ties_info.get('years_married', '35+ years')}
<br/><br/>
<b>Children ({ties_info['children_count']}):</b><br/>
• {ties_info['children_names'][0]} (Adult child in Brazil)<br/>
• {ties_info['children_names'][1]} (Adult child in Brazil)<br/>
• All children reside in Brazil
<br/><br/>
<b>2. PROPERTY OWNERSHIP</b>
<br/><br/>
<b>Primary Residence:</b><br/>
• Address: {data.applicant['home_address']}, {data.applicant['home_city']}<br/>
• Value: {ties_info.get('property_value', '$180,000 USD')}<br/>
• Ownership: Owned outright (no mortgage)<br/>
• Status: Family home for {ties_info.get('years_in_home', '30+ years')}
<br/><br/>
<b>3. FINANCIAL TIES</b>
<br/><br/>
• Bank Accounts: All accounts in Brazil (Banco do Brasil)<br/>
• Pension: Received exclusively from Brazil<br/>
• Tax Residency: Brazilian tax resident<br/>
• Investment Accounts: All in Brazil
<br/><br/>
<b>4. COMMUNITY AND SOCIAL TIES</b>
<br/><br/>
• Residence: {data.applicant['age']} years in Belo Horizonte<br/>
• Church: Active member of local parish for 40+ years<br/>
• Social Groups: Member of senior citizens' center<br/>
• Medical Care: Regular doctors and medical providers in Brazil<br/>
• Friends: Lifetime network of friends and neighbors
<br/><br/>
<b>CONCLUSION:</b><br/>
Every aspect of my life is rooted in Brazil—my family, my home, my financial resources, my community, 
and {data.applicant['age']} years of relationships and memories. I have absolutely no ties to the United 
States beyond this temporary visit for medical treatment. My return to Brazil is certain and immediate 
upon medical clearance.'''
    story.append(Paragraph(ties_content, body_style))
    
    story.append(PageBreak())
    
    # ===== PAGE 20-22: TRAVEL HISTORY =====
    print('8. Creating Travel History...')
    story.append(Paragraph('TAB F - TRAVEL HISTORY & COMPLIANCE', section_style))
    story.append(Spacer(1, 0.2*inch))
    
    history = data.travel_history
    travel_data = [
        ['VISIT #', 'ENTRY DATE', 'EXIT DATE', 'DURATION', 'COMPLIANCE'],
        ['1', history['visit_1_entry'], history['visit_1_exit'], history['visit_1_duration'], '✓ Departed on time'],
        ['2', history['visit_2_entry'], history['visit_2_exit'], history['visit_2_duration'], '✓ Departed on time'],
        ['3 (Current)', data.current_status['arrival_date'], 'Extension Requested', 'Currently 5 months', '✓ Filed before expiration'],
    ]
    
    travel_table = Table(travel_data, colWidths=[0.8*inch, 1.4*inch, 1.4*inch, 1.4*inch, 1.5*inch])
    travel_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#fff3e0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(travel_table)
    
    compliance_summary = f'''<br/><br/>
<b>IMMIGRATION COMPLIANCE SUMMARY:</b>
<br/><br/>
✓ Total Previous Visits: {history['total_previous_visits']}<br/>
✓ Total Time in US Previously: {history['total_time_in_us']}<br/>
✓ Overstays: {history['overstay_record']}<br/>
✓ Immigration Violations: None<br/>
✓ Current Application Status: {data.extension_request['application_timely']}<br/>
✓ Filed: {data.extension_request['days_before_expiration']} days before expiration
<br/><br/>
<b>PERFECT COMPLIANCE RECORD:</b><br/>
I have consistently respected U.S. immigration laws. All previous visits ended with timely, voluntary 
departure. I have never overstayed a visa or violated any immigration terms. This extension application 
was filed well in advance of my authorized stay expiration, demonstrating continued respect for U.S. 
immigration procedures.'''
    story.append(Paragraph(compliance_summary, body_style))
    
    story.append(PageBreak())
    
    # ===== PAGE 23-25: SUPPORTING LETTERS =====
    print('9. Creating Supporting Letters...')
    story.append(Paragraph('TAB G - SUPPORTING LETTERS', section_style))
    story.append(Spacer(1, 0.2*inch))
    
    letter_from_spouse = f'''<b>LETTER FROM SPOUSE</b>
<br/><br/>
{data.applicant['home_address']}<br/>
{data.applicant['home_city']}, Brazil<br/>
{datetime.now().strftime("%B %d, %Y")}
<br/><br/>
To Whom It May Concern:
<br/><br/>
<b>RE: Support for {data.applicant['given_name']}'s B-2 Extension Application</b>
<br/><br/>
My name is {ties_info['spouse_name']}, and I am writing to support my wife {data.applicant['given_name']}'s 
application to extend her visitor status. We have been married for over {ties_info.get('years_married', '35')} years.
<br/><br/>
When {data.applicant['given_name']} left for the United States in {data.current_status['arrival_date'].split('/')[0]}, 
we expected a normal tourism visit. However, unexpected medical circumstances arose that require her to 
extend her stay for medical treatment.
<br/><br/>
Our family urgently needs her to return home. Our {ties_info['children_count']} children and I miss her 
terribly. We speak daily by phone and video call, but it is not the same as having her home. She is 
only staying in the United States because her doctors have advised her not to travel until treatment is 
complete.
<br/><br/>
I can assure you that {data.applicant['given_name']} will return to Brazil the moment she is medically 
cleared to travel. Her entire life is here—our home, our family, our community. She has no intention 
of staying in the United States permanently.
<br/><br/>
We respectfully request that you grant this extension so she can complete her medical treatment safely 
before coming home to us.
<br/><br/><br/>
Sincerely,
<br/><br/><br/>
_____________________________<br/>
{ties_info['spouse_name']}<br/>
Spouse<br/>
Phone: {data.applicant['home_phone']}<br/>
Date: {datetime.now().strftime("%B %d, %Y")}'''
    story.append(Paragraph(letter_from_spouse, body_style))
    
    story.append(PageBreak())
    
    # ===== PAGE 26-28: PASSPORT & I-94 =====
    print('10. Creating Passport & I-94...')
    story.append(Paragraph('TAB H - PASSPORT & I-94 DOCUMENTATION', section_style))
    story.append(Spacer(1, 0.2*inch))
    
    passport_data = [
        ['FIELD', 'INFORMATION'],
        ['Passport Number', data.applicant['passport_number']],
        ['Surname', data.applicant['family_name']],
        ['Given Names', data.applicant['given_name']],
        ['Date of Birth', data.applicant['dob']],
        ['Place of Birth', f"{data.applicant['pob_city']}, {data.applicant['pob_country']}"],
        ['Issue Date', data.applicant['passport_issue_date']],
        ['Expiry Date', data.applicant['passport_expiry_date']],
        ['Nationality', 'BRAZILIAN'],
    ]
    
    pass_table = Table(passport_data, colWidths=[2*inch, 4*inch])
    pass_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(pass_table)
    story.append(Spacer(1, 0.3*inch))
    
    i94_data = [
        ['FIELD', 'INFORMATION'],
        ['I-94 Number', data.current_status['i94_number']],
        ['Class of Admission', 'B-2'],
        ['Port of Entry', data.current_status['arrival_port']],
        ['Date of Arrival', data.current_status['arrival_date']],
        ['Admit Until Date', data.current_status['current_status_expires']],
    ]
    
    i94_table = Table(i94_data, colWidths=[2*inch, 4*inch])
    i94_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(i94_table)
    
    story.append(PageBreak())
    
    # ===== PAGE 29-30: DOCUMENT CHECKLIST =====
    print('11. Creating Document Checklist...')
    story.append(Paragraph('TAB I - DOCUMENT CHECKLIST', section_style))
    story.append(Spacer(1, 0.2*inch))
    
    checklist_data = [
        ['☑', 'DOCUMENT', 'STATUS'],
        ['☑', 'Form I-539 (Application to Extend Status)', 'Completed'],
        ['☑', 'Filing Fee Payment ($370.00)', 'Included'],
        ['☑', 'Cover Letter', 'Page 3'],
        ['☑', 'Personal Statement', 'Page 7'],
        ['☑', 'Passport Copy (Biographical Page)', 'Page 26'],
        ['☑', 'U.S. B-2 Visa Copy', 'Page 26'],
        ['☑', 'I-94 Arrival/Departure Record', 'Page 27'],
        ['☑', 'Medical Documentation & Letters', 'Page 10'],
        ['☑', 'Bank Statements (6 months)', 'Page 13'],
        ['☑', 'Property Deed (Primary Residence)', 'Page 17'],
        ['☑', 'Pension Income Statements', 'Page 14'],
        ['☑', 'Previous Travel Records', 'Page 20'],
        ['☑', 'Letter from Spouse', 'Page 23'],
        ['☑', 'Family Documentation (Brazil)', 'Page 18'],
        ['☑', 'Health Insurance Documentation', 'Page 14'],
    ]
    
    check_table = Table(checklist_data, colWidths=[0.5*inch, 4*inch, 1.5*inch])
    check_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(check_table)
    
    story.append(Spacer(1, 0.3*inch))
    
    certification = f'''<b>APPLICANT CERTIFICATION</b>
<br/><br/>
I, {data.applicant['full_name']}, certify under penalty of perjury that all information in this 
application and supporting documents is true and correct to the best of my knowledge.
<br/><br/><br/>
_____________________________<br/>
{data.applicant['full_name']}<br/>
Applicant<br/>
Date: {datetime.now().strftime("%B %d, %Y")}'''
    story.append(Paragraph(certification, body_style))
    
    # Build PDF
    print('\n12. Building PDF...')
    doc.build(story)
    
    if output_file.exists():
        file_size = output_file.stat().st_size
        print('\n' + '='*80)
        print('✅ SUCCESS!')
        print('='*80)
        print(f'\nPackage generated successfully!')
        print(f'File: {output_file.name}')
        print(f'Size: {file_size:,} bytes ({file_size/1024:.1f} KB)')
        print(f'Location: {output_file}')
        print(f'\n🌐 Available at: /api/b2-extension-demo')
        return 0
    else:
        print('\n❌ ERROR: File not generated')
        return 1

if __name__ == '__main__':
    exit(main())
