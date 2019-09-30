# -*- coding: utf-8 -*-
"""Unit test for case-conversion
"""
import pytest

from case_conversion import CaseConverter


ACRONYMS = ["HTTP"]
ACRONYMS_UNICODE = ["HÉÉP"]

CASES = [
    "camel",
    "pascal",
    "snake",
    "dash",
    #"spinal",
    #"kebab",
    "const",
    #"screaming_snake",
    "dot",
]

CASES_PRESERVE = ["separate_words", "slash", "backslash"]

VALUES = {
    "camel": "fooBarString",
    "pascal": "FooBarString",
    "snake": "foo_bar_string",
    "dash": "foo-bar-string",
    # "spinal": "foo-bar-string",
    # "kebab": "foo-bar-string",
    "const": "FOO_BAR_STRING",
    #"screaming_snake": "FOO_BAR_STRING",
    "dot": "foo.bar.string",
    "separate_words": "foo bar string",
    "slash": "foo/bar/string",
    "backslash": "foo\\bar\\string",
}

VALUES_UNICODE = {
    "camel": "fóoBarString",
    "pascal": "FóoBarString",
    "snake": "fóo_bar_string",
    "dash": "fóo-bar-string",
    # "spinal": "fóo-bar-string",
    # "kebab": "fóo-bar-string",
    "const": "FÓO_BAR_STRING",
    #"screaming_snake": "FÓO_BAR_STRING",
    "dot": "fóo.bar.string",
    "separate_words": "fóo bar string",
    "slash": "fóo/bar/string",
    "backslash": "fóo\\bar\\string",
}

VALUES_SINGLE = {
    "camel": "foo",
    "pascal": "Foo",
    "snake": "foo",
    "dash": "foo",
    # "spinal": "foo",
    # "kebab": "foo",
    "const": "FOO",
    #"screaming_snake": "FOO",
    "dot": "foo",
    "separate_words": "foo",
    "slash": "foo",
    "backslash": "foo",
}

VALUES_SINGLE_UNICODE = {
    "camel": "fóo",
    "pascal": "Fóo",
    "snake": "fóo",
    "dash": "fóo",
    # "spinal": "fóo",
    # "kebab": "fóo",
    "const": "FÓO",
    #"screaming_snake": "FÓO",
    "dot": "fóo",
    "separate_words": "fóo",
    "slash": "fóo",
    "backslash": "fóo",
}

VALUES_ACRONYM = {
    "camel": "fooHTTPBarString",
    "pascal": "FooHTTPBarString",
    "snake": "foo_http_bar_string",
    "dash": "foo-http-bar-string",
    # "spinal": "foo-http-bar-string",
    # "kebab": "foo-http-bar-string",
    "const": "FOO_HTTP_BAR_STRING",
    #"screaming_snake": "FOO_HTTP_BAR_STRING",
    "dot": "foo.http.bar.string",
    "separate_words": "foo http bar string",
    "slash": "foo/http/bar/string",
    "backslash": "foo\\http\\bar\\string",
}

VALUES_ACRONYM_UNICODE = {
    "camel": "fooHÉÉPBarString",
    "pascal": "FooHÉÉPBarString",
    "snake": "foo_héép_bar_string",
    "dash": "foo-héép-bar-string",
    # "spinal": "foo-héép-bar-string",
    # "kebab": "foo-héép-bar-string",
    "const": "FOO_HÉÉP_BAR_STRING",
    #"screaming_snake": "FOO_HÉÉP_BAR_STRING",
    "dot": "foo.héép.bar.string",
    "separate_words": "foo héép bar string",
    "slash": "foo/héép/bar/string",
    "backslash": "foo\\héép\\bar\\string",
}

PRESERVE_VALUES = {
    "separate_words": {
        "camel": "foo Bar String",
        "pascal": "Foo Bar String",
        "const": "FOO BAR STRING",
        #"screaming_snake": "FOO BAR STRING",
        "default": "foo bar string",
    },
    "slash": {
        "camel": "foo/Bar/String",
        "pascal": "Foo/Bar/String",
        "const": "FOO/BAR/STRING",
        #"screaming_snake": "FOO/BAR/STRING",
        "default": "foo/bar/string",
    },
    "backslash": {
        "camel": "foo\\Bar\\String",
        "pascal": "Foo\\Bar\\String",
        "const": "FOO\\BAR\\STRING",
        #"screaming_snake": "FOO\\BAR\\STRING",
        "default": "foo\\bar\\string",
    },
}

