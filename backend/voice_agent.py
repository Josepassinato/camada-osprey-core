import asyncio
import json
import logging
import uuid
import re
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
from fastapi import WebSocket, WebSocketDisconnect
from dataclasses import dataclass, asdict
from emergentintegrations.llm.chat import LlmChat, UserMessage

@dataclass
class FieldState:
    name: str
    label: str = ""
    value: str = ""
    valid: bool = True
    errors: List[str] = None
    required: bool = False
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []

@dataclass 
class SectionState:
    id: str
    label: str
    status: str = "todo"  # "todo" | "in_progress" | "complete"
    missing: List[str] = None
    percent: int = 0
    
    def __post_init__(self):
        if self.missing is None:
            self.missing = []

@dataclass
class Snapshot:
    userId: str
    formId: str
    stepId: str
    url: str
    timestamp: str
    sections: List[SectionState]
    fields: List[FieldState]
    siteVersionHash: str = "v1.0.0"

@dataclass
class Intent:
    kind: str
    stepId: Optional[str] = None
    field: Optional[str] = None
    question: Optional[str] = None

@dataclass
class AgentAdvice:
    disclaimer: str
    say: str
    checklist: Optional[List[str]] = None
    howToVerify: Optional[List[str]] = None
    corrections: Optional[List[Dict[str, str]]] = None
    unresolved: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.checklist is None:
            self.checklist = []
        if self.howToVerify is None:
            self.howToVerify = []
        if self.corrections is None:
            self.corrections = []
        if self.unresolved is None:
            self.unresolved = []

