"""
Pydantic models for video editing operations.

Defines the schema for video editing pipelines that can be composed
from individual operations (trim, overlay, concatenate, etc.).
"""

from enum import Enum
from typing import List, Optional, Union
from pydantic import BaseModel, Field


class VideoFormat(str, Enum):
    mp4 = "mp4"
    webm = "webm"
    mov = "mov"
    avi = "avi"
    mkv = "mkv"
    gif = "gif"


class VideoCodec(str, Enum):
    h264 = "libx264"
    h265 = "libx265"
    vp9 = "libvpx-vp9"
    copy = "copy"


class AudioCodec(str, Enum):
    aac = "aac"
    mp3 = "libmp3lame"
    opus = "libopus"
    copy = "copy"
    none = "none"


class TextPosition(str, Enum):
    top_left = "top_left"
    top_center = "top_center"
    top_right = "top_right"
    center = "center"
    bottom_left = "bottom_left"
    bottom_center = "bottom_center"
    bottom_right = "bottom_right"


class TransitionType(str, Enum):
    fade = "fade"
    dissolve = "dissolve"
    wipe_left = "wipe_left"
    wipe_right = "wipe_right"


class FilterType(str, Enum):
    grayscale = "grayscale"
    sepia = "sepia"
    blur = "blur"
    sharpen = "sharpen"
    brightness = "brightness"
    contrast = "contrast"
    saturation = "saturation"


# --- Individual operation models ---


class TrimOperation(BaseModel):
    """Trim a video segment by start/end time in seconds."""
    type: str = "trim"
    start: float = Field(ge=0, description="Start time in seconds")
    end: float = Field(ge=0, description="End time in seconds")


class ConcatOperation(BaseModel):
    """Concatenate multiple input files."""
    type: str = "concat"
    inputs: List[str] = Field(min_length=2, description="List of input file keys to concatenate")


class TextOverlayOperation(BaseModel):
    """Add text overlay to video."""
    type: str = "text_overlay"
    text: str = Field(min_length=1, max_length=500)
    position: TextPosition = TextPosition.bottom_center
    font_size: int = Field(default=24, ge=8, le=200)
    font_color: str = Field(default="white")
    bg_color: Optional[str] = Field(default=None, description="Background box color, e.g. 'black@0.5'")
    start: Optional[float] = Field(default=None, ge=0, description="Show text starting at this time")
    duration: Optional[float] = Field(default=None, gt=0, description="Duration to show text")


class SpeedOperation(BaseModel):
    """Change playback speed."""
    type: str = "speed"
    factor: float = Field(gt=0.1, le=10.0, description="Speed multiplier (0.5 = half speed, 2.0 = double)")


class ResizeOperation(BaseModel):
    """Resize video to target dimensions."""
    type: str = "resize"
    width: Optional[int] = Field(default=None, ge=16, le=7680)
    height: Optional[int] = Field(default=None, ge=16, le=4320)
    maintain_aspect: bool = True


class CropOperation(BaseModel):
    """Crop video to a region."""
    type: str = "crop"
    x: int = Field(ge=0)
    y: int = Field(ge=0)
    width: int = Field(gt=0)
    height: int = Field(gt=0)


class RotateOperation(BaseModel):
    """Rotate video by degrees."""
    type: str = "rotate"
    degrees: int = Field(description="Rotation in degrees (90, 180, 270)")


class FilterOperation(BaseModel):
    """Apply a visual filter."""
    type: str = "filter"
    filter_type: FilterType
    intensity: float = Field(default=1.0, ge=0.0, le=5.0)


class AudioMixOperation(BaseModel):
    """Mix an audio track into the video."""
    type: str = "audio_mix"
    audio_input: str = Field(description="Key of the uploaded audio file")
    volume: float = Field(default=1.0, ge=0.0, le=3.0)
    start: float = Field(default=0.0, ge=0, description="Start time to insert audio")
    replace: bool = Field(default=False, description="Replace original audio entirely")


class TransitionOperation(BaseModel):
    """Add transition between two clips."""
    type: str = "transition"
    transition_type: TransitionType = TransitionType.fade
    duration: float = Field(default=1.0, gt=0, le=5.0, description="Transition duration in seconds")


class ExtractFramesOperation(BaseModel):
    """Extract frames as images."""
    type: str = "extract_frames"
    timestamps: Optional[List[float]] = Field(default=None, description="Specific timestamps in seconds")
    interval: Optional[float] = Field(default=None, gt=0, description="Extract a frame every N seconds")
    format: str = Field(default="png", pattern="^(png|jpg)$")


class WatermarkOperation(BaseModel):
    """Add an image watermark overlay."""
    type: str = "watermark"
    image_input: str = Field(description="Key of the uploaded watermark image")
    position: TextPosition = TextPosition.bottom_right
    opacity: float = Field(default=0.5, ge=0.0, le=1.0)
    scale: float = Field(default=0.15, gt=0, le=1.0, description="Scale relative to video size")


# Union of all operations
VideoOperation = Union[
    TrimOperation,
    ConcatOperation,
    TextOverlayOperation,
    SpeedOperation,
    ResizeOperation,
    CropOperation,
    RotateOperation,
    FilterOperation,
    AudioMixOperation,
    TransitionOperation,
    ExtractFramesOperation,
    WatermarkOperation,
]


# --- Pipeline models ---


class VideoExportSettings(BaseModel):
    """Export/encoding settings for the output."""
    format: VideoFormat = VideoFormat.mp4
    video_codec: VideoCodec = VideoCodec.h264
    audio_codec: AudioCodec = AudioCodec.aac
    quality: int = Field(default=23, ge=0, le=51, description="CRF value (lower = better quality)")
    fps: Optional[int] = Field(default=None, ge=1, le=120)
    max_width: Optional[int] = Field(default=None, ge=16, le=7680)
    max_height: Optional[int] = Field(default=None, ge=16, le=4320)


class VideoPipeline(BaseModel):
    """
    A composable video editing pipeline.

    Operations are applied sequentially to the input video.
    """
    input_key: str = Field(description="Key of the primary uploaded video file")
    operations: List[VideoOperation] = Field(min_length=1, description="Ordered list of operations to apply")
    export_settings: VideoExportSettings = Field(default_factory=VideoExportSettings)
    output_filename: Optional[str] = Field(default=None, description="Custom output filename (without extension)")


class VideoProjectCreate(BaseModel):
    """Create a new video editing project."""
    name: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)


class VideoProjectUpdate(BaseModel):
    """Update a video project."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    pipeline: Optional[VideoPipeline] = None


class VideoJobStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class VideoJobResponse(BaseModel):
    """Response for a submitted video editing job."""
    job_id: str
    project_id: str
    status: VideoJobStatus
    progress: float = Field(default=0.0, ge=0.0, le=100.0)
    output_url: Optional[str] = None
    error: Optional[str] = None


class VideoProbeResult(BaseModel):
    """Result of probing a video file for metadata."""
    duration: float
    width: int
    height: int
    fps: float
    codec: str
    audio_codec: Optional[str] = None
    file_size: int
    bitrate: int
