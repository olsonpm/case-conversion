# coding=utf-8
"""Unit test for case-conversion
"""

import case_conversion
from unittest import TestCase
from nose_parameterized import parameterized

ACRONYMS = ['HTTP']
ACRONYMS_UNICODE = [u'HÉÉP']

CASES = [
    'camelcase',
    'pascalcase',
    'snakecase',
    'dashcase',
    'spinalcase',
    'kebabcase',
    'constcase',
    'dotcase',
]

CASES_PRESERVE = [
    'separate_words',
    'slashcase',
    'backslashcase',
]

VALUES = {
    'camelcase': 'fooBarString',
    'pascalcase': 'FooBarString',
    'snakecase': 'foo_bar_string',
    'dashcase': 'foo-bar-string',
    'spinalcase': 'foo-bar-string',
    'kebabcase': 'foo-bar-string',
    'constcase': 'FOO_BAR_STRING',
    'dotcase': 'foo.bar.string',
    'separate_words': 'foo bar string',
    'slashcase': 'foo/bar/string',
    'backslashcase': 'foo\\bar\\string',
}

VALUES_UNICODE = {
    'camelcase': u'fóoBarString',
    'pascalcase': u'FóoBarString',
    'snakecase': u'fóo_bar_string',
    'dashcase': u'fóo-bar-string',
    'spinalcase': u'fóo-bar-string',
    'kebabcase': u'fóo-bar-string',
    'constcase': u'FÓO_BAR_STRING',
    'dotcase': u'fóo.bar.string',
    'separate_words': u'fóo bar string',
    'slashcase': u'fóo/bar/string',
    'backslashcase': u'fóo\\bar\\string',
}

VALUES_ACRONYM = {
    'camelcase': 'fooHTTPBarString',
    'pascalcase': 'FooHTTPBarString',
    'snakecase': 'foo_http_bar_string',
    'dashcase': 'foo-http-bar-string',
    'spinalcase': 'foo-http-bar-string',
    'kebabcase': 'foo-http-bar-string',
    'constcase': 'FOO_HTTP_BAR_STRING',
    'dotcase': 'foo.http.bar.string',
    'separate_words': 'foo http bar string',
    'slashcase': 'foo/http/bar/string',
    'backslashcase': 'foo\\http\\bar\\string',
}

VALUES_ACRONYM_UNICODE = {
    'camelcase': u'fooHÉÉPBarString',
    'pascalcase': u'FooHÉÉPBarString',
    'snakecase': u'foo_héép_bar_string',
    'dashcase': u'foo-héép-bar-string',
    'spinalcase': u'foo-héép-bar-string',
    'kebabcase': u'foo-héép-bar-string',
    'constcase': u'FOO_HÉÉP_BAR_STRING',
    'dotcase': u'foo.héép.bar.string',
    'separate_words': u'foo héép bar string',
    'slashcase': u'foo/héép/bar/string',
    'backslashcase': u'foo\\héép\\bar\\string',
}

PRESERVE_VALUES = {
    'separate_words': {'camelcase': 'foo Bar String',
                       'pascalcase': 'Foo Bar String',
                       'constcase': 'FOO BAR STRING',
                       'default': 'foo bar string'},
    'slashcase': {'camelcase': 'foo/Bar/String',
                  'pascalcase': 'Foo/Bar/String',
                  'constcase': 'FOO/BAR/STRING',
                  'default': 'foo/bar/string'},
    'backslashcase': {'camelcase': 'foo\\Bar\\String',
                      'pascalcase': 'Foo\\Bar\\String',
                      'constcase': 'FOO\\BAR\\STRING',
                      'default': 'foo\\bar\\string'},
}

PRESERVE_VALUES_UNICODE = {
    'separate_words': {'camelcase': u'fóo Bar String',
                       'pascalcase': u'Fóo Bar String',
                       'constcase': u'FÓO BAR STRING',
                       'default': u'fóo bar string'},
    'slashcase': {'camelcase': u'fóo/Bar/String',
                  'pascalcase': u'Fóo/Bar/String',
                  'constcase': u'FÓO/BAR/STRING',
                  'default': u'fóo/bar/string'},
    'backslashcase': {'camelcase': u'fóo\\Bar\\String',
                      'pascalcase': u'Fóo\\Bar\\String',
                      'constcase': u'FÓO\\BAR\\STRING',
                      'default': u'fóo\\bar\\string'},
}

PRESERVE_VALUES_ACRONYM = {
    'separate_words': {'camelcase': 'foo HTTP Bar String',
                       'pascalcase': 'Foo HTTP Bar String',
                       'constcase': 'FOO HTTP BAR STRING',
                       'default': 'foo http bar string'},
    'slashcase': {'camelcase': 'foo/HTTP/Bar/String',
                  'pascalcase': 'Foo/HTTP/Bar/String',
                  'constcase': 'FOO/HTTP/BAR/STRING',
                  'default': 'foo/http/bar/string'},
    'backslashcase': {'camelcase': 'foo\\HTTP\\Bar\\String',
                      'pascalcase': 'Foo\\HTTP\\Bar\\String',
                      'constcase': 'FOO\\HTTP\\BAR\\STRING',
                      'default': 'foo\\http\\bar\\string'},
}

