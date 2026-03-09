"""
Tool executor for Osprey Chief of Staff.
All MongoDB read/write logic for the 14 Gemini function-calling tools.
"""

import uuid
import json
import re
from datetime import datetime, timedelta, timezone

from tools.definitions import REQUIRED_DOCUMENTS, DOC_TYPE_LABELS


async def execute_tool(tool_name: str, args: dict, db, office_id: str) -> str:
    """Execute a tool call and return the result as a string for the LLM."""
    try:
        executor = EXECUTORS.get(tool_name)
        if not executor:
            return json.dumps({"error": f"Unknown tool: {tool_name}"})
        result = await executor(args, db, office_id)
        return json.dumps(result, default=str, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


# =============================================================================
# READ TOOLS
# =============================================================================

async def _get_firm_overview(args: dict, db, office_id: str) -> dict:
    now = datetime.now(timezone.utc)
    week = now + timedelta(days=7)

    active_statuses = [
        "intake", "docs_pending", "docs_review", "forms_gen",
        "attorney_review", "ready_to_file", "filed",
        "rfe_received", "rfe_response",
    ]

    total = await db.b2b_cases.count_documents({"office_id": office_id})
    active = await db.b2b_cases.count_documents(
        {"office_id": office_id, "status": {"$in": active_statuses}}
    )

    # By visa type
    type_pipeline = [
        {"$match": {"office_id": office_id, "status": {"$in": active_statuses}}},
        {"$group": {"_id": "$visa_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    by_type = {
        doc["_id"]: doc["count"]
        async for doc in db.b2b_cases.aggregate(type_pipeline)
    }

    # By status
    status_pipeline = [
        {"$match": {"office_id": office_id}},
        {"$group": {"_id": "$status", "count": {"$sum": 1}}},
    ]
    by_status = {
        doc["_id"]: doc["count"]
        async for doc in db.b2b_cases.aggregate(status_pipeline)
    }

    # Deadlines next 7 days
    deadline_pipeline = [
        {"$match": {"office_id": office_id, "status": {"$in": active_statuses}}},
        {"$unwind": {"path": "$deadlines", "preserveNullAndEmptyArrays": False}},
        {"$addFields": {
            "deadline_date": {
                "$cond": {
                    "if": {"$eq": [{"$type": "$deadlines.due_date"}, "string"]},
                    "then": {"$dateFromString": {"dateString": "$deadlines.due_date", "onError": None}},
                    "else": "$deadlines.due_date",
                }
            }
        }},
        {"$match": {"deadline_date": {"$gte": now, "$lte": week}}},
        {"$project": {
            "_id": 0, "case_id": 1, "client_name": 1,
            "deadline_title": "$deadlines.title",
            "deadline_date": "$deadlines.due_date",
        }},
        {"$sort": {"deadline_date": 1}},
    ]
    upcoming = await db.b2b_cases.aggregate(deadline_pipeline).to_list(length=20)

    # Overdue deadlines
    overdue_pipeline = [
        {"$match": {"office_id": office_id, "status": {"$in": active_statuses}}},
        {"$unwind": {"path": "$deadlines", "preserveNullAndEmptyArrays": False}},
        {"$addFields": {
            "deadline_date": {
                "$cond": {
                    "if": {"$eq": [{"$type": "$deadlines.due_date"}, "string"]},
                    "then": {"$dateFromString": {"dateString": "$deadlines.due_date", "onError": None}},
                    "else": "$deadlines.due_date",
                }
            }
        }},
        {"$match": {"deadline_date": {"$lt": now}}},
        {"$project": {
            "_id": 0, "case_id": 1, "client_name": 1,
            "deadline_title": "$deadlines.title",
            "deadline_date": "$deadlines.due_date",
        }},
    ]
    overdue = await db.b2b_cases.aggregate(overdue_pipeline).to_list(length=20)

    # Idle cases (no update in 14+ days)
    idle_cutoff = now - timedelta(days=14)
    idle_cases = await db.b2b_cases.find(
        {
            "office_id": office_id,
            "status": {"$in": active_statuses},
            "updated_at": {"$lt": idle_cutoff},
        },
        {"_id": 0, "case_id": 1, "client_name": 1, "visa_type": 1, "status": 1, "updated_at": 1},
    ).sort("updated_at", 1).to_list(length=10)

    return {
        "total_cases": total,
        "active_cases": active,
        "by_visa_type": by_type,
        "by_status": by_status,
        "deadlines_next_7_days": upcoming,
        "overdue_deadlines": overdue,
        "idle_cases_14_days": idle_cases,
    }


async def _list_cases(args: dict, db, office_id: str) -> dict:
    query = {"office_id": office_id}
    active_statuses = [
        "intake", "docs_pending", "docs_review", "forms_gen",
        "attorney_review", "ready_to_file", "filed",
        "rfe_received", "rfe_response",
    ]

    status = args.get("status")
    visa_type = args.get("visa_type")
    limit = min(args.get("limit", 20), 50)

    if status:
        query["status"] = status
    else:
        query["status"] = {"$in": active_statuses}

    if visa_type:
        query["visa_type"] = {"$regex": re.escape(visa_type), "$options": "i"}

    cases = await db.b2b_cases.find(
        query,
        {"_id": 0, "case_id": 1, "client_name": 1, "visa_type": 1, "status": 1, "updated_at": 1, "deadlines": 1},
    ).sort("updated_at", -1).to_list(length=limit)

    now = datetime.now(timezone.utc)
    result = []
    for c in cases:
        deadlines = c.pop("deadlines", [])
        next_dl = None
        for d in sorted(deadlines, key=lambda x: str(x.get("due_date", ""))):
            try:
                dt = d.get("due_date")
                if isinstance(dt, str):
                    dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
                if dt and dt > now:
                    next_dl = {"title": d.get("title"), "due_date": str(d.get("due_date"))}
                    break
            except Exception:
                continue
        c["next_deadline"] = next_dl
        c["doc_count"] = len(c.get("documents", []))
        c.pop("documents", None)
        result.append(c)

    return {"cases": result, "count": len(result)}


async def _get_case(args: dict, db, office_id: str) -> dict:
    case = await _resolve_case(args, db, office_id)
    if not case:
        return {"error": "Caso não encontrado. Verifique o nome do cliente ou case_id."}
    case.pop("_id", None)
    return case


async def _search_cases(args: dict, db, office_id: str) -> dict:
    query_text = args.get("query", "")
    if not query_text:
        return {"error": "Parâmetro 'query' é obrigatório."}

    regex = {"$regex": re.escape(query_text), "$options": "i"}
    cases = await db.b2b_cases.find(
        {
            "office_id": office_id,
            "$or": [
                {"client_name": regex},
                {"notes": regex},
                {"visa_type": regex},
                {"case_id": regex},
            ],
        },
        {"_id": 0, "case_id": 1, "client_name": 1, "visa_type": 1, "status": 1},
    ).to_list(length=20)

    return {"results": cases, "count": len(cases)}


async def _get_deadlines(args: dict, db, office_id: str) -> dict:
    days = min(args.get("days_ahead", 14), 90)
    include_overdue = args.get("include_overdue", True)
    now = datetime.now(timezone.utc)
    future = now + timedelta(days=days)

    active_statuses = [
        "intake", "docs_pending", "docs_review", "forms_gen",
        "attorney_review", "ready_to_file", "filed",
        "rfe_received", "rfe_response",
    ]

    match_stage = {"$gte": now, "$lte": future}
    if include_overdue:
        match_stage = {"$lte": future}

    pipeline = [
        {"$match": {"office_id": office_id, "status": {"$in": active_statuses}}},
        {"$unwind": {"path": "$deadlines", "preserveNullAndEmptyArrays": False}},
        {"$addFields": {
            "deadline_date": {
                "$cond": {
                    "if": {"$eq": [{"$type": "$deadlines.due_date"}, "string"]},
                    "then": {"$dateFromString": {"dateString": "$deadlines.due_date", "onError": None}},
                    "else": "$deadlines.due_date",
                }
            }
        }},
        {"$match": {"deadline_date": match_stage}},
        {"$project": {
            "_id": 0, "case_id": 1, "client_name": 1, "visa_type": 1,
            "deadline_title": "$deadlines.title",
            "deadline_date": "$deadlines.due_date",
            "deadline_notes": "$deadlines.notes",
        }},
        {"$sort": {"deadline_date": 1}},
    ]
    results = await db.b2b_cases.aggregate(pipeline).to_list(length=50)

    # Tag overdue
    for r in results:
        try:
            dt = r.get("deadline_date")
            if isinstance(dt, str):
                dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
            r["is_overdue"] = dt < now if dt else False
        except Exception:
            r["is_overdue"] = False

    return {"deadlines": results, "count": len(results)}


async def _get_case_documents(args: dict, db, office_id: str) -> dict:
    case = await _resolve_case(args, db, office_id)
    if not case:
        return {"error": "Caso não encontrado."}

    docs = case.get("documents", [])
    visa = case.get("visa_type", "")
    required = REQUIRED_DOCUMENTS.get(visa, [])

    received_types = {d.get("document_type") for d in docs}
    missing = [
        {"type": t, "label": DOC_TYPE_LABELS.get(t, t)}
        for t in required if t not in received_types
    ]
    received = [
        {
            "type": d.get("document_type"),
            "label": DOC_TYPE_LABELS.get(d.get("document_type", ""), d.get("document_type", "")),
            "filename": d.get("filename"),
            "uploaded_at": d.get("uploaded_at"),
            "notes": d.get("notes"),
        }
        for d in docs
    ]

    total_required = len(required) if required else "N/A"
    return {
        "case_id": case.get("case_id"),
        "client_name": case.get("client_name"),
        "visa_type": visa,
        "received": received,
        "received_count": len(received),
        "missing": missing,
        "missing_count": len(missing),
        "total_required": total_required,
        "is_complete": len(missing) == 0 and len(required) > 0,
    }


async def _get_case_stats(args: dict, db, office_id: str) -> dict:
    active_statuses = [
        "intake", "docs_pending", "docs_review", "forms_gen",
        "attorney_review", "ready_to_file", "filed",
        "rfe_received", "rfe_response",
    ]
    now = datetime.now(timezone.utc)
    week = now + timedelta(days=7)

    total = await db.b2b_cases.count_documents({"office_id": office_id})
    active = await db.b2b_cases.count_documents(
        {"office_id": office_id, "status": {"$in": active_statuses}}
    )
    pending_review = await db.b2b_cases.count_documents(
        {"office_id": office_id, "status": "attorney_review"}
    )
    ready_to_file = await db.b2b_cases.count_documents(
        {"office_id": office_id, "status": "ready_to_file"}
    )
    rfe = await db.b2b_cases.count_documents(
        {"office_id": office_id, "status": {"$in": ["rfe_received", "rfe_response"]}}
    )
    approved = await db.b2b_cases.count_documents(
        {"office_id": office_id, "status": "approved"}
    )
    denied = await db.b2b_cases.count_documents(
        {"office_id": office_id, "status": "denied"}
    )

    return {
        "total": total,
        "active": active,
        "pending_review": pending_review,
        "ready_to_file": ready_to_file,
        "rfe_pending": rfe,
        "approved": approved,
        "denied": denied,
    }


# =============================================================================
# WRITE TOOLS
# =============================================================================

async def _create_case(args: dict, db, office_id: str) -> dict:
    client_name = args.get("client_name")
    visa_type = args.get("visa_type")
    notes = args.get("notes", "")

    if not client_name or not visa_type:
        return {"error": "client_name e visa_type são obrigatórios."}

    now = datetime.now(timezone.utc)
    case_id = "CASE-" + str(uuid.uuid4())[:8].upper()

    case_doc = {
        "case_id": case_id,
        "office_id": office_id,
        "client_name": client_name,
        "visa_type": visa_type,
        "status": "intake",
        "notes": notes,
        "documents": [],
        "deadlines": [],
        "history": [
            {"action": "case_created", "timestamp": now.isoformat(), "detail": f"Caso criado via WhatsApp"}
        ],
        "created_at": now,
        "updated_at": now,
    }

    await db.b2b_cases.insert_one(case_doc)

    required = REQUIRED_DOCUMENTS.get(visa_type, [])
    return {
        "success": True,
        "case_id": case_id,
        "client_name": client_name,
        "visa_type": visa_type,
        "status": "intake",
        "required_documents": len(required),
    }


async def _update_case(args: dict, db, office_id: str) -> dict:
    case = await _resolve_case(args, db, office_id)
    if not case:
        return {"error": "Caso não encontrado."}

    case_id = case["case_id"]
    update_fields = {}
    now = datetime.now(timezone.utc)
    history_entry = {"timestamp": now.isoformat()}

    if args.get("status"):
        valid = [
            "intake", "docs_pending", "docs_review", "forms_gen",
            "attorney_review", "ready_to_file", "filed",
            "rfe_received", "rfe_response", "approved", "denied", "withdrawn",
        ]
        if args["status"] not in valid:
            return {"error": f"Status inválido. Válidos: {', '.join(valid)}"}
        update_fields["status"] = args["status"]
        history_entry["action"] = "status_changed"
        history_entry["detail"] = f"Status: {case.get('status')} → {args['status']}"

    if args.get("notes"):
        existing = case.get("notes", "")
        separator = "\n---\n" if existing else ""
        update_fields["notes"] = f"{existing}{separator}[{now.strftime('%d/%m/%Y %H:%M')}] {args['notes']}"
        history_entry["action"] = history_entry.get("action", "note_added")
        history_entry["detail"] = history_entry.get("detail", args["notes"])

    if args.get("visa_type"):
        update_fields["visa_type"] = args["visa_type"]
        history_entry["action"] = "visa_type_changed"
        history_entry["detail"] = f"Tipo: {case.get('visa_type')} → {args['visa_type']}"

    if not update_fields:
        return {"error": "Nenhum campo para atualizar."}

    update_fields["updated_at"] = now

    await db.b2b_cases.update_one(
        {"case_id": case_id, "office_id": office_id},
        {
            "$set": update_fields,
            "$push": {"history": history_entry},
        },
    )

    return {
        "success": True,
        "case_id": case_id,
        "client_name": case.get("client_name"),
        "updated_fields": list(update_fields.keys()),
    }


async def _add_deadline(args: dict, db, office_id: str) -> dict:
    case = await _resolve_case(args, db, office_id)
    if not case:
        return {"error": "Caso não encontrado."}

    case_id = case["case_id"]
    now = datetime.now(timezone.utc)

    deadline_doc = {
        "id": str(uuid.uuid4())[:8],
        "title": args["title"],
        "due_date": args["due_date"],
        "notes": args.get("notes", ""),
        "created_at": now.isoformat(),
    }

    await db.b2b_cases.update_one(
        {"case_id": case_id, "office_id": office_id},
        {
            "$push": {
                "deadlines": deadline_doc,
                "history": {
                    "action": "deadline_added",
                    "timestamp": now.isoformat(),
                    "detail": f"Prazo: {args['title']} — {args['due_date']}",
                },
            },
            "$set": {"updated_at": now},
        },
    )

    return {
        "success": True,
        "case_id": case_id,
        "client_name": case.get("client_name"),
        "deadline": deadline_doc,
    }


async def _add_case_note(args: dict, db, office_id: str) -> dict:
    case = await _resolve_case(args, db, office_id)
    if not case:
        return {"error": "Caso não encontrado."}

    case_id = case["case_id"]
    now = datetime.now(timezone.utc)
    note = args["note"]

    existing = case.get("notes", "")
    separator = "\n---\n" if existing else ""
    updated_notes = f"{existing}{separator}[{now.strftime('%d/%m/%Y %H:%M')}] {note}"

    await db.b2b_cases.update_one(
        {"case_id": case_id, "office_id": office_id},
        {
            "$set": {"notes": updated_notes, "updated_at": now},
            "$push": {
                "history": {
                    "action": "note_added",
                    "timestamp": now.isoformat(),
                    "detail": note,
                },
            },
        },
    )

    return {
        "success": True,
        "case_id": case_id,
        "client_name": case.get("client_name"),
        "note_added": note,
    }


async def _attach_document(args: dict, db, office_id: str) -> dict:
    case = await _resolve_case(args, db, office_id)
    if not case:
        return {"error": "Caso não encontrado. Informe o case_id ou nome do cliente."}

    case_id = case["case_id"]
    now = datetime.now(timezone.utc)
    doc_type = args["document_type"]

    doc_entry = {
        "doc_id": "DOC-" + str(uuid.uuid4())[:8].upper(),
        "document_type": doc_type,
        "filename": args.get("filename", ""),
        "notes": args.get("notes", ""),
        "uploaded_at": now,
    }

    await db.b2b_cases.update_one(
        {"case_id": case_id, "office_id": office_id},
        {
            "$push": {
                "documents": doc_entry,
                "history": {
                    "action": "document_attached",
                    "timestamp": now.isoformat(),
                    "detail": f"Documento: {DOC_TYPE_LABELS.get(doc_type, doc_type)}",
                },
            },
            "$set": {"updated_at": now},
        },
    )

    # Calculate completeness
    all_docs = case.get("documents", []) + [doc_entry]
    visa = case.get("visa_type", "")
    required = REQUIRED_DOCUMENTS.get(visa, [])
    received_types = {d.get("document_type") for d in all_docs}
    missing = [t for t in required if t not in received_types]

    return {
        "success": True,
        "case_id": case_id,
        "client_name": case.get("client_name"),
        "document_added": DOC_TYPE_LABELS.get(doc_type, doc_type),
        "total_received": len(all_docs),
        "total_required": len(required) if required else "N/A",
        "missing_count": len(missing),
        "missing_documents": [DOC_TYPE_LABELS.get(m, m) for m in missing],
        "is_complete": len(missing) == 0 and len(required) > 0,
    }


async def _create_reminder(args: dict, db, office_id: str) -> dict:
    now = datetime.now(timezone.utc)
    message = args["message"]
    remind_at = args["remind_at"]

    reminder = {
        "reminder_id": "REM-" + str(uuid.uuid4())[:8].upper(),
        "office_id": office_id,
        "message": message,
        "remind_at": remind_at,
        "case_id": args.get("case_id"),
        "status": "pending",
        "created_at": now,
    }

    await db.reminders.insert_one(reminder)

    return {
        "success": True,
        "reminder_id": reminder["reminder_id"],
        "message": message,
        "remind_at": remind_at,
    }


async def _generate_letter(args: dict, db, office_id: str) -> dict:
    case = await _resolve_case(args, db, office_id)
    if not case:
        return {"error": "Caso não encontrado."}

    letter_type = args["letter_type"]
    special_instructions = args.get("special_instructions", "")

    try:
        from letter_generator import LetterGenerator

        # Enrich with office name
        office = await db.offices.find_one({"office_id": office_id}, {"_id": 0, "name": 1})
        if office:
            case["office_name"] = office.get("name", "")

        content = await LetterGenerator.generate_cover_letter(
            case, letter_type, special_instructions
        )

        letter_id = "LTR-" + str(uuid.uuid4())[:8].upper()
        now = datetime.now(timezone.utc)

        await db.letters.insert_one({
            "letter_id": letter_id,
            "case_id": case["case_id"],
            "office_id": office_id,
            "letter_type": letter_type,
            "content": content,
            "created_at": now,
        })

        # Log in case history
        await db.b2b_cases.update_one(
            {"case_id": case["case_id"], "office_id": office_id},
            {
                "$push": {
                    "history": {
                        "action": "letter_generated",
                        "timestamp": now.isoformat(),
                        "detail": f"Carta gerada: {letter_type} ({letter_id})",
                    }
                },
                "$set": {"updated_at": now},
            },
        )

        return {
            "success": True,
            "letter_id": letter_id,
            "case_id": case["case_id"],
            "client_name": case.get("client_name"),
            "letter_type": letter_type,
            "content": content,
        }

    except Exception as e:
        return {"error": f"Erro ao gerar carta: {str(e)}"}


# =============================================================================
# HELPERS
# =============================================================================

async def _resolve_case(args: dict, db, office_id: str) -> dict | None:
    """Find a case by case_id or client_name_search/client_name."""
    case_id = args.get("case_id")
    client_name = args.get("client_name_search") or args.get("client_name")

    if case_id:
        return await db.b2b_cases.find_one(
            {"case_id": case_id, "office_id": office_id}, {"_id": 0}
        )

    if client_name:
        regex = {"$regex": re.escape(client_name), "$options": "i"}
        return await db.b2b_cases.find_one(
            {"office_id": office_id, "client_name": regex}, {"_id": 0}
        )

    return None


# =============================================================================
# EXECUTOR MAP
# =============================================================================

EXECUTORS = {
    "get_firm_overview": _get_firm_overview,
    "list_cases": _list_cases,
    "get_case": _get_case,
    "search_cases": _search_cases,
    "get_deadlines": _get_deadlines,
    "get_case_documents": _get_case_documents,
    "get_case_stats": _get_case_stats,
    "create_case": _create_case,
    "update_case": _update_case,
    "add_deadline": _add_deadline,
    "add_case_note": _add_case_note,
    "attach_document": _attach_document,
    "create_reminder": _create_reminder,
    "generate_letter": _generate_letter,
}
