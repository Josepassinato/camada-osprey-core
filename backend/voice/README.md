# Voice Processing Package

This package handles voice-based interactions for the Osprey immigration platform, providing real-time guidance and assistance during form filling.

## Components

### VoiceAgent (`agent.py`)
The main voice processing agent that handles:
- Voice message processing and intent recognition
- Form state analysis and validation
- Guidance generation based on user context
- Multi-language support (Portuguese, English)

**Key Features:**
- Intent parsing from voice transcriptions
- Section-by-section guidance
- Field validation and error detection
- Verification tips and best practices
- LLM-powered general question handling

### VoiceWebSocketManager (`websocket.py`)
WebSocket connection manager for real-time voice interactions:
- Connection lifecycle management
- Message routing to VoiceAgent
- Session tracking and metrics
- Error handling and recovery

## Usage

### Basic Import
```python
from backend.voice import voice_agent, voice_manager
```

### Using the Voice Agent
```python
from backend.voice import voice_agent

# Process a voice message
response = await voice_agent.process_voice_message(
    session_id="user_123",
    message={
        "type": "voice_input",
        "transcription": "Qual é o próximo passo?"
    }
)
```

### WebSocket Integration
```python
from backend.voice import voice_manager
from fastapi import WebSocket

@app.websocket("/ws/voice/{session_id}")
async def voice_endpoint(websocket: WebSocket, session_id: str):
    await voice_manager.connect(websocket, session_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            response = await voice_manager.handle_message(session_id, message)
            await voice_manager.send_personal_message(session_id, response)
    except WebSocketDisconnect:
        voice_manager.disconnect(session_id)
```

## Message Types

### Snapshot
Update form state for analysis:
```json
{
    "type": "snapshot",
    "snapshot": {
        "sections": [...],
        "fields": [...],
        "stepId": "personal_info"
    }
}
```

### Voice Input
Process voice transcription:
```json
{
    "type": "voice_input",
    "transcription": "Como preencho o campo de endereço?"
}
```

### Request Guidance
Explicit guidance request:
```json
{
    "type": "request_guidance",
    "request_type": "next_step"
}
```

## Intent Recognition

The voice agent recognizes the following intents:
- **next_step**: Navigate to next section
- **status**: Check current progress
- **validate_section**: Validate current section
- **fix_field**: Get help fixing a specific field
- **explain_field**: Get explanation of a field
- **general_question**: General questions (uses LLM)

## Guardrails

The voice agent implements strict guardrails:
- ✅ No legal advice
- ✅ Always includes disclaimer
- ✅ No fabricated deadlines or eligibility
- ✅ No automatic data filling
- ✅ Clear marking of unverified information

## API Endpoints

### WebSocket
- `WS /ws/voice/{session_id}` - Real-time voice interaction

### REST
- `POST /api/validate` - Validate form step
- `POST /api/analyze` - Analyze form state with LLM
- `GET /api/voice/status` - Get voice agent status

## Dependencies

- FastAPI (WebSocket support)
- Python 3.11+
- Async/await support

## Future Enhancements

- [ ] Integration with Portkey for LLM calls
- [ ] Enhanced intent recognition with ML models
- [ ] Multi-language expansion
- [ ] Voice synthesis for responses
- [ ] Advanced context tracking
