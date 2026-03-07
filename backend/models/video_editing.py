import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class VideoFormat(str, Enum):
    mp4 = "mp4"
    webm = "webm"
    avi = "avi"
    mov = "mov"
    mkv = "mkv"
    gif = "gif"


class VideoCodec(str, Enum):
    h264 = "h264"
    h265 = "h265"
    vp9 = "vp9"
    av1 = "av1"


class AudioCodec(str, Enum):
    aac = "aac"
    mp3 = "mp3"
    opus = "opus"
    none = "none"


class VideoResolution(str, Enum):
    r360p = "360p"
    r480p = "480p"
    r720p = "720p"
    r1080p = "1080p"
    r1440p = "1440p"
    r2160p = "2160p"
    custom = "custom"


class ProjectStatus(str, Enum):
    created = "created"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class OperationType(str, Enum):
    trim = "trim"
    concat = "concat"
    overlay_text = "overlay_text"
    overlay_image = "overlay_image"
    resize = "resize"
    crop = "crop"
    rotate = "rotate"
    speed = "speed"
    audio_extract = "audio_extract"
    audio_replace = "audio_replace"
    audio_volume = "audio_volume"
    filter_apply = "filter_apply"
    thumbnail = "thumbnail"
    watermark = "watermark"
    transition = "transition"
    subtitle = "subtitle"


RESOLUTION_MAP = {
    VideoResolution.r360p: (640, 360),
    VideoResolution.r480p: (854, 480),
    VideoResolution.r720p: (1280, 720),
    VideoResolution.r1080p: (1920, 1080),
    VideoResolution.r1440p: (2560, 1440),
    VideoResolution.r2160p: (3840, 2160),
}


class TrimParams(BaseModel):
    start_time: float = Field(..., description="Start time in seconds")
    end_time: float = Field(..., description="End time in seconds")


class ConcatParams(BaseModel):
    source_ids: List[str] = Field(..., description="List of source video IDs to concatenate")


class OverlayTextParams(BaseModel):
    text: str
    x: int = 10
    y: int = 10
    font_size: int = 24
    font_color: str = "white"
    bg_color: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None


class OverlayImageParams(BaseModel):
    image_path: str
    x: int = 0
    y: int = 0
    width: Optional[int] = None
    height: Optional[int] = None
    opacity: float = 1.0
    start_time: Optional[float] = None
    end_time: Optional[float] = None


class ResizeParams(BaseModel):
    resolution: Optional[VideoResolution] = None
    width: Optional[int] = None
    height: Optional[int] = None
    keep_aspect_ratio: bool = True


class CropParams(BaseModel):
    x: int
    y: int
    width: int
    height: int


class RotateParams(BaseModel):
    angle: float = Field(..., description="Rotation angle in degrees")


class SpeedParams(BaseModel):
    factor: float = Field(..., ge=0.25, le=4.0, description="Speed multiplier (0.25x to 4x)")
    adjust_audio: bool = True


class AudioVolumeParams(BaseModel):
    volume: float = Field(..., ge=0.0, le=3.0, description="Volume multiplier (0=mute, 1=normal)")


class AudioReplaceParams(BaseModel):
    audio_source_id: str = Field(..., description="ID of audio file to use")
    start_time: Optional[float] = None


class FilterParams(BaseModel):
    filter_name: str = Field(..., description="Filter name: grayscale, sepia, blur, sharpen, brightness, contrast, saturation")
    intensity: float = Field(default=1.0, ge=0.0, le=2.0)


class ThumbnailParams(BaseModel):
    time: float = Field(..., description="Time in seconds to extract thumbnail")
    width: Optional[int] = 1280
    height: Optional[int] = 720


class WatermarkParams(BaseModel):
    text: Optional[str] = None
    image_path: Optional[str] = None
    position: str = Field(default="bottom_right", description="top_left, top_right, bottom_left, bottom_right, center")
    opacity: float = 0.5
    scale: float = 0.15


class TransitionParams(BaseModel):
    transition_type: str = Field(default="fade", description="fade, dissolve, wipe, slide")
    duration: float = Field(default=1.0, ge=0.1, le=5.0)


class SubtitleParams(BaseModel):
    subtitles: List[Dict[str, Any]] = Field(
        ...,
        description="List of {start: float, end: float, text: str} entries"
    )
    font_size: int = 20
    font_color: str = "white"
    bg_color: str = "black@0.5"
    position: str = "bottom"


class VideoOperation(BaseModel):
    operation: OperationType
    params: Dict[str, Any] = {}


class VideoProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None


class VideoProjectResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    status: ProjectStatus
    sources: List[Dict[str, Any]] = []
    operations: List[Dict[str, Any]] = []
    output: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class VideoOperationRequest(BaseModel):
    source_id: str = Field(..., description="ID of the source video to operate on")
    operation: OperationType
    params: Dict[str, Any] = {}


class VideoExportRequest(BaseModel):
    format: VideoFormat = VideoFormat.mp4
    video_codec: VideoCodec = VideoCodec.h264
    audio_codec: AudioCodec = AudioCodec.aac
    resolution: Optional[VideoResolution] = None
    bitrate: Optional[str] = None
    fps: Optional[int] = None


class VideoProbeResponse(BaseModel):
    filename: str
    duration: float
    width: int
    height: int
    fps: float
    video_codec: str
    audio_codec: Optional[str] = None
    bitrate: Optional[int] = None
    file_size: int
    format: str
