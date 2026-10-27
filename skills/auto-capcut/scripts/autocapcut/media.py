"""Read-only inspection of local media; never uploads or edits source files."""

import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from decimal import Decimal, InvalidOperation, ROUND_FLOOR
from fractions import Fraction
from pathlib import Path

from .errors import AutoCapcutError

MEDIA_SUFFIXES = frozenset({
    ".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v", ".mpeg", ".mpg", ".mts",
    ".mp3", ".wav", ".aac", ".m4a", ".flac", ".aiff", ".ogg", ".opus",
    ".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tif", ".tiff", ".avif", ".gif",
})


def verify_sources(assets, asset_ids=None):
    """Recheck referenced local bytes before resuming or issuing an editor write."""
    checked = []
    for asset in assets:
        if asset_ids is not None and asset.get('asset_id') not in asset_ids:
            continue
        source = Path(asset.get('path', '')).expanduser()
        if not source.is_file():
            raise AutoCapcutError('E_MEDIA_MISSING', 'A referenced source file is missing.', 'Locate the source and re-inspect it before continuing.')
        expected = asset.get('hash')
        if not isinstance(expected, str) or re.fullmatch(r'[0-9a-f]{64}', expected) is None:
            raise AutoCapcutError('E_MEDIA_CHANGED', 'Source integrity evidence is missing.', 'Re-inspect the source files.')
        try:
            digest = hashlib.sha256()
            with source.open('rb') as stream:
                while block := stream.read(1024 * 1024):
                    digest.update(block)
        except OSError as exc:
            raise AutoCapcutError('E_MEDIA_READ', 'A referenced source cannot be read.', 'Check source permissions and re-inspect it.') from exc
        if digest.hexdigest() != expected:
            raise AutoCapcutError('E_MEDIA_CHANGED', 'Source bytes changed since inspection.', 'Re-inspect and replan; preserve the old project revision.')
        checked.append(asset['asset_id'])
    return checked


def inspect_assets(paths, ffprobe=None):
    """Inspect only requested paths; directory discovery does not follow symlinks."""
    paths = [paths] if isinstance(paths, (str, Path)) else paths
    sources = []
    for value in paths:
        path = Path(value).expanduser()
        if path.is_dir():
            for parent, directories, files in os.walk(path, followlinks=False):
                directories[:] = sorted(d for d in directories if not (Path(parent) / d).is_symlink())
                sources.extend(Path(parent) / name for name in sorted(files)
                               if Path(name).suffix.lower() in MEDIA_SUFFIXES and not (Path(parent) / name).is_symlink())
        else:
            sources.append(path)
    if not sources:
        raise AutoCapcutError("E_MEDIA_EMPTY", "The selected paths contain no media.", "Choose a folder containing readable video, audio or image files.")
    return [inspect_media(source, ffprobe) for source in dict.fromkeys(p.resolve() for p in sources)]


