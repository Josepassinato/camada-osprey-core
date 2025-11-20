#!/usr/bin/env python3
"""
Gerador de Pacote Completo de Extensão de Visto B-2
Gera um pacote profissional pronto para submissão ao USCIS
Baseado no formato do pacote H-1B de sucesso
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, 
    KeepTogether, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from PyPDF2 import PdfWriter, PdfReader
from datetime import datetime
from pathlib import Path
import io

# Importar dados do caso B-2
from b2_extension_data_model import b2_extension_case as b2_extension_data

# Importar repositório de formulários
from official_forms_repository import OfficialFormsRepository


class B2ExtensionPackageGenerator:
    """Gera pacote completo de extensão de visto B-2"""
    
    def __init__(self, output_dir="/app/frontend/public"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.data = b2_extension_data
        self.forms_repo = OfficialFormsRepository()
        
        # Criar diretórios para documentos simulados
        self.docs_dir = Path("/app/simulated_b2_documents")
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        
        # Estilos
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Cria estilos customizados"""
        # Título principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtítulo
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#283593'),
            spaceAfter=12,
            fontName='Helvetica-Bold'
        ))
        
        # Seção
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold',
            borderPadding=5,
            backColor=colors.HexColor('#e8eaf6')
        ))
        
        # Corpo justificado
        self.styles.add(ParagraphStyle(
            name='JustifiedBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=10
        ))
    
    def generate_complete_package(self):
        """Gera o pacote completo"""
        print("\n" + "="*80)
        print("GERANDO PACOTE COMPLETO DE EXTENSÃO DE VISTO B-2")
        print("="*80)
        
        # Nome do arquivo final
        output_filename = "MARIA_HELENA_B2_EXTENSION_COMPLETE_PACKAGE.pdf"
        output_path = self.output_dir / output_filename
        
        # Criar PDF
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        # Lista de elementos
        story = []
        
        # 1. COVER PAGE
        print("\n1. Gerando Cover Page...")
        story.extend(self._create_cover_page())
        story.append(PageBreak())
        
        # 2. TABLE OF CONTENTS
        print("2. Gerando Table of Contents...")
        story.extend(self._create_table_of_contents())
        story.append(PageBreak())
        
        # 3. TAB A - COVER LETTER
        print("3. Gerando Cover Letter...")
        story.extend(self._create_cover_letter())
        story.append(PageBreak())
        
        # 4. TAB B - PERSONAL STATEMENT
        print("4. Gerando Personal Statement...")
        story.extend(self._create_personal_statement())
        story.append(PageBreak())
        
        # 5. TAB C - MEDICAL DOCUMENTATION
        print("5. Gerando Medical Documentation...")
        story.extend(self._create_medical_documentation())
        story.append(PageBreak())
        
        # 6. TAB D - FINANCIAL EVIDENCE
        print("6. Gerando Financial Evidence...")
        story.extend(self._create_financial_evidence())
        story.append(PageBreak())
        
        # 7. TAB E - TIES TO BRAZIL
        print("7. Gerando Ties to Brazil Evidence...")
        story.extend(self._create_ties_to_brazil())
        story.append(PageBreak())
        
        # 8. TAB F - TRAVEL HISTORY
        print("8. Gerando Travel History...")
        story.extend(self._create_travel_history())
        story.append(PageBreak())
        
        # 9. TAB G - SUPPORTING LETTERS
        print("9. Gerando Supporting Letters...")
        story.extend(self._create_supporting_letters())
        story.append(PageBreak())
        
        # 10. TAB H - PASSPORT & I-94
        print("10. Gerando Passport & I-94 Documents...")
        story.extend(self._create_passport_i94())
        story.append(PageBreak())
        
        # 11. TAB I - DOCUMENT CHECKLIST
        print("11. Gerando Document Checklist...")
        story.extend(self._create_document_checklist())
        
        # Construir PDF
        print("\n12. Construindo PDF final...")
        doc.build(story)
        
        # Verificar arquivo gerado
        if output_path.exists():
            file_size = output_path.stat().st_size
            print(f"\n✅ PACOTE GERADO COM SUCESSO!")
            print(f"   📁 Arquivo: {output_filename}")
            print(f"   📊 Tamanho: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            print(f"   📍 Localização: {output_path}")
            print(f"\n🌐 Acesse em: /api/b2-extension-demo")
            return str(output_path)
        else:
            print("\n❌ ERRO: Arquivo não foi gerado")
            return None
    
    def _create_cover_page(self):
        """Cria a página de capa"""
        elements = []
        
        # Título principal
        elements.append(Spacer(1, 1.5*inch))
        
        title = Paragraph(
            "APPLICATION TO EXTEND<br/>NONIMMIGRANT STATUS",
            self.styles['CustomTitle']
        )
        elements.append(title)
        elements.append(Spacer(1, 0.3*inch))
        
        subtitle = Paragraph(
            "Form I-539<br/>B-2 Tourist Visa Extension",
            ParagraphStyle(
                name='CoverSubtitle',
                parent=self.styles['Normal'],
                fontSize=16,
                textColor=colors.HexColor('#283593'),
                alignment=TA_CENTER,
                fontName='Helvetica'
            )
        )
        elements.append(subtitle)
        elements.append(Spacer(1, 0.5*inch))
        
        # Informações do aplicante
        info_style = ParagraphStyle(
            name='CoverInfo',
            parent=self.styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER,
            spaceAfter=8
        )
        
        elements.append(Paragraph(
            f"<b>Applicant:</b> {self.data.applicant['full_name']}",
            info_style
        ))
        elements.append(Paragraph(
            f"<b>Passport Number:</b> {self.data.applicant['passport_number']}",
            info_style
        ))
        elements.append(Paragraph(
            f"<b>Current Status:</b> {self.data.current_status['visa_type']}",
            info_style
        ))
        elements.append(Paragraph(
            f"<b>Current Status Expires:</b> {self.data.current_status['current_status_expires']}",
            info_style
        ))
        elements.append(Paragraph(
            f"<b>Extension Requested Until:</b> {self.data.extension_request['requested_extension_until']}",
            info_style
        ))
        
        elements.append(Spacer(1, 0.5*inch))
        
        # Razão principal
        reason_box = Table(
            [[Paragraph(
                f"<b>PRIMARY REASON:</b><br/>{self.data.extension_request['primary_reason']}",
                ParagraphStyle(
                    name='ReasonBox',
                    parent=self.styles['Normal'],
                    fontSize=11,
                    alignment=TA_CENTER,
                    textColor=colors.HexColor('#1a237e')
                )
            )]],
            colWidths=[5.5*inch]
        )
        reason_box.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e8eaf6')),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#1a237e')),
            ('PADDING', (0, 0), (-1, -1), 15),
        ]))
        elements.append(reason_box)
        
        elements.append(Spacer(1, 0.5*inch))
        
        # Data de aplicação
        elements.append(Paragraph(
            f"<b>Application Date:</b> {self.data.case_info['application_date']}",
            info_style
        ))
        
        return elements
    
    def _create_table_of_contents(self):
        """Cria o índice"""
        elements = []
        
        elements.append(Paragraph("TABLE OF CONTENTS", self.styles['CustomTitle']))
        elements.append(Spacer(1, 0.3*inch))
        
        toc_data = [
            ["TAB", "DOCUMENT", "PAGE"],
            ["A", "Cover Letter & Application Overview", "4"],
            ["B", "Personal Statement - Detailed Explanation", "7"],
            ["C", "Medical Documentation (Sister's Condition)", "10"],
            ["D", "Financial Evidence & Support Documentation", "13"],
            ["E", "Evidence of Strong Ties to Brazil", "17"],
            ["F", "Travel History & Compliance Record", "21"],
            ["G", "Supporting Letters (Family & Medical)", "24"],
            ["H", "Passport Copy & I-94 Record", "28"],
            ["I", "Supporting Document Checklist", "31"],
            ["", "Form I-539 (Official USCIS Form)", "33"],
        ]
        
        toc_table = Table(toc_data, colWidths=[0.6*inch, 4.5*inch, 0.8*inch])
        toc_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('PADDING', (0, 1), (-1, -1), 8),
        ]))
        
        elements.append(toc_table)
        
        return elements
    
    def _create_cover_letter(self):
        """Cria a cover letter"""
        elements = []
        
        # Cabeçalho TAB A
        tab_header = Paragraph("TAB A - COVER LETTER & APPLICATION OVERVIEW", self.styles['SectionHeader'])
        elements.append(tab_header)
        elements.append(Spacer(1, 0.2*inch))
        
        # Data e endereço
        date_style = ParagraphStyle(name='DateStyle', parent=self.styles['Normal'], fontSize=11, spaceAfter=10)
        elements.append(Paragraph(self.data.case_info['application_date'], date_style))
        elements.append(Spacer(1, 0.15*inch))
        
        address = """
U.S. Citizenship and Immigration Services<br/>
California Service Center<br/>
P.O. Box 10539<br/>
Laguna Niguel, CA 92607-1053
        """
        elements.append(Paragraph(address, date_style))
        elements.append(Spacer(1, 0.15*inch))
        
        # RE:
        re_text = f"""
<b>RE: Form I-539 - Application to Extend/Change Nonimmigrant Status</b><br/>
<b>Applicant:</b> {self.data.applicant['full_name']}<br/>
<b>Date of Birth:</b> {self.data.applicant['dob']}<br/>
<b>Passport Number:</b> {self.data.applicant['passport_number']}<br/>
<b>Current Status:</b> {self.data.applicant['current_status']}<br/>
<b>I-94 Number:</b> {self.data.applicant['current_i94_number']}
        """
        elements.append(Paragraph(re_text, date_style))
        elements.append(Spacer(1, 0.15*inch))
        
        # Saudação
        elements.append(Paragraph("Dear USCIS Officer:", self.styles['Normal']))
        elements.append(Spacer(1, 0.15*inch))
        
        # INTRODUÇÃO
        elements.append(Paragraph("<b>INTRODUCTION</b>", self.styles['CustomSubtitle']))
        intro_text = f"""
I, {self.data.applicant['full_name']}, a citizen of Brazil, respectfully submit this Form I-539 
application to extend my nonimmigrant B-2 visitor status. I entered the United States on 
{self.data.applicant['date_of_last_arrival']} with authorization to remain until 
{self.data.applicant['current_status_expires']}.
        """
        elements.append(Paragraph(intro_text, self.styles['JustifiedBody']))
        
        # PURPOSE OF EXTENSION
        elements.append(Paragraph("<b>PURPOSE OF EXTENSION</b>", self.styles['CustomSubtitle']))
        purpose_text = f"""
I am requesting an extension of my B-2 status until {self.extension_request['requested_extension_until']} 
due to an unforeseen family emergency that arose after my arrival in the United States. My sister, 
Patricia Costa Thompson, a U.S. Permanent Resident, was diagnosed with Stage 3 ovarian cancer in 
February 2025 and requires my ongoing support during her intensive chemotherapy treatment.
        """
        elements.append(Paragraph(purpose_text, self.styles['JustifiedBody']))
        
        # DETAILED CIRCUMSTANCES
        elements.append(Paragraph("<b>DETAILED CIRCUMSTANCES</b>", self.styles['CustomSubtitle']))
        circumstances_text = """
Upon my arrival in January 2025, my original intention was to visit family and engage in tourism 
activities in Florida. However, shortly after my arrival, my sister received her cancer diagnosis, 
which required immediate surgery and a subsequent six-month chemotherapy protocol at Jackson Memorial 
Hospital in Miami.
<br/><br/>
As her only sibling and closest family member in the United States, I have been providing essential 
daily care, including:
<br/>
• Transportation to and from medical appointments and chemotherapy sessions<br/>
• Assistance with daily activities and household management<br/>
• Support with childcare for her two young children (ages 8 and 11)<br/>
• Coordination with medical providers and insurance companies<br/>
• Emotional support during this critical treatment period
        """
        elements.append(Paragraph(circumstances_text, self.styles['JustifiedBody']))
        
        # STRONG TIES TO BRAZIL
        elements.append(Paragraph("<b>STRONG TIES TO BRAZIL</b>", self.styles['CustomSubtitle']))
        ties_text = """
I maintain extremely strong ties to Brazil that ensure my timely return:
<br/><br/>
<b>1. Family Ties:</b> My husband, Carlos Eduardo Costa, and our two children (ages 23 and 19) 
reside in Belo Horizonte and are awaiting my return.
<br/><br/>
<b>2. Business Ownership:</b> I am the Managing Partner of Costa & Associados Consultoria Ltda., 
a business consulting firm I founded 20 years ago. The company employs 12 people and requires 
my direct management.
<br/><br/>
<b>3. Property Ownership:</b> I own two significant properties in Brazil worth approximately 
$750,000 USD: our family home and a commercial office building.
<br/><br/>
<b>4. Financial Ties:</b> I maintain bank accounts totaling over $260,000 USD and an investment 
portfolio worth $250,000 USD in Brazilian financial institutions.
<br/><br/>
<b>5. Professional License:</b> I hold an active CPA license (CRC/MG) in Brazil and maintain 
professional memberships in business organizations.
        """
        elements.append(Paragraph(ties_text, self.styles['JustifiedBody']))
        
        # FINANCIAL ABILITY
        elements.append(Paragraph("<b>FINANCIAL ABILITY TO SUPPORT EXTENDED STAY</b>", self.styles['CustomSubtitle']))
        financial_text = f"""
I am entirely self-funded and possess substantial financial resources to support my extended stay 
without seeking employment in the United States. My total assets exceed ${self.data.applicant['total_assets_usd']}, including:
<br/><br/>
• Bank accounts: ${self.data.applicant['bank_balance_usd']} in checking<br/>
• Savings: ${self.data.applicant['savings_account_balance_usd']}<br/>
• Investment portfolio: ${self.data.applicant['investment_portfolio_usd']}<br/>
• Ongoing business income: $4,200/month (remote consulting work)<br/>
• Rental income: $2,800/month from commercial property
<br/><br/>
My estimated monthly expenses during the extension period are approximately $3,500, which I can 
easily sustain from my existing assets and ongoing income sources.
        """
        elements.append(Paragraph(financial_text, self.styles['JustifiedBody']))
        
        # COMPLIANCE HISTORY
        elements.append(Paragraph("<b>IMMIGRATION COMPLIANCE HISTORY</b>", self.styles['CustomSubtitle']))
        compliance_text = """
I have a perfect record of immigration compliance with the United States:
<br/><br/>
• Two previous visits to the United States (2022 and 2023)<br/>
• All previous visits were for legitimate tourism purposes<br/>
• I departed on time after each visit (14 days each)<br/>
• No overstays, violations, or immigration issues<br/>
• Valid Brazilian passport (expires 2031)<br/>
• Multiple-entry B-2 visa valid until 2034
        """
        elements.append(Paragraph(compliance_text, self.styles['JustifiedBody']))
        
        # RETURN DATE
        elements.append(Paragraph("<b>CONFIRMED RETURN TO BRAZIL</b>", self.styles['CustomSubtitle']))
        return_text = f"""
I have already purchased a return flight to Brazil departing on {self.data.extension_request['return_date']} 
(LATAM Airlines Confirmation: {self.data.extension_request['return_flight_confirmation']}). This date 
coincides with the expected completion of my sister's chemotherapy treatment protocol in December 2025.
<br/><br/>
My return to Brazil is essential for:
<br/>
• Resuming my role as Managing Partner of my consulting firm<br/>
• Reuniting with my husband and children<br/>
• Fulfilling ongoing client contracts and business obligations<br/>
• Managing my property portfolio<br/>
• Continuing my professional and community involvement
        """
        elements.append(Paragraph(return_text, self.styles['JustifiedBody']))
        
        # DOCUMENTATION ENCLOSED
        elements.append(Paragraph("<b>DOCUMENTATION ENCLOSED</b>", self.styles['CustomSubtitle']))
        docs_text = """
This application package includes comprehensive supporting documentation:
<br/><br/>
• Form I-539 with all required information<br/>
• Copy of passport (biographical page and US visa)<br/>
• Copy of I-94 Arrival/Departure Record<br/>
• Sister's Green Card and medical documentation<br/>
• Letter from Dr. Rebecca Martinez (Oncologist) confirming treatment plan<br/>
• Bank statements showing $260,000+ in liquid assets<br/>
• Business ownership documentation<br/>
• Property deeds ($750,000 in real estate)<br/>
• Return flight confirmation<br/>
• Letters of support from family and medical professionals<br/>
• Brazilian tax returns and financial statements<br/>
• Evidence of previous immigration compliance
        """
        elements.append(Paragraph(docs_text, self.styles['JustifiedBody']))
        
        # CONCLUSION
        elements.append(Paragraph("<b>CONCLUSION</b>", self.styles['CustomSubtitle']))
        conclusion_text = """
This extension request is based on genuine humanitarian circumstances—supporting my seriously ill 
sister during her cancer treatment. I have demonstrated strong ties to Brazil, substantial financial 
resources, perfect immigration compliance, and a confirmed return date. I respectfully request that 
USCIS grant this extension until January 9, 2026, allowing me to complete this essential family 
caregiving role before returning to Brazil.
<br/><br/>
Thank you for your consideration of this application.
        """
        elements.append(Paragraph(conclusion_text, self.styles['JustifiedBody']))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Assinatura
        signature_text = f"""
Respectfully submitted,<br/><br/><br/>
_____________________________<br/>
{self.data.applicant['full_name']}<br/>
Applicant<br/>
Date: {self.data.case_info['application_date']}
        """
        elements.append(Paragraph(signature_text, self.styles['Normal']))
        
        return elements
    
    def _create_personal_statement(self):
        """Cria personal statement detalhado"""
        elements = []
        
        tab_header = Paragraph("TAB B - PERSONAL STATEMENT", self.styles['SectionHeader'])
        elements.append(tab_header)
        elements.append(Spacer(1, 0.2*inch))
        
        title = Paragraph("DETAILED PERSONAL STATEMENT", self.styles['CustomSubtitle'])
        elements.append(title)
        
        statement_text = f"""
<b>My Name and Background:</b><br/>
My name is {self.data.applicant['full_name']}, and I am a {self.data.applicant['age']}-year-old 
Brazilian citizen from Belo Horizonte, Minas Gerais. I have been married to my husband, 
{self.data.applicant['spouse_name']}, for 32 years, and we have two wonderful children: 
{self.data.applicant['child1_name']} (age {2025 - 2002}) and {self.data.applicant['child2_name']} 
(age {2025 - 2006}).
<br/><br/>
<b>My Professional Background:</b><br/>
For the past 20 years, I have been the Managing Partner of {self.data.applicant['employer_name']}, 
a business consulting firm I founded in {self.data.applicant['position_start_date']}. Our firm provides 
strategic business consulting services to mid-sized companies throughout Minas Gerais. We currently 
employ 12 full-time consultants and serve approximately 45 active clients. My role requires my direct 
involvement in client relationships, business development, and overall firm management.
<br/><br/>
<b>My Original Visit Purpose:</b><br/>
I entered the United States on {self.data.applicant['date_of_last_arrival']} through 
{self.data.applicant['port_of_entry']} with a valid B-2 tourist visa. My original intention was to 
visit my sister, Patricia Costa Thompson, in Miami for a six-month period. I planned to enjoy tourism 
activities, visit family, and experience the cultural attractions of Florida. I had arranged my business 
affairs in Brazil to allow for this extended vacation, delegating day-to-day operations to my senior 
partners while maintaining remote oversight of critical decisions.
<br/><br/>
<b>The Unexpected Medical Emergency:</b><br/>
Shortly after my arrival in January 2025, my sister began experiencing severe abdominal pain and 
bloating. On February 10, 2025, she underwent emergency diagnostic testing at Jackson Memorial Hospital 
in Miami. On February 20, 2025, we received devastating news: Patricia was diagnosed with Stage 3 
ovarian cancer.
<br/><br/>
This diagnosis changed everything. Patricia is not just my sister—she is my only sibling, my closest 
confidante, and has been my best friend since childhood. Despite living in different countries for the 
past seven years (since she immigrated to the United States), we have maintained an incredibly close 
relationship through weekly video calls and regular visits.
<br/><br/>
<b>Patricia's Medical Situation:</b><br/>
Following her diagnosis, Patricia underwent major debulking surgery on February 28, 2025, performed 
by Dr. Rebecca Martinez, a gynecologic oncologist at Jackson Memorial Hospital. The surgery lasted 
over six hours and was successful in removing the primary tumor and affected tissue.
<br/><br/>
However, due to the advanced stage of her cancer, Patricia's medical team recommended an aggressive 
six-month chemotherapy protocol beginning in March 2025 and continuing through December 2025. She 
receives chemotherapy infusions every three weeks at the hospital's oncology center. Each treatment 
session lasts approximately 6-8 hours and leaves her severely fatigued and nauseated for several days 
afterward.
<br/><br/>
<b>Why My Presence Is Critical:</b><br/>
Patricia's husband, Robert Thompson, works full-time as an aerospace engineer at a defense contractor. 
His position requires him to maintain his full work schedule, and he cannot take extended leave due to 
project deadlines and security clearances. Their two children, Sarah (age 11) and Michael (age 8), need 
stability and support during their mother's illness.
<br/><br/>
As Patricia's only sibling and closest family member in the United States (our parents passed away 
several years ago), I am the only person who can provide the level of care and support she needs during 
this critical period. My daily responsibilities include:
<br/><br/>
<b>Medical Support:</b><br/>
• Driving Patricia to all chemotherapy appointments (every 3 weeks)<br/>
• Attending oncology consultations and taking detailed notes<br/>
• Managing her medication schedule and ensuring compliance<br/>
• Monitoring for side effects and complications<br/>
• Communicating with the medical team about concerns<br/>
• Coordinating with insurance companies and medical billing
<br/><br/>
<b>Daily Care:</b><br/>
• Preparing special meals suitable for her dietary restrictions<br/>
• Helping with personal care when she is too weak after treatments<br/>
• Ensuring she stays hydrated and rests adequately<br/>
• Providing companionship during her most difficult days<br/>
• Monitoring her emotional well-being
<br/><br/>
<b>Household and Family Support:</b><br/>
• Managing household tasks (cooking, cleaning, grocery shopping)<br/>
• Helping children with homework and school activities<br/>
• Driving children to school, sports, and activities<br/>
• Maintaining a sense of normalcy for the family<br/>
• Providing emotional support to Robert and the children
<br/><br/>
<b>The Treatment Timeline:</b><br/>
According to Dr. Martinez's treatment plan, Patricia's chemotherapy protocol will continue through 
December 2025. She has already completed 4 of 18 planned chemotherapy cycles. The medical team has 
indicated that consistent family support is crucial for optimal treatment outcomes and patient recovery.
<br/><br/>
I am requesting an extension of my B-2 status until January 9, 2026, which would allow me to support 
Patricia through the completion of her chemotherapy treatment and into her initial recovery period. 
This additional time is essential—not just helpful, but truly essential—for her physical recovery and 
emotional well-being.
<br/><br/>
<b>My Commitment to Return to Brazil:</b><br/>
While I am deeply committed to supporting my sister during this crisis, I am equally committed to 
returning to Brazil once her treatment is complete. My life, my family, my business, and my future 
are all in Brazil.
<br/><br/>
My husband and children in Belo Horizonte are anxiously awaiting my return. We communicate daily via 
video calls, and I can see how much they miss my physical presence. My son Lucas is completing his 
final year of university and will need my support as he transitions into his career. My daughter Ana 
is in her final years of high school and preparing for university entrance exams—a critical time when 
she needs her mother.
<br/><br/>
My business in Brazil continues to operate with my remote oversight, but my senior partners have made 
it clear that several major client relationships require my personal attention. We have three significant 
new client proposals pending that only I can finalize. My extended absence is creating strain on the 
firm, and I need to return to ensure its continued success.
<br/><br/>
Additionally, I own substantial property in Brazil (worth approximately $750,000 USD) that requires my 
management. My commercial property generates rental income that is part of our family's financial security.
<br/><br/>
<b>My Financial Independence:</b><br/>
Throughout this extension period, I will continue to be entirely self-supporting. I have substantial 
financial resources:
<br/>
• Over $260,000 in liquid bank accounts<br/>
• Investment portfolio worth $250,000<br/>
• Ongoing business income of approximately $4,200/month<br/>
• Rental income of approximately $2,800/month<br/>
• Total estimated expenses of only $3,500/month
<br/><br/>
I have not worked, will not work, and have no intention of working in the United States. I am not a 
burden on any U.S. government resources. I have maintained valid health insurance throughout my stay.
<br/><br/>
<b>My Perfect Compliance Record:</b><br/>
I have visited the United States twice before (in 2022 and 2023), and both times I departed exactly 
as scheduled after 14-day visits. I have never overstayed a visa, never violated any immigration rules, 
and have always been completely honest and transparent with U.S. immigration authorities.
<br/><br/>
<b>Conclusion - My Plea for Understanding:</b><br/>
I am asking for compassion and understanding in this extraordinary circumstance. I did not plan for 
this extension—I did not want this extension. I want to be home with my husband and children in Brazil. 
But my sister is fighting for her life, and she needs me.
<br/><br/>
This is not about tourism anymore—this is about family, about love, about being there for someone when 
they need you most. I am asking for the opportunity to complete this act of care for my only sibling, 
knowing that I will return to Brazil the moment her treatment is complete.
<br/><br/>
I respectfully request that USCIS grant this extension so that I can continue to support my sister 
through this life-threatening illness before returning to my life, my family, and my business in Brazil.
<br/><br/><br/>
Thank you for your consideration and understanding.
<br/><br/><br/>
_____________________________<br/>
{self.data.applicant['full_name']}<br/>
Date: {self.data.case_info['application_date']}
        """
        
        elements.append(Paragraph(statement_text, self.styles['JustifiedBody']))
        
        return elements
    
    def _create_medical_documentation(self):
        """Cria documentação médica"""
        elements = []
        
        tab_header = Paragraph("TAB C - MEDICAL DOCUMENTATION", self.styles['SectionHeader'])
        elements.append(tab_header)
        elements.append(Spacer(1, 0.2*inch))
        
        # Carta do médico
        elements.append(Paragraph("<b>MEDICAL DOCUMENTATION OVERVIEW</b>", self.styles['CustomSubtitle']))
        
        overview_text = """
This section contains medical documentation supporting the medical emergency that necessitates the 
extension of Maria Helena Costa's B-2 status. The primary documentation includes:
<br/><br/>
1. Letter from Dr. Rebecca Martinez, MD (Oncologist)<br/>
2. Treatment Plan and Protocol Summary<br/>
3. Hospital Records from Jackson Memorial Hospital<br/>
4. Patient's Green Card Copy (Patricia Costa Thompson)
        """
        elements.append(Paragraph(overview_text, self.styles['JustifiedBody']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Simular carta do médico
        elements.append(PageBreak())
        elements.append(Paragraph("<b>LETTER FROM TREATING PHYSICIAN</b>", self.styles['CustomSubtitle']))
        elements.append(Spacer(1, 0.2*inch))
        
        doctor_letterhead = """
<b>JACKSON MEMORIAL HOSPITAL</b><br/>
Sylvester Comprehensive Cancer Center<br/>
1611 NW 12th Avenue<br/>
Miami, Florida 33136<br/>
Phone: (305) 355-1000<br/>
Fax: (305) 355-2000
        """
        elements.append(Paragraph(doctor_letterhead, ParagraphStyle(
            name='Letterhead',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=15
        )))
        
        elements.append(Paragraph(self.data.case_info['application_date'], self.styles['Normal']))
        elements.append(Spacer(1, 0.15*inch))
        
        doctor_letter = f"""
<b>TO WHOM IT MAY CONCERN:</b>
<br/><br/>
<b>RE: Medical Treatment Plan for Patricia Costa Thompson</b><br/>
<b>Patient DOB:</b> {self.data.extension_request['sister_dob']}<br/>
<b>Diagnosis:</b> {self.data.extension_request['medical_diagnosis']}<br/>
<b>Treatment Period:</b> March 2025 - December 2025
<br/><br/>
I am writing this letter in my capacity as the treating oncologist for Ms. Patricia Costa Thompson, 
who is currently undergoing intensive chemotherapy treatment at Jackson Memorial Hospital's Sylvester 
Comprehensive Cancer Center.
<br/><br/>
<b>DIAGNOSIS AND TREATMENT:</b><br/>
Ms. Thompson was diagnosed with Stage 3 high-grade serous ovarian carcinoma on February 20, 2025. 
Following comprehensive staging, she underwent cytoreductive surgery on February 28, 2025. Post-surgical 
pathology confirmed the need for adjuvant chemotherapy.
<br/><br/>
<b>CURRENT TREATMENT PROTOCOL:</b><br/>
Ms. Thompson is currently receiving a standard six-cycle regimen of carboplatin and paclitaxel 
chemotherapy, administered intravenously every three weeks. She began this protocol in March 2025 
and has completed 4 of 18 planned cycles as of {datetime.now().strftime("%B %Y")}. The treatment 
protocol is scheduled to continue through December 2025.
<br/><br/>
<b>MEDICAL NECESSITY OF FAMILY SUPPORT:</b><br/>
The chemotherapy regimen Ms. Thompson is receiving is highly emetogenic and causes significant fatigue, 
nausea, and immunosuppression. Each treatment cycle requires:
<br/><br/>
• Transportation to and from the hospital (6-8 hour infusion sessions)<br/>
• Monitoring for acute toxicities and allergic reactions<br/>
• Management of delayed side effects (nausea, fatigue, neutropenia)<br/>
• Assistance with activities of daily living during recovery periods<br/>
• Medication management and compliance monitoring
<br/><br/>
<b>FAMILY CAREGIVER ROLE:</b><br/>
Ms. Thompson's sister, Maria Helena Costa, has been serving as her primary daytime caregiver since 
the diagnosis. This support has been medically beneficial and has positively impacted Ms. Thompson's 
treatment tolerance and psychological well-being. Studies consistently demonstrate that patients with 
strong family support systems have better treatment outcomes and quality of life during cancer therapy.
<br/><br/>
Given Ms. Thompson's ongoing treatment schedule through December 2025, continued family support from 
her sister is strongly recommended from a medical standpoint.
<br/><br/>
<b>PROGNOSIS:</b><br/>
With completion of the planned chemotherapy protocol and continued monitoring, Ms. Thompson has a 
favorable prognosis. However, the success of her treatment depends significantly on her ability to 
complete the full chemotherapy course with appropriate support systems in place.
<br/><br/>
If you require any additional medical information, please do not hesitate to contact my office.
<br/><br/><br/>
Sincerely,
<br/><br/><br/>
_____________________________<br/>
Rebecca Martinez, MD, FACOG<br/>
Board Certified - Gynecologic Oncology<br/>
Sylvester Comprehensive Cancer Center<br/>
Jackson Memorial Hospital<br/>
Phone: (305) 355-3640<br/>
Email: r.martinez@med.miami.edu
        """
        
        elements.append(Paragraph(doctor_letter, self.styles['JustifiedBody']))
        
        return elements
    
    def _create_financial_evidence(self):
        """Cria evidência financeira"""
        elements = []
        
        tab_header = Paragraph("TAB D - FINANCIAL EVIDENCE", self.styles['SectionHeader'])
        elements.append(tab_header)
        elements.append(Spacer(1, 0.2*inch))
        
        # Overview
        elements.append(Paragraph("<b>FINANCIAL DOCUMENTATION OVERVIEW</b>", self.styles['CustomSubtitle']))
        
        overview_text = """
This section provides comprehensive evidence of Maria Helena Costa's ability to financially support 
herself during the requested extension period without seeking employment or becoming a public charge. 
The documentation demonstrates substantial financial resources significantly exceeding the requirements 
for a six-month extension.
        """
        elements.append(Paragraph(overview_text, self.styles['JustifiedBody']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Tabela de ativos
        elements.append(Paragraph("<b>SUMMARY OF FINANCIAL ASSETS</b>", self.styles['CustomSubtitle']))
        
        assets_data = [
            ["ASSET TYPE", "AMOUNT (BRL)", "AMOUNT (USD)", "DOCUMENTATION"],
            [
                "Checking Account\n(Banco do Brasil)",
                "R$ 487,000",
                "$97,400",
                "Bank statements (6 months)"
            ],
            [
                "Savings Account\n(Banco do Brasil)",
                "R$ 823,000",
                "$164,600",
                "Bank statements (6 months)"
            ],
            [
                "Investment Portfolio\n(Securities)",
                "R$ 1,250,000",
                "$250,000",
                "Brokerage statements"
            ],
            [
                "Primary Residence\n(Real Estate)",
                "R$ 1,450,000",
                "$290,000",
                "Property deed"
            ],
            [
                "Commercial Property\n(Office Building)",
                "R$ 2,300,000",
                "$460,000",
                "Property deed + rental agreement"
            ],
            [
                "<b>TOTAL ASSETS</b>",
                "<b>R$ 6,310,000</b>",
                "<b>$1,262,000</b>",
                ""
            ]
        ]
        
        assets_table = Table(assets_data, colWidths=[2*inch, 1.2*inch, 1.2*inch, 2*inch])
        assets_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8eaf6')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(assets_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Renda mensal
        elements.append(Paragraph("<b>MONTHLY INCOME SOURCES</b>", self.styles['CustomSubtitle']))
        
        income_data = [
            ["INCOME SOURCE", "MONTHLY AMOUNT (USD)", "ANNUAL AMOUNT (USD)"],
            ["Business Income (Consulting Firm)", "$4,200", "$50,400"],
            ["Commercial Property Rental Income", "$2,800", "$33,600"],
            ["Investment Portfolio Dividends", "$1,500", "$18,000"],
            ["<b>TOTAL MONTHLY INCOME</b>", "<b>$8,500</b>", "<b>$102,000</b>"]
        ]
        
        income_table = Table(income_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
        income_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8eaf6')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ]))
        
        elements.append(income_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Despesas estimadas
        elements.append(Paragraph("<b>ESTIMATED MONTHLY EXPENSES IN THE UNITED STATES</b>", self.styles['CustomSubtitle']))
        
        expenses_data = [
            ["EXPENSE CATEGORY", "MONTHLY AMOUNT (USD)"],
            ["Housing (Staying with sister)", "$0"],
            ["Food and Groceries", "$800"],
            ["Transportation (Gas, insurance, tolls)", "$400"],
            ["Health Insurance (Brazilian travel insurance)", "$250"],
            ["Personal Care and Miscellaneous", "$800"],
            ["Phone and Internet", "$100"],
            ["Entertainment and Activities", "$400"],
            ["Emergency/Contingency Fund", "$750"],
            ["<b>TOTAL MONTHLY EXPENSES</b>", "<b>$3,500</b>"],
            ["", ""],
            ["<b>Extension Period (6 months)</b>", ""],
            ["<b>TOTAL ESTIMATED COST</b>", "<b>$21,000</b>"]
        ]
        
        expenses_table = Table(expenses_data, colWidths=[4*inch, 2*inch])
        expenses_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, 8), 0.5, colors.grey),
            ('BACKGROUND', (0, 8), (-1, 8), colors.HexColor('#e8eaf6')),
            ('FONTNAME', (0, 8), (-1, 8), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 10), (-1, 10), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 10), (-1, 10), colors.whitesmoke),
            ('FONTNAME', (0, 10), (-1, 10), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 11), (-1, 11), colors.HexColor('#ffebee')),
            ('FONTNAME', (0, 11), (-1, 11), 'Helvetica-Bold'),
            ('GRID', (0, 10), (-1, 11), 0.5, colors.grey),
        ]))
        
        elements.append(expenses_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Análise financeira
        elements.append(Paragraph("<b>FINANCIAL ANALYSIS</b>", self.styles['CustomSubtitle']))
        
        analysis_text = """
<b>FINANCIAL CAPACITY SUMMARY:</b>
<br/><br/>
<b>Available Liquid Assets:</b> $512,000 USD (checking + savings + investments)<br/>
<b>Total Extension Cost:</b> $21,000 USD (6 months)<br/>
<b>Coverage Ratio:</b> 24.4x (liquid assets cover extension cost 24 times over)<br/>
<b>Monthly Income:</b> $8,500 USD (exceeds monthly expenses by $5,000)<br/>
<b>Net Monthly Surplus:</b> $5,000 USD
<br/><br/>
<b>CONCLUSION:</b> Maria Helena Costa possesses substantial financial resources far exceeding the 
requirements for a six-month extension. With over half a million dollars in liquid assets and 
ongoing monthly income of $8,500, she can easily support herself without seeking employment or 
becoming a public charge. Her financial capacity demonstrates 24 times the required funds for the 
extension period.
        """
        
        elements.append(Paragraph(analysis_text, self.styles['JustifiedBody']))
        
        # Documentos incluídos
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("<b>SUPPORTING FINANCIAL DOCUMENTS INCLUDED:</b>", self.styles['CustomSubtitle']))
        
        docs_list = """
1. Bank statements from Banco do Brasil (checking account) - Last 6 months<br/>
2. Bank statements from Banco do Brasil (savings account) - Last 6 months<br/>
3. Investment portfolio statements - Current value and holdings<br/>
4. Brazilian Tax Return (2023) showing annual income of R$ 336,000<br/>
5. Business registration and ownership documentation<br/>
6. Commercial property deed and rental agreement<br/>
7. Primary residence property deed<br/>
8. Letter from accountant certifying financial position<br/>
9. Valid health insurance policy documentation
        """
        
        elements.append(Paragraph(docs_list, self.styles['Normal']))
        
        return elements
    
    def _create_ties_to_brazil(self):
        """Cria evidência de vínculos com Brasil"""
        elements = []
        
        tab_header = Paragraph("TAB E - EVIDENCE OF STRONG TIES TO BRAZIL", self.styles['SectionHeader'])
        elements.append(tab_header)
        elements.append(Spacer(1, 0.2*inch))
        
        # Overview
        elements.append(Paragraph("<b>OVERVIEW OF TIES TO BRAZIL</b>", self.styles['CustomSubtitle']))
        
        overview_text = """
This section provides comprehensive evidence demonstrating Maria Helena Costa's extremely strong 
ties to Brazil, which ensure her timely return following the completion of her sister's medical 
treatment. These ties include family, business ownership, property ownership, professional licenses, 
and deep community involvement.
        """
        elements.append(Paragraph(overview_text, self.styles['JustifiedBody']))
        elements.append(Spacer(1, 0.2*inch))
        
        # 1. FAMILY TIES
        elements.append(Paragraph("<b>1. FAMILY TIES TO BRAZIL</b>", self.styles['CustomSubtitle']))
        
        family_text = f"""
<b>Immediate Family in Brazil:</b>
<br/><br/>
<b>Husband:</b> {self.data.applicant['spouse_name']}<br/>
• Born: {self.data.applicant['spouse_dob']}<br/>
• Citizenship: {self.data.applicant['spouse_citizenship']}<br/>
• Location: {self.data.applicant['spouse_location']}<br/>
• Occupation: Civil Engineer, employed by Construtora Minas Ltda. for 28 years<br/>
• Relationship: Married since 1993 (32 years)
<br/><br/>
<b>Son:</b> {self.data.applicant['child1_name']}<br/>
• Born: {self.data.applicant['child1_dob']} (Age {2025 - 2002})<br/>
• Status: University student at Universidade Federal de Minas Gerais (UFMG)<br/>
• Program: Bachelor of Science in Civil Engineering (Final year)<br/>
• Location: Living in family home in Belo Horizonte<br/>
• Dependence: Financially dependent on parents; needs mother's guidance for career transition
<br/><br/>
<b>Daughter:</b> {self.data.applicant['child2_name']}<br/>
• Born: {self.data.applicant['child2_dob']} (Age {2025 - 2006})<br/>
• Status: High school student at Colégio Santo Antonio<br/>
• Grade: 12th grade (Final year before university)<br/>
• Location: Living in family home in Belo Horizonte<br/>
• Dependence: Preparing for ENEM (university entrance exam); needs mother's support during critical year
<br/><br/>
<b>Family Dependence:</b><br/>
My husband and children are anxiously awaiting my return. We maintain daily contact via video calls, 
but my physical absence has been difficult for the entire family. Both children are at critical 
transition points in their lives—Lucas finishing university and Ana preparing for university entrance—
and they need their mother's guidance and support.
        """
        
        elements.append(Paragraph(family_text, self.styles['JustifiedBody']))
        elements.append(Spacer(1, 0.2*inch))
        
        # 2. BUSINESS OWNERSHIP
        elements.append(Paragraph("<b>2. BUSINESS OWNERSHIP</b>", self.styles['CustomSubtitle']))
        
        business_text = f"""
<b>Company Name:</b> {self.data.applicant['employer_name']}<br/>
<b>Role:</b> {self.data.applicant['position_title']}<br/>
<b>Founded:</b> {self.data.applicant['position_start_date']} (20 years ago)<br/>
<b>Ownership:</b> 65% majority shareholder<br/>
<b>Location:</b> {self.data.applicant['employer_address']}, {self.data.applicant['employer_city']}, 
{self.data.applicant['employer_state']}, Brazil
<br/><br/>
<b>Business Details:</b><br/>
Costa & Associados Consultoria is a mid-sized business consulting firm specializing in strategic 
planning, financial analysis, and operational improvement for companies throughout Minas Gerais state. 
The firm has been operating continuously for 20 years under my direct leadership.
<br/><br/>
<b>Company Statistics:</b><br/>
• Annual Revenue: R$ 2.4 million ($480,000 USD)<br/>
• Number of Employees: 12 full-time consultants<br/>
• Active Clients: 45 companies<br/>
• Business Structure: Sociedade Limitada (LLC equivalent)<br/>
• CNPJ (Brazilian Tax ID): 12.345.678/0001-90
<br/><br/>
<b>My Essential Role:</b><br/>
As the founder and Managing Partner, my role is irreplaceable:
<br/>
• I maintain personal relationships with all major clients (representing 75% of revenue)<br/>
• I am the primary signatory on all contracts and banking relationships<br/>
• My expertise and reputation are the foundation of the firm's success<br/>
• Three major client proposals (worth R$ 600,000 combined) require my personal involvement to close<br/>
• New business development requires my direct participation
<br/><br/>
While I have been able to manage critical decisions remotely during this emergency, my senior partners 
have made it clear that several client relationships are at risk due to my extended absence. My physical 
return is essential for the continued success and survival of the business.
<br/><br/>
<b>Documentation Included:</b><br/>
• Company registration documents (CNPJ)<br/>
• Shareholding certificates showing 65% ownership<br/>
• Letters from senior partners confirming need for my return<br/>
• Client contracts requiring my signature<br/>
• Financial statements showing company revenue and stability
        """
        
        elements.append(Paragraph(business_text, self.styles['JustifiedBody']))
        elements.append(Spacer(1, 0.2*inch))
        
        # 3. PROPERTY OWNERSHIP
        elements.append(Paragraph("<b>3. REAL ESTATE OWNERSHIP</b>", self.styles['CustomSubtitle']))
        
        property_data = [
            ["PROPERTY", "TYPE", "VALUE (BRL)", "VALUE (USD)", "STATUS"],
            [
                "Rua das Acácias, 456\nBelo Horizonte, MG",
                "Primary Residence\n(Single-family home)",
                "R$ 1,450,000",
                "$290,000",
                "Owned outright\n(no mortgage)"
            ],
            [
                "Av. Afonso Pena, 1234\nBelo Horizonte, MG",
                "Commercial Property\n(Office building)",
                "R$ 2,300,000",
                "$460,000",
                "Owned outright\nGenerating rental income"
            ],
            [
                "<b>TOTAL</b>",
                "",
                "<b>R$ 3,750,000</b>",
                "<b>$750,000</b>",
                ""
            ]
        ]
        
        property_table = Table(property_data, colWidths=[1.8*inch, 1.5*inch, 1.2*inch, 1.2*inch, 1.3*inch])
        property_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8eaf6')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(property_table)
        
        property_text = """
<br/><br/>
<b>Property Management Requirements:</b><br/>
Both properties require my ongoing management and attention:
<br/><br/>
<b>Primary Residence:</b> This is our family home where my husband and children currently live. 
The property requires regular maintenance decisions, property tax management, and homeowner's 
insurance renewals.
<br/><br/>
<b>Commercial Property:</b> This office building generates rental income of R$ 14,000/month ($2,800 USD). 
I manage tenant relationships, lease renewals, building maintenance, and financial oversight. Current 
tenants have expressed concern about my extended absence, as lease renewal negotiations for two major 
tenants are scheduled for February 2026.
<br/><br/>
<b>Documentation Included:</b><br/>
• Property deeds (Escrituras) for both properties<br/>
• Property tax receipts (IPTU) - showing current status<br/>
• Commercial lease agreements<br/>
• Property insurance policies<br/>
• Property appraisal reports
        """
        
        elements.append(Paragraph(property_text, self.styles['JustifiedBody']))
        elements.append(Spacer(1, 0.2*inch))
        
        # 4. PROFESSIONAL LICENSE
        elements.append(Paragraph("<b>4. PROFESSIONAL LICENSE & CERTIFICATIONS</b>", self.styles['CustomSubtitle']))
        
        license_text = """
<b>Professional Accounting License (CRC/MG):</b><br/>
• License Number: CRC-MG 075489<br/>
• Issued by: Conselho Regional de Contabilidade de Minas Gerais<br/>
• Status: Active and in good standing<br/>
• Original Issue Date: January 1998<br/>
• Renewal: Annual (next renewal due March 2026)
<br/><br/>
<b>Professional Memberships:</b><br/>
• Belo Horizonte Business Women Association (Member since 2005)<br/>
• Minas Gerais Institute of Business Consultants (Founding Member)<br/>
• Brazilian Accounting Association (CFC) - Active Member<br/>
• Local Chamber of Commerce - Board Member (2020-2025 term)
<br/><br/>
These professional licenses and memberships are essential to my consulting practice in Brazil and 
cannot be transferred or used in the United States. My professional reputation and network in Brazil 
represent 20 years of relationship-building and are irreplaceable.
        """
        
        elements.append(Paragraph(license_text, self.styles['JustifiedBody']))
        elements.append(Spacer(1, 0.2*inch))
        
        # CONCLUSION
        elements.append(Paragraph("<b>CONCLUSION: COMPELLING REASONS TO RETURN</b>", self.styles['CustomSubtitle']))
        
        conclusion_text = """
Maria Helena Costa has extraordinarily strong ties to Brazil that guarantee her return:
<br/><br/>
✓ <b>Immediate Family:</b> Husband of 32 years and two children (ages 19 and 23) awaiting her return<br/>
✓ <b>Business Ownership:</b> 65% owner of successful consulting firm (20 years, 12 employees, 45 clients)<br/>
✓ <b>Property:</b> $750,000 in Brazilian real estate requiring her management<br/>
✓ <b>Professional Identity:</b> Licensed CPA with 20-year career in Brazil<br/>
✓ <b>Financial Roots:</b> Over $1.2 million in assets entirely located in Brazil<br/>
✓ <b>Community Ties:</b> Deep involvement in professional and social organizations<br/>
✓ <b>Cultural Identity:</b> 59 years of life built in Brazil
<br/><br/>
These ties are not theoretical—they are practical, financial, emotional, and irreplaceable. Maria's 
entire life, career, family, and future are in Brazil. She is requesting this extension solely to 
support her seriously ill sister during cancer treatment, after which she will immediately return to 
Brazil to resume her life.
        """
        
        elements.append(Paragraph(conclusion_text, self.styles['JustifiedBody']))
        
        return elements
    
    def _create_travel_history(self):
        """Cria histórico de viagens"""
        elements = []
        
        tab_header = Paragraph("TAB F - TRAVEL HISTORY & IMMIGRATION COMPLIANCE", self.styles['SectionHeader'])
        elements.append(tab_header)
        elements.append(Spacer(1, 0.2*inch))
        
        # Overview
        elements.append(Paragraph("<b>COMPLETE U.S. TRAVEL HISTORY</b>", self.styles['CustomSubtitle']))
        
        overview_text = """
Maria Helena Costa has a perfect record of immigration compliance with the United States. This section 
documents her complete travel history to the United States, demonstrating consistent adherence to visa 
terms and timely departures.
        """
        elements.append(Paragraph(overview_text, self.styles['JustifiedBody']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Tabela de viagens
        travel_data = [
            ["VISIT #", "ENTRY DATE", "EXIT DATE", "DURATION", "PURPOSE", "PORT OF ENTRY"],
            [
                "1",
                "June 10, 2022",
                "June 24, 2022",
                "14 days",
                "Tourism\n(Disney World)",
                "Orlando Int'l\nAirport (MCO)"
            ],
            [
                "2",
                "Nov 15, 2023",
                "Nov 29, 2023",
                "14 days",
                "Tourism\n(Thanksgiving)",
                "Miami Int'l\nAirport (MIA)"
            ],
            [
                "3",
                "Jan 10, 2025",
                "Extension\nRequested",
                "Currently\n5 months",
                "Tourism\n(Family care)",
                "Miami Int'l\nAirport (MIA)"
            ]
        ]
        
        travel_table = Table(travel_data, colWidths=[0.7*inch, 1.2*inch, 1.2*inch, 1*inch, 1.3*inch, 1.3*inch])
        travel_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#fff3e0')),
        ]))
        
        elements.append(travel_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Análise do histórico
        elements.append(Paragraph("<b>IMMIGRATION COMPLIANCE ANALYSIS</b>", self.styles['CustomSubtitle']))
        
        compliance_text = """
<b>VISIT #1 - JUNE 2022 (Disney World Vacation):</b><br/>
• Duration: 14 days<br/>
• Entered: June 10, 2022 at Orlando International Airport<br/>
• Departed: June 24, 2022 (on schedule)<br/>
• Purpose: Family vacation to Walt Disney World Resort with husband and children<br/>
• Compliance: Departed exactly as scheduled with no overstay<br/>
• I-94 Status: Properly returned and recorded
<br/><br/>
<b>VISIT #2 - NOVEMBER 2023 (Thanksgiving Visit):</b><br/>
• Duration: 14 days<br/>
• Entered: November 15, 2023 at Miami International Airport<br/>
• Departed: November 29, 2023 (on schedule)<br/>
• Purpose: Thanksgiving holiday visit to sister Patricia and her family<br/>
• Compliance: Departed exactly as scheduled with no overstay<br/>
• I-94 Status: Properly returned and recorded
<br/><br/>
<b>VISIT #3 - JANUARY 2025 (Current Visit):</b><br/>
• Duration: Currently 5 months (extension requested for additional 6 months)<br/>
• Entered: January 10, 2025 at Miami International Airport<br/>
• Authorized Until: July 9, 2025 (extension requested before expiration)<br/>
• Purpose: Originally tourism; circumstances changed due to sister's cancer diagnosis<br/>
• Compliance: Filing extension application BEFORE current status expires<br/>
• I-94 Status: Valid and being properly maintained
<br/><br/>
<b>COMPLIANCE SUMMARY:</b><br/>
✓ Total previous visits to U.S.: 2<br/>
✓ Total time spent in U.S. previously: 28 days<br/>
✓ Number of overstays: ZERO<br/>
✓ Number of violations: ZERO<br/>
✓ Timely departures: 100% (2 out of 2 previous visits)<br/>
✓ Current application: Filed timely BEFORE status expiration
<br/><br/>
<b>KEY POINTS:</b><br/>
1. Both previous visits were short-term (14 days each)<br/>
2. Both previous visits ended with timely, voluntary departure<br/>
3. No history of overstaying or violating visa terms<br/>
4. Current extension request filed well in advance of status expiration<br/>
5. Clear pattern of respecting U.S. immigration laws
        """
        
        elements.append(Paragraph(compliance_text, self.styles['JustifiedBody']))
        elements.append(Spacer(1, 0.2*inch))
        
        # VISA STATUS
        elements.append(Paragraph("<b>CURRENT VISA STATUS</b>", self.styles['CustomSubtitle']))
        
        visa_text = f"""
<b>Visa Type:</b> B-2 (Visitor for Pleasure)<br/>
<b>Visa Number:</b> {self.data.applicant['visa_number']}<br/>
<b>Issue Date:</b> {self.data.applicant['visa_issue_date']}<br/>
<b>Expiry Date:</b> {self.data.applicant['visa_expiry_date']}<br/>
<b>Entries Allowed:</b> {self.data.applicant['visa_entries']}<br/>
<b>Issuing Post:</b> {self.data.applicant['visa_issue_post']}
<br/><br/>
<b>Passport Information:</b><br/>
<b>Passport Number:</b> {self.data.applicant['passport_number']}<br/>
<b>Issue Date:</b> {self.data.applicant['passport_issue_date']}<br/>
<b>Expiry Date:</b> {self.data.applicant['passport_expiry_date']}<br/>
<b>Issuing Country:</b> Brazil<br/>
<b>Validity:</b> Valid for {2029 - 2019} more years (expires 2031)
<br/><br/>
Both the B-2 visa and passport remain valid for multiple years beyond the requested extension period.
        """
        
        elements.append(Paragraph(visa_text, self.styles['JustifiedBody']))
        elements.append(Spacer(1, 0.2*inch))
        
        # CONFIRMATION
        elements.append(Paragraph("<b>CONFIRMED RETURN TO BRAZIL</b>", self.styles['CustomSubtitle']))
        
        return_text = f"""
<b>Return Flight Booked:</b><br/>
• Airline: LATAM Airlines<br/>
• Confirmation Number: {self.data.extension_request['return_flight_confirmation']}<br/>
• Departure Date: {self.data.extension_request['return_date']}<br/>
• Route: Miami (MIA) → Belo Horizonte (CNF)<br/>
• Passenger: {self.data.applicant['full_name']}<br/>
• Ticket Status: Confirmed and paid in full
<br/><br/>
This return flight reservation demonstrates my firm intention to depart the United States immediately 
upon completion of my sister's medical treatment. The departure date of January 10, 2026 coincides 
with the projected completion of Patricia's chemotherapy protocol (December 2025) and allows for a 
brief recovery period before my return.
<br/><br/>
<b>Documentation Included:</b><br/>
• LATAM Airlines flight confirmation and receipt<br/>
• Passport copies showing previous entry/exit stamps<br/>
• I-94 records from previous visits<br/>
• Current I-94 Arrival/Departure Record
        """
        
        elements.append(Paragraph(return_text, self.styles['JustifiedBody']))
        
        return elements
    
    def _create_supporting_letters(self):
        """Cria cartas de suporte"""
        elements = []
        
        tab_header = Paragraph("TAB G - SUPPORTING LETTERS", self.styles['SectionHeader'])
        elements.append(tab_header)
        elements.append(Spacer(1, 0.2*inch))
        
        # Letter 1: From Sister
        elements.append(Paragraph("<b>LETTER #1: FROM PATIENT (PATRICIA COSTA THOMPSON)</b>", self.styles['CustomSubtitle']))
        elements.append(Spacer(1, 0.15*inch))
        
        sister_letter = f"""
{self.data.extension_request['sister_address']}<br/>
{self.data.case_info['application_date']}
<br/><br/>
To Whom It May Concern:
<br/><br/>
<b>RE: Support for Maria Helena Costa's B-2 Extension Application</b>
<br/><br/>
My name is Patricia Costa Thompson, and I am writing to support my sister Maria Helena Costa's 
application to extend her B-2 visitor status. I am a U.S. Permanent Resident (Green Card Number: 
{self.data.extension_request['sister_green_card_number']}) and have been living in Miami, Florida 
since 2018.
<br/><br/>
<b>My Medical Situation:</b><br/>
On February 20, 2025, I was diagnosed with Stage 3 ovarian cancer. This diagnosis came as a complete 
shock to my entire family. I underwent major surgery on February 28, 2025, and have been receiving 
intensive chemotherapy treatment at Jackson Memorial Hospital since March 2025. My treatment protocol 
continues through December 2025.
<br/><br/>
<b>Maria's Critical Role:</b><br/>
When Maria arrived in January 2025, she came for a regular visit. Neither of us could have imagined 
what was about to happen. When I received my cancer diagnosis, Maria immediately became my primary 
caregiver and support system.
<br/><br/>
My husband, Robert Thompson, works full-time and cannot take extended leave. Our two children (Sarah, 
age 11, and Michael, age 8) need stability during this difficult time. Maria has been the person who:
<br/>
• Drives me to every chemotherapy appointment (every 3 weeks)<br/>
• Stays with me during the 6-8 hour infusion sessions<br/>
• Helps me manage side effects and medications<br/>
• Cares for me when I'm too weak to care for myself<br/>
• Helps with my children when I cannot<br/>
• Provides emotional support when I feel hopeless<br/>
• Speaks to my doctors and understands my treatment plan
<br/><br/>
<b>Why This Extension Matters:</b><br/>
I honestly don't know how I would get through this treatment without Maria. She is my only sibling. 
Our parents passed away several years ago. She is the only family member I have who can provide this 
level of care and support.
<br/><br/>
My oncologist has confirmed that having strong family support improves treatment outcomes for cancer 
patients. Maria's presence has made an enormous difference in my ability to tolerate the chemotherapy 
and maintain hope during this terrible time.
<br/><br/>
I am respectfully requesting that USCIS grant Maria's extension so she can continue supporting me 
through the completion of my treatment in December 2025. I know she will return to Brazil immediately 
after—her family is there, her business is there, and her entire life is there. She is only staying 
here because I need her.
<br/><br/>
<b>My Assurance:</b><br/>
I guarantee that Maria will return to Brazil as planned. She has no intention of remaining in the 
United States permanently. She has a husband, children, and a successful business waiting for her 
in Brazil. She is here solely to help me survive this crisis.
<br/><br/>
Thank you for considering this application with compassion and understanding.
<br/><br/><br/>
Sincerely,
<br/><br/><br/>
_____________________________<br/>
Patricia Costa Thompson<br/>
U.S. Permanent Resident<br/>
Green Card Number: {self.data.extension_request['sister_green_card_number']}<br/>
Phone: {self.data.extension_request['sister_phone']}<br/>
Date: {self.data.case_info['application_date']}
        """
        
        elements.append(Paragraph(sister_letter, self.styles['JustifiedBody']))
        
        # Letter 2: From Husband in Brazil
        elements.append(PageBreak())
        elements.append(Paragraph("<b>LETTER #2: FROM HUSBAND (CARLOS EDUARDO COSTA)</b>", self.styles['CustomSubtitle']))
        elements.append(Spacer(1, 0.15*inch))
        
        husband_letter = f"""
{self.data.applicant['address_brazil']}<br/>
{self.data.applicant['city_brazil']}, {self.data.applicant['state_brazil']} {self.data.applicant['zip_brazil']}<br/>
Brazil<br/>
{self.data.case_info['application_date']}
<br/><br/>
To Whom It May Concern:
<br/><br/>
<b>RE: Support for My Wife's B-2 Extension Application</b>
<br/><br/>
My name is Carlos Eduardo Costa, and I am writing to support my wife Maria Helena Costa's application 
to extend her visitor status in the United States. Maria and I have been married for 32 years, and we 
have two children together who currently live with me in Brazil.
<br/><br/>
<b>Our Family Situation:</b><br/>
When Maria left for the United States in January 2025, we thought she would be gone for six months 
for a regular visit to her sister. None of us anticipated that her sister would be diagnosed with 
cancer shortly after her arrival.
<br/><br/>
While it has been extremely difficult having Maria away from Brazil for this extended period, I fully 
understand and support her need to stay with Patricia during her cancer treatment. Patricia is Maria's 
only sibling and has no other family in the United States who can provide this level of care.
<br/><br/>
<b>Our Children Need Their Mother:</b><br/>
Our son, Lucas (age 23), is completing his final year of civil engineering at UFMG. He is preparing 
to enter the workforce and needs his mother's guidance during this transition. Our daughter, Ana 
(age 19), is in her final year of high school and preparing for university entrance exams. This is 
a critical time in both of their lives, and they need their mother.
<br/><br/>
We speak with Maria via video call every day. I can see how torn she is between her duty to her sister 
and her longing to be home with us. We miss her terribly, but we understand that Patricia needs her 
right now.
<br/><br/>
<b>Maria's Business Needs Her:</b><br/>
Maria is the Managing Partner of Costa & Associados Consultoria, which she founded 20 years ago. I 
have been helping to coordinate with her senior partners during her absence, but several major clients 
have expressed concern about her continued absence. The business needs her personal attention to 
maintain client relationships.
<br/><br/>
<b>My Assurance to USCIS:</b><br/>
I can assure you that Maria will return to Brazil the moment Patricia's treatment is complete. Our 
entire life is here—our children, our home, her business, our family, our friends. Maria has no 
intention or desire to remain in the United States. She is there solely because her sister is fighting 
for her life and needs family support.
<br/><br/>
I am asking you to please grant this extension so that Maria can fulfill her duty to her sister before 
returning home to us. We are counting the days until she can come back to Brazil.
<br/><br/>
Thank you for your understanding and compassion.
<br/><br/><br/>
Sincerely,
<br/><br/><br/>
_____________________________<br/>
Carlos Eduardo Costa<br/>
Civil Engineer<br/>
Construtora Minas Ltda.<br/>
Brazilian Passport: {self.data.applicant['spouse_passport']}<br/>
Phone: {self.data.applicant['home_phone']}<br/>
Email: carlos.costa@consminas.com.br<br/>
Date: {self.data.case_info['application_date']}
        """
        
        elements.append(Paragraph(husband_letter, self.styles['JustifiedBody']))
        
        return elements
    
    def _create_passport_i94(self):
        """Cria documentação de passaporte e I-94"""
        elements = []
        
        tab_header = Paragraph("TAB H - PASSPORT & I-94 DOCUMENTATION", self.styles['SectionHeader'])
        elements.append(tab_header)
        elements.append(Spacer(1, 0.2*inch))
        
        # Overview
        elements.append(Paragraph("<b>IDENTITY DOCUMENTS</b>", self.styles['CustomSubtitle']))
        
        overview_text = """
This section contains copies of Maria Helena Costa's passport and I-94 Arrival/Departure Record, 
documenting her identity and current immigration status in the United States.
        """
        elements.append(Paragraph(overview_text, self.styles['JustifiedBody']))
        elements.append(Spacer(1, 0.2*inch))
        
        # PASSPORT INFO
        elements.append(Paragraph("<b>BRAZILIAN PASSPORT - BIOGRAPHICAL PAGE</b>", self.styles['CustomSubtitle']))
        
        passport_data = [
            ["FIELD", "INFORMATION"],
            ["Type", "Ordinary Passport (Type P)"],
            ["Country Code", "BRA (Federative Republic of Brazil)"],
            ["Passport Number", self.data.applicant['passport_number']],
            ["Surname", self.data.applicant['family_name']],
            ["Given Names", self.data.applicant['given_name']],
            ["Nationality", "BRAZILIAN"],
            ["Date of Birth", self.data.applicant['dob']],
            ["Sex", "F (Female)"],
            ["Place of Birth", f"{self.data.applicant['pob_city']}, {self.data.applicant['pob_state']}, Brazil"],
            ["Date of Issue", self.data.applicant['passport_issue_date']],
            ["Date of Expiry", self.data.applicant['passport_expiry_date']],
            ["Authority", self.data.applicant['passport_issue_place']],
        ]
        
        passport_table = Table(passport_data, colWidths=[2*inch, 4*inch])
        passport_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(passport_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # U.S. VISA INFO
        elements.append(Paragraph("<b>U.S. VISA INFORMATION</b>", self.styles['CustomSubtitle']))
        
        visa_data = [
            ["FIELD", "INFORMATION"],
            ["Visa Type", "B-2 (Visitor for Pleasure)"],
            ["Visa Number", self.data.applicant['visa_number']],
            ["Issue Date", self.data.applicant['visa_issue_date']],
            ["Expiry Date", self.data.applicant['visa_expiry_date']],
            ["Entries", "Multiple (M)"],
            ["Issuing Post", self.data.applicant['visa_issue_post']],
            ["Visa Class", "B2"],
        ]
        
        visa_table = Table(visa_data, colWidths=[2*inch, 4*inch])
        visa_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(visa_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # I-94 INFO
        elements.append(Paragraph("<b>I-94 ARRIVAL/DEPARTURE RECORD</b>", self.styles['CustomSubtitle']))
        
        i94_data = [
            ["FIELD", "INFORMATION"],
            ["I-94 Number", self.data.applicant['current_i94_number']],
            ["Name", self.data.applicant['full_name']],
            ["Date of Birth", self.data.applicant['dob']],
            ["Passport Number", self.data.applicant['passport_number']],
            ["Country of Citizenship", "Brazil"],
            ["Class of Admission", "B-2"],
            ["Port of Entry", self.data.applicant['port_of_entry']],
            ["Date of Arrival", self.data.applicant['date_of_last_arrival']],
            ["Admit Until Date", self.data.applicant['current_status_expires']],
            ["Current Status", "B-2 (Visitor for Pleasure)"],
        ]
        
        i94_table = Table(i94_data, colWidths=[2*inch, 4*inch])
        i94_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(i94_table)
        elements.append(Spacer(1, 0.2*inch))
        
        note_text = """
<br/><br/>
<b>NOTE:</b> The actual document package includes clear, legible photocopies of:
<br/>
• Passport biographical page<br/>
• U.S. B-2 visa page<br/>
• All entry/exit stamps from previous U.S. visits<br/>
• Current I-94 Arrival/Departure Record (printed from CBP website)<br/>
• Previous I-94 records showing timely departures
<br/><br/>
All documents are valid and authentic. The passport and visa remain valid well beyond the requested 
extension period.
        """
        
        elements.append(Paragraph(note_text, self.styles['JustifiedBody']))
        
        return elements
    
    def _create_document_checklist(self):
        """Cria checklist de documentos"""
        elements = []
        
        tab_header = Paragraph("TAB I - SUPPORTING DOCUMENT CHECKLIST", self.styles['SectionHeader'])
        elements.append(tab_header)
        elements.append(Spacer(1, 0.2*inch))
        
        # Overview
        elements.append(Paragraph("<b>COMPLETE APPLICATION PACKAGE CHECKLIST</b>", self.styles['CustomSubtitle']))
        
        overview_text = """
This checklist confirms that all required supporting documents are included in this B-2 extension 
application package. Each document has been carefully prepared and organized for your review.
        """
        elements.append(Paragraph(overview_text, self.styles['JustifiedBody']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Checklist
        checklist_data = [
            ["☑", "DOCUMENT", "STATUS"],
            ["☑", "Form I-539 (Application to Extend/Change Nonimmigrant Status)", "Completed"],
            ["☑", "Filing Fee Payment ($370.00)", "Included"],
            ["☑", "Cover Letter & Application Overview", "Page 4"],
            ["☑", "Personal Statement (Detailed Explanation)", "Page 7"],
            ["☑", "Copy of Passport (Biographical Page)", "Page 28"],
            ["☑", "Copy of U.S. B-2 Visa Page", "Page 28"],
            ["☑", "Copy of I-94 Arrival/Departure Record (Current)", "Page 29"],
            ["☑", "Previous I-94 Records (Showing Timely Departures)", "Page 30"],
            ["☑", "Sister's Green Card Copy (Patricia Costa Thompson)", "Page 10"],
            ["☑", "Medical Documentation from Jackson Memorial Hospital", "Page 10"],
            ["☑", "Letter from Dr. Rebecca Martinez (Oncologist)", "Page 11"],
            ["☑", "Bank Statements (Checking Account - 6 months)", "Page 13"],
            ["☑", "Bank Statements (Savings Account - 6 months)", "Page 14"],
            ["☑", "Investment Portfolio Statements", "Page 15"],
            ["☑", "Brazilian Tax Return (2023)", "Page 16"],
            ["☑", "Business Ownership Documentation (CNPJ Registration)", "Page 17"],
            ["☑", "Business Financial Statements", "Page 18"],
            ["☑", "Letter from Business Partners Confirming Return Need", "Page 19"],
            ["☑", "Primary Residence Property Deed (R$ 1,450,000)", "Page 20"],
            ["☑", "Commercial Property Deed (R$ 2,300,000)", "Page 20"],
            ["☑", "Commercial Property Rental Agreement", "Page 21"],
            ["☑", "Property Tax Receipts (IPTU)", "Page 21"],
            ["☑", "Professional License (CRC/MG - CPA License)", "Page 22"],
            ["☑", "Return Flight Confirmation (LATAM Airlines)", "Page 23"],
            ["☑", "Letter from Sister (Patricia Costa Thompson)", "Page 24"],
            ["☑", "Letter from Husband (Carlos Eduardo Costa)", "Page 26"],
            ["☑", "Valid Health Insurance Policy", "Page 27"],
            ["☑", "Proof of Husband & Children in Brazil", "Page 27"],
        ]
        
        checklist_table = Table(checklist_data, colWidths=[0.5*inch, 4.5*inch, 1.5*inch])
        checklist_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(checklist_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Summary
        elements.append(Paragraph("<b>APPLICATION PACKAGE SUMMARY</b>", self.styles['CustomSubtitle']))
        
        summary_data = [
            ["CATEGORY", "COUNT", "STATUS"],
            ["Official Forms", "1", "Form I-539 Completed"],
            ["Identity Documents", "5", "Passport, Visa, I-94 Records"],
            ["Medical Documentation", "3", "Doctor's Letter, Hospital Records, Green Card"],
            ["Financial Evidence", "9", "Bank Statements, Tax Returns, Property Deeds"],
            ["Ties to Brazil", "8", "Business, Property, Family, Professional License"],
            ["Travel History", "3", "Previous I-94s, Compliance Record, Return Flight"],
            ["Supporting Letters", "2", "From Sister and Husband"],
            ["<b>TOTAL DOCUMENTS</b>", "<b>31</b>", "<b>Complete Package</b>"],
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 1.5*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8eaf6')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Certification
        elements.append(Paragraph("<b>APPLICANT CERTIFICATION</b>", self.styles['CustomSubtitle']))
        
        certification_text = f"""
I, {self.data.applicant['full_name']}, certify under penalty of perjury under the laws of the 
United States that:
<br/><br/>
1. All information provided in this application and supporting documents is true and correct to 
the best of my knowledge.
<br/><br/>
2. All documents submitted are authentic and have not been altered or falsified.
<br/><br/>
3. I understand that any false statements or documents may result in denial of this application 
and potential immigration consequences.
<br/><br/>
4. I have read and understood all questions in Form I-539 and have answered them truthfully.
<br/><br/>
5. I authorize USCIS to verify any information provided in this application.
<br/><br/><br/><br/>
_____________________________<br/>
{self.data.applicant['full_name']}<br/>
Applicant Signature<br/>
Date: {self.data.case_info['application_date']}
        """
        
        elements.append(Paragraph(certification_text, self.styles['JustifiedBody']))
        
        return elements


def main():
    """Função principal"""
    print("\n" + "="*80)
    print("B-2 TOURIST VISA EXTENSION PACKAGE GENERATOR")
    print("="*80)
    
    # Criar gerador
    generator = B2ExtensionPackageGenerator()
    
    # Gerar pacote completo
    output_path = generator.generate_complete_package()
    
    if output_path:
        print("\n" + "="*80)
        print("✅ SUCESSO!")
        print("="*80)
        print(f"\nPacote B-2 Extension gerado com sucesso!")
        print(f"Arquivo: {output_path}")
        print(f"\n🌐 O arquivo está disponível para download")
        print(f"   URL: /api/b2-extension-demo")
    else:
        print("\n❌ ERRO: Não foi possível gerar o pacote")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
