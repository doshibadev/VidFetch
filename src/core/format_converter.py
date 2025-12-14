"""FFmpeg helper utilities for format conversion."""
from __future__ import annotations

import ffmpeg


def convert_to_mp3(input_path: str, output_path: str, bitrate: str = "192k") -> None:
    (ffmpeg
        .input(input_path)
        .output(output_path, audio_bitrate=bitrate, vn=None)
        .run(overwrite_output=True)
    )
