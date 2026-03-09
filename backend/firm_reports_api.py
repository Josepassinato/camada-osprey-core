"""
Firm Reports API — Relatórios visuais do escritório inteiro.
Gera HTML com lista filtrada de casos e retorna link temporário.
"""

from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
import uuid
import os

router = APIRouter(prefix="/api/firm-reports", tags=["firm-reports"])

INTERNAL_TOKEN = os.getenv("BACKEND_INTERNAL_TOKEN", "imigrai-internal-2024")
REPORTS_DIR = "/var/www/visa-application/reports"
BASE_URL = os.getenv("BASE_URL", "https://app.imigrai.app")

os.makedirs(REPORTS_DIR, exist_ok=True)

db = None

def init_db(database):
    global db
    db = database


class FirmReportRequest(BaseModel):
    office_id: str
    filter_type: str          # all_active, rfe_pending, deadlines_week, etc.
    filter_value: Optional[str] = None   # para filtros como visa_type, assignee
    expires_in_hours: int = 24
    title: Optional[str] = None


FILTER_CONFIGS = {
    "all_active": {
        "title": "All Active Cases",
        "icon": "⚡",
        "query": lambda now: {"status": {"$in": ["active", "pending_docs", "ready_to_file", "filed"]}}
    },
    "rfe_pending": {
        "title": "RFE — Request for Evidence",
        "icon": "📬",
        "query": lambda now: {"$or": [
            {"status": "rfe_pending"},
            {"tags": "rfe"},
            {"notes.content": {"$regex": "RFE", "$options": "i"}}
        ]}
    },
    "deadlines_week": {
        "title": "Deadlines This Week",
        "icon": "🗓",
        "query": lambda now: {
            "status": {"$nin": ["closed", "approved"]},
            "deadline": {
                "$gte": now.strftime("%Y-%m-%d"),
                "$lte": (now + timedelta(days=7)).strftime("%Y-%m-%d")
            }
        }
    },
    "deadlines_month": {
        "title": "Deadlines This Month",
        "icon": "📅",
        "query": lambda now: {
            "status": {"$nin": ["closed", "approved"]},
            "deadline": {
                "$gte": now.strftime("%Y-%m-%d"),
                "$lte": (now + timedelta(days=30)).strftime("%Y-%m-%d")
            }
        }
    },
    "ready_to_file": {
        "title": "Ready to File",
        "icon": "✅",
        "query": lambda now: {"status": "ready_to_file"}
    },
    "missing_docs": {
        "title": "Cases with Missing Documents",
        "icon": "📋",
        "query": lambda now: {
            "status": {"$in": ["active", "pending_docs"]},
            "$expr": {"$gt": [
                {"$size": {"$ifNull": ["$documents_required", []]}},
                {"$size": {"$ifNull": ["$documents_received", []]}}
            ]}
        }
    },
    "by_visa_type": {
        "title": "Cases by Visa Type",
        "icon": "🗂",
        "query": lambda now: {}  # override com filter_value
    },
    "by_assignee": {
        "title": "Cases by Team Member",
        "icon": "👤",
        "query": lambda now: {}  # override com filter_value
    },
    "approved_period": {
        "title": "Approved This Month",
        "icon": "🎉",
        "query": lambda now: {
            "status": "approved",
            "updated_at": {"$gte": now.replace(day=1)}
        }
    },
    "idle_cases": {
        "title": "Idle Cases — No Activity in 14+ Days",
        "icon": "💤",
        "query": lambda now: {
            "status": {"$in": ["active", "pending_docs"]},
            "updated_at": {"$lte": now - timedelta(days=14)}
        }
    },
    "firm_overview": {
        "title": "Firm Overview — Full Pipeline",
        "icon": "🏛",
        "query": lambda now: {"status": {"$nin": ["closed"]}}
    },
}


