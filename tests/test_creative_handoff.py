from __future__ import annotations

from pathlib import Path
import unittest

from dreampipe.brief_normalizer import load_and_normalize
from dreampipe.creative_handoff import CreativeHandoffError, load_creative_handoff


ROOT = Path(__file__).resolve().parents[1]


class CreativeHandoffTests(unittest.TestCase):
    def test_pod2_handoff_matches_frozen_brief(self):
        job = load_and_normalize(ROOT / "shared" / "brief.json")
        handoff = load_creative_handoff(job)
        self.assertEqual(handoff["project_bible"]["project_id"], job["job_id"])
        self.assertEqual([shot["shot_id"] for shot in handoff["shots"]], ["S01", "S02", "S03"])
        self.assertEqual(sum(shot["duration_seconds"] for shot in handoff["shots"]), 15)

    def test_rejects_handoff_for_another_project(self):
        job = load_and_normalize(ROOT / "shared" / "brief.json")
        job["job_id"] = "another-project"
        with self.assertRaises(CreativeHandoffError):
            load_creative_handoff(job)


if __name__ == "__main__":
    unittest.main()
