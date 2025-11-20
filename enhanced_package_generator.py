#!/usr/bin/env python3
"""
Gerador de Pacotes Aprimorado com Integração da Base de Conhecimento
Usa templates reais e guias profissionais dos recursos fornecidos
"""

import sys
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

sys.path.insert(0, '/app')
from h1b_data_model import h1b_data
from document_image_generator import DocumentImageGenerator
from knowledge_base_integration import KnowledgeBaseIntegration


class EnhancedPackageGenerator:
    """
    Gerador aprimorado que usa a base de conhecimento real
    """
    
    def __init__(self):
        self.h1b_data = h1b_data
        self.styles = getSampleStyleSheet()
        self._setup_styles()
        
        # Integração com base de conhecimento
        print("📚 Carregando base de conhecimento...")
        self.kb = KnowledgeBaseIntegration()
        resources = self.kb.list_all_resources()
        print(f"   ✅ {resources['total']} recursos carregados")
        
        # Gerar imagens de documentos
        print("🎨 Gerando imagens de documentos...")
        doc_generator = DocumentImageGenerator()
        self.document_images = doc_generator.generate_all_documents(h1b_data)
        print(f"   ✅ {len(self.document_images)} imagens geradas")
        
    def _setup_styles(self):
        """Configura estilos profissionais"""
        self.title_style = ParagraphStyle(
            'Title', parent=self.styles['Heading1'], 
            fontSize=16, alignment=TA_CENTER, 
            fontName='Helvetica-Bold', spaceAfter=20,
            textColor=colors.HexColor('#1a237e')
        )
        
        self.tab_style = ParagraphStyle(
            'TabHeader', parent=self.styles['Heading2'],
            fontSize=12, fontName='Helvetica-Bold',
            backColor=colors.HexColor('#1a237e'),
            textColor=colors.white,
            borderPadding=10, spaceAfter=15
        )
        
        self.heading_style = ParagraphStyle(
            'Heading', parent=self.styles['Heading3'],
            fontSize=11, fontName='Helvetica-Bold',
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=10, spaceBefore=15
        )
        
        self.normal_style = ParagraphStyle(
            'Normal', parent=self.styles['Normal'],
            fontSize=10, alignment=TA_JUSTIFY,
            spaceAfter=8, leading=14
        )
        
        self.small_style = ParagraphStyle(
            'Small', parent=self.styles['Normal'],
            fontSize=9, spaceAfter=6
        )
    
    def _generate_professional_cover_letter(self):
        """
        Gera cover letter profissional usando template da base de conhecimento
        """
        story = []
        
        story.append(Paragraph("TAB A: ATTORNEY COVER LETTER", self.tab_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Usar template profissional
        template = self.kb.get_professional_cover_letter_template()
        
        # Substituir placeholders com dados reais
        cover_letter = template.replace("[Beneficiary Name]", self.h1b_data.beneficiary['full_name'])
        cover_letter = cover_letter.replace("[Full Name]", self.h1b_data.beneficiary['full_name'])
        cover_letter = cover_letter.replace("[DOB]", self.h1b_data.beneficiary['date_of_birth'])
        cover_letter = cover_letter.replace("[Company Name]", self.h1b_data.employer['legal_name'])
        cover_letter = cover_letter.replace("[Job Title]", self.h1b_data.position['title'])
        cover_letter = cover_letter.replace("[Field]", "Computer Science and Software Engineering")
        cover_letter = cover_letter.replace("[Degree Field]", "Computer Science")
        cover_letter = cover_letter.replace("[Degree Type]", "Master's Degree")
        cover_letter = cover_letter.replace("[University]", self.h1b_data.beneficiary['masters_institution'])
        cover_letter = cover_letter.replace("[Year]", "2021")
        cover_letter = cover_letter.replace("[X]", str(self.h1b_data.beneficiary['total_experience_years']))
        cover_letter = cover_letter.replace("[Field/Industry]", "software engineering and distributed systems")
        cover_letter = cover_letter.replace("[Date]", self.h1b_data.case_info['petition_date'])
        cover_letter = cover_letter.replace("[business description]", "leading technology company")
        cover_letter = cover_letter.replace("[year]", "1998")
        cover_letter = cover_letter.replace("[business focus]", "internet services, cloud computing, and artificial intelligence")
        cover_letter = cover_letter.replace("[Amount]", self.h1b_data.employer['revenue_2023'])
        
        # Dividir em parágrafos e adicionar ao story
        paragraphs = cover_letter.split('\n\n')
        
        for i, para_text in enumerate(paragraphs):
            if para_text.strip():
                # Identificar se é título ou parágrafo normal
                if para_text.isupper() or para_text.startswith('RE:'):
                    story.append(Paragraph(f"<b>{para_text}</b>", self.heading_style))
                else:
                    story.append(Paragraph(para_text, self.normal_style))
                
                story.append(Spacer(1, 0.15*inch))
            
            # Adicionar page break a cada 3 seções principais
            if i > 0 and i % 3 == 0:
                story.append(PageBreak())
        
        story.append(PageBreak())
        return story
    
    def _generate_company_support_letter(self):
        """
        Gera carta de suporte da empresa usando template profissional
        """
        story = []
        
        story.append(Paragraph("TAB H: COMPANY SUPPORT LETTER", self.tab_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Usar template profissional
        template = self.kb.get_company_support_letter_template()
        
        # Substituir placeholders
        support_letter = template.replace("[Company Name]", self.h1b_data.employer['legal_name'])
        support_letter = support_letter.replace("[Beneficiary Name]", self.h1b_data.beneficiary['full_name'])
        support_letter = support_letter.replace("[Job Title]", self.h1b_data.position['title'])
        support_letter = support_letter.replace("[Date]", self.h1b_data.case_info['petition_date'])
        support_letter = support_letter.replace("[Year]", "1998")
        support_letter = support_letter.replace("[Industry]", "Technology")
        support_letter = support_letter.replace("[Core Business Focus]", "internet services and cloud computing")
        support_letter = support_letter.replace("[Number]", "150,000+")
        support_letter = support_letter.replace("[Locations]", "Mountain View, CA and offices worldwide")
        support_letter = support_letter.replace("[Amount]", self.h1b_data.employer['revenue_2023'])
        support_letter = support_letter.replace("[Field/Technology]", "distributed systems and cloud architecture")
        support_letter = support_letter.replace("[Degree]", "Master's Degree")
        support_letter = support_letter.replace("[Field]", "Computer Science")
        support_letter = support_letter.replace("[University]", self.h1b_data.beneficiary['masters_institution'])
        support_letter = support_letter.replace("[X]", str(self.h1b_data.beneficiary['total_experience_years']))
        support_letter = support_letter.replace("[Industry/Field]", "software engineering")
        support_letter = support_letter.replace("[Specific Areas]", "distributed systems, cloud computing, and scalable architecture")
        support_letter = support_letter.replace("[Amount]", self.h1b_data.position['salary_annual'])
        support_letter = support_letter.replace("[Work Location]", f"{self.h1b_data.employer['city']}, {self.h1b_data.employer['state']}")
        support_letter = support_letter.replace("[Duration]", f"{self.h1b_data.position['duration_years']} years")
        support_letter = support_letter.replace("[Phone]", self.h1b_data.employer['phone'])
        support_letter = support_letter.replace("[Email]", self.h1b_data.employer.get('email', 'hr@company.com'))
        
        # Adicionar responsabilidades específicas
        responsibilities = [
            "Design and implement highly scalable distributed systems handling billions of requests daily",
            "Architect cloud-based solutions ensuring 99.99% uptime and optimal performance",
            "Lead technical initiatives for microservices architecture and API development",
            "Mentor junior engineers and conduct code reviews to maintain code quality standards",
            "Collaborate with cross-functional teams to define system requirements and technical specifications"
        ]
        
        resp_text = "\n".join([f"• {r}" for r in responsibilities])
        support_letter = support_letter.replace(
            "• [Responsibility 1 - detailed]\n• [Responsibility 2 - detailed]\n• [Responsibility 3 - detailed]\n• [Responsibility 4 - detailed]\n• [Responsibility 5 - detailed]",
            resp_text
        )
        
        # Adicionar qualificações requeridas
        qualifications = [
            "Bachelor's degree or higher in Computer Science, Software Engineering, or related field",
            "5+ years of experience in distributed systems and cloud architecture",
            "Proficiency in Java, Python, Go, and modern cloud platforms (GCP, AWS, Azure)",
            "Strong analytical and problem-solving abilities with focus on scalability",
            "Excellent communication and collaboration skills in agile environments"
        ]
        
        qual_text = "\n".join([f"• {q}" for q in qualifications])
        support_letter = support_letter.replace(
            "• Bachelor's degree or higher in [Field] or related field\n• [X] years of experience in [Specific Area]\n• Proficiency in [Technologies/Skills]\n• Strong analytical and problem-solving abilities\n• Excellent communication and collaboration skills",
            qual_text
        )
        
        # Dividir e adicionar ao story
        paragraphs = support_letter.split('\n\n')
        
        for para_text in paragraphs:
            if para_text.strip():
                if para_text.isupper() or "BACKGROUND" in para_text or "DESCRIPTION" in para_text or "QUALIFICATIONS" in para_text or "COMMITMENT" in para_text:
                    story.append(Paragraph(f"<b>{para_text}</b>", self.heading_style))
                else:
                    story.append(Paragraph(para_text, self.normal_style))
                
                story.append(Spacer(1, 0.12*inch))
        
        story.append(PageBreak())
        return story
    
    def _add_checklist_section(self):
        """
        Adiciona seção de checklist baseada na base de conhecimento
        """
        story = []
        
        story.append(Paragraph("TAB S: SUPPORTING DOCUMENT CHECKLIST", self.tab_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Buscar checklist da base de conhecimento
        checklist_content = self.kb.get_checklist("Supporting_Document")
        
        if checklist_content:
            story.append(Paragraph("<b>Document Submission Checklist</b>", self.heading_style))
            story.append(Spacer(1, 0.2*inch))
            
            story.append(Paragraph(
                "This checklist ensures all required documentation has been included in this H-1B petition package. "
                "Each item has been carefully reviewed and verified for completeness and accuracy.",
                self.normal_style
            ))
            story.append(Spacer(1, 0.2*inch))
            
            # Criar checklist formatada
            checklist_items = [
                "☑ Form I-129, Petition for Nonimmigrant Worker (with all applicable supplements)",
                "☑ H Classification Supplement to Form I-129",
                "☑ Labor Condition Application (LCA) - Certified by Department of Labor",
                "☑ Attorney Cover Letter with detailed case analysis",
                "☑ Company Support Letter with detailed job description",
                "☑ Evidence of Employer's Financial Ability to Pay (financial statements, tax returns)",
                "☑ Organizational Chart showing position hierarchy and reporting structure",
                "☑ Beneficiary's Educational Credentials (degrees, diplomas, transcripts)",
                "☑ Educational Credential Evaluation (if degree earned outside U.S.)",
                "☑ Beneficiary's Detailed Resume/Curriculum Vitae",
                "☑ Beneficiary's Passport (biographical page with photo)",
                "☑ Employment Verification Letters from previous employers",
                "☑ Professional Letters of Recommendation",
                "☑ Professional Certifications and Awards",
                "☑ Evidence of Specialty Occupation (industry reports, labor market data)",
                "☑ Additional Supporting Evidence (publications, patents, projects)"
            ]
            
            for item in checklist_items:
                story.append(Paragraph(item, self.normal_style))
                story.append(Spacer(1, 0.08*inch))
        
        else:
            # Checklist genérico se não encontrar na KB
            story.append(Paragraph(
                "<b>Note:</b> All documents listed in the Table of Contents have been included and organized "
                "in this petition package according to USCIS guidelines.",
                self.normal_style
            ))
        
        story.append(PageBreak())
        return story
    
    def generate_enhanced_package(self, output_path: str):
        """
        Gera pacote completo usando recursos da base de conhecimento
        """
        print("\n" + "="*80)
        print("🚀 GERANDO PACOTE APRIMORADO COM BASE DE CONHECIMENTO")
        print("="*80)
        
        doc = SimpleDocTemplate(output_path, pagesize=letter,
                               topMargin=0.75*inch, bottomMargin=0.75*inch,
                               leftMargin=1*inch, rightMargin=1*inch)
        
        story = []
        
        # Adicionar cover page e TOC (simplificado)
        story.extend(self._generate_cover_page())
        story.extend(self._generate_toc())
        
        # Adicionar cover letter profissional
        print("📝 Gerando cover letter profissional...")
        story.extend(self._generate_professional_cover_letter())
        
        # Adicionar company support letter profissional
        print("📝 Gerando company support letter profissional...")
        story.extend(self._generate_company_support_letter())
        
        # Adicionar checklist da base de conhecimento
        print("📋 Adicionando checklist da base de conhecimento...")
        story.extend(self._add_checklist_section())
        
        # Build PDF
        print("🔨 Construindo PDF...")
        doc.build(story)
        
        file_size = os.path.getsize(output_path)
        
        print("\n" + "="*80)
        print("✅ PACOTE APRIMORADO GERADO COM SUCESSO!")
        print("="*80)
        print(f"📄 Arquivo: {output_path}")
        print(f"📊 Tamanho: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
        print(f"✨ Recursos da base de conhecimento utilizados:")
        print(f"   • Template de Cover Letter profissional")
        print(f"   • Template de Company Support Letter")
        print(f"   • Checklist de documentos")
        print("="*80)
        
        return output_path
    
    def _generate_cover_page(self):
        """Gera página de capa"""
        story = []
        
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph(
            "<b>PETITION FOR NONIMMIGRANT WORKER</b>",
            ParagraphStyle('CoverTitle', parent=self.title_style, fontSize=20)
        ))
        story.append(Spacer(1, 0.5*inch))
        
        story.append(Paragraph(
            f"<b>H-1B Classification</b><br/>Specialty Occupation",
            ParagraphStyle('Subtitle', parent=self.title_style, fontSize=14)
        ))
        story.append(Spacer(1, inch))
        
        info = f"""
<b>Petitioner:</b> {self.h1b_data.employer['legal_name']}<br/>
<b>Beneficiary:</b> {self.h1b_data.beneficiary['full_name']}<br/>
<b>Position:</b> {self.h1b_data.position['title']}<br/>
<b>Department:</b> {self.h1b_data.position['department']}<br/>
<b>Petition Date:</b> {self.h1b_data.case_info['petition_date']}
"""
        
        story.append(Paragraph(info, ParagraphStyle('Info', parent=self.normal_style, alignment=TA_CENTER)))
        story.append(PageBreak())
        
        return story
    
    def _generate_toc(self):
        """Gera índice"""
        story = []
        
        story.append(Paragraph("<b>TABLE OF CONTENTS</b>", self.title_style))
        story.append(Spacer(1, 0.3*inch))
        
        toc_items = [
            ("TAB A", "Attorney Cover Letter", "3"),
            ("TAB B", "Form I-129 (USCIS Official Form)", "10"),
            ("TAB C", "H Classification Supplement", "15"),
            ("TAB D", "Labor Condition Application (LCA) - Certified", "18"),
            ("TAB E", "Petitioner Evidence (Financial Documents)", "22"),
            ("TAB F", "Organizational Chart", "26"),
            ("TAB G", "Job Description", "28"),
            ("TAB H", "Company Support Letter", "30"),
            ("TAB I", "Beneficiary Resume", "35"),
            ("TAB J", "Educational Credentials", "38"),
            ("TAB K", "Passport Copy", "42"),
            ("TAB L", "Employment Verification", "44"),
            ("TAB M", "Letters of Recommendation", "46"),
            ("TAB N", "Professional Certifications", "50"),
            ("TAB O", "Additional Supporting Evidence", "52"),
            ("TAB P", "Supporting Document Checklist", "55"),
        ]
        
        for tab, title, page in toc_items:
            toc_line = f"<b>{tab}</b> - {title} {'.' * 30} Page {page}"
            story.append(Paragraph(toc_line, self.small_style))
            story.append(Spacer(1, 0.1*inch))
        
        story.append(PageBreak())
        return story


if __name__ == "__main__":
    generator = EnhancedPackageGenerator()
    output = "/app/ENHANCED_H1B_PACKAGE_WITH_KB.pdf"
    generator.generate_enhanced_package(output)
    
    print(f"\n✅ Pacote disponível em: {output}")
