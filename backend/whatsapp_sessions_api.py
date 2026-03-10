"""
WhatsApp Session Manager — Imigrai
Gerencia sessões Baileys por office_id via WebSocket.
Permite onboarding inline: botão → QR Code → conectado.
"""

import asyncio
import httpx
import json
import logging
import os
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Header, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient

router = APIRouter(prefix="/api/whatsapp", tags=["whatsapp"])

logger = logging.getLogger(__name__)

MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = "osprey_immigration_db"
INTERNAL_TOKEN = os.getenv("BACKEND_INTERNAL_TOKEN", "imigrai-internal-2024")

# URL do gateway Baileys (porta 3003)
BAILEYS_URL = os.getenv("BAILEYS_URL", "http://localhost:3003")


@router.get("/status/{office_id}")
async def whatsapp_status(
    office_id: str,
    authorization: str = Header(None)
):
    """Retorna status da conexão WhatsApp do escritório."""
    db = AsyncIOMotorClient(MONGO_URI)[DB_NAME]
    office = await db.offices.find_one({"office_id": office_id})
    if not office:
        raise HTTPException(status_code=404, detail="Office not found")

    # Verificar status no gateway Baileys
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{BAILEYS_URL}/session/status/{office_id}",
                headers={"X-Internal-Token": INTERNAL_TOKEN},
                timeout=5
            )
            if resp.status_code == 200:
                data = resp.json()
                connected = data.get("connected", False)
                phone = data.get("phone_number", None)
            else:
                connected = False
                phone = None
    except Exception:
        connected = False
        phone = None

    return {
        "office_id": office_id,
        "connected": connected,
        "phone_number": phone,
        "whatsapp_number": office.get("whatsapp_number"),
    }


@router.post("/session/start/{office_id}")
async def start_whatsapp_session(
    office_id: str,
    authorization: str = Header(None)
):
    """Inicia nova sessão Baileys para o escritório — retorna session_id."""
    db = AsyncIOMotorClient(MONGO_URI)[DB_NAME]
    office = await db.offices.find_one({"office_id": office_id})
    if not office:
        raise HTTPException(status_code=404, detail="Office not found")

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{BAILEYS_URL}/session/create",
                json={"office_id": office_id},
                headers={"X-Internal-Token": INTERNAL_TOKEN},
                timeout=10
            )
            data = resp.json()
            return {
                "success": True,
                "session_id": data.get("session_id", office_id),
                "message": "Session started, waiting for QR scan"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/qr/{office_id}")
async def whatsapp_qr_websocket(websocket: WebSocket, office_id: str):
    """
    WebSocket que envia QR Code em tempo real para o frontend.
    
    Mensagens enviadas ao cliente:
    - {"type": "qr", "qr": "data:image/png;base64,..."}
    - {"type": "connected", "phone": "+1..."}
    - {"type": "error", "message": "..."}
    - {"type": "timeout"}
    """
    await websocket.accept()
    logger.info(f"WS QR connected for office {office_id}")

    try:
        # Iniciar sessão no gateway Baileys
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{BAILEYS_URL}/session/create",
                json={"office_id": office_id},
                headers={"X-Internal-Token": INTERNAL_TOKEN},
                timeout=10
            )

        # Poll QR do Baileys e repassar ao frontend via WebSocket
        timeout = 120
        elapsed = 0
        last_qr = None

        while elapsed < timeout:
            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.get(
                        f"{BAILEYS_URL}/session/qr/{office_id}",
                        headers={"X-Internal-Token": INTERNAL_TOKEN},
                        timeout=5
                    )

                if resp.status_code == 200:
                    data = resp.json()

                    if data.get("qr") and data["qr"] != last_qr:
                        last_qr = data["qr"]
                        await websocket.send_json({
                            "type": "qr",
                            "qr": data["qr"]
                        })

                    elif data.get("connected"):
                        phone = data.get("phone_number", "")
                        await websocket.send_json({
                            "type": "connected",
                            "phone": phone
                        })

                        db = AsyncIOMotorClient(MONGO_URI)[DB_NAME]
                        await db.offices.update_one(
                            {"office_id": office_id},
                            {"$set": {
                                "whatsapp_connected": True,
                                "whatsapp_number": phone,
                                "whatsapp_connected_at": datetime.utcnow()
                            }}
                        )
                        break

            except Exception as e:
                logger.error(f"QR poll error: {e}")

            await asyncio.sleep(2)
            elapsed += 2

        if elapsed >= timeout:
            await websocket.send_json({"type": "timeout"})

    except WebSocketDisconnect:
        logger.info(f"WS QR disconnected for office {office_id}")
    except Exception as e:
        logger.error(f"WS QR error: {e}")
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
