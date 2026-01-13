"""
ORÁCULO JURÍDICO - Consultor de Imigração
Sistema de consulta à base de conhecimento jurídica para orientar os agentes
"""

import json
import os
from typing import List, Dict, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

DEFAULT_KB_PATH = Path(__file__).resolve().parent.parent / "knowledge_base_documents.json"


class ImmigrationOracle:
    """
    Oráculo Jurídico - Consultor especializado em imigração
    Consulta a base de conhecimento para fornecer orientações sobre:
    - Documentos obrigatórios por tipo de formulário
    - Requisitos legais e processuais
    - Checklists e procedimentos
    """
    
    def __init__(self, kb_path: Optional[str] = None):
        self.kb_path = kb_path or str(DEFAULT_KB_PATH)
        self.knowledge_base = self._load_knowledge_base()
        logger.info(f"✅ Oráculo inicializado com {len(self.knowledge_base.get('documents', []))} documentos")
    
    def _load_knowledge_base(self) -> Dict:
        """Carrega a base de conhecimento do arquivo JSON"""
        try:
            if os.path.exists(self.kb_path):
                with open(self.kb_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning(f"⚠️ Arquivo de knowledge base não encontrado: {self.kb_path}")
                return {'documents': []}
        except Exception as e:
            logger.error(f"❌ Erro ao carregar knowledge base: {str(e)}")
            return {'documents': []}
    
    def consult_form_requirements(self, form_code: str) -> Dict:
        """
        Consulta os requisitos para um formulário específico
        
        Args:
            form_code: Código do formulário (ex: I-539, I-130, I-765)
        
        Returns:
            Dict com informações sobre o formulário
        """
        form_code_clean = form_code.upper().replace("FORM ", "").strip()
        
        relevant_docs = []
        for doc in self.knowledge_base.get('documents', []):
            if form_code_clean in doc['filename'].upper():
                relevant_docs.append(doc)
        
        if not relevant_docs:
            return {
                'form_code': form_code,
                'found': False,
                'message': f'Nenhuma informação específica encontrada para {form_code}'
            }
        
        # Compilar informações
        guide_text = ""
        for doc in relevant_docs:
            guide_text += doc['text'] + "\n\n"
        
        return {
            'form_code': form_code,
            'found': True,
            'guide_text': guide_text,
            'documents_found': len(relevant_docs),
            'document_names': [doc['filename'] for doc in relevant_docs]
        }
    
    def get_required_documents(self, form_code: str, visa_category: Optional[str] = None) -> List[str]:
        """
        Retorna lista de documentos obrigatórios para um formulário
        
        Args:
            form_code: Código do formulário
            visa_category: Categoria do visto (opcional, ex: F-1, B-2)
        
        Returns:
            Lista de documentos obrigatórios
        """
        # Mapeamento baseado em conhecimento comum + knowledge base
        common_requirements = {
            'I-539': [
                'Form I-539 (Application to Extend/Change Status)',
                'I-94 Arrival/Departure Record',
                'Current visa copy',
                'Passport (valid for at least 6 months)',
                'Filing fee receipt ($370)',
                'Letter explaining reason for extension/change',
                'Evidence of financial support',
                'Evidence of nonimmigrant intent (ties to home country)'
            ],
            'I-130': [
                'Form I-130 (Petition for Alien Relative)',
                'Proof of U.S. citizenship or lawful permanent residence',
                'Proof of relationship (marriage certificate, birth certificate)',
                'Passport-style photos (2 for each person)',
                'Filing fee receipt ($535)',
                'Form I-864 (Affidavit of Support)',
                'Evidence of bona fide relationship'
            ],
            'I-765': [
                'Form I-765 (Application for Employment Authorization)',
                'I-94 Arrival/Departure Record',
                'Passport-style photos (2)',
                'Copy of previous EAD (if renewing)',
                'Filing fee receipt ($410)',
                'Supporting documentation for eligibility category'
            ],
            'I-485': [
                'Form I-485 (Application to Adjust Status)',
                'Birth certificate',
                'Passport-style photos (2)',
                'Form I-693 (Medical Examination)',
                'Form I-864 (Affidavit of Support)',
                'I-94 Arrival/Departure Record',
                'Employment authorization document (if applicable)',
                'Filing fees ($1,140 + biometrics $85)'
            ]
        }
        
        # Adicionar requisitos específicos para categorias de visto
        if form_code == 'I-539' and visa_category:
            if visa_category == 'F-1':
                return common_requirements.get('I-539', []) + [
                    'Form I-20 (Certificate of Eligibility)',
                    'SEVIS fee receipt (Form I-901)',
                    'Proof of financial support for education',
                    'Letter of acceptance from school',
                    'Academic transcripts',
                    'Proof of English proficiency (if required)'
                ]
            elif visa_category == 'H-1B':
                return common_requirements.get('I-539', []) + [
                    'Form I-129 approval notice',
                    'Labor Condition Application (LCA)',
                    'Employment verification letter',
                    'Educational credentials evaluation'
                ]
        
        return common_requirements.get(form_code, [
            f'Documentação padrão para {form_code}',
            'Entre em contato com especialista para lista completa'
        ])
    
    def consult_general(self, query: str) -> Dict:
        """
        Consulta geral à base de conhecimento
        
        Args:
            query: Pergunta ou tópico a consultar
        
        Returns:
            Dict com informações relevantes
        """
        query_lower = query.lower()
        relevant_docs = []
        
        # Buscar documentos relevantes
        for doc in self.knowledge_base.get('documents', []):
            doc_text_lower = doc['text'].lower()
            doc_name_lower = doc['filename'].lower()
            
            # Busca simples por palavras-chave
            if any(word in doc_text_lower or word in doc_name_lower 
                   for word in query_lower.split()):
                relevant_docs.append({
                    'filename': doc['filename'],
                    'category': doc['category'],
                    'preview': doc['text'][:300] + '...' if len(doc['text']) > 300 else doc['text']
                })
        
        return {
            'query': query,
            'results_found': len(relevant_docs),
            'relevant_documents': relevant_docs[:5]  # Top 5
        }
    
    def get_processing_times(self, form_code: str) -> Dict:
        """
        Retorna tempos de processamento estimados
        (Dados fictícios - em produção, consultar API do USCIS)
        """
        processing_times = {
            'I-539': '3-6 months',
            'I-130': '12-18 months',
            'I-765': '3-5 months',
            'I-485': '10-24 months',
            'N-400': '8-12 months'
        }
        
        return {
            'form_code': form_code,
            'estimated_time': processing_times.get(form_code, 'Varies'),
            'note': 'Processing times vary by service center and case complexity'
        }
    
    def validate_document_checklist(self, form_code: str, submitted_docs: List[str]) -> Dict:
        """
        Valida se todos os documentos obrigatórios foram submetidos
        
        Args:
            form_code: Código do formulário
            submitted_docs: Lista de documentos submetidos
        
        Returns:
            Dict com status da validação
        """
        required = self.get_required_documents(form_code)
        
        # Simplificar nomes para comparação
        submitted_simple = [doc.lower().replace('-', '').replace('_', '') for doc in submitted_docs]
        
        missing = []
        for req in required:
            req_simple = req.lower().replace('-', '').replace('_', '')
            # Busca parcial
            if not any(req_simple[:15] in sub for sub in submitted_simple):
                missing.append(req)
        
        return {
            'form_code': form_code,
            'total_required': len(required),
            'total_submitted': len(submitted_docs),
            'missing_documents': missing,
            'complete': len(missing) == 0,
            'completion_percentage': ((len(required) - len(missing)) / len(required) * 100) if required else 0
        }


# Instância global do oráculo
oracle = ImmigrationOracle()


def consult_oracle(query_type: str, **kwargs) -> Dict:
    """
    Função helper para consultar o oráculo
    
    Args:
        query_type: Tipo de consulta ('form_requirements', 'documents', 'general', 'processing_times', 'validate')
        **kwargs: Parâmetros específicos para cada tipo de consulta
    
    Returns:
        Dict com resultado da consulta
    """
    if query_type == 'form_requirements':
        return oracle.consult_form_requirements(kwargs.get('form_code', ''))
    
    elif query_type == 'documents':
        return {
            'required_documents': oracle.get_required_documents(
                kwargs.get('form_code', ''),
                kwargs.get('visa_category')
            )
        }
    
    elif query_type == 'general':
        return oracle.consult_general(kwargs.get('query', ''))
    
    elif query_type == 'processing_times':
        return oracle.get_processing_times(kwargs.get('form_code', ''))
    
    elif query_type == 'validate':
        return oracle.validate_document_checklist(
            kwargs.get('form_code', ''),
            kwargs.get('submitted_docs', [])
        )
    
    else:
        return {
            'error': 'Invalid query type',
            'valid_types': ['form_requirements', 'documents', 'general', 'processing_times', 'validate']
        }
