from enum import Enum, unique
from typing import Any, Sequence, Tuple, Optional
import sys
import unicodedata

__all__ = ("InvalidAcronymError", "Case", "CaseConverter")

StrSeq = Sequence[str]
OptStrSeq = Optional[StrSeq]

def _getSubstringRanges(a_str, sub):
    start = 0
    subLen = len(sub)
    while True:
        start = a_str.find(sub, start)
        if start == -1:
            return
        yield (start, start + subLen)
        start += 1


def _charIsSep(aChar):
    return (
        not _charIsUpper(aChar)
        and not _charIsLower(aChar)
        and not _charIsNumberDecimalDigit(aChar)
    )


def _charIsNumberDecimalDigit(aChar):
    return unicodedata.category(aChar) == "Nd"


def _charIsLower(aChar):
    return unicodedata.category(aChar) == "Ll"


def _charIsUpper(aChar):
    return unicodedata.category(aChar) == "Lu"


def _isUpper(aString):
    return len(aString) == 1 and _charIsUpper(aString)


def _isValidAcronym(aString):
    if len(aString) == 0:
        return False

    for aChar in aString:
        if _charIsSep(aChar):
            return False

    return True


class InvalidAcronymError(ValueError):
    """Raise when acronym fails validation."""

    def __init__(self, acronym: str) -> None:
        print(f"Case Conversion: acronym '{acronym}' is invalid.")
        super(InvalidAcronymError, self).__init__()


@unique
class Case(Enum):
    # - upper: All words are upper-case.
    # - lower: All words are lower-case.
    # - pascal: All words are title-case or upper-case. Note that the
    #           stringiable may still have separators.
    # - camel: First word is lower-case, the rest are title-case or
    #          upper-case. stringiable may still have separators.
    # - mixed: Any other mixing of word casing. Never occurs if there are
    #          no separators.
    # - unknown: stringiable contains no words.
    UNKOWN = "unknown"
    UPPER = "upper"
    LOWER = "lower"
    CAMEL = "camel"
    PASCAL = "pascal"
    MIXED = "mixed"


