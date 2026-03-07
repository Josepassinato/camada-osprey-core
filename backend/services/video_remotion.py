"""
Remotion Integration Service for Programmatic Video Generation.

This service enables creating videos programmatically using Remotion
(React-based video framework). It handles:
- Project scaffolding from templates
- Composition configuration
- CLI-based rendering
- Template management

Prerequisites:
    - Node.js 18+ installed
    - npx available in PATH
    - ffmpeg installed (for post-processing)

Usage:
    from backend.services.video_remotion import (
        create_remotion_project,
        render_composition,
        list_templates,
    )

    # Create a project from template
    project = await create_remotion_project(
        project_name="my-video",
        template="blank",
        output_dir="/tmp/videos",
    )

    # Render a composition
    result = await render_composition(
        project_dir=project["project_dir"],
        composition_id="MainVideo",
        output_path="/tmp/videos/output.mp4",
        props={"title": "Hello World", "color": "#ff0000"},
    )
"""

import asyncio
import json
import logging
import os
import shutil
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

REMOTION_TEMPLATES_DIR = os.getenv(
    "REMOTION_TEMPLATES_DIR",
    os.path.join(os.path.dirname(__file__), "..", "video_templates"),
)

REMOTION_WORKSPACE = os.getenv("REMOTION_WORKSPACE", "/tmp/osprey_remotion")


# ===== Template Definitions =====

BUILTIN_TEMPLATES = {
    "blank": {
        "name": "Blank",
        "description": "Empty Remotion project with a single composition.",
        "compositions": ["Main"],
    },
    "text-animation": {
        "name": "Text Animation",
        "description": "Animated text with configurable title, subtitle, colors, and timing.",
        "compositions": ["TextAnimation"],
        "props": {
            "title": "string",
            "subtitle": "string",
            "backgroundColor": "string",
            "textColor": "string",
        },
    },
    "slideshow": {
        "name": "Slideshow",
        "description": "Image slideshow with transitions. Pass an array of image URLs.",
        "compositions": ["Slideshow"],
        "props": {
            "images": "string[]",
            "transitionDuration": "number",
            "slideDuration": "number",
        },
    },
    "lower-third": {
        "name": "Lower Third",
        "description": "Broadcast-style lower third overlay with name and title.",
        "compositions": ["LowerThird"],
        "props": {
            "name": "string",
            "title": "string",
            "accentColor": "string",
        },
    },
    "countdown": {
        "name": "Countdown",
        "description": "Animated countdown timer.",
        "compositions": ["Countdown"],
        "props": {
            "from": "number",
            "backgroundColor": "string",
            "textColor": "string",
        },
    },
}


def _generate_package_json(project_name: str) -> dict:
    """Generate package.json for a Remotion project."""
    return {
        "name": project_name,
        "version": "1.0.0",
        "private": True,
        "scripts": {
            "start": "npx remotion studio",
            "build": "npx remotion render Main out/video.mp4",
            "render": "npx remotion render",
        },
        "dependencies": {
            "react": "^18.3.1",
            "react-dom": "^18.3.1",
            "remotion": "^4.0.0",
            "@remotion/cli": "^4.0.0",
            "@remotion/bundler": "^4.0.0",
        },
        "devDependencies": {
            "typescript": "^5.8.0",
            "@types/react": "^18.3.0",
        },
    }


def _generate_tsconfig() -> dict:
    """Generate tsconfig.json for a Remotion project."""
    return {
        "compilerOptions": {
            "target": "ES2022",
            "module": "ES2022",
            "moduleResolution": "bundler",
            "jsx": "react-jsx",
            "strict": True,
            "esModuleInterop": True,
            "skipLibCheck": True,
            "outDir": "./dist",
            "rootDir": "./src",
        },
        "include": ["src/**/*"],
    }