PRESERVE_VALUES_ACRONYM_UNICODE = {
    'separate_words': {'camelcase': u'foo HÉÉP Bar String',
                       'pascalcase': u'Foo HÉÉP Bar String',
                       'constcase': u'FOO HÉÉP BAR STRING',
                       'default': u'foo héép bar string'},
    'slashcase': {'camelcase': u'foo/HÉÉP/Bar/String',
                  'pascalcase': u'Foo/HÉÉP/Bar/String',
                  'constcase': u'FOO/HÉÉP/BAR/STRING',
                  'default': u'foo/héép/bar/string'},
    'backslashcase': {'camelcase': u'foo\\HÉÉP\\Bar\\String',
                      'pascalcase': u'Foo\\HÉÉP\\Bar\\String',
                      'constcase': u'FOO\\HÉÉP\\BAR\\STRING',
                      'default': u'foo\\héép\\bar\\string'},
}

CAPITAL_CASES = [
    'camelcase',
    'pascalcase',
    'constcase',
]


class CaseConversionTest(TestCase):
    @parameterized.expand(
        [item for sublist in [[(name + '2' + case, case, value, VALUES[case]) for name, value in VALUES.iteritems()] + [(case + '_empty', case, '', '')] for case in CASES] for item in sublist])  # nopep8
    def test(self, _, case, value, expected):
        """
        Tests conversions from all cases to all cases that don't preserve
        capital/lower case letters
        """
        case_converter = getattr(case_conversion, case)
        self.assertEqual(case_converter(value), expected)

    @parameterized.expand(
        [item for sublist in [[(name + '2' + case, case, value, VALUES_UNICODE[case]) for name, value in VALUES_UNICODE.iteritems()] + [(case + '_empty', case, '', '')] for case in CASES] for item in sublist])  # nopep8
    def test_unicode(self, _, case, value, expected):
        """
        Tests conversions from all cases to all cases that don't preserve
        capital/lower case letters (with unicode characters)
        """
        case_converter = getattr(case_conversion, case)
        self.assertEqual(case_converter(value), expected)

    @parameterized.expand(
        [item for sublist in [[(name + '2' + case, case, value, PRESERVE_VALUES[case][name if name in CAPITAL_CASES else 'default']) for name, value in VALUES.iteritems()] + [(case + '_empty', case, '', '')] for case in CASES_PRESERVE] for item in sublist])  # nopep8
    def test_preserve_case(self, _, case, value, expected):
        """
        Tests conversions from all cases to all cases that do preserve
        capital/lower case letters
        """
        case_converter = getattr(case_conversion, case)
        self.assertEqual(case_converter(value), expected)

    @parameterized.expand(
        [item for sublist in [[(name + '2' + case, case, value, PRESERVE_VALUES_UNICODE[case][name if name in CAPITAL_CASES else 'default']) for name, value in VALUES_UNICODE.iteritems()] + [(case + '_empty', case, '', '')] for case in CASES_PRESERVE] for item in sublist])  # nopep8
    def test_preserve_case_unicode(self, _, case, value, expected):
        """
        Tests conversions from all cases to all cases that do preserve
        capital/lower case letters (with unicode characters)
        """
        case_converter = getattr(case_conversion, case)
        self.assertEqual(case_converter(value), expected)

    @parameterized.expand(
        [item for sublist in [[(name + '2' + case, case, value, VALUES_ACRONYM[case]) for name, value in VALUES_ACRONYM.iteritems()] + [(case + '_empty', case, '', '')] for case in CASES] for item in sublist])  # nopep8
    def test_acronyms(self, _, case, value, expected):
        """
        Tests conversions from all cases to all cases that don't preserve
        capital/lower case letters
        """
        case_converter = getattr(case_conversion, case)
        result = case_converter(value, detectAcronyms=True, acronyms=ACRONYMS)
        self.assertEqual(result, expected)

    @parameterized.expand(
        [item for sublist in [[(name + '2' + case, case, value, VALUES_ACRONYM_UNICODE[case]) for name, value in VALUES_ACRONYM_UNICODE.iteritems()] + [(case + '_empty', case, '', '')] for case in CASES] for item in sublist])  # nopep8
    def test_acronyms_unicode(self, _, case, value, expected):
        """
        Tests conversions from all cases to all cases that don't preserve
        capital/lower case letters (with unicode characters)
        """
        case_converter = getattr(case_conversion, case)
        result = case_converter(value, detectAcronyms=True,
                                acronyms=ACRONYMS_UNICODE)
        self.assertEqual(result, expected)

    @parameterized.expand(
        [item for sublist in [[(name + '2' + case, case, value, PRESERVE_VALUES_ACRONYM[case][name if name in CAPITAL_CASES else 'default']) for name, value in VALUES_ACRONYM.iteritems()] + [(case + '_empty', case, '', '')] for case in CASES_PRESERVE] for item in sublist])  # nopep8
    def test_acronyms_preserve_case(self, _, case, value, expected):
        """
        Tests conversions from all cases to all cases that do preserve
        capital/lower case letters
        """
        case_converter = getattr(case_conversion, case)
        result = case_converter(value, detectAcronyms=True, acronyms=ACRONYMS)
        self.assertEqual(result, expected)

    @parameterized.expand(
        [item for sublist in [[(name + '2' + case, case, value, PRESERVE_VALUES_ACRONYM_UNICODE[case][name if name in CAPITAL_CASES else 'default']) for name, value in VALUES_ACRONYM_UNICODE.iteritems()] + [(case + '_empty', case, '', '')] for case in CASES_PRESERVE] for item in sublist])  # nopep8
    def test_acronyms_preserve_case_unicode(self, _, case, value, expected):
        """
        Tests conversions from all cases to all cases that do preserve
        capital/lower case letters
        """
        case_converter = getattr(case_conversion, case)
        result = case_converter(value, detectAcronyms=True,
                                acronyms=ACRONYMS_UNICODE)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    from unittest import main

    main()
