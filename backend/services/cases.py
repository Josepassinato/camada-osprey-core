import logging
from datetime import datetime, timezone

from core.database import db

logger = logging.getLogger(__name__)


def get_progress_percentage(step: str) -> int:
    """Calculate progress percentage based on step."""
    step_map = {
        "created": 0,
        "form_selected": 20,
        "story_recorded": 30,
        "friendly_form_partial": 45,
        "friendly-form-complete": 50,
        "documents_uploaded": 60,
        "ai_processing": 70,
        "form_generated": 80,
        "qa_passed": 90,
        "finalized": 100,
    }
    return step_map.get(step, 0)


async def update_case_status_and_progress(case_id: str, new_step: str, collection_name: str = "auto_cases"):
    """
    Update case status and progress based on new step.

    Args:
        case_id: Case ID
        new_step: New step name
        collection_name: Which collection (auto_cases or application_cases)
    """
    progress = get_progress_percentage(new_step)
    step_to_status = {
        "created": "created",
        "form_selected": "form_selected",
        "story_recorded": "in_progress",
        "friendly_form_partial": "in_progress",
        "friendly-form-complete": "in_progress",
        "documents_uploaded": "in_progress",
        "ai_processing": "processing",
        "form_generated": "processing",
        "qa_passed": "ready_for_submission",
        "finalized": "completed",
    }

    status = step_to_status.get(new_step, "in_progress")
    collection = db[collection_name]
    await collection.update_one(
        {"case_id": case_id},
        {
            "$set": {
                "current_step": new_step,
                "progress_percentage": progress,
                "status": status,
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )

    logger.info(f"📊 Case {case_id} updated: {new_step} ({progress}%) - Status: {status}")