def inspect_media(path, ffprobe=None, *, content_evidence=None):
    source = Path(path).expanduser().resolve()
    if not source.is_file():
        raise AutoCapcutError("E_MEDIA_MISSING", "Media is not a readable file.", "Select an existing local media file.")
    executable = resolve_tool("ffprobe", ffprobe)
    try:
        completed = subprocess.run(
            [executable, "-v", "error", "-protocol_whitelist", "file,pipe", "-show_format", "-show_streams", "-of", "json", "-i", str(source)],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise AutoCapcutError("E_MEDIA_PROBE", "Media inspection could not complete.", "Check the local ffprobe executable and retry.") from exc
    if completed.returncode:
        raise AutoCapcutError("E_MEDIA_DECODE", "Media could not be decoded by ffprobe.", "Check the file in a media player or choose a readable source.")
    try:
        metadata = json.loads(completed.stdout)
        streams = metadata["streams"]
    except (ValueError, KeyError, TypeError) as exc:
        raise AutoCapcutError("E_MEDIA_PROBE", "ffprobe returned invalid media metadata.", "Use a working ffprobe version and retry.") from exc
    audio = [s for s in streams if s.get("codec_type") == "audio"]
    video = [s for s in streams if s.get("codec_type") == "video" and not s.get("disposition", {}).get("attached_pic")]
    if not audio and not video:
        raise AutoCapcutError("E_MEDIA_KIND", "The file has no supported video, audio or image stream.", "Select a video, audio or image file.")
    image = bool(video) and source.suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tif", ".tiff", ".avif"}
    kind = "image" if image else "video" if video else "audio"
    duration = None if image else _duration_us(metadata, video[:1] if video else audio)
    try:
        container_duration = None if image else _duration_us(metadata, [])
    except AutoCapcutError:
        container_duration = duration
    picture = video[0] if video else {}
    try:
        fps = Fraction(picture.get("avg_frame_rate", "0/1"))
        if not fps:
            fps = Fraction(picture.get("r_frame_rate", "0/1"))
    except (ValueError, ZeroDivisionError):
        fps = Fraction(0)
    digest = hashlib.sha256()
    try:
        with source.open("rb") as media:
            while block := media.read(1024 * 1024):
                digest.update(block)
        size = source.stat().st_size
    except OSError as exc:
        raise AutoCapcutError("E_MEDIA_READ", "Media could not be read.", "Check local file permissions and retry.") from exc
    identity = hashlib.sha256((str(source) + digest.hexdigest()).encode("utf-8")).hexdigest()[:16]
    return {
        "asset_id": "asset-" + identity, "kind": kind, "path": str(source), "exists": True,
        "size": size, "hash": digest.hexdigest(), "duration_us": duration,
        "container_duration_us": container_duration, "container": metadata.get("format", {}).get("format_name"),
        "width": picture.get("width"), "height": picture.get("height"),
        "fps_num": fps.numerator if fps else None, "fps_den": fps.denominator if fps else None,
        "audio_tracks": len(audio), "content_evidence": content_evidence or [],
    }


def extract_frame(path, at_us, output_path, *, ffprobe=None, ffmpeg=None):
    """Extract one image for Codex visual inspection, without changing the video."""
    if type(at_us) is not int or at_us < 0:
        raise AutoCapcutError("E_MEDIA_RANGE", "Frame time must be non-negative integer microseconds.", "Choose an integer timestamp inside the source video.")
    source = inspect_media(path, ffprobe)
    if source["kind"] != "video" or at_us >= source["duration_us"]:
        raise AutoCapcutError("E_MEDIA_RANGE", "Frame time is outside a video source.", "Choose a timestamp strictly before the inspected video duration.")
    output = Path(output_path).expanduser().absolute()
    if output.suffix.lower() != ".png" or not output.parent.is_dir() or output.exists() or output.is_symlink():
        raise AutoCapcutError("E_MEDIA_OUTPUT", "Frame output needs a new .png path in an existing directory.", "Choose a new evidence filename; existing files are preserved.")
    decoder = resolve_tool("ffmpeg", ffmpeg)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(prefix=".auto-capcut-frame-", suffix=".png", dir=output.parent, delete=False) as handle:
            temporary = Path(handle.name)
        timestamp = f"{at_us // 1_000_000}.{at_us % 1_000_000:06d}"
        result = subprocess.run([decoder, "-v", "error", "-nostdin", "-protocol_whitelist", "file,pipe",
                                 "-i", source["path"], "-ss", timestamp, "-frames:v", "1", "-an", "-y", str(temporary)],
                                capture_output=True, timeout=60, check=False)
        if result.returncode or temporary.stat().st_size < 24 or temporary.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
            raise AutoCapcutError("E_MEDIA_FRAME", "A readable frame could not be extracted.", "Check video decoding support and choose another valid frame time.")
        os.link(temporary, output)
        return {"kind": "frame", "evidence_path": str(output.resolve()), "source_asset_id": source["asset_id"],
                "source_in_us": at_us, "source_out_us": at_us + 1,
                "description": "Extracted frame; inspect its pixels before adding a content description.", "content_reviewed": False}
    except FileExistsError as exc:
        raise AutoCapcutError("E_MEDIA_OUTPUT", "The frame output already exists.", "Choose a new evidence filename.") from exc
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise AutoCapcutError("E_MEDIA_FRAME", "Frame extraction could not complete.", "Check the local decoder, output permissions and source file.") from exc
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def resolve_tool(name, explicit=None):
    """Resolve a trusted installed inspection binary, without downloading anything."""
    candidate = explicit or os.environ.get("AUTO_CAPCUT_" + name.upper()) or shutil.which(name)
    if not candidate or not Path(candidate).is_file():
        raise AutoCapcutError("E_MEDIA_TOOL", f"{name} is not available.", f"Provide an installed {name} path or AUTO_CAPCUT_{name.upper()}.")
    return str(Path(candidate).resolve())


def _duration_us(metadata, streams):
    durations = []
    for stream in streams:
        durations.append(stream.get('duration'))
        try:
            ticks = int(stream['duration_ts'])
            value = Fraction(stream['time_base']) * ticks * 1_000_000
            if value > 0:
                durations.append(Decimal(value.numerator // value.denominator) / 1_000_000)
        except (KeyError, ValueError, TypeError, ZeroDivisionError):
            pass
        for key, value in stream.get('tags', {}).items():
            if key.casefold() == 'duration' and isinstance(value, str):
                match = re.fullmatch(r'(\d+):([0-5]\d):([0-5]\d(?:\.\d+)?)', value)
                if match:
                    durations.append(Decimal(match[1]) * 3600 + Decimal(match[2]) * 60 + Decimal(match[3]))
    # A container may include a longer audio tail. Never use it as a video bound.
    if not streams:
        durations.append(metadata.get("format", {}).get("duration"))
    for value in durations:
        try:
            seconds = Decimal(str(value))
            if seconds.is_finite() and seconds > 0:
                return int((seconds * 1_000_000).to_integral_value(rounding=ROUND_FLOOR))
        except InvalidOperation:
            continue
    raise AutoCapcutError("E_MEDIA_DURATION", "Media duration is missing or invalid.", "Repair or transcode the source with your media tools, then inspect it again.")
