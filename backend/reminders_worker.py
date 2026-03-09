"""
Reminders Worker — Background task that checks for pending reminders
and upcoming deadlines, sends WhatsApp alerts via the gateway.

Started as an asyncio task during server startup.
"""

import asyncio
import os
from datetime import datetime, timedelta, timezone

import httpx

WHATSAPP_GATEWAY = os.environ.get("WHATSAPP_GATEWAY_URL", "http://localhost:3003")
INTERNAL_TOKEN = os.environ.get("BACKEND_INTERNAL_TOKEN", "imigrai-internal-2024")

# Check every 60 seconds
CHECK_INTERVAL = 60

# Track daily deadline alerts already sent (reset each day)
_sent_today: set[str] = set()
_last_reset_date: str = ""


async def send_whatsapp(phone: str, message: str) -> bool:
    """Send a WhatsApp message via the gateway."""
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{WHATSAPP_GATEWAY}/send",
                json={"to": phone, "message": message},
                headers={"X-Internal-Token": INTERNAL_TOKEN},
            )
            return resp.status_code == 200
    except Exception as e:
        print(f"⚠️ WhatsApp send error: {e}")
        return False


async def _get_office_phones(db, office_id: str) -> list[str]:
    """Get WhatsApp phone numbers for an office."""
    office = await db.offices.find_one(
        {"office_id": office_id},
        {"_id": 0, "whatsapp_numbers": 1},
    )
    if not office:
        return []
    return [
        n.get("phone") for n in office.get("whatsapp_numbers", [])
        if n.get("phone")
    ]


async def process_reminders(db):
    """Check and fire pending reminders."""
    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()

    # Find pending reminders whose time has come
    cursor = db.reminders.find({
        "status": "pending",
        "remind_at": {"$lte": now_iso},
    })

    async for reminder in cursor:
        office_id = reminder.get("office_id")
        message = reminder.get("message", "")
        case_id = reminder.get("case_id")
        reminder_id = reminder.get("reminder_id")

        # Build alert message
        alert = f"⏰ *Lembrete*\n{message}"
        if case_id:
            alert += f"\nCaso: {case_id}"

        # Send to all office phones
        phones = await _get_office_phones(db, office_id)
        sent = False
        for phone in phones:
            if await send_whatsapp(phone, alert):
                sent = True

        # Mark as sent
        new_status = "sent" if sent else "failed"
        await db.reminders.update_one(
            {"reminder_id": reminder_id},
            {"$set": {"status": new_status, "sent_at": now}},
        )

        if sent:
            print(f"✅ Reminder {reminder_id} sent to {len(phones)} phones")
        else:
            print(f"❌ Reminder {reminder_id} failed (no phones or gateway down)")


async def process_deadline_alerts(db):
    """Check for deadlines within 3 days and send proactive alerts."""
    global _sent_today, _last_reset_date

    now = datetime.now(timezone.utc)
    today_str = now.strftime("%Y-%m-%d")

    # Reset daily tracker
    if today_str != _last_reset_date:
        _sent_today = set()
        _last_reset_date = today_str

    # Only run deadline checks at 8:00-8:05 AM UTC (roughly morning in US)
    if now.hour != 13 or now.minute > 5:  # 13 UTC = ~8 AM EST
        return

    three_days = now + timedelta(days=3)

    active_statuses = [
        "intake", "docs_pending", "docs_review", "forms_gen",
        "attorney_review", "ready_to_file", "filed",
        "rfe_received", "rfe_response",
    ]

    # Find cases with deadlines in the next 3 days
    pipeline = [
        {"$match": {"status": {"$in": active_statuses}}},
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
        {"$match": {"deadline_date": {"$gte": now, "$lte": three_days}}},
        {"$project": {
            "_id": 0,
            "office_id": 1,
            "case_id": 1,
            "client_name": 1,
            "visa_type": 1,
            "deadline_title": "$deadlines.title",
            "deadline_date": "$deadlines.due_date",
        }},
        {"$sort": {"deadline_date": 1}},
    ]

    results = await db.b2b_cases.aggregate(pipeline).to_list(length=100)

    # Group by office
    by_office: dict[str, list] = {}
    for r in results:
        oid = r.get("office_id")
        if not oid:
            continue
        dedup_key = f"{oid}-{r['case_id']}-{r.get('deadline_title')}-{today_str}"
        if dedup_key in _sent_today:
            continue
        _sent_today.add(dedup_key)
        by_office.setdefault(oid, []).append(r)

    for office_id, deadlines in by_office.items():
        phones = await _get_office_phones(db, office_id)
        if not phones:
            continue

        lines = ["⚠️ *Prazos Críticos — Próximos 3 Dias*\n"]
        for d in deadlines[:10]:
            dt = d.get("deadline_date", "?")
            if isinstance(dt, str) and len(dt) > 10:
                dt = dt[:10]
            lines.append(
                f"• {d['client_name']} ({d.get('visa_type', '?')}) — "
                f"{d.get('deadline_title', 'Prazo')}: {dt}"
            )

        if len(deadlines) > 10:
            lines.append(f"\n...e mais {len(deadlines) - 10} prazos.")

        message = "\n".join(lines)
        for phone in phones:
            await send_whatsapp(phone, message)

        print(f"📅 Deadline alerts sent to office {office_id}: {len(deadlines)} deadlines")


