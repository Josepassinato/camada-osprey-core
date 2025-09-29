"""
Visa Document Mapping - Sistema inteligente de mapeamento de documentos e dados por tipo de visto
Baseado no conhecimento especializado da Dra. Paula B2C
"""

import os
import json
from typing import Dict, List, Any, Optional
from dra_paula_knowledge_base import dra_paula_knowledge, get_visa_knowledge

class VisaDocumentMapper:
    """
    Mapeia documentos necessários e dados a serem extraídos para cada tipo de visto
    """
    
    def __init__(self):
        self.visa_mappings = self._initialize_visa_mappings()
    
    def _initialize_visa_mappings(self) -> Dict[str, Any]:
        """Inicializa mapeamentos detalhados para cada tipo de visto"""
        return {
            "H-1B": {
                "uscis_forms": ["I-129", "I-94"],
                "required_documents": {
                    "passport": {
                        "required": True,
                        "description": "Passaporte válido por pelo menos 6 meses",
                        "extract_fields": [
                            "passport_number", "full_name", "date_of_birth", 
                            "place_of_birth", "nationality", "expiration_date",
                            "issue_date", "issuing_authority"
                        ]
                    },
                    "diploma": {
                        "required": True,
                        "description": "Diploma de ensino superior ou equivalente",
                        "extract_fields": [
                            "degree_type", "field_of_study", "institution_name",
                            "graduation_date", "student_name", "gpa_if_available"
                        ]
                    },
                    "transcript": {
                        "required": True,
                        "description": "Histórico escolar oficial",
                        "extract_fields": [
                            "institution_name", "student_name", "degree_program",
                            "courses_completed", "grades", "graduation_status"
                        ]
                    },
                    "employment_letter": {
                        "required": True,
                        "description": "Carta de oferta de emprego do petitioner",
                        "extract_fields": [
                            "employer_name", "employer_address", "position_title",
                            "job_duties", "salary", "start_date", "employment_type"
                        ]
                    },
                    "lca": {
                        "required": True,
                        "description": "Labor Condition Application aprovada",
                        "extract_fields": [
                            "lca_number", "employer_name", "wage_rate",
                            "work_location", "occupation_code", "validity_period"
                        ]
                    },
                    "resume": {
                        "required": True,
                        "description": "Currículo detalhado",
                        "extract_fields": [
                            "work_experience", "education", "skills",
                            "certifications", "languages"
                        ]
                    },
                    "photos": {
                        "required": True,
                        "description": "2 fotos tipo passaporte padrão USCIS",
                        "extract_fields": ["photo_compliance", "background_color", "dimensions"]
                    }
                },
                "form_data_mapping": {
                    "part1_applicant_info": {
                        "full_name": "passport.full_name",
                        "other_names": "passport.other_names",
                        "date_of_birth": "passport.date_of_birth",
                        "place_of_birth": "passport.place_of_birth",
                        "nationality": "passport.nationality",
                        "passport_number": "passport.passport_number"
                    },
                    "part2_classification": {
                        "classification": "H-1B",
                        "basis_for_classification": "employment_letter.position_title"
                    },
                    "part3_processing": {
                        "action_requested": "Initial status",
                        "total_workers": "lca.total_workers"
                    }
                }
            },
            
            "L-1": {
                "uscis_forms": ["I-129", "I-94"],
                "required_documents": {
                    "passport": {
                        "required": True,
                        "description": "Passaporte válido",
                        "extract_fields": [
                            "passport_number", "full_name", "date_of_birth",
                            "place_of_birth", "nationality", "expiration_date"
                        ]
                    },
                    "employment_letter_us": {
                        "required": True,
                        "description": "Carta da empresa americana",
                        "extract_fields": [
                            "us_company_name", "relationship_to_foreign_entity",
                            "position_offered", "job_duties", "salary"
                        ]
                    },
                    "employment_letter_foreign": {
                        "required": True,
                        "description": "Carta da empresa estrangeira",
                        "extract_fields": [
                            "foreign_company_name", "employee_position",
                            "employment_duration", "job_responsibilities"
                        ]
                    },
                    "company_documents": {
                        "required": True,
                        "description": "Documentos comprovando relacionamento entre empresas",
                        "extract_fields": [
                            "ownership_structure", "business_relationship",
                            "financial_statements", "corporate_documents"
                        ]
                    },
                    "photos": {
                        "required": True,
                        "description": "2 fotos tipo passaporte",
                        "extract_fields": ["photo_compliance"]
                    }
                }
            },

            "O-1": {
                "uscis_forms": ["I-129"],
                "required_documents": {
                    "passport": {
                        "required": True,
                        "description": "Passaporte válido",
                        "extract_fields": [
                            "passport_number", "full_name", "date_of_birth",
                            "nationality", "expiration_date"
                        ]
                    },
                    "awards_certificates": {
                        "required": True,
                        "description": "Prêmios e certificados de excelência",
                        "extract_fields": [
                            "award_name", "granting_organization", "award_date",
                            "achievement_description", "recognition_level"
                        ]
                    },
                    "publications": {
                        "required": False,
                        "description": "Publicações acadêmicas ou profissionais",
                        "extract_fields": [
                            "publication_title", "publication_date", "journal_name",
                            "authors", "citation_count"
                        ]
                    },
                    "media_coverage": {
                        "required": False,
                        "description": "Cobertura da mídia sobre trabalho",
                        "extract_fields": [
                            "media_outlet", "publication_date", "article_title",
                            "coverage_description"
                        ]
                    },
                    "recommendation_letters": {
                        "required": True,
                        "description": "Cartas de recomendação de especialistas",
                        "extract_fields": [
                            "recommender_name", "recommender_qualifications",
                            "relationship_to_applicant", "recommendation_content"
                        ]
                    },
                    "contract_itinerary": {
                        "required": True,
                        "description": "Contrato ou itinerário de trabalho",
                        "extract_fields": [
                            "employer_name", "work_description", "performance_dates",
                            "venues", "compensation"
                        ]
                    }
                }
            },

            "B-1/B-2": {
                "uscis_forms": ["DS-160"],
                "required_documents": {
                    "passport": {
                        "required": True,
                        "description": "Passaporte válido por pelo menos 6 meses",
                        "extract_fields": [
                            "passport_number", "full_name", "date_of_birth",
                            "place_of_birth", "nationality", "expiration_date"
                        ]
                    },
                    "photos": {
                        "required": True,
                        "description": "Foto digital para DS-160",
                        "extract_fields": ["photo_compliance", "dimensions"]
                    },
                    "invitation_letter": {
                        "required": False,
                        "description": "Carta convite (se aplicável)",
                        "extract_fields": [
                            "inviter_name", "inviter_address", "relationship",
                            "purpose_of_visit", "duration_of_stay"
                        ]
                    },
                    "financial_documents": {
                        "required": True,
                        "description": "Comprovantes financeiros",
                        "extract_fields": [
                            "bank_statements", "employment_letter", "salary",
                            "assets", "financial_support"
                        ]
                    },
                    "ties_to_home_country": {
                        "required": True,
                        "description": "Comprovação de vínculos com país de origem",
                        "extract_fields": [
                            "employment_status", "property_ownership",
                            "family_ties", "educational_enrollment"
                        ]
                    }
                }
            },

            "F-1": {
                "uscis_forms": ["DS-160", "I-20"],
                "required_documents": {
                    "passport": {
                        "required": True,
                        "description": "Passaporte válido",
                        "extract_fields": [
                            "passport_number", "full_name", "date_of_birth",
                            "nationality", "expiration_date"
                        ]
                    },
                    "i20_form": {
                        "required": True,
                        "description": "Formulário I-20 da instituição",
                        "extract_fields": [
                            "sevis_id", "school_name", "program_of_study",
                            "program_start_date", "program_end_date", "financial_info"
                        ]
                    },
                    "financial_documents": {
                        "required": True,
                        "description": "Comprovação de recursos financeiros",
                        "extract_fields": [
                            "bank_statements", "scholarship_letter", "sponsor_affidavit",
                            "total_funds_available", "funding_source"
                        ]
                    },
                    "academic_transcripts": {
                        "required": True,
                        "description": "Histórico escolar anterior",
                        "extract_fields": [
                            "school_name", "graduation_date", "gpa",
                            "subjects_studied", "academic_achievements"
                        ]
                    },
                    "language_proficiency": {
                        "required": False,
                        "description": "Certificado de proficiência em inglês",
                        "extract_fields": [
                            "test_type", "test_score", "test_date",
                            "proficiency_level"
                        ]
                    }
                }
            }
        }

    def get_required_documents_for_visa(self, visa_type: str) -> Dict[str, Any]:
        """Retorna documentos necessários para um tipo específico de visto"""
        visa_type_clean = visa_type.upper().replace("-", "").replace("/", "")
        
        if visa_type_clean == "H1B":
            visa_type_clean = "H-1B"
        elif visa_type_clean == "B1B2":
            visa_type_clean = "B-1/B-2"
        
        return self.visa_mappings.get(visa_type_clean, {}).get("required_documents", {})

    def get_extraction_fields_for_document(self, visa_type: str, document_type: str) -> List[str]:
        """Retorna campos específicos a serem extraídos de um documento para um tipo de visto"""
        documents = self.get_required_documents_for_visa(visa_type)
        document_info = documents.get(document_type, {})
        return document_info.get("extract_fields", [])

    def get_form_mapping_for_visa(self, visa_type: str) -> Dict[str, Any]:
        """Retorna mapeamento de dados para formulário específico do visto"""
        visa_type_clean = visa_type.upper().replace("-", "").replace("/", "")
        
        if visa_type_clean == "H1B":
            visa_type_clean = "H-1B"
        elif visa_type_clean == "B1B2":
            visa_type_clean = "B-1/B-2"
            
        return self.visa_mappings.get(visa_type_clean, {}).get("form_data_mapping", {})

    def get_enhanced_extraction_prompt(self, visa_type: str, document_type: str, dra_paula_knowledge: Dict = None) -> str:
        """
        Gera prompt específico para extração usando conhecimento da Dra. Paula
        """
        from dra_paula_knowledge_base import get_visa_knowledge
        
        fields_to_extract = self.get_extraction_fields_for_document(visa_type, document_type)
        visa_knowledge = get_visa_knowledge(visa_type)
        
        prompt = f"""
        [DRA. PAULA B2C - EXTRAÇÃO ESPECIALIZADA DE DOCUMENTO]
        
        Tipo de Visto: {visa_type}
        Documento: {document_type}
        
        CONHECIMENTO ESPECIALIZADO DRA. PAULA:
        {json.dumps(visa_knowledge, indent=2) if visa_knowledge else "Aplicar conhecimento geral de imigração"}
        
        CAMPOS ESPECÍFICOS PARA EXTRAIR:
        {json.dumps(fields_to_extract, indent=2)}
        
        INSTRUÇÕES DE EXTRAÇÃO:
        1. Extraia APENAS os campos listados acima que são relevantes para {visa_type}
        2. Use terminologia oficial do USCIS
        3. Mantenha formatação de datas em MM/DD/YYYY
        4. Para nomes, use EXATAMENTE como aparece no documento
        5. Para documentos brasileiros, considere padrões específicos:
           - CPF: 000.000.000-00
           - Datas: DD/MM/YYYY → converter para MM/DD/YYYY
           - Nomes: formato completo brasileiro
        
        VALIDAÇÕES ESPECÍFICAS PARA {visa_type}:
        """
        
        # Adicionar validações específicas por tipo de visto
        if visa_type == "H-1B":
            prompt += """
        - Diploma deve ser de nível superior (Bachelor ou superior)
        - LCA deve estar aprovada e válida
        - Cargo deve qualificar como "specialty occupation"
        - Salário deve atender "prevailing wage"
        """
        elif visa_type == "O-1":
            prompt += """
        - Prêmios devem ser de excelência reconhecida
        - Cartas de recomendação devem ser de especialistas qualificados
        - Evidências devem provar "extraordinary ability"
        """
        elif visa_type == "L-1":
            prompt += """
        - Comprovar 1 ano de trabalho na empresa no exterior
        - Relacionamento entre empresas deve ser claro
        - Posição deve ser executiva, gerencial ou especializada
        """
        elif visa_type == "B-1/B-2":
            prompt += """
        - Foco em vínculos com país de origem
        - Recursos financeiros suficientes
        - Propósito específico da viagem
        """
        elif visa_type == "F-1":
            prompt += """
        - I-20 deve estar válido e assinado
        - Recursos financeiros para todo o curso
        - Proficiência em inglês adequada
        """
        
        prompt += f"""
        
        RETORNE DADOS EM JSON:
        {{
            "extracted_fields": {{
                // Apenas campos encontrados da lista específica
            }},
            "validation_status": {{
                "document_valid": true/false,
                "meets_{visa_type.lower()}_requirements": true/false,
                "dra_paula_assessment": "Análise especializada"
            }},
            "recommendations": [
                "Sugestões específicas da Dra. Paula para este documento e visto"
            ]
        }}
        """
        
        return prompt

# Instância global do mapeador
visa_document_mapper = VisaDocumentMapper()

def get_visa_document_requirements(visa_type: str) -> Dict[str, Any]:
    """Função utilitária para obter requisitos de documentos"""
    return visa_document_mapper.get_required_documents_for_visa(visa_type)

def get_smart_extraction_prompt(visa_type: str, document_type: str) -> str:
    """Função utilitária para obter prompt de extração inteligente"""
    return visa_document_mapper.get_enhanced_extraction_prompt(visa_type, document_type)