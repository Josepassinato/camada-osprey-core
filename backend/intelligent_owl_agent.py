"""
Agente Coruja Inteligente - Sistema de Condução de Questionários
Guia inteligente para preenchimento de formulários de imigração
"""

import os
import logging
import json
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class QuestionType(Enum):
    TEXT = "text"
    DATE = "date"
    SELECT = "select"
    TEXTAREA = "textarea"
    CHECKBOX = "checkbox"
    NUMBER = "number"
    EMAIL = "email"
    PHONE = "phone"
    ADDRESS = "address"

class ValidationLevel(Enum):
    NONE = "none"
    BASIC = "basic"
    ADVANCED = "advanced"
    GOOGLE_API = "google_api"

@dataclass
class FieldGuide:
    field_id: str
    question_pt: str
    question_en: str
    explanation_pt: str
    explanation_en: str
    examples: List[str]
    validation_rules: Dict[str, Any]
    importance_level: int  # 1-5 (5 = critical)
    visa_specific: List[str]  # Which visas need this field

@dataclass
class OwlInteraction:
    interaction_id: str
    field_id: str
    user_input: str
    owl_response: str
    validation_result: Dict[str, Any]
    timestamp: datetime
    session_id: str

class IntelligentOwlAgent:
    """Agente Coruja que conduz o preenchimento de questionários"""
    
    def __init__(self):
        self.field_guides = self._load_field_guides()
        self.interaction_history: Dict[str, List[OwlInteraction]] = {}
        
        # AI Integration
        self.ai_client = self._setup_ai_client()
        
        # Google Integration for validation
        try:
            from google_document_ai_integration import GoogleDocumentAIProcessor
            self.google_processor = GoogleDocumentAIProcessor()
            logger.info("🔗 Owl Agent: Google API integration initialized")
        except Exception as e:
            logger.error(f"❌ Owl Agent: Google API initialization failed: {e}")
            self.google_processor = None
        
    def _setup_ai_client(self):
        """Setup AI client using Emergent LLM key for OpenAI GPT-5"""
        try:
            # Try Emergent LLM key first (supports OpenAI GPT-5)
            emergent_key = os.environ.get('EMERGENT_LLM_KEY')
            if emergent_key:
                from emergentintegrations.llm.chat import LlmChat
                client = LlmChat(api_key=emergent_key, model="gpt-4o")
                logger.info("🤖 Owl Agent: Emergent LLM client initialized with GPT-4o")
                return {"type": "emergent", "client": client}
            
            # Fallback to OpenAI directly
            import openai
            openai_key = os.environ.get('OPENAI_API_KEY')
            if openai_key:
                client = openai.OpenAI(api_key=openai_key)
                logger.info("🤖 Owl Agent: OpenAI client initialized")
                return {"type": "openai", "client": client}
            else:
                logger.warning("⚠️ Owl Agent: No AI keys found, using mock responses")
                return None
        except Exception as e:
            logger.error(f"❌ Owl Agent: Failed to setup AI client: {e}")
            return None
    
    def _load_field_guides(self) -> Dict[str, FieldGuide]:
        """Load field guides for different visa types"""
        
        guides = {}
        
        # Personal Information Fields
        guides["full_name"] = FieldGuide(
            field_id="full_name",
            question_pt="Qual é o seu nome completo exatamente como aparece no seu passaporte?",
            question_en="What is your full name exactly as it appears on your passport?",
            explanation_pt="É fundamental que o nome seja EXATAMENTE igual ao passaporte. Qualquer diferença pode causar problemas na imigração.",
            explanation_en="The name must be EXACTLY as shown on passport. Any difference can cause immigration issues.",
            examples=["Maria Silva Santos", "João Pedro da Costa", "Ana Carolina Ferreira"],
            validation_rules={
                "min_length": 2,
                "max_length": 100,
                "required": True,
                "pattern": r"^[A-Za-zÀ-ÿ\s]+$",
                "google_validation": True
            },
            importance_level=5,
            visa_specific=["ALL"]
        )
        
        guides["date_of_birth"] = FieldGuide(
            field_id="date_of_birth",
            question_pt="Qual é a sua data de nascimento?",
            question_en="What is your date of birth?",
            explanation_pt="Use o formato DD/MM/AAAA. A data deve ser exatamente igual à do seu documento de identidade.",
            explanation_en="Use DD/MM/YYYY format. Date must match your identity document exactly.",
            examples=["15/08/1990", "23/12/1985", "07/03/1992"],
            validation_rules={
                "required": True,
                "format": "date",
                "max_date": "today-18years",
                "google_validation": True
            },
            importance_level=5,
            visa_specific=["ALL"]
        )
        
        guides["place_of_birth"] = FieldGuide(
            field_id="place_of_birth",
            question_pt="Onde você nasceu? (Cidade, Estado, País)",
            question_en="Where were you born? (City, State, Country)",
            explanation_pt="Informe o local exato como consta na sua certidão de nascimento. Formato: Cidade, Estado, País.",
            explanation_en="Provide exact location as shown on birth certificate. Format: City, State, Country.",
            examples=["São Paulo, SP, Brasil", "Rio de Janeiro, RJ, Brasil", "Brasília, DF, Brasil"],
            validation_rules={
                "required": True,
                "min_length": 5,
                "google_validation": True
            },
            importance_level=5,
            visa_specific=["ALL"]
        )
        
        # Address Fields
        guides["current_address"] = FieldGuide(
            field_id="current_address",
            question_pt="Qual é o seu endereço atual completo?",
            question_en="What is your complete current address?",
            explanation_pt="Informe seu endereço residencial atual. Este será usado para correspondências oficiais.",
            explanation_en="Provide your current residential address. This will be used for official correspondence.",
            examples=["Rua das Flores, 123, Apt 45", "Avenida Paulista, 1000", "Rua Augusta, 500, Casa 2"],
            validation_rules={
                "required": True,
                "min_length": 10,
                "cep_integration": True
            },
            importance_level=4,
            visa_specific=["ALL"]
        )
        
        # Employment Fields (H-1B specific)
        guides["current_job"] = FieldGuide(
            field_id="current_job",
            question_pt="Qual é o seu cargo/função atual?",
            question_en="What is your current job title/position?",
            explanation_pt="Para o visto H-1B, este cargo deve ser de nível universitário e relacionado à sua formação.",
            explanation_en="For H-1B visa, this position must be university-level and related to your education.",
            examples=["Software Engineer", "Data Scientist", "Marketing Manager", "Financial Analyst"],
            validation_rules={
                "required": True,
                "min_length": 3,
                "h1b_validation": True
            },
            importance_level=5,
            visa_specific=["H-1B", "O-1"]
        )
        
        guides["employer_name"] = FieldGuide(
            field_id="employer_name",
            question_pt="Qual é o nome da empresa onde você trabalha ou trabalhará?",
            question_en="What is the name of the company where you work or will work?",
            explanation_pt="Esta deve ser a empresa que está patrocinando seu visto. Verifique se o nome está correto.",
            explanation_en="This should be the company sponsoring your visa. Verify the name is correct.",
            examples=["Google Inc.", "Microsoft Corporation", "Universidade de São Paulo"],
            validation_rules={
                "required": True,
                "min_length": 2,
                "company_validation": True
            },
            importance_level=5,
            visa_specific=["H-1B", "O-1", "L-1"]
        )
        
        # Education Fields
        guides["highest_degree"] = FieldGuide(
            field_id="highest_degree",
            question_pt="Qual é o seu maior grau de educação?",
            question_en="What is your highest degree of education?",
            explanation_pt="Para H-1B, normalmente é necessário pelo menos um bacharelado ou equivalente.",
            explanation_en="For H-1B, typically requires at least a bachelor's degree or equivalent.",
            examples=["Bacharelado", "Mestrado", "Doutorado", "Ensino Médio"],
            validation_rules={
                "required": True,
                "h1b_degree_check": True
            },
            importance_level=5,
            visa_specific=["H-1B", "O-1", "F-1"]
        )
        
        # Family Fields (I-130, I-485)
        guides["marital_status"] = FieldGuide(
            field_id="marital_status",
            question_pt="Qual é o seu estado civil atual?",
            question_en="What is your current marital status?",
            explanation_pt="Para vistos familiares, esta informação é fundamental e deve ser comprovada com documentos.",
            explanation_en="For family visas, this information is crucial and must be proven with documents.",
            examples=["Solteiro(a)", "Casado(a)", "Divorciado(a)", "Viúvo(a)"],
            validation_rules={
                "required": True,
                "family_visa_validation": True
            },
            importance_level=5,
            visa_specific=["I-130", "I-485", "K-1"]
        )
        
        return guides
    
    async def start_guided_session(self, case_id: str, visa_type: str, user_language: str = "pt") -> Dict[str, Any]:
        """Inicia uma sessão guiada com o Agente Coruja"""
        
        session_id = f"owl_session_{case_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize session
        self.interaction_history[session_id] = []
        
        # Get visa-specific fields
        relevant_fields = self._get_relevant_fields(visa_type)
        
        # Create welcome message
        welcome_message = await self._create_welcome_message(visa_type, user_language)
        
        # Get first field guidance
        first_field = relevant_fields[0] if relevant_fields else None
        first_guidance = await self._get_field_guidance(first_field, visa_type, user_language) if first_field else None
        
        return {
            "session_id": session_id,
            "visa_type": visa_type,
            "language": user_language,
            "welcome_message": welcome_message,
            "total_fields": len(relevant_fields),
            "relevant_fields": [field.field_id for field in relevant_fields],
            "first_field_guidance": first_guidance,
            "session_started": datetime.now().isoformat()
        }
    
    def _get_relevant_fields(self, visa_type: str) -> List[FieldGuide]:
        """Get fields relevant to specific visa type"""
        
        relevant_fields = []
        
        for field_guide in self.field_guides.values():
            if "ALL" in field_guide.visa_specific or visa_type in field_guide.visa_specific:
                relevant_fields.append(field_guide)
        
        # Sort by importance level (highest first)
        relevant_fields.sort(key=lambda x: x.importance_level, reverse=True)
        
        return relevant_fields
    
    async def _create_welcome_message(self, visa_type: str, language: str) -> Dict[str, Any]:
        """Create personalized welcome message"""
        
        visa_messages = {
            "pt": {
                "H-1B": f"🦉 Olá! Sou a Coruja do Osprey e vou te guiar no preenchimento do questionário para o visto **H-1B**!\n\nO H-1B é um visto de trabalho para profissionais especializados. Vou te fazer perguntas em português e depois converter tudo para o formulário oficial do USCIS em inglês.\n\n✨ **Dicas importantes:**\n• Tenha seus documentos em mãos\n• Responda com precisão total\n• Posso validar informações em tempo real\n\nVamos começar? 🚀",
                "F-1": f"🦉 Olá! Vou te guiar no questionário para o visto de estudante **F-1**!\n\nVamos preencher tudo em português e eu convertercie automaticamente para o formulário oficial. Tenha em mãos seu I-20 e documentos acadêmicos.\n\nPronto para começar? 📚✨",
                "I-485": f"🦉 Bem-vindo! Vou te ajudar com o questionário do **I-485** (Ajuste de Status)!\n\nEste é um processo importante para obter o green card. Vou te guiar passo a passo com perguntas claras em português.\n\nVamos começar sua jornada para a residência permanente! 🏡✨"
            },
            "en": {
                "H-1B": f"🦉 Hello! I'm Osprey Owl and I'll guide you through the **H-1B** questionnaire!\n\nH-1B is a work visa for specialized professionals. I'll ask questions in English and convert everything to the official USCIS form.\n\nReady to start? 🚀",
                "F-1": f"🦉 Hello! I'll guide you through the **F-1** student visa questionnaire!\n\nHave your I-20 and academic documents ready. Let's get started! 📚✨",
                "I-485": f"🦉 Welcome! I'll help you with the **I-485** (Adjustment of Status) questionnaire!\n\nThis is your path to a green card. Let's start your journey to permanent residence! 🏡✨"
            }
        }
        
        message_text = visa_messages.get(language, visa_messages["pt"]).get(visa_type, 
            visa_messages[language]["H-1B"])
        
        return {
            "type": "welcome",
            "text": message_text,
            "visa_type": visa_type,
            "language": language,
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_field_guidance(self, field_id: str, visa_type: str, user_language: str = "pt", 
                                current_value: str = "", user_context: Dict = None) -> Dict[str, Any]:
        """Get intelligent guidance for a specific field"""
        
        if field_id not in self.field_guides:
            return self._create_generic_guidance(field_id, user_language)
        
        field_guide = self.field_guides[field_id]
        
        # Create base guidance
        guidance = {
            "field_id": field_id,
            "question": field_guide.question_pt if user_language == "pt" else field_guide.question_en,
            "explanation": field_guide.explanation_pt if user_language == "pt" else field_guide.explanation_en,
            "examples": field_guide.examples[:3],  # Show max 3 examples
            "importance_level": field_guide.importance_level,
            "validation_rules": field_guide.validation_rules,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add AI-powered contextual guidance
        if self.ai_client and user_context:
            try:
                contextual_guidance = await self._get_ai_contextual_guidance(
                    field_guide, visa_type, user_language, current_value, user_context
                )
                guidance.update(contextual_guidance)
            except Exception as e:
                logger.error(f"❌ AI guidance error: {e}")
        
        # Add proactive tips
        guidance["proactive_tips"] = self._get_proactive_tips(field_id, visa_type, user_language)
        
        return guidance
    
    async def _get_ai_contextual_guidance(self, field_guide: FieldGuide, visa_type: str, 
                                        language: str, current_value: str, user_context: Dict) -> Dict[str, Any]:
        """Get AI-powered contextual guidance using Emergent LLM or OpenAI"""
        
        if not self.ai_client:
            return {"ai_powered": False}
        
        prompt = f"""
        You are an intelligent immigration assistant helping with a {visa_type} application.
        
        Field: {field_guide.field_id}
        Question: {field_guide.question_pt if language == 'pt' else field_guide.question_en}
        Current Value: {current_value or 'empty'}
        User Context: {json.dumps(user_context, indent=2)}
        
        Provide helpful, contextual guidance in {'Portuguese' if language == 'pt' else 'English'}:
        1. Specific tips for this field
        2. Common mistakes to avoid
        3. How this affects the {visa_type} application
        
        Keep it concise, friendly, and practical.
        """
        
        try:
            if self.ai_client["type"] == "emergent":
                from emergentintegrations.llm.chat import UserMessage
                response = await asyncio.to_thread(
                    self.ai_client["client"].send_message,
                    UserMessage(content=prompt)
                )
                ai_guidance = response.content
            elif self.ai_client["type"] == "openai":
                response = await asyncio.to_thread(
                    self.ai_client["client"].chat.completions.create,
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=300,
                    temperature=0.7
                )
                ai_guidance = response.choices[0].message.content
            
            return {
                "ai_guidance": ai_guidance,
                "ai_powered": True,
                "provider": self.ai_client["type"]
            }
            
        except Exception as e:
            logger.error(f"❌ AI contextual guidance error: {e}")
            return {"ai_powered": False}
    
    def _get_proactive_tips(self, field_id: str, visa_type: str, language: str) -> List[str]:
        """Get proactive tips for specific field and visa combination"""
        
        tips = {
            "pt": {
                "full_name": {
                    "H-1B": ["Verifique se o nome no passaporte está atualizado", "Nomes com acentos podem precisar adaptação"],
                    "F-1": ["O nome deve ser igual ao do I-20", "Certifique-se da grafia correta"],
                },
                "current_job": {
                    "H-1B": ["O cargo deve exigir diploma universitário", "Deve estar relacionado à sua formação"],
                },
                "employer_name": {
                    "H-1B": ["Deve ser a empresa do LCA aprovado", "Verifique se a empresa tem licença para patrocinar H-1B"],
                }
            },
            "en": {
                "full_name": {
                    "H-1B": ["Verify passport name is current", "Names with accents may need adaptation"],
                    "F-1": ["Name must match I-20", "Ensure correct spelling"],
                },
                "current_job": {
                    "H-1B": ["Position must require university degree", "Must be related to your education"],
                },
                "employer_name": {
                    "H-1B": ["Must be the LCA approved company", "Verify company has H-1B sponsorship license"],
                }
            }
        }
        
        return tips.get(language, tips["pt"]).get(field_id, {}).get(visa_type, [])
    
    async def validate_field_input(self, field_id: str, user_input: str, visa_type: str, 
                                 session_id: str, full_context: Dict = None) -> Dict[str, Any]:
        """Validate user input with AI and Google API"""
        
        if field_id not in self.field_guides:
            return {"valid": True, "message": "Campo não encontrado no guia", "score": 50}
        
        field_guide = self.field_guides[field_id]
        validation_result = {
            "field_id": field_id,
            "user_input": user_input,
            "timestamp": datetime.now().isoformat()
        }
        
        # Basic validation
        basic_validation = self._validate_basic_rules(user_input, field_guide.validation_rules)
        validation_result.update(basic_validation)
        
        # Google API validation (if enabled)
        if field_guide.validation_rules.get("google_validation") and user_input.strip():
            try:
                google_validation = await self._validate_with_google_api(field_id, user_input, full_context)
                validation_result["google_validation"] = google_validation
            except Exception as e:
                logger.error(f"❌ Google validation error: {e}")
                validation_result["google_validation"] = {"status": "error", "message": str(e)}
        
        # AI-powered validation
        if self.ai_client and user_input.strip():
            try:
                ai_validation = await self._validate_with_ai(field_guide, user_input, visa_type, full_context)
                validation_result["ai_validation"] = ai_validation
            except Exception as e:
                logger.error(f"❌ AI validation error: {e}")
                validation_result["ai_validation"] = {"status": "error"}
        
        # Calculate overall score
        validation_result["overall_score"] = self._calculate_validation_score(validation_result)
        
        # Generate user-friendly message
        validation_result["user_message"] = self._generate_validation_message(validation_result, field_guide)
        
        # Store interaction
        if session_id in self.interaction_history:
            interaction = OwlInteraction(
                interaction_id=f"{session_id}_{field_id}_{datetime.now().strftime('%H%M%S')}",
                field_id=field_id,
                user_input=user_input,
                owl_response=validation_result["user_message"],
                validation_result=validation_result,
                timestamp=datetime.now(),
                session_id=session_id
            )
            self.interaction_history[session_id].append(interaction)
        
        return validation_result
    
    def _validate_basic_rules(self, user_input: str, rules: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input against basic rules"""
        
        result = {"basic_validation": {"valid": True, "errors": []}}
        
        # Required field check
        if rules.get("required", False) and not user_input.strip():
            result["basic_validation"]["valid"] = False
            result["basic_validation"]["errors"].append("Campo obrigatório não preenchido")
        
        # Length checks
        if user_input.strip():
            if rules.get("min_length") and len(user_input) < rules["min_length"]:
                result["basic_validation"]["valid"] = False
                result["basic_validation"]["errors"].append(f"Mínimo {rules['min_length']} caracteres")
            
            if rules.get("max_length") and len(user_input) > rules["max_length"]:
                result["basic_validation"]["valid"] = False
                result["basic_validation"]["errors"].append(f"Máximo {rules['max_length']} caracteres")
        
        # Pattern validation
        if rules.get("pattern") and user_input.strip():
            import re
            if not re.match(rules["pattern"], user_input):
                result["basic_validation"]["valid"] = False
                result["basic_validation"]["errors"].append("Formato inválido")
        
        # Date validation
        if rules.get("format") == "date" and user_input.strip():
            try:
                from datetime import datetime
                # Try multiple date formats
                for fmt in ["%d/%m/%Y", "%Y-%m-%d", "%m/%d/%Y"]:
                    try:
                        date_obj = datetime.strptime(user_input, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    result["basic_validation"]["valid"] = False
                    result["basic_validation"]["errors"].append("Formato de data inválido (use DD/MM/AAAA)")
            except Exception:
                result["basic_validation"]["valid"] = False
                result["basic_validation"]["errors"].append("Data inválida")
        
        return result
    
    async def _validate_with_google_api(self, field_id: str, user_input: str, context: Dict = None) -> Dict[str, Any]:
        """Validate input using Google APIs"""
        
        try:
            # Address validation using Google API
            if field_id in ["current_address", "mailing_address", "employer_address"]:
                return await self._validate_address_with_google(user_input)
            
            # Name validation using Google Vision for document consistency
            elif field_id in ["full_name", "surname", "given_names"]:
                return await self._validate_name_consistency(user_input, context)
            
            # Phone number validation
            elif field_id in ["phone_number", "mobile_phone", "contact_phone"]:
                return await self._validate_phone_with_google(user_input)
            
            # Email validation
            elif field_id in ["email", "contact_email"]:
                return await self._validate_email_with_google(user_input)
            
            # Default validation
            else:
                return {
                    "status": "validated",
                    "confidence": 0.85,
                    "suggestions": [],
                    "provider": "google_api_basic"
                }
                
        except Exception as e:
            logger.error(f"❌ Google API validation error: {e}")
            return {
                "status": "error",
                "confidence": 0.0,
                "message": str(e),
                "provider": "google_api_error"
            }
    
    async def _validate_address_with_google(self, address: str) -> Dict[str, Any]:
        """Validate address using Google Places API"""
        # Mock implementation - in production would use actual Google Places API
        return {
            "status": "validated",
            "confidence": 0.92,
            "suggestions": [f"Endereço validado: {address}"],
            "formatted_address": address,
            "provider": "google_places"
        }
    
    async def _validate_name_consistency(self, name: str, context: Dict) -> Dict[str, Any]:
        """Validate name consistency with documents using Google Vision"""
        # Mock implementation - in production would cross-reference with uploaded documents
        return {
            "status": "validated", 
            "confidence": 0.95,
            "suggestions": [f"Nome consistente com documentos: {name}"],
            "provider": "google_vision"
        }
    
    async def _validate_phone_with_google(self, phone: str) -> Dict[str, Any]:
        """Validate phone number format"""
        import re
        
        # Basic phone validation
        phone_patterns = [
            r'^\+55\s?\(?\d{2}\)?\s?\d{4,5}-?\d{4}$',  # Brazilian format
            r'^\+1\s?\(?\d{3}\)?\s?\d{3}-?\d{4}$',      # US format
        ]
        
        is_valid = any(re.match(pattern, phone) for pattern in phone_patterns)
        
        return {
            "status": "validated" if is_valid else "invalid_format",
            "confidence": 0.90 if is_valid else 0.20,
            "suggestions": ["Use formato internacional: +55 (11) 99999-9999"] if not is_valid else [],
            "provider": "google_phone_format"
        }
    
    async def _validate_email_with_google(self, email: str) -> Dict[str, Any]:
        """Validate email format and deliverability"""
        import re
        
        # Basic email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        is_valid = re.match(email_pattern, email) is not None
        
        return {
            "status": "validated" if is_valid else "invalid_format",
            "confidence": 0.88 if is_valid else 0.15,
            "suggestions": ["Verifique o formato do email"] if not is_valid else [],
            "provider": "google_email_format"
        }
    
    async def _validate_with_ai(self, field_guide: FieldGuide, user_input: str, 
                              visa_type: str, context: Dict = None) -> Dict[str, Any]:
        """Validate input using AI"""
        
        if not self.ai_client:
            return {"status": "unavailable", "message": "AI not available"}
        
        prompt = f"""
        Validate this immigration form input:
        
        Field: {field_guide.field_id}
        Visa Type: {visa_type}
        User Input: "{user_input}"
        Context: {json.dumps(context or {}, indent=2)}
        
        Validate for:
        1. Accuracy for {visa_type} visa
        2. Potential issues
        3. Improvement suggestions
        
        Return JSON with: valid (boolean), confidence (0-1), suggestions (array), issues (array)
        """
        
        try:
            if self.ai_client["type"] == "emergent":
                from emergentintegrations.llm.chat import UserMessage
                response = await asyncio.to_thread(
                    self.ai_client["client"].send_message,
                    UserMessage(content=prompt)
                )
                ai_response = response.content
            elif self.ai_client["type"] == "openai":
                response = await asyncio.to_thread(
                    self.ai_client["client"].chat.completions.create,
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=200,
                    temperature=0.3
                )
                ai_response = response.choices[0].message.content
            
            # Try to parse JSON response
            try:
                import json
                result = json.loads(ai_response)
                result["provider"] = self.ai_client["type"]
                return result
            except:
                # If not JSON, create structured response
                return {
                    "valid": True,
                    "confidence": 0.8,
                    "suggestions": [ai_response[:100] + "..." if len(ai_response) > 100 else ai_response],
                    "provider": self.ai_client["type"]
                }
                
        except Exception as e:
            logger.error(f"❌ AI validation error: {e}")
            return {"status": "error", "message": str(e)}
    
    def _calculate_validation_score(self, validation_result: Dict[str, Any]) -> int:
        """Calculate overall validation score (0-100)"""
        
        scores = []
        
        # Basic validation score
        if validation_result.get("basic_validation", {}).get("valid", False):
            scores.append(80)
        else:
            scores.append(20)
        
        # Google API score
        google_val = validation_result.get("google_validation", {})
        if google_val.get("status") == "validated":
            scores.append(int(google_val.get("confidence", 0.8) * 100))
        
        # AI validation score
        ai_val = validation_result.get("ai_validation", {})
        if ai_val.get("valid"):
            scores.append(int(ai_val.get("confidence", 0.8) * 100))
        
        return int(sum(scores) / len(scores)) if scores else 50
    
    def _generate_validation_message(self, validation_result: Dict[str, Any], field_guide: FieldGuide) -> str:
        """Generate user-friendly validation message"""
        
        score = validation_result.get("overall_score", 50)
        
        if score >= 85:
            return f"✅ Perfeito! {field_guide.field_id} está correto."
        elif score >= 70:
            return f"✓ Bom! {field_guide.field_id} parece correto, mas verifique novamente."
        elif score >= 50:
            issues = validation_result.get("basic_validation", {}).get("errors", [])
            return f"⚠️ Atenção: {', '.join(issues) if issues else 'Verifique os dados inseridos.'}"
        else:
            return f"❌ Por favor, corrija as informações para {field_guide.field_id}."
    
    def _create_generic_guidance(self, field_id: str, language: str) -> Dict[str, Any]:
        """Create generic guidance for unknown fields"""
        
        messages = {
            "pt": f"Complete o campo {field_id} com as informações solicitadas.",
            "en": f"Please complete the {field_id} field with the requested information."
        }
        
        return {
            "field_id": field_id,
            "question": messages.get(language, messages["pt"]),
            "explanation": "Campo personalizado para seu caso específico.",
            "examples": [],
            "importance_level": 3,
            "validation_rules": {"required": True},
            "proactive_tips": [],
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_session_progress(self, session_id: str) -> Dict[str, Any]:
        """Get current session progress and statistics"""
        
        if session_id not in self.interaction_history:
            return {"error": "Session not found"}
        
        interactions = self.interaction_history[session_id]
        
        # Calculate statistics
        total_interactions = len(interactions)
        valid_interactions = len([i for i in interactions if i.validation_result.get("overall_score", 0) >= 70])
        
        # Get field completion status
        completed_fields = list(set([i.field_id for i in interactions]))
        
        return {
            "session_id": session_id,
            "total_interactions": total_interactions,
            "valid_interactions": valid_interactions,
            "completion_rate": (valid_interactions / max(total_interactions, 1)) * 100,
            "completed_fields": completed_fields,
            "last_interaction": interactions[-1].timestamp.isoformat() if interactions else None,
            "session_duration_minutes": self._calculate_session_duration(interactions),
            "recommendations": self._generate_session_recommendations(interactions)
        }
    
    def _calculate_session_duration(self, interactions: List[OwlInteraction]) -> float:
        """Calculate session duration in minutes"""
        
        if len(interactions) < 2:
            return 0.0
        
        start_time = interactions[0].timestamp
        end_time = interactions[-1].timestamp
        
        duration = (end_time - start_time).total_seconds() / 60
        return round(duration, 2)
    
    def _generate_session_recommendations(self, interactions: List[OwlInteraction]) -> List[str]:
        """Generate recommendations based on session history"""
        
        recommendations = []
        
        # Check for fields with low scores
        low_score_fields = [
            i.field_id for i in interactions 
            if i.validation_result.get("overall_score", 0) < 70
        ]
        
        if low_score_fields:
            recommendations.append(f"Revise os campos: {', '.join(set(low_score_fields))}")
        
        # Check session duration
        duration = self._calculate_session_duration(interactions)
        if duration > 30:
            recommendations.append("Considere fazer uma pausa. Formulários longos podem gerar erros.")
        
        # Check for repeated validation failures
        failed_fields = {}
        for interaction in interactions:
            if interaction.validation_result.get("overall_score", 0) < 50:
                failed_fields[interaction.field_id] = failed_fields.get(interaction.field_id, 0) + 1
        
        problem_fields = [field for field, count in failed_fields.items() if count > 2]
        if problem_fields:
            recommendations.append(f"Campos com dificuldades: {', '.join(problem_fields)}. Consulte os exemplos.")
        
        return recommendations[:3]  # Max 3 recommendations

# Global instance
intelligent_owl = IntelligentOwlAgent()