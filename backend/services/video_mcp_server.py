"""
MCP (Model Context Protocol) Server for Video Editing.

Exposes video editing tools via the MCP protocol so that Claude Code
and other MCP-compatible clients can edit videos through natural language.

Usage:
    # stdio transport (for Claude Code integration)
    python -m backend.services.video_mcp_server

    # Or add to Claude Code MCP config (~/.claude/mcp.json):
    {
        "mcpServers": {
            "video-editor": {
                "command": "python",
                "args": ["-m", "backend.services.video_mcp_server"],
                "cwd": "/path/to/camada-osprey-core"
            }
        }
    }
"""

import asyncio
import json
import logging
import os
import sys
import uuid
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# MCP protocol constants
JSONRPC_VERSION = "2.0"
MCP_PROTOCOL_VERSION = "2024-11-05"

# Video workspace directory
WORKSPACE_DIR = os.getenv("VIDEO_WORKSPACE_DIR", "/tmp/osprey_mcp_videos")


def _ensure_workspace() -> str:
    """Create and return the workspace directory."""
    os.makedirs(WORKSPACE_DIR, exist_ok=True)
    return WORKSPACE_DIR


# ===== Tool Definitions =====

TOOLS = [
    {
        "name": "video_probe",
        "description": "Analyze a video file and return metadata (duration, resolution, codecs, fps, file size).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Absolute path to the video file to analyze.",
                }
            },
            "required": ["file_path"],
        },
    },
    {
        "name": "video_trim",
        "description": "Trim a video to a specific time range. Returns the path to the trimmed output file.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Absolute path to the source video file.",
                },
                "start_time": {
                    "type": "number",
                    "description": "Start time in seconds.",
                },
                "end_time": {
                    "type": "number",
                    "description": "End time in seconds.",
                },
            },
            "required": ["file_path", "start_time", "end_time"],
        },
    },
    {
        "name": "video_resize",
        "description": "Resize a video to a target resolution. Supports presets (720p, 1080p, etc.) or custom width/height.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Absolute path to the source video file.",
                },
                "resolution": {
                    "type": "string",
                    "description": "Preset resolution: 360p, 480p, 720p, 1080p, 1440p, 2160p.",
                },
                "width": {
                    "type": "integer",
                    "description": "Custom width in pixels (alternative to resolution preset).",
                },
                "height": {
                    "type": "integer",
                    "description": "Custom height in pixels (alternative to resolution preset).",
                },
            },
            "required": ["file_path"],
        },
    },
    {
        "name": "video_concat",
        "description": "Concatenate multiple videos into one. All videos should have the same codec for stream copy.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_paths": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of absolute paths to video files, in order.",
                }
            },
            "required": ["file_paths"],
        },
    },
    {
        "name": "video_add_text",
        "description": "Add text overlay to a video. Supports positioning, font size, color, and time range.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to source video."},
                "text": {"type": "string", "description": "Text to overlay."},
                "x": {"type": "integer", "description": "X position in pixels.", "default": 10},
                "y": {"type": "integer", "description": "Y position in pixels.", "default": 10},
                "font_size": {"type": "integer", "description": "Font size.", "default": 24},
                "font_color": {"type": "string", "description": "Font color name.", "default": "white"},
                "start_time": {"type": "number", "description": "When to start showing text (seconds)."},
                "end_time": {"type": "number", "description": "When to stop showing text (seconds)."},
            },
            "required": ["file_path", "text"],
        },
    },
    {
        "name": "video_speed",
        "description": "Change video playback speed. Factor > 1 speeds up, < 1 slows down.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to source video."},
                "factor": {
                    "type": "number",
                    "description": "Speed multiplier (0.25 to 4.0). 2.0 = 2x speed, 0.5 = half speed.",
                },
            },
            "required": ["file_path", "factor"],
        },
    },
    {
        "name": "video_extract_audio",
        "description": "Extract audio track from a video file as AAC.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to source video."},
            },
            "required": ["file_path"],
        },
    },
    {
        "name": "video_apply_filter",
        "description": "Apply a visual filter to a video. Available filters: grayscale, sepia, blur, sharpen, brightness, contrast, saturation.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to source video."},
                "filter_name": {
                    "type": "string",
                    "description": "Filter name: grayscale, sepia, blur, sharpen, brightness, contrast, saturation.",
                },
                "intensity": {
                    "type": "number",
                    "description": "Filter intensity from 0.0 to 2.0. Default 1.0.",
                    "default": 1.0,
                },
            },
            "required": ["file_path", "filter_name"],
        },
    },
    {
        "name": "video_thumbnail",
        "description": "Extract a thumbnail image from a video at a specific time.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to source video."},
                "time": {"type": "number", "description": "Time in seconds to capture thumbnail."},
                "width": {"type": "integer", "description": "Thumbnail width.", "default": 1280},
                "height": {"type": "integer", "description": "Thumbnail height.", "default": 720},
            },
            "required": ["file_path", "time"],
        },
    },
    {
        "name": "video_crop",
        "description": "Crop a region from the video.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to source video."},
                "x": {"type": "integer", "description": "X offset of crop area."},
                "y": {"type": "integer", "description": "Y offset of crop area."},
                "width": {"type": "integer", "description": "Width of crop area."},
                "height": {"type": "integer", "description": "Height of crop area."},
            },
            "required": ["file_path", "x", "y", "width", "height"],
        },
    },
    {
        "name": "video_rotate",
        "description": "Rotate a video by a given angle (90, 180, 270 degrees, or arbitrary).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to source video."},
                "angle": {"type": "number", "description": "Rotation angle in degrees."},
            },
            "required": ["file_path", "angle"],
        },
    },
    {
        "name": "video_add_subtitles",
        "description": "Burn subtitles into a video.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to source video."},
                "subtitles": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "start": {"type": "number"},
                            "end": {"type": "number"},
                            "text": {"type": "string"},
                        },
                    },
                    "description": "List of subtitle entries with start, end (seconds), and text.",
                },
                "font_size": {"type": "integer", "default": 20},
            },
            "required": ["file_path", "subtitles"],
        },
    },
    {
        "name": "video_export",
        "description": "Re-encode/export a video with specific codec, format, resolution, and bitrate settings.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to source video."},
                "format": {
                    "type": "string",
                    "description": "Output format: mp4, webm, avi, mov, mkv, gif.",
                    "default": "mp4",
                },
                "video_codec": {
                    "type": "string",
                    "description": "Video codec: h264, h265, vp9, av1.",
                    "default": "h264",
                },
                "audio_codec": {
                    "type": "string",
                    "description": "Audio codec: aac, mp3, opus, none.",
                    "default": "aac",
                },
                "resolution": {
                    "type": "string",
                    "description": "Target resolution preset (720p, 1080p, etc.).",
                },
                "bitrate": {
                    "type": "string",
                    "description": "Target video bitrate (e.g. '5M', '2500k').",
                },
                "fps": {"type": "integer", "description": "Target frame rate."},
            },
            "required": ["file_path"],
        },
    },
    {
        "name": "video_watermark",
        "description": "Add a text watermark to a video.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to source video."},
                "text": {"type": "string", "description": "Watermark text."},
                "position": {
                    "type": "string",
                    "description": "Position: top_left, top_right, bottom_left, bottom_right, center.",
                    "default": "bottom_right",
                },
                "opacity": {
                    "type": "number",
                    "description": "Opacity from 0.0 to 1.0.",
                    "default": 0.5,
                },
            },
            "required": ["file_path", "text"],
        },
    },
    {
        "name": "video_adjust_volume",
        "description": "Adjust the audio volume of a video. 0 = mute, 1 = original, 2 = double.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to source video."},
                "volume": {
                    "type": "number",
                    "description": "Volume multiplier (0.0 to 3.0).",
                },
            },
            "required": ["file_path", "volume"],
        },
    },
]


