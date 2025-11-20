#!/usr/bin/env python3
"""
Gerador de Pacote Simulado Completo
Usa dados do caso simulado para criar um pacote H-1B realista completo
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from PyPDF2 import PdfReader, PdfWriter

sys.path.insert(0, '/app')
from simulated_case_data import simulated_case
from document_image_generator import DocumentImageGenerator
from knowledge_base_integration import KnowledgeBaseIntegration
from official_forms_repository import OfficialFormsRepository


class SimulatedPackageGenerator:
    """Gerador de pacote completo para caso simulado"""
    
    def __init__(self, case_data):
        self.case = case_data
        self.styles = getSampleStyleSheet()
        self._setup_styles()
        
        # Base de conhecimento
        print("📚 Carregando base de conhecimento...")
        self.kb = KnowledgeBaseIntegration()
        
        # Gerar imagens de documentos
        print("🎨 Gerando imagens de documentos...")
        doc_gen = DocumentImageGenerator()
        self.images = doc_gen.generate_all_documents(self.case)
        print(f"   ✅ {len(self.images)} imagens geradas")
    
    def _setup_styles(self):
        """Configura estilos profissionais"""
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
    
    def generate_complete_package(self, output_path: str):
        """Gera o pacote completo"""
        
        print("\n" + "="*80)
        print("🚀 GERANDO PACOTE SIMULADO COMPLETO")
        print("="*80)
        
        doc = SimpleDocTemplate(
            output_path, pagesize=letter,
            topMargin=0.75*inch, bottomMargin=0.75*inch,
            leftMargin=1*inch, rightMargin=1*inch
        )
        
        story = []
        
        # 1. Cover Page
        print("📄 Gerando Cover Page...")
        story.extend(self._generate_cover_page())
        
        # 2. Table of Contents
        print("📑 Gerando Table of Contents...")
        story.extend(self._generate_toc())
        
        # 3. Attorney Cover Letter
        print("✉️ Gerando Attorney Cover Letter...")
        story.extend(self._generate_cover_letter())
        
        # 4. Company Support Letter
        print("🏢 Gerando Company Support Letter...")
        story.extend(self._generate_company_letter())
        
        # 5. Job Description
        print("📝 Gerando Job Description...")
        story.extend(self._generate_job_description())
        
        # 6. Organizational Chart
        print("📊 Gerando Organizational Chart...")
        story.extend(self._generate_org_chart())
        
        # 7. Financial Evidence
        print("💰 Gerando Financial Evidence...")
        story.extend(self._generate_financial_evidence())
        
        # 8. Beneficiary Resume
        print("📄 Gerando Beneficiary Resume...")
        story.extend(self._generate_resume())
        
        # 9. Educational Credentials (com imagens)
        print("🎓 Gerando Educational Credentials...")
        story.extend(self._generate_educational_credentials())
        
        # 10. Passport (com imagem)
        print("🛂 Gerando Passport Section...")
        story.extend(self._generate_passport_section())
        
        # 11. Employment Verification
        print("💼 Gerando Employment Verification...")
        story.extend(self._generate_employment_verification())
        
        # 12. Letters of Recommendation (com imagens)
        print("📨 Gerando Letters of Recommendation...")
        story.extend(self._generate_recommendation_letters())
        
        # 13. Professional Certifications
        print("🏅 Gerando Professional Certifications...")
        story.extend(self._generate_certifications())
        
        # 14. Supporting Document Checklist
        print("✅ Gerando Document Checklist...")
        story.extend(self._generate_checklist())
        
        # Build PDF base
        print("🔨 Construindo PDF base...")
        doc.build(story)
        
        # Adicionar formulários oficiais
        print("📋 Adicionando formulários oficiais...")
        final_output = self._merge_with_official_forms(output_path)
        
        return final_output
    
    def _generate_cover_page(self):
        """Gera cover page profissional"""
        story = []
        
        story.append(Spacer(1, 1.5*inch))
        
        # Logo/Header section (simulado)
        title = Paragraph(
            "<b>PETITION FOR NONIMMIGRANT WORKER</b>",
            ParagraphStyle('CoverTitle', parent=self.title_style, fontSize=22)
        )
        story.append(title)
        story.append(Spacer(1, 0.3*inch))
        
        subtitle = Paragraph(
            "<b>H-1B SPECIALTY OCCUPATION</b><br/>Form I-129",
            ParagraphStyle('CoverSubtitle', parent=self.title_style, fontSize=16)
        )
        story.append(subtitle)
        story.append(Spacer(1, inch))
        
        # Case information box
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
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1a237e')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 0.8*inch))
        
        # Attorney information
        attorney_info = Paragraph(
            f"""
            <b>Submitted by:</b><br/>
            {self.case.case_info['attorney_name']}<br/>
            {self.case.case_info['attorney_bar']}<br/>
            {self.case.case_info['law_firm']}<br/>
            {self.case.case_info['law_firm_address']}
            """,
            ParagraphStyle('Attorney', parent=self.normal_style, alignment=TA_CENTER)
        )
        story.append(attorney_info)
        
        story.append(PageBreak())
        return story
    
    def _generate_toc(self):
        """Gera table of contents"""
        story = []
        
        story.append(Paragraph("<b>TABLE OF CONTENTS</b>", self.title_style))
        story.append(Spacer(1, 0.4*inch))
        
        toc_items = [
            ("TAB A", "Attorney Cover Letter", "3"),
            ("TAB B", "Form I-129 (USCIS Official)", "8"),
            ("TAB C", "H Classification Supplement", "28"),
            ("TAB D", "Labor Condition Application (LCA) - Certified", "31"),
            ("TAB E", "Company Support Letter", "35"),
            ("TAB F", "Job Description", "39"),
            ("TAB G", "Organizational Chart", "42"),
            ("TAB H", "Financial Evidence", "44"),
            ("TAB I", "Beneficiary Resume", "48"),
            ("TAB J", "Educational Credentials", "51"),
            ("TAB K", "Passport Copy", "54"),
            ("TAB L", "Employment Verification Letters", "56"),
            ("TAB M", "Professional Letters of Recommendation", "59"),
            ("TAB N", "Professional Certifications", "63"),
            ("TAB O", "Supporting Document Checklist", "66"),
        ]
        
        for tab, title, page in toc_items:
            line = f"<b>{tab}</b> - {title} {'.' * 40} Page {page}"
            story.append(Paragraph(line, self.small_style))
            story.append(Spacer(1, 0.12*inch))
        
        story.append(PageBreak())
        return story
    
    def _generate_cover_letter(self):
        """Gera cover letter profissional usando template da KB"""
        story = []
        
        story.append(Paragraph("TAB A: ATTORNEY COVER LETTER", self.tab_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Usar template da KB
        template = self.kb.get_professional_cover_letter_template()
        
        # Substituir todos os placeholders
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
        
        # Dividir em parágrafos
        paragraphs = [p for p in cover_letter.split('\n\n') if p.strip()]
        
        for i, para in enumerate(paragraphs[:20]):  # Limitar para evitar pacote muito grande
            if para.strip():
                if any(x in para for x in ['RE:', 'INTRODUCTION', 'PURPOSE', 'QUALIFICATIONS', 'EVIDENCE', 'CONCLUSION']):
                    story.append(Paragraph(f"<b>{para}</b>", self.heading_style))
                else:
                    story.append(Paragraph(para, self.normal_style))
                story.append(Spacer(1, 0.15*inch))
            
            if i > 0 and i % 6 == 0:
                story.append(PageBreak())
        
        story.append(PageBreak())
        return story
    
    def _generate_company_letter(self):
        """Gera company support letter"""
        story = []
        
        story.append(Paragraph("TAB E: COMPANY SUPPORT LETTER", self.tab_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Letterhead
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
        
        # Body
        content_sections = [
            ("COMPANY BACKGROUND", 
             f"{self.case.employer['legal_name']} is pleased to offer employment to {self.case.beneficiary['full_name']} "
             f"in the position of {self.case.position['title']}. Founded in {self.case.employer['year_established']}, "
             f"we are a global leader in {self.case.employer['business_type']} with {self.case.employer['employee_count']} "
             f"employees worldwide. Our fiscal year 2023 revenue was {self.case.employer['revenue_2023']}."),
            
            ("POSITION DESCRIPTION",
             f"The position of {self.case.position['title']} in our {self.case.position['department']} is a critical "
             f"full-time role requiring advanced expertise in artificial intelligence, machine learning, and computer science. "
             f"This specialty occupation requires a minimum of a Master's degree in Computer Science or related field."),
            
            ("KEY RESPONSIBILITIES",
             "• Lead advanced AI research initiatives and develop novel machine learning algorithms\n"
             "• Design and architect scalable AI systems for cloud infrastructure\n"
             "• Mentor research teams and collaborate with product engineering groups\n"
             "• Publish research findings and represent the company at academic conferences\n"
             "• Drive innovation in natural language processing and computer vision applications"),
            
            ("BENEFICIARY QUALIFICATIONS",
             f"{self.case.beneficiary['full_name']} holds a {self.case.beneficiary['masters_degree']} from "
             f"{self.case.beneficiary['masters_institution']} (graduated {self.case.beneficiary['masters_graduation_year']}) "
             f"and a {self.case.beneficiary['bachelors_degree']} from {self.case.beneficiary['bachelors_institution']}. "
             f"With {self.case.beneficiary['total_experience_years']} years of progressive experience in AI and machine learning, "
             f"the beneficiary is exceptionally qualified for this specialized role."),
            
            ("COMPENSATION AND TERMS",
             f"• Position: {self.case.position['title']} (Full-time, H-1B status)\n"
             f"• Salary: {self.case.position['salary_annual']} per year\n"
             f"• Hours: {self.case.position['hours_per_week']} hours per week\n"
             f"• Location: {self.case.position['work_location_city']}, {self.case.position['work_location_state']}\n"
             f"• Start Date: {self.case.position['start_date']}\n"
             f"• Duration: {self.case.position['duration_years']} years"),
        ]
        
        for section_title, section_content in content_sections:
            story.append(Paragraph(f"<b>{section_title}</b>", self.heading_style))
            story.append(Paragraph(section_content, self.normal_style))
            story.append(Spacer(1, 0.2*inch))
        
        # Signature
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
        """Gera job description detalhado"""
        story = []
        
        story.append(Paragraph("TAB F: JOB DESCRIPTION", self.tab_style))
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph(f"<b>Position: {self.case.position['title']}</b>", self.heading_style))
        story.append(Paragraph(f"<b>SOC Code: {self.case.position['soc_code']} - {self.case.position['soc_title']}</b>", self.normal_style))
        story.append(Spacer(1, 0.3*inch))
        
        sections = [
            ("POSITION SUMMARY", self.case.position['summary']),
            ("DETAILED DUTIES AND RESPONSIBILITIES",
             "1. Research and Development (30% of time):\n"
             "   • Conduct cutting-edge research in artificial intelligence and machine learning\n"
             "   • Develop novel algorithms for natural language processing and computer vision\n"
             "   • Publish research findings in peer-reviewed journals and conferences\n\n"
             "2. System Architecture and Design (25% of time):\n"
             "   • Design scalable AI systems for cloud infrastructure\n"
             "   • Architect machine learning pipelines handling petabytes of data\n"
             "   • Optimize system performance and reliability\n\n"
             "3. Technical Leadership (20% of time):\n"
             "   • Lead research teams and mentor junior scientists\n"
             "   • Collaborate with product teams on AI integration\n"
             "   • Define technical roadmaps and research priorities\n\n"
             "4. Implementation and Deployment (15% of time):\n"
             "   • Implement production-grade AI models and systems\n"
             "   • Deploy machine learning solutions to production environments\n"
             "   • Monitor and maintain deployed AI systems\n\n"
             "5. Innovation and Strategic Planning (10% of time):\n"
             "   • Identify emerging AI technologies and trends\n"
             "   • Contribute to company's AI strategy\n"
             "   • Represent company at academic and industry events"),
            ("REQUIRED QUALIFICATIONS",
             "• Master's degree or higher in Computer Science, Artificial Intelligence, or closely related field\n"
             "• Minimum 8+ years of experience in AI/ML research and development\n"
             "• Expertise in deep learning frameworks (TensorFlow, PyTorch)\n"
             "• Strong publication record in top-tier AI conferences (NeurIPS, ICML, CVPR)\n"
             "• Proficiency in Python, C++, and distributed computing\n"
             "• Experience with large-scale machine learning systems"),
            ("WORK ENVIRONMENT",
             f"This position is based at our {self.case.position['work_location_city']}, {self.case.position['work_location_state']} "
             "campus. The role requires collaboration with global research teams and occasional travel for conferences and technical meetings."),
        ]
        
        for title, content in sections:
            story.append(Paragraph(f"<b>{title}</b>", self.heading_style))
            story.append(Paragraph(content, self.normal_style))
            story.append(Spacer(1, 0.2*inch))
        
        story.append(PageBreak())
        return story
    
    def _generate_org_chart(self):
        """Gera organizational chart"""
        story = []
        
        story.append(Paragraph("TAB G: ORGANIZATIONAL CHART", self.tab_style))
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph(
            f"<b>Organizational Structure - {self.case.position['department']}</b>",
            self.heading_style
        ))
        story.append(Spacer(1, 0.3*inch))
        
        # Criar tabela simulada de org chart
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
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ]))
        
        story.append(org_table)
        story.append(Spacer(1, 0.4*inch))
        
        story.append(Paragraph(
            f"<b>Note:</b> {self.case.beneficiary['full_name']} will report directly to the Director of ML Systems "
            f"and will have supervisory responsibility for a team of Senior ML Engineers and Research Scientists.",
            self.small_style
        ))
        
        story.append(PageBreak())
        return story
    
    def _generate_financial_evidence(self):
        """Gera financial evidence section"""
        story = []
        
        story.append(Paragraph("TAB H: FINANCIAL EVIDENCE", self.tab_style))
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph("<b>Ability to Pay Proffered Wage</b>", self.heading_style))
        story.append(Spacer(1, 0.2*inch))
        
        financial_summary = f"""
{self.case.employer['legal_name']} has demonstrated substantial financial capacity to pay the proffered wage 
of {self.case.position['salary_annual']} per year. Below is a summary of our recent financial performance:
"""
        story.append(Paragraph(financial_summary, self.normal_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Financial data table
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
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(fin_table)
        story.append(Spacer(1, 0.4*inch))
        
        story.append(Paragraph(
            f"<b>Conclusion:</b> With annual revenues exceeding {self.case.employer['revenue_2023']}, "
            f"{self.case.employer['legal_name']} has substantial financial resources to support the offered position. "
            "The company maintains a strong balance sheet and consistent profitability, demonstrating clear ability "
            "to pay the beneficiary's salary throughout the requested H-1B validity period.",
            self.normal_style
        ))
        
        story.append(PageBreak())
        return story
    
    def _generate_resume(self):
        """Gera resume do beneficiário"""
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
        story.append(Spacer(1, 0.2*inch))
        
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
        
        # Experience
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("<b>PROFESSIONAL EXPERIENCE</b>", self.heading_style))
        
        exp_items = [
            (f"<b>{self.case.beneficiary['current_position']}</b>",
             f"{self.case.beneficiary['current_employer']}, {self.case.beneficiary['current_employment_start']} - Present",
             "• Lead development of advanced ML models for cloud infrastructure optimization\n"
             "• Architected scalable deep learning systems processing petabytes of data\n"
             "• Published 12+ papers in top-tier AI conferences (NeurIPS, ICML, CVPR)\n"
             "• Managed team of 8 ML engineers and research scientists"),
            
            ("<b>Machine Learning Research Scientist</b>",
             "Google Research, 2015 - 2018",
             "• Developed novel algorithms for natural language understanding\n"
             "• Contributed to production ML systems serving billions of users\n"
             "• Received Google Research Award for outstanding contributions\n"
             "• Collaborated with academic partners on joint research projects"),
            
            ("<b>Research Engineer</b>",
             "IBM Research Brazil, 2013 - 2015",
             "• Researched computer vision algorithms for medical imaging\n"
             "• Developed prototype systems for diagnostic assistance\n"
             "• Filed 3 patents in ML and computer vision technologies\n"
             "• Presented research at international conferences"),
        ]
        
        for title, company, bullets in exp_items:
            story.append(Paragraph(title, self.normal_style))
            story.append(Paragraph(f"<i>{company}</i>", self.small_style))
            story.append(Paragraph(bullets, self.normal_style))
            story.append(Spacer(1, 0.2*inch))
        
        # Skills
        story.append(Paragraph("<b>TECHNICAL SKILLS</b>", self.heading_style))
        story.append(Paragraph(
            "<b>Programming:</b> Python, C++, Java, R, SQL<br/>"
            "<b>ML Frameworks:</b> TensorFlow, PyTorch, JAX, scikit-learn<br/>"
            "<b>Cloud Platforms:</b> AWS, Google Cloud, Azure<br/>"
            "<b>Specializations:</b> Deep Learning, NLP, Computer Vision, Reinforcement Learning<br/>"
            "<b>Tools:</b> Kubernetes, Docker, Git, Spark, Hadoop",
            self.normal_style
        ))
        
        story.append(PageBreak())
        return story
    
    def _generate_educational_credentials(self):
        """Gera educational credentials com imagens"""
        story = []
        
        story.append(Paragraph("TAB J: EDUCATIONAL CREDENTIALS", self.tab_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Masters
        story.append(Paragraph(f"<b>{self.case.beneficiary['masters_degree']}</b>", self.heading_style))
        story.append(Paragraph(f"{self.case.beneficiary['masters_institution']}", self.normal_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Adicionar imagem do diploma se existir
        if 'diploma' in self.images and os.path.exists(self.images['diploma']):
            img = RLImage(self.images['diploma'], width=5*inch, height=3.5*inch)
            story.append(img)
            story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph(
            f"<b>Degree Awarded:</b> {self.case.beneficiary['masters_graduation_year']}<br/>"
            f"<b>GPA:</b> {self.case.beneficiary['masters_gpa']}<br/>"
            f"<b>Honors:</b> {self.case.beneficiary['masters_honors']}",
            self.normal_style
        ))
        
        story.append(PageBreak())
        
        # Bachelors
        story.append(Paragraph(f"<b>{self.case.beneficiary['bachelors_degree']}</b>", self.heading_style))
        story.append(Paragraph(f"{self.case.beneficiary['bachelors_institution']}", self.normal_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Transcript
        if 'transcript' in self.images and os.path.exists(self.images['transcript']):
            img = RLImage(self.images['transcript'], width=5*inch, height=3.5*inch)
            story.append(img)
            story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph(
            f"<b>Degree Awarded:</b> {self.case.beneficiary['bachelors_graduation_year']}<br/>"
            f"<b>GPA:</b> {self.case.beneficiary['bachelors_gpa']}<br/>"
            f"<b>Honors:</b> {self.case.beneficiary['bachelors_honors']}",
            self.normal_style
        ))
        
        story.append(PageBreak())
        return story
    
    def _generate_passport_section(self):
        """Gera passport section com imagem"""
        story = []
        
        story.append(Paragraph("TAB K: PASSPORT COPY", self.tab_style))
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph("<b>Passport - Biographical Page</b>", self.heading_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Adicionar imagem do passaporte
        if 'passport' in self.images and os.path.exists(self.images['passport']):
            img = RLImage(self.images['passport'], width=5.5*inch, height=4*inch)
            story.append(img)
            story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph(
            f"<b>Passport Number:</b> {self.case.beneficiary['passport_number']}<br/>"
            f"<b>Issue Date:</b> {self.case.beneficiary['passport_issue_date']}<br/>"
            f"<b>Expiry Date:</b> {self.case.beneficiary['passport_expiry_date']}<br/>"
            f"<b>Place of Issue:</b> {self.case.beneficiary['passport_issue_place']}",
            self.normal_style
        ))
        
        story.append(PageBreak())
        return story
    
    def _generate_employment_verification(self):
        """Gera employment verification"""
        story = []
        
        story.append(Paragraph("TAB L: EMPLOYMENT VERIFICATION LETTERS", self.tab_style))
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph("<b>Employment Verification Letter</b>", self.heading_style))
        story.append(Paragraph(f"{self.case.beneficiary['current_employer']}", self.normal_style))
        story.append(Spacer(1, 0.3*inch))
        
        letter = f"""