class CaseConverter:
    """Main Class."""

    @staticmethod
    def _determine_case(was_upper: bool, words: StrSeq, string: str) -> Case:
        """
        Determine case type of string.

        Arguments:
            was_upper (bool) -- [description]
            words {Sequence[str]} -- [description]
            string {str} -- [description]

        Returns:
            Case: TODO: fill this out

        """
        case_type = Case.UNKOWN
        if was_upper:
            case_type = Case.UPPER
        elif string.islower():
            case_type = Case.LOWER
        elif len(words) > 0:
            camel_case = words[0].islower()
            pascal_case = words[0].istitle() or words[0].isupper()

            if camel_case or pascal_case:
                for word in words[1:]:
                    c = word.istitle() or word.isupper()
                    camel_case &= c
                    pascal_case &= c
                    if not c:
                        break

            if camel_case:
                case_type = Case.CAMEL
            elif pascal_case:
                case_type = Case.PASCAL
            else:
                case_type = Case.MIXED

        return case_type

    @staticmethod
    def _advanced_acronym_detection(
        s: int, i: int, words: StrSeq, acronyms: StrSeq
    ) -> int:
        """
        Detect acronyms by checking against a list of acronyms.

        Check a run of words represented by the range [s, i].
        Return last index of new word groups.
        """
        # Combine each letter into single string.
        acstr = "".join(words[s:i])

        # List of ranges representing found acronyms.
        range_list = []
        # Set of remaining letters.
        not_range = set(range(len(acstr)))

        # Search for each acronym in acstr.
        for acronym in acronyms:
            for (a, b) in _getSubstringRanges(acstr, acronym):
                # Make sure found acronym doesn't overlap with others.
                ok = True
                for r in range_list:
                    if a < r[1] and b > r[0]:
                        ok = False
                        break

                if ok:
                    range_list.append((a, b))
                    for j in range(a, b):
                        not_range.remove(j)

        # Add remaining letters as ranges.
        for nr in not_range:
            range_list.append((nr, nr + 1))

        # No ranges will overlap, so it's safe to sort by lower bound,
        # which sort() will do by default.
        range_list.sort()

        # Remove original letters in word list.
        for _ in range(s, i):
            del words[s]

        # Replace them with new word grouping.
        for j in range(len(range_list)):
            r = range_list[j]
            words.insert(s + j, acstr[r[0] : r[1]])

        return s + len(range_list) - 1

    @staticmethod
    def _simple_acronym_detection(s: int, i: int, words: StrSeq, *args: Any) -> int:
        """Detect acronyms based on runs of upper-case letters."""
        # Combine each letter into a single string.
        acronym = "".join(words[s:i])

        # Remove original letters in word list.
        for _ in range(s, i):
            del words[s]

        # Replace them with new word grouping.
        words.insert(s, "".join(acronym))
        return s

    @staticmethod
    def _sanitize_acronyms(unsafe_acronyms: StrSeq) -> StrSeq:
        """

        Normalize valid acronyms to upper-case.
        If an invalid acronym is encountered (contains separators)
        raise InvalidAcronymError.
        """
        acronyms = []
        for a in unsafe_acronyms:
            if _isValidAcronym(a):
                acronyms.append(a.upper())
            else:
                raise InvalidAcronymError(a)
        return acronyms

    @staticmethod
    def _normalize_words(words: StrSeq, acronyms: StrSeq) -> StrSeq:
        """Normalize case of each word to PascalCase."""
        for i, _ in enumerate(words):
            # if detect_acronyms:
            if words[i].upper() in acronyms:
                # Convert known acronyms to upper-case.
                words[i] = words[i].upper()
            elif not words[i].isupper():
                # Fallback behavior: Preserve case on upper-case words.
                words[i] = words[i].capitalize()
        return words

    @classmethod
    def _segment_string(cls, string: str) -> Tuple[StrSeq, str, bool]:
        """
        Segment string on separator into list of words.

        Arguments:
            string -- the string we want to process

        Returns:
            words -- list of words the string got minced to
            separator -- the separator char intersecting words
            was_upper -- whether string happened to be upper-case

        """
        words = []
        separator = ""

        # curr_index of current character. Initially 1 because we don't
        # want to check if the 0th character is a boundary.
        curr_i = 1
        # Index of first character in a sequence
        seq_i = 0
        # Previous character.
        prev_i = string[0:1]

        # Treat an all-caps stringiable as lower-case, to prevent its
        # letters to be counted as boundaries
        was_upper = False
        if string.isupper():
            string = string.lower()
            was_upper = True

        # Iterate over each character, checking for boundaries, or places
        # where the stringiable should divided.
        while curr_i <= len(string):
            char = string[curr_i : curr_i + 1]
            split = False
            if curr_i < len(string):
                # Detect upper-case letter as boundary.
                if _charIsUpper(char):
                    split = True
                # Detect transition from separator to not separator.
                elif not _charIsSep(char) and _charIsSep(prev_i):
                    split = True
                # Detect transition not separator to separator.
                elif _charIsSep(char) and not _charIsSep(prev_i):
                    split = True
            else:
                # The looprev_igoes one extra iteration so that it can
                # handle the remaining text after the last boundary.
                split = True

            if split:
                if not _charIsSep(prev_i):
                    words.append(string[seq_i:curr_i])
                else:
                    # stringiable contains at least one separator.
                    # Use the first one as the stringiable's primary separator.
                    if not separator:
                        separator = string[seq_i : seq_i + 1]

                    # Use None to indicate a separator in the word list.
                    words.append(None)
                    # If separators weren't included in the list, then breaks
                    # between upper-case sequences ("AAA_BBB") would be
                    # disregarded; the letter-run detector would count them
                    # as a single sequence ("AAABBB").
                seq_i = curr_i

            curr_i += 1
            prev_i = char

        return words, separator, was_upper

    @classmethod
    def parse_case(
        cls, string: str, acronyms: OptStrSeq = None, preserve_case: bool = False
    ) -> Tuple[StrSeq, Case, str]:
        """
        Parse a stringiable into a list of words.

        Also returns the case type, which can be one of the following:
            - upper: All words are upper-case.
            - lower: All words are lower-case.
            - pascal: All words are title-case or upper-case. Note that the
                      stringiable may still have separators.
            - camel: First word is lower-case, the rest are title-case or
                     upper-case. stringiable may still have separators.
            - mixed: Any other mixing of word casing. Never occurs if there are
                     no separators.
            - unknown: stringiable contains no words.

        Also returns the first separator character,
        or False if there isn't one.
        """
        words, separator, was_upper = cls._segment_string(string)

        if acronyms:
            # Use advanced acronym detection with list
            acronyms = cls._sanitize_acronyms(acronyms)
            check_acronym = cls._advanced_acronym_detection
        else:
            acronyms = []
            # Fallback to simple acronym detection.
            check_acronym = cls._simple_acronym_detection

        # Letter-run detector

        # Index of current word.
        i = 0
        # Index of first letter in run.
        s = None

        # Find runs of single upper-case letters.
        while i < len(words):
            word = words[i]
            if word is not None and _isUpper(word):
                if s is None:
                    s = i
            elif s is not None:
                i = check_acronym(s, i, words, acronyms) + 1
                s = None
            i += 1

        if s is not None:
            check_acronym(s, i, words, acronyms)

        # Separators are no longer needed, so they should be removed.
        words = [w for w in words if w is not None]

        # Determine case type.
        case_type = cls._determine_case(was_upper, words, string)

        if preserve_case:
            if was_upper:
                words = [w.upper() for w in words]
        else:
            words = cls._normalize_words(words, acronyms)

        return words, case_type, separator

    @classmethod
    def camel(cls, text: str, acronyms: OptStrSeq = None) -> str:
        """Converts text to camelCase style.

        Args:
            text (str): input string to convert case
            acronyms (Optional[Sequence[str]]): a list of acronyms to detect

        Returns:
            str: Case converted text.

        >>> camel("hello world")
        'helloWorld'
        >>> camel("HELLO_HTML_WORLD", ["HTML"])
        'helloHTMLWorld'
        """
        words, _case, _sep = cls.parse_case(text, acronyms)
        if words:
            words[0] = words[0].lower()
        return "".join(words)

    @classmethod
    def pascal(cls, text: str, acronyms: OptStrSeq = None) -> str:
        """Converts text to PascalCase style.

        Synonyms:
            MixedCase

        Args:
            text (str): input string to convert case
            acronyms (Optional[Sequence[str]]): a list of acronyms to detect

        Returns:
            str: Case converted text.

        >>> pascal("hello world")
        'HelloWorld'
        >>> pascal("HELLO_HTML_WORLD", ["HTML"])
        'HelloHTMLWorld'
        """
        words, _case, _sep = cls.parse_case(text, acronyms)
        return "".join(words)

    @classmethod
    def snake(cls, text: str, acronyms: OptStrSeq = None) -> str:
        """Converts text to snake_case style.

        Args:
            text (str): input string to convert case
            acronyms (Optional[Sequence[str]]): a list of acronyms to detect

        Returns:
            str: Case converted text.

        >>> snake("hello world")
        'hello_world'
        >>> snake("HelloHTMLWorld", ["HTML"])
        'hello_html_world'
        """
        words, _case, _sep = cls.parse_case(text, acronyms)
        return "_".join([w.lower() for w in words])

    @classmethod
    def dash(cls, text: str, acronyms: OptStrSeq = None) -> str:
        """Converts text to dash-case style.

        Synonyms:
            kebab-case
            spinal-case
            slug-case

        Args:
            text (str): input string to convert case
            acronyms (Optional[Sequence[str]]): a list of acronyms to detect

        Returns:
            str: Case converted text.

        >>> dash("hello world")
        'hello-world'
        >>> dash("HelloHTMLWorld", ["HTML"])
        'hello-html-world'
        """
        words, _case, _sep = cls.parse_case(text, acronyms)
        return "-".join([w.lower() for w in words])

    @classmethod
    def const(cls, text: str, acronyms: OptStrSeq = None) -> str:
        """Converts text to CONST_CASE style.

        Synonyms:
            SCREAMING_SNAKE_CASE

        Args:
            text: input string to convert case
            detect_acronyms: should attempt to detect acronyms
            acronyms: a list of acronyms to detect

        >>> constcase("hello world")
        'HELLO_WORLD'
        >>> constcase("helloHTMLWorld", True, ["HTML"])
        'HELLO_HTML_WORLD'
        """
        words, _case, _sep = cls.parse_case(text, acronyms)
        return "_".join([w.upper() for w in words])

    @classmethod
    def dot(cls, text: str, acronyms: OptStrSeq = None) -> str:
        """Converts text to dot.case style.

        Args:
            text (str): input string to convert case
            acronyms (Optional[Sequence[str]]): a list of acronyms to detect

        Returns:
            str: Case converted text.

        >>> dot("hello world")
        'hello.world'
        >>> dot("helloHTMLWorld", ["HTML"])
        'hello.html.world'
        """
        words, _case, _sep = cls.parse_case(text, acronyms)
        return ".".join([w.lower() for w in words])

    @classmethod
    def separate_words(cls, text: str, acronyms: OptStrSeq = None) -> str:
        """Converts text to "seperate words" style.

        Args:
            text (str): input string to convert case
            acronyms (Optional[Sequence[str]]): a list of acronyms to detect

        Returns:
            str: Case converted text.

        >>> separate_words("HELLO_WORLD")
        'HELLO WORLD'
        >>> separate_words("helloHTMLWorld", ["HTML"])
        'hello HTML World'
        """
        words, _case, _sep = cls.parse_case(text, acronyms, preserve_case=True)
        return " ".join(words)

    @classmethod
    def slash(cls, text: str, acronyms: OptStrSeq = None) -> str:
        """Converts text to slash/case style.

        Args:
            text (str): input string to convert case
            acronyms (Optional[Sequence[str]]): a list of acronyms to detect

        Returns:
            str: Case converted text.

        >>> slash("HELLO_WORLD")
        'HELLO/WORLD'
        >>> slash("helloHTMLWorld", ["HTML"])
        'hello/HTML/World'
        """
        words, _case, _sep = cls.parse_case(text, acronyms, preserve_case=True)
        return "/".join(words)

    @classmethod
    def backslash(cls, text: str, acronyms: OptStrSeq = None) -> str:
        r"""Converts text to backslash\case style.

        Args:
            text (str): input string to convert case
            acronyms (Optional[Sequence[str]]): a list of acronyms to detect

        Returns:
            str: Case converted text.

        >>> backslash("HELLO_WORLD")
        'HELLO\WORLD'
        >>> backslash("helloHTMLWorld", ["HTML"])
        'hello\HTML\World'
        """
        words, _case, _sep = cls.parse_case(text, acronyms, preserve_case=True)
        return "\\".join(words)

    @classmethod
    def ada(cls, text: str, acronyms: OptStrSeq = None) -> str:
        """Converts text to Ada_Case style.

        Synonyms:
            camel_snake_case

        Args:
            text (str): input string to convert case
            acronyms (Optional[Sequence[str]]): a list of acronyms to detect

        Returns:
            str: Case converted text.

        >>> http_header("hello world")
        'Hello_World'
        >>> http_header("HELLO_HTML_WORLD", ["HTML"])
        'Hello_HTML_World'
        """
        words, _case, _sep = cls.parse_case(text, acronyms)
        return "_".join([w.capitalize() for w in words])

    @classmethod
    def title(cls, text: str, acronyms: OptStrSeq = None) -> str:
        """Converts text to Title_case style.

        Args:
            text (str): input string to convert case
            acronyms (Optional[Sequence[str]]): a list of acronyms to detect

        Returns:
            str: Case converted text.

        >>> http_header("hello world")
        'Hello World'
        >>> http_header("HELLO_HTML_WORLD", ["HTML"])
        'Hello_HTML_World'
        """
        return cls.snake(text, acronyms).capitalize()

    @classmethod
    def lower(cls, text: str, acronyms: OptStrSeq = None) -> str:
        """Converts text to lowercase style.

        Args:
            text (str): input string to convert case
            acronyms (Optional[Sequence[str]]): a list of acronyms to detect

        Returns:
            str: Case converted text.

        >>> http_header("HELLO WORLD")
        'hello world'
        >>> http_header("HELLO_HTML_WORLD", ["HTML"])
        'hello_HTML_world'
        """
        return text.lower()

    @classmethod
    def upper(cls, text: str, acronyms: OptStrSeq = None) -> str:
        """Converts text to UPPERCASE style.

        Args:
            text (str): input string to convert case
            acronyms (Optional[Sequence[str]]): a list of acronyms to detect

        Returns:
            str: Case converted text.

        >>> http_header("hello world")
        'HELLO WORLD'
        >>> http_header("HELLO_HTML_WORLD", ["HTML"])
        'HELLO_HTML_WORLD'
        """
        return text.upper()

    @classmethod
    def capital(cls, text: str, acronyms: OptStrSeq = None) -> str:
        """Converts text to Capitalcase style.

        Args:
            text (str): input string to convert case
            acronyms (Optional[Sequence[str]]): a list of acronyms to detect

        Returns:
            str: Case converted text.

        >>> http_header("hello world")
        'Helloworld'
        >>> http_header("HELLO_HTML_WORLD", ["HTML"])
        'HelloHTMLworld'
        """
        return text.capitalize()

    @classmethod
    def http_header(cls, text: str, acronyms: OptStrSeq = None) -> str:
        """Converts text to Http-Header-Case style.

        Args:
            text (str): input string to convert case
            acronyms (Optional[Sequence[str]]): a list of acronyms to detect

        Returns:
            str: Case converted text.

        >>> http_header("hello world")
        'HelloWorld'
        >>> http_header("HELLO_HTML_WORLD", ["HTML"])
        'Hello-HTML-World'
        """
        words, _case, _sep = cls.parse_case(text, acronyms)
        return "-".join([w.capitalize() for w in words])
