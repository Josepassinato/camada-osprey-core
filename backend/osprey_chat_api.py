"""
Osprey Legal Chat API
B2B Immigration Law Chat for Attorneys — Chief of Staff AI
Uses Google Gemini directly via google-generativeai
"""

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import os
import jwt

import google.generativeai as genai

router = APIRouter(prefix="/api/osprey-chat", tags=["osprey-chat"])

# Support both key names
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY') or os.environ.get('EMERGENT_LLM_KEY') or os.environ.get('GOOGLE_API_KEY')

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    print("✅ Osprey Legal Chat configured with Gemini API Key")
else:
    print("⚠️ No Gemini API key found (GEMINI_API_KEY / EMERGENT_LLM_KEY / GOOGLE_API_KEY)")

# MongoDB reference
db = None

def init_db(database):
    """Initialize database reference"""
    global db
    db = database


# ============================================================================
# SYSTEM PROMPT — Chief of Staff for Immigration Law
# ============================================================================

SYSTEM_PROMPT = """You are the Chief of Staff for an immigration law firm — a highly knowledgeable, efficient, and professional AI assistant built specifically for B2B use by attorneys and paralegals.

Your role is to support legal professionals with:

CORE CAPABILITIES:
1. **Case Strategy & Analysis**: Analyze case facts, identify potential issues, suggest legal strategies, and flag risks. Always cite relevant INA sections, CFR regulations, and USCIS policy manual references.

2. **Form & Filing Guidance**: Provide detailed guidance on USCIS forms (I-129, I-140, I-130, I-485, I-765, I-131, etc.), filing procedures, required evidence, and processing times. Know the differences between service centers and field offices.

3. **Legal Research**: Help research immigration law topics, recent AAO decisions, BIA precedent decisions, circuit court rulings, and policy changes. Stay current with USCIS policy alerts and AILA practice pointers.

4. **Client Communication Drafts**: Draft professional client communications, RFE responses, cover letters, legal briefs, and internal case memos. Maintain appropriate legal tone and precision.

5. **Deadline & Compliance Tracking**: Help track filing deadlines, maintenance of status requirements, visa validity periods, and compliance obligations for employers (LCA, PERM, I-9, etc.).

6. **Visa Category Expertise**: Deep knowledge across all visa categories:
   - Employment-based: H-1B, L-1A/B, O-1A/B, E-1/E-2/E-3, TN, H-2A/B, EB-1/2/3/4/5
   - Family-based: IR, F1-F4, K-1/K-3, V visa
   - Humanitarian: Asylum, TPS, U visa, T visa, VAWA, DACA, Parole
   - Business: B-1/B-2, Treaty Investor/Trader
   - Student: F-1, J-1, M-1, STEM OPT, CPT, Academic Training

COMMUNICATION STYLE:
- Professional, concise, and legally precise
- Use proper legal terminology
- Cite specific statutes, regulations, and policy references when applicable
- Flag when something requires attorney judgment vs. paralegal-level task
- Always note when information may have changed due to recent policy updates
- Include relevant practice tips and common pitfalls

IMPORTANT DISCLAIMERS:
- You are an AI assistant tool, not a licensed attorney
- Your analysis supports but does not replace attorney judgment
- Always recommend attorney review for final case decisions
- Note when case-specific facts could change the analysis
- Flag jurisdictional variations when relevant

RESPONSE FORMAT:
- Use clear headers and bullet points for readability
- Bold key terms and citations
- Provide actionable next steps when appropriate
- Keep responses focused and relevant to the query"""


# ============================================================================
# MODELS
# ============================================================================

JWT_SECRET = os.environ.get("JWT_SECRET", "osprey-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"


class OspreyChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None
    firm_name: Optional[str] = None
    office_id: Optional[str] = None
    channel: Optional[str] = "web"


class OspreyChatResponse(BaseModel):
    response: str
    conversation_id: str
    timestamp: str


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/chat", response_model=OspreyChatResponse)
async def osprey_legal_chat(chat_msg: OspreyChatMessage, authorization: Optional[str] = Header(None)):
    """
    Chat with Osprey Legal AI — Chief of Staff for immigration attorneys.
    Uses Google Gemini 2.0 Flash.
    Supports optional JWT auth for multi-tenant isolation.
    """
    try:
        if not GEMINI_API_KEY:
            raise HTTPException(status_code=500, detail="Gemini API key not configured")

        # Extract office_id from JWT if present
        office_id = chat_msg.office_id
        if authorization and authorization.startswith("Bearer "):
            try:
                token = authorization.replace("Bearer ", "")
                payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
                office_id = payload.get("office_id", office_id)
                if not chat_msg.user_id:
                    chat_msg.user_id = payload.get("user_id")
            except Exception:
                pass  # Token is optional, continue without it

        conversation_id = chat_msg.conversation_id or str(uuid.uuid4())

        # Build system prompt with firm name if provided
        system = SYSTEM_PROMPT
        if chat_msg.firm_name:
            system += f"\n\nYou are the Chief of Staff for {chat_msg.firm_name}."

        # Build conversation history from DB (filtered by office_id if available)
        gemini_history = []
        if chat_msg.conversation_id and db is not None:
            history_query = {"conversation_id": conversation_id}
            if office_id:
                history_query["office_id"] = office_id
            history = await db.osprey_chat_conversations.find(
                history_query
            ).sort("timestamp", 1).to_list(length=20)

            for msg in history:
                gemini_history.append({"role": "user", "parts": [msg.get("user_message", "")]})
                gemini_history.append({"role": "model", "parts": [msg.get("ai_response", "")]})

        # Create Gemini model and chat session
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=system
        )
        chat = model.start_chat(history=gemini_history)

        # Send message
        response = chat.send_message(chat_msg.message)
        response_text = response.text

        now = datetime.utcnow()

        # Save to MongoDB
        if db is not None:
            await db.osprey_chat_conversations.insert_one({
                "conversation_id": conversation_id,
                "user_id": chat_msg.user_id,
                "firm_name": chat_msg.firm_name,
                "office_id": office_id,
                "channel": chat_msg.channel or "web",
                "user_message": chat_msg.message,
                "ai_response": response_text,
                "timestamp": now
            })

        return OspreyChatResponse(
            response=response_text,
            conversation_id=conversation_id,
            timestamp=now.isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Osprey Legal Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def osprey_chat_health():
    """Health check for Osprey Legal Chat"""
    return {
        "service": "Osprey Legal Chat — Chief of Staff AI",
        "status": "active" if GEMINI_API_KEY else "unconfigured",
        "model": "gemini-2.0-flash",
        "version": "1.0"
    }
