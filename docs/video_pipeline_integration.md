# Video Pipeline Integration Guide 🎥

This document details how to integrate VideoMascot into automated video production systems (such as `video-pipe`, MoviePy pipelines, or custom FFmpeg workflows).

---

## 🏛️ In-Memory Zero-Disk Streaming Architecture

A major challenge in video production at scale is I/O bottlenecks. Rendering thousands of individual PNG images to disk causes severe disk thrashing, high latency, and storage bloat.

VideoMascot solves this with **Zero-Disk In-Memory Streaming**:

```
+-----------------------------------------------------------------------------------------------+
|                                      VideoMascot In-Memory                                    |
|                                                                                               |
|   [MascotSequencer] ---> [SpriteCompositor] ---> [StreamEngine]                               |
|                                                         |                                     |
|                                                         v (Raw RGBA Bytes in RAM)             |
+---------------------------------------------------------|-------------------------------------+
                                                          |
                                           stdin.write(frame_bytes)
                                                          |
                                                          v
+-----------------------------------------------------------------------------------------------+
|                                      FFmpeg Subprocess Pipe                                   |
|                                                                                               |
|   ffmpeg -y -i scene_bg.mp4 -f rawvideo -pix_fmt rgba -s 486x486 -r 24 -i pipe:0              |
|          -filter_complex "[0:v][1:v]overlay=x=1404:y=564:eof_action=pass:shortest=1[outv]"     |
|          -c:v libx264 -pix_fmt yuv420p output.mp4                                            |
+-----------------------------------------------------------------------------------------------+
```

* **RAM Overhead**: Constant $O(1)$ memory consumption (~4MB per frame buffer).
* **Disk I/O**: Zero intermediate image files created.

---

## 💻 Consumer Integration with `video-pipe`

In `video-pipe`'s scene assembler ([`video_pipe.assembler.VideoAssembler`](file:///c:/Users/HP/Desktop/video-pipe/src/video_pipe/assembler.py)), VideoMascot is invoked directly during clip generation:

```python
from pathlib import Path
from videomascot import MascotEngine, VideoOverlayCompositor, MascotActionSchema, MascotPlacementSchema

# 1. Initialize engine once per pipeline run
mascot_engine = MascotEngine.from_bundle_dir("assets/mascots/chibi_tech_guide")
compositor = VideoOverlayCompositor(engine=mascot_engine)

# 2. Composite mascot over scene clip
def render_scene_with_mascot(
    background_clip: Path,
    output_clip: Path,
    scene_dict: dict,
    audio_path: Path,
    vtt_path: Path
) -> Path:
    return compositor.overlay_onto_video(
        input_video=background_clip,
        output_video=output_clip,
        scene_dict=scene_dict,       # Parses mascot directives & emotion fallbacks
        audio_path=audio_path,       # Probes duration & audio sync
        vtt_path=vtt_path,           # 9-viseme speech lip-sync
        crf=20,
        preset="medium"
    )
```

---

## 🎞️ Standalone Transparent Alpha Video Exports

If your workflow requires pre-rendered transparent mascot tracks (for DaVinci Resolve, Adobe Premiere, After Effects, or web players), VideoMascot exports native alpha video:

### 1. WebM VP9 (`.webm`) with Alpha
Lightweight, web-compatible transparent video using `yuva420p` pixel format:

```python
engine.export_alpha_video(
    action=action,
    duration=4.0,
    output_path="preview/mascot_alpha.webm",
    fps=24,
    codec="vp9",
    target_size=(400, 400)
)
```

### 2. Apple ProRes 4444 (`.mov`) with Alpha
Broadcast studio lossless transparent video using `yuva444p10le` pixel format:

```python
engine.export_alpha_video(
    action=action,
    duration=4.0,
    output_path="preview/mascot_alpha.mov",
    fps=24,
    codec="prores_4444",
    target_size=(1000, 1000)
)
```

---

## 🛡️ FFmpeg Pipe Deadlock Prevention

When streaming uncompressed frames into FFmpeg via `stdin.write()`, if FFmpeg writes more diagnostic output to `stderr` than the OS pipe buffer can hold (typically 4KB–64KB), the process will deadlock.

VideoMascot prevents this by routing `stderr` to a temporary spool file:

```python
import tempfile
import subprocess

with tempfile.TemporaryFile(mode="w+b") as stderr_file:
    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stderr=stderr_file)
    for frame_bytes in stream:
        proc.stdin.write(frame_bytes)
    proc.stdin.close()
    proc.wait(timeout=60)
    
    if proc.returncode != 0:
        stderr_file.seek(0)
        error_msg = stderr_file.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"FFmpeg error: {error_msg}")
```
This guarantees 100% reliable execution across Windows, Linux, and macOS even during long multi-minute video streams.
