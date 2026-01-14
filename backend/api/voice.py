import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect

from backend.voice.websocket import voice_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")
ws_router = APIRouter()


@ws_router.websocket("/ws/voice/{session_id}")
async def voice_websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for voice agent interactions"""
    await voice_manager.connect(websocket, session_id)

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            response = await voice_manager.handle_message(session_id, message)

            await voice_manager.send_personal_message(session_id, response)

    except WebSocketDisconnect:
        voice_manager.disconnect(session_id)
    except Exception as e:
        logger.error(f"Voice WebSocket error for {session_id}: {e}")
        voice_manager.disconnect(session_id)


@router.post("/validate")
async def validate_form_step(request: dict):
    """Validate form data for a specific step (Osprey Owl Tutor)"""
    try:
        step_id = request.get("stepId", "")
        form_data = request.get("formData", {})

        if not step_id:
            raise HTTPException(status_code=400, detail="stepId is required")

        from validate_endpoint import form_validator

        result = form_validator.validate_step(step_id, form_data)

        return result.to_dict()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating form step: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error validating form step: {str(e)}")


@router.post("/analyze")
async def analyze_with_llm(request: dict):
    """Analyze form state using LLM with guardrails"""
    try:
        from backend.voice.agent import voice_agent

        snapshot = {
            "sections": request.get("sections", []),
            "fields": request.get("fields", []),
            "stepId": request.get("stepId", ""),
            "formId": request.get("formId", ""),
            "userId": "temp_user",
            "url": request.get("url", ""),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "siteVersionHash": "v1.0.0",
        }

        advice = await voice_agent._analyze_current_state(snapshot)

        return {
            "advice": advice.__dict__,
            "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        logger.error(f"Error in LLM analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in LLM analysis: {str(e)}")


@router.get("/voice/status")
async def voice_agent_status():
    """Get voice agent status and metrics"""
    try:
        return {
            "status": "active",
            "active_sessions": voice_manager.get_session_count(),
            "capabilities": [
                "voice_guidance",
                "form_validation",
                "step_assistance",
                "intent_recognition",
            ],
            "supported_languages": ["pt-BR", "en-US"],
            "version": "1.0.0",
        }
    except Exception as e:
        logger.error(f"Error getting voice status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting voice status: {str(e)}")
