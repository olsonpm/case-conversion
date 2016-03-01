"""Unit test for case-conversion
"""

import case_conversion
from unittest import TestCase
from nose_parameterized import parameterized

NO_PRESERVE_CASES = [
    'camelcase',
    'pascalcase',
    'snakecase',
    'dashcase',
    'constcase',
    'dotcase',
]

PRESERVE_CASES = [
    'separate_words',
    'slashcase',
    'backslashcase',
]

VALUES = {
    'camelcase': 'fooBarString',
    'pascalcase': 'FooBarString',
    'snakecase': 'foo_bar_string',
    'dashcase': 'foo-bar-string',
    'constcase': 'FOO_BAR_STRING',
    'dotcase': 'foo.bar.string',
    'separate_words': 'foo bar string',
    'slashcase': 'foo/bar/string',
    'backslashcase': 'foo\\bar\\string',
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

CAPITAL_CASES = [
    'camelcase',
    'pascalcase',
    'constcase',
]


class CaseConversionTest(TestCase):
    @parameterized.expand(
        [item for sublist in [[(name + '2' + case, case, value, VALUES[case]) for name, value in VALUES.iteritems()] + [(case + '_empty', case, '', '')] for case in NO_PRESERVE_CASES] for item in sublist])  # nopep8
    def test_no_preserve(self, _name, case, value, expected):
        """
        Tests conversions from all cases to all cases that don't preserve
        capital/lower case letters
        """
        case_converter = getattr(case_conversion, case)
        self.assertEqual(case_converter(value), expected)

    @parameterized.expand(
        [item for sublist in [[(name + '2' + case, case, value, PRESERVE_VALUES[case][name if name in CAPITAL_CASES else 'default']) for name, value in VALUES.iteritems()] + [(case + '_empty', case, '', '')] for case in PRESERVE_CASES] for item in sublist])  # nopep8
    def test_preserve(self, _name, case, value, expected):
        """
        Tests conversions from all cases to all cases that do preserve
        capital/lower case letters
        """
        case_converter = getattr(case_conversion, case)
        self.assertEqual(case_converter(value), expected)


if __name__ == '__main__':
    from unittest import main

    main()
