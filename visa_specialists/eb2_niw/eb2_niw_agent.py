"""
EB-2 NIW (National Interest Waiver) Specialist Agent
Especialista em EB-2 NIW para Green Card baseado em interesse nacional
"""

from typing import Dict, Any, List
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from visa_specialists.base_agent import BaseVisaAgent


class EB2NIWAgent(BaseVisaAgent):
    """Agente especialista em EB-2 NIW (National Interest Waiver)"""
    
    @property
    def VISA_TYPE(self) -> str:
        return "EB-2 NIW"
    
    @property
    def REQUIRED_FORMS(self) -> List[str]:
        return [
            "I-140",  # Immigrant Petition for Alien Worker
        ]
    
    @property
    def REQUIRED_DOCUMENTS(self) -> List[str]:
        return [
            "Form I-140 (Completed)",
            "Cover Letter",
            "Personal Statement",
            "Curriculum Vitae (CV/Resume)",
            "Educational Credentials (Degrees, Transcripts)",
            "Evidence of Advanced Degree or Exceptional Ability",
            "Evidence of National Interest",
            "Letters of Recommendation (5-8)",
            "Publications and Citations",
            "Patent Documentation",
            "Awards and Recognition",
            "Professional Memberships",
            "Evidence of Impact in Field",
            "Media Coverage",
            "Expert Opinion Letters",
        ]
    
    @property
    def FORBIDDEN_DOCUMENTS(self) -> List[str]:
        return [
            "Labor Certification (PERM) - NIW waives this requirement",
        ]
    
    def __init__(self):
        agent_dir = Path(__file__).parent
        super().__init__(agent_dir)
        
        if not self.lessons_file.exists():
            self._initialize_lessons()
    
    def _initialize_lessons(self):
        """Inicializa lições EB-2 NIW"""
        initial_lessons = """# Lições Aprendidas - EB-2 NIW Agent

## [Three-Prong Test (Matter of Dhanasar)]

**✅ Deve satisfazer todos os 3 critérios:**
1. Proposed endeavor has substantial merit and national importance
2. You are well positioned to advance the proposed endeavor
3. On balance, it would be beneficial to waive job offer and labor certification

---

## [Evidence Requirements]

**✅ Forte documentação necessária:**
- Advanced degree (Master's or higher) OR Bachelor's + 5 years experience
- Publications, citations, patents
- Letters from independent experts
- Evidence of impact on field/national interest

---

"""
        with open(self.lessons_file, 'w') as f:
            f.write(initial_lessons)
    
    def generate_package(self, applicant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gera pacote EB-2 NIW completo com dados dinâmicos"""
        print(f"\n{'='*80}")
        print(f"🎯 EB-2 NIW AGENT - GERANDO PACOTE")
        print(f"{'='*80}\n")
        
        try:
            result = self._generate_with_dynamic_data(applicant_data)
            if result and result.get('success'):
                print(f"✅ Pacote EB-2 NIW gerado com dados dinâmicos")
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
        """Gera pacote EB-2 NIW usando dados reais do usuário"""
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet
        from datetime import datetime
        from pathlib import Path
        
        print("✅ Gerando pacote EB-2 NIW com dados dinâmicos...")
        
        personal = applicant_data.get('personal_info', {})
        professional = applicant_data.get('professional_info', {})
        education = applicant_data.get('education_info', {})
        
        if not personal.get('full_name'):
            raise ValueError("Nome completo é obrigatório")
        
        output_dir = Path('/tmp/visa_packages')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        sanitized_name = personal.get('full_name', 'applicant').replace(' ', '_')
        output_file = output_dir / f'EB2_NIW_{sanitized_name}_{timestamp}.pdf'
        
        doc = SimpleDocTemplate(str(output_file), pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title Page
        story.append(Paragraph("EB-2 NATIONAL INTEREST WAIVER PETITION", styles['Title']))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(f"Form I-140 Immigrant Petition", styles['Heading2']))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(f"Beneficiary: {personal.get('full_name', 'N/A')}", styles['Normal']))
        story.append(Paragraph(f"Field of Expertise: {professional.get('field', 'N/A')}", styles['Normal']))
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
        
        story.append(Paragraph(f"<b>RE: Form I-140, EB-2 National Interest Waiver Petition</b>", styles['Normal']))
        story.append(Paragraph(f"<b>Beneficiary: {personal.get('full_name', 'N/A')}</b>", styles['Normal']))
        story.append(Paragraph(f"<b>Field: {professional.get('field', 'N/A')}</b>", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        cover_text = f"""
        Dear USCIS Officer,
        
        This petition seeks classification of {personal.get('full_name', 'N/A')} as an alien 
        of exceptional ability in the field of {professional.get('field', 'their field')}, 
        with a request for a National Interest Waiver under the Employment-Based Second 
        Preference category (EB-2 NIW).
        
        <b>Qualifications:</b><br/>
        {personal.get('full_name', 'N/A')} holds {education.get('highest_degree', 'an advanced degree')} 
        in {education.get('field_of_study', 'their field')} from {education.get('institution', 'a recognized institution')}.
        
        <b>Professional Achievements:</b><br/>
        - {professional.get('years_experience', '10+')} years of professional experience<br/>
        - {professional.get('publications', '0')} peer-reviewed publications<br/>
        - {professional.get('citations', '0')} citations to work<br/>
        - {professional.get('patents', '0')} patents granted<br/>
        - Significant contributions to {professional.get('field', 'the field')}
        
        <b>National Interest Justification (Matter of Dhanasar):</b>
        
        1. <b>Substantial Merit and National Importance:</b> The beneficiary's work in 
        {professional.get('field', 'their field')} has substantial merit and national importance 
        to the United States, as evidenced by {professional.get('impact_evidence', 'their contributions')}.
        
        2. <b>Well Positioned to Advance:</b> The beneficiary is exceptionally well positioned 
        to advance their proposed endeavor, as demonstrated by their education, experience, 
        publications, and recognition in the field.
        
        3. <b>Beneficial to Waive Requirements:</b> On balance, it would be beneficial to the 
        United States to waive the job offer and labor certification requirements.
        
        This petition includes comprehensive documentation supporting the beneficiary's 
        qualifications and the national interest served by granting this waiver.
        
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
        
        # Professional Summary
        story.append(Paragraph("PROFESSIONAL SUMMARY", styles['Heading1']))
        story.append(Spacer(1, 0.2*inch))
        
        user_story = applicant_data.get('user_story', '')
        if user_story:
            story.append(Paragraph(user_story, styles['Normal']))
        else:
            story.append(Paragraph(f"""
            {personal.get('full_name', 'The beneficiary')} is a highly accomplished professional 
            in the field of {professional.get('field', 'their discipline')} with extensive experience 
            and significant contributions to the field. Their work has garnered recognition from peers 
            and has advanced the state of knowledge in critical areas of national interest to the 
            United States.
            """, styles['Normal']))
        
        doc.build(story)
        
        print(f"✅ Pacote EB-2 NIW gerado: {output_file}")
        
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
            'field': professional.get('field', 'N/A')
        }
