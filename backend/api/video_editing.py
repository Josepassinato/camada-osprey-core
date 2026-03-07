"""
Video editing API router.

Provides endpoints for uploading videos, creating editing projects,
defining pipelines, and executing video processing jobs.
"""

import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from backend.core.auth import get_current_user
from backend.core.database import db
from backend.core.serialization import serialize_doc
from backend.models.video import (
    VideoJobResponse,
    VideoJobStatus,
    VideoPipeline,
    VideoProjectCreate,
    VideoProjectUpdate,
    VideoProbeResult,
)
from backend.services.video_editing import (
    MAX_FILE_SIZE,
    VIDEO_WORKSPACE,
    cleanup_job,
    execute_pipeline,
    generate_thumbnail,
    probe_video,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/video", tags=["Video Editing"])

ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".gif"}
ALLOWED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".aac", ".ogg", ".m4a"}
ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".svg"}
ALLOWED_EXTENSIONS = ALLOWED_VIDEO_EXTENSIONS | ALLOWED_AUDIO_EXTENSIONS | ALLOWED_IMAGE_EXTENSIONS


# ============================================================================
# FILE UPLOAD
# ============================================================================


@router.post("/upload")
async def upload_media(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
):
    """
    Upload a media file (video, audio, or image) for editing.

    Returns a file key that can be referenced in pipeline operations.
    """
    if not file.filename:
        raise HTTPException(400, "Filename is required")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            400,
            f"Unsupported file type '{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    # Read and validate size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(413, f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB")

    file_id = str(uuid.uuid4())
    upload_dir = VIDEO_WORKSPACE / "uploads" / user["id"]
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir / f"{file_id}{ext}"
    with open(file_path, "wb") as f:
        f.write(content)

    # Store file metadata in DB
    file_doc = {
        "file_id": file_id,
        "user_id": user["id"],
        "original_name": file.filename,
        "file_path": str(file_path),
        "extension": ext,
        "size": len(content),
        "content_type": file.content_type,
        "created_at": datetime.now(timezone.utc),
    }
    await db.video_files.insert_one(file_doc)

    logger.info("Media file uploaded", extra={
        "file_id": file_id,
        "user_id": user["id"],
        "filename": file.filename,
        "size": len(content),
    })

    return serialize_doc({
        "file_id": file_id,
        "original_name": file.filename,
        "size": len(content),
        "extension": ext,
    })


# ============================================================================
# VIDEO PROBE
# ============================================================================


@router.get("/probe/{file_id}", response_model=VideoProbeResult)
async def probe_media(
    file_id: str,
    user: dict = Depends(get_current_user),
):
    """Get metadata (duration, resolution, codec, etc.) for an uploaded file."""
    file_doc = await db.video_files.find_one({
        "file_id": file_id,
        "user_id": user["id"],
    })
    if not file_doc:
        raise HTTPException(404, "File not found")

    try:
        result = await probe_video(file_doc["file_path"])
    except Exception as e:
        logger.error("Probe failed", extra={"file_id": file_id, "error": str(e)})
        raise HTTPException(422, f"Could not probe file: {str(e)}")

    return result


# ============================================================================
# PROJECTS (CRUD)
# ============================================================================


