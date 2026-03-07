"""
MCP (Model Context Protocol) Server for Video Editing.

Exposes video editing tools via the official MCP SDK so that Claude Code
and other MCP-compatible clients can edit videos through natural language.

Usage:
    # stdio transport (for Claude Code / Claude Desktop)
    python -m backend.services.video_mcp_server

    # HTTP transport (for network access)
    python -m backend.services.video_mcp_server --http --port 8002

    # Claude Code MCP config (~/.claude.json or project .mcp.json):
    {
        "mcpServers": {
            "video-editor": {
                "command": "python",
                "args": ["-m", "backend.services.video_mcp_server"],
                "cwd": "/path/to/camada-osprey-core"
            }
        }
    }

Prerequisites:
    pip install "mcp[cli]"
    apt-get install ffmpeg  (or brew install ffmpeg)
"""

import json
import logging
import os
import sys
from typing import List, Optional

from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

# Video workspace directory
WORKSPACE_DIR = os.getenv("VIDEO_WORKSPACE_DIR", "/tmp/osprey_mcp_videos")

# Create the MCP server
mcp = FastMCP(
    "Osprey Video Editor",
    version="1.0.0",
    description="AI-powered video editing tools using FFmpeg. Supports trim, resize, crop, rotate, filters, text overlays, watermarks, subtitles, audio processing, and more.",
)


def _ensure_workspace() -> str:
    """Create and return the workspace directory."""
    os.makedirs(WORKSPACE_DIR, exist_ok=True)
    return WORKSPACE_DIR


def _import_services():
    """Lazy import of video editing services."""
    from backend.services.video_editing import (
        execute_operation,
        export_video,
        run_ffprobe,
    )
    return execute_operation, export_video, run_ffprobe


def _format_result(result: dict) -> str:
    """Format a result dict as readable JSON."""
    return json.dumps(result, indent=2, default=str)


# ===== Tools =====


@mcp.tool()
async def video_probe(file_path: str) -> str:
    """Analyze a video file and return metadata including duration, resolution, codecs, FPS, and file size.

    Args:
        file_path: Absolute path to the video file to analyze.
    """
    _, _, run_ffprobe = _import_services()
    result = await run_ffprobe(file_path)
    if not result.get("success"):
        return f"Error: {result.get('error', 'Probe failed')}"
    return _format_result(result)


@mcp.tool()
async def video_trim(file_path: str, start_time: float, end_time: float) -> str:
    """Trim a video to a specific time range using stream copy (fast, no re-encoding).

    Args:
        file_path: Absolute path to the source video file.
        start_time: Start time in seconds.
        end_time: End time in seconds.
    """
    execute_operation, _, _ = _import_services()
    workspace = _ensure_workspace()
    result = await execute_operation(
        source_path=file_path,
        operation="trim",
        params={"start_time": start_time, "end_time": end_time},
        output_dir=workspace,
    )
    return _format_result(result)


@mcp.tool()
async def video_resize(
    file_path: str,
    resolution: Optional[str] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
) -> str:
    """Resize a video to a target resolution. Use a preset (720p, 1080p, etc.) or custom dimensions.

    Args:
        file_path: Absolute path to the source video file.
        resolution: Preset resolution: 360p, 480p, 720p, 1080p, 1440p, or 2160p.
        width: Custom width in pixels (alternative to preset).
        height: Custom height in pixels (alternative to preset).
    """
    execute_operation, _, _ = _import_services()
    workspace = _ensure_workspace()
    params: dict = {"keep_aspect_ratio": True}
    if resolution:
        params["resolution"] = resolution
    if width:
        params["width"] = width
    if height:
        params["height"] = height
    result = await execute_operation(file_path, "resize", params, workspace)
    return _format_result(result)


@mcp.tool()
async def video_concat(file_paths: List[str]) -> str:
    """Concatenate multiple videos into one. Videos should have the same codec for best results.

    Args:
        file_paths: List of absolute paths to video files, in the desired order.
    """
    if len(file_paths) < 2:
        return "Error: Need at least 2 files to concatenate"
    execute_operation, _, _ = _import_services()
    workspace = _ensure_workspace()
    result = await execute_operation(
        source_path=file_paths[0],
        operation="concat",
        params={"source_paths": file_paths[1:]},
        output_dir=workspace,
    )
    return _format_result(result)


