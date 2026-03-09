"""
Reports API — Individual case report generation.
Generates visual HTML reports for a single immigration case.
"""

import os
import json
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse

from backend.core.database import db
from backend.b2b_auth_api import get_b2b_user

router = APIRouter(prefix="/api/reports", tags=["reports"])

REPORTS_DIR = "/var/www/visa-application/reports"
os.makedirs(REPORTS_DIR, exist_ok=True)


def _status_color(status: str) -> str:
    colors = {
        "intake": "#6366f1",
        "docs_pending": "#f59e0b",
        "docs_review": "#3b82f6",
        "forms_gen": "#8b5cf6",
        "attorney_review": "#ec4899",
        "ready_to_file": "#10b981",
        "filed": "#06b6d4",
        "rfe_received": "#ef4444",
        "rfe_response": "#f97316",
        "approved": "#22c55e",
        "denied": "#dc2626",
        "withdrawn": "#6b7280",
    }
    return colors.get(status, "#6b7280")


def _status_label(status: str) -> str:
    labels = {
        "intake": "Intake",
        "docs_pending": "Documents Pending",
        "docs_review": "Documents Review",
        "forms_gen": "Forms Generation",
        "attorney_review": "Attorney Review",
        "ready_to_file": "Ready to File",
        "filed": "Filed with USCIS",
        "rfe_received": "RFE Received",
        "rfe_response": "RFE Response",
        "approved": "Approved",
        "denied": "Denied",
        "withdrawn": "Withdrawn",
    }
    return labels.get(status, status.replace("_", " ").title())


def _render_case_report(case: dict) -> str:
    now = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")
    status = case.get("status", "unknown")
    color = _status_color(status)
    label = _status_label(status)

    # Documents section
    docs = case.get("documents", [])
    docs_html = ""
    for d in docs:
        icon = "✅" if d.get("status") == "verified" else "⏳" if d.get("status") == "pending" else "❌"
        docs_html += f"<tr><td>{icon}</td><td>{d.get('type', 'N/A')}</td><td>{d.get('status', 'N/A')}</td><td>{d.get('uploaded_at', 'N/A')[:10] if d.get('uploaded_at') else '-'}</td></tr>"
    if not docs:
        docs_html = "<tr><td colspan='4' style='text-align:center;color:#999'>No documents uploaded yet</td></tr>"

    # Deadlines section
    deadlines = case.get("deadlines", [])
    deadlines_html = ""
    for dl in deadlines:
        due = dl.get("due_date", "N/A")
        if isinstance(due, str) and len(due) > 10:
            due = due[:10]
        deadlines_html += f"<tr><td>{dl.get('title', 'N/A')}</td><td>{due}</td><td>{dl.get('status', 'pending')}</td></tr>"
    if not deadlines:
        deadlines_html = "<tr><td colspan='3' style='text-align:center;color:#999'>No deadlines set</td></tr>"

    # Notes section
    notes = case.get("notes", [])
    notes_html = ""
    for n in notes[-10:]:
        ts = n.get("created_at", "")
        if isinstance(ts, str) and len(ts) > 10:
            ts = ts[:10]
        notes_html += f"<div class='note'><span class='note-date'>{ts}</span><p>{n.get('text', '')}</p></div>"
    if not notes:
        notes_html = "<p style='color:#999'>No notes yet</p>"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Case Report — {case.get('client_name', 'N/A')}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f8fafc;color:#1e293b;padding:2rem}}
