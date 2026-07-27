#!/usr/bin/env python3
"""
split_audio_blackframe.py

Splits an audio file (.mp3/.wav/etc) into fixed-length video clips with a
solid black video track, for use as Seedance lip-sync audio-input reference
clips. Each output clip = [black video, exact length] + [audio segment,
padded with silence to exact length if it's the final short segment].

Usage:
    python3 split_audio_blackframe.py <audio_file> --clip-length 15 --resolution 1024x576

Requires: ffmpeg, ffprobe on PATH.
"""

import argparse
import math
import subprocess
import sys
from pathlib import Path


def get_duration(audio_path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(audio_path),
        ],
        capture_output=True, text=True, check=True,
    )
    return float(result.stdout.strip())


def main():
    parser = argparse.ArgumentParser(description="Split audio into black-frame video clips for Seedance lip-sync input.")
    parser.add_argument("audio_file", type=str, help="Path to source .mp3/.wav file")
    parser.add_argument("--clip-length", type=float, required=True, help="Clip length in seconds (e.g. 15 or 10)")
    parser.add_argument("--resolution", type=str, required=True, help="WIDTHxHEIGHT, e.g. 1024x576")
    parser.add_argument("--fps", type=int, default=30, help="Frame rate of black video (default 30)")
    parser.add_argument("--output-dir", type=str, default=None, help="Output folder (default: <audio_dir>/<audio_stem>_blackframe_clips/)")
    parser.add_argument("--prefix", type=str, default=None, help="Filename prefix (default: audio file stem)")
    args = parser.parse_args()

    audio_path = Path(args.audio_file).expanduser().resolve()
    if not audio_path.exists():
        sys.exit(f"Error: audio file not found: {audio_path}")

    if "x" not in args.resolution.lower():
        sys.exit(f"Error: --resolution must be WIDTHxHEIGHT, got: {args.resolution}")
    res = args.resolution.lower()

    clip_len = args.clip_length
    if clip_len <= 0:
        sys.exit("Error: --clip-length must be positive")

    prefix = args.prefix or audio_path.stem
    output_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else audio_path.parent / f"{audio_path.stem}_blackframe_clips"
    output_dir.mkdir(parents=True, exist_ok=True)

    duration = get_duration(audio_path)
    total_clips = math.ceil(duration / clip_len)
    pad_width = max(2, len(str(total_clips)))

    print(f"Source: {audio_path.name}")
    print(f"Duration: {duration:.2f}s -> {total_clips} clip(s) at {clip_len}s each ({res}, {args.fps}fps)")
    print(f"Output: {output_dir}")
    print()

    for i in range(total_clips):
        start = i * clip_len
        out_name = f"{prefix}_clip{str(i + 1).zfill(pad_width)}.mp4"
        out_path = output_dir / out_name

        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", f"color=c=black:s={res}:r={args.fps}:d={clip_len}",
            "-ss", f"{start}", "-t", f"{clip_len}", "-i", str(audio_path),
            "-filter_complex", f"[1:a]apad=whole_dur={clip_len}[a]",
            "-map", "0:v", "-map", "[a]",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-t", f"{clip_len}",
            str(out_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  [FAIL] clip {i + 1}/{total_clips}: {out_name}")
            print(result.stderr[-1500:])
            sys.exit(1)
        print(f"  [ok] {out_name}  (segment {start:.1f}s - {min(start + clip_len, duration):.1f}s)")

    print()
    print(f"Done. {total_clips} clip(s) written to {output_dir}")


if __name__ == "__main__":
    main()