PRESERVE_VALUES_UNICODE = {
    "separate_words": {
        "camel": "fóo Bar String",
        "pascal": "Fóo Bar String",
        "const": "FÓO BAR STRING",
        #"screaming_snake": "FÓO BAR STRING",
        "default": "fóo bar string",
    },
    "slash": {
        "camel": "fóo/Bar/String",
        "pascal": "Fóo/Bar/String",
        "const": "FÓO/BAR/STRING",
        #"screaming_snake": "FÓO/BAR/STRING",
        "default": "fóo/bar/string",
    },
    "backslash": {
        "camel": "fóo\\Bar\\String",
        "pascal": "Fóo\\Bar\\String",
        "const": "FÓO\\BAR\\STRING",
        #"screaming_snake": "FÓO\\BAR\\STRING",
        "default": "fóo\\bar\\string",
    },
}

PRESERVE_VALUES_SINGLE = {
    "separate_words": {
        "camel": "foo",
        "pascal": "Foo",
        "const": "FOO",
        # #"screaming_snake": "FOO",
        "default": "foo",
    },
    "slash": {
        "camel": "foo",
        "pascal": "Foo",
        "const": "FOO",
        # #"screaming_snake": "FOO",
        "default": "foo",
    },
    "backslash": {
        "camel": "foo",
        "pascal": "Foo",
        "const": "FOO",
        # #"screaming_snake": "FOO",
        "default": "foo",
    },
}

PRESERVE_VALUES_SINGLE_UNICODE = {
    "separate_words": {
        "camel": "fóo",
        "pascal": "Fóo",
        "const": "FÓO",
        # #"screaming_snake": "FÓO",
        "default": "fóo",
    },
    "slash": {
        "camel": "fóo",
        "pascal": "Fóo",
        "const": "FÓO",
        # #"screaming_snake": "FÓO",
        "default": "fóo",
    },
    "backslash": {
        "camel": "fóo",
        "pascal": "Fóo",
        "const": "FÓO",
        # #"screaming_snake": "FÓO",
        "default": "fóo",
    },
}

PRESERVE_VALUES_ACRONYM = {
    "separate_words": {
        "camel": "foo HTTP Bar String",
        "pascal": "Foo HTTP Bar String",
        "const": "FOO HTTP BAR STRING",
        # #"screaming_snake": "FOO HTTP BAR STRING",
        "default": "foo http bar string",
    },
    "slash": {
        "camel": "foo/HTTP/Bar/String",
        "pascal": "Foo/HTTP/Bar/String",
        "const": "FOO/HTTP/BAR/STRING",
        # #"screaming_snake": "FOO/HTTP/BAR/STRING",
        "default": "foo/http/bar/string",
    },
    "backslash": {
        "camel": "foo\\HTTP\\Bar\\String",
        "pascal": "Foo\\HTTP\\Bar\\String",
        "const": "FOO\\HTTP\\BAR\\STRING",
        # #"screaming_snake": "FOO\\HTTP\\BAR\\STRING",
        "default": "foo\\http\\bar\\string",
    },
}

PRESERVE_VALUES_ACRONYM_UNICODE = {
    "separate_words": {
        "camel": "foo HÉÉP Bar String",
        "pascal": "Foo HÉÉP Bar String",
        "const": "FOO HÉÉP BAR STRING",
        # #"screaming_snake": "FOO HÉÉP BAR STRING",
        "default": "foo héép bar string",
    },
    "slash": {
        "camel": "foo/HÉÉP/Bar/String",
        "pascal": "Foo/HÉÉP/Bar/String",
        "const": "FOO/HÉÉP/BAR/STRING",
        # #"screaming_snake": "FOO/HÉÉP/BAR/STRING",
        "default": "foo/héép/bar/string",
    },
    "backslash": {
        "camel": "foo\\HÉÉP\\Bar\\String",
        "pascal": "Foo\\HÉÉP\\Bar\\String",
        "const": "FOO\\HÉÉP\\BAR\\STRING",
        # #"screaming_snake": "FOO\\HÉÉP\\BAR\\STRING",
        "default": "foo\\héép\\bar\\string",
    },
}


PRESERVE_VALUES_ACRONYM_SINGLE = {
    "separate_words": {
        "camel": "HTTP",
        "pascal": "HTTP",
        "const": "HTTP",
        #"screaming_snake": "HTTP",
        "default": "http",
    },
    "slash": {
        "camel": "HTTP",
        "pascal": "HTTP",
        "const": "HTTP",
        #"screaming_snake": "HTTP",
        "default": "http",
    },
    "backslash": {
        "camel": "HTTP",
        "pascal": "HTTP",
        "const": "HTTP",
        #"screaming_snake": "HTTP",
        "default": "http",
    },
}

CAPITAL_CASES = ["camel", "pascal", "const", "screaming_snake"]


def _expand_values(values):
    test_params = []
    for case in CASES:
        test_params.extend(
            [
                (name + "2" + case, case, value, values[case])
                for name, value in values.items()
            ]
        )
        test_params.append((case + "_empty", case, "", ""))
    return test_params


def _expand_values_preserve(preserve_values, values):
    test_params = []
    for case in CASES_PRESERVE:
        test_params.extend(
            [
                (
                    name + "2" + case,
                    case,
                    value,
                    preserve_values[case][name if name in CAPITAL_CASES else "default"],
                )  # nopep8
                for name, value in values.items()
            ]
        )
        test_params.append((case + "_empty", case, "", ""))
    return test_params


