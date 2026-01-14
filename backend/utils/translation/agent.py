"""
AGENTE DE TRADUÇÃO
Especialidade: Tradução de documentos multilíngues para inglês/português
"""

import logging
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class TranslationAgent:
    """
    Agente especializado em tradução de documentos
    - Tradução de documentos para inglês (USCIS requirements)
    - Tradução para português (para usuários brasileiros)
    - Validação de traduções oficiais
    - Detecção de idioma
    - Tradução certificada (mock)
    """
    
    def __init__(self):
        self.supported_languages = {
            'pt': 'Portuguese',
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'zh': 'Chinese',
            'ar': 'Arabic'
        }
        
        # Glossário jurídico/imigração
        self.legal_glossary = self._load_legal_glossary()
        
        logger.info("✅ Translation Agent inicializado")
    
    def _load_legal_glossary(self) -> Dict:
        """
        Carrega glossário de termos jurídicos e de imigração
        """
        return {
            'pt_to_en': {
                'certidão de nascimento': 'birth certificate',
                'certidão de casamento': 'marriage certificate',
                'diploma': 'diploma',
                'histórico escolar': 'academic transcript',
                'comprovante de residência': 'proof of residence',
                'comprovante de renda': 'proof of income',
                'extrato bancário': 'bank statement',
                'procuração': 'power of attorney',
                'visto': 'visa',
                'passaporte': 'passport',
                'carteira de identidade': 'identity card',
                'CPF': 'Brazilian Tax ID (CPF)',
                'RG': 'Brazilian ID Card (RG)',
                'carteira de trabalho': 'work permit',
                'declaração de imposto de renda': 'tax return',
                'atestado médico': 'medical certificate'
            },
            'en_to_pt': {
                'birth certificate': 'certidão de nascimento',
                'marriage certificate': 'certidão de casamento',
                'diploma': 'diploma',
                'transcript': 'histórico escolar',
                'bank statement': 'extrato bancário',
                'visa': 'visto',
                'passport': 'passaporte',
                'green card': 'green card (residência permanente)',
                'work permit': 'permissão de trabalho',
                'sponsor': 'patrocinador',
                'petition': 'petição',
                'application': 'aplicação/solicitação'
            }
        }
    
    def translate_document(self, text: str, source_lang: str, target_lang: str, 
                          document_type: Optional[str] = None) -> Dict:
        """
        Traduz texto de um idioma para outro
        
        Args:
            text: Texto a ser traduzido
            source_lang: Código do idioma de origem (pt, en, es)
            target_lang: Código do idioma de destino
            document_type: Tipo de documento (opcional, para contexto)
        
        Returns:
            Dict com tradução e metadados
        """
        try:
            if source_lang == target_lang:
                return {
                    'success': True,
                    'translated_text': text,
                    'source_lang': source_lang,
                    'target_lang': target_lang,
                    'note': 'Source and target languages are the same'
                }
            
            # Aplicar glossário de termos jurídicos
            translated_text = self._apply_glossary(text, source_lang, target_lang)
            
            # Simular tradução (em produção: usar Google Translate API, DeepL, etc)
            if not translated_text:
                translated_text = self._translate_simulated(text, source_lang, target_lang)
            
            # Validar qualidade da tradução
            quality_score = self._assess_translation_quality(text, translated_text)
            
            return {
                'success': True,
                'source_text': text[:200] + '...' if len(text) > 200 else text,
                'translated_text': translated_text,
                'source_lang': source_lang,
                'target_lang': target_lang,
                'source_lang_name': self.supported_languages.get(source_lang, 'Unknown'),
                'target_lang_name': self.supported_languages.get(target_lang, 'Unknown'),
                'document_type': document_type,
                'quality_score': quality_score,
                'word_count': len(text.split()),
                'translated_at': datetime.now(timezone.utc).isoformat(),
                'is_certified': False,  # Requer certificação oficial
                'note': 'This is an automated translation. USCIS requires certified translations for official documents.'
            }
            
        except Exception as e:
            logger.error(f"Erro ao traduzir documento: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'source_lang': source_lang,
                'target_lang': target_lang
            }
    
    def _apply_glossary(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """
        Aplica glossário de termos jurídicos/imigração
        """
        glossary_key = f"{source_lang}_to_{target_lang}"
        glossary = self.legal_glossary.get(glossary_key, {})
        
        if not glossary:
            return None
        
        translated = text
        for source_term, target_term in glossary.items():
            # Substituir termos (case insensitive)
            pattern = re.compile(re.escape(source_term), re.IGNORECASE)
            translated = pattern.sub(target_term, translated)
        
        # Se nenhuma substituição foi feita, retornar None
        return translated if translated != text else None
    
    def _translate_simulated(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Simula tradução (em produção: usar API real)
        """
        # Simulações simples
        if source_lang == 'pt' and target_lang == 'en':
            return f"[EN] {text}"
        elif source_lang == 'en' and target_lang == 'pt':
            return f"[PT] {text}"
        else:
            return f"[{target_lang.upper()}] {text}"
    
    def _assess_translation_quality(self, source: str, translation: str) -> float:
        """
        Avalia a qualidade da tradução
        """
        # Critérios simples de qualidade
        source_words = len(source.split())
        translation_words = len(translation.split())
        
        # Espera-se que a tradução tenha tamanho similar
        ratio = min(source_words, translation_words) / max(source_words, translation_words)
        
        # Score de 0-100
        quality_score = ratio * 100
        
        return round(quality_score, 2)
    
    def detect_language(self, text: str) -> Dict:
        """
        Detecta o idioma de um texto
        """
        # Palavras-chave por idioma (detecção simples)
        language_keywords = {
            'pt': ['de', 'da', 'do', 'para', 'com', 'que', 'em', 'não', 'é', 'os'],
            'en': ['the', 'of', 'and', 'to', 'in', 'is', 'you', 'that', 'it', 'for'],
            'es': ['el', 'la', 'de', 'que', 'y', 'en', 'los', 'del', 'se', 'las']
        }
        
        text_lower = text.lower()
        scores = {}
        
        for lang, keywords in language_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower.split())
            scores[lang] = score
        
        detected_lang = max(scores, key=scores.get) if scores else 'unknown'
        confidence = (scores.get(detected_lang, 0) / len(text.split())) * 100
        
        return {
            'detected_language': detected_lang,
            'language_name': self.supported_languages.get(detected_lang, 'Unknown'),
            'confidence': min(round(confidence, 2), 100),
            'all_scores': scores
        }
    
    def create_certified_translation(self, original_text: str, translated_text: str,
                                    source_lang: str, target_lang: str,
                                    translator_name: str, translator_credentials: str) -> Dict:
        """
        Cria uma tradução certificada (mock)
        USCIS requer traduções certificadas para documentos oficiais
        """
        certification_statement = f"""
TRANSLATOR'S CERTIFICATION

I, {translator_name}, certify that I am competent to translate from {self.supported_languages.get(source_lang)} 
to {self.supported_languages.get(target_lang)}, and that the above translation is accurate and complete 
to the best of my knowledge and belief.

Translator's Credentials: {translator_credentials}
Date: {datetime.now(timezone.utc).strftime('%B %d, %Y')}

Signature: ________________________
{translator_name}
"""
        
        certified_document = f"""
{'='*80}
CERTIFIED TRANSLATION
{'='*80}

ORIGINAL TEXT ({self.supported_languages.get(source_lang)}):
{'-'*80}
{original_text}

TRANSLATED TEXT ({self.supported_languages.get(target_lang)}):
{'-'*80}
{translated_text}

{certification_statement}
{'='*80}
"""
        
        return {
            'success': True,
            'certified_document': certified_document,
            'translator_name': translator_name,
            'certification_date': datetime.now(timezone.utc).isoformat(),
            'is_uscis_compliant': True,
            'note': 'This is a simulated certified translation. For official use, hire a professional certified translator.'
        }
    
    def translate_form_labels(self, form_code: str, target_lang: str = 'pt') -> Dict:
        """
        Traduz labels de formulários para outro idioma
        Útil para interface multilíngue
        """
        # Mapeamento de labels comuns
        common_labels = {
            'en': {
                'full_name': 'Full Name',
                'date_of_birth': 'Date of Birth',
                'passport_number': 'Passport Number',
                'address': 'Address',
                'phone': 'Phone Number',
                'email': 'Email Address',
                'current_status': 'Current Immigration Status',
                'i94_number': 'I-94 Number'
            },
            'pt': {
                'full_name': 'Nome Completo',
                'date_of_birth': 'Data de Nascimento',
                'passport_number': 'Número do Passaporte',
                'address': 'Endereço',
                'phone': 'Número de Telefone',
                'email': 'Email',
                'current_status': 'Status de Imigração Atual',
                'i94_number': 'Número I-94'
            }
        }
        
        return {
            'form_code': form_code,
            'target_lang': target_lang,
            'labels': common_labels.get(target_lang, common_labels['en'])
        }
    
    def batch_translate(self, texts: List[str], source_lang: str, target_lang: str) -> Dict:
        """
        Traduz múltiplos textos de uma vez
        """
        translations = []
        
        for i, text in enumerate(texts):
            result = self.translate_document(text, source_lang, target_lang)
            translations.append({
                'index': i,
                'original': text[:100] + '...' if len(text) > 100 else text,
                'translated': result.get('translated_text', '')[:100] + '...' if len(result.get('translated_text', '')) > 100 else result.get('translated_text', ''),
                'success': result.get('success', False)
            })
        
        return {
            'success': True,
            'total_texts': len(texts),
            'translations': translations,
            'batch_translated_at': datetime.now(timezone.utc).isoformat()
        }


# Instância global
translator = TranslationAgent()


def translate_text(text: str, source_lang: str, target_lang: str) -> Dict:
    """
    Helper function para tradução
    """
    return translator.translate_document(text, source_lang, target_lang)
