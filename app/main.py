from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class VideoClip:
    id: str
    filename: str
    path: str
    duration: float = 0.0
    start: float = 0.0
    end: float = 0.0
    color_tag: str = "#3b82f6"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "filename": self.filename,
            "path": self.path,
            "duration": self.duration,
            "start": self.start,
            "end": self.end,
            "color_tag": self.color_tag,
        }


class VideoProject:
    def __init__(self) -> None:
        self.clips: List[VideoClip] = []

    def add_clip(self, file_path: str) -> VideoClip:
        resolved = Path(file_path).expanduser().resolve()
        if not resolved.exists():
            raise FileNotFoundError(f"Media file not found: {resolved}")

        duration = self._probe_duration(str(resolved))
        clip = VideoClip(
            id=f"clip_{len(self.clips) + 1}",
            filename=resolved.name,
            path=str(resolved),
            duration=duration,
            start=0.0,
            end=duration,
        )
        self.clips.append(clip)
        return clip

    def clear(self) -> None:
        self.clips.clear()

    def total_duration(self) -> float:
        return sum(clip.duration for clip in self.clips)

    def _probe_duration(self, file_path: str) -> float:
        ffprobe = shutil.which("ffprobe")
        if not ffprobe:
            return 0.0

        cmd = [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            file_path,
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if result.returncode == 0 and result.stdout.strip():
                return float(result.stdout.strip())
        except Exception:
            pass
        return 0.0

    def export(self, output_path: str) -> str:
        if not self.clips:
            raise ValueError("No media clips in the project.")

        ffmpeg = shutil.which("ffmpeg")
        if not ffmpeg:
            raise RuntimeError("FFmpeg is not installed or not available on PATH.")

        output = Path(output_path).expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)

        concat_file = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8")
        try:
            for clip in self.clips:
                safe_path = clip.path.replace("\\", "/")
                concat_file.write(f"file '{safe_path}'\n")
            concat_file.close()

            cmd = [
                ffmpeg,
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                concat_file.name,
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-crf",
                "20",
                "-c:a",
                "aac",
                "-movflags",
                "+faststart",
                str(output),
            ]
            subprocess.run(cmd, check=True)
            return str(output)
        finally:
            try:
                os.unlink(concat_file.name)
            except OSError:
                pass

    def __len__(self) -> int:
        return len(self.clips)