def _case_check(case, value, expected):
    case_converter = getattr(CaseConverter, case)
    assert case_converter(value) == expected


@pytest.mark.parametrize("name,case,value,expected", _expand_values(VALUES))
def test(name, case, value, expected):
    """
    Test conversions from all cases to all cases that don't preserve
    capital/lower case letters.
    """
    _case_check(case, value, expected)


@pytest.mark.parametrize("name,case,value,expected", _expand_values(VALUES_UNICODE))
def test_unicode(name, case, value, expected):
    """
    Test conversions from all cases to all cases that don't preserve
    capital/lower case letters (with unicode characters).
    """
    _case_check(case, value, expected)


@pytest.mark.parametrize("name,case,value,expected", _expand_values(VALUES_SINGLE))
def test_single(name, case, value, expected):
    """
    Test conversions of single words from all cases to all cases that
    don't preserve capital/lower case letters.
    """
    _case_check(case, value, expected)


@pytest.mark.parametrize(
    "name,case,value,expected", _expand_values(VALUES_SINGLE_UNICODE)
)
def test_single_unicode(name, case, value, expected):
    """
    Test conversions of single words from all cases to all cases that
    don't preserve capital/lower case letters (with unicode characters).
    """
    _case_check(case, value, expected)


@pytest.mark.parametrize(
    "name,case,value,expected", _expand_values_preserve(PRESERVE_VALUES, VALUES)
)
def test_preserve_case(name, case, value, expected):
    """
    Test conversions from all cases to all cases that do preserve
    capital/lower case letters.
    """
    _case_check(case, value, expected)


@pytest.mark.parametrize(
    "name,case,value,expected",
    _expand_values_preserve(PRESERVE_VALUES_UNICODE, VALUES_UNICODE),
)
def test_preserve_case_unicode(name, case, value, expected):
    """
    Test conversions from all cases to all cases that do preserve
    capital/lower case letters (with unicode characters).
    """
    _case_check(case, value, expected)


@pytest.mark.parametrize(
    "name,case,value,expected",
    _expand_values_preserve(PRESERVE_VALUES_SINGLE, VALUES_SINGLE),
)
def test_preserve_case_single(name, case, value, expected):
    """
    Test conversions of single words from all cases to all cases that do
    preserve capital/lower case letters.
    """
    _case_check(case, value, expected)


@pytest.mark.parametrize(
    "name,case,value,expected",
    _expand_values_preserve(PRESERVE_VALUES_SINGLE_UNICODE, VALUES_SINGLE_UNICODE),
)
def test_preserve_case_single_unicode(name, case, value, expected):
    """
    Test conversions of single words from all cases to all cases that do
    preserve capital/lower case letters (with unicode characters).
    """
    _case_check(case, value, expected)


# @pytest.mark.parametrize("name,case,value,expected", _expand_values(VALUES_ACRONYM))
# def test_acronyms(name, case, value, expected):
#     """
#     Test conversions from all cases to all cases that don't preserve
#     capital/lower case letters (with acronym detection).
#     """
#     case_converter = getattr(case_conversion, case)
#     result = case_converter(value, acronyms=ACRONYMS)
#     assert case_converter(result) == expected


# @pytest.mark.parametrize("name,case,value,expected", _expand_values(VALUES_ACRONYM_UNICODE))
# def test_acronyms_unicode(name, case, value, expected):
#     """
#     Test conversions from all cases to all cases that don't preserve
#     capital/lower case letters (with acronym detection and unicode
#     characters).
#     """
#     case_converter = getattr(case_conversion, case)
#     result = case_converter(value, acronyms=ACRONYMS_UNICODE)
#     assert case_converter(result) == expected


# @pytest.mark.parametrize(
#     _expand_values_preserve(PRESERVE_VALUES_ACRONYM, VALUES_ACRONYM)
# )
# def test_acronyms_preserve_case(name, case, value, expected):
#     """
#     Test conversions from all cases to all cases that do preserve
#     capital/lower case letters (with acronym detection).
#     """
#     case_converter = getattr(case_conversion, case)
#     result = case_converter(value, acronyms=ACRONYMS)
#     assert case_converter(result) == expected


# @pytest.mark.parametrize(
#     _expand_values_preserve(PRESERVE_VALUES_ACRONYM_UNICODE, VALUES_ACRONYM_UNICODE)
# )
# def test_acronyms_preserve_case_unicode(name, case, value, expected):
#     """
#     Test conversions from all cases to all cases that do preserve
#     capital/lower case letters (with acronym detection and unicode
#     characters).
#     """
#     case_converter = getattr(case_conversion, case)
#     result = case_converter(value, acronyms=ACRONYMS_UNICODE)
#     assert case_converter(result) == expected