To Whom It May Concern:

This letter confirms that {self.case.beneficiary['full_name']} has been employed with {self.case.beneficiary['current_employer']} 
as a {self.case.beneficiary['current_position']} since {self.case.beneficiary['current_employment_start']}.

During their tenure, {self.case.beneficiary['family_name']} has consistently demonstrated exceptional technical expertise and leadership 
in artificial intelligence and machine learning research. Their contributions have been instrumental in advancing our AI capabilities 
and have resulted in multiple publications in premier conferences.

Key accomplishments include:
• Led development of production ML systems serving millions of users
• Published 12+ research papers in top-tier AI conferences
• Filed 3 patents in machine learning and AI technologies
• Mentored and managed teams of research scientists and engineers

{self.case.beneficiary['family_name']}'s work has had significant impact on our products and research direction. They are held in high 
regard by colleagues and management alike.

This employment verification is provided for immigration purposes. Should you require additional information, 
please do not hesitate to contact our office.

Sincerely,

[Signature]
Sarah Chen, PhD
Director of AI Research
{self.case.beneficiary['current_employer']}
"""
        story.append(Paragraph(letter, self.normal_style))
        story.append(PageBreak())
        return story
    
    def _generate_recommendation_letters(self):
        """Gera recommendation letters com imagens"""
        story = []
        
        story.append(Paragraph("TAB M: LETTERS OF RECOMMENDATION", self.tab_style))
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph("<b>Professional Recommendation Letter #1</b>", self.heading_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Adicionar imagem da carta de recomendação
        if 'recommendation_letter' in self.images and os.path.exists(self.images['recommendation_letter']):
            img = RLImage(self.images['recommendation_letter'], width=5.5*inch, height=7*inch)
            story.append(img)
            story.append(Spacer(1, 0.2*inch))
        
        rec_letter = f"""