@router.post("/projects")
async def create_project(
    data: VideoProjectCreate,
    user: dict = Depends(get_current_user),
):
    """Create a new video editing project."""
    project = {
        "project_id": str(uuid.uuid4()),
        "user_id": user["id"],
        "name": data.name,
        "description": data.description,
        "pipeline": None,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    await db.video_projects.insert_one(project)

    logger.info("Video project created", extra={
        "project_id": project["project_id"],
        "user_id": user["id"],
    })

    return serialize_doc(project)


@router.get("/projects")
async def list_projects(
    user: dict = Depends(get_current_user),
):
    """List all video editing projects for the current user."""
    projects = await db.video_projects.find(
        {"user_id": user["id"]}
    ).sort("updated_at", -1).to_list(100)

    return [serialize_doc(p) for p in projects]


@router.get("/projects/{project_id}")
async def get_project(
    project_id: str,
    user: dict = Depends(get_current_user),
):
    """Get a specific video project."""
    project = await db.video_projects.find_one({
        "project_id": project_id,
        "user_id": user["id"],
    })
    if not project:
        raise HTTPException(404, "Project not found")

    return serialize_doc(project)


@router.patch("/projects/{project_id}")
async def update_project(
    project_id: str,
    data: VideoProjectUpdate,
    user: dict = Depends(get_current_user),
):
    """Update a video project (name, description, or pipeline)."""
    project = await db.video_projects.find_one({
        "project_id": project_id,
        "user_id": user["id"],
    })
    if not project:
        raise HTTPException(404, "Project not found")

    update_fields = {"updated_at": datetime.now(timezone.utc)}
    if data.name is not None:
        update_fields["name"] = data.name
    if data.description is not None:
        update_fields["description"] = data.description
    if data.pipeline is not None:
        update_fields["pipeline"] = data.pipeline.model_dump()

    await db.video_projects.update_one(
        {"project_id": project_id},
        {"$set": update_fields},
    )

    project.update(update_fields)
    return serialize_doc(project)


@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: str,
    user: dict = Depends(get_current_user),
):
    """Delete a video project and its associated jobs."""
    result = await db.video_projects.delete_one({
        "project_id": project_id,
        "user_id": user["id"],
    })
    if result.deleted_count == 0:
        raise HTTPException(404, "Project not found")

    # Clean up associated jobs
    jobs = await db.video_jobs.find({"project_id": project_id}).to_list(100)
    for job in jobs:
        cleanup_job(job["job_id"])
    await db.video_jobs.delete_many({"project_id": project_id})

    return {"status": "deleted"}


# ============================================================================
# PIPELINE EXECUTION
# ============================================================================


@router.post("/projects/{project_id}/execute", response_model=VideoJobResponse)
async def execute_project_pipeline(
    project_id: str,
    user: dict = Depends(get_current_user),
):
    """Execute the pipeline defined in a project. Creates a processing job."""
    project = await db.video_projects.find_one({
        "project_id": project_id,
        "user_id": user["id"],
    })
    if not project:
        raise HTTPException(404, "Project not found")

    if not project.get("pipeline"):
        raise HTTPException(400, "No pipeline defined for this project. Update the project with a pipeline first.")

    pipeline = VideoPipeline(**project["pipeline"])

    # Resolve file keys to paths
    input_files = await _resolve_input_files(pipeline, user["id"])

    job_id = str(uuid.uuid4())
    job_doc = {
        "job_id": job_id,
        "project_id": project_id,
        "user_id": user["id"],
        "status": VideoJobStatus.processing,
        "progress": 0.0,
        "pipeline": project["pipeline"],
        "created_at": datetime.now(timezone.utc),
    }
    await db.video_jobs.insert_one(job_doc)

    # Execute pipeline (in-request for now; can be moved to background task)
    try:
        await db.video_jobs.update_one(
            {"job_id": job_id},
            {"$set": {"status": VideoJobStatus.processing, "progress": 10.0}},
        )

        output_path = await execute_pipeline(pipeline, input_files, job_id)

        await db.video_jobs.update_one(
            {"job_id": job_id},
            {"$set": {
                "status": VideoJobStatus.completed,
                "progress": 100.0,
                "output_path": output_path,
            }},
        )

        logger.info("Video job completed", extra={"job_id": job_id, "project_id": project_id})

        return VideoJobResponse(
            job_id=job_id,
            project_id=project_id,
            status=VideoJobStatus.completed,
            progress=100.0,
            output_url=f"/api/video/jobs/{job_id}/download",
        )

    except Exception as e:
        logger.error("Video job failed", extra={"job_id": job_id, "error": str(e)})
        await db.video_jobs.update_one(
            {"job_id": job_id},
            {"$set": {"status": VideoJobStatus.failed, "error": str(e)}},
        )
        return VideoJobResponse(
            job_id=job_id,
            project_id=project_id,
            status=VideoJobStatus.failed,
            error=str(e),
        )


@router.post("/execute")
async def execute_pipeline_direct(
    pipeline: VideoPipeline,
    user: dict = Depends(get_current_user),
):
    """
    Execute a pipeline directly without creating a project.

    Useful for one-off edits or programmatic usage by Claude Code.
    """
    input_files = await _resolve_input_files(pipeline, user["id"])

    job_id = str(uuid.uuid4())
    job_doc = {
        "job_id": job_id,
        "project_id": None,
        "user_id": user["id"],
        "status": VideoJobStatus.processing,
        "progress": 0.0,
        "pipeline": pipeline.model_dump(),
        "created_at": datetime.now(timezone.utc),
    }
    await db.video_jobs.insert_one(job_doc)

    try:
        output_path = await execute_pipeline(pipeline, input_files, job_id)

        await db.video_jobs.update_one(
            {"job_id": job_id},
            {"$set": {
                "status": VideoJobStatus.completed,
                "progress": 100.0,
                "output_path": output_path,
            }},
        )

        return serialize_doc({
            "job_id": job_id,
            "status": "completed",
            "download_url": f"/api/video/jobs/{job_id}/download",
        })

    except Exception as e:
        await db.video_jobs.update_one(
            {"job_id": job_id},
            {"$set": {"status": VideoJobStatus.failed, "error": str(e)}},
        )
        raise HTTPException(422, f"Pipeline execution failed: {str(e)}")