@mcp.tool()
async def video_add_text(
    file_path: str,
    text: str,
    x: int = 10,
    y: int = 10,
    font_size: int = 24,
    font_color: str = "white",
    start_time: Optional[float] = None,
    end_time: Optional[float] = None,
) -> str:
    """Add text overlay to a video with positioning, font size, color, and optional time range.

    Args:
        file_path: Path to source video.
        text: Text to overlay on the video.
        x: X position in pixels from left edge.
        y: Y position in pixels from top edge.
        font_size: Font size in pixels.
        font_color: Font color name (white, black, red, yellow, blue, green).
        start_time: When to start showing text (seconds). Omit for entire video.
        end_time: When to stop showing text (seconds). Omit for entire video.
    """
    execute_operation, _, _ = _import_services()
    workspace = _ensure_workspace()
    params: dict = {
        "text": text,
        "x": x,
        "y": y,
        "font_size": font_size,
        "font_color": font_color,
    }
    if start_time is not None:
        params["start_time"] = start_time
    if end_time is not None:
        params["end_time"] = end_time
    result = await execute_operation(file_path, "overlay_text", params, workspace)
    return _format_result(result)


@mcp.tool()
async def video_speed(file_path: str, factor: float) -> str:
    """Change video playback speed. Factor > 1 speeds up, < 1 slows down.

    Args:
        file_path: Path to source video.
        factor: Speed multiplier (0.25 to 4.0). Examples: 2.0 = 2x speed, 0.5 = half speed.
    """
    execute_operation, _, _ = _import_services()
    workspace = _ensure_workspace()
    result = await execute_operation(
        file_path, "speed",
        {"factor": factor, "adjust_audio": True},
        workspace,
    )
    return _format_result(result)


@mcp.tool()
async def video_extract_audio(file_path: str) -> str:
    """Extract the audio track from a video file as AAC.

    Args:
        file_path: Path to source video.
    """
    execute_operation, _, _ = _import_services()
    workspace = _ensure_workspace()
    result = await execute_operation(file_path, "audio_extract", {}, workspace)
    return _format_result(result)


@mcp.tool()
async def video_apply_filter(
    file_path: str,
    filter_name: str,
    intensity: float = 1.0,
) -> str:
    """Apply a visual filter to a video.

    Args:
        file_path: Path to source video.
        filter_name: Filter to apply. Options: grayscale, sepia, blur, sharpen, brightness, contrast, saturation.
        intensity: Filter intensity from 0.0 to 2.0. Default 1.0.
    """
    execute_operation, _, _ = _import_services()
    workspace = _ensure_workspace()
    result = await execute_operation(
        file_path, "filter_apply",
        {"filter_name": filter_name, "intensity": intensity},
        workspace,
    )
    return _format_result(result)


@mcp.tool()
async def video_thumbnail(
    file_path: str,
    time: float,
    width: int = 1280,
    height: int = 720,
) -> str:
    """Extract a thumbnail image (JPEG) from a video at a specific time.

    Args:
        file_path: Path to source video.
        time: Time in seconds to capture the thumbnail.
        width: Thumbnail width in pixels.
        height: Thumbnail height in pixels.
    """
    execute_operation, _, _ = _import_services()
    workspace = _ensure_workspace()
    result = await execute_operation(
        file_path, "thumbnail",
        {"time": time, "width": width, "height": height},
        workspace,
    )
    return _format_result(result)


@mcp.tool()
async def video_crop(
    file_path: str,
    x: int,
    y: int,
    width: int,
    height: int,
) -> str:
    """Crop a rectangular region from the video.

    Args:
        file_path: Path to source video.
        x: X offset of crop area (pixels from left).
        y: Y offset of crop area (pixels from top).
        width: Width of crop area in pixels.
        height: Height of crop area in pixels.
    """
    execute_operation, _, _ = _import_services()
    workspace = _ensure_workspace()
    result = await execute_operation(
        file_path, "crop",
        {"x": x, "y": y, "width": width, "height": height},
        workspace,
    )
    return _format_result(result)


