from __future__ import annotations
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Tuple, Union
from PIL import Image

from videomascot.models.manifest import MascotManifest
from videomascot.models.pose import PoseState
from videomascot.models.schema import MascotActionSchema, MascotPlacementSchema, SpeechCue
from videomascot.compositor.sprite_engine import SpriteCompositor
from videomascot.compositor.stream_engine import StreamEngine
from videomascot.animation.sequencer import MascotSequencer
from videomascot.animation.lipsync import LipSyncEngine
from videomascot.animation.procedural import ProceduralLifeEngine


def probe_audio_duration(audio_path: Union[str, Path]) -> float:
    """Probes audio file duration in seconds using ffprobe."""
    path_str = str(audio_path)
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "csv=p=0",
            path_str
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if res.returncode == 0 and res.stdout.strip():
            return float(res.stdout.strip())
    except Exception:
        pass
    return 3.0  # Fallback duration


class MascotEngine:
    """High-level facade for mascot animation generation, streaming, and alpha video exports."""

    def __init__(self, compositor: SpriteCompositor) -> None:
        self.compositor = compositor
        self.manifest: MascotManifest = compositor.manifest
        self.canvas_size: Tuple[int, int] = compositor.canvas_size

    @classmethod
    def from_bundle_dir(cls, bundle_dir: Union[str, Path]) -> MascotEngine:
        compositor = SpriteCompositor.from_bundle_dir(bundle_dir)
        return cls(compositor=compositor)

    def render_frame(
        self,
        pose: Optional[PoseState] = None,
        target_size: Optional[Tuple[int, int]] = None
    ) -> Image.Image:
        """Renders a single transparent RGBA frame."""
        p = pose or PoseState()
        return self.compositor.render_frame(p, target_size=target_size)

    def create_sequencer(
        self,
        action: Optional[MascotActionSchema] = None,
        vtt_path: Optional[Union[str, Path]] = None,
        speech_cues: Optional[List[SpeechCue]] = None
    ) -> MascotSequencer:
        """Constructs a configured MascotSequencer."""
        act = action or MascotActionSchema()
        
        if speech_cues:
            lipsync = LipSyncEngine(
                cues=speech_cues,
                default_resting_viseme=MascotSequencer._get_resting_viseme_for_emotion(act.emotion)
            )
        elif vtt_path and Path(vtt_path).exists():
            lipsync = LipSyncEngine.from_vtt_file(
                vtt_path=vtt_path,
                default_resting_viseme=MascotSequencer._get_resting_viseme_for_emotion(act.emotion)
            )
        elif act.speech_cues:
            lipsync = LipSyncEngine(
                cues=act.speech_cues,
                default_resting_viseme=MascotSequencer._get_resting_viseme_for_emotion(act.emotion)
            )
        else:
            lipsync = LipSyncEngine(
                cues=[],
                default_resting_viseme=MascotSequencer._get_resting_viseme_for_emotion(act.emotion)
            )
            
        procedural = ProceduralLifeEngine(config=act.procedural)
        return MascotSequencer(action=act, lipsync=lipsync, procedural=procedural)

    def stream_scene(
        self,
        action: MascotActionSchema,
        duration: float,
        fps: int = 24,
        vtt_path: Optional[Union[str, Path]] = None,
        speech_cues: Optional[List[SpeechCue]] = None,
        target_size: Optional[Tuple[int, int]] = None
    ) -> Iterator[bytes]:
        """Streams raw uncompressed RGBA bytes for a scene duration."""
        seq = self.create_sequencer(action=action, vtt_path=vtt_path, speech_cues=speech_cues)
        streamer = StreamEngine(compositor=self.compositor, sequencer=seq)
        return streamer.iter_rgba_bytes(duration=duration, fps=fps, target_size=target_size)

    def stream_from_scene_dict(
        self,
        scene_dict: Dict,
        audio_path: Optional[Union[str, Path]] = None,
        vtt_path: Optional[Union[str, Path]] = None,
        duration: Optional[float] = None,
        fps: int = 24,
        target_size: Optional[Tuple[int, int]] = None
    ) -> Iterator[bytes]:
        """Parses a scene dictionary (e.g. from video-pipe story JSON/YAML) and streams raw RGBA frames."""
        mascot_data = scene_dict.get("mascot") or {}
        
        # If emotion is omitted from mascot, fall back to scene emotion
        if "emotion" not in mascot_data and "emotion" in scene_dict:
            scene_emo = scene_dict["emotion"].lower()
            emo_map = {
                "happy": "happy",
                "excited": "excited",
                "serious": "serious",
                "thoughtful": "thinking",
                "nostalgic": "friendly",
                "peaceful": "friendly",
                "neutral": "neutral"
            }
            mascot_data["emotion"] = emo_map.get(scene_emo, "friendly")
            
        action = MascotActionSchema.model_validate(mascot_data)
        
        # Calculate duration
        scene_dur = duration
        if scene_dur is None and audio_path:
            scene_dur = probe_audio_duration(audio_path)
        if scene_dur is None:
            scene_dur = 3.0
            
        # Automatic VTT subtitle file resolution if not specified
        resolved_vtt = vtt_path
        if resolved_vtt is None and audio_path:
            candidate_vtt = Path(audio_path).with_suffix(".vtt")
            if candidate_vtt.exists():
                resolved_vtt = candidate_vtt
                
        return self.stream_scene(
            action=action,
            duration=scene_dur,
            fps=fps,
            vtt_path=resolved_vtt,
            target_size=target_size
        )

    def export_alpha_video(
        self,
        action: MascotActionSchema,
        duration: float,
        output_path: Union[str, Path],
        fps: int = 24,
        codec: str = "vp9",
        vtt_path: Optional[Union[str, Path]] = None,
        target_size: Optional[Tuple[int, int]] = None
    ) -> Path:
        """Exports a standalone transparent alpha video (WebM VP9 or ProRes 4444)."""
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        
        w, h = target_size or self.canvas_size
        
        if codec == "prores_4444" or out_file.suffix.lower() == ".mov":
            # Apple ProRes 4444 with alpha (yuva444p10le)
            ffmpeg_cmd = [
                "ffmpeg", "-y",
                "-f", "rawvideo",
                "-pix_fmt", "rgba",
                "-s", f"{w}x{h}",
                "-r", str(fps),
                "-i", "pipe:0",
                "-c:v", "prores_ks",
                "-profile:v", "4",
                "-pix_fmt", "yuva444p10le",
                str(out_file)
            ]
        else:
            # WebM VP9 with alpha (yuva420p)
            ffmpeg_cmd = [
                "ffmpeg", "-y",
                "-f", "rawvideo",
                "-pix_fmt", "rgba",
                "-s", f"{w}x{h}",
                "-r", str(fps),
                "-i", "pipe:0",
                "-c:v", "libvpx-vp9",
                "-pix_fmt", "yuva420p",
                "-crf", "20",
                "-b:v", "0",
                str(out_file)
            ]
            
        with tempfile.TemporaryFile(mode="w+b") as stderr_file:
            proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stderr=stderr_file)
            
            stream = self.stream_scene(
                action=action,
                duration=duration,
                fps=fps,
                vtt_path=vtt_path,
                target_size=(w, h)
            )
            
            try:
                for frame_chunk in stream:
                    proc.stdin.write(frame_chunk)
                proc.stdin.close()
                proc.wait(timeout=120)
            except Exception as e:
                proc.kill()
                raise RuntimeError(f"FFmpeg alpha export failed: {e}")
                
            if proc.returncode != 0:
                stderr_file.seek(0)
                stderr = stderr_file.read().decode("utf-8", errors="replace")
                raise RuntimeError(f"FFmpeg error (code {proc.returncode}): {stderr}")
                
        return out_file
