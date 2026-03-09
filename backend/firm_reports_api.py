"""
Firm Reports API — Aggregated reports for the entire law firm.
Dashboards, KPIs, and case pipeline analytics.
"""

import os
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse

from backend.core.database import db
from backend.b2b_auth_api import get_b2b_user

router = APIRouter(prefix="/api/firm-reports", tags=["firm-reports"])


@router.get("/summary")
async def firm_summary(current_user=Depends(get_b2b_user)):
    """Get firm-wide KPIs: total cases, by status, by visa type, conversion rates."""
    office_id = current_user["office_id"]
    now = datetime.now(timezone.utc)

    active_statuses = [
        "intake", "docs_pending", "docs_review", "forms_gen",
        "attorney_review", "ready_to_file", "filed",
        "rfe_received", "rfe_response",
    ]

    total = await db.b2b_cases.count_documents({"office_id": office_id})
    active = await db.b2b_cases.count_documents(
        {"office_id": office_id, "status": {"": active_statuses}}
    )
    approved = await db.b2b_cases.count_documents(
        {"office_id": office_id, "status": "approved"}
    )
    denied = await db.b2b_cases.count_documents(
        {"office_id": office_id, "status": "denied"}
    )

    # By status
    status_pipeline = [
        {"": {"office_id": office_id}},
        {"": {"_id": "", "count": {"": 1}}},
        {"": {"count": -1}},
    ]
    by_status = {r["_id"]: r["count"] async for r in db.b2b_cases.aggregate(status_pipeline)}

    # By visa type
    type_pipeline = [
        {"": {"office_id": office_id, "status": {"": active_statuses}}},
        {"": {"_id": "", "count": {"": 1}}},
        {"": {"count": -1}},
    ]
    by_visa = {r["_id"]: r["count"] async for r in db.b2b_cases.aggregate(type_pipeline)}

    # Upcoming deadlines (7 days)
    week = now + timedelta(days=7)
    deadline_pipeline = [
        {"": {"office_id": office_id, "status": {"": active_statuses}}},
        {"": {"path": "", "preserveNullAndEmptyArrays": False}},
        {"": {"deadlines.status": {"": "completed"}}},
        {"": {
            "_id": 0,
            "case_id": 1,
            "client_name": 1,
            "visa_type": 1,
            "deadline_title": ".title",
            "due_date": ".due_date",
        }},
        {"": {"due_date": 1}},
        {"": 20},
    ]
    upcoming_deadlines = await db.b2b_cases.aggregate(deadline_pipeline).to_list(length=20)

    # Idle cases (14+ days no update)
    idle_cutoff = now - timedelta(days=14)
    idle = await db.b2b_cases.count_documents(
        {"office_id": office_id, "status": {"": active_statuses}, "updated_at": {"": idle_cutoff}}
    )

    # Approval rate
    decided = approved + denied
    approval_rate = round((approved / decided) * 100, 1) if decided > 0 else None

    return {
        "total_cases": total,
        "active_cases": active,
        "approved": approved,
        "denied": denied,
        "approval_rate_pct": approval_rate,
        "idle_cases_14d": idle,
        "by_status": by_status,
        "by_visa_type": by_visa,
        "upcoming_deadlines": upcoming_deadlines,
    }


@router.get("/pipeline")
async def firm_pipeline(current_user=Depends(get_b2b_user)):
    """Case pipeline: count at each stage, avg days per stage."""
    office_id = current_user["office_id"]

    stages = [
        "intake", "docs_pending", "docs_review", "forms_gen",
        "attorney_review", "ready_to_file", "filed",
        "rfe_received", "rfe_response", "approved", "denied",
    ]

    pipeline_data = []
    for stage in stages:
        count = await db.b2b_cases.count_documents(
            {"office_id": office_id, "status": stage}
        )
        pipeline_data.append({"stage": stage, "count": count})

    return {"pipeline": pipeline_data}


@router.get("/activity")
async def firm_activity(
    days: int = Query(30, ge=1, le=365),
    current_user=Depends(get_b2b_user),
):
    """Recent activity: cases created and updated in the last N days."""
    office_id = current_user["office_id"]
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    created = await db.b2b_cases.count_documents(
        {"office_id": office_id, "created_at": {"": cutoff}}
    )
    updated = await db.b2b_cases.count_documents(
        {"office_id": office_id, "updated_at": {"": cutoff}}
    )

    # Recent documents
    docs_received = await db.document_uploads.count_documents(
        {"office_id": office_id, "created_at": {"": cutoff}}
    )

    # Recent reminders sent
    reminders_sent = await db.reminders.count_documents(
        {"office_id": office_id, "status": "sent", "sent_at": {"": cutoff}}
    ) if await db.list_collection_names() and "reminders" in await db.list_collection_names() else 0

    return {
        "period_days": days,
        "cases_created": created,
        "cases_updated": updated,
        "documents_received": docs_received,
        "reminders_sent": reminders_sent,
    }


