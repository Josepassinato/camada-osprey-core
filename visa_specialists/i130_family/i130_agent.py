"""
I-130 Family-Based Immigration Specialist Agent
Especialista em petições familiares I-130
"""

from typing import Dict, Any, List
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from visa_specialists.base_agent import BaseVisaAgent


class I130FamilyAgent(BaseVisaAgent):
    """Agente especialista em petições I-130 (Family-Based)"""
    
    @property
    def VISA_TYPE(self) -> str:
        return "I-130"
    
    @property
    def REQUIRED_FORMS(self) -> List[str]:
        return [
            "I-130",  # Petition for Alien Relative
        ]
    
    @property
    def REQUIRED_DOCUMENTS(self) -> List[str]:
        return [
            "Form I-130 (Completed)",
            "Cover Letter",
            "Petitioner's Proof of Status (US Citizen or Green Card)",
            "Birth Certificate (Beneficiary)",
            "Marriage Certificate (if spouse)",
            "Divorce/Death Certificates (if applicable)",
            "Passport Copies",
            "Two Passport Photos (each person)",
            "Proof of Relationship",
            "Financial Support Evidence (I-864)",
            "Police Clearance Certificates",
            "Medical Examination",
        ]
    
    @property
    def FORBIDDEN_DOCUMENTS(self) -> List[str]:
        return [
            "Employment Authorization (unless concurrent filing)",
            "Work Visa Documents",
            "Student Visa Documents",
        ]
    
    def __init__(self):
        agent_dir = Path(__file__).parent
        super().__init__(agent_dir)
        
        if not self.lessons_file.exists():
            self._initialize_lessons()
    
    def _initialize_lessons(self):
        """Inicializa lições I-130"""
        initial_lessons = """# Lições Aprendidas - I-130 Family Agent

## [Relationship Proof] CRÍTICO

**✅ Documentação de relacionamento é essencial:**
- Marriage certificate para cônjuges
- Birth certificate para filhos/pais
- Fotos, cartas, documentos conjuntos
- Histórico de comunicação

---

## [Bona Fide Marriage]

**✅ Para casamentos:**
- Comprovar relacionamento genuíno
- Joint bank accounts, lease, utilities
- Fotos de casamento e vida juntos
- Cartas de amigos/família

---

"""
        with open(self.lessons_file, 'w') as f:
            f.write(initial_lessons)
    
    def generate_package(self, applicant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gera pacote I-130 completo com dados dinâmicos"""
        print(f"\n{'='*80}")
        print(f"🎯 I-130 FAMILY AGENT - GERANDO PACOTE")
        print(f"{'='*80}\n")
        
        try:
            result = self._generate_with_dynamic_data(applicant_data)
            if result and result.get('success'):
                print(f"✅ Pacote I-130 gerado com dados dinâmicos")
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
        """Gera pacote I-130 usando dados reais do usuário"""
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet
        from datetime import datetime
        from pathlib import Path
        
        print("✅ Gerando pacote I-130 com dados dinâmicos...")
        
        personal = applicant_data.get('personal_info', {})
        relationship = applicant_data.get('relationship_info', {})
        petitioner = applicant_data.get('petitioner_info', {})
        
        if not personal.get('full_name'):
            raise ValueError("Nome completo é obrigatório")
        
        output_dir = Path('/tmp/visa_packages')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        sanitized_name = personal.get('full_name', 'applicant').replace(' ', '_')
        output_file = output_dir / f'I130_Family_{sanitized_name}_{timestamp}.pdf'
        
        doc = SimpleDocTemplate(str(output_file), pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title Page
        story.append(Paragraph("I-130 PETITION FOR ALIEN RELATIVE", styles['Title']))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(f"Family-Based Immigration Petition", styles['Heading2']))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(f"Petitioner: {petitioner.get('full_name', 'N/A')}", styles['Normal']))
        story.append(Paragraph(f"Beneficiary: {personal.get('full_name', 'N/A')}", styles['Normal']))
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
        
        story.append(Paragraph(f"<b>RE: Form I-130, Petition for Alien Relative</b>", styles['Normal']))
        story.append(Paragraph(f"<b>Petitioner: {petitioner.get('full_name', 'N/A')}</b>", styles['Normal']))
        story.append(Paragraph(f"<b>Beneficiary: {personal.get('full_name', 'N/A')}</b>", styles['Normal']))
        story.append(Paragraph(f"<b>Relationship: {relationship.get('relationship_type', 'N/A')}</b>", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        cover_text = f"""
        Dear USCIS Officer,
        
        I, {petitioner.get('full_name', 'N/A')}, am filing this Form I-130 petition on behalf of my 
        {relationship.get('relationship_type', 'relative').lower()}, {personal.get('full_name', 'N/A')}.
        
        <b>Petitioner Status:</b><br/>
        {petitioner.get('status', 'U.S. Citizen')}
        
        <b>Relationship:</b><br/>
        I am the {relationship.get('petitioner_role', 'spouse/parent/child')} of the beneficiary. 
        Our relationship is genuine and well-documented through the evidence provided in this petition.
        
        <b>Supporting Evidence:</b><br/>
        This petition includes comprehensive documentation proving our relationship, including 
        marriage certificates, birth certificates, joint financial records, photographs, 
        and statements from family and friends.
        
        <b>Intent:</b><br/>
        The purpose of this petition is to reunite our family and allow {personal.get('full_name', 'N/A')} 
        to reside permanently in the United States with me.
        
        Thank you for your consideration of this petition.
        
        Respectfully,<br/>
        {petitioner.get('full_name', 'N/A')}
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
        
        # Relationship Evidence
        story.append(Paragraph("RELATIONSHIP EVIDENCE", styles['Heading1']))
        story.append(Spacer(1, 0.2*inch))
        
        user_story = applicant_data.get('user_story', '')
        if user_story:
            story.append(Paragraph(user_story, styles['Normal']))
        else:
            story.append(Paragraph(f"""
            This petition is filed to establish the qualifying relationship between 
            {petitioner.get('full_name', 'N/A')} and {personal.get('full_name', 'N/A')}. 
            
            The relationship is supported by official government documents, personal testimony, 
            and evidence of shared life experiences.
            """, styles['Normal']))
        
        doc.build(story)
        
        print(f"✅ Pacote I-130 gerado: {output_file}")
        
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
            'petitioner': petitioner.get('full_name', 'N/A'),
            'beneficiary': personal.get('full_name', 'N/A')
        }
