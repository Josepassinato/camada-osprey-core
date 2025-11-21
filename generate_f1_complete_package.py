#!/usr/bin/env python3
"""
Gerador COMPLETO de Pacote F-1 Student Visa
Inclui: Documentação acadêmica, financeira, I-20, evidências de vínculos
Versão: Professional Package
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from datetime import datetime
from pathlib import Path
from f1_student_data_model import f1_student_case as data
from f1_image_generator import F1ImageGenerator

def generate_f1_student_package():
    """
    Gera pacote F-1 completo profissional
    """
    print('\n' + '='*80)
    print('🚀 GENERATING COMPLETE F-1 STUDENT VISA PACKAGE')
    print('='*80)
    
    # Setup
    output_dir = Path('/app/frontend/public')
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'F1_STUDENT_COMPLETE_PACKAGE_RAFAEL_OLIVEIRA.pdf'
    
    # Generate images first
    print('\n📸 STEP 1: Generating simulated images...')
    image_gen = F1ImageGenerator()
    
    passport_photo = image_gen.create_passport_photo(data.applicant)
    print(f'   ✅ Passport photo: {passport_photo.name}')
    
    passport_biopage = image_gen.create_passport_biopage(data.applicant)
    print(f'   ✅ Passport biopage: {passport_biopage.name}')
    
    i20_form_image = image_gen.create_i20_form(data.applicant, data.i20, data.us_program)
    print(f'   ✅ I-20 form: {i20_form_image.name}')
    
    transcript_image = image_gen.create_transcript(data.applicant, data.education)
    print(f'   ✅ Transcript: {transcript_image.name}')
    
    # Generate bank statements (3 months)
    bank_statements = []
    for month in ['January 2025', 'February 2025', 'March 2025']:
        bank_data = {
            'account_number': '12345-6',
            'account_type': 'Savings Account',
            'opening_balance': '225,000.00',
            'credits': '8,500.00',
            'debits': '4,000.00',
            'closing_balance': '229,500.00'
        }
        stmt = image_gen.create_bank_statement(data.applicant, bank_data, month)
        bank_statements.append(stmt)
        print(f'   ✅ Bank statement: {stmt.name}')
    
    print(f'\n📄 STEP 2: Creating PDF document...')
    
    # Create PDF
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
        fontSize=22,
        textColor=colors.HexColor('#0d47a1'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1565c0'),
        spaceAfter=12,
        spaceBefore=16,
        fontName='Helvetica-Bold'
    )
    
    subsection_style = ParagraphStyle(
        'SubSection',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=colors.HexColor('#1976d2'),
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'JustifiedBody',
        parent=styles['BodyText'],
        fontSize=11,
        alignment=TA_JUSTIFY,
        spaceAfter=10,
        leading=14
    )
    
    # Build content
    story = []
    page_count = 1
    
    print(f'\n📝 Building document content...')
    
    # ===== COVER PAGE =====
    print(f'   Page {page_count}: Cover Page')
    story.append(Spacer(1, 1.5*inch))
    story.append(Paragraph('F-1 STUDENT VISA<br/>APPLICATION PACKAGE', title_style))
    story.append(Spacer(1, 0.4*inch))
    
    cover_info = [
        ['<b>Applicant:</b>', data.applicant['full_name']],
        ['<b>Passport:</b>', data.applicant['passport_number']],
        ['<b>Nationality:</b>', data.applicant['nationality']],
        ['<b>Program:</b>', data.us_program['program_name']],
        ['<b>Institution:</b>', data.us_program['school_name']],
        ['<b>Program Start:</b>', data.us_program['start_date']],
        ['<b>SEVIS ID:</b>', data.i20['sevis_id']],
    ]
    
    cover_table = Table(cover_info, colWidths=[2*inch, 4*inch])
    cover_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1565c0')),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(cover_table)
    
    story.append(Spacer(1, 0.6*inch))
    
    status_box = Table(
        [[Paragraph(
            f'<b>Application Status:</b> Ready for Consular Processing<br/>'
            f'<b>Interview Location:</b> {data.current_status["interview_location"]}<br/>'
            f'<b>Package Date:</b> {datetime.now().strftime("%B %d, %Y")}',
            ParagraphStyle('StatusBox', parent=styles['Normal'], fontSize=11, alignment=TA_CENTER)
        )]],
        colWidths=[5.5*inch]
    )
    status_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e3f2fd')),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#1565c0')),
        ('PADDING', (0, 0), (-1, -1), 15),
    ]))
    story.append(status_box)
    story.append(PageBreak())
    page_count += 1
    
    # ===== TABLE OF CONTENTS =====
    print(f'   Page {page_count}: Table of Contents')
    story.append(Paragraph('TABLE OF CONTENTS', title_style))
    story.append(Spacer(1, 0.3*inch))
    
    toc_data = [
        ['SECTION', 'DOCUMENT', 'PAGE'],
        ['I', 'Cover Letter & Application Overview', '3'],
        ['II', 'Form I-20 (Certificate of Eligibility)', '7'],
        ['III', 'Academic Documents', '9'],
        ['IV', 'Financial Support Evidence', '13'],
        ['V', 'English Proficiency (TOEFL)', '18'],
        ['VI', 'Standardized Tests (GRE)', '19'],
        ['VII', 'Ties to Home Country (Brazil)', '20'],
        ['VIII', 'Statement of Purpose', '23'],
        ['IX', 'Recommendation Letters', '26'],
        ['X', 'Work Experience & Professional Background', '29'],
        ['XI', 'Supporting Documents', '31'],
        ['XII', 'Document Checklist', '33'],
    ]
    
    toc_table = Table(toc_data, colWidths=[0.8*inch, 4.2*inch, 1*inch])
    toc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1565c0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),
    ]))
    story.append(toc_table)
    story.append(PageBreak())
    page_count += 1
    
    # ===== SECTION I: COVER LETTER =====
    print(f'   Pages {page_count}-{page_count+3}: Cover Letter')
    story.append(Paragraph('SECTION I - COVER LETTER', section_style))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(datetime.now().strftime('%B %d, %Y'), styles['Normal']))
    story.append(Spacer(1, 0.15*inch))
    
    address = f'''Consular Section<br/>
U.S. Consulate General<br/>
{data.current_status['interview_location']}<br/>
Brazil'''
    story.append(Paragraph(address, styles['Normal']))
    story.append(Spacer(1, 0.15*inch))
    
    re_text = f'''<b>RE: F-1 Student Visa Application</b><br/>
<b>Applicant:</b> {data.applicant['full_name']}<br/>
<b>Passport:</b> {data.applicant['passport_number']}<br/>
<b>SEVIS ID:</b> {data.i20['sevis_id']}<br/>
<b>Program:</b> {data.us_program['program_name']}<br/>
<b>Institution:</b> {data.us_program['school_name']}'''
    story.append(Paragraph(re_text, styles['Normal']))
    story.append(Spacer(1, 0.15*inch))
    
    story.append(Paragraph('Dear Consular Officer:', styles['Normal']))
    story.append(Spacer(1, 0.15*inch))
    
    # Introduction
    story.append(Paragraph('<b>I. INTRODUCTION</b>', subsection_style))
    intro = f'''I, {data.applicant['full_name']}, a {data.applicant['age']}-year-old citizen of {data.applicant['nationality']}, 
respectfully submit this F-1 student visa application to pursue a {data.us_program['program_name']} at 
{data.us_program['school_name']}, commencing {data.us_program['start_date']}. I have been unconditionally admitted to this 
program and have received my Form I-20 (SEVIS ID: {data.i20['sevis_id']}) from the university.'''
    story.append(Paragraph(intro, body_style))
    
    # Academic Background
    story.append(Paragraph('<b>II. ACADEMIC BACKGROUND</b>', subsection_style))
    academic = f'''I hold a {data.education['highest_degree']} in {data.education['field_of_study']} from 
{data.education['institution']}, where I graduated in {data.education['graduation_date']} with a GPA of {data.education['gpa']}. 
During my undergraduate studies, I distinguished myself through academic excellence, earning placement on the Dean's List for 
4 semesters. I also published a research paper on Machine Learning and served as a Teaching Assistant for the Data Structures 
course, demonstrating both my academic capability and commitment to the field.
<br/><br/>
My undergraduate curriculum included advanced coursework in {', '.join(data.education['transcript_summary']['relevant_courses'][:3])}, 
providing me with a strong foundation for graduate studies. My academic achievements reflect my dedication to computer science 
and my readiness for the rigorous graduate program at Boston University.'''
    story.append(Paragraph(academic, body_style))
    
    # Program Selection
    story.append(Paragraph('<b>III. PROGRAM SELECTION AND ACADEMIC GOALS</b>', subsection_style))
    program = f'''I have chosen {data.us_program['school_name']}'s {data.us_program['program_name']} program with a specialization in 
{data.us_program['specialization']} for several compelling reasons:
<br/><br/>
<b>1. Academic Excellence:</b> Boston University's Computer Science program is ranked among the top 50 in the United States and is 
particularly renowned for its research in artificial intelligence and machine learning. The program's faculty includes leading researchers 
whose work aligns perfectly with my academic interests.
<br/><br/>
<b>2. Specialized Curriculum:</b> The program offers specialized coursework in machine learning and AI that is not available at this 
advanced level in Brazil. This specialized knowledge is essential for my career goals and will enable me to contribute to Brazil's 
growing technology sector at a higher level.
<br/><br/>
<b>3. Research Opportunities:</b> The university's state-of-the-art research facilities and industry partnerships will provide me 
with hands-on experience in cutting-edge AI technologies, which is crucial for my professional development.
<br/><br/>
The 2-year program ({data.us_program['duration']}) requires completion of 32 credits and includes either a thesis or capstone project, 
allowing me to develop both theoretical knowledge and practical skills in my field.'''
    story.append(Paragraph(program, body_style))
    story.append(PageBreak())
    page_count += 1
    
    # Financial Support (CRÍTICO)
    print(f'   Page {page_count}: Financial Support')
    story.append(Paragraph('<b>IV. FINANCIAL SUPPORT AND SELF-SUFFICIENCY</b>', subsection_style))
    financial = f'''I have comprehensive financial resources to cover all expenses during my studies in the United States:
<br/><br/>
<b>Total Program Cost:</b> {data.i20['total_program_cost']}<br/>
<b>Annual Cost Breakdown:</b>
<br/>
• Tuition and Fees: {data.i20['tuition_fees']}<br/>
• Living Expenses: {data.i20['living_expenses']}<br/>
• Books and Supplies: {data.i20['books_supplies']}<br/>
• Health Insurance: {data.i20['health_insurance']}<br/>
• Personal Expenses: {data.i20['personal_expenses']}<br/>
• <b>Total Annual: {data.i20['total_annual_cost']}</b>
<br/><br/>
<b>Sources of Funding:</b>
<br/><br/>
<b>1. Personal Savings ({data.financial_support['sources']['personal_savings']['percentage']}):</b> 
{data.financial_support['sources']['personal_savings']['amount']}<br/>
I have accumulated substantial personal savings during my 4 years of professional work as a software engineer. My bank statements 
from {data.financial_support['student_bank']['bank_name']} show a current balance of {data.financial_support['student_bank']['current_balance']}, 
demonstrating my financial responsibility and planning.
<br/><br/>
<b>2. Parental Support ({data.financial_support['sources']['parental_support']['percentage']}):</b> 
{data.financial_support['sources']['parental_support']['amount']}<br/>
My parents, {data.sponsors['father']['name']} (Civil Engineer) and {data.sponsors['mother']['name']} (Financial Controller), 
have committed to supporting my education. Their combined annual income is {data.sponsors['combined_annual_income']}. They maintain 
substantial savings in {data.financial_support['parents_bank']['bank_name']} with a current balance of 
{data.financial_support['parents_bank']['current_balance']}. Additionally, they own property valued at over $480,000 USD, 
demonstrating their financial stability.
<br/><br/>
<b>3. University Scholarship ({data.financial_support['sources']['scholarship']['percentage']}):</b> 
{data.financial_support['sources']['scholarship']['amount']}<br/>
{data.financial_support['sources']['scholarship']['details']}
<br/><br/>
<b>Total Available Funding: {data.financial_support['total_available']}</b>
<br/><br/>
<b>Financial Documentation Included:</b>
<br/>
• Bank statements (6 months) from both my account and my parents' accounts<br/>
• Parents' employment verification letters and income statements<br/>
• Property ownership documents<br/>
• University scholarship award letter<br/>
• Affidavit of Support from my parents<br/>
• Parents' tax returns (demonstrating financial capability)
<br/><br/>
This comprehensive financial documentation demonstrates that I have sufficient, legitimate funds to cover all expenses during my 
studies without the need to work illegally or become a burden on the US system.'''
    story.append(Paragraph(financial, body_style))
    story.append(PageBreak())
    page_count += 1
    
    # Strong Ties to Brazil
    print(f'   Page {page_count}: Ties to Brazil')
    story.append(Paragraph('<b>V. STRONG TIES TO BRAZIL AND INTENT TO RETURN</b>', subsection_style))
    ties = f'''I have deep and unbreakable ties to Brazil that ensure my return after completing my studies:
<br/><br/>
<b>1. Family Ties (Primary and Strongest):</b><br/>
My entire immediate family resides in Brazil:
<br/>
• <b>Parents:</b> {data.sponsors['father']['name']} (age {data.sponsors['father']['age']}) and {data.sponsors['mother']['name']} 
(age {data.sponsors['mother']['age']}) both live and work in São Paulo<br/>
• <b>Sister:</b> {data.home_country_ties['family']['siblings']}<br/>
• <b>Extended Family:</b> Grandparents, aunts, uncles, and cousins all reside in Brazil<br/>
<br/>
I have extremely close relationships with my family. As an only son (with one sister), my parents depend on me for support as they 
age. This creates a strong obligation and desire to return to Brazil after my studies.
<br/><br/>
<b>2. Property and Financial Ties:</b><br/>
My family owns substantial property in Brazil:
<br/>
• Primary Residence in São Paulo: {data.sponsors['property_owned']['primary_residence']['address']}, 
valued at {data.sponsors['property_owned']['primary_residence']['value']}<br/>
• Additional Property: {data.sponsors['property_owned']['additional_property']['address']}, 
valued at {data.sponsors['property_owned']['additional_property']['value']}<br/>
<br/>
As the only son, I stand to inherit a significant portion of these assets, creating a strong financial incentive to maintain my 
ties to Brazil.
<br/><br/>
<b>3. Career Opportunities in Brazil:</b><br/>
Brazil's technology sector is experiencing rapid growth, with particularly strong demand for professionals with advanced knowledge 
in AI and machine learning. My career plan is specifically focused on returning to Brazil to:
<br/>
• Apply my advanced knowledge to Brazil's growing tech industry<br/>
• Work for leading Brazilian tech companies such as {', '.join(data.home_country_ties['career_plans']['potential_employers'][:2])}<br/>
• Expected salary: {data.home_country_ties['career_plans']['salary_expectation']} - substantially higher than current wages<br/>
• Long-term goal: {data.home_country_ties['career_plans']['long_term']}<br/>
<br/>
The knowledge I gain from this US education is specifically intended to enhance my ability to contribute to Brazil's technological 
development, not to immigrate permanently to the United States.
<br/><br/>
<b>4. Current Professional Position:</b><br/>
I currently work as a {data.work_experience['current_job']['title']} at {data.work_experience['current_job']['company']} in São Paulo, 
where I have been employed since {data.work_experience['current_job']['start_date']}. I have established professional relationships 
and a career trajectory in Brazil. Several colleagues from my company have pursued graduate studies abroad and returned to Brazil, 
achieving significant career advancement.
<br/><br/>
<b>5. Cultural and Social Ties:</b><br/>
Brazil is my home. Portuguese is my native language. All my friends, my community, my cultural identity, and my life are in Brazil. 
At age {data.applicant['age']}, I have no desire to abandon everything I know and love to start over in a foreign country. The United 
States is purely an educational destination for me, not a place to immigrate.
<br/><br/>
<b>6. Previous International Travel:</b><br/>
I have traveled internationally before ({data.home_country_ties['previous_travel']['international']}) and have always returned to Brazil 
as scheduled. I have no history of overstays or immigration violations anywhere.
<br/><br/>
<b>Intent to Return:</b><br/>
Upon completing my master's degree, I intend to return immediately to Brazil. My F-1 visa application is for temporary educational purposes 
only. I have no immigrant intent whatsoever. The advanced education I seek is a means to enhance my career in Brazil, not a pathway to 
remain in the United States.'''
    story.append(Paragraph(ties, body_style))
    story.append(PageBreak())
    page_count += 2
    
    # English Proficiency
    print(f'   Page {page_count}: English Proficiency')
    story.append(Paragraph('<b>VI. ENGLISH LANGUAGE PROFICIENCY</b>', subsection_style))
    english = f'''I have demonstrated strong English language proficiency through standardized testing:
<br/><br/>
<b>{data.english_proficiency['test']} Score:</b> {data.english_proficiency['overall_score']}<br/>
<b>Test Date:</b> {data.english_proficiency['test_date']}<br/>
<b>Test Report Number:</b> {data.english_proficiency['test_report_number']}
<br/><br/>
<b>Section Scores:</b><br/>
• Reading: {data.english_proficiency['section_scores']['Reading']}<br/>
• Listening: {data.english_proficiency['section_scores']['Listening']}<br/>
• Speaking: {data.english_proficiency['section_scores']['Speaking']}<br/>
• Writing: {data.english_proficiency['section_scores']['Writing']}<br/>
<br/>
<b>University Requirement:</b> {data.english_proficiency['requirement']}<br/>
<b>Status:</b> {data.english_proficiency['status']}
<br/><br/>
My TOEFL score significantly exceeds Boston University's minimum requirement, demonstrating my ability to succeed in an English-language 
graduate program. Official TOEFL score report is included in this package.'''
    story.append(Paragraph(english, body_style))
    
    # Standardized Tests
    story.append(Paragraph('<b>VII. STANDARDIZED TEST SCORES (GRE)</b>', subsection_style))
    gre = f'''I have taken the {data.standardized_tests['gre']['test_name']} to demonstrate my academic preparedness:
<br/><br/>
<b>Test Date:</b> {data.standardized_tests['gre']['test_date']}<br/>
<b>Verbal Reasoning:</b> {data.standardized_tests['gre']['verbal']}<br/>
<b>Quantitative Reasoning:</b> {data.standardized_tests['gre']['quantitative']}<br/>
<b>Analytical Writing:</b> {data.standardized_tests['gre']['analytical_writing']}<br/>
<b>Combined Score:</b> {data.standardized_tests['gre']['total']}<br/>
<b>Percentile:</b> {data.standardized_tests['gre']['percentile']}
<br/><br/>
While {data.standardized_tests['gre']['requirement']}, my strong GRE performance demonstrates my academic capability and readiness 
for graduate-level coursework. Official GRE score report is included.'''
    story.append(Paragraph(gre, body_style))
    story.append(PageBreak())
    page_count += 1
    
    # Documentation Enclosed
    print(f'   Page {page_count}: Documentation')
    story.append(Paragraph('<b>VIII. COMPREHENSIVE DOCUMENTATION ENCLOSED</b>', subsection_style))
    docs = '''This application package contains complete documentation to support my F-1 visa application:
<br/><br/>
<b>A. Core Immigration Documents:</b><br/>
• Form I-20 (Certificate of Eligibility for Nonimmigrant Student Status) - Original<br/>
• SEVIS Fee Payment Receipt (Form I-797) - To be obtained<br/>
• DS-160 Confirmation Page - To be completed<br/>
• Passport (valid until 2032)<br/>
• Passport-style photographs (2)
<br/><br/>
<b>B. Academic Documents:</b><br/>
• Bachelor's degree diploma from USP<br/>
• Official transcripts (with English translation)<br/>
• Boston University acceptance letter (unconditional admission)<br/>
• TOEFL official score report<br/>
• GRE official score report<br/>
• Academic achievement certificates<br/>
• Published research paper
<br/><br/>
<b>C. Financial Documents (Comprehensive):</b><br/>
• Personal bank statements (6 months) - Banco do Brasil<br/>
• Parents' bank statements (6 months) - Itaú Unibanco<br/>
• Parents' employment verification letters<br/>
• Parents' income tax returns<br/>
• Affidavit of Support from parents<br/>
• Boston University scholarship award letter ($19,000)<br/>
• Property ownership documents (family properties worth $480,000+)
<br/><br/>
<b>D. Ties to Brazil:</b><br/>
• Current employment verification letter<br/>
• Family photographs and documentation<br/>
• Property deed for family home<br/>
• Previous international travel records (passport stamps)<br/>
• Community involvement documentation
<br/><br/>
<b>E. Supporting Letters:</b><br/>
• Recommendation letter from Prof. Dr. Maria Silva (Academic Advisor, USP)<br/>
• Recommendation letter from Dr. João Santos (Manager, Tech Solutions Brazil)<br/>
• Recommendation letter from Prof. Dr. Carlos Mendes (Department Head, USP)<br/>
• Letter from current employer regarding leave of absence<br/>
• Letter from parents confirming financial support
<br/><br/>
<b>F. Additional Documents:</b><br/>
• Statement of Purpose<br/>
• Detailed study plan<br/>
• Post-graduation career plan (focused on returning to Brazil)<br/>
• Resume/CV<br/>
<br/>
All documents are organized by section, clearly labeled, and include English translations where applicable.'''
    story.append(Paragraph(docs, body_style))
    story.append(PageBreak())
    page_count += 1
    
    # Conclusion
    print(f'   Page {page_count}: Conclusion')
    story.append(Paragraph('<b>IX. CONCLUSION AND RESPECTFUL REQUEST</b>', subsection_style))
    conclusion = f'''This F-1 visa application represents my sincere desire to pursue advanced education in computer science at a leading 
US institution. My application is supported by:
<br/><br/>
<b>1. Strong Academic Qualifications:</b> Bachelor's degree with 3.7 GPA from a prestigious Brazilian university, excellent TOEFL (105) 
and GRE (326) scores, published research, and unconditional admission to a top-ranked graduate program.
<br/><br/>
<b>2. Complete Financial Support:</b> Total funding of $114,000 from personal savings, parental support, and university scholarship - 
fully documented with 6 months of bank statements, employment verification, and property ownership records.
<br/><br/>
<b>3. Deep Ties to Brazil:</b> Entire immediate and extended family in Brazil, family property worth $480,000+, established career in 
Brazilian tech industry, strong cultural and social connections, and clear career goals focused on returning to contribute to Brazil's 
technology sector.
<br/><br/>
<b>4. Temporary Intent:</b> No immigrant intent. Clear educational purpose with defined timeline (2 years). Compelling reasons to return 
to Brazil including family obligations, career opportunities in Brazil's growing tech sector, and personal/cultural ties.
<br/><br/>
<b>5. Compliance History:</b> No previous immigration violations anywhere. Always returned from international travel as scheduled.
<br/><br/>
I understand and respect the requirements and restrictions of F-1 student status. I commit to:
<br/>
• Maintaining full-time enrollment (minimum 12 credits per semester)<br/>
• Maintaining satisfactory academic progress<br/>
• Not engaging in unauthorized employment<br/>
• Departing the United States upon completion of my program<br/>
• Complying with all US immigration laws and regulations
<br/><br/>
<b>Request:</b><br/>
I respectfully request that the US Consulate grant me an F-1 student visa to pursue my Master of Science in Computer Science at 
Boston University. This educational opportunity will enable me to gain advanced knowledge that I will use to contribute to Brazil's 
technological development and economic growth.
<br/><br/>
Thank you for your time and consideration of my application. I am prepared to answer any questions during my visa interview and to 
provide any additional documentation that may be required.
<br/><br/>
Respectfully submitted,<br/><br/><br/>
_____________________________<br/>
{data.applicant['full_name']}<br/>
Applicant<br/>
Date: {datetime.now().strftime("%B %d, %Y")}'''
    story.append(Paragraph(conclusion, body_style))
    story.append(PageBreak())
    page_count += 1
    
    # ===== SECTION II: FORM I-20 OFFICIAL IMAGE =====
    print(f'   Page {page_count}: I-20 Certificate')
    story.append(Paragraph('SECTION II - FORM I-20 (CERTIFICATE OF ELIGIBILITY)', section_style))
    story.append(Spacer(1, 0.2*inch))
    
    i20_notice = '''<b>OFFICIAL FORM I-20:</b> Below is the official Form I-20 issued by Boston University. This is the most critical 
document for F-1 visa application and must be presented at the consular interview and at port of entry.'''
    story.append(Paragraph(i20_notice, body_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Add I-20 image (full page)
    i20_img = RLImage(str(i20_form_image), width=6.5*inch, height=8.4*inch)
    story.append(i20_img)
    story.append(PageBreak())
    page_count += 2
    
    # Add detailed I-20 information table
    story.append(Paragraph('I-20 KEY INFORMATION SUMMARY', subsection_style))
    story.append(Spacer(1, 0.2*inch))
    
    i20_data = [
        ['<b>I-20 Information</b>', ''],
        ['SEVIS ID:', data.i20['sevis_id']],
        ['Form I-20 Number:', data.i20['i20_number']],
        ['Issue Date:', data.i20['issue_date']],
        ['', ''],
        ['<b>School Information</b>', ''],
        ['School Name:', data.us_program['school_name']],
        ['School Address:', data.us_program['school_address']],
        ['SEVIS School Code:', data.us_program['sevis_school_code']],
        ['DSO Name:', data.i20['dso_name']],
        ['DSO Title:', data.i20['dso_title']],
        ['DSO Phone:', data.i20['dso_phone']],
        ['', ''],
        ['<b>Program Information</b>', ''],
        ['Program:', data.us_program['program_name']],
        ['Level of Education:', data.us_program['program_level']],
        ['Program Start Date:', data.us_program['start_date']],
        ['Program End Date:', data.us_program['expected_completion']],
        ['', ''],
        ['<b>Financial Information</b>', ''],
        ['Tuition & Fees (annual):', data.i20['tuition_fees']],
        ['Living Expenses (annual):', data.i20['living_expenses']],
        ['Books & Supplies (annual):', data.i20['books_supplies']],
        ['Total Annual Cost:', data.i20['total_annual_cost']],
        ['Total Program Cost (2 years):', data.i20['total_program_cost']],
        ['', ''],
        ['<b>Entry Authorization</b>', ''],
        ['Valid for Entry:', data.i20['valid_for_entry']],
    ]
    
    i20_table = Table(i20_data, colWidths=[2.5*inch, 4*inch])
    i20_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e3f2fd')),
        ('BACKGROUND', (0, 5), (-1, 5), colors.HexColor('#e3f2fd')),
        ('BACKGROUND', (0, 13), (-1, 13), colors.HexColor('#e3f2fd')),
        ('BACKGROUND', (0, 18), (-1, 18), colors.HexColor('#e3f2fd')),
        ('BACKGROUND', (0, 25), (-1, 25), colors.HexColor('#e3f2fd')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(i20_table)
    
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph('<b>IMPORTANT:</b> Original Form I-20 signed by DSO must be presented at consular interview and port of entry.', body_style))
    story.append(PageBreak())
    page_count += 1
    
    # ===== SECTION III: ACADEMIC DOCUMENTS WITH IMAGES =====
    print(f'   Pages {page_count}-{page_count+2}: Academic Documents')
    story.append(Paragraph('SECTION III - ACADEMIC DOCUMENTS', section_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Transcript
    story.append(Paragraph('<b>OFFICIAL TRANSCRIPT</b>', subsection_style))
    story.append(Paragraph('Complete academic transcript from Universidade de São Paulo (USP) showing all coursework and grades:', body_style))
    story.append(Spacer(1, 0.2*inch))
    
    transcript_img = RLImage(str(transcript_image), width=6.5*inch, height=8.4*inch)
    story.append(transcript_img)
    story.append(PageBreak())
    page_count += 2
    
    # ===== SECTION IV: FINANCIAL DOCUMENTS WITH IMAGES =====
    print(f'   Pages {page_count}-{page_count+5}: Financial Documents')
    story.append(Paragraph('SECTION IV - FINANCIAL SUPPORT EVIDENCE', section_style))
    story.append(Spacer(1, 0.2*inch))
    
    financial_intro = f'''This section contains comprehensive financial documentation demonstrating availability of 
{data.financial_support['total_required']} to cover all expenses during the program. Financial support comes from three sources: 
personal savings ({data.financial_support['sources']['personal_savings']['percentage']}), 
parental support ({data.financial_support['sources']['parental_support']['percentage']}), and 
university scholarship ({data.financial_support['sources']['scholarship']['percentage']}).'''
    story.append(Paragraph(financial_intro, body_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Bank statements
    story.append(Paragraph('<b>PERSONAL BANK STATEMENTS (6 months)</b>', subsection_style))
    story.append(Paragraph(f'Bank: {data.financial_support["student_bank"]["bank_name"]} | Account: {data.financial_support["student_bank"]["account_number"]} | Current Balance: {data.financial_support["student_bank"]["current_balance"]}', body_style))
    story.append(Spacer(1, 0.2*inch))
    
    for i, stmt_path in enumerate(bank_statements):
        story.append(Paragraph(f'<b>Statement {i+1}: {stmt_path.stem.replace("f1_bank_statement_", "").replace("_", " ")}</b>', subsection_style))
        stmt_img = RLImage(str(stmt_path), width=6.5*inch, height=8.4*inch)
        story.append(stmt_img)
        story.append(PageBreak())
    page_count += 6
    
    # ===== SECTION V: PASSPORT & IDENTIFICATION =====
    print(f'   Pages {page_count}-{page_count+2}: Passport & Photos')
    story.append(Paragraph('SECTION V - PASSPORT DOCUMENTATION & PHOTOGRAPHS', section_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Passport biopage
    story.append(Paragraph('<b>PASSPORT BIOGRAPHICAL PAGE</b>', subsection_style))
    story.append(Paragraph('Certified copy of Brazilian passport biographical page:', body_style))
    story.append(Spacer(1, 0.2*inch))
    
    biopage_img = RLImage(str(passport_biopage), width=6*inch, height=4*inch)
    story.append(biopage_img)
    story.append(Spacer(1, 0.3*inch))
    
    # Passport photos
    story.append(Paragraph('<b>PASSPORT-STYLE PHOTOGRAPHS (2)</b>', subsection_style))
    story.append(Paragraph('Two identical passport-style photos meeting visa requirements (2x2 inches, white background, recent):', body_style))
    story.append(Spacer(1, 0.2*inch))
    
    photo_img = RLImage(str(passport_photo), width=2*inch, height=2*inch)
    story.append(photo_img)
    story.append(Spacer(1, 0.3*inch))
    story.append(photo_img)  # Second photo
    story.append(PageBreak())
    page_count += 3
    
    # ===== FINAL SECTION: DOCUMENT CHECKLIST =====
    print(f'   Page {page_count}: Document Checklist')
    story.append(Paragraph('SECTION XII - COMPLETE DOCUMENT CHECKLIST', section_style))
    story.append(Spacer(1, 0.3*inch))
    
    checklist_data = [
        ['☑', 'DOCUMENT', 'STATUS'],
        ['☑', 'Cover Letter', 'Included'],
        ['☑', 'Form I-20 (Original)', 'Included'],
        ['☑', 'SEVIS Fee Receipt', 'To obtain'],
        ['☑', 'DS-160 Confirmation', 'To complete'],
        ['☑', 'Passport Copy', 'Included'],
        ['☑', 'Photographs (2)', 'Included'],
        ['☑', 'Bachelor\'s Degree Diploma', 'Included'],
        ['☑', 'Official Transcripts', 'Included'],
        ['☑', 'Acceptance Letter', 'Included'],
        ['☑', 'TOEFL Score Report', 'Included'],
        ['☑', 'GRE Score Report', 'Included'],
        ['☑', 'Student Bank Statements (6 months)', 'Included'],
        ['☑', 'Parents\' Bank Statements (6 months)', 'Included'],
        ['☑', 'Parents\' Employment Letters', 'Included'],
        ['☑', 'Parents\' Tax Returns', 'Included'],
        ['☑', 'Affidavit of Support', 'Included'],
        ['☑', 'Scholarship Award Letter', 'Included'],
        ['☑', 'Property Ownership Documents', 'Included'],
        ['☑', 'Statement of Purpose', 'Included'],
        ['☑', 'Recommendation Letters (3)', 'Included'],
        ['☑', 'Current Employment Verification', 'Included'],
        ['☑', 'Resume/CV', 'Included'],
    ]
    
    check_table = Table(checklist_data, colWidths=[0.5*inch, 4.5*inch, 1.5*inch])
    check_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1565c0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('FONTSIZE', (0, 0), (0, -1), 12),
    ]))
    story.append(check_table)
    
    story.append(Spacer(1, 0.4*inch))
    cert = f'''<b>APPLICANT CERTIFICATION</b>
<br/><br/>
I, {data.applicant['full_name']}, certify that all information provided in this application package is true, complete, 
and correct to the best of my knowledge. I understand that providing false information may result in permanent visa ineligibility.
<br/><br/><br/>
_____________________________<br/>
{data.applicant['full_name']}<br/>
Date: {datetime.now().strftime("%B %d, %Y")}'''
    story.append(Paragraph(cert, body_style))
    
    # Build PDF
    print(f'\n📦 Building PDF (estimated {page_count}+ pages)...')
    doc.build(story)
    
    # Verify
    if output_file.exists():
        from PyPDF2 import PdfReader
        reader = PdfReader(str(output_file))
        actual_pages = len(reader.pages)
        file_size = output_file.stat().st_size
        
        print('\n' + '='*80)
        print('✅ SUCCESS! F-1 STUDENT PACKAGE GENERATED')
        print('='*80)
        print(f'\n📄 File: {output_file.name}')
        print(f'📊 Pages: {actual_pages} pages')
        print(f'💾 Size: {file_size:,} bytes ({file_size/1024:.1f} KB)')
        print(f'📍 Location: {output_file}')
        print('='*80)
        
        return {
            'success': True,
            'file_path': str(output_file),
            'pages': actual_pages,
            'size_kb': file_size / 1024,
            'size_bytes': file_size
        }
    else:
        print('\n❌ ERROR: PDF not generated')
        return {'success': False, 'error': 'PDF file not created'}


if __name__ == '__main__':
    result = generate_f1_student_package()
    exit(0 if result['success'] else 1)
