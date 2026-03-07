import asyncio
import json
import logging
import os
import shutil
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from models.video_editing import (
    AudioCodec,
    OperationType,
    RESOLUTION_MAP,
    VideoCodec,
    VideoFormat,
    VideoResolution,
)

logger = logging.getLogger(__name__)

# Base directory for video storage
VIDEO_STORAGE_DIR = os.getenv("VIDEO_STORAGE_DIR", "/tmp/osprey_videos")
MAX_VIDEO_SIZE_MB = int(os.getenv("MAX_VIDEO_SIZE_MB", "500"))

SUPPORTED_VIDEO_MIMES = {
    "video/mp4",
    "video/webm",
    "video/x-msvideo",
    "video/quicktime",
    "video/x-matroska",
}

SUPPORTED_AUDIO_MIMES = {
    "audio/mpeg",
    "audio/wav",
    "audio/ogg",
    "audio/aac",
}

FILTER_MAP = {
    "grayscale": "colorchannelmixer=.3:.4:.3:0:.3:.4:.3:0:.3:.4:.3",
    "sepia": "colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131",
    "blur": "boxblur={intensity_int}:1",
    "sharpen": "unsharp=5:5:{intensity}:5:5:0.0",
    "brightness": "eq=brightness={brightness_val}",
    "contrast": "eq=contrast={intensity}",
    "saturation": "eq=saturation={intensity}",
}


def _ensure_storage_dir(user_id: str) -> Path:
    """Create user-specific storage directory."""
    user_dir = Path(VIDEO_STORAGE_DIR) / user_id
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir


def _get_project_dir(user_id: str, project_id: str) -> Path:
    """Get project-specific directory."""
    project_dir = Path(VIDEO_STORAGE_DIR) / user_id / project_id
    project_dir.mkdir(parents=True, exist_ok=True)
    return project_dir


def validate_video_file(mime_type: str, file_size: int) -> Optional[str]:
    """Validate video file type and size. Returns error message or None."""
    if mime_type not in SUPPORTED_VIDEO_MIMES and mime_type not in SUPPORTED_AUDIO_MIMES:
        return f"Unsupported file type: {mime_type}. Supported: {', '.join(SUPPORTED_VIDEO_MIMES | SUPPORTED_AUDIO_MIMES)}"

    max_bytes = MAX_VIDEO_SIZE_MB * 1024 * 1024
    if file_size > max_bytes:
        return f"File too large: {file_size / (1024*1024):.1f}MB. Maximum: {MAX_VIDEO_SIZE_MB}MB"

    return None


async def run_ffmpeg(args: List[str], timeout: int = 300) -> Dict[str, Any]:
    """Run an ffmpeg command asynchronously.

    Args:
        args: List of ffmpeg arguments (without the 'ffmpeg' prefix).
        timeout: Maximum execution time in seconds.

    Returns:
        dict with keys: success, stdout, stderr, return_code
    """
    cmd = ["ffmpeg", "-y", "-hide_banner"] + args

    logger.info("Running ffmpeg command", extra={"args": " ".join(cmd)})

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await asyncio.wait_for(
            process.communicate(), timeout=timeout
        )

        return {
            "success": process.returncode == 0,
            "stdout": stdout.decode("utf-8", errors="replace"),
            "stderr": stderr.decode("utf-8", errors="replace"),
            "return_code": process.returncode,
        }

    except asyncio.TimeoutError:
        process.kill()
        logger.error("ffmpeg command timed out", extra={"timeout": timeout})
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Command timed out after {timeout}s",
            "return_code": -1,
        }
    except FileNotFoundError:
        logger.error("ffmpeg not found. Install ffmpeg to use video editing features.")
        return {
            "success": False,
            "stdout": "",
            "stderr": "ffmpeg not installed. Run: apt-get install ffmpeg",
            "return_code": -1,
        }


