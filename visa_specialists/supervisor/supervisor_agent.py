"""
Supervisor Agent - Orquestrador que analisa demanda e delega para especialista correto
"""

from typing import Dict, Any, Optional
from pathlib import Path
import re


class SupervisorAgent:
    """Agente supervisor que coordena especialistas"""
    
    def __init__(self):
        self.specialists = {}
        self.visa_type_patterns = {
            'B-2': [
                r'\bb-?2\b',
                r'i-?539',
                r'tourist',
                r'turista',
                r'visitor for pleasure',
                r'extensão.*turista',
                r'extend.*tourist',
                r'medical.*emergency',
                r'extend.*stay'
            ],
            'H-1B': [
                r'\bh-?1b\b',
                r'work visa',
                r'specialty occupation',
                r'professional worker',
                r'visto de trabalho',
                r'lca',
                r'labor condition'
            ],
            'F-1': [
                r'\bf-?1\b',
                r'student',
                r'estudante',
                r'i-?20',
                r'school',
                r'university',
                r'college',
                r'transcript',
                r'histórico escolar'
            ],
            'I-130': [
                r'i-?130',
                r'family.*based',
                r'familiar',
                r'spouse',
                r'cônjuge',
                r'marriage',
                r'casamento',
                r'petition.*relative'
            ],
            'I-765': [
                r'i-?765',
                r'ead',
                r'employment authorization',
                r'autorização.*trabalho',
                r'work permit'
            ],
            'I-90': [
                r'i-?90',
                r'green card.*renew',
                r'renov.*green',
                r'replace.*green.*card',
                r'permanent.*resident.*card'
            ],
            'EB-2 NIW': [
                r'eb-?2',
                r'niw',
                r'national interest waiver',
                r'interesse nacional',
                r'advanced degree',
                r'exceptional ability'
            ],
            'EB-1A': [
                r'eb-?1a?',
                r'extraordinary ability',
                r'habilidade extraordinária',
                r'outstanding',
                r'exceptional achievements'
            ],
            'Green Card': [
                r'green card',
                r'permanent residence',
                r'residência permanente',
                r'i-?485',
                r'i-?140',
                r'i-?130',
                r'adjustment of status'
            ]
        }
    
    def register_specialist(self, visa_type: str, specialist):
        """Registra um agente especialista"""
        self.specialists[visa_type] = specialist
        print(f"✅ Especialista registrado: {visa_type}")
    
    def detect_visa_type(self, user_input: str) -> Optional[str]:
        """
        Analisa entrada do usuário e detecta tipo de visto
        
        Args:
            user_input: Texto descrevendo o que o usuário precisa
            
        Returns:
            Tipo de visto detectado ou None
        """
        user_input_lower = user_input.lower()
        
        # Contagem de matches por tipo
        matches = {}
        
        for visa_type, patterns in self.visa_type_patterns.items():
            match_count = 0
            for pattern in patterns:
                if re.search(pattern, user_input_lower):
                    match_count += 1
            if match_count > 0:
                matches[visa_type] = match_count
        
        if not matches:
            return None
        
        # Retornar tipo com mais matches
        detected_type = max(matches, key=matches.get)
        confidence = matches[detected_type]
        
        print(f"🎯 Tipo de visto detectado: {detected_type} (confiança: {confidence} matches)")
        return detected_type
    
    def analyze_request(self, user_input: str) -> Dict[str, Any]:
        """
        Analisa requisição completa do usuário
        
        Returns:
            Dicionário com análise da requisição
        """
        visa_type = self.detect_visa_type(user_input)
        
        analysis = {
            'visa_type': visa_type,
            'has_specialist': visa_type in self.specialists if visa_type else False,
            'user_input': user_input,
            'confidence': 'high' if visa_type else 'unknown'
        }
        
        return analysis
    
    def delegate_to_specialist(self, visa_type: str, applicant_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delega trabalho para especialista apropriado
        
        Args:
            visa_type: Tipo de visto
            applicant_data: Dados do aplicante
            
        Returns:
            Resultado do especialista
        """
        if visa_type not in self.specialists:
            raise ValueError(f"Nenhum especialista disponível para {visa_type}")
        
        specialist = self.specialists[visa_type]
        
        print(f"\n{'='*80}")
        print(f"🎯 DELEGANDO para especialista: {visa_type}")
        print(f"{'='*80}\n")
        
        # Especialista gera o pacote
        result = specialist.generate_package(applicant_data)
        
        return result
    
    def validate_result(self, result: Dict[str, Any], visa_type: str) -> Dict[str, Any]:
        """
        Valida resultado do especialista
        
        Args:
            result: Resultado retornado pelo especialista
            visa_type: Tipo de visto
            
        Returns:
            Resultado da validação
        """
        if visa_type not in self.specialists:
            return {'is_valid': False, 'error': 'Especialista não encontrado'}
        
        specialist = self.specialists[visa_type]
        
        # Extrair lista de documentos do resultado
        package_contents = result.get('documents', [])
        
        # Validar com o especialista
        validation = specialist.validate_package(package_contents)
        
        print(f"\n{'='*80}")
        print(f"✅ VALIDAÇÃO DO PACOTE {visa_type}")
        print(f"{'='*80}")
        print(f"Status: {'✅ VÁLIDO' if validation['is_valid'] else '❌ INVÁLIDO'}")
        
        if validation['missing_items']:
            print(f"\n❌ Itens Faltando ({len(validation['missing_items'])}):")
            for item in validation['missing_items']:
                print(f"   • {item}")
        
        if validation['forbidden_items_found']:
            print(f"\n⚠️  ERRO CRÍTICO - Documentos Proibidos Encontrados:")
            for item in validation['forbidden_items_found']:
                print(f"   • {item}")
        
        if validation['warnings']:
            print(f"\n⚠️  Avisos:")
            for warning in validation['warnings']:
                print(f"   • {warning}")
        
        print(f"\n{'='*80}\n")
        
        return validation
    
    def process_request(self, user_input: str, applicant_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa requisição completa: analisa, delega, valida
        
        Args:
            user_input: Descrição do que usuário precisa
            applicant_data: Dados do aplicante
            
        Returns:
            Resultado completo com pacote gerado e validação
        """
        # 1. Analisar requisição
        analysis = self.analyze_request(user_input)
        
        if not analysis['visa_type']:
            return {
                'success': False,
                'error': 'Não foi possível detectar o tipo de visto',
                'suggestion': 'Por favor, especifique o tipo de visto (B-2, H-1B, F-1, etc.)'
            }
        
        visa_type = analysis['visa_type']
        
        if not analysis['has_specialist']:
            return {
                'success': False,
                'error': f'Especialista para {visa_type} ainda não implementado',
                'visa_type': visa_type
            }
        
        # 2. Delegar para especialista
        try:
            result = self.delegate_to_specialist(visa_type, applicant_data)
        except Exception as e:
            return {
                'success': False,
                'error': f'Erro ao gerar pacote: {str(e)}',
                'visa_type': visa_type
            }
        
        # 3. Validar resultado
        validation = self.validate_result(result, visa_type)
        
        # 4. Retornar resultado completo
        return {
            'success': True,
            'visa_type': visa_type,
            'result': result,
            'validation': validation,
            'analysis': analysis
        }
