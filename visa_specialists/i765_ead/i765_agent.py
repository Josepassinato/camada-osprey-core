"""
I-765 Employment Authorization Document (EAD) Specialist Agent
Especialista em autorizações de trabalho I-765
"""

from typing import Dict, Any, List
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from visa_specialists.base_agent import BaseVisaAgent


class I765EADAgent(BaseVisaAgent):
    """Agente especialista em EAD (Employment Authorization Document)"""
    
    @property
    def VISA_TYPE(self) -> str:
        return "I-765"
    
    @property
    def REQUIRED_FORMS(self) -> List[str]:
        return [
            "I-765",  # Application for Employment Authorization
        ]
    
    @property
    def REQUIRED_DOCUMENTS(self) -> List[str]:
        return [
            "Form I-765 (Completed)",
            "Cover Letter",
            "Two Passport Photos",
            "Copy of I-94 (Arrival/Departure Record)",
            "Copy of Passport (biographical page)",
            "Copy of Previous EAD (if renewal)",
            "Evidence of Eligible Category",
            "Supporting Documents for Category",
            "Filing Fee Payment",
        ]
    
    @property
    def FORBIDDEN_DOCUMENTS(self) -> List[str]:
        return [
            "Documents unrelated to employment authorization",
        ]
    
    def __init__(self):
        agent_dir = Path(__file__).parent
        super().__init__(agent_dir)
        
        if not self.lessons_file.exists():
            self._initialize_lessons()
    
    def _initialize_lessons(self):
        """Inicializa lições I-765"""
        initial_lessons = """# Lições Aprendidas - I-765 EAD Agent

## [Eligibility Category] CRÍTICO

**✅ Categoria de elegibilidade deve estar clara:**
- (c)(3) F-1 OPT Students
- (c)(9) Adjustment of Status pending
- (c)(26) Spouse of E or L visa holder
- (a)(12) Asylee
- etc.

---

## [Supporting Evidence]

**✅ Documentos variam por categoria:**
- F-1 OPT: I-20 with OPT recommendation
- AOS: Receipt notice of I-485
- Spouse: Copy of principal's visa

---

"""
        with open(self.lessons_file, 'w') as f:
            f.write(initial_lessons)
    
    def generate_package(self, applicant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gera pacote I-765 completo com dados dinâmicos"""
        print(f"\n{'='*80}")
        print(f"🎯 I-765 EAD AGENT - GERANDO PACOTE")
        print(f"{'='*80}\n")
        
        try:
            result = self._generate_with_dynamic_data(applicant_data)
            if result and result.get('success'):
                print(f"✅ Pacote I-765 gerado com dados dinâmicos")
                return result
        except Exception as e:
            print(f"⚠️ Erro ao gerar com dados dinâmicos: {e}")
            import traceback
            traceback.print_exc()
        
        return {
            'package_path': None,
            'pages': 0,
            'size_kb': 0,
            'documents': self.REQUIRED_DOCUMENTS
        }
    
    def _generate_with_dynamic_data(self, applicant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gera pacote I-765 usando dados reais do usuário"""
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet
        from datetime import datetime
        from pathlib import Path
        
        print("✅ Gerando pacote I-765 com dados dinâmicos...")
        
        personal = applicant_data.get('personal_info', {})
        ead_info = applicant_data.get('ead_data', {})
        immigration = applicant_data.get('immigration_info', {})
        
        if not personal.get('full_name'):
            raise ValueError("Nome completo é obrigatório")
        
        output_dir = Path('/tmp/visa_packages')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        sanitized_name = personal.get('full_name', 'applicant').replace(' ', '_')
        output_file = output_dir / f'I765_EAD_{sanitized_name}_{timestamp}.pdf'
        
        doc = SimpleDocTemplate(str(output_file), pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title Page
        story.append(Paragraph("I-765 APPLICATION FOR EMPLOYMENT AUTHORIZATION", styles['Title']))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(f"Employment Authorization Document (EAD)", styles['Heading2']))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(f"Applicant: {personal.get('full_name', 'N/A')}", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
        story.append(PageBreak())
        
        # Cover Letter
        story.append(Paragraph("COVER LETTER", styles['Heading1']))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(f"{datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("U.S. Citizenship and Immigration Services", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph(f"<b>RE: Form I-765, Application for Employment Authorization</b>", styles['Normal']))
        story.append(Paragraph(f"<b>Applicant: {personal.get('full_name', 'N/A')}</b>", styles['Normal']))
        story.append(Paragraph(f"<b>Category: {ead_info.get('category', 'N/A')}</b>", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        cover_text = f"""
        Dear USCIS Officer,
        
        I am submitting this Form I-765 application to request employment authorization 
        in the United States.
        
        <b>Eligibility Category:</b><br/>
        {ead_info.get('category', 'N/A')} - {ead_info.get('category_description', 'Employment authorization')}
        
        <b>Current Status:</b><br/>
        {immigration.get('current_status', 'N/A')}
        
        <b>Reason for Application:</b><br/>
        {ead_info.get('reason', 'I am eligible for employment authorization under the specified category and wish to work legally in the United States.')}
        
        <b>Supporting Documentation:</b><br/>
        I have included all required documentation to support this application, including 
        proof of my eligible status and all necessary forms and fees.
        
        Thank you for your consideration.
        
        Respectfully,<br/>
        {personal.get('full_name', 'N/A')}
        """
        
        story.append(Paragraph(cover_text, styles['Normal']))
        story.append(PageBreak())
        
        # Document Checklist
        story.append(Paragraph("DOCUMENT CHECKLIST", styles['Heading1']))
        story.append(Spacer(1, 0.2*inch))
        
        for item in self.REQUIRED_DOCUMENTS:
            story.append(Paragraph(f"✓ {item}", styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
        
        story.append(PageBreak())
        
        # Applicant Information
        story.append(Paragraph("APPLICANT INFORMATION", styles['Heading1']))
        story.append(Spacer(1, 0.2*inch))
        
        info = [
            ("Full Name:", personal.get('full_name', 'N/A')),
            ("Date of Birth:", personal.get('date_of_birth', 'N/A')),
            ("Country of Birth:", personal.get('country_of_birth', 'N/A')),
            ("Current Address:", personal.get('current_address', 'N/A')),
            ("Phone:", personal.get('phone', 'N/A')),
            ("Email:", personal.get('email', 'N/A')),
            ("", ""),
            ("<b>IMMIGRATION STATUS</b>", ""),
            ("Current Status:", immigration.get('current_status', 'N/A')),
            ("A-Number:", immigration.get('alien_number', 'N/A')),
            ("Status Expiration:", immigration.get('status_expiration', 'N/A')),
            ("", ""),
            ("<b>EAD APPLICATION</b>", ""),
            ("Eligibility Category:", ead_info.get('category', 'N/A')),
            ("Application Type:", ead_info.get('application_type', 'Initial/Renewal/Replacement')),
        ]
        
        for label, value in info:
            if label:
                story.append(Paragraph(f"{label} {value}", styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
            else:
                story.append(Spacer(1, 0.2*inch))
        
        doc.build(story)
        
        print(f"✅ Pacote I-765 gerado: {output_file}")
        
        from PyPDF2 import PdfReader
        reader = PdfReader(str(output_file))
        page_count = len(reader.pages)
        
        return {
            'success': True,
            'output_pdf': str(output_file),
            'package_path': str(output_file),
            'pages': page_count,
            'size_kb': output_file.stat().st_size / 1024,
            'generated_with': 'dynamic_data',
            'applicant_name': personal.get('full_name', 'N/A'),
            'category': ead_info.get('category', 'N/A')
        }
