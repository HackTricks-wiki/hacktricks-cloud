import unittest

from translator import preserve_mdbook_directives, preserve_reference_markup


class PreserveMdbookDirectivesTests(unittest.TestCase):
    def test_restores_translated_directive_and_attribute_names(self):
        source = '''{{#tabs }}
{{#tab name="API" }}
Use the API.
{{#endtab }}
{{#endtabs }}'''
        translated = '''{{#oortjies }}
{{#oortjie naam="API" }}
Gebruik die API.
{{#eindoortjie }}
{{#eindoortjies }}'''

        self.assertEqual(
            preserve_mdbook_directives(source, translated),
            '''{{#tabs }}
{{#tab name="API" }}
Gebruik die API.
{{#endtab }}
{{#endtabs }}''',
        )

    def test_restores_attribute_when_directive_name_was_preserved(self):
        source = '{{#tab name="API" }}\nUse the API.\n{{#endtab }}'
        translated = '{{#tab naam="API" }}\nGebruik die API.\n{{#endtab }}'

        self.assertEqual(
            preserve_mdbook_directives(source, translated),
            '{{#tab name="API" }}\nGebruik die API.\n{{#endtab }}',
        )

    def test_falls_back_to_source_when_directive_count_changes(self):
        source = '{{#tabs }}\n{{#endtabs }}'
        translated = '{{#tabs }}\nVertaalde teks'

        self.assertEqual(preserve_mdbook_directives(source, translated), source)

    def test_leaves_plain_translation_unchanged(self):
        self.assertEqual(
            preserve_mdbook_directives('Original prose', 'Translated prose'),
            'Translated prose',
        )


class PreserveReferenceMarkupTests(unittest.TestCase):
    def test_restores_citations_numbers_and_urls_but_keeps_translated_titles(self):
        source = '''Claim.<sup>[[1]](#references)[[2]](#references)</sup>

## References

- [1] [First source](https://example.com/one)
- [2] [Second source](https://example.com/two)'''
        translated = '''Afirmación.<sup>[[9]](#references)</sup><sup>[[8]](#references)</sup>

## References

- [9] [Primera fuente](https://invalid.example/one)
- [8] [Segunda fuente](https://invalid.example/two)'''

        self.assertEqual(preserve_reference_markup(source, translated), source)

        translated = '''Afirmación.<sup>[[9]](#references)[[8]](#references)</sup>

## References

- [9] [Primera fuente](https://invalid.example/one)
- [8] [Segunda fuente](https://invalid.example/two)'''
        self.assertEqual(
            preserve_reference_markup(source, translated),
            '''Afirmación.<sup>[[1]](#references)[[2]](#references)</sup>

## References

- [1] [Primera fuente](https://example.com/one)
- [2] [Segunda fuente](https://example.com/two)''',
        )

    def test_falls_back_when_references_heading_is_translated(self):
        source = '''Claim.<sup>[[1]](#references)</sup>

## References

- [1] [Source](https://example.com/source)'''
        translated = '''Afirmación.<sup>[[1]](#references)</sup>

## Referencias

- [1] [Fuente](https://example.com/source)'''

        self.assertEqual(preserve_reference_markup(source, translated), source)

    def test_leaves_text_without_references_unchanged(self):
        self.assertEqual(
            preserve_reference_markup('Original prose', 'Translated prose'),
            'Translated prose',
        )


if __name__ == '__main__':
    unittest.main()