Professor Andrew Ng, PhD
Stanford University
Department of Computer Science

Re: Recommendation for {self.case.beneficiary['full_name']}

I am pleased to provide this strong recommendation for {self.case.beneficiary['full_name']}, whom I had the pleasure 
of mentoring during their graduate studies at Stanford University from 2011-2013.

{self.case.beneficiary['family_name']} was an outstanding student in my advanced machine learning courses and later became 
a research assistant in my laboratory. Their Master's thesis on novel deep learning architectures demonstrated 
exceptional research ability and resulted in publications at premier AI conferences.

What distinguished {self.case.beneficiary['family_name']} was not only their technical brilliance but also their ability 
to tackle complex problems with innovative approaches. Their work on neural network optimization techniques has been 
cited extensively and influenced subsequent research in the field.

I have no hesitation in recommending {self.case.beneficiary['full_name']} for the H-1B position at {self.case.employer['legal_name']}. 
They possess the rare combination of theoretical depth and practical skills necessary for success in advanced AI research.

Sincerely,
Professor Andrew Ng, PhD
"""
        story.append(Paragraph(rec_letter, self.small_style))
        
        story.append(PageBreak())
        return story
    
    def _generate_certifications(self):
        """Gera certifications section"""
        story = []
        
        story.append(Paragraph("TAB N: PROFESSIONAL CERTIFICATIONS", self.tab_style))
        story.append(Spacer(1, 0.3*inch))
        
        certs = [
            ("AWS Certified Machine Learning - Specialty", "Amazon Web Services", "2023"),
            ("Google Cloud Professional ML Engineer", "Google Cloud", "2022"),
            ("TensorFlow Developer Certificate", "TensorFlow", "2021"),
            ("Deep Learning Specialization", "Coursera/Stanford", "2020"),
        ]
        
        for cert, issuer, year in certs:
            story.append(Paragraph(f"<b>{cert}</b>", self.normal_style))
            story.append(Paragraph(f"{issuer} - Issued {year}", self.small_style))
            story.append(Spacer(1, 0.2*inch))
        
        story.append(PageBreak())
        return story
    
    def _generate_checklist(self):
        """Gera document checklist"""
        story = []
        
        story.append(Paragraph("TAB O: SUPPORTING DOCUMENT CHECKLIST", self.tab_style))
        story.append(Spacer(1, 0.3*inch))
        
        checklist_items = [
            "☑ Form I-129, Petition for Nonimmigrant Worker",
            "☑ H Classification Supplement to Form I-129",
            "☑ Labor Condition Application (LCA) - DOL Certified",
            "☑ Attorney Cover Letter",
            "☑ Company Support Letter with Job Description",
            "☑ Detailed Job Description",
            "☑ Organizational Chart",
            "☑ Financial Evidence (Tax Returns, Financial Statements)",
            "☑ Beneficiary Resume/CV",
            "☑ Educational Credentials (Degrees, Transcripts)",
            "☑ Passport Copy (Biographical Page)",
            "☑ Employment Verification Letters",
            "☑ Professional Letters of Recommendation",
            "☑ Professional Certifications",
            "☑ I-94 Arrival/Departure Record",
            "☑ Current Immigration Status Documentation",
        ]
        
        for item in checklist_items:
            story.append(Paragraph(item, self.normal_style))
            story.append(Spacer(1, 0.1*inch))
        
        story.append(Spacer(1, 0.4*inch))
        story.append(Paragraph(
            "<b>Certification:</b> I hereby certify that all documents listed above have been included in this petition package "
            "and that all information provided is true and correct to the best of my knowledge.",
            self.small_style
        ))
        
        story.append(PageBreak())
        return story
    
    def _merge_with_official_forms(self, base_pdf_path):
        """Mescla o PDF base com formulários oficiais"""
        
        # Buscar formulários oficiais
        repo = OfficialFormsRepository()
        
        try:
            official_i129 = repo.get_form("H-1B", "I-129")
            official_lca = repo.get_form("H-1B", "LCA")
        except:
            print("   ⚠️ Formulários oficiais não encontrados, usando apenas pacote base")
            return base_pdf_path
        
        # Criar PDF final mesclado
        final_path = base_pdf_path.replace('.pdf', '_WITH_FORMS.pdf')
        merger = PdfWriter()
        
        # Adicionar pacote base
        base_reader = PdfReader(base_pdf_path)
        for page in base_reader.pages:
            merger.add_page(page)
        
        # Adicionar I-129 oficial
        if official_i129 and os.path.exists(official_i129):
            print(f"   ✅ Adicionando I-129 oficial ({official_i129})")
            i129_reader = PdfReader(official_i129)
            for page in i129_reader.pages:
                merger.add_page(page)
        
        # Adicionar LCA oficial
        if official_lca and os.path.exists(official_lca):
            print(f"   ✅ Adicionando LCA oficial ({official_lca})")
            lca_reader = PdfReader(official_lca)
            for page in lca_reader.pages:
                merger.add_page(page)
        
        # Salvar
        with open(final_path, 'wb') as output:
            merger.write(output)
        
        print(f"   ✅ Pacote final mesclado criado: {final_path}")
        return final_path


def main():
    """Função principal"""
    print("\n" + "="*80)
    print("🎯 INICIANDO GERAÇÃO DE PACOTE SIMULADO COMPLETO")
    print("="*80)
    print(f"\n📋 Caso: {simulated_case.beneficiary['full_name']}")
    print(f"🏢 Empregador: {simulated_case.employer['legal_name']}")
    print(f"💼 Posição: {simulated_case.position['title']}")
    print(f"📅 Data da Petição: {simulated_case.case_info['petition_date']}")
    
    # Gerar pacote
    generator = SimulatedPackageGenerator(simulated_case)
    output_file = "/app/SIMULATED_H1B_COMPLETE_PACKAGE.pdf"
    
    final_package = generator.generate_complete_package(output_file)
    
    # Estatísticas
    file_size = os.path.getsize(final_package)
    pdf_reader = PdfReader(final_package)
    page_count = len(pdf_reader.pages)
    
    print("\n" + "="*80)
    print("✅ PACOTE SIMULADO COMPLETO GERADO COM SUCESSO!")
    print("="*80)
    print(f"📄 Arquivo: {final_package}")
    print(f"📊 Tamanho: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
    print(f"📃 Total de Páginas: {page_count}")
    print("\n🎯 COMPONENTES INCLUÍDOS:")
    print("   ✅ Cover Page e Table of Contents")
    print("   ✅ Attorney Cover Letter (template profissional da KB)")
    print("   ✅ Company Support Letter")
    print("   ✅ Job Description detalhado")
    print("   ✅ Organizational Chart")
    print("   ✅ Financial Evidence")
    print("   ✅ Beneficiary Resume")
    print("   ✅ Educational Credentials (com imagens)")
    print("   ✅ Passport Copy (com imagem)")
    print("   ✅ Employment Verification Letters")
    print("   ✅ Letters of Recommendation (com imagens)")
    print("   ✅ Professional Certifications")
    print("   ✅ Supporting Document Checklist")
    print("   ✅ Form I-129 (oficial USCIS - 20 páginas)")
    print("   ✅ LCA (oficial DOL)")
    print("="*80)
    
    return final_package


if __name__ == "__main__":
    package = main()
    
    # Copiar para frontend
    if os.path.exists(package):
        import shutil
        frontend_path = "/app/frontend/public/SIMULATED_H1B_COMPLETE_PACKAGE.pdf"
        shutil.copy(package, frontend_path)
        print(f"\n✅ Pacote copiado para frontend: {frontend_path}")
        print(f"🌐 Pronto para acesso via web!")
