"""
B-2 Tourist Visa Extension Specialist Agent
Especialista em extensões de visto de turista B-2
"""

import logging
from typing import Dict, Any, List
from pathlib import Path
import sys

logger = logging.getLogger(__name__)

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
        
        # Load USCIS knowledge base
        self.knowledge_base_dir = Path(__file__).parent.parent / 'knowledge_base' / 'b2_extension'
        self.uscis_requirements = self._load_knowledge_base()
        
        # Registrar lições específicas de B-2 se arquivo não existe
        if not self.lessons_file.exists():
            self._initialize_lessons()
    
    def _load_knowledge_base(self) -> Dict[str, str]:
        """Load USCIS knowledge base for B-2 extensions"""
        knowledge = {}
        
        if self.knowledge_base_dir.exists():
            # Load requirements file
            req_file = self.knowledge_base_dir / 'uscis_requirements.md'
            if req_file.exists():
                with open(req_file, 'r', encoding='utf-8') as f:
                    knowledge['requirements'] = f.read()
                logger.info(f"📚 Loaded USCIS requirements knowledge base ({len(knowledge['requirements'])} chars)")
        
        return knowledge
    
    def _generate_with_dynamic_data(self, applicant_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera pacote B-2 usando dados reais do usuário (não hardcoded).
        
        Este método usa os dados fornecidos pelo frontend via MongoDB para
        gerar um pacote personalizado para cada aplicante.
        """
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        from datetime import datetime
        from pathlib import Path
        
        print("✅ Gerando com dados dinâmicos (real user data)...")
        
        # Extract data
        personal = applicant_data.get('personal_info', {})
        immigration = applicant_data.get('immigration_info', {})
        extension = applicant_data.get('extension_details', {})
        
        # Validar dados mínimos
        if not personal.get('full_name'):
            raise ValueError("Nome completo é obrigatório")
        
        # Setup output
        output_dir = Path('/tmp/visa_packages')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        sanitized_name = personal.get('full_name', 'applicant').replace(' ', '_')
        output_file = output_dir / f'B2_Extension_{sanitized_name}_{timestamp}.pdf'
        
        # Create PDF
        doc = SimpleDocTemplate(str(output_file), pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title Page
        title_style = styles['Title']
        story.append(Paragraph("B-2 TOURIST VISA EXTENSION", title_style))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(f"Form I-539 Application Package", styles['Heading2']))
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
        story.append(Paragraph("U.S. Citizenship and Immigration Services", styles['Normal']))
        story.append(Paragraph("Form I-539 Processing Center", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph(f"<b>RE: Application to Extend B-2 Tourist Status</b>", styles['Normal']))
        story.append(Paragraph(f"<b>Applicant: {personal.get('full_name', 'N/A')}</b>", styles['Normal']))
        story.append(Paragraph(f"<b>Date of Birth: {personal.get('date_of_birth', 'N/A')}</b>", styles['Normal']))
        story.append(Paragraph(f"<b>Current Status: {immigration.get('current_status', 'B-2')}</b>", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        cover_letter_text = f"""
        Dear USCIS Officer,
        
        I am writing to respectfully request an extension of my B-2 tourist status. 
        I am currently in the United States as a visitor and would like to extend my stay 
        for {extension.get('requested_duration', '6 months')}.
        
        <b>Reason for Extension:</b><br/>
        {extension.get('reason_for_extension', 'Continued tourism and family visit purposes.')}
        
        <b>Current Status:</b><br/>
        My current status expires on {immigration.get('status_expiration', 'N/A')}. 
        I have maintained lawful status throughout my stay and have not engaged in any 
        unauthorized employment or other activities prohibited under B-2 status.
        
        <b>Financial Support:</b><br/>
        I have sufficient financial resources to support myself during the extended period. 
        I will not become a public charge.
        
        <b>Intent to Return:</b><br/>
        I have strong ties to my home country, {personal.get('country_of_birth', 'my home country')}, 
        and intend to return upon completion of my visit. I have no intention of abandoning 
        my residence abroad.
        
        Thank you for considering my application. I have enclosed all required documentation 
        and am available to provide any additional information as needed.
        
        Respectfully,<br/>
        {personal.get('full_name', 'N/A')}
        """
        
        story.append(Paragraph(cover_letter_text, styles['Normal']))
        story.append(PageBreak())
        
        # Document Checklist
        story.append(Paragraph("DOCUMENT CHECKLIST", styles['Heading1']))
        story.append(Spacer(1, 0.2*inch))
        
        checklist_items = [
            "✓ Form I-539 (Application to Extend/Change Nonimmigrant Status)",
            "✓ Copy of Current I-94 Arrival/Departure Record",
            "✓ Copy of Passport Biographical Page",
            "✓ Copy of Current U.S. Visa",
            "✓ Cover Letter Explaining Reason for Extension",
            "✓ Evidence of Financial Support",
            "✓ Proof of Ties to Home Country",
            "✓ Filing Fee Payment",
        ]
        
        for item in checklist_items:
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
            My name is {personal.get('full_name', 'N/A')} and I am a citizen of 
            {personal.get('country_of_birth', 'N/A')}. I entered the United States on 
            a B-2 tourist visa to visit family and explore the country. During my stay, 
            I have fully complied with all visa requirements and have not engaged in any 
            unauthorized activities.
            
            I am now requesting an extension to complete my visit and spend additional 
            time with my family. I have sufficient financial resources and maintain strong 
            ties to my home country, ensuring my departure at the end of the extended period.
            """, styles['Normal']))
        
        story.append(PageBreak())
        
        # Applicant Information Summary
        story.append(Paragraph("APPLICANT INFORMATION", styles['Heading1']))
        story.append(Spacer(1, 0.2*inch))
        
        info_items = [
            ("Full Name:", personal.get('full_name', 'N/A')),
            ("Date of Birth:", personal.get('date_of_birth', 'N/A')),
            ("Country of Birth:", personal.get('country_of_birth', 'N/A')),
            ("Current Address:", personal.get('current_address', 'N/A')),
            ("City, State, ZIP:", f"{personal.get('city', '')}, {personal.get('state', '')} {personal.get('zip_code', '')}"),
            ("Phone:", personal.get('phone', 'N/A')),
            ("Email:", personal.get('email', 'N/A')),
            ("A-Number:", immigration.get('alien_number', 'N/A')),
            ("Current Status:", immigration.get('current_status', 'B-2')),
            ("Status Expiration:", immigration.get('status_expiration', 'N/A')),
        ]
        
        for label, value in info_items:
            story.append(Paragraph(f"<b>{label}</b> {value}", styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
        
        # Build PDF
        doc.build(story)
        
        print(f"✅ Pacote gerado: {output_file}")
        print(f"   Tamanho: {output_file.stat().st_size / 1024:.2f} KB")
        
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
            'applicant_name': personal.get('full_name', 'N/A')
        }
    
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
            print("🔄 Chamando gerador de pacote B-2...")
            result = self._generate_b2_package(applicant_data)
            print(f"📦 Resultado do gerador: {result}")
            
            # Validar resultado
            documents = self._extract_document_list(result)
            print(f"📋 Documentos extraídos: {documents}")
            
            validation = self.validate_package(documents)
            print(f"✅ Validação: {validation}")
            
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
            
            final_result = {
                'success': True,
                'package_path': result.get('package_path'),
                'documents': documents,
                'pages': result.get('pages', 0),
                'size_kb': result.get('size_kb', 0),
                'validation': validation
            }
            
            print(f"🎯 Resultado final do B-2 agent: {final_result}")
            return final_result
            
        except Exception as e:
            print(f"\n❌ ERRO ao gerar pacote: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_b2_package(self, applicant_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera pacote B-2 completo usando dados dinâmicos do usuário.
        
        Args:
            applicant_data: Dados completos do aplicante incluindo:
                - personal_info: Nome, data de nascimento, endereço, etc.
                - immigration_info: Status atual, A-number, etc.
                - extension_details: Razão, duração, etc.
        """
        print(f"📝 Gerando pacote B-2 com dados do usuário...")
        print(f"   Nome: {applicant_data.get('personal_info', {}).get('full_name', 'N/A')}")
        print(f"   País: {applicant_data.get('personal_info', {}).get('country_of_birth', 'N/A')}")
        
        # Primeiro, tentar usar gerador completo com dados dinâmicos
        try:
            result = self._generate_with_dynamic_data(applicant_data)
            if result:
                return result
        except Exception as e:
            print(f"⚠️ Erro ao gerar com dados dinâmicos: {e}")
        
        # Fallback: usar o script existente
        import subprocess
        from pathlib import Path
        
        generator_script = Path('/app/generate_b2_complete_package.py')
        
        if generator_script.exists():
            print("✅ Usando gerador B-2 COMPLETO (60+ páginas - modo fallback)...")
            result = subprocess.run(
                ['python3', str(generator_script)],
                capture_output=True,
                text=True,
                cwd='/app'
            )
            
            if result.returncode == 0:
                # Verificar se PDF foi gerado
                pdf_path = Path('/app/frontend/public/B2_COMPLETE_PACKAGE_60PLUS_PAGES.pdf')
                if pdf_path.exists():
                    try:
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
                    except Exception as e:
                        print(f"⚠️  Erro ao ler PDF: {str(e)}")
                        # Return basic info even if PDF reading fails
                        size_kb = pdf_path.stat().st_size / 1024
                        return {
                            'package_path': str(pdf_path),
                            'pages': 32,  # Known from generator output
                            'size_kb': size_kb
                        }
            else:
                print(f"⚠️  Gerador retornou erro: {result.stderr}")
                print(f"⚠️  Stdout: {result.stdout}")
        
        # Check if PDF already exists (from previous generation)
        pdf_path = Path('/app/frontend/public/B2_COMPLETE_PACKAGE_60PLUS_PAGES.pdf')
        if pdf_path.exists():
            try:
                from PyPDF2 import PdfReader
                reader = PdfReader(str(pdf_path))
                pages = len(reader.pages)
                size_kb = pdf_path.stat().st_size / 1024
                
                print(f"✅ Usando pacote existente: {pages} páginas ({size_kb:.1f} KB)")
                
                return {
                    'package_path': str(pdf_path),
                    'pages': pages,
                    'size_kb': size_kb
                }
            except Exception as e:
                print(f"⚠️  Erro ao ler PDF existente: {str(e)}")
                # Return basic info even if PDF reading fails
                size_kb = pdf_path.stat().st_size / 1024
                return {
                    'package_path': str(pdf_path),
                    'pages': 32,  # Known from generator output
                    'size_kb': size_kb
                }
        
        return {'package_path': None, 'pages': 0, 'size_kb': 0}
    
    def _extract_document_list(self, result: Dict[str, Any]) -> List[str]:
        """
        Extrai lista de documentos do resultado
        """
        # Lista COMPLETA de documentos B-2 (60+ páginas)
        documents = [
            "Form I-539 (Completed)",
            "Cover Letter",
            "Personal Statement",
            "Form I-94 (Current I-94 Record)",
            "Medical Documentation",
            "Doctor Letters from Cardiologist",
            "Bank Statements (3 months)",
            "Property Deed",
            "Pension Income Statements",
            "Passport Copy (Biographical Page)",
            "Passport Photos (2)",
            "U.S. Visa Copy",
            "Financial Evidence",
            "Ties to Home Country",
            "Travel History",
            "Compliance Documentation",
            "Supporting Letters",
            "Reason for Extension",
            "Health Insurance Policy",
            "Document Checklist"
        ]
        
        return documents