async def run_ffprobe(file_path: str) -> Dict[str, Any]:
    """Probe a media file to get metadata.

    Args:
        file_path: Path to the media file.

    Returns:
        dict with file metadata (duration, dimensions, codecs, etc.)
    """
    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        file_path,
    ]

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)

        if process.returncode != 0:
            return {"success": False, "error": stderr.decode("utf-8", errors="replace")}

        probe_data = json.loads(stdout.decode("utf-8"))

        video_stream = next(
            (s for s in probe_data.get("streams", []) if s.get("codec_type") == "video"),
            None,
        )
        audio_stream = next(
            (s for s in probe_data.get("streams", []) if s.get("codec_type") == "audio"),
            None,
        )
        fmt = probe_data.get("format", {})

        result = {
            "success": True,
            "filename": os.path.basename(file_path),
            "duration": float(fmt.get("duration", 0)),
            "file_size": int(fmt.get("size", 0)),
            "format": fmt.get("format_name", "unknown"),
            "bitrate": int(fmt.get("bit_rate", 0)),
        }

        if video_stream:
            fps_parts = video_stream.get("r_frame_rate", "0/1").split("/")
            fps = float(fps_parts[0]) / float(fps_parts[1]) if len(fps_parts) == 2 and float(fps_parts[1]) > 0 else 0

            result.update({
                "width": int(video_stream.get("width", 0)),
                "height": int(video_stream.get("height", 0)),
                "fps": round(fps, 2),
                "video_codec": video_stream.get("codec_name", "unknown"),
            })

        if audio_stream:
            result["audio_codec"] = audio_stream.get("codec_name", "unknown")
            result["audio_sample_rate"] = int(audio_stream.get("sample_rate", 0))

        return result

    except FileNotFoundError:
        return {"success": False, "error": "ffprobe not installed"}
    except Exception as e:
        logger.error(f"ffprobe failed: {str(e)}")
        return {"success": False, "error": str(e)}


async def save_uploaded_file(
    content: bytes,
    filename: str,
    user_id: str,
    project_id: str,
) -> Dict[str, Any]:
    """Save uploaded video file to disk.

    Returns:
        dict with source_id, file_path, and probe metadata.
    """
    source_id = str(uuid.uuid4())
    project_dir = _get_project_dir(user_id, project_id)
    ext = Path(filename).suffix or ".mp4"
    file_path = project_dir / f"{source_id}{ext}"

    with open(file_path, "wb") as f:
        f.write(content)

    probe = await run_ffprobe(str(file_path))

    return {
        "source_id": source_id,
        "file_path": str(file_path),
        "filename": filename,
        "probe": probe if probe.get("success") else None,
    }


