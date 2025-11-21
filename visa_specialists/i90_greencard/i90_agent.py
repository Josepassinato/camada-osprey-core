"""
I-90 Green Card Renewal/Replacement Specialist Agent
Especialista em renovação/substituição de Green Card
"""

from typing import Dict, Any, List
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from visa_specialists.base_agent import BaseVisaAgent


class I90GreenCardAgent(BaseVisaAgent):
    """Agente especialista em I-90 (Green Card Renewal/Replacement)"""
    
    @property
    def VISA_TYPE(self) -> str:
        return "I-90"
    
    @property
    def REQUIRED_FORMS(self) -> List[str]:
        return [
            "I-90",  # Application to Replace Permanent Resident Card
        ]
    
    @property
    def REQUIRED_DOCUMENTS(self) -> List[str]:
        return [
            "Form I-90 (Completed)",
            "Cover Letter",
            "Copy of Current/Expired Green Card (front and back)",
            "Two Passport Photos",
            "Copy of Passport (biographical page)",
            "Evidence for Replacement Reason",
            "Filing Fee Payment",
        ]
    
    @property
    def FORBIDDEN_DOCUMENTS(self) -> List[str]:
        return [
            "Citizenship documents (N-400 is separate)",
        ]
    
    def __init__(self):
        agent_dir = Path(__file__).parent
        super().__init__(agent_dir)
        
        if not self.lessons_file.exists():
            self._initialize_lessons()
    
    def _initialize_lessons(self):
        """Inicializa lições I-90"""
        initial_lessons = """# Lições Aprendidas - I-90 Green Card Agent

## [Renewal vs Replacement]

**✅ Diferentes razões para I-90:**
- Card expiring/expired
- Lost or stolen card
- Damaged or destroyed card
- Name change
- Date of birth error
- Card issued before 14th birthday

---

## [Timing]

**✅ Quando aplicar:**
- 6 months before expiration (renewal)
- Immediately if lost/stolen/damaged
- Before card expires to avoid complications

---

"""
        with open(self.lessons_file, 'w') as f:
            f.write(initial_lessons)
    
    def generate_package(self, applicant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gera pacote I-90 completo com dados dinâmicos"""
        print(f"\n{'='*80}")
        print(f"🎯 I-90 GREEN CARD AGENT - GERANDO PACOTE")
        print(f"{'='*80}\n")
        
        try:
            result = self._generate_with_dynamic_data(applicant_data)
            if result and result.get('success'):
                print(f"✅ Pacote I-90 gerado com dados dinâmicos")
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
        """Gera pacote I-90 usando dados reais do usuário"""
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet
        from datetime import datetime
        from pathlib import Path
        
        print("✅ Gerando pacote I-90 com dados dinâmicos...")
        
        personal = applicant_data.get('personal_info', {})
        greencard_info = applicant_data.get('greencard_info', {})
        
        if not personal.get('full_name'):
            raise ValueError("Nome completo é obrigatório")
        
        output_dir = Path('/tmp/visa_packages')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        sanitized_name = personal.get('full_name', 'applicant').replace(' ', '_')
        output_file = output_dir / f'I90_GreenCard_{sanitized_name}_{timestamp}.pdf'
        
        doc = SimpleDocTemplate(str(output_file), pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title Page
        story.append(Paragraph("I-90 APPLICATION TO REPLACE PERMANENT RESIDENT CARD", styles['Title']))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(f"Green Card Renewal/Replacement", styles['Heading2']))
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
        
        story.append(Paragraph(f"<b>RE: Form I-90, Application to Replace Permanent Resident Card</b>", styles['Normal']))
        story.append(Paragraph(f"<b>Applicant: {personal.get('full_name', 'N/A')}</b>", styles['Normal']))
        story.append(Paragraph(f"<b>A-Number: {greencard_info.get('alien_number', 'N/A')}</b>", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        reason = greencard_info.get('reason', 'renewal')
        reason_text = {
            'renewal': 'my Green Card is expiring or has expired',
            'lost': 'my Green Card was lost',
            'stolen': 'my Green Card was stolen',
            'damaged': 'my Green Card is damaged',
            'name_change': 'I legally changed my name',
            'error': 'there is an error on my Green Card'
        }.get(reason, 'I need to replace my Green Card')
        
        cover_text = f"""
        Dear USCIS Officer,
        
        I am submitting this Form I-90 application to replace my Permanent Resident Card because 
        {reason_text}.
        
        <b>Current Green Card Information:</b><br/>
        Card Number: {greencard_info.get('card_number', 'N/A')}<br/>
        Expiration Date: {greencard_info.get('expiration_date', 'N/A')}<br/>
        A-Number: {greencard_info.get('alien_number', 'N/A')}
        
        <b>Reason for Replacement:</b><br/>
        {greencard_info.get('detailed_reason', reason_text.capitalize())}
        
        <b>Permanent Resident Status:</b><br/>
        I have maintained my permanent resident status and have not abandoned my residence 
        in the United States. I continue to reside at the address listed in this application.
        
        I have included all required documentation and fees with this application.
        
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
            ("<b>GREEN CARD INFORMATION</b>", ""),
            ("A-Number:", greencard_info.get('alien_number', 'N/A')),
            ("Card Number:", greencard_info.get('card_number', 'N/A')),
            ("Expiration Date:", greencard_info.get('expiration_date', 'N/A')),
            ("Date Became Permanent Resident:", greencard_info.get('date_became_pr', 'N/A')),
            ("Reason for Application:", reason.capitalize()),
        ]
        
        for label, value in info:
            if label:
                story.append(Paragraph(f"{label} {value}", styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
            else:
                story.append(Spacer(1, 0.2*inch))
        
        doc.build(story)
        
        print(f"✅ Pacote I-90 gerado: {output_file}")
        
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
            'reason': reason
        }
