"""
EB-1A Extraordinary Ability Specialist Agent
Especialista em EB-1A para indivíduos com habilidade extraordinária
"""

from typing import Dict, Any, List
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from visa_specialists.base_agent import BaseVisaAgent


class EB1AAgent(BaseVisaAgent):
    """Agente especialista em EB-1A (Extraordinary Ability)"""
    
    @property
    def VISA_TYPE(self) -> str:
        return "EB-1A"
    
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
            "Comprehensive CV/Resume",
            "Evidence of One-Time Achievement OR 3+ of 10 Criteria",
            "Major International Award Evidence (if applicable)",
            "Membership in Associations",
            "Published Material About You",
            "Judging Work of Others",
            "Original Contributions of Major Significance",
            "Scholarly Articles",
            "Work Displayed at Exhibitions",
            "Leading/Critical Role Evidence",
            "High Salary/Remuneration",
            "Commercial Success Evidence",
            "Expert Opinion Letters",
            "Letters of Recommendation (8-10)",
        ]
    
    @property
    def FORBIDDEN_DOCUMENTS(self) -> List[str]:
        return [
            "Labor Certification (not required for EB-1A)",
            "Job Offer (not required for EB-1A)",
        ]
    
    def __init__(self):
        agent_dir = Path(__file__).parent
        super().__init__(agent_dir)
        
        if not self.lessons_file.exists():
            self._initialize_lessons()
    
    def _initialize_lessons(self):
        """Inicializa lições EB-1A"""
        initial_lessons = """# Lições Aprendidas - EB-1A Agent

## [10 Criteria] CRÍTICO

**✅ Deve atender 3 dos 10 critérios:**
1. Evidence of receipt of lesser nationally or internationally recognized prizes or awards
2. Evidence of membership in associations that require outstanding achievements
3. Evidence of published material about you
4. Evidence of participation as a judge of others' work
5. Evidence of original contributions of major significance
6. Evidence of authorship of scholarly articles
7. Evidence of work displayed at artistic exhibitions
8. Evidence of leading/critical role for distinguished organizations
9. Evidence of high salary or remuneration
10. Evidence of commercial success in performing arts

---

## [Sustained National/International Acclaim]

**✅ Deve demonstrar:**
- Sustained acclaim (not one-time)
- National or international recognition
- Rising to very top of field
- Small percentage with such acclaim

---

## [OR One-Time Major Award]

**✅ Alternativa aos 10 critérios:**
- Nobel Prize
- Oscar/Emmy/Grammy
- Olympic Medal
- Pulitzer Prize
- etc.

---

"""
        with open(self.lessons_file, 'w') as f:
            f.write(initial_lessons)
    
    def generate_package(self, applicant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gera pacote EB-1A completo com dados dinâmicos"""
        print(f"\n{'='*80}")
        print(f"🎯 EB-1A EXTRAORDINARY ABILITY AGENT - GERANDO PACOTE")
        print(f"{'='*80}\n")
        
        try:
            result = self._generate_with_dynamic_data(applicant_data)
            if result and result.get('success'):
                print(f"✅ Pacote EB-1A gerado com dados dinâmicos")
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
        """Gera pacote EB-1A usando dados reais do usuário"""
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet
        from datetime import datetime
        from pathlib import Path
        
        print("✅ Gerando pacote EB-1A com dados dinâmicos...")
        
        personal = applicant_data.get('personal_info', {})
        professional = applicant_data.get('professional_info', {})
        achievements = applicant_data.get('achievements', {})
        
        if not personal.get('full_name'):
            raise ValueError("Nome completo é obrigatório")
        
        output_dir = Path('/tmp/visa_packages')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        sanitized_name = personal.get('full_name', 'applicant').replace(' ', '_')
        output_file = output_dir / f'EB1A_Extraordinary_{sanitized_name}_{timestamp}.pdf'
        
        doc = SimpleDocTemplate(str(output_file), pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title Page
        story.append(Paragraph("EB-1A EXTRAORDINARY ABILITY PETITION", styles['Title']))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(f"Form I-140 Immigrant Petition", styles['Heading2']))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(f"Beneficiary: {personal.get('full_name', 'N/A')}", styles['Normal']))
        story.append(Paragraph(f"Field of Extraordinary Ability: {professional.get('field', 'N/A')}", styles['Normal']))
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
        
        story.append(Paragraph(f"<b>RE: Form I-140, EB-1A Extraordinary Ability Petition</b>", styles['Normal']))
        story.append(Paragraph(f"<b>Beneficiary: {personal.get('full_name', 'N/A')}</b>", styles['Normal']))
        story.append(Paragraph(f"<b>Field: {professional.get('field', 'N/A')}</b>", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        cover_text = f"""
        Dear USCIS Officer,
        
        This petition seeks classification of {personal.get('full_name', 'N/A')} under the 
        Employment-Based First Preference category (EB-1A) as an alien of extraordinary ability 
        in the field of {professional.get('field', 'their field')}.
        
        <b>Extraordinary Ability:</b><br/>
        {personal.get('full_name', 'N/A')} has risen to the very top of their field and has 
        sustained national and international acclaim. This petition demonstrates that the 
        beneficiary meets at least three of the ten regulatory criteria for extraordinary ability.
        
        <b>Notable Achievements:</b><br/>
        - {achievements.get('awards', '0')} significant awards and honors<br/>
        - {achievements.get('publications', '0')} publications in major media<br/>
        - {achievements.get('citations', '0')} citations to scholarly work<br/>
        - {achievements.get('judging', '0')} instances of judging others' work<br/>
        - Leading role in {achievements.get('organizations', 'distinguished organizations')}
        
        <b>Evidence of Sustained Acclaim:</b>
        
        This petition includes comprehensive documentation demonstrating:
        
        1. <b>Receipt of Awards:</b> Evidence of nationally and internationally recognized 
        prizes and awards for excellence in the field.
        
        2. <b>Membership in Elite Associations:</b> Membership in associations that require 
        outstanding achievements as judged by recognized experts.
        
        3. <b>Published Material About Beneficiary:</b> Published material in professional or 
        major trade publications or major media about the beneficiary's work.
        
        4. <b>Judging Others' Work:</b> Evidence of participation as a judge of the work of 
        others in the same or allied field.
        
        5. <b>Original Contributions:</b> Evidence of original scientific, scholarly, artistic, 
        athletic, or business-related contributions of major significance.
        
        6. <b>Scholarly Articles:</b> Evidence of authorship of scholarly articles in 
        professional journals or major media.
        
        7. <b>High Remuneration:</b> Evidence of commanding a high salary or significantly 
        high remuneration in relation to others in the field.
        
        The beneficiary has achieved sustained national and international acclaim and is 
        recognized internationally as being at the very top of their field. Their continued 
        work in the United States will substantially benefit the nation.
        
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
        
        # Professional Achievement Statement
        story.append(Paragraph("STATEMENT OF EXTRAORDINARY ABILITY", styles['Heading1']))
        story.append(Spacer(1, 0.2*inch))
        
        user_story = applicant_data.get('user_story', '')
        if user_story:
            story.append(Paragraph(user_story, styles['Normal']))
        else:
            story.append(Paragraph(f"""
            {personal.get('full_name', 'The beneficiary')} has achieved extraordinary ability 
            in the field of {professional.get('field', 'their discipline')}, demonstrated by 
            sustained national and international acclaim. Their work has been recognized at 
            the highest levels of their profession, and they have risen to the very top of 
            their field.
            
            The beneficiary's contributions have had a significant impact on {professional.get('field', 'the field')}, 
            and their continued work in the United States will provide substantial benefit to the nation.
            """, styles['Normal']))
        
        doc.build(story)
        
        print(f"✅ Pacote EB-1A gerado: {output_file}")
        
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
