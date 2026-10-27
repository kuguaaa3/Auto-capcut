"""Plan contract tests exercise public validation, not an editing engine."""

import copy
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "skills/auto-capcut/scripts"))

from autocapcut.errors import AutoCapcutError
from autocapcut.plan import validate_plan, frames_to_us, us_to_frame, revise_plan


def example():
    assets = [{"asset_id": "v1", "kind": "video", "duration_us": 10_000_000,
               "content_evidence": [{"kind": "user_annotation", "description": "User selected these source ranges.",
                                     "source_in_us": 0, "source_out_us": 10_000_000}]}]
    plan = {"schema_version": "1.0", "revision": 1, "style_id": "pet-healing",
            "target": {"aspect_ratio": "9:16", "duration_us": 6_000_000},
            "shots": [{"shot_id": f"s{i + 1}", "asset_id": "v1", "source_in_us": i * 2_000_000,
                       "source_out_us": (i + 1) * 2_000_000, "target_in_us": i * 2_000_000,
                       "target_out_us": (i + 1) * 2_000_000,
                       "decision": "Keep the user-selected action.", "evidence": "User-selected source range."}
                      for i in range(3)], "captions": [], "music": [], "unresolved": []}
    return plan, assets


class PlanTests(unittest.TestCase):
    def test_fractional_frame_conversion_does_not_accumulate_float_drift(self):
        self.assertEqual(frames_to_us(30000, 30000, 1001), 1_001_000_000)
        self.assertEqual(frames_to_us(1, 30000, 1001), 33366)
        self.assertEqual(us_to_frame(1_001_000_000, 30000, 1001), 30000)
        with self.assertRaises(AutoCapcutError):
            frames_to_us(True, 30, 1)

    def test_valid_user_annotated_plan_is_ready_without_changing_input(self):
        plan, assets = example()
        before = copy.deepcopy(plan)
        report = validate_plan(plan, assets)
        self.assertTrue(report["valid"])
        self.assertTrue(report["ready_to_edit"])
        self.assertEqual(report["duration_us"], 6_000_000)
        self.assertEqual(plan, before)

    def test_rejects_out_of_source_and_discontinuous_target_ranges(self):
        for field, value in [("source_out_us", 10_000_001), ("target_in_us", 1),
                             ("source_in_us", -1), ("source_out_us", 0),
                             ("target_out_us", 2_000_000.0), ("target_in_us", False)]:
            with self.subTest(field=field, value=value):
                plan, assets = example()
                plan["shots"][0][field] = value
                with self.assertRaises(AutoCapcutError) as caught:
                    validate_plan(plan, assets)
                self.assertEqual(caught.exception.code, "E_PLAN")

    def test_missing_content_evidence_or_unresolved_questions_blocks_editing(self):
        plan, assets = example()
        assets[0]["content_evidence"] = []
        report = validate_plan(plan, assets)
        self.assertFalse(report["ready_to_edit"])
        self.assertIn("content evidence", " ".join(report["warnings"]))
        plan, assets = example()
        plan["unresolved"] = ["Which ending should be kept?"]
        self.assertFalse(validate_plan(plan, assets)["ready_to_edit"])

    def test_rejects_caption_drift_overlap_and_unreadable_text(self):
        for captions in [
            [{"text": "end", "in_us": 5_000_000, "out_us": 6_000_001}],
            [{"text": "", "in_us": 0, "out_us": 1_000_000}],
            [{"text": "one", "in_us": 0, "out_us": 2_000_000},
             {"text": "two", "in_us": 1_000_000, "out_us": 3_000_000}],
        ]:
            with self.subTest(captions=captions):
                plan, assets = example()
                plan["captions"] = captions
                with self.assertRaises(AutoCapcutError):
                    validate_plan(plan, assets)

    def test_rejects_music_without_a_real_source_range_or_finite_gain(self):
        for change in [{"gain_db": float("nan")}, {"gain_db": True}, {"target_out_us": 6_000_001},
                       {"source_in_us": 5_000_000}, {"asset_id": "unknown"}]:
            with self.subTest(change=change):
                plan, assets = example()
                assets.append({"asset_id": "m1", "kind": "audio", "duration_us": 7_000_000})
                music = {"asset_id": "m1", "target_in_us": 0, "target_out_us": 6_000_000, "gain_db": -18}
                music.update(change)
                plan["music"] = [music]
                with self.assertRaises(AutoCapcutError):
                    validate_plan(plan, assets)

    def test_rejects_unknown_schema_invalid_revision_and_aspect_ratio(self):
        for change in [{"schema_version": "future"}, {"revision": True}, {"style_id": ""},
                       {"target": {"duration_us": 6_000_000, "aspect_ratio": "0:16"}}]:
            with self.subTest(change=change):
                plan, assets = example()
                plan.update(change)
                with self.assertRaises(AutoCapcutError):
                    validate_plan(plan, assets)

    def test_shortening_third_shot_preserves_old_plan_and_later_source_ranges(self):
        plan, assets = example()
        plan["target"]["duration_us"] = 8_000_000
        plan["shots"].append({"shot_id": "s4", "asset_id": "v1", "source_in_us": 6_000_000,
                              "source_out_us": 8_000_000, "target_in_us": 6_000_000,
                              "target_out_us": 8_000_000, "decision": "User-selected ending", "evidence": "User"})
        plan["captions"] = [{"text": "Ending", "in_us": 6_200_000, "out_us": 7_500_000}]
        before = copy.deepcopy(plan)
        revised = revise_plan(plan, {"shot_index": 3, "shorten_us": 1_000_000})
        self.assertEqual(plan, before)
        self.assertEqual(revised["revision"], 2)
        self.assertEqual(revised["target"]["duration_us"], 7_000_000)
        self.assertEqual(revised["shots"][2]["source_out_us"], 5_000_000)
        self.assertEqual(revised["shots"][3]["source_in_us"], 6_000_000)
        self.assertEqual(revised["shots"][3]["target_in_us"], 5_000_000)
        self.assertEqual(revised["captions"][0]["in_us"], 5_200_000)
        self.assertTrue(validate_plan(revised, assets)["ready_to_edit"])

    def test_shortening_trims_bgm_tail_and_requires_review_of_caption_overlap(self):
        plan, assets = example()
        assets.append({"asset_id": "m1", "kind": "audio", "duration_us": 6_000_000})
        plan["music"] = [{"asset_id": "m1", "target_in_us": 0, "target_out_us": 6_000_000,
                          "source_in_us": 0, "source_out_us": 6_000_000, "gain_db": -18}]
        revised = revise_plan(plan, {"shot_id": "s3", "shorten_us": 1_000_000})
        self.assertEqual(revised["music"][0]["target_out_us"], 5_000_000)
        self.assertEqual(revised["music"][0]["source_out_us"], 5_000_000)
        self.assertTrue(validate_plan(revised, assets)["ready_to_edit"])
        plan["captions"] = [{"text": "Do not cut a word", "in_us": 4_000_000, "out_us": 5_500_000}]
        with self.assertRaises(AutoCapcutError) as caught:
            revise_plan(plan, {"shot_id": "s3", "shorten_us": 1_000_000})
        self.assertEqual(caught.exception.code, "E_PLAN_REVIEW")

    def test_music_gain_patch_is_versioned_and_unknown_or_ambiguous_patches_fail(self):
        plan, _ = example()
        plan["music"] = [{"asset_id": "m1", "target_in_us": 0, "target_out_us": 6_000_000, "gain_db": -18}]
        changed = revise_plan(plan, {"kind": "music_gain", "music_index": 1, "gain_db": -24})
        self.assertEqual(changed["music"][0]["gain_db"], -24)
        self.assertEqual(plan["music"][0]["gain_db"], -18)
        self.assertEqual(changed["revision"], 2)
        for patch in [{"kind": "rebuild"}, {"shot_id": "s1", "shot_index": 2, "shorten_us": 1},
                      {"shot_id": "s1", "shorten_us": 2_000_000},
                      {"kind": "music_gain", "music_index": 1, "gain_db": float("inf")}]:
            with self.subTest(patch=patch), self.assertRaises(AutoCapcutError):
                revise_plan(plan, patch)

    def test_malformed_source_identity_and_evidence_return_structured_errors(self):
        plan, assets = example()
        plan["shots"][0]["asset_id"] = []
        with self.assertRaises(AutoCapcutError):
            validate_plan(plan, assets)
        plan, assets = example()
        assets[0]["content_evidence"] = None
        with self.assertRaises(AutoCapcutError):
            validate_plan(plan, assets)


if __name__ == "__main__":
    unittest.main()
