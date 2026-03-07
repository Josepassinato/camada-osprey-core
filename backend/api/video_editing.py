import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from backend.core.auth import get_current_user
from backend.core.database import db
from backend.core.serialization import serialize_doc
from backend.models.video_editing import (
    OperationType,
    ProjectStatus,
    VideoExportRequest,
    VideoFormat,
    VideoOperationRequest,
    VideoProjectCreate,
)
from backend.services.video_editing import (
    cleanup_project_files,
    execute_operation,
    export_video,
    run_ffprobe,
    save_uploaded_file,
    validate_video_file,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/video", tags=["Video Editing"])


# ===== PROJECT MANAGEMENT =====


@router.post("/projects")
async def create_project(
    data: VideoProjectCreate,
    current_user=Depends(get_current_user),
):
    """Create a new video editing project."""
    try:
        project = {
            "id": str(uuid.uuid4()),
            "user_id": current_user["id"],
            "name": data.name,
            "description": data.description,
            "status": ProjectStatus.created.value,
            "sources": [],
            "operations": [],
            "output": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        await db.video_projects.insert_one(project)

        logger.info(
            "Video project created",
            extra={"project_id": project["id"], "user_id": current_user["id"]},
        )

        return serialize_doc(project)

    except Exception as e:
        logger.error(f"Error creating video project: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating project: {str(e)}")


@router.get("/projects")
async def list_projects(
    current_user=Depends(get_current_user),
):
    """List all video projects for the current user."""
    try:
        projects = (
            await db.video_projects.find(
                {"user_id": current_user["id"]},
                {"_id": 0},
            )
            .sort("updated_at", -1)
            .to_list(50)
        )

        return {"projects": projects, "total": len(projects)}

    except Exception as e:
        logger.error(f"Error listing video projects: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing projects: {str(e)}")


@router.get("/projects/{project_id}")
async def get_project(
    project_id: str,
    current_user=Depends(get_current_user),
):
    """Get a specific video project."""
    try:
        project = await db.video_projects.find_one(
            {"id": project_id, "user_id": current_user["id"]},
            {"_id": 0},
        )
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        return project

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting video project: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting project: {str(e)}")


@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: str,
    current_user=Depends(get_current_user),
):
    """Delete a video project and its files."""
    try:
        project = await db.video_projects.find_one(
            {"id": project_id, "user_id": current_user["id"]},
        )
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        cleanup_project_files(current_user["id"], project_id)
        await db.video_projects.delete_one({"id": project_id})

        logger.info("Video project deleted", extra={"project_id": project_id})

        return {"message": "Project deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting video project: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting project: {str(e)}")


# ===== SOURCE UPLOAD =====


@router.post("/projects/{project_id}/sources")
async def upload_source(
    project_id: str,
    file: UploadFile = File(...),
    label: Optional[str] = Form(None),
    current_user=Depends(get_current_user),
):
    """Upload a source video/audio file to a project."""
    try:
        project = await db.video_projects.find_one(
            {"id": project_id, "user_id": current_user["id"]},
        )
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        content = await file.read()
        mime_type = file.content_type or "application/octet-stream"

        error = validate_video_file(mime_type, len(content))
        if error:
            raise HTTPException(status_code=400, detail=error)

        result = await save_uploaded_file(
            content=content,
            filename=file.filename,
            user_id=current_user["id"],
            project_id=project_id,
        )

        source_record = {
            "source_id": result["source_id"],
            "filename": file.filename,
            "label": label or file.filename,
            "file_path": result["file_path"],
            "mime_type": mime_type,
            "file_size": len(content),
            "probe": result.get("probe"),
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
        }

        await db.video_projects.update_one(
            {"id": project_id},
            {
                "$push": {"sources": source_record},
                "$set": {"updated_at": datetime.now(timezone.utc)},
            },
        )

        logger.info(
            "Source uploaded to video project",
            extra={
                "project_id": project_id,
                "source_id": result["source_id"],
                "filename": file.filename,
            },
        )

        return {
            "message": "Source uploaded successfully",
            "source_id": result["source_id"],
            "filename": file.filename,
            "probe": result.get("probe"),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading source: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading source: {str(e)}")


@router.get("/projects/{project_id}/sources/{source_id}/probe")
async def probe_source(
    project_id: str,
    source_id: str,
    current_user=Depends(get_current_user),
):
    """Get detailed metadata for a source file."""
    try:
        project = await db.video_projects.find_one(
            {"id": project_id, "user_id": current_user["id"]},
        )
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        source = next(
            (s for s in project.get("sources", []) if s["source_id"] == source_id),
            None,
        )
        if not source:
            raise HTTPException(status_code=404, detail="Source not found")

        probe = await run_ffprobe(source["file_path"])
        if not probe.get("success"):
            raise HTTPException(status_code=500, detail=probe.get("error", "Probe failed"))

        return probe

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error probing source: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error probing source: {str(e)}")


# ===== VIDEO OPERATIONS =====


@router.post("/projects/{project_id}/operations")
async def add_operation(
    project_id: str,
    request: VideoOperationRequest,
    current_user=Depends(get_current_user),
):
    """Apply a video editing operation to a source.

    Supported operations: trim, resize, crop, rotate, speed,
    overlay_text, overlay_image, audio_extract, audio_volume,
    audio_replace, filter_apply, thumbnail, watermark, subtitle, concat.
    """
    try:
        project = await db.video_projects.find_one(
            {"id": project_id, "user_id": current_user["id"]},
        )
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        source = next(
            (s for s in project.get("sources", []) if s["source_id"] == request.source_id),
            None,
        )
        if not source:
            raise HTTPException(status_code=404, detail="Source not found in project")

        if not os.path.exists(source["file_path"]):
            raise HTTPException(status_code=404, detail="Source file not found on disk")

        # For concat, resolve source_ids to file paths
        params = dict(request.params)
        if request.operation == OperationType.concat:
            source_ids = params.get("source_ids", [])
            source_paths = []
            for sid in source_ids:
                s = next(
                    (s for s in project.get("sources", []) if s["source_id"] == sid),
                    None,
                )
                if not s:
                    raise HTTPException(status_code=404, detail=f"Source {sid} not found")
                source_paths.append(s["file_path"])
            params["source_paths"] = source_paths

        # For audio_replace, resolve audio source path
        if request.operation == OperationType.audio_replace:
            audio_source_id = params.get("audio_source_id")
            if audio_source_id:
                audio_source = next(
                    (s for s in project.get("sources", []) if s["source_id"] == audio_source_id),
                    None,
                )
                if not audio_source:
                    raise HTTPException(status_code=404, detail="Audio source not found")
                params["audio_path"] = audio_source["file_path"]

        await db.video_projects.update_one(
            {"id": project_id},
            {"$set": {"status": ProjectStatus.processing.value, "updated_at": datetime.now(timezone.utc)}},
        )

        output_dir = os.path.dirname(source["file_path"])
        result = await execute_operation(
            source_path=source["file_path"],
            operation=request.operation,
            params=params,
            output_dir=output_dir,
        )

        if not result["success"]:
            await db.video_projects.update_one(
                {"id": project_id},
                {"$set": {"status": ProjectStatus.failed.value, "updated_at": datetime.now(timezone.utc)}},
            )
            raise HTTPException(status_code=500, detail=result.get("error", "Operation failed"))

        operation_record = {
            "operation_id": str(uuid.uuid4()),
            "source_id": request.source_id,
            "operation": request.operation.value,
            "params": request.params,
            "output_path": result["output_path"],
            "executed_at": datetime.now(timezone.utc).isoformat(),
        }

        # Add the output as a new source so it can be used in subsequent operations
        output_source = {
            "source_id": str(uuid.uuid4()),
            "filename": os.path.basename(result["output_path"]),
            "label": f"{request.operation.value} output",
            "file_path": result["output_path"],
            "mime_type": "video/mp4",
            "file_size": os.path.getsize(result["output_path"]) if os.path.exists(result["output_path"]) else 0,
            "probe": None,
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
            "generated": True,
        }

        await db.video_projects.update_one(
            {"id": project_id},
            {
                "$push": {
                    "operations": operation_record,
                    "sources": output_source,
                },
                "$set": {
                    "status": ProjectStatus.completed.value,
                    "updated_at": datetime.now(timezone.utc),
                },
            },
        )

        logger.info(
            "Video operation executed",
            extra={
                "project_id": project_id,
                "operation": request.operation.value,
                "output_source_id": output_source["source_id"],
            },
        )

        return {
            "message": "Operation completed successfully",
            "operation_id": operation_record["operation_id"],
            "output_source_id": output_source["source_id"],
            "output_path": result["output_path"],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing operation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error executing operation: {str(e)}")


# ===== EXPORT & DOWNLOAD =====


@router.post("/projects/{project_id}/export")
async def export_project(
    project_id: str,
    request: VideoExportRequest,
    source_id: Optional[str] = None,
    current_user=Depends(get_current_user),
):
    """Export a video source with specific encoding settings."""
    try:
        project = await db.video_projects.find_one(
            {"id": project_id, "user_id": current_user["id"]},
        )
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        sources = project.get("sources", [])
        if not sources:
            raise HTTPException(status_code=400, detail="No sources in project")

        # Use specified source or last generated source
        if source_id:
            source = next(
                (s for s in sources if s["source_id"] == source_id),
                None,
            )
        else:
            # Prefer last generated source, fallback to last source
            generated = [s for s in sources if s.get("generated")]
            source = generated[-1] if generated else sources[-1]

        if not source:
            raise HTTPException(status_code=404, detail="Source not found")

        output_dir = os.path.dirname(source["file_path"])

        result = await export_video(
            source_path=source["file_path"],
            output_dir=output_dir,
            format=request.format.value,
            video_codec=request.video_codec.value,
            audio_codec=request.audio_codec.value,
            resolution=request.resolution.value if request.resolution else None,
            bitrate=request.bitrate,
            fps=request.fps,
        )

        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Export failed"))

        await db.video_projects.update_one(
            {"id": project_id},
            {
                "$set": {
                    "output": {
                        "file_path": result["output_path"],
                        "format": request.format.value,
                        "probe": result.get("probe"),
                        "exported_at": datetime.now(timezone.utc).isoformat(),
                    },
                    "updated_at": datetime.now(timezone.utc),
                },
            },
        )

        logger.info(
            "Video exported",
            extra={"project_id": project_id, "format": request.format.value},
        )

        return {
            "message": "Video exported successfully",
            "output_path": result["output_path"],
            "probe": result.get("probe"),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting video: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error exporting video: {str(e)}")


@router.get("/projects/{project_id}/download/{source_id}")
async def download_file(
    project_id: str,
    source_id: str,
    current_user=Depends(get_current_user),
):
    """Download a source or output file from a project."""
    try:
        project = await db.video_projects.find_one(
            {"id": project_id, "user_id": current_user["id"]},
        )
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        source = next(
            (s for s in project.get("sources", []) if s["source_id"] == source_id),
            None,
        )
        if not source:
            raise HTTPException(status_code=404, detail="Source not found")

        file_path = source["file_path"]
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found on disk")

        return FileResponse(
            path=file_path,
            filename=source.get("filename", os.path.basename(file_path)),
            media_type=source.get("mime_type", "application/octet-stream"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")


# ===== UTILITY =====


@router.get("/capabilities")
async def get_video_capabilities():
    """Get available video editing capabilities and supported formats."""
    return {
        "operations": [op.value for op in OperationType],
        "formats": [fmt.value for fmt in VideoFormat],
        "filters": [
            "grayscale", "sepia", "blur", "sharpen",
            "brightness", "contrast", "saturation",
        ],
        "max_upload_size_mb": int(os.getenv("MAX_VIDEO_SIZE_MB", "500")),
        "supported_video_types": [
            "video/mp4", "video/webm", "video/x-msvideo",
            "video/quicktime", "video/x-matroska",
        ],
        "supported_audio_types": [
            "audio/mpeg", "audio/wav", "audio/ogg", "audio/aac",
        ],
    }


# ===== REMOTION INTEGRATION =====


@router.get("/remotion/templates")
async def list_remotion_templates():
    """List available Remotion project templates."""
    from backend.services.video_remotion import list_templates

    return {"templates": list_templates()}


@router.post("/remotion/projects")
async def create_remotion_project(
    data: dict,
    current_user=Depends(get_current_user),
):
    """Create a new Remotion project from a template.

    Body params:
        name: Project name
        template: Template ID (blank, text-animation, slideshow, lower-third, countdown)
        width: Video width (default 1920)
        height: Video height (default 1080)
        fps: Frame rate (default 30)
        duration_seconds: Duration in seconds (default 5)
    """
    from backend.services.video_remotion import create_remotion_project as create_project

    try:
        result = await create_project(
            project_name=data.get("name", "untitled"),
            template=data.get("template", "blank"),
            width=data.get("width", 1920),
            height=data.get("height", 1080),
            fps=data.get("fps", 30),
            duration_seconds=data.get("duration_seconds", 5.0),
        )

        # Store in DB
        project_record = {
            "id": str(uuid.uuid4()),
            "user_id": current_user["id"],
            "type": "remotion",
            "name": data.get("name", "untitled"),
            "template": data.get("template", "blank"),
            "project_dir": result["project_dir"],
            "compositions": result["compositions"],
            "status": "created",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        await db.video_projects.insert_one(project_record)

        logger.info(
            "Remotion project created",
            extra={"project_id": project_record["id"], "template": data.get("template")},
        )

        return {
            "message": "Remotion project created",
            "project_id": project_record["id"],
            "project_dir": result["project_dir"],
            "compositions": result["compositions"],
            "requires_npm_install": True,
        }

    except Exception as e:
        logger.error(f"Error creating Remotion project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/remotion/projects/{project_id}/install")
async def install_remotion_deps(
    project_id: str,
    current_user=Depends(get_current_user),
):
    """Install npm dependencies for a Remotion project."""
    from backend.services.video_remotion import install_dependencies

    try:
        project = await db.video_projects.find_one(
            {"id": project_id, "user_id": current_user["id"], "type": "remotion"},
        )
        if not project:
            raise HTTPException(status_code=404, detail="Remotion project not found")

        result = await install_dependencies(project["project_dir"])

        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "npm install failed"))

        await db.video_projects.update_one(
            {"id": project_id},
            {"$set": {"status": "ready", "updated_at": datetime.now(timezone.utc)}},
        )

        return {"message": "Dependencies installed successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error installing Remotion deps: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/remotion/projects/{project_id}/render")
async def render_remotion_project(
    project_id: str,
    data: dict,
    current_user=Depends(get_current_user),
):
    """Render a Remotion composition to video.

    Body params:
        composition_id: Composition to render (default "Main")
        props: Input props for the composition
        codec: Video codec (default "h264")
        crf: Quality (0-63, default 18)
    """
    from backend.services.video_remotion import render_composition

    try:
        project = await db.video_projects.find_one(
            {"id": project_id, "user_id": current_user["id"], "type": "remotion"},
        )
        if not project:
            raise HTTPException(status_code=404, detail="Remotion project not found")

        await db.video_projects.update_one(
            {"id": project_id},
            {"$set": {"status": "rendering", "updated_at": datetime.now(timezone.utc)}},
        )

        result = await render_composition(
            project_dir=project["project_dir"],
            composition_id=data.get("composition_id", "Main"),
            props=data.get("props"),
            codec=data.get("codec", "h264"),
            crf=data.get("crf", 18),
        )

        status = "completed" if result["success"] else "failed"
        await db.video_projects.update_one(
            {"id": project_id},
            {
                "$set": {
                    "status": status,
                    "render_output": result,
                    "updated_at": datetime.now(timezone.utc),
                },
            },
        )

        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Render failed"))

        return {
            "message": "Video rendered successfully",
            "output_path": result["output_path"],
            "file_size": result.get("file_size", 0),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rendering Remotion project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
