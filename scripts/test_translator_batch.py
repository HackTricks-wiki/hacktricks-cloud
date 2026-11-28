import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import translator
from translation_quality import copied_sentence, markdown_problems, preserve_source_heading_anchors


class FailingClient:
    class chat:
        class completions:
            @staticmethod
            def create(**_kwargs):
                raise RuntimeError("temporary translation error")


class TranslationBatchTests(unittest.TestCase):
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
        self.assertIn(ref, chunks)
        self.assertEqual("".join(chunks), source)

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