@router.get("/dashboard", response_class=HTMLResponse)
async def firm_dashboard(current_user=Depends(get_b2b_user)):
    """Visual HTML dashboard for the entire firm."""
    office_id = current_user["office_id"]
    now = datetime.now(timezone.utc)

    active_statuses = [
        "intake", "docs_pending", "docs_review", "forms_gen",
        "attorney_review", "ready_to_file", "filed",
        "rfe_received", "rfe_response",
    ]

    total = await db.b2b_cases.count_documents({"office_id": office_id})
    active = await db.b2b_cases.count_documents(
        {"office_id": office_id, "status": {"": active_statuses}}
    )
    approved = await db.b2b_cases.count_documents(
        {"office_id": office_id, "status": "approved"}
    )
    denied = await db.b2b_cases.count_documents(
        {"office_id": office_id, "status": "denied"}
    )

    idle_cutoff = now - timedelta(days=14)
    idle = await db.b2b_cases.count_documents(
        {"office_id": office_id, "status": {"": active_statuses}, "updated_at": {"": idle_cutoff}}
    )

    decided = approved + denied
    approval_rate = round((approved / decided) * 100, 1) if decided > 0 else 0

    # Pipeline counts
    stages = ["intake", "docs_pending", "docs_review", "forms_gen",
              "attorney_review", "ready_to_file", "filed", "rfe_received"]
    bars = ""
    for s in stages:
        c = await db.b2b_cases.count_documents({"office_id": office_id, "status": s})
        label = s.replace("_", " ").title()
        bars += f'<div class="bar-row"><span class="bar-label">{label}</span><div class="bar" style="width:{max(c * 40, 4)}px"></div><span class="bar-val">{c}</span></div>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Firm Dashboard — Osprey</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f1f5f9;color:#1e293b;padding:2rem}}
.container{{max-width:1000px;margin:0 auto}}
h1{{font-size:1.5rem;margin-bottom:1.5rem}}
.kpi-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:1rem;margin-bottom:1.5rem}}
.kpi{{background:#fff;border-radius:12px;padding:1.25rem;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,.08)}}
.kpi .num{{font-size:2rem;font-weight:700}}
.kpi .lbl{{font-size:.8rem;color:#64748b;margin-top:.25rem;text-transform:uppercase}}
.kpi.warn .num{{color:#ef4444}}
.card{{background:#fff;border-radius:12px;padding:1.5rem;margin-bottom:1rem;box-shadow:0 1px 3px rgba(0,0,0,.08)}}
.card h2{{font-size:1.1rem;margin-bottom:1rem;color:#334155}}
.bar-row{{display:flex;align-items:center;margin-bottom:.5rem}}
.bar-label{{width:140px;font-size:.85rem;color:#64748b}}
.bar{{height:20px;background:#6366f1;border-radius:4px;min-width:4px}}
.bar-val{{margin-left:.5rem;font-weight:600;font-size:.85rem}}
.footer{{text-align:center;color:#94a3b8;font-size:.8rem;margin-top:2rem}}
</style>
</head>
<body>
<div class="container">
<h1>Firm Dashboard</h1>
<div class="kpi-grid">
<div class="kpi"><div class="num">{total}</div><div class="lbl">Total Cases</div></div>
<div class="kpi"><div class="num">{active}</div><div class="lbl">Active</div></div>
<div class="kpi"><div class="num">{approved}</div><div class="lbl">Approved</div></div>
<div class="kpi"><div class="num">{denied}</div><div class="lbl">Denied</div></div>
<div class="kpi"><div class="num">{approval_rate}%</div><div class="lbl">Approval Rate</div></div>
<div class="kpi {'warn' if idle > 0 else ''}"><div class="num">{idle}</div><div class="lbl">Idle (14+ days)</div></div>
</div>
<div class="card">
<h2>Case Pipeline</h2>
{bars}
</div>
<div class="footer">Osprey Immigration Platform &bull; Generated {now.strftime('%B %d, %Y %H:%M UTC')}</div>
</div>
</body>
</html>"""
