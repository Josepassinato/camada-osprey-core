"""
Sistema de Geração de Pacote Final para USCIS
Gera todos os documentos necessários para envio
"""

import os
from datetime import datetime
from typing import Dict, List, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import zipfile
import io

class USCISPackageGenerator:
    """Gera pacote completo para envio ao USCIS"""
    
    def __init__(self, case_data: Dict):
        self.case_data = case_data
        self.case_id = case_data.get('case_id', 'UNKNOWN')
        self.form_code = case_data.get('form_code', 'I-539')
        self.basic_data = case_data.get('basic_data', {})
        self.user_story = case_data.get('user_story', {})
        
    def generate_official_form_pdf(self) -> bytes:
        """Gera o formulário oficial USCIS preenchido"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, 
                               topMargin=0.75*inch, bottomMargin=0.75*inch,
                               leftMargin=0.75*inch, rightMargin=0.75*inch)
        
        story = []
        styles = getSampleStyleSheet()
        
        # Criar estilos customizados
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#000000'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#000000'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        field_style = ParagraphStyle(
            'FieldStyle',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            fontName='Helvetica'
        )
        
        # Cabeçalho
        story.append(Paragraph(f"U.S. DEPARTMENT OF HOMELAND SECURITY", title_style))
        story.append(Paragraph(f"U.S. CITIZENSHIP AND IMMIGRATION SERVICES", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Título do formulário
        form_titles = {
            'I-539': 'APPLICATION TO EXTEND/CHANGE NONIMMIGRANT STATUS',
            'F-1': 'APPLICATION TO CHANGE NONIMMIGRANT STATUS TO F-1 STUDENT',
            'I-130': 'PETITION FOR ALIEN RELATIVE',
            'I-765': 'APPLICATION FOR EMPLOYMENT AUTHORIZATION',
            'I-90': 'APPLICATION TO REPLACE PERMANENT RESIDENT CARD',
            'EB-2 NIW': 'IMMIGRANT PETITION FOR ALIEN WORKER',
            'EB-1A': 'IMMIGRANT PETITION FOR ALIEN WORKER'
        }
        
        story.append(Paragraph(f"FORM {self.form_code}", title_style))
        story.append(Paragraph(form_titles.get(self.form_code, 'APPLICATION FORM'), styles['Normal']))
        story.append(Paragraph(f"OMB No. 1615-0003", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # PARTE 1: Informações sobre o Requerente
        story.append(Paragraph("PART 1: INFORMATION ABOUT YOU", heading_style))
        
        applicant_data = [
            ['Field', 'Information'],
            ['1. Family Name (Last Name)', self.basic_data.get('lastName', '')],
            ['2. Given Name (First Name)', self.basic_data.get('firstName', '')],
            ['3. Middle Name', self.basic_data.get('middleName', '')],
            ['4. Date of Birth (mm/dd/yyyy)', self.basic_data.get('dateOfBirth', '')],
            ['5. Country of Birth', self.basic_data.get('countryOfBirth', '')],
            ['6. Gender', self.basic_data.get('gender', '')],
            ['7. Current Mailing Address', self.basic_data.get('currentAddress', '')],
            ['   City', self.basic_data.get('city', '')],
            ['   State', self.basic_data.get('state', '')],
            ['   ZIP Code', self.basic_data.get('zipCode', '')],
            ['8. Daytime Phone Number', self.basic_data.get('phoneNumber', '')],
            ['9. Email Address', self.basic_data.get('email', '')],
        ]
        
        table = Table(applicant_data, colWidths=[3*inch, 3.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.3*inch))
        
        # PARTE 2: Informações sobre Status Atual
        story.append(Paragraph("PART 2: INFORMATION ABOUT YOUR CURRENT STATUS", heading_style))
        
        status_data = [
            ['Field', 'Information'],
            ['10. Current Nonimmigrant Status', self.basic_data.get('currentStatus', '')],
            ['11. Date Status Expires (mm/dd/yyyy)', self.basic_data.get('statusExpiration', '')],
            ['12. I-94 Arrival/Departure Record Number', self.basic_data.get('i94Number', '')],
            ['13. A-Number (if any)', self.basic_data.get('alienNumber', 'N/A')],
        ]
        
        table2 = Table(status_data, colWidths=[3*inch, 3.5*inch])
        table2.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ]))
        
        story.append(table2)
        story.append(PageBreak())
        
        # PARTE 3: Informações sobre a Solicitação
        story.append(Paragraph("PART 3: APPLICATION TYPE AND REASON", heading_style))
        
        reason = self.user_story.get('reasonForExtension', self.user_story.get('user_story', ''))
        
        story.append(Paragraph(f"<b>Reason for Application:</b>", field_style))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph(reason, field_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Rodapé
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(f"Form prepared on: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
        story.append(Paragraph(f"Case ID: {self.case_id}", styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_cover_letter(self) -> bytes:
        """Gera carta de apresentação"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                               topMargin=1*inch, bottomMargin=1*inch,
                               leftMargin=1*inch, rightMargin=1*inch)
        
        story = []
        styles = getSampleStyleSheet()
        
        # Estilo para carta
        letter_style = ParagraphStyle(
            'LetterStyle',
            parent=styles['Normal'],
            fontSize=11,
            leading=16,
            alignment=TA_JUSTIFY
        )
        
        # Cabeçalho
        name = f"{self.basic_data.get('firstName', '')} {self.basic_data.get('lastName', '')}"
        address = self.basic_data.get('currentAddress', '')
        city_state_zip = f"{self.basic_data.get('city', '')}, {self.basic_data.get('state', '')} {self.basic_data.get('zipCode', '')}"
        
        story.append(Paragraph(name, styles['Normal']))
        story.append(Paragraph(address, styles['Normal']))
        story.append(Paragraph(city_state_zip, styles['Normal']))
        story.append(Paragraph(self.basic_data.get('email', ''), styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph(datetime.now().strftime('%B %d, %Y'), styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph("U.S. Citizenship and Immigration Services", styles['Normal']))
        story.append(Paragraph("Attn: I-539 Processing", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph(f"<b>Re: Application for Extension/Change of Status - Form {self.form_code}</b>", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph("Dear Sir/Madam:", letter_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Corpo da carta
        intro = f"I am writing to submit my application for {'extension' if self.form_code == 'I-539' else 'change'} of nonimmigrant status. "
        intro += f"I am currently in the United States in {self.basic_data.get('currentStatus', '')} status, which expires on {self.basic_data.get('statusExpiration', '')}."
        
        story.append(Paragraph(intro, letter_style))
        story.append(Spacer(1, 0.15*inch))
        
        reason = self.user_story.get('reasonForExtension', self.user_story.get('user_story', 'I respectfully request this change of status to pursue my goals in the United States.'))
        story.append(Paragraph(reason, letter_style))
        story.append(Spacer(1, 0.15*inch))
        
        closing = "I have enclosed all required documentation and fees. I respectfully request that you approve this application. "
        closing += "Should you need any additional information, please do not hesitate to contact me."
        
        story.append(Paragraph(closing, letter_style))
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph("Respectfully submitted,", letter_style))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph("_________________________", styles['Normal']))
        story.append(Paragraph(name, styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_document_checklist(self) -> bytes:
        """Gera checklist de documentos"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                               topMargin=0.75*inch, bottomMargin=0.75*inch,
                               leftMargin=0.75*inch, rightMargin=0.75*inch)
        
        story = []
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'ChecklistTitle',
            parent=styles['Heading1'],
            fontSize=14,
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        story.append(Paragraph(f"DOCUMENT CHECKLIST - FORM {self.form_code}", title_style))
        story.append(Paragraph(f"Case ID: {self.case_id}", styles['Normal']))
        story.append(Paragraph(f"Applicant: {self.basic_data.get('firstName', '')} {self.basic_data.get('lastName', '')}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Lista de documentos requeridos
        required_docs = [
            ['☐', 'Form ' + self.form_code + ' (completed and signed)', '✓'],
            ['☐', 'Cover Letter', '✓'],
            ['☐', 'Copy of Passport (biographical page)', 'Required'],
            ['☐', 'Copy of current I-94 Arrival/Departure Record', 'Required'],
            ['☐', 'Copy of current visa stamp', 'Required'],
            ['☐', 'Evidence of financial support', 'Required'],
            ['☐', 'Filing fee payment receipt', 'Required'],
        ]
        
        if self.form_code == 'F-1':
            required_docs.extend([
                ['☐', 'Form I-20 from educational institution', 'Required'],
                ['☐', 'Proof of SEVIS fee payment', 'Required'],
                ['☐', 'Academic transcripts', 'Required'],
            ])
        
        table = Table(required_docs, colWidths=[0.5*inch, 4.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph("<b>IMPORTANT NOTES:</b>", styles['Heading3']))
        story.append(Paragraph("• Review all documents before mailing", styles['Normal']))
        story.append(Paragraph("• Make copies of everything for your records", styles['Normal']))
        story.append(Paragraph("• Use certified mail with tracking", styles['Normal']))
        story.append(Paragraph(f"• Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_index_page(self) -> bytes:
        """Gera página de índice/sumário do pacote"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                               topMargin=0.75*inch, bottomMargin=0.75*inch,
                               leftMargin=0.75*inch, rightMargin=0.75*inch)
        
        story = []
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'IndexTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#000066')
        )
        
        story.append(Paragraph("USCIS APPLICATION PACKAGE", title_style))
        story.append(Paragraph(f"FORM {self.form_code} - COMPLETE SUBMISSION", styles['Heading2']))
        story.append(Spacer(1, 0.3*inch))
        
        # Informações do caso
        story.append(Paragraph(f"<b>Applicant:</b> {self.basic_data.get('firstName', '')} {self.basic_data.get('lastName', '')}", styles['Normal']))
        story.append(Paragraph(f"<b>Case ID:</b> {self.case_id}", styles['Normal']))
        story.append(Paragraph(f"<b>Date Prepared:</b> {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
        story.append(Spacer(1, 0.4*inch))
        
        story.append(Paragraph("<b>PACKAGE CONTENTS:</b>", styles['Heading2']))
        story.append(Spacer(1, 0.2*inch))
        
        # Índice de documentos
        index_data = [
            ['Section', 'Document', 'Description'],
            ['', '', ''],
            ['SECTION 1', 'Cover Letter', 'Introduction and summary of application'],
            ['', 'Form ' + self.form_code, 'Official USCIS application form (completed in English)'],
            ['', '', ''],
            ['SECTION 2', 'Supporting Documents', 'All required evidence and documentation'],
            ['', '• Passport Copy', 'Biographical page showing identity'],
            ['', '• I-94 Record', 'Proof of legal entry to United States'],
            ['', '• Additional Documents', 'All uploaded supporting evidence'],
            ['', '', ''],
            ['SECTION 3', 'Administrative', 'Checklists and instructions'],
            ['', 'Document Checklist', 'Complete list of all included documents'],
            ['', 'Mailing Instructions', 'How to submit this package to USCIS'],
        ]
        
        table = Table(index_data, colWidths=[1.3*inch, 2.2*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#000066')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 2), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 2), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 2), (-1, -1), 6),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.4*inch))
        
        # Instruções importantes
        story.append(Paragraph("<b>IMPORTANT INSTRUCTIONS:</b>", styles['Heading3']))
        story.append(Paragraph("1. Review ALL documents carefully before mailing", styles['Normal']))
        story.append(Paragraph("2. Sign Form " + self.form_code + " where indicated", styles['Normal']))
        story.append(Paragraph("3. Make complete copies of everything for your records", styles['Normal']))
        story.append(Paragraph("4. Follow the mailing instructions in Section 3", styles['Normal']))
        story.append(Paragraph("5. Use certified mail with tracking number", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph("<i>This package was prepared using Osprey Immigration Platform. All documents are organized in the proper order for USCIS submission.</i>", styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_section_separator(self, section_number: int, section_title: str, description: str) -> bytes:
        """Gera página separadora entre seções"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        
        story = []
        styles = getSampleStyleSheet()
        
        story.append(Spacer(1, 2*inch))
        
        title_style = ParagraphStyle(
            'SectionTitle',
            parent=styles['Heading1'],
            fontSize=24,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#000066'),
            spaceAfter=20
        )
        
        story.append(Paragraph(f"SECTION {section_number}", title_style))
        story.append(Paragraph(section_title, styles['Heading2']))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(description, styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_complete_package(self) -> bytes:
        """Gera pacote ZIP com TODOS os documentos organizados como advogados fazem"""
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            
            # ============ ÍNDICE ============
            index_page = self.generate_index_page()
            zip_file.writestr("00_INDEX_Package_Contents.pdf", index_page)
            
            # ============ SECTION 1: APPLICATION FORMS ============
            section1 = self.generate_section_separator(1, "APPLICATION FORMS", 
                "This section contains the cover letter and official USCIS application form")
            zip_file.writestr("Section_1_APPLICATION_FORMS/00_Section_Separator.pdf", section1)
            
            # 1. Carta de apresentação
            cover_letter = self.generate_cover_letter()
            zip_file.writestr("Section_1_APPLICATION_FORMS/01_Cover_Letter.pdf", cover_letter)
            
            # 2. Formulário oficial USCIS preenchido pela IA
            official_form = self.generate_official_form_pdf()
            zip_file.writestr(f"Section_1_APPLICATION_FORMS/02_Form_{self.form_code}_COMPLETED.pdf", official_form)
            
            # ============ SECTION 2: SUPPORTING DOCUMENTS ============
            section2 = self.generate_section_separator(2, "SUPPORTING DOCUMENTS", 
                "This section contains all required supporting documentation and evidence")
            zip_file.writestr("Section_2_SUPPORTING_DOCUMENTS/00_Section_Separator.pdf", section2)
            
            # Adicionar documentos do usuário (se existirem)
            documents = self.case_data.get('documents', [])
            doc_counter = 1
            
            # Documentos padrão que sempre devem ser incluídos (placeholder se não houver upload)
            required_docs = [
                ('Passport_Biographical_Page', 'Copy of passport biographical page'),
                ('I94_Arrival_Departure_Record', 'Copy of I-94 Arrival/Departure Record'),
                ('Current_Visa', 'Copy of current visa stamp'),
                ('Financial_Evidence', 'Evidence of financial support'),
            ]
            
            for doc_name, doc_description in required_docs:
                # Verificar se usuário fez upload deste documento
                user_doc = next((d for d in documents if doc_name.lower() in d.get('name', '').lower()), None)
                
                if user_doc and 'file_data' in user_doc:
                    # Incluir documento real do usuário
                    zip_file.writestr(
                        f"Section_2_SUPPORTING_DOCUMENTS/{doc_counter:02d}_{doc_name}.pdf",
                        user_doc['file_data']
                    )
                else:
                    # Criar placeholder indicando que documento deve ser anexado
                    placeholder = self.generate_document_placeholder(doc_name, doc_description)
                    zip_file.writestr(
                        f"Section_2_SUPPORTING_DOCUMENTS/{doc_counter:02d}_{doc_name}_PLACEHOLDER.pdf",
                        placeholder
                    )
                
                doc_counter += 1
            
            # Adicionar outros documentos que o usuário fez upload
            other_docs = [d for d in documents if not any(req[0].lower() in d.get('name', '').lower() for req in required_docs)]
            for doc in other_docs:
                if 'file_data' in doc:
                    filename = doc.get('name', f'Additional_Document_{doc_counter}')
                    zip_file.writestr(
                        f"Section_2_SUPPORTING_DOCUMENTS/{doc_counter:02d}_{filename}",
                        doc['file_data']
                    )
                    doc_counter += 1
            
            # ============ SECTION 3: ADMINISTRATIVE ============
            section3 = self.generate_section_separator(3, "ADMINISTRATIVE", 
                "This section contains checklists and mailing instructions")
            zip_file.writestr("Section_3_ADMINISTRATIVE/00_Section_Separator.pdf", section3)
            
            # 1. Document Checklist
            checklist = self.generate_document_checklist()
            zip_file.writestr("Section_3_ADMINISTRATIVE/01_Document_Checklist.pdf", checklist)
            
            # 2. Instruções de envio
            instructions = self.generate_mailing_instructions()
            zip_file.writestr("Section_3_ADMINISTRATIVE/02_Mailing_Instructions.txt", instructions.encode('utf-8'))
            
            # 3. Adicionar README
            readme = self.generate_readme()
            zip_file.writestr("README_FIRST.txt", readme.encode('utf-8'))
        
        zip_buffer.seek(0)
        return zip_buffer.getvalue()
    
    def generate_document_placeholder(self, doc_name: str, description: str) -> bytes:
        """Gera placeholder PDF para documentos não enviados"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        
        story = []
        styles = getSampleStyleSheet()
        
        story.append(Spacer(1, 2*inch))
        
        warning_style = ParagraphStyle(
            'Warning',
            parent=styles['Heading1'],
            fontSize=16,
            alignment=TA_CENTER,
            textColor=colors.red,
            spaceAfter=30
        )
        
        story.append(Paragraph("⚠️ DOCUMENT REQUIRED", warning_style))
        story.append(Paragraph(f"<b>{doc_name.replace('_', ' ')}</b>", styles['Heading2']))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(description, styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph("<b>ACTION REQUIRED:</b>", styles['Heading3']))
        story.append(Paragraph("Please insert this document here before mailing your application to USCIS.", styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_readme(self) -> str:
        """Gera arquivo README"""
        return f"""
================================================================================
                        USCIS APPLICATION PACKAGE
                            FORM {self.form_code}
================================================================================

Applicant: {self.basic_data.get('firstName', '')} {self.basic_data.get('lastName', '')}
Case ID: {self.case_id}
Date Prepared: {datetime.now().strftime('%B %d, %Y')}

================================================================================
                            QUICK START GUIDE
================================================================================

📋 STEP 1: REVIEW THE INDEX
   Open: 00_INDEX_Package_Contents.pdf
   This shows you everything included in this package

📝 STEP 2: REVIEW AND SIGN FORMS
   Go to: Section_1_APPLICATION_FORMS/
   • Read the cover letter
   • Review Form {self.form_code} (already filled out in English by AI)
   • Sign Form {self.form_code} where indicated
   • Date the signature

📎 STEP 3: CHECK SUPPORTING DOCUMENTS
   Go to: Section_2_SUPPORTING_DOCUMENTS/
   • Review all included documents
   • If you see any PLACEHOLDER files, replace them with the actual documents
   • Make sure all copies are clear and legible

✅ STEP 4: USE THE CHECKLIST
   Go to: Section_3_ADMINISTRATIVE/
   • Open the Document Checklist
   • Check off each item as you verify it
   • Make sure nothing is missing

📮 STEP 5: MAIL YOUR APPLICATION
   • Follow instructions in: Section_3_ADMINISTRATIVE/02_Mailing_Instructions.txt
   • Use certified mail with tracking
   • Keep copies of EVERYTHING

================================================================================
                        PACKAGE ORGANIZATION
================================================================================

This package is organized exactly as immigration attorneys prepare submissions:

📁 Section 1: APPLICATION FORMS
   ├── Cover Letter
   └── Official USCIS Form (completed in English)

📁 Section 2: SUPPORTING DOCUMENTS  
   ├── Passport Copy
   ├── I-94 Record
   ├── Visa Copy
   ├── Financial Evidence
   └── Additional Documents

📁 Section 3: ADMINISTRATIVE
   ├── Document Checklist
   └── Mailing Instructions

================================================================================
                        IMPORTANT NOTES
================================================================================

✓ All forms are pre-filled in English by our AI system
✓ Documents are organized in the order USCIS expects
✓ Simply print, sign, and mail - no additional formatting needed
✓ Keep complete copies of everything you mail

⚠️ This is NOT legal advice. For complex cases, consult an immigration attorney.

================================================================================
                        NEED HELP?
================================================================================

Questions? Contact:
• USCIS: 1-800-375-5283
• Case Status: https://egov.uscis.gov/casestatus/

================================================================================

Good luck with your application!
Prepared by Osprey Immigration Platform
"""
    
    def generate_mailing_instructions(self) -> str:
        """Gera instruções de envio"""
        instructions = f"""
================================================================================
MAILING INSTRUCTIONS - FORM {self.form_code}
================================================================================

Case ID: {self.case_id}
Applicant: {self.basic_data.get('firstName', '')} {self.basic_data.get('lastName', '')}
Date Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

================================================================================
STEP 1: REVIEW ALL DOCUMENTS
================================================================================
□ Form {self.form_code} - Official application form (completed and signed)
□ Cover Letter - Introducing your application
□ Document Checklist - List of all required documents
□ Supporting Documents - All documents listed in the checklist

================================================================================
STEP 2: ORGANIZE YOUR PACKAGE
================================================================================
1. Place cover letter on top
2. Add Form {self.form_code} (signed)
3. Add document checklist
4. Add all supporting documents in order listed
5. Use paper clips (NO staples)
6. Place everything in a large envelope

================================================================================
STEP 3: MAILING ADDRESS
================================================================================
Send your package to:

USCIS
P.O. Box 7219
Chicago, IL 60680-7219

For Express Mail/Courier:
USCIS
Attn: I-539
131 South Dearborn - 3rd Floor
Chicago, IL 60603-5517

================================================================================
STEP 4: SEND YOUR PACKAGE
================================================================================
□ Use USPS Certified Mail with Return Receipt
□ OR use FedEx/UPS with tracking
□ Keep tracking number for your records
□ Keep copies of EVERYTHING you send

================================================================================
IMPORTANT NOTES
================================================================================
• Filing Fee: Check current USCIS website for exact amount
• Processing Time: Typically 4-6 months (check USCIS website for updates)
• Keep your receipt notice (I-797) when you receive it
• Do NOT leave the United States while application is pending

================================================================================
NEXT STEPS AFTER MAILING
================================================================================
1. You will receive a receipt notice (Form I-797C) within 2-4 weeks
2. Save the receipt number - you can use it to check status online
3. Check status at: https://egov.uscis.gov/casestatus/landing.do
4. If USCIS needs more documents, they will send a Request for Evidence (RFE)
5. Respond to any RFEs within the deadline given

================================================================================
NEED HELP?
================================================================================
• USCIS Contact Center: 1-800-375-5283
• USCIS Website: www.uscis.gov
• Case Status: https://egov.uscis.gov/casestatus/

================================================================================
DISCLAIMER
================================================================================
This package was generated by Osprey Immigration Platform as an aid to help
you prepare your application. This is not legal advice. For complex cases or
if you have questions, please consult with an immigration attorney.

Good luck with your application!
================================================================================
"""
        return instructions


def generate_final_package(case_data: Dict) -> bytes:
    """
    Função principal para gerar pacote final
    """
    generator = USCISPackageGenerator(case_data)
    return generator.generate_complete_package()