# ============================================================================
# JOBS
# ============================================================================


@router.get("/jobs")
async def list_jobs(
    user: dict = Depends(get_current_user),
):
    """List all video processing jobs for the current user."""
    jobs = await db.video_jobs.find(
        {"user_id": user["id"]}
    ).sort("created_at", -1).to_list(50)

    return [serialize_doc(j) for j in jobs]


@router.get("/jobs/{job_id}")
async def get_job(
    job_id: str,
    user: dict = Depends(get_current_user),
):
    """Get the status of a video processing job."""
    job = await db.video_jobs.find_one({
        "job_id": job_id,
        "user_id": user["id"],
    })
    if not job:
        raise HTTPException(404, "Job not found")

    return serialize_doc(job)


@router.get("/jobs/{job_id}/download")
async def download_job_output(
    job_id: str,
    user: dict = Depends(get_current_user),
):
    """Download the output file of a completed job."""
    job = await db.video_jobs.find_one({
        "job_id": job_id,
        "user_id": user["id"],
    })
    if not job:
        raise HTTPException(404, "Job not found")

    if job["status"] != VideoJobStatus.completed:
        raise HTTPException(400, f"Job is not completed (status: {job['status']})")

    output_path = job.get("output_path")
    if not output_path or not Path(output_path).exists():
        raise HTTPException(404, "Output file not found")

    return FileResponse(
        output_path,
        filename=Path(output_path).name,
        media_type="application/octet-stream",
    )


@router.delete("/jobs/{job_id}")
async def delete_job(
    job_id: str,
    user: dict = Depends(get_current_user),
):
    """Delete a job and its output files."""
    result = await db.video_jobs.delete_one({
        "job_id": job_id,
        "user_id": user["id"],
    })
    if result.deleted_count == 0:
        raise HTTPException(404, "Job not found")

    cleanup_job(job_id)
    return {"status": "deleted"}


# ============================================================================
# THUMBNAIL
# ============================================================================


@router.get("/thumbnail/{file_id}")
async def get_thumbnail(
    file_id: str,
    time: float = 1.0,
    user: dict = Depends(get_current_user),
):
    """Generate and return a thumbnail from a video at a specific timestamp."""
    file_doc = await db.video_files.find_one({
        "file_id": file_id,
        "user_id": user["id"],
    })
    if not file_doc:
        raise HTTPException(404, "File not found")

    try:
        thumb_path = await generate_thumbnail(file_doc["file_path"], file_id, time)
    except Exception as e:
        raise HTTPException(422, f"Could not generate thumbnail: {str(e)}")

    return FileResponse(thumb_path, media_type="image/jpeg")


# ============================================================================
# HELPERS
# ============================================================================


async def _resolve_input_files(pipeline: VideoPipeline, user_id: str) -> Dict[str, str]:
    """Resolve file keys from the pipeline to actual file paths on disk."""
    # Collect all file keys referenced in the pipeline
    keys = {pipeline.input_key}

    for op in pipeline.operations:
        if hasattr(op, "inputs"):
            keys.update(op.inputs)
        if hasattr(op, "audio_input"):
            keys.add(op.audio_input)
        if hasattr(op, "image_input"):
            keys.add(op.image_input)

    # Look up all files in DB
    files = await db.video_files.find({
        "file_id": {"$in": list(keys)},
        "user_id": user_id,
    }).to_list(len(keys))

    resolved = {f["file_id"]: f["file_path"] for f in files}

    missing = keys - set(resolved.keys())
    if missing:
        raise HTTPException(404, f"Files not found: {', '.join(missing)}")

    # Verify files exist on disk
    for key, path in resolved.items():
        if not Path(path).exists():
            raise HTTPException(404, f"File '{key}' no longer exists on disk")

    return resolved
