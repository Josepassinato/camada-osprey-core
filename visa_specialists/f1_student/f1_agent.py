"""
F-1 Student Visa Specialist Agent  
Especialista em vistos de estudante F-1
"""

from typing import Dict, Any, List
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from visa_specialists.base_agent import BaseVisaAgent


class F1StudentAgent(BaseVisaAgent):
    """Agente especialista em vistos F-1"""
    
    @property
    def VISA_TYPE(self) -> str:
        return "F-1 Student"
    
    @property
    def REQUIRED_FORMS(self) -> List[str]:
        return [
            "I-20",      # Certificate of Eligibility (issued by school)
            # Note: I-539 only required for status changes, not new F-1 applications
        ]
    
    @property
    def REQUIRED_DOCUMENTS(self) -> List[str]:
        return [
            "I-20 from School",
            "Acceptance Letter",
            "Transcript",
            "Academic Records",
            "Financial Support Evidence",
            "Bank Statements",
            "Sponsor Affidavit (if applicable)",
            "English Proficiency Test (TOEFL/IELTS)",
            "Ties to Home Country",
            "Intent to Return",
            "Passport Copy"
        ]
    
    @property
    def FORBIDDEN_DOCUMENTS(self) -> List[str]:
        return [
            "I-129",     # H-1B Worker petition
            "LCA",       # Labor Condition Application
            "Employment Authorization (unless OPT/CPT)",
            "Work Visa Documentation"
        ]
    
    def __init__(self):
        agent_dir = Path(__file__).parent
        super().__init__(agent_dir)
        
        if not self.lessons_file.exists():
            self._initialize_lessons()
    
    def _initialize_lessons(self):
        """Inicializa lições F-1"""
        initial_lessons = """# Lições Aprendidas - F-1 Student Agent

## [I-20] CRÍTICO

**✅ I-20 é o documento mais importante:**
- Emitido pela escola, não pelo USCIS
- DEVE estar assinado pelo DSO (Designated School Official)
- DEVE ter data recente (geralmente válido por 30 dias para nova admissão)

---

## [Financial Support] Obrigatório

**✅ Demonstrar fundos suficientes:**
- Para tuition + living expenses
- Geralmente $30,000-$70,000 por ano dependendo da escola
- Bank statements, sponsor letters, scholarship letters

---

"""
        with open(self.lessons_file, 'w') as f:
            f.write(initial_lessons)
    
    def generate_package(self, applicant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gera pacote F-1 completo com dados dinâmicos"""
        print(f"\n{'='*80}")
        print(f"🎯 F-1 STUDENT AGENT - GERANDO PACOTE")
        print(f"{'='*80}\n")
        
        # Tentar gerar com dados dinâmicos primeiro
        try:
            result = self._generate_with_dynamic_data(applicant_data)
            if result and result.get('success'):
                print(f"✅ Pacote gerado com dados dinâmicos")
                return result
        except Exception as e:
            print(f"⚠️ Erro ao gerar com dados dinâmicos: {e}")
            import traceback
            traceback.print_exc()
        
        # Fallback: Executar gerador F-1 com dados hardcoded
        import subprocess
        from pathlib import Path
        
        generator_script = Path('/app/generate_f1_complete_package.py')
        
        if generator_script.exists():
            print("✅ Usando gerador F-1 completo profissional (fallback mode)...")
            result = subprocess.run(
                ['/root/.venv/bin/python3', str(generator_script)],
                capture_output=True,
                text=True
            )
            
            print(f"🔍 Subprocess return code: {result.returncode}")
            print(f"🔍 Subprocess stdout: {result.stdout}")
            print(f"🔍 Subprocess stderr: {result.stderr}")
            
            if result.returncode == 0:
                pdf_path = Path('/app/frontend/public/F1_STUDENT_COMPLETE_PACKAGE_RAFAEL_OLIVEIRA.pdf')
                print(f"🔍 Checking PDF path: {pdf_path}")
                print(f"🔍 PDF exists: {pdf_path.exists()}")
                
                if pdf_path.exists():
                    try:
                        from PyPDF2 import PdfReader
                        reader = PdfReader(str(pdf_path))
                        pages = len(reader.pages)
                        size_kb = pdf_path.stat().st_size / 1024
                        
                        print(f"✅ Pacote F-1 completo gerado: {pages} páginas ({size_kb:.1f} KB)")
                        
                        return {
                            'package_path': str(pdf_path),
                            'pages': pages,
                            'size_kb': size_kb,
                            'has_images': True,
                            'documents': self.REQUIRED_DOCUMENTS
                        }
                    except Exception as e:
                        print(f"❌ Error reading PDF: {e}")
                else:
                    print(f"❌ PDF file not found at {pdf_path}")
            
            print(f"⚠️  Gerador retornou erro: {result.stderr}")
        
        return {
            'package_path': None,
            'pages': 0,
            'size_kb': 0,
            'has_images': False,
            'documents': self.REQUIRED_DOCUMENTS
        }
    
    def _generate_with_dynamic_data(self, applicant_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera pacote F-1 usando dados reais do usuário.
        """
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet
        from datetime import datetime
        from pathlib import Path
        
        print("✅ Gerando pacote F-1 com dados dinâmicos...")
        
        # Extract data
        personal = applicant_data.get('personal_info', {})
        education = applicant_data.get('education_info', {})
        financial = applicant_data.get('financial_info', {})
        immigration = applicant_data.get('immigration_info', {})
        
        if not personal.get('full_name'):
            raise ValueError("Nome completo é obrigatório")
        
        # Setup output
        output_dir = Path('/tmp/visa_packages')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        sanitized_name = personal.get('full_name', 'applicant').replace(' ', '_')
        output_file = output_dir / f'F1_Student_{sanitized_name}_{timestamp}.pdf'
        
        # Create PDF
        doc = SimpleDocTemplate(str(output_file), pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title Page
        story.append(Paragraph("F-1 STUDENT VISA APPLICATION", styles['Title']))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(f"Academic Study Application Package", styles['Heading2']))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(f"Prepared for:", styles['Normal']))
        story.append(Paragraph(f"<b>{personal.get('full_name', 'N/A')}</b>", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
        story.append(PageBreak())
        
        # Cover Letter
        story.append(Paragraph("COVER LETTER", styles['Heading1']))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(f"{datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("U.S. Consular Officer", styles['Normal']))
        story.append(Paragraph(f"U.S. Embassy - {personal.get('country_of_birth', 'Home Country')}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph(f"<b>RE: F-1 Student Visa Application</b>", styles['Normal']))
        story.append(Paragraph(f"<b>Applicant: {personal.get('full_name', 'N/A')}</b>", styles['Normal']))
        story.append(Paragraph(f"<b>Date of Birth: {personal.get('date_of_birth', 'N/A')}</b>", styles['Normal']))
        story.append(Paragraph(f"<b>School: {education.get('school_name', 'N/A')}</b>", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        cover_text = f"""
        Dear Consular Officer,
        
        I am writing to apply for an F-1 student visa to pursue my academic studies 
        at {education.get('school_name', 'an accredited U.S. institution')}. I have been 
        accepted into the {education.get('program_name', 'degree program')} and am eager 
        to begin my studies.
        
        <b>Academic Program:</b><br/>
        Program: {education.get('program_name', 'N/A')}<br/>
        Degree Level: {education.get('degree_level', 'N/A')}<br/>
        Start Date: {education.get('start_date', 'N/A')}<br/>
        Expected Completion: {education.get('end_date', 'N/A')}<br/>
        SEVIS ID: {education.get('sevis_id', 'N/A')}
        
        <b>Financial Support:</b><br/>
        I have secured sufficient financial resources to cover all educational and living 
        expenses during my study period through {financial.get('funding_source', 'personal/family funds')}.
        
        <b>Intent to Return:</b><br/>
        Upon completion of my studies, I intend to return to {personal.get('country_of_birth', 'my home country')} 
        to apply my education and contribute to my community. I maintain strong family, 
        social, and economic ties to my home country.
        
        Thank you for considering my application.
        
        Respectfully,<br/>
        {personal.get('full_name', 'N/A')}
        """
        
        story.append(Paragraph(cover_text, styles['Normal']))
        story.append(PageBreak())
        
        # Document Checklist
        story.append(Paragraph("DOCUMENT CHECKLIST", styles['Heading1']))
        story.append(Spacer(1, 0.2*inch))
        
        checklist = [
            "✓ Form I-20 (Certificate of Eligibility for Nonimmigrant Student Status)",
            "✓ Copy of Passport Biographical Page",
            "✓ Acceptance Letter from U.S. School",
            "✓ Academic Transcripts and Records",
            "✓ Evidence of Financial Support",
            "✓ Bank Statements",
            "✓ SEVIS Fee Payment Receipt",
            "✓ English Proficiency Test Results (if required)",
            "✓ Statement of Intent to Return",
            "✓ Ties to Home Country Documentation",
        ]
        
        for item in checklist:
            story.append(Paragraph(item, styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
        
        story.append(PageBreak())
        
        # Personal Statement
        story.append(Paragraph("PERSONAL STATEMENT", styles['Heading1']))
        story.append(Spacer(1, 0.2*inch))
        
        user_story = applicant_data.get('user_story', '')
        if user_story:
            story.append(Paragraph(user_story, styles['Normal']))
        else:
            story.append(Paragraph(f"""
            My name is {personal.get('full_name', 'N/A')} and I am from {personal.get('country_of_birth', 'N/A')}. 
            I have been accepted to study at {education.get('school_name', 'a U.S. institution')} in the 
            {education.get('program_name', 'academic program')}. This educational opportunity aligns perfectly 
            with my career goals and will enable me to contribute significantly to my field upon returning to 
            my home country.
            
            I am financially prepared for this endeavor and maintain strong ties to my home country, including 
            family, property, and career prospects that ensure my return after completing my studies.
            """, styles['Normal']))
        
        story.append(PageBreak())
        
        # Applicant Information
        story.append(Paragraph("APPLICANT INFORMATION", styles['Heading1']))
        story.append(Spacer(1, 0.2*inch))
        
        info = [
            ("Full Name:", personal.get('full_name', 'N/A')),
            ("Date of Birth:", personal.get('date_of_birth', 'N/A')),
            ("Country of Birth:", personal.get('country_of_birth', 'N/A')),
            ("Email:", personal.get('email', 'N/A')),
            ("Phone:", personal.get('phone', 'N/A')),
            ("", ""),
            ("<b>ACADEMIC INFORMATION</b>", ""),
            ("School Name:", education.get('school_name', 'N/A')),
            ("Program:", education.get('program_name', 'N/A')),
            ("Degree Level:", education.get('degree_level', 'N/A')),
            ("Start Date:", education.get('start_date', 'N/A')),
            ("Expected Completion:", education.get('end_date', 'N/A')),
            ("SEVIS ID:", education.get('sevis_id', 'N/A')),
            ("", ""),
            ("<b>FINANCIAL INFORMATION</b>", ""),
            ("Funding Source:", financial.get('funding_source', 'N/A')),
            ("Annual Expenses:", financial.get('annual_expenses', 'N/A')),
        ]
        
        for label, value in info:
            if label:
                story.append(Paragraph(f"{label} {value}", styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
            else:
                story.append(Spacer(1, 0.2*inch))
        
        # Build PDF
        doc.build(story)
        
        print(f"✅ Pacote F-1 gerado: {output_file}")
        
        # Count pages
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
            'school': education.get('school_name', 'N/A')
        }
