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
            "I-539",     # If changing from another status
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
        """Gera pacote F-1 completo"""
        print(f"\n{'='*80}")
        print(f"🎯 F-1 STUDENT AGENT - GERANDO PACOTE")
        print(f"{'='*80}\n")
        
        # Executar gerador F-1
        import subprocess
        from pathlib import Path
        
        generator_script = Path('/app/generate_f1_complete_package.py')
        
        if generator_script.exists():
            print("✅ Usando gerador F-1 completo profissional...")
            result = subprocess.run(
                ['python3', str(generator_script)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                pdf_path = Path('/app/frontend/public/F1_STUDENT_COMPLETE_PACKAGE_RAFAEL_OLIVEIRA.pdf')
                if pdf_path.exists():
                    from PyPDF2 import PdfReader
                    reader = PdfReader(str(pdf_path))
                    pages = len(reader.pages)
                    size_kb = pdf_path.stat().st_size / 1024
                    
                    print(f"✅ Pacote F-1 completo gerado: {pages} páginas ({size_kb:.1f} KB)")
                    
                    return {
                        'package_path': str(pdf_path),
                        'pages': pages,
                        'size_kb': size_kb,
                        'documents': self.REQUIRED_DOCUMENTS
                    }
            
            print(f"⚠️  Gerador retornou erro: {result.stderr}")
        
        return {
            'package_path': None,
            'pages': 0,
            'size_kb': 0,
            'documents': self.REQUIRED_DOCUMENTS
        }