# ===== Tool Handlers =====


async def _handle_tool(name: str, arguments: dict) -> dict:
    """Route a tool call to the appropriate handler and return the result."""
    # Import here to avoid circular imports at module level
    from backend.services.video_editing import (
        execute_operation,
        export_video,
        run_ffprobe,
    )

    workspace = _ensure_workspace()
    file_path = arguments.get("file_path", "")

    if name == "video_probe":
        result = await run_ffprobe(file_path)
        if not result.get("success"):
            return {"error": result.get("error", "Probe failed")}
        return result

    elif name == "video_trim":
        return await execute_operation(
            source_path=file_path,
            operation="trim",
            params={
                "start_time": arguments["start_time"],
                "end_time": arguments["end_time"],
            },
            output_dir=workspace,
        )

    elif name == "video_resize":
        params = {}
        if arguments.get("resolution"):
            params["resolution"] = arguments["resolution"]
        if arguments.get("width"):
            params["width"] = arguments["width"]
        if arguments.get("height"):
            params["height"] = arguments["height"]
        params["keep_aspect_ratio"] = True
        return await execute_operation(file_path, "resize", params, workspace)

    elif name == "video_concat":
        paths = arguments.get("file_paths", [])
        if len(paths) < 2:
            return {"success": False, "error": "Need at least 2 files to concatenate"}
        return await execute_operation(
            source_path=paths[0],
            operation="concat",
            params={"source_paths": paths[1:]},
            output_dir=workspace,
        )

    elif name == "video_add_text":
        params = {
            "text": arguments["text"],
            "x": arguments.get("x", 10),
            "y": arguments.get("y", 10),
            "font_size": arguments.get("font_size", 24),
            "font_color": arguments.get("font_color", "white"),
        }
        if arguments.get("start_time") is not None:
            params["start_time"] = arguments["start_time"]
        if arguments.get("end_time") is not None:
            params["end_time"] = arguments["end_time"]
        return await execute_operation(file_path, "overlay_text", params, workspace)

    elif name == "video_speed":
        return await execute_operation(
            file_path, "speed",
            {"factor": arguments["factor"], "adjust_audio": True},
            workspace,
        )

    elif name == "video_extract_audio":
        return await execute_operation(file_path, "audio_extract", {}, workspace)

    elif name == "video_apply_filter":
        return await execute_operation(
            file_path, "filter_apply",
            {
                "filter_name": arguments["filter_name"],
                "intensity": arguments.get("intensity", 1.0),
            },
            workspace,
        )

    elif name == "video_thumbnail":
        return await execute_operation(
            file_path, "thumbnail",
            {
                "time": arguments["time"],
                "width": arguments.get("width", 1280),
                "height": arguments.get("height", 720),
            },
            workspace,
        )

    elif name == "video_crop":
        return await execute_operation(
            file_path, "crop",
            {
                "x": arguments["x"],
                "y": arguments["y"],
                "width": arguments["width"],
                "height": arguments["height"],
            },
            workspace,
        )

    elif name == "video_rotate":
        return await execute_operation(
            file_path, "rotate",
            {"angle": arguments["angle"]},
            workspace,
        )

    elif name == "video_add_subtitles":
        return await execute_operation(
            file_path, "subtitle",
            {
                "subtitles": arguments["subtitles"],
                "font_size": arguments.get("font_size", 20),
            },
            workspace,
        )

    elif name == "video_export":
        return await export_video(
            source_path=file_path,
            output_dir=workspace,
            format=arguments.get("format", "mp4"),
            video_codec=arguments.get("video_codec", "h264"),
            audio_codec=arguments.get("audio_codec", "aac"),
            resolution=arguments.get("resolution"),
            bitrate=arguments.get("bitrate"),
            fps=arguments.get("fps"),
        )

    elif name == "video_watermark":
        return await execute_operation(
            file_path, "watermark",
            {
                "text": arguments["text"],
                "position": arguments.get("position", "bottom_right"),
                "opacity": arguments.get("opacity", 0.5),
            },
            workspace,
        )

    elif name == "video_adjust_volume":
        return await execute_operation(
            file_path, "audio_volume",
            {"volume": arguments["volume"]},
            workspace,
        )

    else:
        return {"error": f"Unknown tool: {name}"}


