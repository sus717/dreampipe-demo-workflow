from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from export_web_demo import build_demo


class WebDemoTests(unittest.TestCase):
    def test_shared_contracts_reach_frontend_with_selective_retry(self):
        demo = build_demo()
        snapshots = demo["snapshots"]
        self.assertEqual(snapshots["waiting"]["status"]["status"], "WAITING_FOR_ASSETS")
        retries = snapshots["retrying"]["status"]["retry"]["shots"]
        self.assertLess(snapshots["retrying"]["status"]["progress"]["percent"], 100)
        self.assertEqual([shot["shot_id"] for shot in retries if shot["status"] == "RETRYING"], ["S03"])
        final = snapshots["completed"]["status"]
        self.assertEqual(final["qa"]["summary"]["passed"], 3)
        self.assertEqual([shot["attempt"] for shot in final["retry"]["shots"]], [1, 1, 2])
        self.assertEqual(final["final_output"], {"status": "PENDING"})
        self.assertFalse(demo["has_real_video"])
