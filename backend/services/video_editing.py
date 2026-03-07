"""
Video editing service - FFmpeg wrapper for composable video operations.

Provides an async interface for building and executing FFmpeg pipelines
from a declarative list of operations (trim, overlay, concat, etc.).
"""

import asyncio
import json
import logging
import os
import shutil
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.models.video import (
    AudioCodec,
    AudioMixOperation,
    ConcatOperation,
    CropOperation,
    ExtractFramesOperation,
    FilterOperation,
    FilterType,
    RotateOperation,
    ResizeOperation,
    SpeedOperation,
    TextOverlayOperation,
    TextPosition,
    TransitionOperation,
    TrimOperation,
    VideoExportSettings,
    VideoFormat,
    VideoPipeline,
    VideoProbeResult,
    WatermarkOperation,
)

logger = logging.getLogger(__name__)

# Base directory for video processing workspace
VIDEO_WORKSPACE = Path(os.getenv("VIDEO_WORKSPACE", "/tmp/osprey_video"))
VIDEO_WORKSPACE.mkdir(parents=True, exist_ok=True)

# Max file size: 500MB
MAX_FILE_SIZE = 500 * 1024 * 1024


def _get_job_dir(job_id: str) -> Path:
    """Get or create a working directory for a job."""
    job_dir = VIDEO_WORKSPACE / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    return job_dir


def _position_to_ffmpeg(position: TextPosition, pad: int = 20) -> str:
    """Convert TextPosition enum to FFmpeg x:y expression."""
    mapping = {
        TextPosition.top_left: f"x={pad}:y={pad}",
        TextPosition.top_center: f"x=(w-text_w)/2:y={pad}",
        TextPosition.top_right: f"x=w-text_w-{pad}:y={pad}",
        TextPosition.center: "x=(w-text_w)/2:y=(h-text_h)/2",
        TextPosition.bottom_left: f"x={pad}:y=h-text_h-{pad}",
        TextPosition.bottom_center: f"x=(w-text_w)/2:y=h-text_h-{pad}",
        TextPosition.bottom_right: f"x=w-text_w-{pad}:y=h-text_h-{pad}",
    }
    return mapping[position]


def _overlay_position(position: TextPosition, pad: int = 10) -> str:
    """Convert TextPosition to overlay filter position expression."""
    mapping = {
        TextPosition.top_left: f"{pad}:{pad}",
        TextPosition.top_center: f"(W-w)/2:{pad}",
        TextPosition.top_right: f"W-w-{pad}:{pad}",
        TextPosition.center: "(W-w)/2:(H-h)/2",
        TextPosition.bottom_left: f"{pad}:H-h-{pad}",
        TextPosition.bottom_center: f"(W-w)/2:H-h-{pad}",
        TextPosition.bottom_right: f"W-w-{pad}:H-h-{pad}",
    }
    return mapping[position]


async def _run_ffmpeg(args: List[str], timeout: int = 600) -> str:
    """Run an FFmpeg command asynchronously. Returns stderr output."""
    cmd = ["ffmpeg", "-y", "-hide_banner"] + args
    logger.info("Running FFmpeg", extra={"command": " ".join(cmd)})

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        raise RuntimeError(f"FFmpeg timed out after {timeout}s")

    output = stderr.decode("utf-8", errors="replace")

    if proc.returncode != 0:
        logger.error("FFmpeg failed", extra={"returncode": proc.returncode, "stderr": output[-2000:]})
        raise RuntimeError(f"FFmpeg exited with code {proc.returncode}: {output[-500:]}")

    return output


async def _run_ffprobe(file_path: str) -> Dict[str, Any]:
    """Run ffprobe to get video metadata."""
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format", "-show_streams",
        str(file_path),
    ]

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {stderr.decode()}")

    return json.loads(stdout.decode())


async def probe_video(file_path: str) -> VideoProbeResult:
    """Probe a video file and return structured metadata."""
    data = await _run_ffprobe(file_path)

    video_stream = next(
        (s for s in data.get("streams", []) if s["codec_type"] == "video"),
        None,
    )
    audio_stream = next(
        (s for s in data.get("streams", []) if s["codec_type"] == "audio"),
        None,
    )

    if not video_stream:
        raise ValueError("No video stream found in file")

    fmt = data.get("format", {})

    # Parse FPS from r_frame_rate (e.g. "30/1" or "30000/1001")
    fps_parts = video_stream.get("r_frame_rate", "30/1").split("/")
    fps = float(fps_parts[0]) / float(fps_parts[1]) if len(fps_parts) == 2 else 30.0

    return VideoProbeResult(
        duration=float(fmt.get("duration", 0)),
        width=int(video_stream.get("width", 0)),
        height=int(video_stream.get("height", 0)),
        fps=round(fps, 2),
        codec=video_stream.get("codec_name", "unknown"),
        audio_codec=audio_stream.get("codec_name") if audio_stream else None,
        file_size=int(fmt.get("size", 0)),
        bitrate=int(fmt.get("bit_rate", 0)),
    )