@router.post("/generate")
async def generate_firm_report(
    req: FirmReportRequest,
    x_internal_token: str = Header(None)
):
    if x_internal_token != INTERNAL_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

    now = datetime.utcnow()
    config = FILTER_CONFIGS.get(req.filter_type)
    if not config:
        raise HTTPException(status_code=400, detail=f"Unknown filter: {req.filter_type}")

    # Montar query
    base_query = {"office_id": req.office_id}
    filter_query = config["query"](now)

    # Filtros especiais com valor
    if req.filter_type == "by_visa_type" and req.filter_value:
        filter_query = {"visa_type": {"$regex": req.filter_value, "$options": "i"},
                        "status": {"$nin": ["closed"]}}
        config = {**config, "title": f"Cases — {req.filter_value}"}

    if req.filter_type == "by_assignee" and req.filter_value:
        filter_query = {"assigned_to": {"$regex": req.filter_value, "$options": "i"},
                        "status": {"$nin": ["closed"]}}
        config = {**config, "title": f"Cases — {req.filter_value}"}

    full_query = {**base_query, **filter_query}

    # Buscar casos
    cases = await db.cases.find(full_query).sort("deadline", 1).to_list(length=200)

    # Buscar escritório
    office = await db.offices.find_one({"office_id": req.office_id})
    firm_name = office.get("name", "Immigration Law Firm") if office else "Law Firm"

    # Stats agregadas
    total = len(cases)
    by_status = {}
    by_visa = {}
    urgent_count = 0

    for c in cases:
        s = c.get("status", "unknown")
        by_status[s] = by_status.get(s, 0) + 1
        v = c.get("visa_type", "Other")
        by_visa[v] = by_visa.get(v, 0) + 1
        dl = c.get("deadline")
        if dl:
            try:
                dl_date = datetime.fromisoformat(dl) if isinstance(dl, str) else dl
                if 0 <= (dl_date - now).days <= 7:
                    urgent_count += 1
            except:
                pass

    # Gerar HTML
    report_id = str(uuid.uuid4())[:12]
    expires_at = now + timedelta(hours=req.expires_in_hours)
    title = req.title or config["title"]

    html = build_firm_report_html(
        cases=cases,
        firm_name=firm_name,
        title=title,
        icon=config["icon"],
        filter_type=req.filter_type,
        total=total,
        by_status=by_status,
        by_visa=by_visa,
        urgent_count=urgent_count,
        report_id=report_id,
        expires_at=expires_at,
        generated_at=now
    )

    filepath = os.path.join(REPORTS_DIR, f"{report_id}.html")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    await db.reports.insert_one({
        "report_id": report_id,
        "report_type": "firm",
        "filter_type": req.filter_type,
        "office_id": req.office_id,
        "filepath": filepath,
        "expires_at": expires_at,
        "created_at": now,
        "total_cases": total
    })

    return {
        "success": True,
        "report_id": report_id,
        "report_url": f"{BASE_URL}/reports/{report_id}",
        "title": title,
        "total_cases": total,
        "urgent_cases": urgent_count,
        "expires_at": expires_at.isoformat()
    }


