import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import translator


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

    def test_failed_page_fails_the_entire_batch(self):
        calls = []

        def translate(_language, path, _destination, _model, _client):
            calls.append(path)
            if path == "src/broken.md":
                raise RuntimeError("API failed")

        with tempfile.TemporaryDirectory() as destination:
            with patch.object(translator, "translate_file", side_effect=translate):
                with self.assertRaisesRegex(RuntimeError, "1 pages failed translation"):
                    translator.translate_selected_files(
                        "French", ["src/okay.md", "src/broken.md"], destination, "gpt-4o", None, 2
                    )
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


if __name__ == "__main__":
    unittest.main()