@mcp.tool()
async def video_rotate(file_path: str, angle: float) -> str:
    """Rotate a video by a given angle. Common values: 90, 180, 270 degrees.

    Args:
        file_path: Path to source video.
        angle: Rotation angle in degrees (90, 180, 270, or arbitrary).
    """
    execute_operation, _, _ = _import_services()
    workspace = _ensure_workspace()
    result = await execute_operation(
        file_path, "rotate",
        {"angle": angle},
        workspace,
    )
    return _format_result(result)


@mcp.tool()
async def video_add_subtitles(
    file_path: str,
    subtitles: List[dict],
    font_size: int = 20,
) -> str:
    """Burn subtitles into a video. Each subtitle entry needs start time, end time, and text.

    Args:
        file_path: Path to source video.
        subtitles: List of subtitle entries, each with keys: start (seconds), end (seconds), text.
        font_size: Subtitle font size.
    """
    execute_operation, _, _ = _import_services()
    workspace = _ensure_workspace()
    result = await execute_operation(
        file_path, "subtitle",
        {"subtitles": subtitles, "font_size": font_size},
        workspace,
    )
    return _format_result(result)


@mcp.tool()
async def video_export(
    file_path: str,
    format: str = "mp4",
    video_codec: str = "h264",
    audio_codec: str = "aac",
    resolution: Optional[str] = None,
    bitrate: Optional[str] = None,
    fps: Optional[int] = None,
) -> str:
    """Re-encode and export a video with specific codec, format, resolution, and quality settings.

    Args:
        file_path: Path to source video.
        format: Output format: mp4, webm, avi, mov, mkv, or gif.
        video_codec: Video codec: h264, h265, vp9, or av1.
        audio_codec: Audio codec: aac, mp3, opus, or none (to remove audio).
        resolution: Target resolution preset: 360p, 480p, 720p, 1080p, 1440p, 2160p.
        bitrate: Target video bitrate (e.g. '5M', '2500k').
        fps: Target frame rate.
    """
    _, export_video_fn, _ = _import_services()
    workspace = _ensure_workspace()
    result = await export_video_fn(
        source_path=file_path,
        output_dir=workspace,
        format=format,
        video_codec=video_codec,
        audio_codec=audio_codec,
        resolution=resolution,
        bitrate=bitrate,
        fps=fps,
    )
    return _format_result(result)


@mcp.tool()
async def video_watermark(
    file_path: str,
    text: str,
    position: str = "bottom_right",
    opacity: float = 0.5,
) -> str:
    """Add a text watermark to a video.

    Args:
        file_path: Path to source video.
        text: Watermark text (e.g. '(c) My Company').
        position: Position on video: top_left, top_right, bottom_left, bottom_right, or center.
        opacity: Opacity from 0.0 (invisible) to 1.0 (fully opaque).
    """
    execute_operation, _, _ = _import_services()
    workspace = _ensure_workspace()
    result = await execute_operation(
        file_path, "watermark",
        {"text": text, "position": position, "opacity": opacity},
        workspace,
    )
    return _format_result(result)


@mcp.tool()
async def video_adjust_volume(file_path: str, volume: float) -> str:
    """Adjust the audio volume of a video.

    Args:
        file_path: Path to source video.
        volume: Volume multiplier. 0.0 = mute, 1.0 = original, 2.0 = double volume, max 3.0.
    """
    execute_operation, _, _ = _import_services()
    workspace = _ensure_workspace()
    result = await execute_operation(
        file_path, "audio_volume",
        {"volume": volume},
        workspace,
    )
    return _format_result(result)


# ===== Entry Point =====


def main():
    """Entry point for the MCP video editing server."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )

    transport = "stdio"
    port = 8002

    if "--http" in sys.argv:
        transport = "streamable-http"
    if "--port" in sys.argv:
        idx = sys.argv.index("--port")
        if idx + 1 < len(sys.argv):
            port = int(sys.argv[idx + 1])

    logger.info(f"Starting MCP Video Editor server (transport={transport})")

    if transport == "streamable-http":
        mcp.run(transport="streamable-http", host="127.0.0.1", port=port)
    else:
        mcp.run()


if __name__ == "__main__":
    main()
