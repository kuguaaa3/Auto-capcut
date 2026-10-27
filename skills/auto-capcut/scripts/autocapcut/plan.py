"""Pure local plan validation. A valid plan is never an edited CapCut draft."""

import math
import re
from copy import deepcopy
from fractions import Fraction

from .errors import AutoCapcutError


def frames_to_us(frame, fps_num, fps_den=1):
    """Floor an absolute frame position once; do not sum rounded frame durations."""
    frame = _integer(frame, "frame")
    rate = Fraction(_integer(fps_num, "fps_num", minimum=1), _integer(fps_den, "fps_den", minimum=1))
    value = frame * 1_000_000 / rate
    return value.numerator // value.denominator


def us_to_frame(time_us, fps_num, fps_den=1):
    """Return the frame at/before an integer microsecond position."""
    value = Fraction(_integer(time_us, "time_us"), 1_000_000) * Fraction(
        _integer(fps_num, "fps_num", minimum=1), _integer(fps_den, "fps_den", minimum=1))
    return value.numerator // value.denominator


def revise_plan(plan, patch):
    """Create a local revision proposal; this never changes an external draft."""
    _object(plan, "plan")
    _object(patch, "patch")
    revised = deepcopy(plan)
    revision = _integer(plan.get("revision"), "revision", minimum=1)
    kind = patch.get("kind", "shorten")
    if kind == "music_gain":
        if set(patch) - {"kind", "music_index", "gain_db"}:
            _fail("Unknown music gain patch fields.")
        music = _list(revised.get("music"), "music")
        index = _integer(patch.get("music_index"), "music_index", minimum=1) - 1
        if index >= len(music):
            _fail("The requested music_index is outside this plan.")
        gain = patch.get("gain_db")
        if type(gain) not in {int, float} or not math.isfinite(gain):
            _fail("Music gain_db must be a finite number.")
        music[index]["gain_db"] = gain
        revised["revision"] = revision + 1
        revised["derived_from_revision"] = revision
        return revised
    if kind != "shorten" or set(patch) - {"kind", "shot_id", "shot_index", "shorten_us"}:
        _fail("This patch is not a supported local revision operation.")
    if ("shot_id" in patch) == ("shot_index" in patch):
        _fail("Specify exactly one shot_id or one-based shot_index.")
    shots = _list(revised.get("shots"), "shots")
    if "shot_id" in patch:
        matches = [i for i, shot in enumerate(shots) if shot.get("shot_id") == patch["shot_id"]]
        if len(matches) != 1:
            _fail("The requested shot_id does not identify exactly one shot.")
        index = matches[0]
    else:
        index = _integer(patch.get("shot_index"), "shot_index", minimum=1) - 1
        if index >= len(shots):
            _fail("The requested shot_index is outside this plan.")
    amount = _integer(patch.get("shorten_us"), "shorten_us", minimum=1)
    shot = shots[index]
    start, end = _range(shot, "target_in_us", "target_out_us")
    if amount >= end - start:
        _fail("Shortening must leave a non-empty shot; removing a shot needs a separate decision.")
    removed_start = end - amount
    shot["source_out_us"] -= amount
    shot["target_out_us"] -= amount
    for later in shots[index + 1:]:
        later["target_in_us"] -= amount
        later["target_out_us"] -= amount
    for caption in revised.get("captions", []):
        caption_start, caption_end = _range(caption, "in_us", "out_us")
        if caption_start >= end:
            caption["in_us"] -= amount
            caption["out_us"] -= amount
        elif caption_end > removed_start:
            raise AutoCapcutError("E_PLAN_REVIEW", "The removed interval overlaps caption text.", "Re-time or re-recognize the affected caption before shortening this shot.")
    for music in revised.get("music", []):
        music_start, music_end = _range(music, "target_in_us", "target_out_us")
        if music_start >= end:
            music["target_in_us"] -= amount
            music["target_out_us"] -= amount
        elif music_end > removed_start:
            if music_start >= removed_start or music_end < end:
                raise AutoCapcutError("E_PLAN_REVIEW", "The cut removes part of a timed audio cue.", "Choose new timing for the affected audio cue.")
            music["target_out_us"] -= amount
            if "source_out_us" in music:
                music["source_out_us"] -= amount
    revised["target"]["duration_us"] -= amount
    revised["revision"] = revision + 1
    revised["derived_from_revision"] = revision
    return revised


