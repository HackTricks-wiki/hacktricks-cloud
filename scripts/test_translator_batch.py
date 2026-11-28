import os
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import translator
from translation_quality import (
    check_rendered_sidebar, copied_sentence, markdown_problems, preserve_source_heading_anchors,
    repair_cjk_bold_boundaries, suspected_english_blocks,
)


class FailingClient:
    class chat:
        class completions:
            @staticmethod
            def create(**_kwargs):
                raise RuntimeError("temporary translation error")


class TranslationBatchTests(unittest.TestCase):
    def test_publish_preserves_unrelated_updates_and_aborts_on_conflicts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            def git(repo, *args):
                return subprocess.check_output(["git", *args], cwd=repo, text=True).strip()

            remote, local, editor = (root / name for name in ("remote.git", "local", "editor"))
            git(root, "init", "--bare", "--initial-branch=fr", str(remote))
            git(root, "clone", str(remote), str(local))
            for name in ("guide.md", "notes.md"):
                (local / name).write_text("Original\n", encoding="utf-8")
            git(local, "config", "user.name", "Translator Fixture")
            git(local, "config", "user.email", "translation@example.org")
            git(local, "add", "-A")
            git(local, "commit", "-m", "Original files")
            git(local, "push", "origin", "fr")
            git(root, "clone", str(remote), str(editor))
            git(editor, "config", "user.name", "Editor Fixture")
            git(editor, "config", "user.email", "editor@example.org")
            (editor / "notes.md").write_text("Editorial change\n", encoding="utf-8")
            git(editor, "commit", "-am", "Concurrent notes update")
            git(editor, "push", "origin", "fr")

            previous = Path.cwd()
            try:
                os.chdir(local)
                (local / "guide.md").write_text("Traduction\n", encoding="utf-8")
                translator.commit_and_push(["guide.md"], "fr")
                self.assertEqual(git(remote, "show", "fr:notes.md"), "Editorial change")
                self.assertEqual(git(remote, "show", "fr:guide.md"), "Traduction")

                git(editor, "pull", "--ff-only")
                (editor / "guide.md").write_text("Révision\n", encoding="utf-8")
                git(editor, "commit", "-am", "Concurrent chapter update")
                git(editor, "push", "origin", "fr")
                (local / "guide.md").write_text("Nouvelle traduction\n", encoding="utf-8")
                with self.assertRaises(subprocess.CalledProcessError):
                    translator.commit_and_push(["guide.md"], "fr")
                self.assertEqual(git(remote, "show", "fr:guide.md"), "Révision")
                self.assertEqual(git(local, "status", "--porcelain"), "")
                self.assertEqual(git(local, "branch", "--show-current"), "fr")
            finally:
                os.chdir(previous)

    @unittest.skipUnless(shutil.which("mdbook"), "mdBook is required for the translation integration test")
    def test_git_and_mdbook_integration_blocks_swapped_links_then_publishes_valid_output(self):
        cli = str(Path(translator.__file__).resolve())
        source = (
            "# Reading guide\n\nOpen the [library](https://example.org/library).\n\n"
            "Read the [catalog](https://example.org/catalog).\n\nReceipts\n--------\n"
        )
        localized = (
            "# Guide de lecture\n\nOuvrez la [bibliothèque](https://example.org/library).\n\n"
            "Consultez le [catalogue](https://example.org/catalog).\n\nReçus\n-----\n"
        )
        summary = "# Summary\n\n# Welcome!\n\n- [Reading guide](guide.md)\n"
        swapped = localized.replace(
            "https://example.org/library", "https://example.org/temporary"
        ).replace(
            "https://example.org/catalog", "https://example.org/library"
        ).replace("https://example.org/temporary", "https://example.org/catalog")

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = root / "repo"
            repo.mkdir()

            def git(*args):
                return subprocess.check_output(["git", *args], cwd=repo, text=True).strip()

            git("init", "--bare", str(root / "remote.git"))
            git("init", "-b", "master")
            git("config", "user.name", "Translation Fixture")
            git("config", "user.email", "fixture@example.com")
            git("remote", "add", "origin", str(root / "remote.git"))
            for folder in ("src", "src/images", "theme"):
                (repo / folder).mkdir()
            for name in (".gitignore", "src/robots.txt", "src/images/.keep", "theme/.keep",
                         "hacktricks-preprocessor.py"):
                (repo / name).touch()
            (repo / "book.toml").write_text('[book]\ntitle = "Guide"\nlanguage = "fr"\n', encoding="utf-8")
            (repo / "src/guide.md").write_text(source, encoding="utf-8")
            (repo / "src/SUMMARY.md").write_text(summary, encoding="utf-8")
            git("add", "-A")
            git("commit", "-m", "English fixture")
            revision = git("rev-parse", "HEAD")
            git("branch", "fr")
            git("push", "origin", "fr")
            args = [
                cli, "--language", "French", "--branch", "fr", "--model", "gpt-4o", "--api-key", "fixture",
                "--source-ref", revision, "--initial-source-ref", revision, "--record-source",
                "--file-paths", "src/guide.md,src/SUMMARY.md",
            ]

            def run(result):
                def complete(**kwargs):
                    text = kwargs["messages"][-1]["content"]
                    output = result if text == source else "# 1. Bienvenue !\n# 2. Guide de lecture"
                    return SimpleNamespace(choices=[
                        SimpleNamespace(message=SimpleNamespace(content=output), finish_reason="stop")
                    ])

                client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=complete)))
                with patch("openai.OpenAI", return_value=client), patch.object(sys, "argv", args):
                    runpy.run_path(cli, run_name="__main__")

            previous = Path.cwd()
            try:
                os.chdir(repo)
                with self.assertRaisesRegex(RuntimeError, "moved Markdown links"):
                    run(swapped)
                self.assertEqual(git("rev-parse", "fr"), revision)
                self.assertFalse((repo / ".translation-source-blobs.json").exists())
                run(localized)
                self.assertEqual(git("rev-parse", "fr"), git("rev-parse", "origin/fr"))
                self.assertEqual(set(git("diff-tree", "-r", "--no-commit-id", "--name-only", "fr").splitlines()), {
                    "src/guide.md", "src/SUMMARY.md", ".translation-source-blobs.json",
                })
                subprocess.run(["mdbook", "build"], cwd=repo, check=True, capture_output=True)
                localized_summary = (repo / "src/SUMMARY.md").read_text(encoding="utf-8")
                toc = (repo / "book/toc.html").read_text(encoding="utf-8")
                check_rendered_sidebar(localized_summary, toc, "fr")
                chapter = (repo / "book/guide.html").read_text(encoding="utf-8")
                self.assertIn('<h2 id="reçus">', chapter)
                self.assertIn('class="translation-source-anchor" id="receipts"', chapter)
            finally:
                os.chdir(previous)

    def test_api_failure_does_not_publish_english_source(self):
        with self.assertRaisesRegex(RuntimeError, "could not be translated after retries"):
            translator.translate_text("French", "English content", "src/page.md", "gpt-4o", client=FailingClient())

    def test_truncated_model_response_is_retried(self):
        def response(text, reason):
            return SimpleNamespace(choices=[
                SimpleNamespace(message=SimpleNamespace(content=text), finish_reason=reason)
            ])

        with patch.object(FailingClient.chat.completions, "create", side_effect=[
            response("Esta", "length"),
            response("Esta é a mensagem.", "stop"),
        ]) as create:
            self.assertEqual(
                translator.translate_text("Brazilian Portuguese", "This is the message.", "src/page.md", "gpt-4o", client=FailingClient()),
                "Esta é a mensagem.",
            )
        self.assertEqual(create.call_count, 2)

    def test_summary_keeps_verified_product_name_with_english_connective(self):
        source = "# Summary\n\n- [Az - Defender for Cloud](guide.md)\n"
        with patch.object(translator, "translate_text") as translate:
            for language, code in (("Japanese", "ja"), ("Simplified Chinese", "zh")):
                localized = translator.translate_summary(language, source, None, "fixture", None, code)
                self.assertEqual(localized, source)
        translate.assert_not_called()
        with patch.object(translator, "translate_text", return_value="# 1. Az - Defender para Nuvem"):
            portuguese = translator.translate_summary("Brazilian Portuguese", source, None, "fixture", None, "pt")
        self.assertIn("Defender para Nuvem", portuguese)

    def test_summary_uses_verified_turkish_product_name(self):
        source = "# Summary\n\n- [Az - Defender for Cloud](guide.md)\n"
        with patch.object(translator, "translate_text") as translate:
            localized = translator.translate_summary("Turkish", source, None, "fixture", None, "tr")
        self.assertIn("[Az - Bulut için Microsoft Defender](guide.md)", localized)
        translate.assert_not_called()

    def test_french_summary_accepts_shared_french_vocabulary(self):
        source = "# Summary\n\n# Introduction\n"
        with patch.object(translator, "translate_text", return_value="# 1. Introduction") as translate:
            localized = translator.translate_summary("French", source, None, "fixture", None, "fr")
        self.assertEqual(localized, source)
        translate.assert_called_once()

    def test_summary_tries_quality_model_for_only_the_stubborn_label(self):
        source = "# Summary\n\n# Welcome!\n- [About the author](guide.md)\n"
        cheap = "# 1. Welcome!"
        with patch.object(translator, "translate_text", side_effect=[
            "# 1. Welcome!\n# 2. Sobre o autor", cheap, cheap, "# 1. Boas-vindas!",
        ]) as translate:
            localized = translator.translate_summary(
                "Brazilian Portuguese", source, None, "fast-model", None, "pt",
                fallback_model=lambda: "quality-model",
            )
        args = translate.call_args.args
        self.assertEqual((args[1], args[3]), ("# 1. Welcome!", "quality-model"))
        self.assertIn("- [Sobre o autor](guide.md)", localized)

    def test_summary_retries_only_missing_or_unchanged_labels(self):
        source = "# Summary\n\n# Welcome!\n- [About the author](guide.md)\n"
        with patch.object(translator, "translate_text", side_effect=[
            "# 2. Sobre o autor\n# 1. Welcome!",
            "# 1. Boas-vindas!",
        ]) as translate:
            localized = translator.translate_summary("Brazilian Portuguese", source, None, "fixture", None, "pt")
        self.assertEqual(translate.call_args.args[1], "# 1. Welcome!")
        self.assertIn("# Boas-vindas!", localized)
        self.assertIn("- [Sobre o autor](guide.md)", localized)

    def test_summary_translates_labels_and_keeps_structure_and_previous_labels(self):
        old_source = "# Summary\n\n# Welcome!\n- [About the author](old.md)\n"
        old_target = "# Summary\n\n# Bem-vindo!\n- [Sobre o autor](old.md)\n"
        source = (
            "# Summary\n\n# Welcome!\n- [About the author](changed.md)\n"
            "  - [How to get started](loc(al).md#start) <!-- editorial (note) -->\n\n[External Guide]()\n"
        )
        with patch.object(translator, "translate_text", return_value=(
            "# 1. Como começar\n# 2. Guia externo"
        )) as translate:
            translated = translator.translate_summary(
                "Brazilian Portuguese", source, (old_source, old_target), "gpt-4o", None
            )
        self.assertEqual(translate.call_args.args[1], "# 1. How to get started\n# 2. External Guide")
        self.assertEqual(translated, (
            "# Summary\n\n# Bem-vindo!\n- [Sobre o autor](changed.md)\n"
            "  - [Como começar](loc(al).md#start) <!-- editorial (note) -->\n\n[Guia externo]()\n"
        ))

    def test_summary_translates_only_remaining_labels_when_current_title_is_reusable(self):
        source = "# Summary\n\n# Welcome!\n- [Read the guide](guide.md)\n"
        with patch.object(translator, "translate_text", return_value="# 1. Bienvenue !") as translate:
            localized = translator.translate_summary(
                "French", source, None, "fixture", None, "fr", {"Read the guide": "Lire le guide"}
            )
        self.assertEqual(translate.call_args.args[1], "# 1. Welcome!")
        self.assertIn("- [Lire le guide](guide.md)", localized)

    def test_summary_translates_only_the_visible_external_link_label(self):
        source = "# Summary\n\n- [About the author$$external:https://example.org/author?from=toc$$]()\n"
        with patch.object(translator, "translate_text", return_value="# 1. Sobre o autor") as translate:
            localized = translator.translate_summary("Brazilian Portuguese", source, None, "fixture", None, "pt")
        self.assertEqual(translate.call_args.args[1], "# 1. About the author")
        self.assertEqual(localized, source.replace("About the author", "Sobre o autor"))

    def test_summary_repairs_wrong_language_checkpoint(self):
        source = "# Summary\n\n# Welcome!\n"
        previous = "# Summary\n\n# Willkommen!\n"
        with patch.object(translator, "wrong_language", side_effect=[True, False]), patch.object(
            translator, "translate_text", return_value="# 1. Bem-vindo!"
        ) as translate:
            self.assertEqual(
                translator.translate_summary("Brazilian Portuguese", source, (source, previous), "gpt-4o", None, "pt"),
                "# Summary\n\n# Bem-vindo!\n",
            )
        translate.assert_called_once()

    def test_markdown_chunking_keeps_reference_block_and_arguments_intact(self):
        ref = "{{#ref}}\n`../guide.md`\n{{#endref}}\n"
        source = "Introduction to our guide.\n" + ref + "Read the documentation.\n"
        with patch.object(translator, "MAX_TOKENS", 24), patch.object(
            translator, "reportTokens", side_effect=lambda text, _model: len(text)
        ):
            chunks = translator.split_text(source, "gpt-4o")
        self.assertEqual(sum(ref in chunk for chunk in chunks), 1)
        self.assertEqual("".join(chunks), source)

    def test_chunking_never_splits_a_markdown_table_or_nested_list(self):
        intro = "# Guide\n\nIntroductory paragraph.\n"
        table = "\n| Name | Value |\n| --- | --- |\n| First | One |\n| Second | Two |\n"
        items = "\n- Pack the parcel.\n  - Include the receipt.\n  - Add a label.\n"
        end = "\nRead the shipping guide.\n"
        source = intro + table + items + end
        with patch.object(translator, "MAX_TOKENS", 22), patch.object(
            translator, "reportTokens", side_effect=lambda text, _model: len(text)
        ):
            chunks = translator.split_text(source, "gpt-4o")
        self.assertEqual("".join(chunks), source)
        self.assertTrue(any(table.lstrip("\n") in chunk for chunk in chunks))
        self.assertTrue(any(items.lstrip("\n") in chunk for chunk in chunks))

    def test_context_error_splits_complete_blocks_and_preserves_spacing(self):
        source = "First paragraph with one line.\n\nSecond paragraph with one line.\n"
        left = "Premier paragraphe sur une ligne."
        right = "Deuxième paragraphe sur une ligne."
        def choice(value):
            return SimpleNamespace(choices=[
                SimpleNamespace(message=SimpleNamespace(content=value), finish_reason="stop")
            ])
        create = Mock(side_effect=[RuntimeError("maximum context length"), choice(left), choice(right)])
        client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
        result = translator.translate_text("French", source, "src/guide.md", "test-model", client=client)
        self.assertEqual(result, left + "\n\n" + right + "\n")
        self.assertEqual(create.call_count, 3)

    def test_oversized_indivisible_table_is_not_retried_as_broken_rows(self):
        source = "| Name | Value |\n| --- | --- |\n| First | One |\n| Second | Two |\n"
        create = Mock(side_effect=RuntimeError("maximum context length"))
        client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
        with self.assertRaisesRegex(RuntimeError, "no safe Markdown boundary"):
            translator.translate_text("French", source, "src/guide.md", "test-model", client=client)
        create.assert_called_once()

    def test_truncated_output_retries_as_smaller_markdown_blocks(self):
        source = "First paragraph.\n\nSecond paragraph.\n"
        def choice(value, reason):
            return SimpleNamespace(choices=[
                SimpleNamespace(message=SimpleNamespace(content=value), finish_reason=reason)
            ])
        create = Mock(side_effect=[
            choice("Premier", "length"),
            choice("Premier paragraphe.", "stop"),
            choice("Deuxième paragraphe.", "stop"),
        ])
        client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
        result = translator.translate_text("French", source, "src/guide.md", "test-model", client=client)
        self.assertEqual(result, "Premier paragraphe.\n\nDeuxième paragraphe.\n")
        self.assertEqual(create.call_count, 3)

    def test_summary_refuses_copied_labels_even_if_punctuation_changes(self):
        with patch.object(translator, "translate_text", return_value="# 1. WELCOME.") as translate:
            with self.assertRaisesRegex(RuntimeError, "untranslated navigation labels"):
                translator.translate_summary("French", "# Summary\n\n# Welcome!\n", None, "gpt-4o", None)
        self.assertEqual(translate.call_count, 3)

    def test_same_language_does_not_require_rewriting_code_or_proper_names(self):
        english = "This is the original message. The report shows how to update your account. " * 10
        french = "Ce document explique comment consulter votre compte et mettre à jour vos coordonnées. " * 10
        code = "\n\n```text\n" + english + "\n```"
        self.assertFalse(translator.copied_prose(french + code, french + code))
        self.assertFalse(translator.wrong_language(french + code, "fr"))
        self.assertTrue(translator.wrong_language(french, "pt"))

    def test_mixed_prose_detects_english_sentence_inside_a_translated_paragraph(self):
        copied = "This guide contains the information that you need before you can finish the setup."
        source = f"Welcome to our guide. {copied}"
        localized = f"Bienvenue dans notre guide. {copied}"
        self.assertFalse(translator.copied_prose(source, localized))
        self.assertTrue(copied_sentence(source, localized))
        self.assertFalse(copied_sentence(source, "Bienvenue.\n\n```text\n" + copied + "\n```"))

    def test_language_checks_ignore_indented_code_and_quotation_continuations(self):
        english = (
            "The library has a reading room where you can sit while you review the book. "
            "When you have finished, you should return the book to the shelf and ask the staff "
            "for help if you are uncertain about where it belongs."
        )
        code = f"    {english}\n"
        self.assertFalse(translator.copied_prose(f"Library\n\n{code}", f"Bibliothèque\n\n{code}"))
        self.assertFalse(copied_sentence(english, f"Bibliothèque\n\n{code}"))
        self.assertEqual(suspected_english_blocks(f"Bibliothèque\n\n{english}"), 1)
        for quote in (f"> Original quotation\n{english}", f"<blockquote>{english}</blockquote>"):
            with self.subTest(quote=quote):
                self.assertFalse(copied_sentence(english, quote))
                self.assertEqual(suspected_english_blocks(f"Bibliothèque\n\n{quote}"), 0)

    def test_markdown_checks_accept_localized_text_and_flag_structural_regressions(self):
        source = (
            "## Your receipt {#receipt .section}\n\n"
            "View the [instructions](guide(v2).md#steps) using `--help`.\n\n"
            "Open [the receipt][receipt].\n\n[receipt]: receipt.pdf\n"
        )
        localized = (
            "## Votre reçu {#receipt .section}\n\n"
            "Consultez le [guide](guide(v2).md#steps) avec `--help`.\n\n"
            "Ouvrez [le reçu][receipt].\n\n[receipt]: receipt.pdf\n"
        )
        self.assertEqual(markdown_problems(source, localized), [])
        for old, new, expected in [
            ("#receipt .section", "#recu .section", "changed link, image, or HTML anchor targets"),
            ("guide(v2).md#steps", "guide(v3).md#steps", "changed link, image, or HTML anchor targets"),
            ("receipt.pdf", "recu.pdf", "changed link, image, or HTML anchor targets"),
            ("`--help`", "`--aide`", "changed inline or indented code"),
            ("Ouvrez [le reçu][receipt].\n\n", "", "missing Markdown sections, paragraphs, list entries, or table cells"),
        ]:
            with self.subTest(old=old):
                self.assertIn(expected, markdown_problems(source, localized.replace(old, new)))

    def test_markdown_checks_detect_swapped_inline_elements_with_equal_counts(self):
        source = (
            "# Forms\n\n"
            "Fetch the [application](apply.pdf) with `fetch`.\n\n"
            "Send the [receipt](receipt.pdf) with `send`.\n"
        )
        translated = (
            "# Formulaires\n\n"
            "Téléchargez la [demande](apply.pdf) avec `fetch`.\n\n"
            "Envoyez le [reçu](receipt.pdf) avec `send`.\n"
        )
        self.assertEqual(markdown_problems(source, translated), [])
        links_swapped = translated.replace("apply.pdf", "TEMP").replace("receipt.pdf", "apply.pdf").replace("TEMP", "receipt.pdf")
        code_swapped = translated.replace("`fetch`", "TEMP").replace("`send`", "`fetch`").replace("TEMP", "`send`")
        for variant in (links_swapped, code_swapped):
            self.assertEqual(markdown_problems(source, variant), ["moved Markdown links, images, or inline code"])

    def test_markdown_checks_preserve_translated_alternative_text_tooltips_and_labels(self):
        source = (
            '![Map of the building](map.png "View the map") and [directions](guide.md "Open the guide").\n\n'
            '![A waiting room][room]\n\n[room]: room.png "Room preview"\n\n'
            '<img src="door.png" alt="Front entrance">\n\n'
            '<a href="rooms.html" aria-label="List of rooms">Rooms</a>\n\n![](decoration.png)\n'
        )
        localized = (
            '![Plan du bâtiment](map.png "Voir le plan") et [itinéraire](guide.md "Ouvrir le guide").\n\n'
            '![Une salle d’attente][room]\n\n[room]: room.png "Aperçu de la salle"\n\n'
            '<img src="door.png" alt="Entrée principale">\n\n'
            '<a href="rooms.html" aria-label="Liste des salles">Salles</a>\n\n![](decoration.png)\n'
        )
        self.assertEqual(markdown_problems(source, localized), [])
        for removed in (
            'Plan du bâtiment', 'Voir le plan', ' "Ouvrir le guide"', 'Une salle d’attente',
            ' "Aperçu de la salle"', 'Entrée principale', ' aria-label="Liste des salles"',
        ):
            with self.subTest(removed=removed):
                self.assertEqual(
                    markdown_problems(source, localized.replace(removed, "")),
                    ["missing image alternative text, tooltip, or accessible label"],
                )

    def test_markdown_checks_detect_reordered_heading_levels_with_equal_counts(self):
        original = "# Handbook\n\n## Reading\n\n### Examples\n\n## Writing\n"
        localized = "# Manuel\n\n## Lecture\n\n## Rédaction\n\n### Exemples\n"
        self.assertEqual(markdown_problems(original, localized), ["changed Markdown heading order or nesting"])

    def test_markdown_checks_preserve_inline_formatting_without_restricting_word_order(self):
        source = "This is **important** and *current*.  \nAsk for ~~paper~~ digital copies.\n\nThank you.\n"
        localized = "Statut _actuel_ et __important__.\\\nDemandez une copie numérique ~~papier~~.\n\nMerci.\n"
        self.assertEqual(markdown_problems(source, localized), [])
        for old, new in (
            ("_actuel_", "actuel"),
            ("__important__", "_important_"),
            ("~~papier~~", "papier"),
            ("\\\n", "\n"),
            ("~~papier~~.\n\nMerci", "papier.\n\n~~Merci~~"),
        ):
            with self.subTest(old=old, new=new):
                self.assertEqual(
                    markdown_problems(source, localized.replace(old, new)),
                    ["changed Markdown emphasis, strikethrough, or hard line breaks"],
                )

    def test_markdown_checks_find_visible_bold_delimiters_with_equal_formatting_counts(self):
        source = "Follow [the library](https://example.org) **for updates**. Use \\*\\* in examples.\n"
        localized = (
            "Suivez [la bibliothèque](https://example.org) pour les **nouveautés**. "
            "Utilisez \\*\\* dans les exemples.\n"
        )
        broken = localized.replace("pour les **nouveautés**", "** pour les nouvelles** et les **nouveautés**")
        self.assertEqual(markdown_problems(source, localized), [])
        self.assertEqual(markdown_problems(source, broken), ["introduced visible Markdown bold markers"])
        self.assertEqual(markdown_problems(source, localized.replace("dans les exemples", "avec `**` dans les exemples")), [
            "changed inline or indented code",
        ])

    def test_cjk_bold_repair_preserves_punctuation_and_protected_text(self):
        text = "请先**打开指南。**然后开始。\n\n用途是**「読書」**です。\n"
        sample = "请先**打开指南。**然后开始。"
        code = f"\n示例：`{sample}`\n\n```text\n{sample}\n```\n"
        escaped = "\n请先\\*\\*打开指南。\\*\\*然后开始。\n"
        original = text + code + escaped
        expected = "请先**打开指南**。然后开始。\n\n用途是「**読書**」です。\n" + code + escaped
        self.assertEqual(repair_cjk_bold_boundaries(original), expected)
        self.assertEqual(repair_cjk_bold_boundaries(expected), expected)
        ambiguous = f"\\*\\*打开指南。\\*\\* 或 `**打开指南。**`\n"
        self.assertEqual(repair_cjk_bold_boundaries(ambiguous), ambiguous)

    def test_cjk_bold_repair_moves_outer_spaces_without_changing_text(self):
        examples = (
            ("공지의** 안내서 **를 읽으세요.", "공지의 **안내서** 를 읽으세요."),
            ("준비는**(안내서)**부터 시작합니다.", "준비는(**안내서**)부터 시작합니다."),
            ("請** 読書。 **後に確認。", "請 **読書**。 後に確認。"),
        )
        for original, expected in examples:
            with self.subTest(original=original):
                self.assertEqual(repair_cjk_bold_boundaries(original), expected)
                self.assertEqual(expected.replace("**", ""), original.replace("**", ""))
                self.assertEqual(repair_cjk_bold_boundaries(expected), expected)

    def test_page_repairs_cjk_bold_only_after_full_structure_validation(self):
        english = "First, **open the guide**. Then begin.\n"
        chinese = "请先**打开指南。**然后开始。\n"
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.md"
            output = Path(directory) / "output.md"
            source.write_text(english, encoding="utf-8")
            with patch.object(translator, "reportTokens", return_value=1), patch.object(
                translator, "translate_text", return_value=chinese,
            ):
                translator.translate_file("Chinese", source, output, "gpt-4o", None, "zh")
            self.assertEqual(output.read_text(encoding="utf-8"), "请先**打开指南**。然后开始。\n")

    def test_markdown_checks_preserve_callout_type_and_position(self):
        source = (
            "> [!NOTE]\n> The reading room is inside.\n\n"
            "> [!WARNING]\n> The stairs are steep.\n\n"
            "- Accessibility\n\n  > [!TIP]\n  > Ask about the lift.\n"
        )
        localized = (
            "> [!note]\n> La salle de lecture est à l’intérieur.\n\n"
            "> [!WARNING]\n> L’escalier est raide.\n\n"
            "- Accessibilité\n\n  > [!TIP]\n  > Renseignez-vous sur l’ascenseur.\n"
        )
        self.assertEqual(markdown_problems(source, localized), [])
        for marker in ("[!NOTE]", "[!REMARQUE]", "[!WARNING] Autre titre", ""):
            with self.subTest(marker=marker):
                broken = localized.replace("[!WARNING]", marker)
                self.assertIn("changed Markdown callout types or positions", markdown_problems(source, broken))
        swapped = localized.replace("[!WARNING]", "[!NOTE]").replace("[!note]", "[!WARNING]")
        self.assertIn("changed Markdown callout types or positions", markdown_problems(source, swapped))

    def test_markdown_checks_preserve_list_quote_table_and_rule_structure(self):
        original = (
            "> Read this first.\n\n---\n\n"
            "3. Get the forms\n   - [x] Application\n   - [ ] Receipt\n\n"
            "| Form | Price |\n| :--- | ---: |\n| Receipt | 0 |\n"
        )
        localized = (
            "> À lire en premier.\n\n***\n\n"
            "3. Récupérez les formulaires\n   * [X] Demande\n   * [ ] Reçu\n\n"
            "| Formulaire | Prix |\n| :--- | ---: |\n| Reçu | 0 |\n"
        )
        self.assertEqual(markdown_problems(original, localized), [])
        for old, new in (
            ("> À lire", "À lire"),
            ("\n***\n", ""),
            ("3. Récupérez", "1. Récupérez"),
            ("3. Récupérez", "- Récupérez"),
            ("   * [ ]", "* [ ]"),
            ("[X] Demande", "[ ] Demande"),
            ("| :--- | ---: |", "| ---: | :--- |"),
        ):
            with self.subTest(old=old, new=new):
                self.assertIn(
                    "changed Markdown lists, block quotes, tables, or thematic breaks",
                    markdown_problems(original, localized.replace(old, new)),
                )

    def test_translation_preserves_distinct_source_and_localized_heading_ids(self):
        source = (
            "# Reader guide\n\n## Find your receipt\n\n## Find your receipt\n\n"
            "## About {#explicit}\n\n```markdown\n## Ignored heading\n```\n"
        )
        localized = (
            "# Guide du lecteur\n\n## Trouver un reçu\n\n## Trouver un reçu\n\n"
            "## À propos {#explicit}\n\n```markdown\n## Ignored heading\n```\n"
        )
        preserved = preserve_source_heading_anchors(source, localized)
        for anchor in ["reader-guide", "find-your-receipt", "find-your-receipt-1"]:
            self.assertIn(f'id="{anchor}"', preserved)
        self.assertNotIn('id="explicit"', preserved)
        self.assertNotIn('id="ignored-heading"', preserved)
        self.assertEqual(preserve_source_heading_anchors(source, preserved), preserved)
        self.assertEqual(markdown_problems(source, preserved, allow_source_aliases=True), [])

    def test_translation_does_not_add_an_anchor_with_an_existing_id(self):
        source = "# Introduction\n\n## Details\n"
        localized = "# Bienvenue\n\n## Introduction\n"
        preserved = preserve_source_heading_anchors(source, localized)
        self.assertNotIn('id="introduction"', preserved)
        self.assertIn('id="details"', preserved)

    def test_translation_preserves_setext_bookmarks_and_line_endings(self):
        source = "Reader guide\n============\n\nWhere to find receipts\n----------------------\n"
        localized = "Guide du lecteur\r\n================\r\n\r\nOù trouver les reçus\r\n--------------------\r\n"
        preserved = preserve_source_heading_anchors(source, localized)
        self.assertIn('id="reader-guide"></span>Guide du lecteur\r\n', preserved)
        self.assertIn('id="where-to-find-receipts"></span>Où trouver les reçus\r\n', preserved)
        self.assertEqual(preserved.count("\r\n"), localized.count("\r\n"))
        self.assertEqual(preserve_source_heading_anchors(source, preserved), preserved)
        self.assertEqual(markdown_problems(source, preserved, allow_source_aliases=True), [])

    def test_translation_restores_heading_that_contains_a_legacy_bookmark(self):
        source = '# <a href="#legacy-id" id="legacy-id"></a>Reader guide\n'
        localized = '# <a href="#legacy-id" id="legacy-id"></a>Guide du lecteur\n'
        restored = preserve_source_heading_anchors(source, localized)
        self.assertIn('id="reader-guide"', restored)
        self.assertEqual(restored.count('id="legacy-id"'), 1)

    def test_translation_leaves_ambiguous_heading_structure_alone(self):
        source = "# Overview\n\n## Summary\n"
        localized = "# Présentation\n\n### Synthèse\n"
        self.assertEqual(preserve_source_heading_anchors(source, localized), localized)

    def test_html_check_rejects_the_stray_closing_tag_that_broke_mdbook(self):
        source = "Read <strong>the guide</strong>.\n"
        translated = "Lisez <strong>le guide</strong>.\n"
        self.assertEqual(markdown_problems(source, translated), [])
        self.assertIn("introduced unmatched HTML tags",
                      markdown_problems(source, translated + "</strong>\n"))
        self.assertIn("introduced unmatched HTML tags",
                      markdown_problems(source, translated.replace("</strong>", "")))

    def test_html_check_tolerates_a_legacy_imbalance_and_ignores_code(self):
        source = "<strong>Reminder\n\n```html\n</strong>\n```\n"
        translated = source.replace("Reminder", "Rappel")
        self.assertEqual(markdown_problems(source, translated), [])
        self.assertEqual(markdown_problems(source, translated.replace("<strong>", "")), [])

    def test_html_check_rejects_crossed_tags_even_when_all_tags_are_closed(self):
        source = (
            "<details>\n<summary><strong><em>Guide</em></strong></summary>\n\n"
            "Read <em><strong>this guide</strong></em>.\n\n</details>\n"
        )
        translated = source.replace("Read", "Lisez").replace("this guide", "ce guide")
        self.assertEqual(markdown_problems(source, translated), [])
        for first, second in (("em", "strong"), ("strong", "em")):
            with self.subTest(first=first, second=second):
                broken = translated.replace(f"</{first}></{second}>", f"</{second}></{first}>")
                self.assertEqual(
                    markdown_problems(source, broken), ["introduced incorrectly nested HTML tags"],
                )
                self.assertEqual(markdown_problems(broken, broken.replace("Lisez", "Consultez")), [])

    def test_structurally_incomplete_page_never_writes_a_translation(self):
        source = "# Receipts\n\nFirst paragraph.\n\nSecond paragraph.\n"
        incomplete = "# Reçus\n\nPremier paragraphe.\n"
        with tempfile.TemporaryDirectory() as directory:
            origin = directory + "/source.md"
            target = directory + "/target.md"
            with open(origin, "w") as stream:
                stream.write(source)
            with patch.object(translator, "reportTokens", return_value=1), patch.object(
                translator, "translate_text", return_value=incomplete
            ):
                with self.assertRaisesRegex(RuntimeError, "missing Markdown"):
                    translator.translate_file("French", origin, target, "gpt-4o", None, "fr")
            self.assertFalse(translator.os.path.exists(target))

    def test_page_restores_the_blank_line_before_the_training_footer(self):
        english = (
            "The library opens early on weekdays.\n\n## References\n\n"
            "- [1] [Schedule](https://example.org/hours)\n\n{{#include ./banners/hacktricks-training.md}}\n"
        )
        french = english.replace("The library opens early on weekdays.", "La bibliothèque ouvre tôt en semaine.")
        french = french.replace("[Schedule]", "[Horaires]")
        without_separator = french.replace("\n\n{{#include", "\n{{#include")
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.md"
            target = Path(directory) / "output.md"
            source.write_text(english, encoding="utf-8")
            with patch.object(translator, "reportTokens", return_value=1), patch.object(
                translator, "translate_text", return_value=without_separator
            ):
                translator.translate_file("French", source, target, "gpt-4o", None, "fr")
            self.assertEqual(target.read_text(encoding="utf-8"), french)

    def test_page_retries_copied_prose_before_writing_output(self):
        english = "This is the original text and it should be translated before publication.\n"
        french = "Ce texte doit être traduit avant sa publication.\n"
        with tempfile.TemporaryDirectory() as directory:
            source = directory + "/source.md"
            target = directory + "/output.md"
            with open(source, "w") as stream:
                stream.write(english)
            with patch.object(translator, "reportTokens", return_value=1), patch.object(
                translator, "translate_text", side_effect=[english, french]
            ) as translate:
                translator.translate_file("French", source, target, "gpt-4o", None, "fr")
            with open(target) as stream:
                self.assertEqual(stream.read(), french)
        self.assertEqual(translate.call_count, 2)

    def test_failed_page_fails_the_entire_batch(self):
        calls = []

        def translate(_language, path, _destination, _model, _client):
            calls.append(path)
            if path == "src/broken.md":
                raise RuntimeError("API failed")

        with tempfile.TemporaryDirectory() as destination:
            with patch.object(translator, "_get_encoding_for_model"), patch.object(translator, "translate_file", side_effect=translate):
                with self.assertRaisesRegex(RuntimeError, "1 pages failed translation.*src/broken.md: API failed") as failure:
                    translator.translate_selected_files(
                        "French", ["src/okay.md", "src/broken.md"], destination, "gpt-4o", None, 2
                    )
                self.assertEqual(str(failure.exception.__cause__), "API failed")
        self.assertCountEqual(calls, ["src/okay.md", "src/broken.md"])

    def test_broken_directives_retry_with_exact_source_markup(self):
        source = "Read this.\n{{#ref}}\n../README.md\n{{#endref}}\nMore details."

        class Client:
            class chat:
                class completions:
                    @staticmethod
                    def create(**kwargs):
                        content = kwargs["messages"][-1]["content"]
                        if "__HTC_STRUCT_" in content:
                            result = content.replace("Read this.", "Lee esto.").replace("More details.", "Más detalles.")
                        else:
                            result = "Lee esto. Más detalles."  # Model dropped the ref block.
                        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=result))])

        translated = translator.translate_text("Spanish", source, "src/page.md", "gpt-4o", client=Client())
        self.assertIn("Lee esto.", translated)
        self.assertIn("Más detalles.", translated)
        self.assertIn("{{#ref}}\n../README.md\n{{#endref}}", translated)

    def test_ref_path_is_restored_without_losing_translated_prose(self):
        source = "Read this.\n{{#ref}}\n../gcp-cloudfunctions-privesc.md\n{{#endref}}\nMore details."

        class Client:
            class chat:
                class completions:
                    @staticmethod
                    def create(**_kwargs):
                        result = "Lee esto.\n{{#ref}}\n../gcp-cloud-functions-privesc.md\n{{#endref}}\nMás detalles."
                        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=result))])

        translated = translator.translate_text("Spanish", source, "src/page.md", "gpt-4o", client=Client())
        self.assertEqual(
            translated,
            "Lee esto.\n{{#ref}}\n../gcp-cloudfunctions-privesc.md\n{{#endref}}\nMás detalles.",
        )

    def test_broken_references_retry_with_exact_source_citations(self):
        source = "Read this.<sup>[[1]](#references)</sup>\n\n## References\n\n- [1] [AWS API](https://example.com/api)"

        class Client:
            class chat:
                class completions:
                    @staticmethod
                    def create(**kwargs):
                        content = kwargs["messages"][-1]["content"]
                        if "__HTC_STRUCT_" in content:
                            result = content.replace("Read this.", "Lee esto.")
                        else:
                            result = "Lee esto.\n\n## Referencias"  # Model dropped citations.
                        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=result))])

        translated = translator.translate_text("Spanish", source, "src/page.md", "gpt-4o", client=Client())
        self.assertIn("Lee esto.<sup>[[1]](#references)</sup>", translated)
        self.assertIn("## References", translated)
        self.assertIn("- [1] [AWS API](https://example.com/api)", translated)

    def test_placeholder_loss_translates_prose_around_protected_spans(self):
        source = "Read this.\n{{#include ./banner.md}}\nMore details."

        class Client:
            class chat:
                class completions:
                    @staticmethod
                    def create(**kwargs):
                        content = kwargs["messages"][-1]["content"]
                        if "__HTC_STRUCT_" in content:
                            result = "El modelo omitió el marcador"
                        elif "{{#include" in content:
                            result = "El modelo omitió la directiva"
                        else:
                            result = content.replace("Read this.", "Lee esto.").replace("More details.", "Más detalles.")
                        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=result))])

        translated = translator.translate_text("Spanish", source, "src/page.md", "gpt-4o", client=Client())
        self.assertIn("Lee esto.\n{{#include ./banner.md}}\nMás detalles.", translated)

    def test_extra_citation_outside_preserved_markers_retries_prose(self):
        source = "Read this.<sup>[[1]](#references)</sup>\n\n## References\n\n- [1] [API](https://example.com)"

        class Client:
            class chat:
                class completions:
                    @staticmethod
                    def create(**kwargs):
                        content = kwargs["messages"][-1]["content"]
                        if "__HTC_STRUCT_" in content:
                            result = content.replace("Read this.", "Lee esto.")
                            result += "\n<sup>[[99]](#references)</sup>"
                        elif "<sup>" in content:
                            result = "Lee esto.\n\n## Referencias"
                        else:
                            result = content.replace("Read this.", "Lee esto.")
                        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=result))])

        translated = translator.translate_text("Spanish", source, "src/page.md", "gpt-4o", client=Client())
        self.assertTrue(translator.protected_markup_is_intact(source, translated))
        self.assertIn("Lee esto.<sup>[[1]](#references)</sup>", translated)
        self.assertNotIn("[[99]]", translated)

    def test_model_added_citation_to_source_without_references_is_retried(self):
        calls = []

        class Client:
            class chat:
                class completions:
                    @staticmethod
                    def create(**_kwargs):
                        calls.append(1)
                        result = "Lee esto."
                        if len(calls) == 1:
                            result += "<sup>[[9]](#references)</sup>"
                        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=result))])

        translated = translator.translate_text("Spanish", "Read this.", "src/page.md", "gpt-4o", client=Client())
        self.assertEqual(translated, "Lee esto.")
        self.assertEqual(len(calls), 2)

    def test_bare_source_citation_is_restored_after_model_wraps_it(self):
        source = "Read this.[[1]](#references)\n\n## References\n\n- [1] [API](https://example.com)"

        class Client:
            class chat:
                class completions:
                    @staticmethod
                    def create(**_kwargs):
                        result = source.replace("Read this.", "Lee esto.").replace(
                            "[[1]](#references)", "<sup>[[1]](#references)</sup>"
                        )
                        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=result))])

        translated = translator.translate_text("Spanish", source, "src/page.md", "gpt-4o", client=Client())
        self.assertIn("Lee esto.[[1]](#references)", translated)
        self.assertTrue(translator.protected_markup_is_intact(source, translated))
        self.assertNotIn("<sup>", translated)

    def test_persistently_added_citation_fails_closed(self):
        class Client:
            class chat:
                class completions:
                    @staticmethod
                    def create(**_kwargs):
                        result = "Lee esto.<sup>[[9]](#references)</sup>"
                        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=result))])

        with self.assertRaisesRegex(RuntimeError, "changed protected markup after retries"):
            translator.translate_text("Spanish", "Read this.", "src/page.md", "gpt-4o", client=Client())

    def test_page_level_validation_rejects_structural_drift_before_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = f"{tmp}/source.md"
            target = f"{tmp}/target.md"
            with open(source, "w") as f:
                f.write("# Title\n\nPlain text.\n")
            with patch.object(translator, "split_text", return_value=["# Title", "Plain text."]):
                with patch.object(translator, "translate_text", side_effect=["# Title", "Texte.<sup>[[1]](#references)</sup>"]):
                    with self.assertRaisesRegex(RuntimeError, "changed protected markup"):
                        translator.translate_file("French", source, target, "gpt-4o", None)
            self.assertFalse(__import__("os").path.exists(target))


if __name__ == "__main__":
    unittest.main()
