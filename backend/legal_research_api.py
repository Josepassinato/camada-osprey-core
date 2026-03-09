"""
Legal Research API — Imigrai
Busca semântica + texto na base de conhecimento jurídico indexada.
"""

import logging
import os
from typing import Optional

import numpy as np
from fastapi import APIRouter, Header, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/legal", tags=["legal-research"])

MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = "osprey_immigration_db"
COLLECTION = "legal_knowledge"
INTERNAL_TOKEN = os.getenv("BACKEND_INTERNAL_TOKEN", "imigrai-internal-2024")

# Carregar modelo uma vez na inicialização
_model = None


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def cosine_similarity(a: list, b: list) -> float:
    a_arr, b_arr = np.array(a), np.array(b)
    return float(np.dot(a_arr, b_arr) / (np.linalg.norm(a_arr) * np.linalg.norm(b_arr) + 1e-10))


class ResearchQuery(BaseModel):
    query: str
    visa_type: Optional[str] = None
    source_filter: Optional[str] = None
    max_results: int = 5
    min_similarity: float = 0.35


@router.post("/research")
async def legal_research(
    req: ResearchQuery,
    x_internal_token: str = Header(None),
):
    if x_internal_token != INTERNAL_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

    db = AsyncIOMotorClient(MONGO_URI)[DB_NAME]
    model = get_model()

    # 1. Embedding da query
    query_embedding = model.encode([req.query])[0].tolist()

    # 2. Filtro MongoDB
    mongo_filter = {}
    if req.visa_type:
        mongo_filter["visa_types"] = req.visa_type
    if req.source_filter:
        mongo_filter["source"] = req.source_filter

    # 3. Busca texto (MongoDB $text) — rápida, para pré-filtro
    projection = {
        "text": 1,
        "embedding": 1,
        "source": 1,
        "url": 1,
        "visa_types": 1,
        "case_name": 1,
        "volume_name": 1,
        "part_name": 1,
        "date_filed": 1,
    }

    text_filter = {**mongo_filter, "$text": {"$search": req.query}}
    candidates = await db[COLLECTION].find(text_filter, projection).limit(50).to_list(50)

    # Se poucos resultados, buscar sem filtro de texto
    if len(candidates) < 10:
        extra = (
            await db[COLLECTION].find(mongo_filter, projection).limit(100).to_list(100)
        )
        candidates += extra

    # 4. Re-ranquear por similaridade semântica
    scored = []
    seen_texts = set()
    for doc in candidates:
        if "embedding" not in doc:
            continue
        text_key = doc["text"][:100]
        if text_key in seen_texts:
            continue
        seen_texts.add(text_key)

        sim = cosine_similarity(query_embedding, doc["embedding"])
        if sim >= req.min_similarity:
            scored.append((sim, doc))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[: req.max_results]

    # 5. Formatar resposta
    source_labels = {
        "uscis_policy_manual": "USCIS Policy Manual",
        "cfr_title_8": "CFR Title 8",
        "aao_decisions": "AAO Decision",
    }

    results = []
    for sim, doc in top:
        metadata = {}
        if doc.get("volume_name"):
            metadata["volume"] = doc["volume_name"]
        if doc.get("part_name"):
            metadata["part"] = doc["part_name"]
        if doc.get("case_name"):
            metadata["case"] = doc["case_name"]
        if doc.get("date_filed"):
            metadata["date"] = doc["date_filed"]

        results.append(
            {
                "text": doc["text"],
                "source": source_labels.get(doc.get("source", ""), doc.get("source", "")),
                "url": doc.get("url", ""),
                "similarity": round(sim, 3),
                "visa_types": doc.get("visa_types", []),
                "metadata": metadata,
            }
        )

    return {
        "query": req.query,
        "visa_type": req.visa_type,
        "total_results": len(results),
        "results": results,
    }


@router.get("/stats")
async def knowledge_base_stats(x_internal_token: str = Header(None)):
    if x_internal_token != INTERNAL_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

    db = AsyncIOMotorClient(MONGO_URI)[DB_NAME]

    total = await db[COLLECTION].count_documents({})
    by_source = {}
    for source in ["uscis_policy_manual", "cfr_title_8", "aao_decisions"]:
        count = await db[COLLECTION].count_documents({"source": source})
        by_source[source] = count

    return {
        "total_chunks": total,
        "by_source": by_source,
        "model": "all-MiniLM-L6-v2",
        "ready": total > 0,
    }