.container{{max-width:900px;margin:0 auto}}
.header{{background:linear-gradient(135deg,#1e293b,#334155);color:#fff;padding:2rem;border-radius:12px;margin-bottom:1.5rem}}
.header h1{{font-size:1.5rem;margin-bottom:.5rem}}
.header .meta{{opacity:.8;font-size:.9rem}}
.badge{{display:inline-block;padding:.25rem .75rem;border-radius:999px;font-size:.8rem;font-weight:600;color:#fff;background:{color}}}
.card{{background:#fff;border-radius:12px;padding:1.5rem;margin-bottom:1rem;box-shadow:0 1px 3px rgba(0,0,0,.1)}}
.card h2{{font-size:1.1rem;margin-bottom:1rem;color:#334155;border-bottom:2px solid #e2e8f0;padding-bottom:.5rem}}
table{{width:100%;border-collapse:collapse}}
th,td{{text-align:left;padding:.5rem .75rem;border-bottom:1px solid #f1f5f9;font-size:.9rem}}
th{{color:#64748b;font-weight:600;font-size:.8rem;text-transform:uppercase}}
.info-grid{{display:grid;grid-template-columns:1fr 1fr;gap:1rem}}
.info-item label{{font-size:.75rem;color:#64748b;text-transform:uppercase;font-weight:600}}
.info-item p{{font-size:1rem;margin-top:.25rem}}
.note{{border-left:3px solid #e2e8f0;padding:.5rem 1rem;margin-bottom:.75rem}}
.note-date{{font-size:.75rem;color:#94a3b8}}
.footer{{text-align:center;color:#94a3b8;font-size:.8rem;margin-top:2rem}}
@media print{{body{{padding:.5rem}}.container{{max-width:100%}}}}
</style>
</head>
<body>
<div class="container">
<div class="header">
<h1>{case.get('client_name', 'N/A')}</h1>
<div class="meta">Case ID: {case.get('case_id', 'N/A')} &bull; Generated: {now}</div>
</div>

<div class="card">
<h2>Case Information</h2>
<div class="info-grid">
<div class="info-item"><label>Visa Type</label><p>{case.get('visa_type', 'N/A')}</p></div>
<div class="info-item"><label>Status</label><p><span class="badge">{label}</span></p></div>
<div class="info-item"><label>Created</label><p>{str(case.get('created_at', 'N/A'))[:10]}</p></div>
<div class="info-item"><label>Last Updated</label><p>{str(case.get('updated_at', 'N/A'))[:10]}</p></div>
<div class="info-item"><label>Priority</label><p>{case.get('priority', 'normal').title()}</p></div>
<div class="info-item"><label>Assigned Attorney</label><p>{case.get('attorney', 'Unassigned')}</p></div>
</div>
</div>

<div class="card">
<h2>Documents ({len(docs)})</h2>
<table><thead><tr><th></th><th>Type</th><th>Status</th><th>Date</th></tr></thead>
<tbody>{docs_html}</tbody></table>
</div>

<div class="card">
<h2>Deadlines ({len(deadlines)})</h2>
<table><thead><tr><th>Title</th><th>Due Date</th><th>Status</th></tr></thead>
<tbody>{deadlines_html}</tbody></table>
</div>

<div class="card">
<h2>Notes ({len(notes)})</h2>
{notes_html}
</div>

<div class="footer">Osprey Immigration Platform &bull; Confidential</div>
</div>
</body>
</html>"""


@router.get("/case/{case_id}")
async def get_case_report(case_id: str, current_user=Depends(get_b2b_user)):
    """Generate a visual HTML report for a single case."""
    office_id = current_user["office_id"]
    case = await db.b2b_cases.find_one(
        {"case_id": case_id, "office_id": office_id},
        {"_id": 0},
    )
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    html = _render_case_report(case)

    # Save to reports dir
    filename = f"{case_id}_{datetime.now(timezone.utc).strftime('%Y%m%d')}.html"
    filepath = os.path.join(REPORTS_DIR, filename)
    with open(filepath, "w") as f:
        f.write(html)

    return HTMLResponse(content=html)


@router.get("/case/{case_id}/json")
async def get_case_report_json(case_id: str, current_user=Depends(get_b2b_user)):
    """Get case data as JSON for custom report rendering."""
    office_id = current_user["office_id"]
    case = await db.b2b_cases.find_one(
        {"case_id": case_id, "office_id": office_id},
        {"_id": 0},
    )
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    return case
