"""Checks for the anonymous InstallScout usage event."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from app import build_event, post_event, session_id, shorten_locale, windows_locale_name


class UsageEventTest(unittest.TestCase):
    def test_session_id_is_digits_and_is_reused_within_the_hour(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            os.environ["LOCALAPPDATA"] = directory
            first = session_id(1_800_000_000)
            second = session_id(1_800_000_100)
            self.assertTrue(first.isdigit())
            self.assertGreaterEqual(len(first), 10)
            self.assertLessEqual(len(first), 20)
            self.assertEqual(first, second)
            stored = json.loads(Path(directory, "InstallScout", "usage-session.json").read_text(encoding="utf-8"))
            self.assertEqual(stored["id"], first)
            later = session_id(1_800_000_100 + 60 * 60)
            self.assertNotEqual(first, later)

    def test_event_has_no_paths_or_names(self) -> None:
        event = build_event("1.8.65", True, session="180000000012345678")
        encoded = json.dumps(event)
        self.assertEqual(event["eventName"], "app_start")
        self.assertEqual(event["props"], {"source": "program"})
        self.assertTrue(event["systemProps"]["isDebug"])
        self.assertEqual(event["systemProps"]["appVersion"], "1.8.65")
        self.assertLessEqual(len(event["systemProps"]["locale"]), 10)
        self.assertNotIn("English_United", event["systemProps"]["locale"])
        self.assertNotIn("Danish_Denmark", event["systemProps"]["locale"])
        self.assertNotIn("tenant", encoded.lower())
        self.assertNotIn("argv", encoded.lower())
        self.assertNotIn("\\", encoded)

    def test_aptabase_accepts_a_debug_event(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            os.environ["LOCALAPPDATA"] = directory
            status = post_event(build_event("1.8.65", True))
        self.assertEqual(status, 200)

    def test_windows_locale_names_fit_the_aptabase_limit(self) -> None:
        self.assertEqual(windows_locale_name(), "")
        self.assertEqual(shorten_locale("en_US.UTF-8"), "en-US")
        self.assertEqual(shorten_locale("da-DK"), "da-DK")
        self.assertEqual(shorten_locale("English_United States"), "English-Un")
        self.assertLessEqual(len(shorten_locale("Danish_Denmark")), 10)
        self.assertLessEqual(len(shorten_locale("English_United States")), 10)


if __name__ == "__main__":
    unittest.main()