async def process_daily_email_summary(db):
    """Send daily email summary at 13:30 UTC (~8:30 AM EST)."""
    now = datetime.now(timezone.utc)

    # Only run at 13:30-13:35 UTC
    if now.hour != 13 or now.minute < 30 or now.minute > 35:
        return

    today_str = now.strftime("%Y-%m-%d")
    dedup_key = f"daily_email_{today_str}"
    if dedup_key in _sent_today:
        return
    _sent_today.add(dedup_key)

    try:
        from email_service import send_daily_summary
    except ImportError:
        print("⚠️ email_service not available, skipping daily email summary")
        return

    # Get all offices with email configured
    offices = await db.offices.find(
        {"email_contacts": {"$exists": True, "$ne": []}},
        {"_id": 0, "office_id": 1, "name": 1, "email_contacts": 1},
    ).to_list(length=100)

    if not offices:
        # Fallback: get offices with any data
        offices = await db.offices.find(
            {},
            {"_id": 0, "office_id": 1, "name": 1, "email_contacts": 1},
        ).to_list(length=100)

    for office in offices:
        office_id = office.get("office_id")
        if not office_id:
            continue

        emails = [
            e.get("email") for e in office.get("email_contacts", [])
            if e.get("email")
        ]
        if not emails:
            continue

        active_statuses = [
            "intake", "docs_pending", "docs_review", "forms_gen",
            "attorney_review", "ready_to_file", "filed",
            "rfe_received", "rfe_response",
        ]

        # Gather stats
        active = await db.b2b_cases.count_documents(
            {"office_id": office_id, "status": {"$in": active_statuses}}
        )
        pending_review = await db.b2b_cases.count_documents(
            {"office_id": office_id, "status": "attorney_review"}
        )
        ready = await db.b2b_cases.count_documents(
            {"office_id": office_id, "status": "ready_to_file"}
        )
        rfe = await db.b2b_cases.count_documents(
            {"office_id": office_id, "status": {"$in": ["rfe_received", "rfe_response"]}}
        )

        stats = {
            "active": active,
            "pending_review": pending_review,
            "ready_to_file": ready,
            "rfe_pending": rfe,
        }

        # Deadlines next 7 days
        week = now + timedelta(days=7)
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
                "_id": 0, "client_name": 1, "visa_type": 1,
                "deadline_title": "$deadlines.title",
                "deadline_date": "$deadlines.due_date",
            }},
            {"$sort": {"deadline_date": 1}},
        ]
        deadlines = await db.b2b_cases.aggregate(deadline_pipeline).to_list(length=20)

        # Idle cases
        idle_cutoff = now - timedelta(days=14)
        idle_cases = await db.b2b_cases.find(
            {"office_id": office_id, "status": {"$in": active_statuses}, "updated_at": {"$lt": idle_cutoff}},
            {"_id": 0, "client_name": 1, "visa_type": 1, "updated_at": 1},
        ).to_list(length=10)

        result = await send_daily_summary(
            to=emails,
            office_name=office.get("name", "Your Firm"),
            stats=stats,
            deadlines=deadlines,
            idle_cases=idle_cases,
        )

        if result.get("success"):
            print(f"📧 Daily email summary sent to {office_id}: {len(emails)} recipients")
        else:
            print(f"❌ Daily email summary failed for {office_id}: {result.get('error')}")


async def process_idle_case_alerts(db):
    """Weekly check: cases with no activity in 14+ days."""
    now = datetime.now(timezone.utc)

    # Only run on Mondays at 14:00 UTC (~9 AM EST)
    if now.weekday() != 0 or now.hour != 14 or now.minute > 5:
        return

    idle_cutoff = now - timedelta(days=14)
    active_statuses = [
        "intake", "docs_pending", "docs_review", "forms_gen",
        "attorney_review", "ready_to_file", "rfe_received", "rfe_response",
    ]

    cases = await db.b2b_cases.find(
        {"status": {"$in": active_statuses}, "updated_at": {"$lt": idle_cutoff}},
        {"_id": 0, "office_id": 1, "case_id": 1, "client_name": 1, "visa_type": 1, "updated_at": 1},
    ).to_list(length=200)

    by_office: dict[str, list] = {}
    for c in cases:
        oid = c.get("office_id")
        if oid:
            by_office.setdefault(oid, []).append(c)

    for office_id, idle_cases in by_office.items():
        phones = await _get_office_phones(db, office_id)
        if not phones:
            continue

        lines = ["📋 *Casos Inativos (14+ dias sem atividade)*\n"]
        for c in idle_cases[:10]:
            days_idle = (now - c.get("updated_at", now)).days if c.get("updated_at") else "?"
            lines.append(
                f"• {c['client_name']} ({c.get('visa_type', '?')}) — "
                f"{days_idle} dias sem atualização"
            )

        if len(idle_cases) > 10:
            lines.append(f"\n...e mais {len(idle_cases) - 10} casos.")

        message = "\n".join(lines)
        for phone in phones:
            await send_whatsapp(phone, message)

        print(f"📋 Idle case alerts sent to office {office_id}: {len(idle_cases)} cases")


async def reminders_loop(db):
    """Main worker loop — runs as a background asyncio task."""
    print("✅ Reminders Worker started")

    while True:
        try:
            await process_reminders(db)
            await process_deadline_alerts(db)
            await process_daily_email_summary(db)
            await process_idle_case_alerts(db)
        except Exception as e:
            print(f"❌ Reminders Worker error: {e}")

        await asyncio.sleep(CHECK_INTERVAL)


def start_reminders_worker(db):
    """Launch the worker as a background task. Call from server startup."""
    asyncio.create_task(reminders_loop(db))
    print("✅ Reminders Worker scheduled")
