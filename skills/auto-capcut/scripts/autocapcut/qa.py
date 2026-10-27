"""Technical verification of an actual local export; no editor success is inferred."""

from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
import re
import subprocess

from .errors import AutoCapcutError
from .media import inspect_media, resolve_tool


def verify_media(path, expected=None, *, ffprobe=None, ffmpeg=None):
    report = {
        "scope": "local_media_only", "passed": False, "review_status": "failed",
        "verified_at": datetime.now(timezone.utc).isoformat(), "checks": [],
        "artifact_paths": [str(Path(path).resolve())],
        "unverified": ["editor_reopen_and_editability", "story_and_caption_quality"],
    }
    try:
        asset = inspect_media(path, ffprobe)
    except AutoCapcutError as exc:
        report["checks"].append({"id": "media_readable", "status": "blocked" if exc.code == "E_MEDIA_TOOL" else "failed",
                                 "error": exc.to_dict(), "evidencePath": str(Path(path).resolve())})
        if exc.code == "E_MEDIA_TOOL":
            report["review_status"] = "blocked"
        return report
    report["media"] = asset
    report["checks"].append({"id": "media_readable", "status": "passed", "evidencePath": asset["path"]})
    if asset["kind"] != "video":
        report["checks"].append({"id": "video_stream", "status": "failed", "details": "The export has no video stream."})
        return report
    expected = expected or {}
    for key in ("width", "height", "audio_tracks", "fps_num", "fps_den"):
        if key in expected:
            valid = type(expected[key]) is int and expected[key] >= (0 if key == "audio_tracks" else 1)
            report["checks"].append({"id": key, "status": "passed" if valid and asset.get(key) == expected[key] else "failed",
                                     "details": {"expected": expected[key], "actual": asset.get(key)}})
    if "duration_us" in expected:
        frame_us = Fraction(1_000_000 * asset["fps_den"], asset["fps_num"]) if asset.get("fps_num") else Fraction(1000)
        tolerance = expected.get("duration_tolerance_us", -(-frame_us.numerator // frame_us.denominator))
        wanted = expected["duration_us"]
        valid = type(wanted) is int and wanted > 0 and type(tolerance) is int and tolerance >= 0
        actual_duration = max(asset["duration_us"], asset.get("container_duration_us") or 0)
        matched = valid and abs(actual_duration - wanted) <= tolerance
        report["checks"].append({"id": "duration", "status": "passed" if matched else "failed",
                                 "details": {"expected_us": wanted, "actual_us": actual_duration,
                                             "video_duration_us": asset["duration_us"], "tolerance_us": tolerance}})
    if expected.get("require_audio") is True:
        report["checks"].append({"id": "audio_present", "status": "passed" if asset["audio_tracks"] else "failed"})
    if "aspect_ratio" in expected:
        try:
            horizontal, vertical = map(int, expected["aspect_ratio"].split(":"))
            matched = horizontal > 0 and vertical > 0 and asset["width"] * vertical == asset["height"] * horizontal
        except (AttributeError, ValueError, TypeError):
            matched = False
        report["checks"].append({"id": "aspect_ratio", "status": "passed" if matched else "failed"})
    try:
        decoder = resolve_tool("ffmpeg", ffmpeg)
        command = [decoder, "-v", "info", "-hide_banner", "-nostats", "-nostdin", "-xerror", "-protocol_whitelist", "file,pipe",
                   "-i", asset["path"], "-map", "0:v?", "-map", "0:a?", "-vf", "blackdetect=d=0.05:pix_th=0.10"]
        if asset["audio_tracks"]:
            command.extend(["-af", "silencedetect=noise=-50dB:d=0.25,astats=metadata=1:reset=0"])
        command.extend(["-f", "null", "-"])
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace",
                                timeout=min(600, max(30, asset["duration_us"] / 500_000)), check=False)
        report["checks"].append({"id": "full_decode", "status": "passed" if result.returncode == 0 else "failed",
                                 "evidencePath": asset["path"], "details": {"exit_code": result.returncode}})
        if result.returncode == 0:
            black = re.findall(r"black_start:(.*?)\s+black_end:(\S+)\s+black_duration:(\S+)", result.stderr)
            report["checks"].append({"id": "black_frames", "status": "review" if black else "passed",
                                     "details": {"intervals_seconds": black, "note": "Detected black may be intentional; inspect before acceptance."}})
            if asset["audio_tracks"]:
                silence = re.findall(r"silence_start:\s*([^\r\n]+)", result.stderr)
                peak_values = re.findall(r"Peak level dB:\s*(\S+)", result.stderr)
                peaks = [float(value) for value in peak_values if re.fullmatch(r"-?\d+(?:\.\d+)?", value)]
                report["checks"].append({"id": "silence", "status": "review" if silence else "passed",
                                         "details": {"starts_seconds": silence, "threshold_db": -50, "minimum_seconds": 0.25}})
                peak_status = "review" if peaks and max(peaks) >= -0.1 else "passed" if peak_values else "blocked"
                report["checks"].append({"id": "audio_peak", "status": peak_status,
                                         "details": {"peak_db": max(peaks) if peaks else "-inf" if "-inf" in peak_values else None,
                                                     "note": "A near-full-scale peak requires listening; this does not prove clipping."}})
    except AutoCapcutError as exc:
        report["checks"].append({"id": "full_decode", "status": "blocked", "error": exc.to_dict()})
    except (OSError, subprocess.TimeoutExpired):
        report["checks"].append({"id": "full_decode", "status": "blocked", "details": "Decoder could not complete."})
    report["passed"] = all(check["status"] == "passed" for check in report["checks"])
    report["review_status"] = "technical_pass" if report["passed"] else (
        "failed" if any(check["status"] == "failed" for check in report["checks"]) else
        "blocked" if any(check["status"] == "blocked" for check in report["checks"]) else "review_required")
    return report
