import io
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch, sentinel

from requests.exceptions import ConnectionError

import translator


class TokenizerTests(unittest.TestCase):
    def setUp(self):
        translator._get_encoding_for_model.cache_clear()
        self.addCleanup(translator._get_encoding_for_model.cache_clear)

    def test_native_model_mapping_takes_priority(self):
        with patch.object(translator.tiktoken, "encoding_name_for_model", return_value="native_encoding"):
            with patch.object(translator.tiktoken, "get_encoding", return_value=sentinel.encoding) as load:
                self.assertIs(translator._get_encoding_for_model("gpt-6-luna"), sentinel.encoding)
        load.assert_called_once_with("native_encoding")

    def test_known_model_families_do_not_warn(self):
        families = {
            "gpt-6-luna": "o200k_base",
            "gpt-6-astra": "o200k_base",
            "GPT-6-LUNA": "o200k_base",
            "gpt-5.6-luna": "o200k_base",
            "gpt-4o-custom": "o200k_base",
            "gpt-4.1-custom": "o200k_base",
            "gpt-4-custom": "cl100k_base",
            "gpt-3.5-custom": "cl100k_base",
        }
        output = io.StringIO()
        with redirect_stdout(output):
            with patch.object(translator.tiktoken, "encoding_name_for_model", side_effect=KeyError):
                with patch.object(translator.tiktoken, "get_encoding", return_value=sentinel.encoding) as load:
                    for model, encoding in families.items():
                        with self.subTest(model=model):
                            self.assertIs(translator._get_encoding_for_model(model), sentinel.encoding)
                            load.assert_called_with(encoding)
        self.assertEqual(output.getvalue(), "")

    def test_unknown_model_warns_only_once_after_successful_load(self):
        output = io.StringIO()
        with redirect_stdout(output):
            with patch.object(translator.tiktoken, "encoding_name_for_model", side_effect=KeyError):
                with patch.object(translator.tiktoken, "get_encoding", return_value=sentinel.encoding) as load:
                    for _ in range(10):
                        translator._get_encoding_for_model("unknown-model")
        self.assertEqual(output.getvalue().count("Tokenizer for model unknown-model not found"), 1)
        load.assert_called_once_with("o200k_base")

    def test_vocabulary_download_retries_transient_network_failures(self):
        with patch.object(translator.tiktoken, "encoding_name_for_model", return_value="o200k_base"):
            with patch.object(translator.tiktoken, "get_encoding", side_effect=[
                ConnectionError("temporary DNS failure"), OSError("temporary network failure"), sentinel.encoding,
            ]) as load:
                with patch.object(translator.time, "sleep") as sleep:
                    self.assertIs(translator._get_encoding_for_model("gpt-6-luna"), sentinel.encoding)
                    self.assertIs(translator._get_encoding_for_model("gpt-6-luna"), sentinel.encoding)
        self.assertEqual(load.call_count, 3)
        self.assertEqual([call.args[0] for call in sleep.call_args_list], [1, 2])

    def test_failed_initialization_starts_no_page_workers(self):
        error = ConnectionError("vocabulary host cannot be resolved")
        with patch.object(translator.tiktoken, "encoding_name_for_model", return_value="o200k_base"):
            with patch.object(translator.tiktoken, "get_encoding", side_effect=error) as load:
                with patch.object(translator.time, "sleep"):
                    with patch.object(translator.concurrent.futures, "ThreadPoolExecutor") as pool:
                        with self.assertRaisesRegex(RuntimeError, "no pages were translated.*cannot be resolved") as failure:
                            translator.translate_selected_files(
                                "Japanese", ["src/page.md"], "/unused", "gpt-6-luna", None, 3,
                            )
                        pool.assert_not_called()
        self.assertEqual(load.call_count, 3)
        self.assertIs(failure.exception.__cause__, error)

    def test_initialization_failure_is_not_cached(self):
        with patch.object(translator.tiktoken, "encoding_name_for_model", return_value="o200k_base"):
            with patch.object(translator.tiktoken, "get_encoding", side_effect=[
                ConnectionError("DNS"), ConnectionError("DNS"), ConnectionError("DNS"), sentinel.encoding,
            ]):
                with patch.object(translator.time, "sleep"):
                    with self.assertRaises(RuntimeError):
                        translator._get_encoding_for_model("gpt-6-luna")
                    self.assertIs(translator._get_encoding_for_model("gpt-6-luna"), sentinel.encoding)

    def test_successful_initialization_precedes_all_pages(self):
        events = []
        with tempfile.TemporaryDirectory() as destination:
            with patch.object(translator, "_get_encoding_for_model", side_effect=lambda _model: events.append("tokenizer")):
                with patch.object(translator, "translate_file", side_effect=lambda *args: events.append(args[1])):
                    translator.translate_selected_files(
                        "Japanese", ["src/one.md", "src/two.md"], destination, "gpt-6-luna", None, 2,
                    )
        self.assertEqual(events[0], "tokenizer")
        self.assertCountEqual(events[1:], ["src/one.md", "src/two.md"])

    def test_empty_batch_does_not_load_a_tokenizer(self):
        with patch.object(translator, "_get_encoding_for_model") as load:
            translator.translate_selected_files("Japanese", [], "/unused", "gpt-6-luna", None, 2)
        load.assert_not_called()


if __name__ == "__main__":
    unittest.main()