async def execute_operation(
    source_path: str,
    operation: str,
    params: Dict[str, Any],
    output_dir: str,
) -> Dict[str, Any]:
    """Execute a single video editing operation.

    Args:
        source_path: Path to the source video.
        operation: Operation type (trim, resize, etc.).
        params: Operation-specific parameters.
        output_dir: Directory to write output files.

    Returns:
        dict with output_path and operation details.
    """
    output_id = str(uuid.uuid4())
    source_ext = Path(source_path).suffix
    output_path = os.path.join(output_dir, f"{output_id}{source_ext}")

    if operation == OperationType.trim:
        start = params.get("start_time", 0)
        end = params.get("end_time")
        args = ["-i", source_path, "-ss", str(start)]
        if end is not None:
            args.extend(["-t", str(end - start)])
        args.extend(["-c", "copy", output_path])

    elif operation == OperationType.resize:
        resolution = params.get("resolution")
        width = params.get("width")
        height = params.get("height")
        keep_aspect = params.get("keep_aspect_ratio", True)

        if resolution and resolution in RESOLUTION_MAP:
            width, height = RESOLUTION_MAP[VideoResolution(resolution)]

        if width and height:
            if keep_aspect:
                scale_filter = f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"
            else:
                scale_filter = f"scale={width}:{height}"
        elif width:
            scale_filter = f"scale={width}:-2"
        elif height:
            scale_filter = f"scale=-2:{height}"
        else:
            return {"success": False, "error": "No resolution, width, or height provided"}

        args = ["-i", source_path, "-vf", scale_filter, "-c:a", "copy", output_path]

    elif operation == OperationType.crop:
        x = params.get("x", 0)
        y = params.get("y", 0)
        w = params.get("width")
        h = params.get("height")
        if not w or not h:
            return {"success": False, "error": "crop requires width and height"}
        args = ["-i", source_path, "-vf", f"crop={w}:{h}:{x}:{y}", "-c:a", "copy", output_path]

    elif operation == OperationType.rotate:
        angle = params.get("angle", 90)
        if angle == 90:
            transpose = "transpose=1"
        elif angle == 180:
            transpose = "transpose=1,transpose=1"
        elif angle == 270:
            transpose = "transpose=2"
        else:
            transpose = f"rotate={angle}*PI/180"
        args = ["-i", source_path, "-vf", transpose, "-c:a", "copy", output_path]

    elif operation == OperationType.speed:
        factor = params.get("factor", 1.0)
        video_filter = f"setpts={1/factor}*PTS"
        audio_filter = f"atempo={factor}" if params.get("adjust_audio", True) else None

        args = ["-i", source_path, "-vf", video_filter]
        if audio_filter:
            args.extend(["-af", audio_filter])
        else:
            args.extend(["-an"])
        args.append(output_path)

    elif operation == OperationType.overlay_text:
        text = params.get("text", "").replace("'", "\\'").replace(":", "\\:")
        x = params.get("x", 10)
        y = params.get("y", 10)
        font_size = params.get("font_size", 24)
        font_color = params.get("font_color", "white")

        drawtext = f"drawtext=text='{text}':x={x}:y={y}:fontsize={font_size}:fontcolor={font_color}"

        bg_color = params.get("bg_color")
        if bg_color:
            drawtext += f":box=1:boxcolor={bg_color}:boxborderw=5"

        start_time = params.get("start_time")
        end_time = params.get("end_time")
        if start_time is not None and end_time is not None:
            drawtext += f":enable='between(t,{start_time},{end_time})'"

        args = ["-i", source_path, "-vf", drawtext, "-c:a", "copy", output_path]

    elif operation == OperationType.audio_extract:
        output_path = os.path.join(output_dir, f"{output_id}.aac")
        args = ["-i", source_path, "-vn", "-acodec", "aac", output_path]

    elif operation == OperationType.audio_volume:
        volume = params.get("volume", 1.0)
        args = ["-i", source_path, "-af", f"volume={volume}", "-c:v", "copy", output_path]

    elif operation == OperationType.audio_replace:
        audio_path = params.get("audio_path")
        if not audio_path or not os.path.exists(audio_path):
            return {"success": False, "error": "Audio file not found"}
        args = [
            "-i", source_path,
            "-i", audio_path,
            "-map", "0:v",
            "-map", "1:a",
            "-c:v", "copy",
            "-shortest",
            output_path,
        ]

    elif operation == OperationType.filter_apply:
        filter_name = params.get("filter_name", "grayscale")
        intensity = params.get("intensity", 1.0)

        filter_template = FILTER_MAP.get(filter_name)
        if not filter_template:
            return {"success": False, "error": f"Unknown filter: {filter_name}. Available: {list(FILTER_MAP.keys())}"}

        intensity_int = max(1, int(intensity * 5))
        brightness_val = (intensity - 1.0) * 0.3
        vf = filter_template.format(
            intensity=intensity,
            intensity_int=intensity_int,
            brightness_val=brightness_val,
        )
        args = ["-i", source_path, "-vf", vf, "-c:a", "copy", output_path]

    elif operation == OperationType.thumbnail:
        time = params.get("time", 0)
        width = params.get("width", 1280)
        height = params.get("height", 720)
        output_path = os.path.join(output_dir, f"{output_id}.jpg")
        args = [
            "-i", source_path,
            "-ss", str(time),
            "-vframes", "1",
            "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease",
            output_path,
        ]

    elif operation == OperationType.watermark:
        text = params.get("text")
        position = params.get("position", "bottom_right")
        opacity = params.get("opacity", 0.5)

        position_map = {
            "top_left": "x=10:y=10",
            "top_right": "x=w-tw-10:y=10",
            "bottom_left": "x=10:y=h-th-10",
            "bottom_right": "x=w-tw-10:y=h-th-10",
            "center": "x=(w-tw)/2:y=(h-th)/2",
        }
        pos = position_map.get(position, position_map["bottom_right"])

        if text:
            safe_text = text.replace("'", "\\'").replace(":", "\\:")
            vf = f"drawtext=text='{safe_text}':{pos}:fontsize=20:fontcolor=white@{opacity}"
            args = ["-i", source_path, "-vf", vf, "-c:a", "copy", output_path]
        else:
            return {"success": False, "error": "Watermark requires text or image_path"}

    elif operation == OperationType.subtitle:
        subtitles = params.get("subtitles", [])
        if not subtitles:
            return {"success": False, "error": "No subtitles provided"}

        srt_path = os.path.join(output_dir, f"{output_id}.srt")
        with open(srt_path, "w", encoding="utf-8") as f:
            for i, sub in enumerate(subtitles, 1):
                start = _seconds_to_srt_time(sub.get("start", 0))
                end = _seconds_to_srt_time(sub.get("end", 0))
                text = sub.get("text", "")
                f.write(f"{i}\n{start} --> {end}\n{text}\n\n")

        font_size = params.get("font_size", 20)
        font_color = params.get("font_color", "&Hffffff&")
        vf = f"subtitles={srt_path}:force_style='FontSize={font_size}'"
        args = ["-i", source_path, "-vf", vf, "-c:a", "copy", output_path]

    elif operation == OperationType.concat:
        source_ids = params.get("source_paths", [])
        if not source_ids:
            return {"success": False, "error": "No source paths for concatenation"}

        concat_list_path = os.path.join(output_dir, f"{output_id}_concat.txt")
        with open(concat_list_path, "w") as f:
            f.write(f"file '{source_path}'\n")
            for path in source_ids:
                f.write(f"file '{path}'\n")

        args = ["-f", "concat", "-safe", "0", "-i", concat_list_path, "-c", "copy", output_path]

    else:
        return {"success": False, "error": f"Unsupported operation: {operation}"}

    result = await run_ffmpeg(args)

    if result["success"]:
        return {
            "success": True,
            "output_path": output_path,
            "operation": operation,
        }
    else:
        logger.error(
            "Video operation failed",
            extra={"operation": operation, "stderr": result["stderr"][:500]},
        )
        return {
            "success": False,
            "error": result["stderr"][:500],
            "operation": operation,
        }