def _generate_root_index(compositions: List[Dict[str, Any]]) -> str:
    """Generate the root index.tsx that registers compositions."""
    imports = []
    registrations = []

    for comp in compositions:
        comp_id = comp["id"]
        component_name = comp["component"]
        width = comp.get("width", 1920)
        height = comp.get("height", 1080)
        fps = comp.get("fps", 30)
        duration = comp.get("durationInFrames", 150)

        imports.append(f'import {{ {component_name} }} from "./compositions/{component_name}";')
        registrations.append(
            f"""      <Composition
        id="{comp_id}"
        component={{{component_name}}}
        durationInFrames={{{duration}}}
        fps={{{fps}}}
        width={{{width}}}
        height={{{height}}}
        defaultProps={{{json.dumps(comp.get("defaultProps", {}))}}}
      />"""
        )

    return f"""import {{ Composition }} from "remotion";
{chr(10).join(imports)}

export const RemotionRoot: React.FC = () => {{
  return (
    <>
{chr(10).join(registrations)}
    </>
  );
}};
"""


def _generate_blank_composition() -> str:
    """Generate a blank composition component."""
    return """import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate } from "remotion";

interface MainProps {
  title?: string;
  backgroundColor?: string;
  textColor?: string;
}

export const Main: React.FC<MainProps> = ({
  title = "Hello World",
  backgroundColor = "#000000",
  textColor = "#ffffff",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const opacity = interpolate(frame, [0, fps * 0.5], [0, 1], {
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor,
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <h1
        style={{
          color: textColor,
          fontSize: 80,
          fontFamily: "Arial, sans-serif",
          opacity,
        }}
      >
        {title}
      </h1>
    </AbsoluteFill>
  );
};
"""


def _generate_text_animation_composition() -> str:
    """Generate a text animation composition."""
    return """import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
} from "remotion";

interface TextAnimationProps {
  title?: string;
  subtitle?: string;
  backgroundColor?: string;
  textColor?: string;
}

export const TextAnimation: React.FC<TextAnimationProps> = ({
  title = "Title",
  subtitle = "Subtitle",
  backgroundColor = "#1a1a2e",
  textColor = "#ffffff",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleSpring = spring({ frame, fps, config: { damping: 12 } });
  const subtitleOpacity = interpolate(frame, [fps * 0.5, fps * 1], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const titleY = interpolate(titleSpring, [0, 1], [50, 0]);

  return (
    <AbsoluteFill
      style={{
        backgroundColor,
        justifyContent: "center",
        alignItems: "center",
        flexDirection: "column",
        gap: 20,
      }}
    >
      <h1
        style={{
          color: textColor,
          fontSize: 72,
          fontFamily: "Arial, sans-serif",
          transform: `translateY(${titleY}px)`,
          opacity: titleSpring,
          margin: 0,
        }}
      >
        {title}
      </h1>
      <p
        style={{
          color: textColor,
          fontSize: 32,
          fontFamily: "Arial, sans-serif",
          opacity: subtitleOpacity,
          margin: 0,
        }}
      >
        {subtitle}
      </p>
    </AbsoluteFill>
  );
};
"""


def _generate_slideshow_composition() -> str:
    """Generate a slideshow composition."""
    return """import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  Img,
  interpolate,
  Sequence,
} from "remotion";

interface SlideshowProps {
  images?: string[];
  slideDuration?: number;
  transitionDuration?: number;
}

export const Slideshow: React.FC<SlideshowProps> = ({
  images = [],
  slideDuration = 3,
  transitionDuration = 0.5,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const slideFrames = slideDuration * fps;
  const transitionFrames = transitionDuration * fps;

  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      {images.map((src, i) => {
        const startFrame = i * slideFrames;
        return (
          <Sequence key={i} from={startFrame} durationInFrames={slideFrames + transitionFrames}>
            <AbsoluteFill>
              <Img
                src={src}
                style={{
                  width: "100%",
                  height: "100%",
                  objectFit: "cover",
                  opacity: interpolate(
                    frame - startFrame,
                    [0, transitionFrames, slideFrames, slideFrames + transitionFrames],
                    [0, 1, 1, 0],
                    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
                  ),
                }}
              />
            </AbsoluteFill>
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
"""


TEMPLATE_GENERATORS = {
    "Main": _generate_blank_composition,
    "TextAnimation": _generate_text_animation_composition,
    "Slideshow": _generate_slideshow_composition,
}


# ===== Core Functions =====