def _build_filter_complex(operations: list, input_files: Dict[str, str]) -> tuple:
    """
    Build a filter_complex string from a list of operations.

    Returns (filter_string, list_of_input_args, last_label).
    """
    filters = []
    input_args = []
    current_label = "0:v"
    audio_label = "0:a"
    label_counter = 0

    def next_label():
        nonlocal label_counter
        label_counter += 1
        return f"v{label_counter}"

    for op in operations:
        if isinstance(op, TrimOperation):
            out = next_label()
            out_a = f"a{label_counter}"
            filters.append(f"[{current_label}]trim=start={op.start}:end={op.end},setpts=PTS-STARTPTS[{out}]")
            filters.append(f"[{audio_label}]atrim=start={op.start}:end={op.end},asetpts=PTS-STARTPTS[{out_a}]")
            current_label = out
            audio_label = out_a

        elif isinstance(op, TextOverlayOperation):
            out = next_label()
            pos = _position_to_ffmpeg(op.position)
            text_escaped = op.text.replace("'", "\\'").replace(":", "\\:")
            drawtext = f"drawtext=text='{text_escaped}':fontsize={op.font_size}:fontcolor={op.font_color}:{pos}"
            if op.bg_color:
                drawtext += f":box=1:boxcolor={op.bg_color}:boxborderw=8"
            if op.start is not None:
                enable_expr = f"enable='gte(t,{op.start})"
                if op.duration is not None:
                    enable_expr += f"*lte(t,{op.start + op.duration})"
                enable_expr += "'"
                drawtext += f":{enable_expr}"
            filters.append(f"[{current_label}]{drawtext}[{out}]")
            current_label = out

        elif isinstance(op, SpeedOperation):
            out = next_label()
            out_a = f"a{label_counter}"
            pts_factor = 1.0 / op.factor
            filters.append(f"[{current_label}]setpts={pts_factor}*PTS[{out}]")
            filters.append(f"[{audio_label}]atempo={op.factor}[{out_a}]")
            current_label = out
            audio_label = out_a

        elif isinstance(op, ResizeOperation):
            out = next_label()
            w = op.width or -2
            h = op.height or -2
            if op.maintain_aspect and (op.width and not op.height):
                h = -2
            elif op.maintain_aspect and (op.height and not op.width):
                w = -2
            filters.append(f"[{current_label}]scale={w}:{h}[{out}]")
            current_label = out

        elif isinstance(op, CropOperation):
            out = next_label()
            filters.append(f"[{current_label}]crop={op.width}:{op.height}:{op.x}:{op.y}[{out}]")
            current_label = out

        elif isinstance(op, RotateOperation):
            out = next_label()
            if op.degrees == 90:
                filters.append(f"[{current_label}]transpose=1[{out}]")
            elif op.degrees == 180:
                filters.append(f"[{current_label}]transpose=1,transpose=1[{out}]")
            elif op.degrees == 270:
                filters.append(f"[{current_label}]transpose=2[{out}]")
            else:
                angle_rad = op.degrees * 3.14159265 / 180
                filters.append(f"[{current_label}]rotate={angle_rad}:c=black[{out}]")
            current_label = out

        elif isinstance(op, FilterOperation):
            out = next_label()
            intensity = op.intensity
            filter_map = {
                FilterType.grayscale: "colorchannelmixer=.3:.4:.3:0:.3:.4:.3:0:.3:.4:.3",
                FilterType.sepia: f"colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131",
                FilterType.blur: f"boxblur={int(2 * intensity)}:{int(2 * intensity)}",
                FilterType.sharpen: f"unsharp=5:5:{intensity}:5:5:{intensity}",
                FilterType.brightness: f"eq=brightness={0.1 * intensity}",
                FilterType.contrast: f"eq=contrast={intensity}",
                FilterType.saturation: f"eq=saturation={intensity}",
            }
            filters.append(f"[{current_label}]{filter_map[op.filter_type]}[{out}]")
            current_label = out

        elif isinstance(op, WatermarkOperation):
            if op.image_input not in input_files:
                raise ValueError(f"Watermark image '{op.image_input}' not found in uploaded files")
            idx = len(input_args) // 2 + 1  # next input index
            input_args.extend(["-i", input_files[op.image_input]])
            wm_label = f"{idx}:v"
            scaled = next_label()
            out = next_label()
            filters.append(f"[{wm_label}]scale=iw*{op.scale}:-1,format=rgba,colorchannelmixer=aa={op.opacity}[{scaled}]")
            pos = _overlay_position(op.position)
            filters.append(f"[{current_label}][{scaled}]overlay={pos}[{out}]")
            current_label = out

    return ";".join(filters), input_args, current_label, audio_label


