"""
Email Service — Imigrai
Async email sending via Resend API (httpx).
Templates: custom, daily_summary, deadline_alert, package_ready.
"""

import logging
import os
from datetime import datetime, timezone
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "Imigrai <noreply@iaimmigration.com>")
RESEND_API_URL = "https://api.resend.com/emails"


def _base_html(title: str, body: str) -> str:
    """Wrap content in a clean HTML email template."""
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f4f4f7; margin: 0; padding: 0; }}
.container {{ max-width: 600px; margin: 0 auto; background: #fff; border-radius: 8px; overflow: hidden; margin-top: 24px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
.header {{ background: #1a365d; padding: 24px 32px; }}
.header h1 {{ color: #fff; margin: 0; font-size: 20px; font-weight: 600; }}
.body {{ padding: 32px; color: #333; line-height: 1.6; }}
.body h2 {{ color: #1a365d; font-size: 18px; margin-top: 24px; }}
.body p {{ margin: 12px 0; }}
.badge {{ display: inline-block; padding: 4px 10px; border-radius: 4px; font-size: 12px; font-weight: 600; }}
.badge-urgent {{ background: #fed7d7; color: #c53030; }}
.badge-warning {{ background: #fefcbf; color: #b7791f; }}
.badge-ok {{ background: #c6f6d5; color: #276749; }}
table {{ width: 100%; border-collapse: collapse; margin: 16px 0; }}
th {{ background: #f7fafc; text-align: left; padding: 8px 12px; border-bottom: 2px solid #e2e8f0; font-size: 13px; color: #4a5568; }}
td {{ padding: 8px 12px; border-bottom: 1px solid #e2e8f0; font-size: 14px; }}
.footer {{ background: #f7fafc; padding: 16px 32px; text-align: center; font-size: 12px; color: #a0aec0; }}
</style>
</head>
<body>
<div class="container">
  <div class="header"><h1>{title}</h1></div>
  <div class="body">{body}</div>
  <div class="footer">Imigrai — Immigration Case Management<br>This is an automated message.</div>
</div>
</body>
</html>"""


async def send_email(
    to: str | list[str],
    subject: str,
    html: str,
    reply_to: Optional[str] = None,
) -> dict:
    """Send an email via Resend API. Returns {"success": True, "id": ...} or {"success": False, "error": ...}."""
    if not RESEND_API_KEY:
        logger.warning("RESEND_API_KEY not configured — email not sent")
        return {"success": False, "error": "RESEND_API_KEY not configured"}

    recipients = [to] if isinstance(to, str) else to

    payload = {
        "from": SENDER_EMAIL,
        "to": recipients,
        "subject": subject,
        "html": html,
    }
    if reply_to:
        payload["reply_to"] = reply_to

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                RESEND_API_URL,
                json=payload,
                headers={
                    "Authorization": f"Bearer {RESEND_API_KEY}",
                    "Content-Type": "application/json",
                },
            )

        if resp.status_code in (200, 201):
            data = resp.json()
            logger.info(f"Email sent to {recipients}: {data.get('id')}")
            return {"success": True, "id": data.get("id")}
        else:
            error = resp.text
            logger.error(f"Resend API error {resp.status_code}: {error}")
            return {"success": False, "error": f"Resend {resp.status_code}: {error}"}

    except Exception as e:
        logger.error(f"Email send error: {e}")
        return {"success": False, "error": str(e)}


async def send_custom_email(
    to: str | list[str],
    subject: str,
    message: str,
    reply_to: Optional[str] = None,
) -> dict:
    """Send a custom text email wrapped in the HTML template."""
    paragraphs = "".join(f"<p>{line}</p>" for line in message.split("\n") if line.strip())
    html = _base_html(subject, paragraphs)
    return await send_email(to, subject, html, reply_to=reply_to)


async def send_daily_summary(
    to: str | list[str],
    office_name: str,
    stats: dict,
    deadlines: list,
    idle_cases: list,
) -> dict:
    """Send the daily firm summary email."""
    today = datetime.now(timezone.utc).strftime("%B %d, %Y")

    # Stats section
    body = f"<h2>Daily Summary — {today}</h2>"
    body += f"<p><strong>{office_name}</strong></p>"
    body += "<table>"
    body += f"<tr><td>Active cases</td><td><strong>{stats.get('active', 0)}</strong></td></tr>"
    body += f"<tr><td>Pending review</td><td><strong>{stats.get('pending_review', 0)}</strong></td></tr>"
    body += f"<tr><td>Ready to file</td><td><strong>{stats.get('ready_to_file', 0)}</strong></td></tr>"
    body += f"<tr><td>RFE pending</td><td><strong>{stats.get('rfe_pending', 0)}</strong></td></tr>"
    body += "</table>"

    # Deadlines
    if deadlines:
        body += "<h2>Upcoming Deadlines (7 days)</h2><table>"
        body += "<tr><th>Client</th><th>Visa</th><th>Deadline</th><th>Date</th></tr>"
        for d in deadlines[:10]:
            dt = str(d.get("deadline_date", ""))[:10]
            body += (
                f"<tr><td>{d.get('client_name', '?')}</td>"
                f"<td>{d.get('visa_type', '?')}</td>"
                f"<td>{d.get('deadline_title', '?')}</td>"
                f"<td>{dt}</td></tr>"
            )
        body += "</table>"
    else:
        body += "<p>No upcoming deadlines in the next 7 days.</p>"

    # Idle cases
    if idle_cases:
        body += "<h2>Idle Cases (14+ days)</h2><table>"
        body += "<tr><th>Client</th><th>Visa</th><th>Last Update</th></tr>"
        for c in idle_cases[:10]:
            updated = str(c.get("updated_at", ""))[:10]
            body += (
                f"<tr><td>{c.get('client_name', '?')}</td>"
                f"<td>{c.get('visa_type', '?')}</td>"
                f"<td>{updated}</td></tr>"
            )
        body += "</table>"

    html = _base_html(f"Imigrai Daily Summary — {today}", body)
    return await send_email(to, f"Imigrai Daily Summary — {today}", html)


async def send_deadline_alert(
    to: str | list[str],
    client_name: str,
    visa_type: str,
    deadline_title: str,
    due_date: str,
    case_id: str,
) -> dict:
    """Send an urgent deadline alert email."""
    body = f"""
    <p><span class="badge badge-urgent">URGENT</span></p>
    <h2>Deadline Approaching</h2>
    <table>
    <tr><td>Client</td><td><strong>{client_name}</strong></td></tr>
    <tr><td>Case</td><td>{case_id}</td></tr>
    <tr><td>Visa</td><td>{visa_type}</td></tr>
    <tr><td>Deadline</td><td><strong>{deadline_title}</strong></td></tr>
    <tr><td>Due Date</td><td><strong>{due_date}</strong></td></tr>
    </table>
    <p>Please review this case and take action before the deadline.</p>
    """
    html = _base_html(f"Deadline Alert: {client_name} — {deadline_title}", body)
    return await send_email(to, f"⚠️ Deadline Alert: {client_name} — {deadline_title}", html)


async def send_package_ready(
    to: str | list[str],
    client_name: str,
    visa_type: str,
    case_id: str,
    package_id: str,
    files_count: int,
) -> dict:
    """Send notification that a filing package is ready."""
    body = f"""
    <p><span class="badge badge-ok">READY</span></p>
    <h2>Filing Package Generated</h2>
    <table>
    <tr><td>Client</td><td><strong>{client_name}</strong></td></tr>
    <tr><td>Case</td><td>{case_id}</td></tr>
    <tr><td>Visa</td><td>{visa_type}</td></tr>
    <tr><td>Package ID</td><td>{package_id}</td></tr>
    <tr><td>Files</td><td>{files_count} documents</td></tr>
    </table>
    <p>The filing package is ready for attorney review. Download it from the dashboard or request it via WhatsApp.</p>
    """
    html = _base_html(f"Package Ready: {client_name}", body)
    return await send_email(to, f"Filing Package Ready: {client_name} — {visa_type}", html)
