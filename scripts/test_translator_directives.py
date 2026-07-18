import unittest

from translator import preserve_mdbook_directives


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


if __name__ == '__main__':
    unittest.main()
