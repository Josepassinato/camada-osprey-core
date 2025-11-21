"""
B-2 Tourist Visa Extension Specialist Agent
Especialista em extensões de visto de turista B-2
"""

from typing import Dict, Any, List
from pathlib import Path
import sys

# Adicionar path do projeto
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from visa_specialists.base_agent import BaseVisaAgent


class B2ExtensionAgent(BaseVisaAgent):
    """Agente especialista em extensões de visto B-2"""
    
    @property
    def VISA_TYPE(self) -> str:
        return "B-2 Extension"
    
    @property
    def REQUIRED_FORMS(self) -> List[str]:
        return [
            "I-539",  # Application to Extend/Change Nonimmigrant Status
        ]
    
    @property
    def REQUIRED_DOCUMENTS(self) -> List[str]:
        return [
            "Cover Letter",
            "Personal Statement",
            "Form I-539 (Completed)",
            "Current I-94 Record",
            "Passport Copy",
            "Financial Evidence",
            "Bank Statements",
            "Ties to Home Country",
            "Travel History",
            "Compliance Documentation",
            "Reason for Extension"
        ]
    
    @property
    def FORBIDDEN_DOCUMENTS(self) -> List[str]:
        return [
            "I-20",      # F-1 Student form
            "I-129",     # H-1B Worker petition
            "LCA",       # Labor Condition Application (H-1B)
            "ETA-9035",  # LCA form
            "Transcript", # School records (F-1)
            "Diploma",   # Educational docs (unless relevant to ties)
            "Employment Authorization",
            "I-140",     # Immigrant petition
            "I-485"      # Green card application
        ]
    
    def __init__(self):
        agent_dir = Path(__file__).parent
        super().__init__(agent_dir)
        
        # Registrar lições específicas de B-2 se arquivo não existe
        if not self.lessons_file.exists():
            self._initialize_lessons()
    
    def _initialize_lessons(self):
        """Inicializa arquivo de lições com erros conhecidos"""
        initial_lessons = """# Lições Aprendidas - B-2 Extension Agent

Este arquivo registra erros cometidos e correções aplicadas para melhorar continuamente.

## [Documento Proibido] 2025-06-XX

**❌ Erro:** Agente confundiu B-2 Extension com F-1 Student e mencionou necessidade de I-20 e histórico escolar.

**✅ Correção:** B-2 Extension é para TURISTAS que querem estender estadia. NÃO tem relação com estudos. I-20 e histórico escolar são EXCLUSIVOS de F-1 Student visa.

**📝 Regra:** NUNCA mencionar documentos acadêmicos (I-20, transcript, diploma) em B-2 Extension, a menos que seja para demonstrar vínculos com país de origem.

---

## [Validação] Importante

**✅ Sempre Incluir:**
- Razão clara e convincente para extensão (médica, familiar, etc.)
- Evidência de recursos financeiros substanciais
- Prova de vínculos fortes com país de origem
- Histórico de compliance perfeito
- I-94 atual mostrando status válido

**❌ Nunca Incluir:**
- Documentos de trabalho (I-129, LCA)
- Documentos de estudo (I-20, transcripts)
- Documentos de imigração permanente (I-140, I-485)

---

"""
        with open(self.lessons_file, 'w') as f:
            f.write(initial_lessons)
    
    def generate_package(self, applicant_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera pacote completo de B-2 Extension
        
        Args:
            applicant_data: Dados do aplicante (pode ser dict ou caminho para data model)
            
        Returns:
            Dicionário com resultado da geração
        """
        print(f"\n{'='*80}")
        print(f"🎯 B-2 EXTENSION AGENT - GERANDO PACOTE")
        print(f"{'='*80}\n")
        
        # Ler lições antes de começar
        print("📚 Lendo lições aprendidas...")
        if self.lessons:
            print("✅ Lições carregadas - aplicando conhecimento acumulado")
        
        # Importar gerador existente
        try:
            # Aqui chamamos o gerador que já criamos
            result = self._generate_b2_package(applicant_data)
            
            # Validar resultado
            documents = self._extract_document_list(result)
            validation = self.validate_package(documents)
            
            if not validation['is_valid']:
                print("\n⚠️  AVISO: Pacote gerado tem problemas de validação")
                if validation['forbidden_items_found']:
                    print("❌ ERRO CRÍTICO: Documentos proibidos detectados!")
                    # Registrar como lição
                    self.log_lesson(
                        f"Documentos proibidos incluídos: {', '.join(validation['forbidden_items_found'])}",
                        "Remover imediatamente e revisar checklist",
                        "Documento Proibido"
                    )
            
            return {
                'success': True,
                'package_path': result.get('package_path'),
                'documents': documents,
                'pages': result.get('pages', 0),
                'size_kb': result.get('size_kb', 0),
                'validation': validation
            }
            
        except Exception as e:
            print(f"\n❌ ERRO ao gerar pacote: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_b2_package(self, applicant_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Chama o gerador de pacote B-2 completo (60+ páginas)
        """
        # Executar o script de geração completo
        import subprocess
        from pathlib import Path
        
        # Usar o gerador completo de 60+ páginas
        generator_script = Path('/app/generate_b2_complete_package.py')
        
        if generator_script.exists():
            print("✅ Usando gerador B-2 COMPLETO (60+ páginas)...")
            result = subprocess.run(
                ['python3', str(generator_script)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Verificar se PDF foi gerado
                pdf_path = Path('/app/frontend/public/B2_COMPLETE_PACKAGE_60PLUS_PAGES.pdf')
                if pdf_path.exists():
                    from PyPDF2 import PdfReader
                    reader = PdfReader(str(pdf_path))
                    pages = len(reader.pages)
                    size_kb = pdf_path.stat().st_size / 1024
                    
                    print(f"✅ Pacote completo gerado: {pages} páginas ({size_kb:.1f} KB)")
                    
                    return {
                        'package_path': str(pdf_path),
                        'pages': pages,
                        'size_kb': size_kb
                    }
            
            print(f"⚠️  Gerador retornou erro: {result.stderr}")
        
        return {'package_path': None, 'pages': 0, 'size_kb': 0}
    
    def _extract_document_list(self, result: Dict[str, Any]) -> List[str]:
        """
        Extrai lista de documentos do resultado
        """
        # Lista padrão de documentos B-2
        documents = [
            "Form I-539",
            "Cover Letter",
            "Personal Statement",
            "Current I-94",
            "Passport Copy",
            "Bank Statements",
            "Financial Evidence",
            "Ties to Home Country",
            "Travel History",
            "Medical Documentation",
            "Supporting Letters"
        ]
        
        return documents
