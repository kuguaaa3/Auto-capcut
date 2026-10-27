"""Local media inspection checks; no CapCut edits are simulated."""

import pathlib
import os
import shutil
import sys
import tempfile
import unittest
import wave

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "skills/auto-capcut/scripts"))

from autocapcut.errors import AutoCapcutError
from autocapcut.media import inspect_media, inspect_assets


class MediaTests(unittest.TestCase):
    @unittest.skipUnless(os.environ.get("AUTO_CAPCUT_FFPROBE") or shutil.which("ffprobe"), "ffprobe not configured")
    def test_corrupt_media_has_a_decode_error(self):
        with tempfile.TemporaryDirectory() as folder:
            source = pathlib.Path(folder) / "broken.mp4"
            source.write_bytes(b"not a movie")
            with self.assertRaises(AutoCapcutError) as caught:
                inspect_media(source)
            self.assertEqual(caught.exception.code, "E_MEDIA_DECODE")

    def test_probe_prerequisite_is_reported_without_downloading(self):
        with tempfile.TemporaryDirectory() as folder:
            source = pathlib.Path(folder) / "clip.mp4"
            source.write_bytes(b"not decoded")
            with self.assertRaises(AutoCapcutError) as caught:
                inspect_media(source, ffprobe=pathlib.Path(folder) / "missing-ffprobe")
            self.assertEqual(caught.exception.code, "E_MEDIA_TOOL")

    def test_an_empty_material_folder_is_not_ready_input(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(AutoCapcutError) as caught:
                inspect_assets([folder])
            self.assertEqual(caught.exception.code, "E_MEDIA_EMPTY")

    def test_missing_media_has_a_recoverable_error(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(AutoCapcutError) as caught:
                inspect_media(pathlib.Path(folder) / "missing.mp4")
        self.assertEqual(caught.exception.code, "E_MEDIA_MISSING")
        self.assertTrue(caught.exception.recovery)

    @unittest.skipUnless(os.environ.get("AUTO_CAPCUT_FFPROBE") or shutil.which("ffprobe"), "ffprobe not configured")
    def test_reads_actual_unicode_audio_without_inventing_content(self):
        with tempfile.TemporaryDirectory() as folder:
            source = pathlib.Path(folder) / "声音 测试.wav"
            with wave.open(str(source), "wb") as audio:
                audio.setnchannels(1)
                audio.setsampwidth(2)
                audio.setframerate(8000)
                audio.writeframes(b"\0\0" * 8000)
            asset = inspect_media(source)
            self.assertEqual(asset["duration_us"], 1_000_000)
            self.assertEqual(asset["kind"], "audio")
            self.assertEqual(asset["audio_tracks"], 1)
            self.assertEqual(asset["content_evidence"], [])
            self.assertEqual(len(asset["hash"]), 64)
            self.assertEqual(source.stat().st_size, 16044)


if __name__ == "__main__":
    unittest.main()