async def create_remotion_project(
    project_name: str,
    template: str = "blank",
    output_dir: Optional[str] = None,
    compositions: Optional[List[Dict[str, Any]]] = None,
    width: int = 1920,
    height: int = 1080,
    fps: int = 30,
    duration_seconds: float = 5.0,
) -> Dict[str, Any]:
    """Create a new Remotion project from a template.

    Args:
        project_name: Name of the project (used for directory name).
        template: Template name (blank, text-animation, slideshow, lower-third, countdown).
        output_dir: Base directory for the project. Defaults to REMOTION_WORKSPACE.
        compositions: Custom composition definitions. If None, uses template defaults.
        width: Default video width.
        height: Default video height.
        fps: Default frames per second.
        duration_seconds: Default duration in seconds.

    Returns:
        dict with project_dir, template, compositions info.
    """
    base_dir = output_dir or REMOTION_WORKSPACE
    project_dir = os.path.join(base_dir, f"{project_name}-{uuid.uuid4().hex[:8]}")
    os.makedirs(project_dir, exist_ok=True)

    template_info = BUILTIN_TEMPLATES.get(template, BUILTIN_TEMPLATES["blank"])
    duration_frames = int(duration_seconds * fps)

    if compositions is None:
        compositions = []
        for comp_name in template_info.get("compositions", ["Main"]):
            compositions.append({
                "id": comp_name,
                "component": comp_name,
                "width": width,
                "height": height,
                "fps": fps,
                "durationInFrames": duration_frames,
                "defaultProps": {},
            })

    # Write package.json
    package_json = _generate_package_json(project_name)
    with open(os.path.join(project_dir, "package.json"), "w") as f:
        json.dump(package_json, f, indent=2)

    # Write tsconfig.json
    tsconfig = _generate_tsconfig()
    with open(os.path.join(project_dir, "tsconfig.json"), "w") as f:
        json.dump(tsconfig, f, indent=2)

    # Create src directory structure
    src_dir = os.path.join(project_dir, "src")
    compositions_dir = os.path.join(src_dir, "compositions")
    os.makedirs(compositions_dir, exist_ok=True)

    # Generate root index
    root_index = _generate_root_index(compositions)
    with open(os.path.join(src_dir, "index.tsx"), "w") as f:
        f.write(root_index)

    # Generate composition files
    for comp in compositions:
        component_name = comp["component"]
        generator = TEMPLATE_GENERATORS.get(component_name, _generate_blank_composition)
        content = generator()
        with open(os.path.join(compositions_dir, f"{component_name}.tsx"), "w") as f:
            f.write(content)

    # Write remotion.config.ts
    remotion_config = """import { Config } from "@remotion/cli/config";

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);
"""
    with open(os.path.join(project_dir, "remotion.config.ts"), "w") as f:
        f.write(remotion_config)

    logger.info(
        "Remotion project created",
        extra={
            "project_name": project_name,
            "template": template,
            "project_dir": project_dir,
        },
    )

    return {
        "success": True,
        "project_dir": project_dir,
        "template": template,
        "compositions": [c["id"] for c in compositions],
        "requires_npm_install": True,
    }


async def install_dependencies(project_dir: str, timeout: int = 120) -> Dict[str, Any]:
    """Run npm install in a Remotion project directory.

    Args:
        project_dir: Path to the Remotion project.
        timeout: Maximum time in seconds.

    Returns:
        dict with success status and output.
    """
    try:
        process = await asyncio.create_subprocess_exec(
            "npm", "install",
            cwd=project_dir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)

        return {
            "success": process.returncode == 0,
            "stdout": stdout.decode("utf-8", errors="replace"),
            "stderr": stderr.decode("utf-8", errors="replace"),
        }

    except asyncio.TimeoutError:
        return {"success": False, "error": f"npm install timed out after {timeout}s"}
    except FileNotFoundError:
        return {"success": False, "error": "npm not found. Install Node.js 18+."}