# ===== MCP Protocol (JSON-RPC over stdio) =====


class MCPVideoServer:
    """Minimal MCP server implementing the Model Context Protocol over stdio."""

    def __init__(self):
        self.server_info = {
            "name": "osprey-video-editor",
            "version": "1.0.0",
        }

    async def handle_message(self, message: dict) -> dict | None:
        """Process a single JSON-RPC message and return a response."""
        method = message.get("method")
        msg_id = message.get("id")
        params = message.get("params", {})

        # Notifications (no id) don't get a response
        if msg_id is None:
            if method == "notifications/initialized":
                logger.info("MCP client initialized")
            return None

        if method == "initialize":
            return self._response(msg_id, {
                "protocolVersion": MCP_PROTOCOL_VERSION,
                "capabilities": {
                    "tools": {"listChanged": False},
                },
                "serverInfo": self.server_info,
            })

        elif method == "tools/list":
            return self._response(msg_id, {"tools": TOOLS})

        elif method == "tools/call":
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})

            try:
                result = await _handle_tool(tool_name, arguments)
                text = json.dumps(result, indent=2, default=str)
                is_error = not result.get("success", True) if isinstance(result, dict) else False

                return self._response(msg_id, {
                    "content": [{"type": "text", "text": text}],
                    "isError": is_error,
                })

            except Exception as e:
                logger.error(f"Tool execution error: {e}")
                return self._response(msg_id, {
                    "content": [{"type": "text", "text": f"Error: {str(e)}"}],
                    "isError": True,
                })

        elif method == "ping":
            return self._response(msg_id, {})

        else:
            return self._error_response(msg_id, -32601, f"Method not found: {method}")

    def _response(self, msg_id: Any, result: dict) -> dict:
        return {"jsonrpc": JSONRPC_VERSION, "id": msg_id, "result": result}

    def _error_response(self, msg_id: Any, code: int, message: str) -> dict:
        return {
            "jsonrpc": JSONRPC_VERSION,
            "id": msg_id,
            "error": {"code": code, "message": message},
        }


async def run_stdio_server():
    """Run the MCP server over stdio transport."""
    server = MCPVideoServer()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, sys.stdin.buffer)

    writer_transport, writer_protocol = await asyncio.get_event_loop().connect_write_pipe(
        asyncio.streams.FlowControlMixin, sys.stdout.buffer
    )
    writer = asyncio.StreamWriter(writer_transport, writer_protocol, None, asyncio.get_event_loop())

    logger.info("MCP Video Editor server started (stdio)")

    buffer = b""

    while True:
        try:
            chunk = await reader.read(4096)
            if not chunk:
                break

            buffer += chunk

            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                line = line.strip()
                if not line:
                    continue

                try:
                    message = json.loads(line.decode("utf-8"))
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON received: {line[:200]}")
                    continue

                response = await server.handle_message(message)
                if response is not None:
                    response_bytes = json.dumps(response).encode("utf-8") + b"\n"
                    writer.write(response_bytes)
                    await writer.drain()

        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Server error: {e}")
            break

    logger.info("MCP Video Editor server stopped")


def main():
    """Entry point for the MCP server."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,  # Log to stderr to keep stdout clean for MCP protocol
    )
    asyncio.run(run_stdio_server())


if __name__ == "__main__":
    main()