def validate_plan(plan, assets, *, require_evidence=True):
    _object(plan, "plan")
    if plan.get("schema_version") != "1.0":
        _fail("Only plan schema_version 1.0 is supported.")
    _integer(plan.get("revision"), "revision", minimum=1)
    if not isinstance(plan.get("style_id"), str) or not plan["style_id"].strip():
        _fail("A style_id is required.")
    target = _object(plan.get("target"), "target")
    if not isinstance(target.get("aspect_ratio"), str) or not re.fullmatch(r"[1-9]\d*:[1-9]\d*", target["aspect_ratio"]):
        _fail("target.aspect_ratio must contain positive integer dimensions, e.g. 9:16.")
    duration = _integer(target.get("duration_us"), "target.duration_us", minimum=1)
    shots = _list(plan.get("shots"), "shots")
    if not shots:
        _fail("At least one shot is required.")
    source_assets = _asset_index(assets)
    warnings = []
    cursor = 0
    identifiers = set()
    for shot in shots:
        _object(shot, "shot")
        identifier = shot.get("shot_id")
        if not isinstance(identifier, str) or not identifier or identifier in identifiers:
            _fail("Each shot must have a unique non-empty shot_id.")
        identifiers.add(identifier)
        asset = _referenced_asset(source_assets, shot.get("asset_id"))
        if not asset or asset.get("kind") not in {"video", "image"}:
            _fail(f"Shot {identifier} must reference a known video or image asset.")
        source_in, source_out = _range(shot, "source_in_us", "source_out_us")
        target_in, target_out = _range(shot, "target_in_us", "target_out_us")
        if asset["kind"] != "image" and source_out > _integer(asset.get("duration_us"), "asset.duration_us", minimum=1):
            _fail(f"Shot {identifier} exceeds its source duration.")
        if asset["kind"] == "image" and source_in != 0:
            _fail("Still images must start at source time zero.")
        if target_in != cursor or target_out > duration:
            _fail("Shots must form a continuous timeline starting at zero.")
        if source_out - source_in != target_out - target_in:
            _fail("Source and target durations differ; unsupported speed mapping must not be inferred.")
        if not _has_evidence(asset, source_in, source_out) or not shot.get("evidence"):
            warnings.append(f"Shot {identifier} needs content evidence from user annotations, frames or a transcript.")
        if not isinstance(shot.get("decision"), str) or not shot["decision"].strip():
            _fail("Each shot needs an explicit editorial decision.")
        cursor = target_out
    if cursor != duration:
        _fail("The final shot must end at target.duration_us.")
    caption_intervals = []
    for caption in _list(plan.get("captions", []), "captions"):
        _object(caption, "caption")
        if not isinstance(caption.get("text"), str) or not caption["text"].strip():
            _fail("Caption text must not be empty.")
        start, end = _range(caption, "in_us", "out_us")
        if end > duration:
            _fail("Caption exceeds the target duration.")
        caption_intervals.append((start, end))
    for earlier, later in zip(sorted(caption_intervals), sorted(caption_intervals)[1:]):
        if earlier[1] > later[0]:
            _fail("Captions overlap on the caption track.")
    for music in _list(plan.get("music", []), "music"):
        _object(music, "music")
        asset = _referenced_asset(source_assets, music.get("asset_id"))
        if not asset or not (asset.get("kind") == "audio" or asset.get("audio_tracks", 0) > 0):
            _fail("Music must reference a known asset containing audio.")
        start, end = _range(music, "target_in_us", "target_out_us")
        source_start = _integer(music.get("source_in_us", 0), "music.source_in_us")
        source_end = _integer(music.get("source_out_us", source_start + end - start), "music.source_out_us", minimum=1)
        if end > duration or source_end - source_start != end - start:
            _fail("Music timing must fit the target without an inferred speed or loop.")
        if source_end > _integer(asset.get("duration_us"), "audio.duration_us", minimum=1):
            _fail("Music exceeds its source duration.")
        gain = music.get("gain_db")
        if type(gain) not in {int, float} or not math.isfinite(gain):
            _fail("Music gain_db must be a finite number.")
    unresolved = _list(plan.get("unresolved", []), "unresolved")
    if unresolved:
        warnings.append("Resolve outstanding editorial questions before editing.")
    return {"valid": True, "ready_to_edit": not warnings, "duration_us": duration,
            "warnings": warnings, "scope": "local_plan_only", "evidence_required": require_evidence}


def _has_evidence(asset, source_in, source_out):
    for evidence in _list(asset.get("content_evidence", []), "content_evidence"):
        if not isinstance(evidence, dict) or not str(evidence.get("description", "")).strip():
            continue
        if evidence.get("kind") not in {"user_annotation", "user_instruction", "frame", "transcript"}:
            continue
        start = evidence.get("source_in_us", 0)
        end = evidence.get("source_out_us", asset.get("duration_us"))
        if type(start) is not int or type(end) is not int or start > source_in or end < source_out:
            continue
        if evidence["kind"] in {"frame", "transcript"}:
            from pathlib import Path
            path = evidence.get("evidence_path")
            if not path or not Path(path).is_file():
                continue
            if evidence["kind"] == "frame" and evidence.get("content_reviewed") is not True:
                continue
        return True
    return False


def _fail(message):
    raise AutoCapcutError("E_PLAN", message, "Correct the plan against inspected source media, then validate again.")


def _referenced_asset(assets, identifier):
    if not isinstance(identifier, str):
        _fail("asset_id must be a string identifying inspected source media.")
    return assets.get(identifier)


def _object(value, label):
    if not isinstance(value, dict):
        _fail(f"{label} must be an object.")
    return value


def _list(value, label):
    if not isinstance(value, list):
        _fail(f"{label} must be a list.")
    return value


def _integer(value, label, minimum=0):
    if type(value) is not int or value < minimum:
        _fail(f"{label} must be an integer >= {minimum}.")
    return value


def _range(item, start_key, end_key):
    start = _integer(item.get(start_key), start_key)
    end = _integer(item.get(end_key), end_key, minimum=1)
    if end <= start:
        _fail(f"{end_key} must follow {start_key}.")
    return start, end


def _asset_index(assets):
    if isinstance(assets, dict):
        assets = assets.get("assets")
    result = {}
    for asset in _list(assets, "assets"):
        _object(asset, "asset")
        identifier = asset.get("asset_id")
        if not isinstance(identifier, str) or not identifier or identifier in result:
            _fail("Each asset must have a unique non-empty asset_id.")
        if asset.get("exists") is False:
            _fail("An asset is marked missing.")
        result[identifier] = asset
    return result
