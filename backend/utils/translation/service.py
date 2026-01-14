"""
Translation Service - Serviço de Tradução Automática
Traduz respostas do usuário para inglês usando OpenAI via Portkey
"""

import logging
import os
from typing import Dict

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

# Get OpenAI API key
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


class TranslationService:
    """
    Serviço de tradução automática para formulários USCIS
    Traduz respostas do usuário de qualquer idioma para inglês formal
    """

    def __init__(self):
        self.api_key = OPENAI_API_KEY
        self.available = OPENAI_API_KEY is not None
        self.client = AsyncOpenAI(api_key=self.api_key) if self.available else None

        if not self.available:
            logger.warning("⚠️ OPENAI_API_KEY not configured - translation disabled")
        else:
            logger.info("✅ Translation service initialized with OpenAI")

    async def translate_field(
        self, text: str, source_language: str = "pt", context: str = None
    ) -> Dict:
        """
        Traduz um campo específico para inglês

        Args:
            text: Texto a ser traduzido
            source_language: Idioma de origem (pt, es, fr, etc)
            context: Contexto do campo (ex: "Nome completo", "Endereço")

        Returns:
            Dict com tradução e metadata
        """
        if not self.available:
            return {
                "success": False,
                "error": "Translation service not available",
                "original": text,
                "translated": text,
            }

        if not text or not text.strip():
            return {"success": True, "original": text, "translated": text, "skipped": True}

        try:
            # Criar prompt para tradução contextualizada
            prompt = self._create_translation_prompt(text, source_language, context)

            # Call OpenAI for translation
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",  # Fast and cost-effective for translation
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional translator for USCIS immigration forms. Translate accurately and formally.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,  # Low temperature for consistent translations
                max_tokens=500,
            )

            # Extrair tradução
            translated_text = response.choices[0].message.content.strip()

            # Remover aspas se existirem
            if translated_text.startswith('"') and translated_text.endswith('"'):
                translated_text = translated_text[1:-1]
            if translated_text.startswith("'") and translated_text.endswith("'"):
                translated_text = translated_text[1:-1]

            logger.info(f"✅ Tradução: '{text[:50]}...' → '{translated_text[:50]}...'")

            return {
                "success": True,
                "original": text,
                "translated": translated_text,
                "source_language": source_language,
                "context": context,
            }

        except Exception as e:
            logger.error(f"❌ Erro na tradução: {e}")
            return {
                "success": False,
                "error": str(e),
                "original": text,
                "translated": text,  # Fallback para texto original
            }

    async def translate_form_data(
        self, form_data: Dict, source_language: str = "pt", field_contexts: Dict[str, str] = None
    ) -> Dict:
        """
        Traduz todos os campos de um formulário

        Args:
            form_data: Dicionário com dados do formulário
            source_language: Idioma de origem
            field_contexts: Dicionário mapeando campo → contexto/descrição

        Returns:
            Dict com dados traduzidos
        """
        if not self.available:
            logger.warning("⚠️ Translation service not available, returning original data")
            return {
                "success": False,
                "translated_data": form_data,
                "original_data": form_data,
                "error": "Translation service not available",
            }

        try:
            translated_data = {}
            translations_log = []
            field_contexts = field_contexts or {}

            for field, value in form_data.items():
                # Pular campos que não precisam tradução
                if self._should_skip_translation(field, value):
                    translated_data[field] = value
                    continue

                # Se for string, traduzir
                if isinstance(value, str):
                    context = field_contexts.get(field, field)
                    result = await self.translate_field(value, source_language, context)

                    if result.get("success"):
                        translated_data[field] = result["translated"]
                        translations_log.append(
                            {"field": field, "original": value, "translated": result["translated"]}
                        )
                    else:
                        translated_data[field] = value

                # Se for lista, traduzir cada item
                elif isinstance(value, list):
                    translated_list = []
                    for item in value:
                        if isinstance(item, str):
                            result = await self.translate_field(item, source_language, field)
                            translated_list.append(result.get("translated", item))
                        else:
                            translated_list.append(item)
                    translated_data[field] = translated_list

                # Se for dict, processar recursivamente
                elif isinstance(value, dict):
                    sub_result = await self.translate_form_data(
                        value, source_language, field_contexts
                    )
                    translated_data[field] = sub_result.get("translated_data", value)

                else:
                    translated_data[field] = value

            logger.info(f"✅ Formulário traduzido: {len(translations_log)} campos")

            return {
                "success": True,
                "translated_data": translated_data,
                "original_data": form_data,
                "translations_count": len(translations_log),
                "translations_log": translations_log,
                "source_language": source_language,
            }

        except Exception as e:
            logger.error(f"❌ Erro ao traduzir formulário: {e}")
            return {
                "success": False,
                "error": str(e),
                "translated_data": form_data,
                "original_data": form_data,
            }

    def _create_translation_prompt(
        self, text: str, source_language: str, context: str = None
    ) -> str:
        """Cria prompt para tradução contextualizada"""

        language_names = {
            "pt": "Portuguese",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "zh": "Chinese",
            "ja": "Japanese",
            "ko": "Korean",
            "ar": "Arabic",
            "ru": "Russian",
        }

        source_lang_name = language_names.get(source_language, source_language)

        if context:
            prompt = f"""Translate the following {source_lang_name} text to formal English for a USCIS immigration form.

Context: This is for the field "{context}"

Text to translate:
{text}

Important:
- Translate to formal, professional English
- Keep names and proper nouns as they are
- Maintain capitalization for names
- Return ONLY the translated text, nothing else"""
        else:
            prompt = f"""Translate the following {source_lang_name} text to formal English for a USCIS immigration form.

Text:
{text}

Return ONLY the translated text, nothing else."""

        return prompt

    def _should_skip_translation(self, field: str, value) -> bool:
        """Determina se um campo deve ser pulado na tradução"""

        # Campos que não precisam tradução
        skip_fields = [
            "id",
            "case_id",
            "user_id",
            "email",
            "phone",
            "date",
            "number",
            "passport_number",
            "a_number",
            "ssn",
            "zip_code",
            "postal_code",
            "country_code",
            "area_code",
            "extension",
            "created_at",
            "updated_at",
            "timestamp",
        ]

        field_lower = field.lower()

        # Pular campos específicos
        if any(skip in field_lower for skip in skip_fields):
            return True

        # Pular valores não-string ou vazios
        if not isinstance(value, str) or not value.strip():
            return True

        # Pular se parecer ser um código, número, data
        if value.replace("-", "").replace("/", "").replace(".", "").replace(" ", "").isdigit():
            return True

        # Pular se for email
        if "@" in value and "." in value:
            return True

        # Pular URLs
        if value.startswith("http://") or value.startswith("https://"):
            return True

        return False


# Singleton instance
translation_service = TranslationService()


# Funções auxiliares para uso direto
async def translate_text(text: str, source_language: str = "pt", context: str = None) -> str:
    """
    Traduz um texto simples

    Returns:
        String traduzida
    """
    result = await translation_service.translate_field(text, source_language, context)
    return result.get("translated", text)


async def translate_form(form_data: Dict, source_language: str = "pt") -> Dict:
    """
    Traduz dados de formulário

    Returns:
        Dict com dados traduzidos
    """
    result = await translation_service.translate_form_data(form_data, source_language)
    return result.get("translated_data", form_data)
