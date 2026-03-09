"""
Firm Memory API — Sistema de memória adaptativa por escritório.
O agente aprende padrões, estratégias e preferências de cada advogado.
"""

from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid
import os

router = APIRouter(prefix="/api/memory", tags=["firm-memory"])

INTERNAL_TOKEN = os.getenv("BACKEND_INTERNAL_TOKEN", "imigrai-internal-2024")

db = None

def init_db(database):
    global db
    db = database

# ── SCHEMAS ─────────────────────────────────────────────────────

class MemoryCreate(BaseModel):
    office_id: str
    memory_type: str        # strategy | pattern | preference | checklist_rule | warning
    visa_type: Optional[str] = None   # None = aplica a todos os tipos
    trigger: Optional[str] = None     # quando aplicar: new_case, rfe, missing_docs, etc.
    content: str            # o que o agente deve lembrar/fazer
    source: str = "explicit"          # explicit | learned
    confidence: float = 1.0           # 0.0 a 1.0

class MemoryUpdate(BaseModel):
    content: Optional[str] = None
    active: Optional[bool] = None
    confidence: Optional[float] = None

class MemoryApplied(BaseModel):
    memory_id: str
    office_id: str
    case_id: Optional[str] = None
    result: str             # applied | skipped | rejected

# ── CRIAR MEMÓRIA ────────────────────────────────────────────────
@router.post("/")
async def create_memory(req: MemoryCreate,
                        x_internal_token: str = Header(None)):
    if x_internal_token != INTERNAL_TOKEN:
        raise HTTPException(status_code=401)

    # Checar se já existe memória similar para evitar duplicatas
    existing = await db.firm_memory.find_one({
        "office_id": req.office_id,
        "memory_type": req.memory_type,
        "visa_type": req.visa_type,
        "active": True,
        "content": {"$regex": req.content[:40], "$options": "i"}
    })

    if existing:
        # Reforçar confiança se já existe
        await db.firm_memory.update_one(
            {"_id": existing["_id"]},
            {"$inc": {"times_reinforced": 1},
             "$set": {"confidence": min(1.0, existing.get("confidence", 0.8) + 0.05),
                      "last_reinforced": datetime.utcnow()}}
        )
        return {"action": "reinforced", "memory_id": str(existing["_id"]),
                "message": "Existing memory reinforced"}

    memory = {
        "memory_id": "MEM-" + str(uuid.uuid4())[:8].upper(),
        "office_id": req.office_id,
        "memory_type": req.memory_type,
        "visa_type": req.visa_type,
        "trigger": req.trigger,
        "content": req.content,
        "source": req.source,
        "confidence": req.confidence,
        "times_applied": 0,
        "times_reinforced": 0,
        "times_rejected": 0,
        "active": True,
        "created_at": datetime.utcnow(),
        "last_applied": None,
        "last_reinforced": None
    }

    await db.firm_memory.insert_one(memory)
    return {"action": "created", "memory_id": memory["memory_id"],
            "message": "Memory saved successfully"}


# ── LISTAR MEMÓRIAS DO ESCRITÓRIO ────────────────────────────────
@router.get("/{office_id}")
async def list_memories(office_id: str,
                        memory_type: Optional[str] = None,
                        visa_type: Optional[str] = None,
                        active_only: bool = True):
    query = {"office_id": office_id}
    if active_only:
        query["active"] = True
    if memory_type:
        query["memory_type"] = memory_type
    if visa_type:
        query["$or"] = [{"visa_type": visa_type}, {"visa_type": None}]

    memories = await db.firm_memory.find(query).sort(
        "confidence", -1).to_list(length=200)

    return {
        "office_id": office_id,
        "total": len(memories),
        "memories": [{
            "memory_id": m.get("memory_id"),
            "type": m.get("memory_type"),
            "visa_type": m.get("visa_type", "All visas"),
            "trigger": m.get("trigger"),
            "content": m.get("content"),
            "source": m.get("source"),
            "confidence": m.get("confidence"),
            "times_applied": m.get("times_applied", 0),
            "active": m.get("active"),
            "created_at": m.get("created_at", "").isoformat()
                if hasattr(m.get("created_at", ""), "isoformat") else ""
        } for m in memories]
    }


