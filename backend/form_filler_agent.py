"""
AGENTE DE PREENCHIMENTO DE FORMULÁRIOS
Especialidade: Automação de preenchimento de formulários USCIS
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone
import json
import os
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_KB_PATH = Path(__file__).resolve().parent.parent / "knowledge_base_documents.json"


class FormFillerAgent:
    """
    Agente especializado em preenchimento automático de formulários
    - Mapeia dados do usuário para campos de formulários
    - Valida dados antes de preencher
    - Gera formulários preenchidos
    - Detecta campos obrigatórios faltantes
    """
    
    def __init__(self, knowledge_base_path: Optional[str] = None):
        self.form_mappings = self._load_form_mappings()
        kb_path = knowledge_base_path or str(DEFAULT_KB_PATH)
        self.knowledge_base = self._load_knowledge_base(kb_path)
        logger.info(f"✅ Form Filler Agent inicializado com {len(self.knowledge_base.get('documents', []))} documentos de referência")
    
    def _load_knowledge_base(self, kb_path: str) -> Dict:
        """Carrega a base de conhecimento"""
        try:
            if os.path.exists(kb_path):
                with open(kb_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {'documents': []}
        except Exception as e:
            logger.error(f"Erro ao carregar KB: {str(e)}")
            return {'documents': []}
    
    def _load_form_mappings(self) -> Dict:
        """
        Carrega mapeamentos de campos para cada formulário
        """
        return {
            'I-539': {
                'fields': {
                    'part1_1_family_name': 'basic_data.full_name.last',
                    'part1_2_given_name': 'basic_data.full_name.first',
                    'part1_3_middle_name': 'basic_data.full_name.middle',
                    'part1_4_date_of_birth': 'basic_data.date_of_birth',
                    'part1_5_country_of_birth': 'basic_data.country_of_birth',
                    'part1_6_country_of_citizenship': 'basic_data.nationality',
                    'part1_7_passport_number': 'basic_data.passport_number',
                    'part1_8_i94_number': 'basic_data.i94_number',
                    'part2_current_status': 'basic_data.current_status',
                    'part2_status_expires': 'basic_data.current_status_expires',
                    'part2_requested_status': 'basic_data.requested_status',
                    'part3_address_street': 'basic_data.address.street',
                    'part3_address_city': 'basic_data.address.city',
                    'part3_address_state': 'basic_data.address.state',
                    'part3_address_zip': 'basic_data.address.zip',
                    'part4_school_name': 'f1_data.school_name',
                    'part4_sevis_id': 'f1_data.sevis_number',
                    'part4_program_start': 'f1_data.program_start_date'
                },
                'required_fields': [
                    'part1_1_family_name', 'part1_2_given_name',
                    'part1_4_date_of_birth', 'part1_7_passport_number'
                ]
            },
            'I-130': {
                'fields': {
                    'part1_family_name': 'petitioner.family_name',
                    'part1_given_name': 'petitioner.given_name',
                    'part1_address': 'petitioner.address',
                    'part2_beneficiary_family_name': 'beneficiary.family_name',
                    'part2_beneficiary_given_name': 'beneficiary.given_name',
                    'part2_relationship': 'relationship.type'
                },
                'required_fields': [
                    'part1_family_name', 'part1_given_name',
                    'part2_beneficiary_family_name'
                ]
            },
            'I-765': {
                'fields': {
                    'part1_family_name': 'basic_data.full_name.last',
                    'part1_given_name': 'basic_data.full_name.first',
                    'part1_date_of_birth': 'basic_data.date_of_birth',
                    'part1_i94_number': 'basic_data.i94_number',
                    'part2_eligibility_category': 'ead_data.eligibility_category'
                },
                'required_fields': [
                    'part1_family_name', 'part1_given_name',
                    'part2_eligibility_category'
                ]
            }
        }
    
    def fill_form(self, form_code: str, user_data: Dict) -> Dict:
        """
        Preenche um formulário com dados do usuário
        
        Args:
            form_code: Código do formulário (I-539, I-130, etc)
            user_data: Dados do usuário (do banco de dados)
        
        Returns:
            Dict com formulário preenchido e status
        """
        try:
            if form_code not in self.form_mappings:
                return {
                    'success': False,
                    'error': f'Form {form_code} not supported',
                    'supported_forms': list(self.form_mappings.keys())
                }
            
            form_config = self.form_mappings[form_code]
            
            # Preencher campos
            filled_fields = {}
            missing_required = []
            
            for field_name, data_path in form_config['fields'].items():
                value = self._get_nested_value(user_data, data_path)
                
                if value:
                    filled_fields[field_name] = value
                elif field_name in form_config['required_fields']:
                    missing_required.append(field_name)
            
            # Validar campos obrigatórios
            is_complete = len(missing_required) == 0
            completion_percentage = (len(filled_fields) / len(form_config['fields'])) * 100
            
            return {
                'success': True,
                'form_code': form_code,
                'filled_fields': filled_fields,
                'total_fields': len(form_config['fields']),
                'filled_count': len(filled_fields),
                'missing_required': missing_required,
                'is_complete': is_complete,
                'completion_percentage': round(completion_percentage, 2),
                'filled_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao preencher formulário: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'form_code': form_code
            }
    
    def _get_nested_value(self, data: Dict, path: str) -> Optional[str]:
        """
        Obtém valor de um caminho aninhado (ex: 'basic_data.full_name.last')
        """
        try:
            keys = path.split('.')
            value = data
            
            for key in keys:
                if isinstance(value, dict):
                    value = value.get(key)
                else:
                    return None
            
            return str(value) if value is not None else None
        except:
            return None
    
    def validate_field_data(self, field_name: str, value: str, field_type: str) -> Dict:
        """
        Valida dados de um campo específico
        
        Args:
            field_name: Nome do campo
            value: Valor a validar
            field_type: Tipo do campo (date, text, number, etc)
        
        Returns:
            Dict com resultado da validação
        """
        is_valid = True
        errors = []
        
        if field_type == 'date':
            # Validar formato de data
            try:
                datetime.strptime(value, '%Y-%m-%d')
            except:
                is_valid = False
                errors.append('Invalid date format. Expected: YYYY-MM-DD')
        
        elif field_type == 'passport':
            # Validar número de passaporte
            if not value or len(value) < 5:
                is_valid = False
                errors.append('Passport number too short')
        
        elif field_type == 'i94':
            # Validar I-94 number (11 dígitos)
            if not value.isdigit() or len(value) != 11:
                is_valid = False
                errors.append('I-94 must be 11 digits')
        
        elif field_type == 'sevis':
            # Validar SEVIS ID (formato N1234567890)
            if not value.startswith('N') or len(value) != 11:
                is_valid = False
                errors.append('SEVIS ID must start with N and be 11 characters')
        
        return {
            'field_name': field_name,
            'is_valid': is_valid,
            'errors': errors,
            'value': value
        }
    
    def get_missing_fields(self, form_code: str, user_data: Dict) -> List[str]:
        """
        Retorna lista de campos obrigatórios que estão faltando
        """
        if form_code not in self.form_mappings:
            return []
        
        form_config = self.form_mappings[form_code]
        missing = []
        
        for field_name in form_config['required_fields']:
            data_path = form_config['fields'].get(field_name)
            if data_path:
                value = self._get_nested_value(user_data, data_path)
                if not value:
                    missing.append({
                        'field_name': field_name,
                        'data_path': data_path,
                        'description': self._get_field_description(field_name)
                    })
        
        return missing
    
    def _get_field_description(self, field_name: str) -> str:
        """
        Retorna descrição amigável do campo
        """
        descriptions = {
            'part1_1_family_name': 'Family Name (Last Name)',
            'part1_2_given_name': 'Given Name (First Name)',
            'part1_4_date_of_birth': 'Date of Birth',
            'part1_7_passport_number': 'Passport Number',
            'part1_8_i94_number': 'I-94 Arrival/Departure Number',
            'part2_current_status': 'Current Immigration Status',
            'part4_sevis_id': 'SEVIS ID Number'
        }
        return descriptions.get(field_name, field_name.replace('_', ' ').title())
    
    def generate_field_map(self, form_code: str) -> Dict:
        """
        Gera mapa de campos para um formulário
        Útil para UI dinâmica
        """
        if form_code not in self.form_mappings:
            return {}
        
        form_config = self.form_mappings[form_code]
        field_map = []
        
        for field_name, data_path in form_config['fields'].items():
            field_map.append({
                'field_name': field_name,
                'data_path': data_path,
                'description': self._get_field_description(field_name),
                'is_required': field_name in form_config['required_fields']
            })
        
        return {
            'form_code': form_code,
            'total_fields': len(field_map),
            'required_fields': len(form_config['required_fields']),
            'fields': field_map
        }
    
    def auto_suggest_values(self, field_name: str, context: Dict) -> List[str]:
        """
        Sugere valores para um campo baseado no contexto
        """
        suggestions = []
        
        # Lógica de sugestões baseada no tipo de campo
        if 'country' in field_name.lower():
            suggestions = ['Brazil', 'United States', 'Mexico', 'Canada']
        elif 'status' in field_name.lower():
            suggestions = ['B-2', 'F-1', 'H-1B', 'L-1']
        
        return suggestions
    
    def get_form_guide_from_kb(self, form_code: str) -> Dict:
        """
        Busca o guia completo de preenchimento do formulário na KB
        """
        form_guides = []
        
        for doc in self.knowledge_base.get('documents', []):
            if form_code in doc.get('filename', ''):
                form_guides.append({
                    'filename': doc['filename'],
                    'category': doc['category'],
                    'guide_text': doc['text'],
                    'full_length': doc.get('full_length', 0)
                })
        
        if form_guides:
            return {
                'form_code': form_code,
                'guides_found': len(form_guides),
                'primary_guide': form_guides[0],
                'all_guides': form_guides
            }
        
        return {
            'form_code': form_code,
            'guides_found': 0,
            'message': f'Nenhum guia encontrado para {form_code} na base de conhecimento'
        }
    
    def get_field_instructions(self, form_code: str, field_name: str) -> Dict:
        """
        Busca instruções específicas para um campo do formulário
        """
        guide = self.get_form_guide_from_kb(form_code)
        
        if guide.get('guides_found', 0) > 0:
            guide_text = guide['primary_guide']['guide_text']
            
            # Buscar menções ao campo no guia
            instructions = []
            lines = guide_text.split('\n')
            for i, line in enumerate(lines):
                if field_name.lower() in line.lower():
                    # Pegar contexto (linha anterior, atual e próxima)
                    context_lines = lines[max(0, i-1):min(len(lines), i+2)]
                    instructions.append('\n'.join(context_lines))
            
            return {
                'field_name': field_name,
                'form_code': form_code,
                'instructions_found': len(instructions),
                'instructions': instructions[:2]  # Top 2
            }
        
        return {
            'field_name': field_name,
            'form_code': form_code,
            'instructions_found': 0
        }


# Instância global
form_filler = FormFillerAgent()


def fill_form_automatically(form_code: str, user_data: Dict) -> Dict:
    """
    Helper function para preenchimento automático
    """
    return form_filler.fill_form(form_code, user_data)