async def export_video(
    source_path: str,
    output_dir: str,
    format: str = "mp4",
    video_codec: str = "h264",
    audio_codec: str = "aac",
    resolution: Optional[str] = None,
    bitrate: Optional[str] = None,
    fps: Optional[int] = None,
) -> Dict[str, Any]:
    """Export video with specific encoding settings.

    Args:
        source_path: Path to the source video.
        output_dir: Directory to write the exported file.
        format: Output format (mp4, webm, etc.).
        video_codec: Video codec to use.
        audio_codec: Audio codec to use.
        resolution: Target resolution preset.
        bitrate: Target bitrate (e.g. "5M").
        fps: Target frame rate.

    Returns:
        dict with output_path and export details.
    """
    output_id = str(uuid.uuid4())
    output_path = os.path.join(output_dir, f"{output_id}.{format}")

    codec_map = {
        "h264": "libx264",
        "h265": "libx265",
        "vp9": "libvpx-vp9",
        "av1": "libaom-av1",
    }

    audio_codec_map = {
        "aac": "aac",
        "mp3": "libmp3lame",
        "opus": "libopus",
        "none": None,
    }

    args = ["-i", source_path]

    vcodec = codec_map.get(video_codec, "libx264")
    args.extend(["-c:v", vcodec])

    acodec = audio_codec_map.get(audio_codec, "aac")
    if acodec:
        args.extend(["-c:a", acodec])
    else:
        args.append("-an")

    if resolution and resolution in RESOLUTION_MAP:
        w, h = RESOLUTION_MAP[VideoResolution(resolution)]
        args.extend(["-vf", f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2"])

    if bitrate:
        args.extend(["-b:v", bitrate])

    if fps:
        args.extend(["-r", str(fps)])

    args.append(output_path)

    result = await run_ffmpeg(args, timeout=600)

    if result["success"]:
        probe = await run_ffprobe(output_path)
        return {
            "success": True,
            "output_path": output_path,
            "probe": probe if probe.get("success") else None,
        }
    else:
        return {"success": False, "error": result["stderr"][:500]}


def cleanup_project_files(user_id: str, project_id: str) -> None:
    """Remove all files for a project."""
    project_dir = _get_project_dir(user_id, project_id)
    if project_dir.exists():
        shutil.rmtree(project_dir)
        logger.info("Project files cleaned up", extra={"project_id": project_id})


def _seconds_to_srt_time(seconds: float) -> str:
    """Convert seconds to SRT timestamp format (HH:MM:SS,mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