async def execute_pipeline(
    pipeline: VideoPipeline,
    input_files: Dict[str, str],
    job_id: str,
) -> str:
    """
    Execute a video editing pipeline and return the path to the output file.

    Args:
        pipeline: The pipeline definition with operations and export settings.
        input_files: Mapping of input keys to file paths on disk.
        job_id: Unique job identifier for working directory.

    Returns:
        Path to the output file.
    """
    job_dir = _get_job_dir(job_id)

    if pipeline.input_key not in input_files:
        raise ValueError(f"Input key '{pipeline.input_key}' not found in uploaded files")

    primary_input = input_files[pipeline.input_key]
    export = pipeline.export_settings
    ext = export.format.value
    output_name = pipeline.output_filename or f"output_{job_id[:8]}"
    output_path = str(job_dir / f"{output_name}.{ext}")

    # Check for concat operation (special handling)
    concat_ops = [op for op in pipeline.operations if isinstance(op, ConcatOperation)]
    other_ops = [op for op in pipeline.operations if not isinstance(op, ConcatOperation)]
    extract_ops = [op for op in pipeline.operations if isinstance(op, ExtractFramesOperation)]
    audio_mix_ops = [op for op in pipeline.operations if isinstance(op, AudioMixOperation)]

    # Handle extract_frames separately
    if extract_ops:
        return await _execute_extract_frames(extract_ops[0], primary_input, job_dir)

    # Handle concat
    if concat_ops:
        concat_op = concat_ops[0]
        concat_list_file = str(job_dir / "concat_list.txt")
        with open(concat_list_file, "w") as f:
            for key in concat_op.inputs:
                if key not in input_files:
                    raise ValueError(f"Concat input '{key}' not found")
                f.write(f"file '{input_files[key]}'\n")

        if not other_ops:
            # Pure concat with no other filters
            args = [
                "-f", "concat", "-safe", "0",
                "-i", concat_list_file,
                "-c", "copy",
                output_path,
            ]
            await _run_ffmpeg(args)
            return output_path

    # Build filter complex from remaining operations
    filterable_ops = [
        op for op in other_ops
        if not isinstance(op, (AudioMixOperation, ExtractFramesOperation))
    ]

    args = ["-i", primary_input]

    if filterable_ops:
        filter_str, extra_inputs, video_out, audio_out = _build_filter_complex(
            filterable_ops, input_files
        )
        args.extend(extra_inputs)

        if filter_str:
            args.extend(["-filter_complex", filter_str])
            args.extend(["-map", f"[{video_out}]"])
            # Only map audio if we have audio filters
            if any(f"[{audio_out}]" in f for f in filter_str.split(";")):
                args.extend(["-map", f"[{audio_out}]"])
            else:
                args.extend(["-map", "0:a?"])

    # Handle audio mix
    if audio_mix_ops:
        mix = audio_mix_ops[0]
        if mix.audio_input not in input_files:
            raise ValueError(f"Audio input '{mix.audio_input}' not found")
        args.extend(["-i", input_files[mix.audio_input]])
        if mix.replace:
            args.extend(["-map", "0:v", "-map", f"{len(args)//2}:a"])

    # Export settings
    if export.video_codec.value != "copy":
        args.extend(["-c:v", export.video_codec.value])
        args.extend(["-crf", str(export.quality)])
    else:
        args.extend(["-c:v", "copy"])

    if export.audio_codec == AudioCodec.none:
        args.append("-an")
    elif export.audio_codec.value != "copy":
        args.extend(["-c:a", export.audio_codec.value])
    else:
        args.extend(["-c:a", "copy"])

    if export.fps:
        args.extend(["-r", str(export.fps)])

    # Pixel format for broad compatibility
    if export.video_codec.value in ("libx264", "libx265"):
        args.extend(["-pix_fmt", "yuv420p"])

    args.append(output_path)
    await _run_ffmpeg(args)

    logger.info("Pipeline completed", extra={"job_id": job_id, "output": output_path})
    return output_path


async def _execute_extract_frames(
    op: ExtractFramesOperation,
    input_path: str,
    job_dir: Path,
) -> str:
    """Extract frames from a video as images."""
    frames_dir = job_dir / "frames"
    frames_dir.mkdir(exist_ok=True)

    if op.timestamps:
        paths = []
        for i, ts in enumerate(op.timestamps):
            out = str(frames_dir / f"frame_{i:04d}.{op.format}")
            await _run_ffmpeg([
                "-ss", str(ts),
                "-i", input_path,
                "-frames:v", "1",
                out,
            ])
            paths.append(out)
        return str(frames_dir)
    elif op.interval:
        out_pattern = str(frames_dir / f"frame_%04d.{op.format}")
        await _run_ffmpeg([
            "-i", input_path,
            "-vf", f"fps=1/{op.interval}",
            out_pattern,
        ])
        return str(frames_dir)
    else:
        raise ValueError("Either timestamps or interval must be provided")


async def generate_thumbnail(input_path: str, job_id: str, time: float = 1.0) -> str:
    """Generate a thumbnail from a specific timestamp."""
    job_dir = _get_job_dir(job_id)
    output = str(job_dir / "thumbnail.jpg")
    await _run_ffmpeg([
        "-ss", str(time),
        "-i", input_path,
        "-frames:v", "1",
        "-q:v", "2",
        output,
    ])
    return output


def cleanup_job(job_id: str) -> None:
    """Remove all temporary files for a job."""
    job_dir = VIDEO_WORKSPACE / job_id
    if job_dir.exists():
        shutil.rmtree(job_dir)
        logger.info("Cleaned up job directory", extra={"job_id": job_id})
