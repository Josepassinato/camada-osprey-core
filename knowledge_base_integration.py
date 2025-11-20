#!/usr/bin/env python3
"""
Integração com a Base de Conhecimento
Lê templates, guias e checklists dos recursos processados
"""

import os
import json
from pathlib import Path
import pdfplumber
from typing import Dict, List, Optional


class KnowledgeBaseIntegration:
    """
    Classe para acessar e extrair conteúdo da base de conhecimento
    """
    
    def __init__(self, kb_path: str = "/app/immigration_resources"):
        self.kb_path = Path(kb_path)
        self.catalog_path = self.kb_path / "catalog.json"
        self.catalog = self._load_catalog()
        
    def _load_catalog(self) -> Dict:
        """Carrega o catálogo de recursos"""
        if not self.catalog_path.exists():
            print(f"⚠️ Catálogo não encontrado em {self.catalog_path}")
            return {}
        
        with open(self.catalog_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_completion_guide(self, form_name: str) -> Optional[str]:
        """
        Busca e retorna o guia de preenchimento para um formulário específico
        Args:
            form_name: Nome do formulário (ex: "I-129", "I-130")
        Returns:
            Texto extraído do guia ou None
        """
        guides = self.catalog.get("completion_guides", [])
        
        # Buscar guia específico
        for guide in guides:
            filename = guide.get("filename", "")
            if form_name in filename:
                pdf_path = self.kb_path / guide.get("path", "")
                if pdf_path.exists():
                    return self._extract_text_from_pdf(pdf_path)
        
        return None
    
    def get_checklist(self, checklist_type: str = "Supporting_Document") -> Optional[str]:
        """
        Busca e retorna um checklist específico
        Args:
            checklist_type: Tipo do checklist (ex: "Supporting_Document", "USCIS_Form_Filing")
        Returns:
            Texto extraído do checklist ou None
        """
        checklists = self.catalog.get("checklists_and_trackers", [])
        
        for checklist in checklists:
            filename = checklist.get("filename", "")
            if checklist_type in filename:
                pdf_path = self.kb_path / checklist.get("path", "")
                if pdf_path.exists():
                    return self._extract_text_from_pdf(pdf_path)
        
        return None
    
    def get_letter_template(self, template_type: str = "Affidavit") -> Optional[str]:
        """
        Busca e retorna um template de carta
        Args:
            template_type: Tipo do template (ex: "Affidavit", "Support")
        Returns:
            Texto extraído do template ou None
        """
        templates = self.catalog.get("letter_templates", [])
        
        for template in templates:
            filename = template.get("filename", "")
            if template_type in filename:
                pdf_path = self.kb_path / template.get("path", "")
                if pdf_path.exists():
                    return self._extract_text_from_pdf(pdf_path)
        
        return None
    
    def get_all_checklists(self) -> List[Dict]:
        """
        Retorna todos os checklists disponíveis
        Returns:
            Lista de dicts com informações dos checklists
        """
        checklists = self.catalog.get("checklists_and_trackers", [])
        results = []
        
        for checklist in checklists:
            pdf_path = self.kb_path / checklist.get("path", "")
            if pdf_path.exists():
                results.append({
                    "filename": checklist.get("filename", ""),
                    "path": str(pdf_path),
                    "content": self._extract_text_from_pdf(pdf_path)
                })
        
        return results
    
    def get_form_requirements(self, form_name: str) -> Dict:
        """
        Extrai requisitos específicos de um formulário baseado no guia
        Args:
            form_name: Nome do formulário (ex: "I-129")
        Returns:
            Dict com seções importantes extraídas do guia
        """
        guide_text = self.get_completion_guide(form_name)
        
        if not guide_text:
            return {}
        
        requirements = {
            "required_documents": [],
            "common_mistakes": [],
            "key_sections": [],
            "important_notes": []
        }
        
        # Extrair seções importantes usando keywords
        lines = guide_text.split('\n')
        current_section = None
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Identificar seções
            if "required document" in line_lower or "necessary document" in line_lower:
                current_section = "required_documents"
            elif "common mistake" in line_lower or "error" in line_lower:
                current_section = "common_mistakes"
            elif "important" in line_lower or "note" in line_lower:
                current_section = "important_notes"
            elif "section" in line_lower and any(c.isdigit() for c in line):
                current_section = "key_sections"
            
            # Adicionar conteúdo à seção apropriada
            if current_section and line.strip() and len(line.strip()) > 10:
                if line.strip() not in requirements[current_section]:
                    requirements[current_section].append(line.strip())
        
        return requirements
    
    def _extract_text_from_pdf(self, pdf_path: Path) -> str:
        """
        Extrai texto de um arquivo PDF
        Args:
            pdf_path: Caminho para o arquivo PDF
        Returns:
            Texto extraído
        """
        try:
            text_content = []
            
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
            
            return '\n'.join(text_content)
        
        except Exception as e:
            print(f"⚠️ Erro ao extrair texto de {pdf_path}: {e}")
            return ""
    
    def get_professional_cover_letter_template(self) -> str:
        """
        Cria um template profissional de cover letter baseado nos recursos
        Returns:
            Template de cover letter
        """
        # Buscar guia I-129 para referência
        i129_guide = self.get_completion_guide("I-129")
        
        template = """[Law Firm Letterhead]
[Attorney Name]
[Bar Number]
[Firm Name]
[Address]
[Phone] | [Email]

[Date]

U.S. Citizenship and Immigration Services
[Service Center Address]

RE: H-1B Petition for [Beneficiary Name]
    Beneficiary: [Full Name]
    Beneficiary Date of Birth: [DOB]
    Petitioner: [Company Name]
    Classification Sought: H-1B Specialty Occupation

Dear USCIS Officer:

INTRODUCTION

On behalf of our client, [Company Name] ("Petitioner"), we respectfully submit this petition for H-1B nonimmigrant classification for [Beneficiary Name] ("Beneficiary") pursuant to Section 101(a)(15)(H)(i)(b) of the Immigration and Nationality Act (INA).

PURPOSE OF PETITION

The Petitioner seeks to employ the Beneficiary in the position of [Job Title], a specialty occupation requiring theoretical and practical application of a body of highly specialized knowledge in [Field]. This position requires a minimum of a bachelor's degree in [Degree Field] or its equivalent.

PETITIONER QUALIFICATIONS

[Company Name] is a [business description] established in [year]. The company specializes in [business focus] and has demonstrated significant financial capacity to support this H-1B position through the submitted evidence.

BENEFICIARY QUALIFICATIONS

The Beneficiary holds a [Degree Type] in [Field] from [University], completed in [Year]. Additionally, the Beneficiary has [X] years of progressive experience in [Field/Industry], making them exceptionally qualified for this specialized role.

SPECIALTY OCCUPATION EVIDENCE

The proffered position meets all criteria for a specialty occupation as defined in 8 CFR 214.2(h)(4)(iii)(A). Specifically:

1. The position requires a baccalaureate or higher degree, or its equivalent, as a minimum for entry
2. The degree requirement is common to the industry or the position is so complex that it can only be performed by an individual with a degree
3. The Petitioner normally requires a degree or its equivalent for the position
4. The nature of the specific duties is so specialized and complex that the knowledge required is usually associated with a bachelor's degree or higher

DOCUMENTATION ENCLOSED

This petition includes the following supporting documentation:

• Form I-129, Petition for Nonimmigrant Worker
• H Classification Supplement to Form I-129
• Certified Labor Condition Application (LCA)
• Company support letter with detailed job description
• Evidence of Petitioner's ability to pay the proffered wage
• Organizational chart showing position hierarchy
• Beneficiary's educational credentials with evaluation
• Beneficiary's detailed resume
• Beneficiary's passport
• Employment verification letters
• Professional letters of recommendation
• Additional supporting evidence

CONCLUSION

Based on the foregoing and the supporting documentation provided, we respectfully request that USCIS approve this H-1B petition. The Beneficiary possesses the requisite education, training, and experience to perform the duties of the specialty occupation position offered by the Petitioner.

Should you have any questions or require additional information, please do not hesitate to contact our office.

Respectfully submitted,

[Attorney Signature]
[Attorney Name]
[Bar Number]
[Date]

Enclosures: As stated above
"""
        
        return template
    
    def get_company_support_letter_template(self) -> str:
        """
        Cria um template de carta de suporte da empresa
        Returns:
            Template de support letter
        """
        template = """[Company Letterhead]

[Date]

U.S. Citizenship and Immigration Services
[Service Center Address]

RE: H-1B Petition for [Beneficiary Name]
    Company: [Company Name]
    Position: [Job Title]

To Whom It May Concern:

COMPANY BACKGROUND

[Company Name] is pleased to offer employment to [Beneficiary Name] in the position of [Job Title]. Our company was established in [Year] and is a leading [Industry] company specializing in [Core Business Focus].

We currently employ [Number] professionals and maintain operations in [Locations]. Our annual revenue for [Year] was approximately $[Amount], demonstrating our strong financial position and ability to compensate the Beneficiary at the offered wage.

POSITION DESCRIPTION

The position of [Job Title] is a full-time position requiring a minimum of 40 hours per week. The role is critical to our operations and requires advanced knowledge in [Field/Technology].

Primary Responsibilities:
• [Responsibility 1 - detailed]
• [Responsibility 2 - detailed]
• [Responsibility 3 - detailed]
• [Responsibility 4 - detailed]
• [Responsibility 5 - detailed]

Required Qualifications:
• Bachelor's degree or higher in [Field] or related field
• [X] years of experience in [Specific Area]
• Proficiency in [Technologies/Skills]
• Strong analytical and problem-solving abilities
• Excellent communication and collaboration skills

BENEFICIARY QUALIFICATIONS

[Beneficiary Name] possesses the requisite educational background and professional experience for this position. The Beneficiary holds a [Degree] in [Field] from [University] and has [X] years of progressive experience in [Industry/Field].

The Beneficiary's unique combination of education and experience makes them exceptionally qualified to perform the complex duties of this specialty occupation. Their background in [Specific Areas] directly aligns with our business needs.

COMPENSATION AND TERMS

• Position: [Job Title] (Full-time, H-1B status)
• Salary: $[Amount] per year
• Benefits: Health insurance, retirement plan, paid time off
• Location: [Work Location]
• Start Date: [Date]
• Duration: [Duration] (with possibility of extension)

COMPANY COMMITMENT

We are committed to complying with all H-1B program requirements, including maintaining proper working conditions and compensation for the Beneficiary. We will also fulfill all obligations regarding the Labor Condition Application filed with the Department of Labor.

We respectfully request favorable consideration of this H-1B petition. [Beneficiary Name] will be a valuable addition to our team, and we are confident in their ability to contribute significantly to our continued success.

Should you require any additional information, please contact our office at [Phone] or [Email].

Sincerely,

[Signature]
[Name]
[Title]
[Company Name]
[Contact Information]
"""
        
        return template
    
    def list_all_resources(self) -> Dict:
        """
        Lista todos os recursos disponíveis na base de conhecimento
        Returns:
            Dict com todas as categorias e seus recursos
        """
        summary = {
            "completion_guides": len(self.catalog.get("completion_guides", [])),
            "checklists_and_trackers": len(self.catalog.get("checklists_and_trackers", [])),
            "letter_templates": len(self.catalog.get("letter_templates", [])),
            "forms_and_templates": len(self.catalog.get("forms_and_templates", [])),
            "official_forms": len(self.catalog.get("official_forms", [])),
            "total": sum([
                len(self.catalog.get("completion_guides", [])),
                len(self.catalog.get("checklists_and_trackers", [])),
                len(self.catalog.get("letter_templates", [])),
                len(self.catalog.get("forms_and_templates", [])),
                len(self.catalog.get("official_forms", []))
            ])
        }
        
        return summary


# Função de teste
if __name__ == "__main__":
    print("\n" + "="*80)
    print("🔍 TESTANDO INTEGRAÇÃO COM BASE DE CONHECIMENTO")
    print("="*80)
    
    kb = KnowledgeBaseIntegration()
    
    # Listar recursos
    print("\n📚 Recursos Disponíveis:")
    resources = kb.list_all_resources()
    for category, count in resources.items():
        if category != "total":
            print(f"   • {category.replace('_', ' ').title()}: {count} recursos")
    print(f"\n   Total: {resources['total']} recursos")
    
    # Testar busca de guia I-129
    print("\n📖 Testando busca de guia I-129...")
    guide = kb.get_completion_guide("I-129")
    if guide:
        print(f"   ✅ Guia encontrado! Tamanho: {len(guide)} caracteres")
        print(f"   Prévia: {guide[:200]}...")
    else:
        print("   ⚠️ Guia não encontrado")
    
    # Testar busca de checklist
    print("\n📋 Testando busca de checklist...")
    checklist = kb.get_checklist("Supporting_Document")
    if checklist:
        print(f"   ✅ Checklist encontrado! Tamanho: {len(checklist)} caracteres")
    else:
        print("   ⚠️ Checklist não encontrado")
    
    # Testar extração de requisitos
    print("\n📝 Testando extração de requisitos do I-129...")
    requirements = kb.get_form_requirements("I-129")
    print(f"   • Documentos necessários: {len(requirements.get('required_documents', []))} itens")
    print(f"   • Erros comuns: {len(requirements.get('common_mistakes', []))} itens")
    print(f"   • Seções importantes: {len(requirements.get('key_sections', []))} itens")
    
    print("\n" + "="*80)
    print("✅ TESTE CONCLUÍDO")
    print("="*80)
