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
        (self.root / "src" / "SUMMARY.md").write_text("# Summary\n\n# Welcome!\n\n- [About the author](old.md)\n")
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
            ["src/new.md", "src/old.md", backlog.SUMMARY_PATH],
        )
        self.git("checkout", "af")
        (self.root / "src" / "new.md").write_text("Nuwe bladsy\n")
        (self.root / "src" / "old.md").write_text("Afrikaans v2\n")
        (self.root / backlog.SUMMARY_PATH).write_text(
            "# Summary\n\n# Welkom!\n\n- [Oor die skrywer](old.md)\n"
        )
        self.git("add", "src")
        self.git("commit", "-m", "translate batch")
        batch = self.root / "batch.txt"
        batch.write_text("src/new.md\nsrc/old.md\nsrc/SUMMARY.md\n")
        with patch.object(sys, "argv", ["translation_backlog.py", "mark", "--language", "af", "--file-list", str(batch)]):
            backlog.main()
        state = json.loads(backlog.STATE_PATH.read_text())
        self.assertEqual(state["sources"]["src/new.md"], backlog.markdown_blobs("master")["src/new.md"])
        self.git("add", ".translation-source-blobs.json")
        self.git("commit", "-m", "record source blobs")
        self.assertEqual(backlog.pending("af", "master", set()), [])
        self.assertEqual(backlog.pending("af", "master", {"src/old.md"}), ["src/old.md"])

    def test_historical_english_copy_is_pending_despite_checkpoint(self):
        path = self.root / "src/old.md"
        english = "This is the original text and it should be translated before publication.\n"
        path.write_text(english)
        self.git("commit", "-am", "Add English prose")
        path.write_text("Here is a new version with different wording for the reader to review.\n")
        self.git("commit", "-am", "Revise English prose")
        self.git("checkout", "af")
        path.write_text(english)
        self.git("commit", "-am", "Accidentally copy original English")
        backlog.record_translations("master", ["src/old.md"], {})
        self.git("add", str(backlog.STATE_PATH))
        self.git("commit", "-m", "Record incorrect checkpoint")

        report = backlog.audit("af", backlog.markdown_blobs("master"), backlog.markdown_blobs("af"),
                               backlog.english_history("master"))
        self.assertEqual(report["untranslated"], [backlog.SUMMARY_PATH, "src/old.md"])
        self.assertIn("src/old.md", backlog.pending("af", "master", set()))

    def test_detailed_audit_checks_structure_against_recorded_source(self):
        path = self.root / "src/old.md"
        path.write_text("Read [the guide](guide.md).\n")
        self.git("commit", "-am", "Add source link")
        recorded = self.git("rev-parse", "HEAD")
        path.write_text("Read [the updated guide](guide-v2.md).\n\nNew paragraph.\n")
        self.git("commit", "-am", "Revise source link and add a paragraph")
        self.git("checkout", "af")
        path.write_text("Lees [die gids](guide.md).\n")
        backlog.record_translations(recorded, ["src/old.md"], {})
        self.git("add", str(backlog.STATE_PATH), "src/old.md")
        self.git("commit", "-m", "Publish translation of the first guide")
        source = backlog.markdown_blobs("master")
        history = backlog.english_history("master")

        report = backlog.audit("af", source, backlog.markdown_blobs("af"), history, detailed=True)
        self.assertEqual(report["source_advanced"], ["src/old.md"])
        self.assertEqual(report["checkpoint_unverified"], [backlog.SUMMARY_PATH])
        self.assertEqual(report["structural_review"], {})

        path.write_text("Lees [die gids](verkeerd.md).\n")
        self.git("commit", "-am", "Break a link in the localized copy")
        report = backlog.audit("af", source, backlog.markdown_blobs("af"), history, detailed=True)
        self.assertIn("src/old.md", report["structural_review"])

    def test_checkpoint_does_not_record_the_inferred_legacy_baseline_as_translated(self):
        self.git("checkout", "af")
        state, baseline = backlog.checkpoint_for_update("af")
        self.assertEqual((state, baseline), ({}, self.baseline))
        (self.root / backlog.SUMMARY_PATH).write_text("# Summary\n\n# Welkom!\n")
        backlog.record_translations("master", [backlog.SUMMARY_PATH], state, assumed_baseline=baseline)
        self.git("add", "src", str(backlog.STATE_PATH))
        self.git("commit", "-m", "Record one verified localization")

        recorded = backlog.recorded_sources("af")
        self.assertEqual(set(recorded), {backlog.SUMMARY_PATH})
        plan = backlog.load_state("af", backlog.markdown_blobs("af").keys())
        self.assertEqual(plan["src/old.md"], backlog.markdown_blobs(self.baseline)["src/old.md"])
        result = backlog.audit("af", backlog.markdown_blobs("master"), backlog.markdown_blobs("af"),
                               backlog.english_history("master"), detailed=True)
        self.assertIn("src/old.md", result["checkpoint_unverified"])

    def test_reuse_navigation_requires_the_current_exact_chapter_title(self):
        page = self.root / "src/old.md"
        page.write_text("# Read the guide\n")
        self.git("commit", "-am", "Add English chapter title")
        english = self.git("rev-parse", "HEAD")
        self.git("checkout", "af")
        page.write_text(
            '# <span class="translation-source-anchor" id="read-the-guide"></span>Lees die gids\n'
        )
        backlog.record_translations(english, ["src/old.md"], {})
        self.git("add", "src", str(backlog.STATE_PATH))
        self.git("commit", "-m", "Translate the current chapter title")

        files = backlog.markdown_blobs(english)
        summary = (
            "# Summary\n\n- [Read the guide](old.md)\n"
            "- [Short guide](old.md)\n- [About the guide](old.md#appendix)\n"
            "- [Read the guide](https://example.org/old.md)\n"
        )
        self.assertEqual(backlog.reusable_chapter_labels(summary, files, "af"), {"Read the guide": "Lees die gids"})
        self.git("checkout", "master")
        page.write_text("# Read the updated guide\n")
        self.git("commit", "-am", "Advance the English source")
        self.assertEqual(backlog.reusable_chapter_labels(summary, backlog.markdown_blobs("master"), "af"), {})

    def test_restore_anchors_uses_only_real_checkpoints_from_english_history(self):
        page = self.root / "src" / "old.md"
        page.write_text("# Read the guide\n")
        self.git("commit", "-am", "English heading")
        revision = self.git("rev-parse", "HEAD")
        page.write_text("# Read the revised guide\n")
        self.git("commit", "-am", "Change the source heading after translation")
        self.git("checkout", "af")
        page.write_text("# Lees die gids\n")
        (self.root / "src" / "new.md").write_text("# Nuwe bladsy\n")
        backlog.record_translations(revision, ["src/old.md"], {})
        before = self.git("rev-parse", "HEAD")
        self.git("add", "src", str(backlog.STATE_PATH))
        self.git("commit", "-m", "Translated guide plus an untracked revision")
        published = self.git("rev-parse", "HEAD")

        self.assertEqual(backlog.restore_anchors("af", "master"), (["src/old.md"], 1))
        self.assertIn('id="read-the-guide"', page.read_text())
        self.assertNotIn("read-the-revised-guide", page.read_text())
        self.assertEqual((self.root / "src" / "new.md").read_text(), "# Nuwe bladsy\n")
        self.assertEqual(self.git("rev-parse", "HEAD"), published)
        self.assertNotEqual(published, before)

    def test_restore_anchors_leaves_dirty_working_source_alone(self):
        self.git("checkout", "af")
        page = self.root / "src" / "old.md"
        page.write_text("Unsaved derivative edit\n")
        with self.assertRaisesRegex(ValueError, "must be clean"):
            backlog.restore_anchors("af", "master")
        self.assertEqual(page.read_text(), "Unsaved derivative edit\n")

    def test_rendered_bookmarks_do_not_shadow_an_existing_section(self):
        path = self.root / "guide.html"
        markup = '<h2 id="source">Section</h2><span class="translation-source-anchor" id="source"></span>'
        path.write_text(markup)
        with self.assertRaisesRegex(ValueError, "duplicates a rendered ID in guide.html"):
            backlog.check_rendered_anchor_collisions(self.root)
        path.write_text(markup.replace('<h2 id="source">', '<h2 id="localized">'))
        (self.root / "print.html").write_text(markup)
        backlog.check_rendered_anchor_collisions(self.root)

    def test_sidebar_script_rejects_stale_embedded_labels(self):
        localized = "# Summary\n\n# Bienvenue !\n\n- [À propos de l'auteur](author.md)\n"
        markup = (
            '<li class="part-title">Bienvenue !</li>'
            '<span class="chapter-link-wrapper"><a href="author.html">À propos de l’auteur</a></span>'
        )
        script = "var toc = '" + markup + "';\n"
        backlog.check_sidebar_script(localized, script, "fr")
        with self.assertRaisesRegex(ValueError, "chapter 1 differs"):
            backlog.check_sidebar_script(localized, script.replace("À propos de l’auteur", "About the author"), "fr")
        with self.assertRaisesRegex(ValueError, "Cannot find the embedded sidebar"):
            backlog.check_sidebar_script(localized, "const toc = null;", "fr")

    def test_rendered_sidebar_rejects_english_fallback_with_correct_lang_tag(self):
        summary = "# Summary\n\n# Boas-vindas!\n"
        rendered = '<html lang="pt"><li class="part-title">Boas-vindas!</li></html>'
        backlog.check_rendered_sidebar(summary, rendered, "pt")
        with self.assertRaisesRegex(ValueError, "section 1 differs"):
            backlog.check_rendered_sidebar(summary, rendered.replace("Boas-vindas!", "Welcome!"), "pt")
        with self.assertRaisesRegex(ValueError, "language pt, got en"):
            backlog.check_rendered_sidebar(summary, rendered.replace('lang="pt"', 'lang="en"'), "pt")

    def test_rendered_sidebar_rejects_untranslated_chapter_or_changed_destination(self):
        summary = (
            "# Summary\n\n# Boas-vindas!\n\n"
            "- [Guia de leitura](guide/README.md)\n"
            "  - [Sobre o autor$$external:https://example.org/author?from=toc$$]()\n"
        )
        rendered = (
            '<html lang="pt"><li class="part-title">Boas-vindas!</li>'
            '<span class="chapter-link-wrapper"><a href="guide/index.html"><strong aria-hidden="true">1.</strong> Guia de leitura</a>'
            '<a class="chapter-fold-toggle"><div>❱</div></a></span>'
            '<span class="chapter-link-wrapper">'
            '<span>Sobre o autor$$external:https://example.org/author?from=toc$$</span></span></html>'
        )
        backlog.check_rendered_sidebar(summary, rendered, "pt")
        for previous, replacement, failure in (
            ("Guia de leitura", "Reading guide", "chapter 1 differs"),
            ("guide/index.html", "guide/other.html", "chapter 1 destination differs"),
            ("example.org/author?from=toc", "example.org/author/from=toc", "chapter 2 external destination differs"),
        ):
            with self.subTest(previous=previous):
                with self.assertRaisesRegex(ValueError, failure):
                    backlog.check_rendered_sidebar(summary, rendered.replace(previous, replacement), "pt")

    def test_missing_language_page_is_pending_even_if_english_is_unchanged(self):
        self.git("checkout", "af")
        self.git("rm", "src/old.md")
        self.git("commit", "-m", "remove translation")
        self.assertIn("src/old.md", backlog.pending("af", self.baseline, set()))


if __name__ == "__main__":
    unittest.main()
