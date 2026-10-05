import os
import tempfile
import unittest
from unittest.mock import patch

import translator


class CodeBlockPreservationTests(unittest.TestCase):
    def translate(self, source, translate_prose=None):
        with tempfile.TemporaryDirectory() as directory:
            origin = os.path.join(directory, 'source.md')
            target = os.path.join(directory, 'translated.md')
            with open(origin, 'w') as stream:
                stream.write(source)
            with patch.object(translator, 'reportTokens', side_effect=lambda text, _model: len(text)):
                with patch.object(translator, 'translate_text', side_effect=translate_prose or
                                  (lambda _language, text, *_args, **_kwargs: text.replace('English prose', 'French prose'))):
                    translator.translate_file('French', origin, target, 'test-model', None)
            with open(target) as stream:
                return stream.read()

    def test_preserves_python_indentation_and_blank_lines(self):
        code = '```python\ndef example():\n    if True:\n        return 1\n\n    return 0\n```'
        result = self.translate('# English prose\n\n'+code+'\n\nEnglish prose\n')
        self.assertIn('# French prose', result)
        self.assertEqual(translator.fenced_code_blocks(result), [code])

    def test_inner_indented_backticks_stay_inside_the_original_block(self):
        code = '```python\nexample = """\n    ```markdown\n    example\n    ```\n"""\n```'
        result = self.translate('# English prose\n\n'+code+'\n')
        self.assertEqual(translator.fenced_code_blocks(result), [code])

    def test_tilde_quote_and_indented_fences_are_not_sent_to_the_model(self):
        source = ('# English prose\n\n~~~yaml\nparent:\n  child: value\n~~~\n\n'
                  '> ```python\n> if True:\n>     print("example")\n> ```\n\n'
                  '  ```json\n  {\n    "key": "value"\n  }\n  ```\n')
        sent = []

        def prose(_language, text, *_args, **_kwargs):
            sent.append(text)
            return text.replace('English prose', 'French prose')

        result = self.translate(source, prose)
        self.assertEqual(translator.fenced_code_blocks(result), translator.fenced_code_blocks(source))
        self.assertFalse(any('child: value' in text or 'print(' in text or '"key"' in text for text in sent))

    def test_code_is_not_split_at_the_prose_token_limit(self):
        code = '```python\n'+''.join('    example = 1\n' for _ in range(20))+'```\n'
        with patch.object(translator, 'MAX_TOKENS', 3):
            with patch.object(translator, 'reportTokens', side_effect=lambda text, _model: len(text)):
                chunks = translator.split_text(code, 'test-model')
        self.assertEqual(chunks, [code])

    def test_nested_list_code_preserves_its_list_indentation(self):
        code = '    ```python\n    def example():\n        return 1\n    ```'
        source = '1. English prose\n\n'+code+'\n\n2. English prose\n'
        result = self.translate(source)
        self.assertEqual(translator.fenced_code_blocks(result), [code])
        self.assertIn('2. French prose', result)

    def test_longer_outer_fence_keeps_inner_fences_literal(self):
        code = '````markdown\n```python\n    example = 1\n```\n````'
        self.assertEqual(translator.fenced_code_blocks(self.translate('# English prose\n'+code+'\n')), [code])

    def test_added_code_is_rejected_before_publication(self):
        def added_code(_language, text, *_args, **_kwargs):
            return text+'\n```python\nexample = 1\n```\n'

        with self.assertRaisesRegex(RuntimeError, 'changed fenced code blocks'):
            self.translate('# English prose\n', added_code)


if __name__ == '__main__':
    unittest.main()