class VoiceAgent:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.active_sessions: Dict[str, Dict] = {}
        
    async def process_voice_message(self, session_id: str, message: Dict) -> Dict:
        """Process voice message and return response"""
        try:
            message_type = message.get("type")
            
            if message_type == "snapshot":
                return await self._handle_snapshot(session_id, message)
            elif message_type == "voice_input":
                return await self._handle_voice_input(session_id, message)
            elif message_type == "request_guidance":
                return await self._handle_guidance_request(session_id, message)
            else:
                return {"error": f"Unknown message type: {message_type}"}
                
        except Exception as e:
            self.logger.error(f"Error processing voice message: {e}")
            return {"error": "Failed to process message"}
    
    async def _handle_snapshot(self, session_id: str, message: Dict) -> Dict:
        """Handle form snapshot update"""
        try:
            snapshot_data = message.get("snapshot", {})
            
            # Store snapshot for session
            self.active_sessions[session_id] = {
                "snapshot": snapshot_data,
                "last_update": datetime.utcnow().isoformat()
            }
            
            # Generate immediate guidance based on snapshot
            advice = await self._analyze_current_state(snapshot_data)
            
            return {
                "type": "snapshot_received",
                "advice": asdict(advice),
                "session_id": session_id
            }
            
        except Exception as e:
            self.logger.error(f"Error handling snapshot: {e}")
            return {"error": "Failed to process snapshot"}
    
    async def _handle_voice_input(self, session_id: str, message: Dict) -> Dict:
        """Handle voice input and return guidance"""
        try:
            transcription = message.get("transcription", "")
            
            # Get current snapshot
            snapshot = self.active_sessions.get(session_id, {}).get("snapshot", {})
            
            # Parse intent from transcription
            intent = await self._parse_intent(transcription)
            
            # Generate response based on intent and current state
            advice = await self._generate_advice(intent, snapshot)
            
            return {
                "type": "voice_response",
                "advice": asdict(advice),
                "intent": asdict(intent)
            }
            
        except Exception as e:
            self.logger.error(f"Error handling voice input: {e}")
            return {"error": "Failed to process voice input"}
    
    async def _handle_guidance_request(self, session_id: str, message: Dict) -> Dict:
        """Handle explicit guidance request"""
        try:
            request_type = message.get("request_type", "general")
            snapshot = self.active_sessions.get(session_id, {}).get("snapshot", {})
            
            if request_type == "next_step":
                advice = await self._get_next_step_guidance(snapshot)
            elif request_type == "validate_current":
                advice = await self._validate_current_section(snapshot)
            else:
                advice = await self._analyze_current_state(snapshot)
            
            return {
                "type": "guidance_response",
                "advice": asdict(advice),
                "request_type": request_type
            }
            
        except Exception as e:
            self.logger.error(f"Error handling guidance request: {e}")
            return {"error": "Failed to provide guidance"}
    
    async def _parse_intent(self, transcription: str) -> Intent:
        """Parse user intent from transcription using NLU"""
        try:
            text = transcription.lower().strip()
            
            # Simple regex-based intent classification (MVP)
            if re.search(r"\b(próximo|próxima|continuar|avançar)\b", text):
                return Intent(kind="next_step")
            elif re.search(r"\b(status|situação|progresso|onde estou)\b", text):
                return Intent(kind="status")
            elif re.search(r"\b(validar|verificar|checar|conferir)\b", text):
                return Intent(kind="validate_section")
            elif re.search(r"\b(corrigir|consertar|erro|problema)\b", text):
                # Try to extract field name
                field_match = re.search(r"\b(nome|email|telefone|endereço|data|nascimento)\b", text)
                field = field_match.group(0) if field_match else None
                return Intent(kind="fix_field", field=field)
            elif re.search(r"\b(explicar|explicação|que significa|o que é)\b", text):
                field_match = re.search(r"\b(nome|email|telefone|endereço|data|nascimento)\b", text)
                field = field_match.group(0) if field_match else None
                return Intent(kind="explain_field", field=field)
            else:
                return Intent(kind="general_question", question=transcription)
                
        except Exception as e:
            self.logger.error(f"Error parsing intent: {e}")
            return Intent(kind="general_question", question=transcription)
    
    async def _analyze_current_state(self, snapshot: Dict) -> AgentAdvice:
        """Analyze current form state and provide guidance"""
        try:
            sections = snapshot.get("sections", [])
            fields = snapshot.get("fields", [])
            step_id = snapshot.get("stepId", "")
            
            # Find current section
            current_section = None
            for section in sections:
                if section.get("status") == "in_progress":
                    current_section = section
                    break
            
            if not current_section and sections:
                # Find first incomplete section
                for section in sections:
                    if section.get("status") == "todo":
                        current_section = section
                        break
            
            if current_section:
                return await self._get_section_guidance(current_section, fields, step_id)
            else:
                return AgentAdvice(
                    disclaimer="Esta é uma ferramenta de apoio, não aconselhamento jurídico.",
                    say="Parece que você completou todas as seções. Posso ajudá-lo com algo específico?"
                )
                
        except Exception as e:
            self.logger.error(f"Error analyzing state: {e}")
            return AgentAdvice(
                disclaimer="Esta é uma ferramenta de apoio, não aconselhamento jurídico.",
                say="Desculpe, houve um erro ao analisar seu progresso. Posso ajudá-lo de outra forma?"
            )
    
    async def _get_section_guidance(self, section: Dict, fields: List[Dict], step_id: str) -> AgentAdvice:
        """Get specific guidance for a section"""
        try:
            section_id = section.get("id", "")
            section_label = section.get("label", "")
            missing = section.get("missing", [])
            
            # Find fields for this section
            section_fields = [f for f in fields if f.get("name", "").startswith(section_id)]
            
            # Check for errors
            field_errors = []
            for field in section_fields:
                if not field.get("valid", True) and field.get("errors"):
                    field_errors.extend([{
                        "field": field.get("label", field.get("name")),
                        "reason": error,
                        "how": f"Verifique o campo '{field.get('label', field.get('name'))}'"
                    } for error in field.get("errors", [])])
            
            # Generate guidance text
            if field_errors:
                say = f"Encontrei alguns problemas na seção {section_label}. "
                if len(field_errors) == 1:
                    say += f"O campo '{field_errors[0]['field']}' precisa ser corrigido."
                else:
                    say += f"Existem {len(field_errors)} campos que precisam ser corrigidos."
            elif missing:
                say = f"Na seção {section_label}, ainda faltam {len(missing)} campos obrigatórios."
            else:
                say = f"A seção {section_label} está progredindo bem. Continue preenchendo os campos."
            
            # Generate verification tips
            how_to_verify = self._get_verification_tips(section_id)
            
            return AgentAdvice(
                disclaimer="Esta é uma ferramenta de apoio, não aconselhamento jurídico.",
                say=say,
                corrections=field_errors,
                howToVerify=how_to_verify,
                unresolved=missing if missing else []
            )
            
        except Exception as e:
            self.logger.error(f"Error getting section guidance: {e}")
            return AgentAdvice(
                disclaimer="Esta é uma ferramenta de apoio, não aconselhamento jurídico.",
                say="Posso ajudá-lo com esta seção. O que você gostaria de saber?"
            )
    
    def _get_verification_tips(self, section_id: str) -> List[str]:
        """Get verification tips for a section"""
        tips = {
            "personal": [
                "Verifique se o nome está exatamente como no passaporte",
                "Confirme a data de nascimento no formato correto",
                "Certifique-se de que a nacionalidade está correta"
            ],
            "address": [
                "Use o endereço atual onde você recebe correspondência",
                "Inclua CEP e informações completas",
                "Verifique se o telefone está com código do país"
            ],
            "employment": [
                "Confirme o nome oficial da empresa",
                "Verifique as datas de início e término do trabalho",
                "Inclua informações completas do cargo"
            ],
            "family": [
                "Verifique nomes completos dos familiares",
                "Confirme datas de nascimento e relacionamentos",
                "Inclua informações de cônjuges e filhos se aplicável"
            ]
        }
        
        return tips.get(section_id, [
            "Verifique se todas as informações estão corretas",
            "Confirme datas e nomes com documentos oficiais",
            "Certifique-se de preencher todos os campos obrigatórios"
        ])
    
    async def _get_next_step_guidance(self, snapshot: Dict) -> AgentAdvice:
        """Get next step guidance"""
        try:
            sections = snapshot.get("sections", [])
            
            # Find next incomplete section
            for section in sections:
                if section.get("status") in ["todo", "in_progress"]:
                    section_label = section.get("label", "")
                    missing = section.get("missing", [])
                    
                    if missing:
                        say = f"Seu próximo passo é completar a seção {section_label}. "
                        say += f"Ainda faltam {len(missing)} campos obrigatórios."
                    else:
                        say = f"Continue trabalhando na seção {section_label}."
                    
                    return AgentAdvice(
                        disclaimer="Esta é uma ferramenta de apoio, não aconselhamento jurídico.",
                        say=say,
                        checklist=[f"Complete a seção: {section_label}"],
                        howToVerify=self._get_verification_tips(section.get("id", ""))
                    )
            
            return AgentAdvice(
                disclaimer="Esta é uma ferramenta de apoio, não aconselhamento jurídico.",
                say="Parabéns! Você completou todas as seções. Pode revisar e finalizar sua aplicação."
            )
            
        except Exception as e:
            self.logger.error(f"Error getting next step guidance: {e}")
            return AgentAdvice(
                disclaimer="Esta é uma ferramenta de apoio, não aconselhamento jurídico.",
                say="Posso ajudá-lo com o próximo passo. Me diga onde você está com dificuldades."
            )
    
    async def _validate_current_section(self, snapshot: Dict) -> AgentAdvice:
        """Validate current section"""
        try:
            sections = snapshot.get("sections", [])
            fields = snapshot.get("fields", [])
            
            # Find current section
            current_section = None
            for section in sections:
                if section.get("status") == "in_progress":
                    current_section = section
                    break
            
            if not current_section:
                return AgentAdvice(
                    disclaimer="Esta é uma ferramenta de apoio, não aconselhamento jurídico.",
                    say="Não encontrei uma seção ativa para validar. Qual seção você gostaria de verificar?"
                )
            
            # Validate fields in current section
            section_id = current_section.get("id", "")
            section_fields = [f for f in fields if f.get("name", "").startswith(section_id)]
            
            errors = []
            warnings = []
            
            for field in section_fields:
                field_name = field.get("label", field.get("name"))
                field_value = field.get("value", "")
                
                if field.get("required", False) and not field_value.strip():
                    errors.append(f"Campo obrigatório '{field_name}' está vazio")
                elif field.get("errors"):
                    errors.extend([f"{field_name}: {error}" for error in field.get("errors")])
            
            if errors:
                say = f"Encontrei {len(errors)} problema(s) na seção atual que precisam ser corrigidos."
            else:
                say = f"A seção atual está válida! Todos os campos obrigatórios foram preenchidos corretamente."
            
            return AgentAdvice(
                disclaimer="Esta é uma ferramenta de apoio, não aconselhamento jurídico.",
                say=say,
                corrections=[{"field": "vários", "reason": error, "how": "Verifique e corrija"} for error in errors],
                unresolved=warnings
            )
            
        except Exception as e:
            self.logger.error(f"Error validating section: {e}")
            return AgentAdvice(
                disclaimer="Esta é uma ferramenta de apoio, não aconselhamento jurídico.",
                say="Houve um erro ao validar a seção. Tente novamente."
            )
    
    async def _generate_advice(self, intent: Intent, snapshot: Dict) -> AgentAdvice:
        """Generate advice based on intent and current state"""
        try:
            if intent.kind == "next_step":
                return await self._get_next_step_guidance(snapshot)
            elif intent.kind == "status":
                return await self._analyze_current_state(snapshot)
            elif intent.kind == "validate_section":
                return await self._validate_current_section(snapshot)
            elif intent.kind == "fix_field":
                return await self._get_field_fix_guidance(intent.field, snapshot)
            elif intent.kind == "explain_field":
                return await self._explain_field(intent.field)
            elif intent.kind == "general_question":
                return await self._handle_general_question(intent.question, snapshot)
            else:
                return AgentAdvice(
                    disclaimer="Esta é uma ferramenta de apoio, não aconselhamento jurídico.",
                    say="Não entendi sua pergunta. Posso ajudá-lo com próximos passos, validação, ou explicações de campos."
                )
                
        except Exception as e:
            self.logger.error(f"Error generating advice: {e}")
            return AgentAdvice(
                disclaimer="Esta é uma ferramenta de apoio, não aconselhamento jurídico.",
                say="Desculpe, houve um erro. Como posso ajudá-lo?"
            )
    
    async def _get_field_fix_guidance(self, field: Optional[str], snapshot: Dict) -> AgentAdvice:
        """Get guidance for fixing a specific field"""
        if not field:
            return AgentAdvice(
                disclaimer="Esta é uma ferramenta de apoio, não aconselhamento jurídico.",
                say="Qual campo você gostaria de corrigir? Posso ajudar com nome, email, telefone, endereço, ou datas."
            )
        
        tips = {
            "nome": "Verifique se o nome está exatamente como no seu passaporte, incluindo acentos e espaços",
            "email": "Confirme se o email está no formato correto, como exemplo@email.com",
            "telefone": "Inclua o código do país (+55 para Brasil) e o DDD",
            "endereço": "Use o endereço completo onde você recebe correspondência, incluindo CEP",
            "data": "Use o formato DD/MM/YYYY e verifique se a data está correta"
        }
        
        tip = tips.get(field, f"Verifique o campo {field} cuidadosamente")
        
        return AgentAdvice(
            disclaimer="Esta é uma ferramenta de apoio, não aconselhamento jurídico.",
            say=f"Para corrigir o campo {field}: {tip}",
            howToVerify=[tip, "Confirme com documentos oficiais", "Verifique a formatação"]
        )
    
    async def _explain_field(self, field: Optional[str]) -> AgentAdvice:
        """Explain what a field means"""
        if not field:
            return AgentAdvice(
                disclaimer="Esta é uma ferramenta de apoio, não aconselhamento jurídico.",
                say="Qual campo você gostaria que eu explicasse?"
            )
        
        explanations = {
            "nome": "Nome completo como aparece no seu documento de identidade ou passaporte",
            "email": "Seu endereço de email principal para correspondência oficial",
            "telefone": "Número de telefone com código do país para contato",
            "endereço": "Endereço residencial atual onde você recebe correspondência",
            "data": "Data no formato dia/mês/ano, como 15/03/1990"
        }
        
        explanation = explanations.get(field, f"Campo {field} requer informações específicas")
        
        return AgentAdvice(
            disclaimer="Esta é uma ferramenta de apoio, não aconselhamento jurídico.",
            say=f"O campo {field} significa: {explanation}",
            howToVerify=[f"Confirme {field} com documentos oficiais"]
        )
    
    async def _handle_general_question(self, question: str, snapshot: Dict) -> AgentAdvice:
        """Handle general questions using LLM with guardrails"""
        try:
            # Create prompt with guardrails
            prompt = f"""
Você é um assistente de conformidade do sistema Osprey para aplicações de imigração.

REGRAS IMPORTANTES:
- Não dar aconselhamento jurídico
- Sempre incluir disclaimer sobre ferramenta de apoio
- Não inventar prazos, eligibilidade ou status
- Não preencher dados do usuário
- Quando não puder confirmar algo, dizer "Não posso verificar isso" e prefixar [Não verificado]

PERGUNTA DO USUÁRIO: {question}

CONTEXTO ATUAL: O usuário está preenchendo um formulário de auto-aplicação

Responda de forma útil mas sempre dentro dos guardrails.
"""

            # Call OpenAI with guardrails
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Você é um assistente de conformidade que ajuda com preenchimento de formulários, mas nunca dá aconselhamento jurídico."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=200
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            return AgentAdvice(
                disclaimer="Esta é uma ferramenta de apoio, não aconselhamento jurídico.",
                say=ai_response,
                unresolved=["[Não verificado] Consulte um advogado para questões jurídicas específicas"]
            )
            
        except Exception as e:
            self.logger.error(f"Error handling general question: {e}")
            return AgentAdvice(
                disclaimer="Esta é uma ferramenta de apoio, não aconselhamento jurídico.",
                say="Posso ajudá-lo com preenchimento de formulários, próximos passos, ou validação de campos. Como posso ajudar?"
            )

# Global instance
voice_agent = VoiceAgent()