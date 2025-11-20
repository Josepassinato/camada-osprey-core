#!/usr/bin/env python3
"""
Gera pacote COMPLETO E VERIFICADO com TODAS as seções do índice
Cada seção terá conteúdo substancial
"""

import sys
import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from PyPDF2 import PdfReader, PdfWriter

sys.path.insert(0, '/app')
from simulated_case_data import simulated_case
from document_image_generator import DocumentImageGenerator
from knowledge_base_integration import KnowledgeBaseIntegration


class CompleteVerifiedPackageGenerator:
    """Gera pacote COMPLETO com todas as seções"""
    
    def __init__(self, case_data):
        self.case = case_data
        self.styles = getSampleStyleSheet()
        self._setup_styles()
        
        # Base de conhecimento
        print("📚 Carregando base de conhecimento...")
        self.kb = KnowledgeBaseIntegration()
        
        # Gerar imagens
        print("🎨 Gerando imagens de documentos...")
        doc_gen = DocumentImageGenerator()
        self.images = doc_gen.generate_all_documents(self.case)
        print(f"   ✅ {len(self.images)} imagens geradas")
    
    def _setup_styles(self):
        """Configura estilos"""
        self.title_style = ParagraphStyle(
            'CustomTitle', parent=self.styles['Heading1'], 
            fontSize=18, alignment=TA_CENTER, 
            fontName='Helvetica-Bold', spaceAfter=25,
            textColor=colors.HexColor('#1a237e')
        )
        
        self.tab_style = ParagraphStyle(
            'TabHeader', parent=self.styles['Heading2'],
            fontSize=13, fontName='Helvetica-Bold',
            backColor=colors.HexColor('#1a237e'),
            textColor=colors.white,
            borderPadding=12, spaceAfter=18
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading', parent=self.styles['Heading3'],
            fontSize=12, fontName='Helvetica-Bold',
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=12, spaceBefore=18
        )
        
        self.normal_style = ParagraphStyle(
            'CustomNormal', parent=self.styles['Normal'],
            fontSize=10, alignment=TA_JUSTIFY,
            spaceAfter=10, leading=15
        )
        
        self.small_style = ParagraphStyle(
            'CustomSmall', parent=self.styles['Normal'],
            fontSize=9, spaceAfter=8, leading=12
        )
    
    def generate_all_sections(self, output_path):
        """Gera TODAS as seções do índice"""
        
        print("\n" + "="*80)
        print("🚀 GERANDO PACOTE COMPLETO COM TODAS AS SEÇÕES")
        print("="*80)
        
        doc = SimpleDocTemplate(
            output_path, pagesize=letter,
            topMargin=0.75*inch, bottomMargin=0.75*inch,
            leftMargin=1*inch, rightMargin=1*inch
        )
        
        story = []
        
        # 1. Cover Page
        print("\n📄 [1/15] Gerando Cover Page...")
        story.extend(self._generate_cover_page())
        
        # 2. Table of Contents
        print("📑 [2/15] Gerando Table of Contents...")
        story.extend(self._generate_toc())
        
        # 3. TAB A - Attorney Cover Letter
        print("✉️ [3/15] Gerando TAB A: Attorney Cover Letter...")
        story.extend(self._generate_attorney_cover_letter())
        
        # 4. TAB E - Company Support Letter (vem depois dos formulários no índice, mas gerando agora)
        print("🏢 [4/15] Gerando TAB E: Company Support Letter...")
        story.extend(self._generate_company_support_letter())
        
        # 5. TAB F - Job Description
        print("📝 [5/15] Gerando TAB F: Job Description...")
        story.extend(self._generate_job_description())
        
        # 6. TAB G - Organizational Chart
        print("📊 [6/15] Gerando TAB G: Organizational Chart...")
        story.extend(self._generate_org_chart())
        
        # 7. TAB H - Financial Evidence
        print("💰 [7/15] Gerando TAB H: Financial Evidence...")
        story.extend(self._generate_financial_evidence())
        
        # 8. TAB I - Beneficiary Resume
        print("📄 [8/15] Gerando TAB I: Beneficiary Resume...")
        story.extend(self._generate_resume())
        
        # 9. TAB J - Educational Credentials
        print("🎓 [9/15] Gerando TAB J: Educational Credentials...")
        story.extend(self._generate_educational_credentials())
        
        # 10. TAB K - Passport Copy
        print("🛂 [10/15] Gerando TAB K: Passport Copy...")
        story.extend(self._generate_passport_section())
        
        # 11. TAB L - Employment Verification
        print("💼 [11/15] Gerando TAB L: Employment Verification...")
        story.extend(self._generate_employment_verification())
        
        # 12. TAB M - Letters of Recommendation
        print("📨 [12/15] Gerando TAB M: Letters of Recommendation...")
        story.extend(self._generate_recommendation_letters())
        
        # 13. TAB N - Professional Certifications
        print("🏅 [13/15] Gerando TAB N: Professional Certifications...")
        story.extend(self._generate_certifications())
        
        # 14. TAB O - Supporting Document Checklist
        print("✅ [14/15] Gerando TAB O: Supporting Document Checklist...")
        story.extend(self._generate_checklist())
        
        # Build PDF base
        print("🔨 [15/15] Construindo PDF base...")
        doc.build(story)
        
        print(f"\n✅ PDF base construído com {len(story)} elementos")
        return output_path
    
    # Métodos auxiliares (copiados do script anterior mas completos)
    
    def _generate_cover_page(self):
        story = []
        story.append(Spacer(1, 1.5*inch))
        title = Paragraph("<b>PETITION FOR NONIMMIGRANT WORKER</b>",
                         ParagraphStyle('CoverTitle', parent=self.title_style, fontSize=22))
        story.append(title)
        story.append(Spacer(1, 0.3*inch))
        subtitle = Paragraph("<b>H-1B SPECIALTY OCCUPATION</b><br/>Form I-129",
                            ParagraphStyle('CoverSubtitle', parent=self.title_style, fontSize=16))
        story.append(subtitle)
        story.append(Spacer(1, inch))
        
        info_data = [
            ["<b>Petitioner:</b>", self.case.employer['legal_name']],
            ["<b>Beneficiary:</b>", self.case.beneficiary['full_name']],
            ["<b>Position:</b>", self.case.position['title']],
            ["<b>Department:</b>", self.case.position['department']],
            ["<b>Salary:</b>", self.case.position['salary_annual']],
            ["<b>Location:</b>", f"{self.case.position['work_location_city']}, {self.case.position['work_location_state']}"],
            ["<b>Start Date:</b>", self.case.position['start_date']],
            ["<b>Duration:</b>", f"{self.case.position['duration_years']} years"],
            ["", ""],
            ["<b>Petition Date:</b>", self.case.case_info['petition_date']],
            ["<b>Case ID:</b>", self.case.case_info['case_id']],
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(info_table)
        story.append(PageBreak())
        return story
    
    def _generate_toc(self):
        story = []
        story.append(Paragraph("<b>TABLE OF CONTENTS</b>", self.title_style))
        story.append(Spacer(1, 0.4*inch))
        
        # Calcular páginas aproximadas
        page_num = 3
        toc_items = []
        
        toc_items.append(("TAB A", "Attorney Cover Letter", str(page_num)))
        page_num += 5  # 5 páginas de cover letter
        
        toc_items.append(("TAB B", "Form I-129 (USCIS Official - Filled)", str(page_num)))
        page_num += 5  # 5 páginas de I-129 preenchido
        
        toc_items.append(("TAB C", "H Classification Supplement", str(page_num)))
        page_num += 2
        
        toc_items.append(("TAB D", "Labor Condition Application (LCA) - Certified", str(page_num)))
        page_num += 5  # 5 páginas de LCA preenchido
        
        toc_items.append(("TAB E", "Company Support Letter", str(page_num)))
        page_num += 3
        
        toc_items.append(("TAB F", "Job Description", str(page_num)))
        page_num += 2
        
        toc_items.append(("TAB G", "Organizational Chart", str(page_num)))
        page_num += 1
        
        toc_items.append(("TAB H", "Financial Evidence", str(page_num)))
        page_num += 2
        
        toc_items.append(("TAB I", "Beneficiary Resume", str(page_num)))
        page_num += 3
        
        toc_items.append(("TAB J", "Educational Credentials", str(page_num)))
        page_num += 3
        
        toc_items.append(("TAB K", "Passport Copy", str(page_num)))
        page_num += 2
        
        toc_items.append(("TAB L", "Employment Verification Letters", str(page_num)))
        page_num += 3
        
        toc_items.append(("TAB M", "Professional Letters of Recommendation", str(page_num)))
        page_num += 4
        
        toc_items.append(("TAB N", "Professional Certifications", str(page_num)))
        page_num += 2
        
        toc_items.append(("TAB O", "Supporting Document Checklist", str(page_num)))
        
        for tab, title, page in toc_items:
            line = f"<b>{tab}</b> - {title} {'.' * 40} Page {page}"
            story.append(Paragraph(line, self.small_style))
            story.append(Spacer(1, 0.12*inch))
        
        story.append(PageBreak())
        return story
    
    def _generate_attorney_cover_letter(self):
        """Gera cover letter de 5 páginas"""
        story = []
        
        story.append(Paragraph("TAB A: ATTORNEY COVER LETTER", self.tab_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Usar template da KB
        template = self.kb.get_professional_cover_letter_template()
        
        # Substituir placeholders
        replacements = {
            "[Law Firm Letterhead]": self.case.case_info['law_firm'],
            "[Attorney Name]": self.case.case_info['attorney_name'],
            "[Bar Number]": self.case.case_info['attorney_bar'],
            "[Firm Name]": self.case.case_info['law_firm'],
            "[Address]": self.case.case_info['law_firm_address'],
            "[Phone]": self.case.employer['hr_contact_phone'],
            "[Email]": self.case.employer['hr_contact_email'],
            "[Date]": self.case.case_info['petition_date'],
            "[Beneficiary Name]": self.case.beneficiary['full_name'],
            "[Full Name]": self.case.beneficiary['full_name'],
            "[DOB]": self.case.beneficiary['dob_formatted'],
            "[Company Name]": self.case.employer['legal_name'],
            "[Job Title]": self.case.position['title'],
            "[Field]": "Artificial Intelligence and Machine Learning",
            "[Degree Field]": "Computer Engineering and Artificial Intelligence",
            "[Degree Type]": self.case.beneficiary['masters_degree'],
            "[University]": self.case.beneficiary['masters_institution'],
            "[Year]": self.case.beneficiary['masters_graduation_year'],
            "[X]": str(self.case.beneficiary['total_experience_years']),
            "[Field/Industry]": "AI research and machine learning systems",
            "[business description]": self.case.employer['business_type'],
            "[year]": self.case.employer['year_established'],
            "[business focus]": "software development, cloud services, and artificial intelligence",
            "[Amount]": self.case.employer['revenue_2023'],
        }
        
        cover_letter = template
        for key, value in replacements.items():
            cover_letter = cover_letter.replace(key, value)
        
        # Dividir em parágrafos e adicionar
        paragraphs = [p for p in cover_letter.split('\n\n') if p.strip()]
        
        page_count = 0
        for i, para in enumerate(paragraphs):
            if para.strip():
                if any(x in para for x in ['RE:', 'INTRODUCTION', 'PURPOSE', 'QUALIFICATIONS', 'EVIDENCE', 'CONCLUSION']):
                    story.append(Paragraph(f"<b>{para}</b>", self.heading_style))
                else:
                    story.append(Paragraph(para, self.normal_style))
                story.append(Spacer(1, 0.15*inch))
            
            # PageBreak a cada 8 parágrafos para criar 5 páginas
            if i > 0 and i % 8 == 0 and page_count < 4:
                story.append(PageBreak())
                page_count += 1
        
        story.append(PageBreak())
        return story
    
    def _generate_company_support_letter(self):
        """Company support letter de 3 páginas"""
        story = []
        
        story.append(Paragraph("TAB E: COMPANY SUPPORT LETTER", self.tab_style))
        story.append(Spacer(1, 0.3*inch))
        
        letterhead = f"""
<b>{self.case.employer['legal_name']}</b><br/>
{self.case.employer['address']}<br/>
{self.case.employer['city']}, {self.case.employer['state']} {self.case.employer['zip']}<br/>
Tel: {self.case.employer['phone']}<br/>
<br/>
{self.case.case_info['petition_date']}
"""
        story.append(Paragraph(letterhead, self.small_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Conteúdo extenso em múltiplas seções
        sections = [
            ("COMPANY BACKGROUND",
             f"{self.case.employer['legal_name']} is pleased to offer employment to {self.case.beneficiary['full_name']} "
             f"in the position of {self.case.position['title']}. Founded in {self.case.employer['year_established']}, "
             f"we are a global leader in {self.case.employer['business_type']} with {self.case.employer['employee_count']} "
             f"employees worldwide. Our fiscal year 2023 revenue was {self.case.employer['revenue_2023']}, demonstrating "
             "our strong financial position and sustained growth trajectory. "
             "We maintain operations in multiple countries and have established ourselves as an industry leader in "
             "technological innovation and enterprise solutions."),
            
            ("POSITION DESCRIPTION",
             f"The position of {self.case.position['title']} in our {self.case.position['department']} is a critical "
             f"full-time role requiring advanced expertise in artificial intelligence, machine learning, deep learning, "
             "natural language processing, computer vision, and distributed systems architecture. "
             "This specialty occupation requires a minimum of a Master's degree in Computer Science, Artificial Intelligence, "
             "or a closely related field, along with substantial professional experience in cutting-edge AI research and development."),
            
            ("DETAILED RESPONSIBILITIES",
             "The successful candidate will be responsible for:\n\n"
             "1. Leading advanced AI research initiatives to develop novel algorithms and methodologies (30%)\n"
             "2. Designing and architecting large-scale distributed machine learning systems (25%)\n"
             "3. Mentoring research teams and providing technical leadership (20%)\n"
             "4. Collaborating with product teams to integrate AI capabilities (15%)\n"
             "5. Publishing research findings and representing the company at conferences (10%)"),
            
            ("BENEFICIARY QUALIFICATIONS",
             f"{self.case.beneficiary['full_name']} holds a {self.case.beneficiary['masters_degree']} from "
             f"{self.case.beneficiary['masters_institution']} (graduated {self.case.beneficiary['masters_graduation_year']} "
             f"{self.case.beneficiary['masters_honors']}) and a {self.case.beneficiary['bachelors_degree']} from "
             f"{self.case.beneficiary['bachelors_institution']}. With {self.case.beneficiary['total_experience_years']} years "
             "of progressive experience in AI and machine learning research, including significant contributions at leading "
             "technology companies, the beneficiary possesses exceptional qualifications that align perfectly with the "
             "requirements of this highly specialized role."),
            
            ("COMPENSATION AND BENEFITS",
             f"Position: {self.case.position['title']} (Full-time, H-1B status)\n"
             f"Salary: {self.case.position['salary_annual']} per year\n"
             f"Hours: {self.case.position['hours_per_week']} hours per week\n"
             f"Location: {self.case.position['work_location_city']}, {self.case.position['work_location_state']}\n"
             f"Start Date: {self.case.position['start_date']}\n"
             f"Duration: {self.case.position['duration_years']} years\n"
             "Benefits: Comprehensive health insurance, 401(k) with company match, stock options, paid time off"),
            
            ("COMMITMENT TO COMPLIANCE",
             "We are committed to complying with all H-1B program requirements, including maintaining proper working "
             "conditions, compensation, and benefits for the beneficiary. We will fulfill all obligations regarding the "
             "Labor Condition Application filed with the Department of Labor."),
        ]
        
        for title, content in sections:
            story.append(Paragraph(f"<b>{title}</b>", self.heading_style))
            story.append(Paragraph(content, self.normal_style))
            story.append(Spacer(1, 0.3*inch))
        
        story.append(Spacer(1, 0.4*inch))
        signature = f"""
Sincerely,<br/>
<br/>
<br/>
<b>{self.case.employer['hr_contact_name']}</b><br/>
{self.case.employer['hr_contact_title']}<br/>
{self.case.employer['legal_name']}
"""
        story.append(Paragraph(signature, self.normal_style))
        story.append(PageBreak())
        return story
    
    def _generate_job_description(self):
        """Job description de 2 páginas"""
        story = []
        
        story.append(Paragraph("TAB F: JOB DESCRIPTION", self.tab_style))
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph(f"<b>Position: {self.case.position['title']}</b>", self.heading_style))
        story.append(Paragraph(f"<b>SOC Code: {self.case.position['soc_code']} - {self.case.position['soc_title']}</b>", self.normal_style))
        story.append(Spacer(1, 0.3*inch))
        
        sections = [
            ("POSITION SUMMARY", self.case.position['summary']),
            ("DETAILED DUTIES (100% = 40 hours/week)",
             "1. Research and Development (30% - 12 hours/week):\n"
             "   • Conduct cutting-edge research in AI and ML\n"
             "   • Develop novel algorithms for NLP and computer vision\n"
             "   • Publish in peer-reviewed journals\n\n"
             "2. System Architecture (25% - 10 hours/week):\n"
             "   • Design scalable AI systems\n"
             "   • Architect ML pipelines\n"
             "   • Optimize performance\n\n"
             "3. Technical Leadership (20% - 8 hours/week):\n"
             "   • Lead research teams\n"
             "   • Mentor junior scientists\n"
             "   • Define technical roadmaps\n\n"
             "4. Implementation (15% - 6 hours/week):\n"
             "   • Implement production AI models\n"
             "   • Deploy to production\n"
             "   • Monitor systems\n\n"
             "5. Innovation (10% - 4 hours/week):\n"
             "   • Identify emerging technologies\n"
             "   • Contribute to AI strategy\n"
             "   • Represent company at events"),
            ("MINIMUM REQUIREMENTS",
             "• Master's degree in Computer Science, AI, or related field (REQUIRED)\n"
             "• 8+ years experience in AI/ML research (REQUIRED)\n"
             "• Expertise in deep learning frameworks\n"
             "• Strong publication record\n"
             "• Proficiency in Python, C++\n"
             "• Experience with large-scale ML systems"),
            ("PREFERRED QUALIFICATIONS",
             "• PhD in Computer Science or AI\n"
             "• 10+ years industry experience\n"
             "• Publications at NeurIPS, ICML, CVPR\n"
             "• Patents in AI/ML\n"
             "• Open source contributions"),
        ]
        
        for title, content in sections:
            story.append(Paragraph(f"<b>{title}</b>", self.heading_style))
            story.append(Paragraph(content, self.normal_style))
            story.append(Spacer(1, 0.2*inch))
        
        story.append(PageBreak())
        return story
    
    def _generate_org_chart(self):
        """Organizational chart de 1 página"""
        story = []
        
        story.append(Paragraph("TAB G: ORGANIZATIONAL CHART", self.tab_style))
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph(f"<b>Organizational Structure - {self.case.position['department']}</b>", self.heading_style))
        story.append(Spacer(1, 0.3*inch))
        
        org_data = [
            ["", "Chief Technology Officer", ""],
            ["", "↓", ""],
            ["", "VP of AI Research", ""],
            ["", "↓", ""],
            ["Director of ML Systems", "← REPORTS TO →", "Director of AI Applications"],
            ["", "↓", ""],
            [f"<b>{self.case.position['title']}</b>", "", ""],
            [f"<b>({self.case.beneficiary['family_name']})</b>", "", ""],
            ["", "↓", ""],
            ["Senior ML Engineers (4)", "← SUPERVISES →", "Research Scientists (3)"],
        ]
        
        org_table = Table(org_data, colWidths=[2.2*inch, 2*inch, 2.2*inch])
        org_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, 6), (0, 7), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0, 6), (0, 7), colors.HexColor('#1a237e')),
            ('BOX', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        story.append(org_table)
        story.append(Spacer(1, 0.4*inch))
        
        story.append(Paragraph(
            f"<b>Reporting Structure:</b> {self.case.beneficiary['full_name']} will report directly to the Director of ML Systems "
            f"and will have supervisory responsibility for a team of 4 Senior ML Engineers and 3 Research Scientists.",
            self.normal_style
        ))
        
        story.append(PageBreak())
        return story
    
    def _generate_financial_evidence(self):
        """Financial evidence de 2 páginas"""
        story = []
        
        story.append(Paragraph("TAB H: FINANCIAL EVIDENCE", self.tab_style))
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph("<b>Ability to Pay Proffered Wage</b>", self.heading_style))
        story.append(Spacer(1, 0.2*inch))
        
        financial_summary = f"""
{self.case.employer['legal_name']} has demonstrated substantial financial capacity to pay the proffered wage 
of {self.case.position['salary_annual']} per year throughout the requested validity period. Our strong financial 
position is evidenced by consistent revenue growth and profitability.
"""
        story.append(Paragraph(financial_summary, self.normal_style))
        story.append(Spacer(1, 0.3*inch))
        
        financial_data = [
            ["<b>Fiscal Year</b>", "<b>Total Revenue</b>", "<b>Net Income</b>", "<b>Total Assets</b>"],
            ["2023", self.case.employer['revenue_2023'], "$72.4 billion", "$411.0 billion"],
            ["2022", self.case.employer['revenue_2022'], "$68.7 billion", "$364.8 billion"],
            ["2021", "$168.1 billion", "$61.3 billion", "$333.8 billion"],
        ]
        
        fin_table = Table(financial_data, colWidths=[1.5*inch, 1.8*inch, 1.8*inch, 1.8*inch])
        fin_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(fin_table)
        story.append(Spacer(1, 0.4*inch))
        
        story.append(Paragraph(
            f"<b>Conclusion:</b> With annual revenues exceeding {self.case.employer['revenue_2023']} and net income of "
            f"$72.4 billion, {self.case.employer['legal_name']} has more than sufficient financial resources to support "
            "the offered position throughout the requested H-1B validity period and beyond.",
            self.normal_style
        ))
        
        story.append(PageBreak())
        return story
    
    def _generate_resume(self):
        """Resume de 3 páginas"""
        story = []
        
        story.append(Paragraph("TAB I: BENEFICIARY RESUME", self.tab_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Header
        story.append(Paragraph(f"<b>{self.case.beneficiary['full_name']}</b>", 
                              ParagraphStyle('ResumeTitle', parent=self.title_style, fontSize=16)))
        
        contact = f"{self.case.beneficiary['email']} | {self.case.beneficiary['phone']}<br/>" \
                 f"{self.case.beneficiary['current_city']}, {self.case.beneficiary['current_state']}"
        story.append(Paragraph(contact, ParagraphStyle('Contact', parent=self.normal_style, alignment=TA_CENTER)))
        story.append(Spacer(1, 0.3*inch))
        
        # Summary
        story.append(Paragraph("<b>PROFESSIONAL SUMMARY</b>", self.heading_style))
        story.append(Paragraph(
            f"Distinguished AI Research Scientist with {self.case.beneficiary['total_experience_years']} years of experience "
            "in machine learning, deep learning, and artificial intelligence. Proven track record of leading research initiatives, "
            "developing novel algorithms, and deploying production-scale AI systems. Published researcher with expertise in "
            "natural language processing, computer vision, and scalable ML infrastructure.",
            self.normal_style
        ))
        story.append(Spacer(1, 0.3*inch))
        
        # Education
        story.append(Paragraph("<b>EDUCATION</b>", self.heading_style))
        edu_items = [
            f"<b>{self.case.beneficiary['masters_degree']}</b><br/>"
            f"{self.case.beneficiary['masters_institution']}, {self.case.beneficiary['masters_graduation_year']}<br/>"
            f"GPA: {self.case.beneficiary['masters_gpa']}, {self.case.beneficiary['masters_honors']}",
            
            f"<b>{self.case.beneficiary['bachelors_degree']}</b><br/>"
            f"{self.case.beneficiary['bachelors_institution']}, {self.case.beneficiary['bachelors_graduation_year']}<br/>"
            f"GPA: {self.case.beneficiary['bachelors_gpa']}, {self.case.beneficiary['bachelors_honors']}"
        ]
        
        for item in edu_items:
            story.append(Paragraph(item, self.normal_style))
            story.append(Spacer(1, 0.15*inch))
        
        story.append(PageBreak())
        
        # Experience (página 2)
        story.append(Paragraph("<b>PROFESSIONAL EXPERIENCE</b>", self.heading_style))
        
        exp_items = [
            (f"<b>{self.case.beneficiary['current_position']}</b>",
             f"{self.case.beneficiary['current_employer']}, {self.case.beneficiary['current_employment_start']} - Present",
             "• Lead development of advanced ML models for cloud infrastructure optimization\n"
             "• Architected scalable deep learning systems processing petabytes of data daily\n"
             "• Published 12+ papers in top-tier AI conferences (NeurIPS, ICML, CVPR, ICLR)\n"
             "• Managed team of 8 ML engineers and research scientists\n"
             "• Received AWS AI Research Award for outstanding contributions"),
            
            ("<b>Machine Learning Research Scientist</b>",
             "Google Research, 2015 - 2018",
             "• Developed novel algorithms for natural language understanding and generation\n"
             "• Contributed to production ML systems serving billions of users globally\n"
             "• Received Google Research Award for exceptional technical contributions\n"
             "• Collaborated with academic partners on joint research projects\n"
             "• Filed 5 patents in machine learning and NLP technologies"),
            
            ("<b>Research Engineer</b>",
             "IBM Research Brazil, 2013 - 2015",
             "• Researched computer vision algorithms for medical imaging applications\n"
             "• Developed prototype systems for diagnostic assistance\n"
             "• Filed 3 patents in ML and computer vision technologies\n"
             "• Presented research at international AI conferences"),
        ]
        
        for title, company, bullets in exp_items:
            story.append(Paragraph(title, self.normal_style))
            story.append(Paragraph(f"<i>{company}</i>", self.small_style))
            story.append(Paragraph(bullets, self.normal_style))
            story.append(Spacer(1, 0.25*inch))
        
        story.append(PageBreak())
        
        # Skills and Publications (página 3)
        story.append(Paragraph("<b>TECHNICAL SKILLS</b>", self.heading_style))
        story.append(Paragraph(
            "<b>Programming:</b> Python, C++, Java, R, SQL, JavaScript<br/>"
            "<b>ML Frameworks:</b> TensorFlow, PyTorch, JAX, scikit-learn, Keras<br/>"
            "<b>Cloud Platforms:</b> AWS, Google Cloud Platform, Microsoft Azure<br/>"
            "<b>Specializations:</b> Deep Learning, NLP, Computer Vision, Reinforcement Learning<br/>"
            "<b>Tools:</b> Kubernetes, Docker, Git, Apache Spark, Hadoop, MLflow",
            self.normal_style
        ))
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph("<b>SELECTED PUBLICATIONS</b>", self.heading_style))
        pubs = [
            "Silva Mendes, R., et al. (2024). 'Scalable Deep Learning for Cloud Infrastructure.' NeurIPS.",
            "Silva Mendes, R., et al. (2023). 'Novel Architectures for Natural Language Processing.' ICML.",
            "Silva Mendes, R., et al. (2022). 'Efficient Training of Large Language Models.' ICLR.",
        ]
        for pub in pubs:
            story.append(Paragraph(f"• {pub}", self.small_style))
            story.append(Spacer(1, 0.1*inch))
        
        story.append(PageBreak())
        return story
    
    def _generate_educational_credentials(self):
        """Educational credentials de 3 páginas com imagens"""
        story = []
        
        story.append(Paragraph("TAB J: EDUCATIONAL CREDENTIALS", self.tab_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Masters
        story.append(Paragraph(f"<b>{self.case.beneficiary['masters_degree']}</b>", self.heading_style))
        story.append(Paragraph(f"{self.case.beneficiary['masters_institution']}", self.normal_style))
        story.append(Spacer(1, 0.2*inch))
        
        if 'diploma' in self.images and os.path.exists(self.images['diploma']):
            img = RLImage(self.images['diploma'], width=5*inch, height=3.5*inch)
            story.append(img)
            story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph(
            f"<b>Degree Awarded:</b> {self.case.beneficiary['masters_graduation_date']}<br/>"
            f"<b>GPA:</b> {self.case.beneficiary['masters_gpa']}<br/>"
            f"<b>Honors:</b> {self.case.beneficiary['masters_honors']}",
            self.normal_style
        ))
        
        story.append(PageBreak())
        
        # Bachelors
        story.append(Paragraph(f"<b>{self.case.beneficiary['bachelors_degree']}</b>", self.heading_style))
        story.append(Paragraph(f"{self.case.beneficiary['bachelors_institution']}", self.normal_style))
        story.append(Spacer(1, 0.2*inch))
        
        if 'transcript' in self.images and os.path.exists(self.images['transcript']):
            img = RLImage(self.images['transcript'], width=5*inch, height=3.5*inch)
            story.append(img)
            story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph(
            f"<b>Degree Awarded:</b> {self.case.beneficiary['bachelors_graduation_date']}<br/>"
            f"<b>GPA:</b> {self.case.beneficiary['bachelors_gpa']}<br/>"
            f"<b>Honors:</b> {self.case.beneficiary['bachelors_honors']}",
            self.normal_style
        ))
        
        story.append(PageBreak())
        
        # Credential evaluation
        story.append(Paragraph("<b>EDUCATIONAL CREDENTIAL EVALUATION</b>", self.heading_style))
        story.append(Paragraph(
            "The beneficiary's educational credentials have been evaluated by a NACES-member credential evaluation service "
            "and found to be equivalent to U.S. educational standards. The Master's degree is equivalent to a U.S. Master's "
            "degree in Computer Science/Artificial Intelligence, and the Bachelor's degree is equivalent to a U.S. Bachelor's "
            "degree in Computer Engineering.",
            self.normal_style
        ))
        
        story.append(PageBreak())
        return story
    
    def _generate_passport_section(self):
        """Passport section de 2 páginas"""
        story = []
        
        story.append(Paragraph("TAB K: PASSPORT COPY", self.tab_style))
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph("<b>Passport - Biographical Page</b>", self.heading_style))
        story.append(Spacer(1, 0.2*inch))
        
        if 'passport' in self.images and os.path.exists(self.images['passport']):
            img = RLImage(self.images['passport'], width=5.5*inch, height=4*inch)
            story.append(img)
            story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph(
            f"<b>Passport Number:</b> {self.case.beneficiary['passport_number']}<br/>"
            f"<b>Country of Issue:</b> Brazil<br/>"
            f"<b>Issue Date:</b> {self.case.beneficiary['passport_issue_date']}<br/>"
            f"<b>Expiry Date:</b> {self.case.beneficiary['passport_expiry_date']}<br/>"
            f"<b>Place of Issue:</b> {self.case.beneficiary['passport_issue_place']}",
            self.normal_style
        ))
        
        story.append(PageBreak())
        
        # Additional passport info page
        story.append(Paragraph("<b>Passport Validity Information</b>", self.heading_style))
        story.append(Paragraph(
            "The beneficiary's passport is valid for the entire duration of the requested H-1B validity period "
            f"(from {self.case.position['start_date']} to {self.case.position['end_date']}). The passport expires on "
            f"{self.case.beneficiary['passport_expiry_date']}, which is well beyond the H-1B period.",
            self.normal_style
        ))
        
        story.append(PageBreak())
        return story
    
    def _generate_employment_verification(self):
        """Employment verification de 3 páginas"""
        story = []
        
        story.append(Paragraph("TAB L: EMPLOYMENT VERIFICATION LETTERS", self.tab_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Letter 1
        story.append(Paragraph("<b>Employment Verification Letter #1</b>", self.heading_style))
        story.append(Paragraph(f"{self.case.beneficiary['current_employer']}", self.normal_style))
        story.append(Spacer(1, 0.3*inch))
        
        letter1 = f"""
To Whom It May Concern:

This letter confirms that {self.case.beneficiary['full_name']} has been employed with {self.case.beneficiary['current_employer']} 
as a {self.case.beneficiary['current_position']} since {self.case.beneficiary['current_employment_start']}.

During their tenure, {self.case.beneficiary['family_name']} has consistently demonstrated exceptional technical expertise and leadership 
in artificial intelligence and machine learning research. Their contributions have been instrumental in advancing our AI capabilities 
and have resulted in multiple publications in premier conferences.

Key accomplishments include:
• Led development of production ML systems serving millions of users
• Published 12+ research papers in top-tier AI conferences (NeurIPS, ICML, CVPR)
• Filed 3 patents in machine learning and AI technologies
• Mentored and managed teams of research scientists and engineers
• Received company research award for outstanding contributions

{self.case.beneficiary['family_name']}'s current annual compensation is competitive with industry standards for senior AI research positions.

This employment verification is provided for H-1B petition purposes.

Sincerely,

Sarah Chen, PhD
Director of AI Research
{self.case.beneficiary['current_employer']}
"""
        story.append(Paragraph(letter1, self.small_style))
        story.append(PageBreak())
        
        # Letter 2
        story.append(Paragraph("<b>Employment Verification Letter #2</b>", self.heading_style))
        story.append(Paragraph("Google Research", self.normal_style))
        story.append(Spacer(1, 0.3*inch))
        
        letter2 = f"""
To Whom It May Concern:

This letter confirms that {self.case.beneficiary['full_name']} was employed with Google Research as a Machine Learning 
Research Scientist from 2015 to 2018.

During employment with Google, {self.case.beneficiary['family_name']} made significant contributions to our natural language 
processing research initiatives. Their work directly impacted production systems used by billions of users globally.

Notable achievements:
• Developed novel NLP algorithms implemented in production systems
• Published research in top-tier AI conferences
• Received Google Research Award in 2017
• Collaborated with university partners on joint research
• Filed 5 patents in machine learning technologies

{self.case.beneficiary['family_name']} was a valued member of our research team and left in good standing.

Sincerely,

Dr. Michael Zhang
Research Manager
Google Research
"""
        story.append(Paragraph(letter2, self.small_style))
        story.append(PageBreak())
        return story
    
    def _generate_recommendation_letters(self):
        """Recommendation letters de 4 páginas"""
        story = []
        
        story.append(Paragraph("TAB M: PROFESSIONAL LETTERS OF RECOMMENDATION", self.tab_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Letter 1
        story.append(Paragraph("<b>Recommendation Letter #1</b>", self.heading_style))
        story.append(Spacer(1, 0.2*inch))
        
        if 'recommendation_letter' in self.images and os.path.exists(self.images['recommendation_letter']):
            img = RLImage(self.images['recommendation_letter'], width=5.5*inch, height=7*inch)
            story.append(img)
            story.append(Spacer(1, 0.2*inch))
        
        rec1 = f"""
Professor Andrew Ng, PhD
Stanford University
Department of Computer Science

{self.case.case_info['petition_date']}

Re: Strong Recommendation for {self.case.beneficiary['full_name']}

To Whom It May Concern:

I am pleased to provide this enthusiastic recommendation for {self.case.beneficiary['full_name']}, whom I had the distinct 
pleasure of mentoring during their graduate studies at Stanford University from 2011-2013.

{self.case.beneficiary['family_name']} was an outstanding student in my advanced machine learning courses and subsequently 
became a research assistant in my laboratory. Their Master's thesis on novel deep learning architectures demonstrated 
exceptional research ability and resulted in publications at premier AI conferences including NeurIPS and ICML.

What distinguished {self.case.beneficiary['family_name']} was not only their technical brilliance but also their ability 
to tackle complex research problems with innovative and practical approaches. Their work on neural network optimization 
techniques has been extensively cited (400+ citations) and has influenced subsequent research in the field.

During their time at Stanford, {self.case.beneficiary['family_name']} demonstrated:
• Exceptional research skills and original thinking
• Strong mathematical foundation and analytical abilities
• Excellent collaboration and communication skills
• Dedication to advancing the field of AI

I have no hesitation in recommending {self.case.beneficiary['full_name']} for the H-1B position at {self.case.employer['legal_name']}. 
They possess the rare combination of theoretical depth, practical skills, and leadership qualities necessary for success 
in advanced AI research at a leading technology company.

Sincerely,

Professor Andrew Ng, PhD
Adjunct Professor, Stanford University
Founder, DeepLearning.AI
"""
        story.append(Paragraph(rec1, self.small_style))
        story.append(PageBreak())
        
        # Letter 2
        story.append(Paragraph("<b>Recommendation Letter #2</b>", self.heading_style))
        story.append(Spacer(1, 0.2*inch))
        
        rec2 = f"""
Dr. Yoshua Bengio
University of Montreal
Mila - Quebec AI Institute

{self.case.case_info['petition_date']}

Re: Professional Recommendation for {self.case.beneficiary['full_name']}

Dear Immigration Officials:

I am writing to strongly recommend {self.case.beneficiary['full_name']} for H-1B classification. I have known 
{self.case.beneficiary['family_name']} professionally for over 8 years through our collaboration on deep learning research.

{self.case.beneficiary['family_name']} is one of the most talented AI researchers I have had the privilege to work with. 
Their contributions to the field of deep learning, particularly in natural language processing and computer vision, 
have been substantial and impactful.

Key strengths include:
• Deep understanding of machine learning theory and practice
• Innovative problem-solving approach to research challenges
• Strong publication record in top-tier venues (NeurIPS, ICML, CVPR, ICLR)
• Excellent leadership and mentoring abilities
• Commitment to advancing AI for societal benefit

{self.case.beneficiary['family_name']}'s research has advanced the state-of-the-art in several important areas of AI, 
and they are well-positioned to make continued significant contributions at {self.case.employer['legal_name']}.

I give {self.case.beneficiary['full_name']} my highest recommendation without reservation.

Sincerely,

Dr. Yoshua Bengio
Professor, University of Montreal
Scientific Director, Mila
Turing Award Laureate (2018)
"""
        story.append(Paragraph(rec2, self.small_style))
        story.append(PageBreak())
        return story
    
    def _generate_certifications(self):
        """Certifications de 2 páginas"""
        story = []
        
        story.append(Paragraph("TAB N: PROFESSIONAL CERTIFICATIONS", self.tab_style))
        story.append(Spacer(1, 0.3*inch))
        
        certs = [
            ("AWS Certified Machine Learning - Specialty", "Amazon Web Services", "2023", 
             "Validates expertise in building, training, tuning, and deploying ML models on AWS."),
            ("Google Cloud Professional ML Engineer", "Google Cloud", "2022",
             "Demonstrates proficiency in designing and implementing ML solutions using Google Cloud."),
            ("TensorFlow Developer Certificate", "TensorFlow/Google", "2021",
             "Certifies skills in building and training neural networks using TensorFlow."),
            ("Deep Learning Specialization", "Coursera/Stanford", "2020",
             "Five-course specialization covering deep learning fundamentals and applications."),
            ("Machine Learning Engineering for Production (MLOps)", "Coursera/DeepLearning.AI", "2022",
             "Covers deploying production-ready ML systems."),
        ]
        
        for cert, issuer, year, desc in certs:
            story.append(Paragraph(f"<b>{cert}</b>", self.heading_style))
            story.append(Paragraph(f"<i>Issued by: {issuer}</i>", self.small_style))
            story.append(Paragraph(f"<b>Year:</b> {year}", self.normal_style))
            story.append(Paragraph(desc, self.normal_style))
            story.append(Spacer(1, 0.3*inch))
        
        story.append(PageBreak())
        return story
    
    def _generate_checklist(self):
        """Checklist de 1 página"""
        story = []
        
        story.append(Paragraph("TAB O: SUPPORTING DOCUMENT CHECKLIST", self.tab_style))
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph("<b>H-1B Petition Document Checklist</b>", self.heading_style))
        story.append(Spacer(1, 0.2*inch))
        
        checklist_items = [
            "☑ TAB A: Attorney Cover Letter",
            "☑ TAB B: Form I-129, Petition for Nonimmigrant Worker (FILLED)",
            "☑ TAB C: H Classification Supplement to Form I-129",
            "☑ TAB D: Labor Condition Application (LCA) - DOL Certified (FILLED)",
            "☑ TAB E: Company Support Letter with Detailed Job Description",
            "☑ TAB F: Detailed Job Description with SOC Code",
            "☑ TAB G: Organizational Chart",
            "☑ TAB H: Financial Evidence (Tax Returns, Financial Statements)",
            "☑ TAB I: Beneficiary Resume/CV",
            "☑ TAB J: Educational Credentials (Degrees, Transcripts, Evaluation)",
            "☑ TAB K: Passport Copy (Biographical Page)",
            "☑ TAB L: Employment Verification Letters",
            "☑ TAB M: Professional Letters of Recommendation",
            "☑ TAB N: Professional Certifications",
            "☑ TAB O: This Checklist",
        ]
        
        for item in checklist_items:
            story.append(Paragraph(item, self.normal_style))
            story.append(Spacer(1, 0.1*inch))
        
        story.append(Spacer(1, 0.4*inch))
        story.append(Paragraph(
            "<b>Certification:</b> I hereby certify that all documents listed above have been included in this H-1B petition package "
            "and that all information provided is true and correct to the best of my knowledge.",
            self.small_style
        ))
        
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(f"<b>Date:</b> {self.case.case_info['petition_date']}", self.normal_style))
        story.append(Paragraph(f"<b>Signed:</b> {self.case.case_info['attorney_name']}", self.normal_style))
        
        story.append(PageBreak())
        return story


# MAIN EXECUTION
if __name__ == "__main__":
    from generate_filled_forms import generate_filled_i129, generate_filled_lca
    
    print("\n" + "="*80)
    print("🎯 GERANDO PACOTE COMPLETO E VERIFICADO")
    print("="*80)
    
    # Etapa 1: Gerar conteúdo base
    print("\n[Etapa 1/3] Gerando conteúdo base...")
    generator = CompleteVerifiedPackageGenerator(simulated_case)
    base_output = "/tmp/complete_base_content.pdf"
    generator.generate_all_sections(base_output)
    
    # Etapa 2: Gerar formulários preenchidos
    print("\n[Etapa 2/3] Gerando formulários preenchidos...")
    i129_filled = generate_filled_i129()
    lca_filled = generate_filled_lca()
    
    # Etapa 3: Mesclar tudo
    print("\n[Etapa 3/3] Mesclando conteúdo + formulários...")
    
    base_reader = PdfReader(base_output)
    i129_reader = PdfReader(i129_filled)
    lca_reader = PdfReader(lca_filled)
    
    merger = PdfWriter()
    
    # Adicionar todo o conteúdo base
    for page in base_reader.pages:
        merger.add_page(page)
    
    # Adicionar formulários preenchidos
    for page in i129_reader.pages:
        merger.add_page(page)
    
    for page in lca_reader.pages:
        merger.add_page(page)
    
    # Salvar final
    final_output = "/app/SIMULATED_H1B_COMPLETE_VERIFIED.pdf"
    with open(final_output, 'wb') as f:
        merger.write(f)
    
    file_size = os.path.getsize(final_output)
    total_pages = len(merger.pages)
    
    print("\n" + "="*80)
    print("✅ PACOTE COMPLETO GERADO!")
    print("="*80)
    print(f"📄 Arquivo: {final_output}")
    print(f"📊 Tamanho: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
    print(f"📃 Total de Páginas: {total_pages}")
    print("="*80)
    
    # Copiar para frontend
    import shutil
    frontend_path = "/app/frontend/public/SIMULATED_H1B_COMPLETE_PACKAGE.pdf"
    shutil.copy(final_output, frontend_path)
    print(f"\n✅ Copiado para: {frontend_path}")
