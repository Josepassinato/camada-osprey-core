"""
Base Agent - Classe base para todos os agentes especialistas
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any
from pathlib import Path
import json
from datetime import datetime


class BaseVisaAgent(ABC):
    """Classe base para todos os agentes de visto"""
    
    def __init__(self, agent_dir: Path):
        self.agent_dir = agent_dir
        self.knowledge_base_dir = agent_dir / 'knowledge_base'
        self.templates_dir = agent_dir / 'templates'
        self.lessons_file = agent_dir / 'lessons_learned.md'
        self.checklist_file = agent_dir / 'checklist.json'
        
        # Garantir que diretórios existem
        self.knowledge_base_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Carregar configurações
        self._load_checklist()
        self._load_lessons()
    
    @property
    @abstractmethod
    def VISA_TYPE(self) -> str:
        """Tipo de visto que este agente processa"""
        pass
    
    @property
    @abstractmethod
    def REQUIRED_FORMS(self) -> List[str]:
        """Formulários oficiais obrigatórios"""
        pass
    
    @property
    @abstractmethod
    def REQUIRED_DOCUMENTS(self) -> List[str]:
        """Documentos de suporte obrigatórios"""
        pass
    
    @property
    @abstractmethod
    def FORBIDDEN_DOCUMENTS(self) -> List[str]:
        """Documentos que NÃO devem ser incluídos"""
        pass
    
    def _load_checklist(self):
        """Carrega checklist de validação"""
        if self.checklist_file.exists():
            with open(self.checklist_file, 'r') as f:
                self.checklist = json.load(f)
        else:
            self.checklist = {
                'required_forms': self.REQUIRED_FORMS,
                'required_documents': self.REQUIRED_DOCUMENTS,
                'forbidden_documents': self.FORBIDDEN_DOCUMENTS
            }
            self._save_checklist()
    
    def _save_checklist(self):
        """Salva checklist"""
        with open(self.checklist_file, 'w') as f:
            json.dump(self.checklist, f, indent=2)
    
    def _load_lessons(self):
        """Carrega lições aprendidas"""
        if self.lessons_file.exists():
            with open(self.lessons_file, 'r') as f:
                self.lessons = f.read()
        else:
            self.lessons = ""
    
    def log_lesson(self, mistake: str, fix: str, category: str = 'General'):
        """Registra lição aprendida"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        lesson_entry = f"""
## [{category}] {timestamp}

**❌ Erro:** {mistake}

**✅ Correção:** {fix}

---

"""
        with open(self.lessons_file, 'a') as f:
            f.write(lesson_entry)
        
        # Recarregar lições
        self._load_lessons()
        print(f"✅ Lição registrada: {category}")
    
    @abstractmethod
    def generate_package(self, applicant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gera pacote completo para este tipo de visto"""
        pass
    
    def validate_package(self, package_contents: List[str]) -> Dict[str, Any]:
        """Valida se o pacote está completo e correto"""
        validation_result = {
            'is_valid': True,
            'missing_items': [],
            'forbidden_items_found': [],
            'warnings': []
        }
        
        # Verificar formulários obrigatórios
        for form in self.REQUIRED_FORMS:
            if not any(form.lower() in item.lower() for item in package_contents):
                validation_result['missing_items'].append(f"Form {form}")
                validation_result['is_valid'] = False
        
        # Verificar documentos obrigatórios
        for doc in self.REQUIRED_DOCUMENTS:
            if not any(doc.lower() in item.lower() for item in package_contents):
                validation_result['missing_items'].append(doc)
                validation_result['is_valid'] = False
        
        # Verificar documentos proibidos
        for forbidden in self.FORBIDDEN_DOCUMENTS:
            if any(forbidden.lower() in item.lower() for item in package_contents):
                validation_result['forbidden_items_found'].append(forbidden)
                validation_result['is_valid'] = False
                validation_result['warnings'].append(
                    f"⚠️ ERRO CRÍTICO: {forbidden} não deve ser incluído em pacote {self.VISA_TYPE}"
                )
        
        return validation_result
    
    def get_package_checklist(self) -> Dict[str, Any]:
        """Retorna checklist completo para este tipo de visto"""
        return {
            'visa_type': self.VISA_TYPE,
            'required_forms': self.REQUIRED_FORMS,
            'required_documents': self.REQUIRED_DOCUMENTS,
            'forbidden_documents': self.FORBIDDEN_DOCUMENTS,
            'checklist': self.checklist
        }
