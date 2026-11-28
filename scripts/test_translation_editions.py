"""Verify edition reports use pinned Git revisions without modifying the checkout."""

from pathlib import Path
import os
import subprocess
import tempfile
import unittest

from audit_translation_editions import audit_editions


class AuditTranslationEditionsTests(unittest.TestCase):
    def test_reports_both_locales_at_their_remote_tracking_revisions(self):
        with tempfile.TemporaryDirectory() as directory:
            original_directory = Path.cwd()
            try:
                os.chdir(directory)

                def git(*args):
                    return subprocess.check_output(["git", *args], text=True).strip()

                git("init", "-b", "master")
                git("config", "user.name", "Translation audit")
                git("config", "user.email", "audit@example.org")
                Path("src").mkdir()
                page = Path("src/guide.md")
                page.write_text("This is the first version of the guide and it will help you with the forms.\n")
                git("add", "src")
                git("commit", "-m", "English guide")
                baseline = git("rev-parse", "HEAD")
                git("update-ref", "refs/remotes/origin/pt", baseline)
                git("checkout", "-b", "fr")
                page.write_text("La première version du guide explique comment remplir les formulaires.\n")
                git("commit", "-am", "French guide")
                french = git("rev-parse", "HEAD")
                git("update-ref", "refs/remotes/origin/fr", french)
                git("checkout", "master")

                report = audit_editions("master", ("fr", "pt"), workers=1)
                self.assertEqual(report["english_source_commit"], baseline)
                self.assertEqual(report["english_markdown_files"], 1)
                self.assertEqual(set(report["languages"]), {"fr", "pt"})
                self.assertEqual(report["languages"]["fr"]["commit"], french)
                self.assertEqual(report["languages"]["fr"]["findings"]["untranslated"], [])
                portuguese = report["languages"]["pt"]
                self.assertEqual(portuguese["commit"], baseline)
                self.assertEqual(portuguese["counts"]["untranslated"], 1)
                self.assertEqual(portuguese["findings"]["untranslated"], ["src/guide.md"])
                self.assertEqual(git("status", "--porcelain"), "")
                self.assertEqual(git("rev-parse", "HEAD"), baseline)
            finally:
                os.chdir(original_directory)


if __name__ == "__main__":
    unittest.main()
