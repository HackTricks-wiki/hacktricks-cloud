import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import translation_backlog as backlog


class TranslationBacklogTests(unittest.TestCase):
    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.root).decode().strip()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.original_dir = Path.cwd()
        os.chdir(self.root)
        self.addCleanup(os.chdir, self.original_dir)
        self.git("init", "-b", "master")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.com")
        (self.root / "src").mkdir()
        (self.root / "src" / "old.md").write_text("English v1\n")
        (self.root / "src" / "SUMMARY.md").write_text("# Summary\n")
        self.git("add", "src")
        self.git("commit", "-m", "baseline")
        self.baseline = self.git("rev-parse", "HEAD")
        self.git("checkout", "-b", "af")
        (self.root / "src" / "old.md").write_text("Afrikaans v1\n")
        self.git("add", "src")
        self.git("commit", "-m", "translated baseline")
        self.git("checkout", "master")
        (self.root / "src" / "old.md").write_text("English v2\n")
        (self.root / "src" / "new.md").write_text("New English page\n")
        self.git("add", "src")
        self.git("commit", "-m", "update English pages")
        self.initial_ref = patch.object(backlog, "INITIAL_SOURCE_REF", self.baseline)
        self.initial_ref.start()
        self.addCleanup(self.initial_ref.stop)

    def test_changed_and_added_pages_resume_from_recorded_blobs(self):
        self.assertEqual(
            backlog.pending("af", "master", set()),
            ["src/new.md", "src/old.md"],
        )
        self.git("checkout", "af")
        (self.root / "src" / "new.md").write_text("Nuwe bladsy\n")
        (self.root / "src" / "old.md").write_text("Afrikaans v2\n")
        self.git("add", "src")
        self.git("commit", "-m", "translate batch")
        batch = self.root / "batch.txt"
        batch.write_text("src/new.md\nsrc/old.md\n")
        with patch.object(sys, "argv", ["translation_backlog.py", "mark", "--language", "af", "--file-list", str(batch)]):
            backlog.main()
        state = json.loads(backlog.STATE_PATH.read_text())
        self.assertEqual(state["sources"]["src/new.md"], backlog.markdown_blobs("master")["src/new.md"])
        self.git("add", ".translation-source-blobs.json")
        self.git("commit", "-m", "record source blobs")
        self.assertEqual(backlog.pending("af", "master", set()), [])
        self.assertEqual(backlog.pending("af", "master", {"src/old.md"}), ["src/old.md"])

    def test_missing_language_page_is_pending_even_if_english_is_unchanged(self):
        self.git("checkout", "af")
        self.git("rm", "src/old.md")
        self.git("commit", "-m", "remove translation")
        self.assertIn("src/old.md", backlog.pending("af", self.baseline, set()))


if __name__ == "__main__":
    unittest.main()
