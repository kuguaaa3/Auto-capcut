"""Actual local decode QA on technical fixtures, never CapCut acceptance."""

import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "skills/auto-capcut/scripts"))

from autocapcut.qa import verify_media
from autocapcut.media import extract_frame, inspect_media
from autocapcut.errors import AutoCapcutError


class QATests(unittest.TestCase):
    def test_missing_export_is_not_a_successful_video(self):
        with tempfile.TemporaryDirectory() as folder:
            report = verify_media(pathlib.Path(folder) / "never-exported.mp4")
        self.assertFalse(report["passed"])
        self.assertEqual(report["review_status"], "failed")
        self.assertEqual(report["checks"][0]["error"]["code"], "E_MEDIA_MISSING")


@unittest.skipUnless((os.environ.get("AUTO_CAPCUT_FFPROBE") or shutil.which("ffprobe")) and
                     (os.environ.get("AUTO_CAPCUT_FFMPEG") or shutil.which("ffmpeg")), "ffprobe/ffmpeg not configured")
class ActualDecodeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder = tempfile.TemporaryDirectory()
        cls.source = pathlib.Path(cls.folder.name) / "技术 样本.mp4"
        ffmpeg = os.environ.get("AUTO_CAPCUT_FFMPEG") or shutil.which("ffmpeg")
        subprocess.run([ffmpeg, "-v", "error", "-nostdin", "-f", "lavfi", "-i", "color=c=red:s=160x90:r=25:d=1",
                        "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=44100:duration=1",
                        "-c:v", "mpeg4", "-q:v", "5", "-c:a", "aac", "-shortest", str(cls.source)],
                       check=True, capture_output=True, timeout=30)

    @classmethod
    def tearDownClass(cls):
        cls.folder.cleanup()

    def test_actual_video_decodes_and_matches_requested_technical_format(self):
        report = verify_media(self.source, {"duration_us": 1_000_000, "width": 160, "height": 90, "audio_tracks": 1})
        self.assertTrue(report["passed"], report)
        self.assertEqual(report["review_status"], "technical_pass")
        self.assertEqual(report["scope"], "local_media_only")
        self.assertIn("editor_reopen_and_editability", report["unverified"])

    def test_actual_wrong_dimensions_and_missing_decoder_do_not_pass(self):
        report = verify_media(self.source, {"width": 1080})
        self.assertFalse(report["passed"])
        self.assertEqual(next(c for c in report["checks"] if c["id"] == "width")["status"], "failed")
        report = verify_media(self.source, ffmpeg=pathlib.Path(self.folder.name) / "missing-decoder")
        self.assertEqual(report["review_status"], "blocked")

    def test_actual_black_frames_require_review(self):
        black = pathlib.Path(self.folder.name) / "black.mp4"
        ffmpeg = os.environ.get("AUTO_CAPCUT_FFMPEG") or shutil.which("ffmpeg")
        subprocess.run([ffmpeg, "-v", "error", "-nostdin", "-f", "lavfi", "-i", "color=c=black:s=160x90:r=25:d=1",
                        "-c:v", "mpeg4", "-q:v", "5", str(black)], check=True, capture_output=True, timeout=30)
        report = verify_media(black)
        self.assertFalse(report["passed"])
        self.assertEqual(next(c for c in report["checks"] if c["id"] == "black_frames")["status"], "review")

    def test_extracts_a_real_frame_for_visual_inspection_without_overwriting(self):
        frame = pathlib.Path(self.folder.name) / "evidence.png"
        evidence = extract_frame(self.source, 400_000, frame)
        self.assertEqual(evidence["kind"], "frame")
        self.assertEqual(frame.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
        self.assertEqual(inspect_media(frame)["kind"], "image")
        self.assertEqual(evidence["source_in_us"], 400_000)
        before = frame.read_bytes()
        with self.assertRaises(AutoCapcutError):
            extract_frame(self.source, 400_000, frame)
        self.assertEqual(frame.read_bytes(), before)
        with self.assertRaises(AutoCapcutError):
            extract_frame(self.source, True, pathlib.Path(self.folder.name) / "invalid.png")
        with self.assertRaises(AutoCapcutError):
            extract_frame(self.source, 1_000_000, pathlib.Path(self.folder.name) / "beyond.png")

    def test_actual_silence_is_reported_for_listening_review(self):
        silent = pathlib.Path(self.folder.name) / "silent.mp4"
        ffmpeg = os.environ.get("AUTO_CAPCUT_FFMPEG") or shutil.which("ffmpeg")
        subprocess.run([ffmpeg, "-v", "error", "-nostdin", "-f", "lavfi", "-i", "color=c=red:s=160x90:r=25:d=1",
                        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "1", "-c:v", "mpeg4", "-c:a", "aac", str(silent)],
                       check=True, capture_output=True, timeout=30)
        report = verify_media(silent)
        self.assertFalse(report["passed"])
        self.assertEqual(next(c for c in report["checks"] if c["id"] == "silence")["status"], "review")

    def test_video_source_bound_does_not_extend_to_a_longer_audio_track(self):
        source = pathlib.Path(self.folder.name) / "long-audio.mp4"
        ffmpeg = os.environ.get("AUTO_CAPCUT_FFMPEG") or shutil.which("ffmpeg")
        subprocess.run([ffmpeg, "-v", "error", "-nostdin", "-f", "lavfi", "-i", "color=c=red:s=160x90:r=25:d=1",
                        "-f", "lavfi", "-i", "sine=duration=2", "-c:v", "mpeg4", "-c:a", "aac", str(source)],
                       check=True, capture_output=True, timeout=30)
        self.assertEqual(inspect_media(source)["duration_us"], 1_000_000)
        self.assertFalse(verify_media(source, {"duration_us": 1_000_000})["passed"])




if __name__ == "__main__":
    unittest.main()