# ── BUSCAR MEMÓRIAS RELEVANTES (usado pelo agente) ───────────────
@router.get("/{office_id}/relevant")
async def get_relevant_memories(
    office_id: str,
    visa_type: Optional[str] = None,
    trigger: Optional[str] = None,
    min_confidence: float = 0.5,
    x_internal_token: str = Header(None)
):
    if x_internal_token != INTERNAL_TOKEN:
        raise HTTPException(status_code=401)

    query = {
        "office_id": office_id,
        "active": True,
        "confidence": {"$gte": min_confidence}
    }

    # Visa type filter: pega memórias do tipo específico OU globais (None)
    if visa_type:
        query["$or"] = [
            {"visa_type": visa_type},
            {"visa_type": None},
            {"visa_type": {"$exists": False}}
        ]

    if trigger:
        query["trigger"] = {"$in": [trigger, "any", None]}

    memories = await db.firm_memory.find(query).sort(
        "confidence", -1).to_list(length=50)

    return {
        "count": len(memories),
        "memories": [{
            "memory_id": m.get("memory_id"),
            "type": m.get("memory_type"),
            "content": m.get("content"),
            "confidence": m.get("confidence"),
            "visa_type": m.get("visa_type"),
            "auto_apply": m.get("confidence", 0) >= 0.85
        } for m in memories]
    }


# ── REGISTRAR USO DE MEMÓRIA ─────────────────────────────────────
@router.post("/applied")
async def register_memory_applied(
    req: MemoryApplied,
    x_internal_token: str = Header(None)
):
    if x_internal_token != INTERNAL_TOKEN:
        raise HTTPException(status_code=401)

    memory = await db.firm_memory.find_one({
        "memory_id": req.memory_id,
        "office_id": req.office_id
    })

    if not memory:
        raise HTTPException(status_code=404)

    if req.result == "applied":
        new_confidence = min(1.0, memory.get("confidence", 0.8) + 0.03)
        await db.firm_memory.update_one(
            {"memory_id": req.memory_id},
            {"$inc": {"times_applied": 1},
             "$set": {"confidence": new_confidence,
                      "last_applied": datetime.utcnow()}}
        )
    elif req.result == "rejected":
        new_confidence = max(0.1, memory.get("confidence", 0.8) - 0.15)
        await db.firm_memory.update_one(
            {"memory_id": req.memory_id},
            {"$inc": {"times_rejected": 1},
             "$set": {"confidence": new_confidence}}
        )
        if memory.get("times_rejected", 0) >= 2:
            await db.firm_memory.update_one(
                {"memory_id": req.memory_id},
                {"$set": {"active": False}}
            )

    return {"ok": True, "result": req.result,
            "memory_id": req.memory_id}


# ── EDITAR / DESATIVAR MEMÓRIA ───────────────────────────────────
@router.patch("/{memory_id}")
async def update_memory(memory_id: str, req: MemoryUpdate,
                        x_internal_token: str = Header(None)):
    if x_internal_token != INTERNAL_TOKEN:
        raise HTTPException(status_code=401)

    update = {"$set": {}}
    if req.content is not None:
        update["$set"]["content"] = req.content
    if req.active is not None:
        update["$set"]["active"] = req.active
    if req.confidence is not None:
        update["$set"]["confidence"] = req.confidence
    update["$set"]["updated_at"] = datetime.utcnow()

    result = await db.firm_memory.update_one(
        {"memory_id": memory_id}, update)

    if result.matched_count == 0:
        raise HTTPException(status_code=404)

    return {"ok": True, "memory_id": memory_id}


# ── DELETAR MEMÓRIA ──────────────────────────────────────────────
@router.delete("/{office_id}/{memory_id}")
async def delete_memory(office_id: str, memory_id: str,
                        x_internal_token: str = Header(None)):
    if x_internal_token != INTERNAL_TOKEN:
        raise HTTPException(status_code=401)

    await db.firm_memory.delete_one({
        "memory_id": memory_id,
        "office_id": office_id
    })
    return {"ok": True, "deleted": memory_id}