async def render_composition(
    project_dir: str,
    composition_id: str = "Main",
    output_path: Optional[str] = None,
    props: Optional[Dict[str, Any]] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    fps: Optional[int] = None,
    codec: str = "h264",
    crf: int = 18,
    timeout: int = 300,
) -> Dict[str, Any]:
    """Render a Remotion composition to a video file.

    Args:
        project_dir: Path to the Remotion project.
        composition_id: ID of the composition to render.
        output_path: Output file path. Defaults to project_dir/out/video.mp4.
        props: Input props to pass to the composition (JSON-serializable).
        width: Override video width.
        height: Override video height.
        fps: Override frame rate.
        codec: Video codec (h264, h265, vp8, vp9).
        crf: Constant Rate Factor (0-63, lower = better quality).
        timeout: Maximum render time in seconds.

    Returns:
        dict with output_path and render details.
    """
    if output_path is None:
        out_dir = os.path.join(project_dir, "out")
        os.makedirs(out_dir, exist_ok=True)
        output_path = os.path.join(out_dir, "video.mp4")

    cmd = [
        "npx", "remotion", "render",
        composition_id,
        output_path,
    ]

    if props:
        cmd.extend(["--props", json.dumps(props)])
    if width:
        cmd.extend(["--width", str(width)])
    if height:
        cmd.extend(["--height", str(height)])
    if fps:
        cmd.extend(["--fps", str(fps)])

    cmd.extend(["--codec", codec])
    cmd.extend(["--crf", str(crf)])

    logger.info(
        "Rendering Remotion composition",
        extra={
            "composition_id": composition_id,
            "output_path": output_path,
            "project_dir": project_dir,
        },
    )

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=project_dir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)

        if process.returncode == 0:
            file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0

            logger.info(
                "Remotion render completed",
                extra={
                    "composition_id": composition_id,
                    "output_path": output_path,
                    "file_size": file_size,
                },
            )

            return {
                "success": True,
                "output_path": output_path,
                "file_size": file_size,
                "composition_id": composition_id,
            }
        else:
            error_msg = stderr.decode("utf-8", errors="replace")
            logger.error(f"Remotion render failed: {error_msg[:500]}")
            return {
                "success": False,
                "error": error_msg[:500],
            }

    except asyncio.TimeoutError:
        return {"success": False, "error": f"Render timed out after {timeout}s"}
    except FileNotFoundError:
        return {
            "success": False,
            "error": "npx not found. Install Node.js 18+ and ensure npx is in PATH.",
        }


async def update_composition_props(
    project_dir: str,
    composition_id: str,
    props: Dict[str, Any],
) -> Dict[str, Any]:
    """Update the default props for a composition in the root index.

    This modifies the defaultProps in the root index.tsx file so that
    subsequent renders use the updated values.

    Args:
        project_dir: Path to the Remotion project.
        composition_id: Composition ID to update.
        props: New default props.

    Returns:
        dict with success status.
    """
    index_path = os.path.join(project_dir, "src", "index.tsx")

    if not os.path.exists(index_path):
        return {"success": False, "error": "index.tsx not found"}

    with open(index_path, "r") as f:
        content = f.read()

    # Find and replace defaultProps for the specified composition
    import re

    pattern = rf'(id="{composition_id}"[\s\S]*?defaultProps={{)(.*?)(}})'
    replacement = rf'\g<1>{json.dumps(props)}\3'

    new_content = re.sub(pattern, replacement, content)

    if new_content == content:
        return {"success": False, "error": f"Composition {composition_id} not found in index.tsx"}

    with open(index_path, "w") as f:
        f.write(new_content)

    return {"success": True, "composition_id": composition_id, "props": props}


def list_templates() -> List[Dict[str, Any]]:
    """List available Remotion project templates.

    Returns:
        List of template info dicts with name, description, and available props.
    """
    return [
        {
            "id": tid,
            "name": info["name"],
            "description": info["description"],
            "compositions": info.get("compositions", []),
            "configurable_props": info.get("props", {}),
        }
        for tid, info in BUILTIN_TEMPLATES.items()
    ]


def cleanup_remotion_project(project_dir: str) -> None:
    """Remove a Remotion project directory."""
    if os.path.exists(project_dir):
        shutil.rmtree(project_dir)
        logger.info("Remotion project cleaned up", extra={"project_dir": project_dir})
