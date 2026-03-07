---
name: video-editing
description: Edit videos programmatically using FFmpeg operations (trim, resize, crop, rotate, filters, text overlay, watermark, subtitles, audio) and Remotion (React-based video generation). Use when the user wants to process, transform, or create videos.
allowed-tools: Read, Grep, Glob, Bash
---

# Video Editing Skill for Claude Code

## Overview

This skill enables Claude Code to edit videos programmatically using the Osprey Video Editing Framework. You have access to FFmpeg-based video processing and Remotion-based programmatic video generation.

## Available Tools

### MCP Server (Direct FFmpeg)

Configure in `~/.claude/mcp.json`:
```json
{
  "mcpServers": {
    "video-editor": {
      "command": "python",
      "args": ["-m", "backend.services.video_mcp_server"],
      "cwd": "/path/to/camada-osprey-core"
    }
  }
}
```

### REST API Endpoints

Base URL: `http://localhost:8001/api/video`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/projects` | Create a video editing project |
| GET | `/projects` | List all projects |
| GET | `/projects/{id}` | Get project details |
| DELETE | `/projects/{id}` | Delete project and files |
| POST | `/projects/{id}/sources` | Upload source video |
| GET | `/projects/{id}/sources/{sid}/probe` | Get video metadata |
| POST | `/projects/{id}/operations` | Apply an editing operation |
| POST | `/projects/{id}/export` | Export with encoding settings |
| GET | `/projects/{id}/download/{sid}` | Download file |
| GET | `/capabilities` | List all capabilities |

## Supported Operations

When using the `/projects/{id}/operations` endpoint, these operations are available:

### Cutting & Arranging
- **trim**: Cut a segment → `{ "start_time": 5.0, "end_time": 15.0 }`
- **concat**: Join videos → `{ "source_ids": ["id1", "id2"] }`

### Transform
- **resize**: Change resolution → `{ "resolution": "1080p" }` or `{ "width": 1280, "height": 720 }`
- **crop**: Crop region → `{ "x": 0, "y": 0, "width": 1280, "height": 720 }`
- **rotate**: Rotate → `{ "angle": 90 }`
- **speed**: Change speed → `{ "factor": 2.0 }` (0.25x to 4x)

### Overlays
- **overlay_text**: Add text → `{ "text": "Hello", "x": 10, "y": 10, "font_size": 24, "font_color": "white" }`
- **watermark**: Add watermark → `{ "text": "Draft", "position": "bottom_right", "opacity": 0.5 }`
- **subtitle**: Burn subtitles → `{ "subtitles": [{"start": 0, "end": 5, "text": "Hello"}] }`

### Audio
- **audio_extract**: Extract audio track
- **audio_replace**: Replace audio → `{ "audio_source_id": "id" }`
- **audio_volume**: Adjust volume → `{ "volume": 1.5 }`

### Filters
- **filter_apply**: Apply filter → `{ "filter_name": "grayscale", "intensity": 1.0 }`
  - Available: grayscale, sepia, blur, sharpen, brightness, contrast, saturation

### Export
- **thumbnail**: Extract frame → `{ "time": 5.0, "width": 1280, "height": 720 }`

## Workflow Example

```bash
# 1. Create project
curl -X POST http://localhost:8001/api/video/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "My Video"}'

# 2. Upload source video
curl -X POST http://localhost:8001/api/video/projects/{project_id}/sources \
  -F "file=@input.mp4"

# 3. Trim to 10-30 seconds
curl -X POST http://localhost:8001/api/video/projects/{project_id}/operations \
  -H "Content-Type: application/json" \
  -d '{"source_id": "{source_id}", "operation": "trim", "params": {"start_time": 10, "end_time": 30}}'

# 4. Add title text
curl -X POST http://localhost:8001/api/video/projects/{project_id}/operations \
  -H "Content-Type: application/json" \
  -d '{"source_id": "{output_source_id}", "operation": "overlay_text", "params": {"text": "My Title", "x": 100, "y": 50, "font_size": 48}}'

# 5. Export as 1080p MP4
curl -X POST http://localhost:8001/api/video/projects/{project_id}/export \
  -H "Content-Type: application/json" \
  -d '{"format": "mp4", "video_codec": "h264", "resolution": "1080p"}'
```

## Remotion (Programmatic Video Generation)

For creating videos from code (animations, data visualizations, slideshows):

### Templates Available
- **blank**: Empty canvas with customizable title
- **text-animation**: Animated title + subtitle with spring physics
- **slideshow**: Image slideshow with transitions
- **lower-third**: Broadcast-style name/title overlay
- **countdown**: Animated countdown timer

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/video/remotion/templates` | List templates |
| POST | `/api/video/remotion/projects` | Create project from template |
| POST | `/api/video/remotion/projects/{id}/install` | Install npm deps |
| POST | `/api/video/remotion/projects/{id}/render` | Render to video |

## Prerequisites

- **ffmpeg** must be installed: `apt-get install ffmpeg` or `brew install ffmpeg`
- **Node.js 18+** for Remotion features: `nvm install 18`
- **Backend running** on port 8001: `cd backend && python3 server.py`

## File Structure

```
backend/
├── api/video_editing.py         # REST API endpoints
├── models/video_editing.py      # Pydantic schemas
├── services/
│   ├── video_editing.py         # FFmpeg processing engine
│   ├── video_mcp_server.py      # MCP server for Claude Code
│   └── video_remotion.py        # Remotion integration
└── video_templates/             # Remotion project templates
```
