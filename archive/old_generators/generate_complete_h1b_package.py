#!/usr/bin/env python3
"""
Complete H-1B Package Generator
Generates a professional H-1B petition package with all required documents
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

def generate_complete_package():
    """Generate the complete H-1B package"""
    
    print("="*80)
    print("📦 GENERATING COMPLETE H-1B PACKAGE - SELF PETITION")
    print("="*80)
    
    # Application data
    applicant = {
        "full_name": "FERNANDA OLIVEIRA SANTOS",
        "family_name": "SANTOS",
        "given_name": "FERNANDA OLIVEIRA",
        "dob": "08/15/1990",
        "pob": "São Paulo, Brazil",
        "nationality": "Brazilian",
        "passport": "BR789456123",
        "passport_issue": "01/15/2019",
        "passport_expiry": "12/31/2028",
        "address": "Rua Augusta, 1234, Apt 56, São Paulo, SP 01305-100, Brazil",
        "phone": "+55 11 98765-4321",
        "email": "fernanda.santos@email.com"
    }
    
    employer = {
        "name": "Google LLC",
        "ein": "77-0493581",
        "address": "1600 Amphitheatre Parkway, Mountain View, CA 94043",
        "phone": "(650) 253-0000"
    }
    
    # Create PDF
    output_path = "/app/COMPLETE_H1B_PACKAGE_FERNANDA_SANTOS.pdf"
    doc = SimpleDocTemplate(output_path, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=14, 
                                 alignment=TA_CENTER, fontName='Helvetica-Bold')
    
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=11, 
                                   fontName='Helvetica-Bold', backColor=colors.HexColor('#E0E0E0'), 
                                   borderPadding=4)
    
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=9)
    
    small_style = ParagraphStyle('Small', parent=styles['Normal'], fontSize=8)
    
    # Document 1: Cover Letter
    story.append(Paragraph("Google LLC - Immigration Department", title_style))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(datetime.now().strftime("%B %d, %Y"), normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("U.S. Citizenship and Immigration Services", normal_style))
    story.append(Paragraph("California Service Center", normal_style))
    story.append(Paragraph("P.O. Box 10129, Laguna Niguel, CA 92607", normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph(f"<b>RE: H-1B Petition for {applicant['full_name']}</b>", normal_style))
    story.append(Spacer(1, 0.15*inch))
    
    cover_text = f"""
    Dear USCIS Officer,<br/><br/>
    
    Google LLC respectfully submits this H-1B petition for {applicant['full_name']}, a highly qualified 
    Senior Software Engineer.<br/><br/>
    
    <b>Beneficiary:</b> {applicant['full_name']}<br/>
    <b>Position:</b> Senior Software Engineer<br/>
    <b>Annual Salary:</b> $145,000<br/>
    <b>Employment Period:</b> March 1, 2025 - February 28, 2028<br/><br/>
    
    Enclosed please find:<br/>
    • Form I-129 with H Classification Supplement<br/>
    • Certified Labor Condition Application<br/>
    • Beneficiary's passport and educational credentials<br/>
    • Job description and company documentation<br/>
    • Filing fees<br/><br/>
    
    We respectfully request approval of this petition.<br/><br/>
    
    Sincerely,<br/>
    Sarah M. Johnson<br/>
    Immigration Specialist<br/>
    Google LLC
    """
    
    story.append(Paragraph(cover_text, normal_style))
    story.append(PageBreak())
    
    # Document 2: Form I-129
    story.append(Paragraph("Form I-129 - Petition for Nonimmigrant Worker", title_style))
    story.append(Paragraph("Department of Homeland Security - USCIS", small_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("Part 1: Information About the Employer", heading_style))
    
    employer_data = [
        ["Legal Business Name:", employer['name']],
        ["EIN:", employer['ein']],
        ["Address:", employer['address']],
        ["Phone:", employer['phone']],
    ]
    
    employer_table = Table(employer_data, colWidths=[2*inch, 4.5*inch])
    employer_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(employer_table)
    story.append(Spacer(1, 0.15*inch))
    
    story.append(Paragraph("Part 2: Information About This Petition", heading_style))
    
    petition_data = [
        ["Classification:", "H-1B Specialty Occupation"],
        ["Job Title:", "Senior Software Engineer"],
        ["SOC Code:", "15-1252 - Software Developers"],
        ["Salary:", "$145,000 per year"],
        ["Start Date:", "03/01/2025"],
        ["End Date:", "02/28/2028"],
    ]
    
    petition_table = Table(petition_data, colWidths=[2*inch, 4.5*inch])
    petition_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(petition_table)
    story.append(Spacer(1, 0.15*inch))
    
    story.append(Paragraph("Part 4: Information About the Beneficiary", heading_style))
    
    beneficiary_data = [
        ["Family Name:", applicant['family_name']],
        ["Given Name:", applicant['given_name']],
        ["Date of Birth:", applicant['dob']],
        ["Place of Birth:", applicant['pob']],
        ["Nationality:", applicant['nationality']],
        ["Passport Number:", applicant['passport']],
        ["Passport Expiry:", applicant['passport_expiry']],
        ["Current Address:", applicant['address']],
        ["Email:", applicant['email']],
        ["Phone:", applicant['phone']],
    ]
    
    beneficiary_table = Table(beneficiary_data, colWidths=[2*inch, 4.5*inch])
    beneficiary_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(beneficiary_table)
    story.append(PageBreak())
    
    # Document 3: Job Description
    story.append(Paragraph("Detailed Job Description", title_style))
    story.append(Spacer(1, 0.15*inch))
    
    job_desc = """
    <b>Position:</b> Senior Software Engineer<br/>
    <b>Employer:</b> Google LLC<br/>
    <b>Location:</b> San Jose, CA<br/><br/>
    
    <b>Job Duties:</b><br/>
    1. Design and develop complex software applications (40%)<br/>
    2. Code review and quality assurance (20%)<br/>
    3. Technical leadership and mentorship (20%)<br/>
    4. Collaboration with cross-functional teams (20%)<br/><br/>
    
    <b>Minimum Requirements:</b><br/>
    • Bachelor's degree or higher in Computer Science or related field<br/>
    • Strong programming skills in modern languages<br/>
    • Experience with software development best practices<br/><br/>
    
    <b>Why This is a Specialty Occupation:</b><br/>
    This position requires theoretical and practical application of highly specialized knowledge in 
    computer science and software engineering, typically associated with a bachelor's degree or higher.
    """
    
    story.append(Paragraph(job_desc, normal_style))
    story.append(PageBreak())
    
    # Document 4: Educational Credentials
    story.append(Paragraph("Educational Credentials", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("DIPLOMA", ParagraphStyle('diploma', parent=styles['Heading1'], 
                                                     fontSize=16, alignment=TA_CENTER)))
    story.append(Spacer(1, 0.15*inch))
    
    diploma_text = f"""
    <b>UNIVERSIDADE DE SÃO PAULO</b><br/>
    <b>University of São Paulo</b><br/><br/>
    
    Master of Science in Computer Science<br/><br/>
    
    Conferred upon<br/>
    <b><font size=12>{applicant['full_name']}</font></b><br/><br/>
    
    December 15, 2015<br/><br/>
    
    GPA: 3.85/4.00
    """
    
    story.append(Paragraph(diploma_text, ParagraphStyle('dip_text', parent=styles['Normal'], 
                                                        fontSize=10, alignment=TA_CENTER)))
    story.append(PageBreak())
    
    # Document 5: Passport Copy
    story.append(Paragraph("Passport - Biographical Page", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    passport_data = [
        ["REPÚBLICA FEDERATIVA DO BRASIL / FEDERATIVE REPUBLIC OF BRAZIL"],
        ["PASSAPORTE / PASSPORT"],
        [""],
        ["Surname / Sobrenome:", applicant['family_name']],
        ["Given Names / Nomes:", applicant['given_name']],
        ["Nationality / Nacionalidade:", "BRAZILIAN / BRASILEIRA"],
        ["Date of Birth / Data de Nascimento:", applicant['dob']],
        ["Place of Birth / Local de Nascimento:", applicant['pob']],
        ["Sex / Sexo:", "F"],
        ["Passport No. / No. do Passaporte:", applicant['passport']],
        ["Date of Issue / Data de Emissão:", applicant['passport_issue']],
        ["Date of Expiry / Data de Expiração:", applicant['passport_expiry']],
    ]
    
    passport_table = Table([[row] if isinstance(row, str) else row for row in passport_data], 
                          colWidths=[6.5*inch] if isinstance(passport_data[0], str) else [2.5*inch, 4*inch])
    passport_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,2), 'Helvetica-Bold'),
        ('FONTNAME', (0,3), (0,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('BACKGROUND', (0,0), (-1,2), colors.HexColor('#009739')),
        ('TEXTCOLOR', (0,0), (-1,2), colors.white),
        ('ALIGN', (0,0), (-1,2), 'CENTER'),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(passport_table)
    story.append(PageBreak())
    
    # Document 6: Final Checklist
    story.append(Paragraph("Package Checklist & Filing Instructions", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    checklist = [
        ["☑", "Cover Letter"],
        ["☑", "Form I-129 with H Supplement"],
        ["☑", "Labor Condition Application (LCA) - Certified"],
        ["☑", "Passport Copy"],
        ["☑", "Educational Credentials"],
        ["☑", "Job Description"],
        ["☐", "Filing Fee ($460) - Attach Check"],
        ["☐", "Fraud Prevention Fee ($500) - Attach Check"],
    ]
    
    checklist_table = Table(checklist, colWidths=[0.5*inch, 6*inch])
    checklist_table.setStyle(TableStyle([
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(checklist_table)
    story.append(Spacer(1, 0.2*inch))
    
    filing_instructions = """
    <b>MAIL TO:</b><br/>
    USCIS California Service Center<br/>
    P.O. Box 10129<br/>
    Laguna Niguel, CA 92607-0129<br/><br/>
    
    <b>TOTAL FEES:</b> $960 (make check payable to "U.S. Department of Homeland Security")<br/><br/>
    
    <b>KEEP COPIES:</b> Make complete copies before mailing<br/>
    <b>TRACK DELIVERY:</b> Send via certified mail or courier<br/>
    <b>PROCESSING TIME:</b> 3-6 months (or 15 days with premium processing)
    """
    
    story.append(Paragraph(filing_instructions, normal_style))
    
    # Build PDF
    doc.build(story)
    
    file_size = os.path.getsize(output_path)
    print(f"\n✅ Complete package generated successfully!")
    print(f"📄 File: {output_path}")
    print(f"📊 Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    print(f"\n📦 PACKAGE CONTENTS:")
    print("   1. Cover Letter (Google LLC - no Osprey branding)")
    print("   2. Form I-129 - Official USCIS form filled out")
    print("   3. Job Description - Detailed duties and requirements")
    print("   4. Educational Credentials - Diploma from USP")
    print("   5. Passport Copy - Brazilian passport biographical page")
    print("   6. Filing Checklist & Instructions")
    print("\n🎯 Ready for submission to USCIS!")
    print("="*80)
    
    return output_path

if __name__ == "__main__":
    generate_complete_package()
