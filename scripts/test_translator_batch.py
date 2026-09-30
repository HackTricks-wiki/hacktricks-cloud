import tempfile
import unittest
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


if __name__ == "__main__":
    unittest.main()
