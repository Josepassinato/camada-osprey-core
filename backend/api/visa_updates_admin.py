import asyncio
import logging
import os
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request

from admin_security import AuditAction, log_admin_action, require_admin
from core.database import db, visa_scheduler
from core.serialization import serialize_doc
from visa_auto_updater import VisaAutoUpdater

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


@router.get("/admin/visa-updates/pending")
async def get_pending_visa_updates(skip: int = 0, limit: int = 20, admin=Depends(require_admin)):
    """Get all pending visa updates for admin review - PROTECTED."""
    try:
        cursor = db.visa_updates.find({"status": "pending"}).sort("created_at", -1).skip(skip).limit(limit)
        updates = await cursor.to_list(length=None)
        updates = serialize_doc(updates)

        total_count = await db.visa_updates.count_documents({"status": "pending"})

        return {
            "success": True,
            "updates": updates,
            "total_count": total_count,
            "has_more": (skip + limit) < total_count,
        }
    except Exception as e:
        logger.error(f"Error getting pending updates: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve pending updates")


@router.post("/admin/visa-updates/{update_id}/approve")
async def approve_visa_update(update_id: str, request: Request, admin=Depends(require_admin)):
    """Approve a pending visa update and apply it to production - PROTECTED."""
    try:
        body = await request.json()
        admin_notes = body.get("admin_notes", "")
        admin_user_param = body.get("admin_user", "system")

        admin_user = admin.get("email", admin_user_param)

        await log_admin_action(
            admin_user=admin,
            action=AuditAction.APPROVE_VISA_UPDATE,
            resource_type="visa_update",
            resource_id=update_id,
            details={"admin_notes": admin_notes},
            request=request,
            success=True,
        )

        update = await db.visa_updates.find_one({"id": update_id, "status": "pending"})
        if not update:
            raise HTTPException(status_code=404, detail="Update not found")

        visa_info = {
            "form_code": update["form_code"],
            "data_type": update["update_type"],
            "data": update["new_value"],
            "last_updated": datetime.now(timezone.utc),
            "updated_by": admin_user,
            "is_active": True,
        }

        await db.visa_information.update_one(
            {"form_code": update["form_code"], "data_type": update["update_type"]},
            {"$set": visa_info, "$inc": {"version": 1}},
            upsert=True,
        )

        await db.visa_updates.update_one(
            {"id": update_id},
            {
                "$set": {
                    "status": "approved",
                    "admin_notes": admin_notes,
                    "approved_by": admin_user,
                    "approved_date": datetime.now(timezone.utc),
                }
            },
        )

        logger.info(f"Visa update {update_id} approved by {admin_user}")

        return {"success": True, "message": "Update approved and applied"}

    except Exception as e:
        logger.error(f"Error approving update: {e}")
        raise HTTPException(status_code=500, detail="Failed to approve update")


@router.post("/admin/visa-updates/{update_id}/reject")
async def reject_visa_update(update_id: str, request: Request, admin=Depends(require_admin)):
    """Reject a pending visa update - PROTECTED."""
    try:
        body = await request.json()
        admin_notes = body.get("admin_notes", "")
        admin_user = body.get("admin_user", "system")

        result = await db.visa_updates.update_one(
            {"id": update_id, "status": "pending"},
            {
                "$set": {
                    "status": "rejected",
                    "admin_notes": admin_notes,
                    "approved_by": admin_user,
                    "approved_date": datetime.now(timezone.utc),
                }
            },
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Update not found")

        logger.info(f"Visa update {update_id} rejected by {admin_user}")

        return {"success": True, "message": "Update rejected"}

    except Exception as e:
        logger.error(f"Error rejecting update: {e}")
        raise HTTPException(status_code=500, detail="Failed to reject update")


@router.post("/admin/visa-updates/run-manual-scan")
async def run_manual_visa_scan(admin=Depends(require_admin)):
    """Manually trigger visa information scan - PROTECTED."""
    try:
        llm_key = os.environ.get("EMERGENT_LLM_KEY")

        if not llm_key:
            raise HTTPException(status_code=500, detail="EMERGENT_LLM_KEY not configured")

        updater = VisaAutoUpdater(db, llm_key)
        result = await updater.run_weekly_update()

        return {
            "success": result["success"],
            "message": "Manual visa scan completed",
            "changes_detected": result.get("changes_detected", 0),
        }

    except Exception as e:
        logger.error(f"Error running manual scan: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to run manual scan: {str(e)}")


@router.get("/admin/visa-updates/history")
async def get_visa_update_history(skip: int = 0, limit: int = 50, admin=Depends(require_admin)):
    """Get history of all visa updates - PROTECTED."""
    try:
        cursor = db.visa_updates.find({}).sort("created_at", -1).skip(skip).limit(limit)
        updates = await cursor.to_list(length=None)
        updates = serialize_doc(updates)

        total_count = await db.visa_updates.count_documents({})

        return {
            "success": True,
            "updates": updates,
            "total_count": total_count,
            "has_more": (skip + limit) < total_count,
        }
    except Exception as e:
        logger.error(f"Error getting update history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve update history")


@router.get("/admin/visa-updates/scheduler/status")
async def get_scheduler_status(admin=Depends(require_admin)):
    """Get visa update scheduler status - PROTECTED."""
    try:
        if visa_scheduler is None:
            return {"success": True, "is_running": False, "message": "Scheduler not initialized"}

        status = await visa_scheduler.get_schedule_status()

        recent_logs = await db.scheduler_logs.find({"job_type": "visa_update"}).sort("executed_at", -1).limit(5).to_list(length=None)

        return {"success": True, **status, "recent_logs": serialize_doc(recent_logs)}
    except Exception as e:
        logger.error(f"Error getting scheduler status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/visa-updates/scheduler/trigger")
async def trigger_manual_scheduler_update(admin=Depends(require_admin)):
    """Manually trigger visa update scan (outside of schedule) - PROTECTED."""
    try:
        if visa_scheduler is None:
            raise HTTPException(status_code=503, detail="Scheduler not initialized")

        asyncio.create_task(visa_scheduler.trigger_manual_update())

        return {
            "success": True,
            "message": "Manual visa update triggered. Check pending updates in a few minutes.",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering manual update: {e}")
        raise HTTPException(status_code=500, detail=str(e))
