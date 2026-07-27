---
name: audio-blackframe-splitter
description: Splits an audio file (.mp3, .wav, or any ffmpeg-readable format) into fixed-length (e.g. 10s or 15s) .mp4 clips consisting of a solid black video track plus the matching audio segment. Built for AI video tools with a max clip length (like Seedance) whose lip-sync feature works better when given audio as a "video input" than through native audio-upload — this produces those black-frame carrier clips. ALWAYS use this skill whenever the user says "black frame clips", "black video clips", "chop this song into clips for lip sync", "split this track for Seedance", "make lip-sync input clips", "cut this into 15 second clips with no video", "blackframe the audio", "prep this track for lip sync", or hands off an audio file and asks for it to be cut into silent-video/black-video segments.
---

# Audio Blackframe Splitter

Converts an audio file into a folder of numbered black-video .mp4 clips, each
carrying one segment of the audio — useful for AI video generation tools
(e.g. Seedance) whose lip-sync feature tracks audio fed in as *video input*
more reliably than through native audio-upload.

## Workflow

1. **Get the source audio file.** If the user hasn't given a path, ask for it.

2. **Ask two things every time this runs — do not assume defaults, do not reuse
   values from a previous run in this session:**
   - **Clip length** in seconds. If the target tool has a known max clip
     length (Seedance's is 15s), mention that as a likely choice, alongside
     other common options like 10s, or "other (I'll type it)".
   - **Resolution** for the black video track (WIDTHxHEIGHT). Common options:
     "1024x576", "1920x1080", "1080x1920 (vertical)", "Other (I'll type it)".
     If the user has no preference, 1024x576 is a safe default to suggest —
     it's cheap to render, and most lip-sync tools re-render the visual
     entirely anyway, so the black-frame resolution just needs to be a valid,
     standard size.

3. **Confirm ffmpeg/ffprobe are on PATH** (`which ffmpeg ffprobe`). If missing,
   tell the user to install ffmpeg (e.g. `brew install ffmpeg` on macOS,
   `apt install ffmpeg` on Linux, or download from ffmpeg.org on Windows)
   rather than trying to work around it.

4. **Run the script** (copy it to a scratch/output location first if the
   bundled copy is in a read-only skills folder):

   ```bash
   python3 scripts/split_audio_blackframe.py "<audio_file>" \
     --clip-length <N> \
     --resolution <WxH>
   ```

   Optional flags:
   - `--output-dir <path>` — default is `<audio_folder>/<audio_stem>_blackframe_clips/`
   - `--prefix <name>` — default is the audio filename's stem
   - `--fps <n>` — default 30

5. **Report back** the output folder path and clip count/list. The final clip
   is always padded with silence to the full clip length (never left short) so
   every clip in the batch is a uniform, predictable duration.

6. **Point the user to the next step**: upload each numbered clip in order as
   the video input for its corresponding lip-sync generation, paired with
   whatever reference character/image that shot uses.

## How the script works (for reference, not required reading to use it)

For each clip `i`:
- Generates a solid black video track of exactly `clip-length` seconds at the
  chosen resolution via ffmpeg's `lavfi color` source.
- Extracts the matching audio segment (`start = i * clip-length`, duration =
  `clip-length`).
- Pads that audio segment with silence up to the full `clip-length` if it's
  the last, shorter segment (via `apad=whole_dur=`), so no clip is ever
  shorter than the others.
- Muxes video + audio into one `.mp4` (h264 / yuv420p / aac).

Output filenames: `<prefix>_clip01.mp4`, `<prefix>_clip02.mp4`, ... zero-padded
to fit the total clip count.

## Notes / edge cases

- Works on any ffmpeg-readable audio format (mp3, wav, m4a, flac, etc.).
- If the user wants clips numbered starting from a specific offset (e.g.
  picking up mid-track), pass `--output-dir` and rename after, or ask before
  running — the script always starts from 0:00.
- This skill only produces the black-frame input clips. It does not call any
  video generation tool itself, write lip-sync prompts, or handle character
  references — that's a separate step in whatever pipeline the user is using.
