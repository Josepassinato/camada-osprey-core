"""
Maria Voice Integration usando Google Gemini
Vozes naturais e humanizadas para text-to-speech
"""

import logging
import os
import base64
from typing import Dict, Any, Optional
import google.generativeai as genai
from datetime import datetime, timezone
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

# Configurar Gemini
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


class MariaVoiceService:
    """
    Serviço de voz da Maria usando Gemini
    
    Gemini oferece vozes mais naturais e humanizadas
    Suporta múltiplos idiomas incluindo Português BR
    """
    
    def __init__(self):
        self.model_name = "gemini-pro"  # Para texto
        self.available = GEMINI_API_KEY is not None
        
        if not self.available:
            logger.warning("⚠️ GEMINI_API_KEY não configurada. Voz da Maria indisponível.")
    
    async def text_to_speech(
        self,
        text: str,
        language: str = "pt-BR",
        voice_gender: str = "female",
        speaking_rate: float = 1.0,
        pitch: float = 0.0
    ) -> Dict[str, Any]:
        """
        Converte texto em áudio usando Gemini
        
        Args:
            text: Texto para converter
            language: Código do idioma (pt-BR, en-US, es-ES)
            voice_gender: Gênero da voz (female/male)
            speaking_rate: Velocidade (0.5-2.0, padrão 1.0)
            pitch: Tom da voz (-20.0 a 20.0, padrão 0.0)
        
        Returns:
            Dict com audio_content (base64) e metadados
        """
        if not self.available:
            return {
                "success": False,
                "error": "Gemini API key not configured"
            }
        
        try:
            # Nota: Gemini Text-to-Speech ainda está em preview
            # Por enquanto, vamos usar Google Cloud TTS via Gemini API
            from google.cloud import texttospeech
            
            # Configurar cliente
            client = texttospeech.TextToSpeechClient()
            
            # Configurar voz
            voice_name = self._get_voice_name(language, voice_gender)
            
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            voice = texttospeech.VoiceSelectionParams(
                language_code=language,
                name=voice_name,
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE if voice_gender == "female" else texttospeech.SsmlVoiceGender.MALE
            )
            
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=speaking_rate,
                pitch=pitch,
                effects_profile_id=['handset-class-device']  # Otimizar para telefone/chat
            )
            
            # Sintetizar
            response = client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            # Converter para base64
            audio_base64 = base64.b64encode(response.audio_content).decode('utf-8')
            
            return {
                "success": True,
                "audio_content": audio_base64,
                "format": "mp3",
                "language": language,
                "voice": voice_name,
                "duration_estimate": len(text) / 10,  # Aproximado
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erro no text-to-speech: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def speech_to_text(
        self,
        audio_data: bytes,
        language: str = "pt-BR"
    ) -> Dict[str, Any]:
        """
        Converte áudio em texto usando Gemini
        
        Args:
            audio_data: Dados do áudio (bytes)
            language: Código do idioma
        
        Returns:
            Dict com texto transcrito
        """
        if not self.available:
            return {
                "success": False,
                "error": "Gemini API key not configured"
            }
        
        try:
            from google.cloud import speech
            
            client = speech.SpeechClient()
            
            audio = speech.RecognitionAudio(content=audio_data)
            
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
                sample_rate_hertz=48000,
                language_code=language,
                enable_automatic_punctuation=True,
                model='latest_long'  # Melhor para conversação
            )
            
            response = client.recognize(config=config, audio=audio)
            
            # Extrair texto
            transcript = ""
            for result in response.results:
                transcript += result.alternatives[0].transcript + " "
            
            return {
                "success": True,
                "transcript": transcript.strip(),
                "confidence": response.results[0].alternatives[0].confidence if response.results else 0,
                "language": language,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erro no speech-to-text: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_voice_name(self, language: str, gender: str) -> str:
        """
        Retorna nome da voz mais natural para o idioma
        
        Google Cloud TTS tem vozes WaveNet e Neural2 muito naturais
        """
        # Vozes Neural2 são as mais recentes e naturais
        voice_map = {
            "pt-BR": {
                "female": "pt-BR-Neural2-A",  # Voz feminina natural brasileira
                "male": "pt-BR-Neural2-B"
            },
            "en-US": {
                "female": "en-US-Neural2-C",
                "male": "en-US-Neural2-D"
            },
            "es-ES": {
                "female": "es-ES-Neural2-A",
                "male": "es-ES-Neural2-B"
            }
        }
        
        return voice_map.get(language, {}).get(gender, "pt-BR-Neural2-A")
    
    async def get_available_voices(self, language: str = None) -> Dict[str, Any]:
        """
        Lista vozes disponíveis
        """
        try:
            from google.cloud import texttospeech
            
            client = texttospeech.TextToSpeechClient()
            
            voices = client.list_voices(language_code=language)
            
            available = []
            for voice in voices.voices:
                if "Neural" in voice.name:  # Apenas vozes neurais (melhores)
                    available.append({
                        "name": voice.name,
                        "language": voice.language_codes[0],
                        "gender": voice.ssml_gender.name
                    })
            
            return {
                "success": True,
                "voices": available,
                "total": len(available)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Singleton instance
maria_voice = MariaVoiceService()
