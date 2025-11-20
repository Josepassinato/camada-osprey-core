"""
H-1B Specialty Occupation Worker Specialist Agent
Especialista em petições H-1B para trabalhadores especializados
"""

from typing import Dict, Any, List
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from visa_specialists.base_agent import BaseVisaAgent


class H1BWorkerAgent(BaseVisaAgent):
    """Agente especialista em petições H-1B"""
    
    @property
    def VISA_TYPE(self) -> str:
        return "H-1B Worker"
    
    @property
    def REQUIRED_FORMS(self) -> List[str]:
        return [
            "I-129",      # Petition for Nonimmigrant Worker
            "I-129H",     # H Classification Supplement
            "LCA",        # Labor Condition Application (ETA-9035)
        ]
    
    @property
    def REQUIRED_DOCUMENTS(self) -> List[str]:
        return [
            "Cover Letter",
            "Support Letter",
            "Form I-129 (Completed)",
            "Form I-129H Supplement",
            "LCA (Certified)",
            "LCA Posting Notice",
            "Company Evidence",
            "Job Description",
            "Beneficiary Resume/CV",
            "Educational Credentials",
            "Degree Evaluation (if foreign degree)",
            "Proof of Specialty Occupation",
            "Employer-Employee Relationship Evidence"
        ]
    
    @property
    def FORBIDDEN_DOCUMENTS(self) -> List[str]:
        return [
            "I-20",      # F-1 Student form
            "I-539",     # Extension/Change form (unless changing from another status)
            "I-94 (visitor)",  # Tourist I-94
            "Tourist Visa",
            "B-2 Documentation"
        ]
    
    def __init__(self):
        agent_dir = Path(__file__).parent
        super().__init__(agent_dir)
        
        if not self.lessons_file.exists():
            self._initialize_lessons()
    
    def _initialize_lessons(self):
        """Inicializa lições H-1B"""
        initial_lessons = """# Lições Aprendidas - H-1B Worker Agent

## [Formulários] Importante

**✅ Formulários Críticos:**
- I-129: Petition principal
- I-129H: Supplement obrigatório para H classification
- LCA: DEVE estar certificado pelo DOL antes de filing

**❌ Erro Comum:** Esquecer de incluir LCA Posting Notice (prova de que LCA foi postado para empregados)

---

## [Especialização] Crítico

**✅ Sempre Demonstrar:**
- Posição requer degree específico
- Beneficiário possui degree requerido
- Salário atende prevailing wage
- Employer-employee relationship existe

---

"""
        with open(self.lessons_file, 'w') as f:
            f.write(initial_lessons)
    
    def generate_package(self, applicant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gera pacote H-1B completo"""
        print(f"\n{'='*80}")
        print(f"🎯 H-1B WORKER AGENT - GERANDO PACOTE")
        print(f"{'='*80}\n")
        
        # TODO: Implementar gerador H-1B
        # Por enquanto, retornar placeholder
        return {
            'success': True,
            'message': 'H-1B generator will be implemented',
            'documents': self.REQUIRED_DOCUMENTS
        }