@router.get("/{report_id}", response_class=HTMLResponse)
async def serve_firm_report(report_id: str):
    filepath = os.path.join(REPORTS_DIR, f"{report_id}.html")
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Report not found or expired")

    report_meta = await db.reports.find_one({"report_id": report_id})
    if report_meta:
        expires_at = report_meta.get("expires_at")
        if expires_at and datetime.utcnow() > expires_at:
            os.remove(filepath)
            raise HTTPException(status_code=410, detail="Report expired")

    with open(filepath, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


def build_firm_report_html(cases, firm_name, title, icon, filter_type,
                            total, by_status, by_visa, urgent_count,
                            report_id, expires_at, generated_at):

    STATUS_CONFIG = {
        "active":         {"label": "Active",           "color": "#3B82F6", "bg": "rgba(59,130,246,0.1)"},
        "pending_docs":   {"label": "Pending Docs",     "color": "#F59E0B", "bg": "rgba(245,158,11,0.1)"},
        "ready_to_file":  {"label": "Ready to File",    "color": "#10B981", "bg": "rgba(16,185,129,0.1)"},
        "filed":          {"label": "Filed",             "color": "#8B5CF6", "bg": "rgba(139,92,246,0.1)"},
        "rfe_pending":    {"label": "RFE Pending",       "color": "#EF4444", "bg": "rgba(239,68,68,0.1)"},
        "approved":       {"label": "Approved",          "color": "#10B981", "bg": "rgba(16,185,129,0.1)"},
        "closed":         {"label": "Closed",            "color": "#6B7280", "bg": "rgba(107,114,128,0.1)"},
    }

    now = datetime.utcnow()

    # Stats bar HTML
    stats_html = ""
    for status, count in sorted(by_status.items(), key=lambda x: -x[1]):
        cfg = STATUS_CONFIG.get(status, {"label": status, "color": "#6B7280", "bg": "rgba(107,114,128,0.1)"})
        pct = int(count / total * 100) if total > 0 else 0
        stats_html += f"""
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">
          <div style="width:110px;font-size:11px;color:#6B7280;text-align:right;flex-shrink:0;">{cfg['label']}</div>
          <div style="flex:1;height:6px;background:rgba(255,255,255,0.05);border-radius:3px;overflow:hidden;">
            <div style="height:100%;width:{pct}%;background:{cfg['color']};border-radius:3px;"></div>
          </div>
          <div style="width:30px;font-size:12px;font-weight:600;color:{cfg['color']};">{count}</div>
        </div>"""

    # Visa breakdown
    visa_html = ""
    for vtype, count in sorted(by_visa.items(), key=lambda x: -x[1])[:8]:
        visa_html += f"""
        <div style="display:flex;justify-content:space-between;align-items:center;
                    padding:7px 0;border-bottom:1px solid rgba(255,255,255,0.04);">
          <span style="font-size:13px;color:#9CA3AF;">{vtype}</span>
          <span style="font-size:13px;font-weight:600;color:#C9A84C;">{count}</span>
        </div>"""

    # Cases table HTML
    cases_html = ""
    for i, c in enumerate(cases):
        client = c.get("client_name", "Unknown")
        case_id = c.get("case_id", "")
        visa = c.get("visa_type", "—")
        status = c.get("status", "active")
        assigned = c.get("assigned_to", "—") or "—"
        deadline = c.get("deadline", "")
        notes_count = len(c.get("notes", []))
        docs_req = len(c.get("documents_required", []))
        docs_rec = len(c.get("documents_received", []))
        docs_pct = int(docs_rec / docs_req * 100) if docs_req > 0 else 0

        # Deadline urgency
        dl_str = ""
        dl_color = "#4B5563"
        dl_icon = ""
        if deadline:
            try:
                dl_date = datetime.fromisoformat(deadline) if isinstance(deadline, str) else deadline
                days = (dl_date - now).days
                dl_str = dl_date.strftime("%b %d")
                if days < 0:
                    dl_color = "#EF4444"
                    dl_icon = "🚨"
                    dl_str = f"OVERDUE {dl_str}"
                elif days <= 7:
                    dl_color = "#F59E0B"
                    dl_icon = "⚠️"
                    dl_str = f"{dl_str} ({days}d)"
                elif days <= 14:
                    dl_color = "#FBBF24"
                    dl_str = f"{dl_str} ({days}d)"
                    dl_icon = "📅"
                else:
                    dl_color = "#6B7280"
                    dl_str = f"{dl_str} ({days}d)"
            except:
                dl_str = str(deadline)[:10]

        status_cfg = STATUS_CONFIG.get(status, {"label": status, "color": "#6B7280", "bg": "rgba(107,114,128,0.1)"})

        # Flags especiais
        flags = ""
        if status == "rfe_pending":
            flags += '<span style="font-size:10px;padding:2px 8px;border-radius:10px;background:rgba(239,68,68,0.15);color:#EF4444;font-weight:700;margin-left:6px;">RFE</span>'
        if docs_pct == 100:
            flags += '<span style="font-size:10px;padding:2px 8px;border-radius:10px;background:rgba(16,185,129,0.12);color:#10B981;font-weight:700;margin-left:6px;">DOCS ✓</span>'
        elif docs_pct < 50 and status in ["active", "pending_docs"]:
            flags += '<span style="font-size:10px;padding:2px 8px;border-radius:10px;background:rgba(245,158,11,0.12);color:#F59E0B;font-weight:700;margin-left:6px;">DOCS MISSING</span>'

        row_bg = "rgba(255,255,255,0.015)" if i % 2 == 0 else "transparent"

        cases_html += f"""
        <div style="display:grid;grid-template-columns:1fr auto;align-items:center;
                    padding:14px 18px;background:{row_bg};
                    border-bottom:1px solid rgba(255,255,255,0.04);">
          <div>
            <div style="display:flex;align-items:center;flex-wrap:wrap;gap:6px;margin-bottom:5px;">
              <span style="font-size:15px;font-weight:600;color:#F3F4F6;">{client}</span>
              <span style="font-size:10px;color:#4B5563;font-family:monospace;">{case_id}</span>
              {flags}
            </div>
            <div style="display:flex;flex-wrap:wrap;gap:10px;align-items:center;">
              <span style="font-size:11px;font-weight:700;letter-spacing:0.06em;
                           padding:2px 8px;border-radius:10px;
                           background:{status_cfg['bg']};color:{status_cfg['color']};">
                {status_cfg['label']}
              </span>
              <span style="font-size:11px;color:#6B7280;">📁 {visa}</span>
              <span style="font-size:11px;color:#6B7280;">👤 {assigned}</span>
              <span style="font-size:11px;color:#6B7280;">📝 {notes_count} notes</span>
            </div>
            <div style="margin-top:8px;display:flex;align-items:center;gap:8px;">
              <div style="flex:1;max-width:120px;height:4px;background:rgba(255,255,255,0.06);border-radius:2px;overflow:hidden;">
                <div style="height:100%;width:{docs_pct}%;background:{'#10B981' if docs_pct==100 else '#C9A84C'};border-radius:2px;"></div>
              </div>
              <span style="font-size:10px;color:#4B5563;">{docs_rec}/{docs_req} docs</span>
            </div>
          </div>
          <div style="text-align:right;padding-left:16px;">
            {f'<div style="font-size:13px;font-weight:600;color:{dl_color};">{dl_icon} {dl_str}</div>' if dl_str else '<div style="font-size:12px;color:#374151;">No deadline</div>'}
          </div>
        </div>"""

    if not cases_html:
        cases_html = """
        <div style="padding:48px;text-align:center;color:#374151;">
          <div style="font-size:32px;margin-bottom:12px;">🔍</div>
          <p style="font-size:14px;">No cases found for this filter.</p>
        </div>"""

    expires_str = expires_at.strftime("%b %d, %Y at %I:%M %p UTC")
    generated_str = generated_at.strftime("%B %d, %Y at %I:%M %p UTC")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title} | Imigrai</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;700&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
  *{{box-sizing:border-box;margin:0;padding:0;}}
  body{{font-family:'DM Sans',sans-serif;background:#080809;color:#E5E7EB;min-height:100vh;}}
  .grain{{position:fixed;inset:0;pointer-events:none;z-index:0;opacity:0.3;
    background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.05'/%3E%3C/svg%3E");}}
  .wrap{{max-width:860px;margin:0 auto;padding:36px 20px 80px;position:relative;z-index:1;}}
  .brand{{display:flex;align-items:center;gap:10px;margin-bottom:28px;}}
  .brand-icon{{width:30px;height:30px;background:linear-gradient(135deg,#C9A84C,#E8C76A);
    border-radius:7px;display:flex;align-items:center;justify-content:center;font-size:14px;}}
  .brand-name{{font-family:'Playfair Display',serif;font-size:16px;font-weight:700;color:#C9A84C;}}
  h1{{font-family:'Playfair Display',serif;font-size:30px;font-weight:700;color:#F9FAFB;
    margin-bottom:6px;line-height:1.2;}}
  .subtitle{{font-size:13px;color:#4B5563;margin-bottom:32px;}}
  .grid{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px;margin-bottom:28px;}}
  @media(max-width:600px){{.grid{{grid-template-columns:1fr 1fr;}}}}
  .stat-card{{background:linear-gradient(160deg,#111113,#0D0D10);
    border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:18px 20px;}}
  .stat-label{{font-size:10px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;
    color:#4B5563;margin-bottom:6px;}}
  .stat-val{{font-size:30px;font-weight:700;color:#F9FAFB;font-family:'Playfair Display',serif;}}
  .stat-sub{{font-size:11px;color:#6B7280;margin-top:3px;}}
  .panel{{background:linear-gradient(160deg,#111113,#0D0D10);
    border:1px solid rgba(255,255,255,0.07);border-radius:14px;
    overflow:hidden;margin-bottom:20px;}}
  .panel-header{{padding:16px 20px;border-bottom:1px solid rgba(255,255,255,0.06);
    display:flex;justify-content:space-between;align-items:center;}}
  .panel-title{{font-size:13px;font-weight:600;color:#D1D5DB;letter-spacing:0.02em;}}
  .panel-count{{font-size:11px;color:#6B7280;}}
  .footer{{margin-top:40px;text-align:center;}}
  .footer p{{font-size:11px;color:#374151;line-height:1.9;}}
  @keyframes fadeUp{{from{{opacity:0;transform:translateY(12px)}}to{{opacity:1;transform:translateY(0)}}}}
  .stat-card,.panel{{animation:fadeUp 0.4s ease both;}}
  .stat-card:nth-child(2){{animation-delay:.05s;}}
  .stat-card:nth-child(3){{animation-delay:.1s;}}
  .panel:nth-child(2){{animation-delay:.05s;}}
  .panel:nth-child(3){{animation-delay:.1s;}}
</style>
</head>
<body>
<div class="grain"></div>
<div class="wrap">

  <div class="brand">
    <div class="brand-icon">⚖️</div>
    <span class="brand-name">Imigrai</span>
    <span style="color:#374151;font-size:12px;margin-left:4px;">/ {firm_name}</span>
  </div>

  <h1>{icon} {title}</h1>
  <p class="subtitle">Generated {generated_str} · Link expires {expires_str}</p>

  <!-- Stats -->
  <div class="grid">
    <div class="stat-card">
      <div class="stat-label">Total Cases</div>
      <div class="stat-val">{total}</div>
      <div class="stat-sub">in this report</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Urgent Deadlines</div>
      <div class="stat-val" style="color:{'#EF4444' if urgent_count > 0 else '#10B981'};">{urgent_count}</div>
      <div class="stat-sub">within 7 days</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Visa Types</div>
      <div class="stat-val">{len(by_visa)}</div>
      <div class="stat-sub">in this filter</div>
    </div>
  </div>

  <!-- Status breakdown -->
  <div class="panel" style="margin-bottom:20px;">
    <div class="panel-header">
      <span class="panel-title">Status Breakdown</span>
    </div>
    <div style="padding:18px 20px;">
      {stats_html}
    </div>
  </div>

  <!-- Visa breakdown -->
  <div class="panel" style="margin-bottom:20px;">
    <div class="panel-header">
      <span class="panel-title">By Visa Type</span>
    </div>
    <div style="padding:4px 20px 12px;">
      {visa_html}
    </div>
  </div>

  <!-- Cases list -->
  <div class="panel">
    <div class="panel-header">
      <span class="panel-title">Cases</span>
      <span class="panel-count">{total} records · sorted by deadline</span>
    </div>
    {cases_html}
  </div>

  <div class="footer">
    <p>Generated by <strong style="color:#C9A84C;">Imigrai Chief of Staff</strong> for <strong style="color:#C9A84C;">{firm_name}</strong></p>
    <p>Report ID: {report_id} · This report is confidential</p>
  </div>

</div>
</body>
</html>"""
