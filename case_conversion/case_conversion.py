import sys

import regex

PYTHON2 = sys.version_info[0] < 3
if not PYTHON2:
    xrange = range
    unicode = str

UPPER = regex.compile(u'^[\p{Lu}]$')
SEP = regex.compile(u'^[^\p{Ll}\p{Lu}\p{Nd}]$')
NOTSEP = regex.compile(u'^[\p{Ll}\p{Lu}\p{Nd}]$')


def aliased(klass):
    """
    Use in combination with `@alias` decorator.

    Classes decorated with @aliased will have their aliased methods
    (via @alias) actually aliased.
    """
    methods = klass.__dict__.copy()
    for method in methods.values():
        if hasattr(method, '_aliases'):
            # add aliases but don't override attributes of 'klass'
            try:
                for alias in method._aliases - set(methods):
                    setattr(klass, alias, method)
            except TypeError:
                pass
    return klass


class alias(object):
    """
    Decorator for aliasing method names.

    Only works within classes decorated with '@aliased'
    """

    def __init__(self, *aliases):
        self.aliases = set(aliases)

    def __call__(self, f):
        f._aliases = self.aliases
        return f


class InvalidAcronymError(Exception):
    """Raise when acronym fails validation."""

    def __init__(self, acronym):
        super(InvalidAcronymError, self).__init__()
        m = "Case Conversion: acronym '{}' is invalid."
        print(m.format(acronym))


@aliased
class CaseConverter(object):
    """Main Class."""

    @staticmethod
    def _determine_case(was_upper, words, string):
        """
        Determine case type of string.

        Arguments:
            was_upper {[type]} -- [description]
            words {[type]} -- [description]
            string {[type]} -- [description]

        Returns:
            - upper: All words are upper-case.
            - lower: All words are lower-case.
            - pascal: All words are title-case or upper-case. Note that the
                      stringiable may still have separators.
            - camel: First word is lower-case, the rest are title-case or
                     upper-case. stringiable may still have separators.
            - mixed: Any other mixing of word casing. Never occurs if there are
                     no separators.
            - unknown: stringiable contains no words.

        """
        case_type = 'unknown'
        if was_upper:
            case_type = 'upper'
        elif string.islower():
            case_type = 'lower'
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
                case_type = 'camel'
            elif pascal_case:
                case_type = 'pascal'
            else:
                case_type = 'mixed'

        return case_type

    @staticmethod
    def _advanced_acronym_detection(s, i, words, acronyms):
        """
        Detect acronyms by checking against a list of acronyms.

        Check a run of words represented by the range [s, i].
        Return last index of new word groups.
        """
        # Combine each letter into single string.
        acstr = ''.join(words[s:i])

        # List of ranges representing found acronyms.
        range_list = []
        # Set of remaining letters.
        not_range = set(range(len(acstr)))

        # Search for each acronym in acstr.
        for acronym in acronyms:
            rac = regex.compile(unicode(acronym))

            # Loop until all instances of the acronym are found,
            # instead of just the first.
            n = 0
            while True:
                m = rac.search(acstr, n)
                if not m:
                    break

                a, b = m.start(), m.end()
                n = b

                # Make sure found acronym doesn't overlap with others.
                ok = True
                for r in range_list:
                    if a < r[1] and b > r[0]:
                        ok = False
                        break

                if ok:
                    range_list.append((a, b))
                    for j in xrange(a, b):
                        not_range.remove(j)

        # Add remaining letters as ranges.
        for nr in not_range:
            range_list.append((nr, nr + 1))

        # No ranges will overlap, so it's safe to sort by lower bound,
        # which sort() will do by default.
        range_list.sort()

        # Remove original letters in word list.
        for _ in xrange(s, i):
            del words[s]

        # Replace them with new word grouping.
        for j in xrange(len(range_list)):
            r = range_list[j]
            words.insert(s + j, acstr[r[0]:r[1]])

        return s + len(range_list) - 1

    @staticmethod
    def _simple_acronym_detection(s, i, words, *args):
        """Detect acronyms based on runs of upper-case letters."""
        # Combine each letter into a single string.
        acronym = ''.join(words[s:i])

        # Remove original letters in word list.
        for _ in xrange(s, i):
            del words[s]

        # Replace them with new word grouping.
        words.insert(s, ''.join(acronym))

        return s

    @staticmethod
    def _sanitize_acronyms(unsafe_acronyms):
        """
        Check acronyms against regex.

        Normalize valid acronyms to upper-case.
        If an invalid acronym is encountered raise InvalidAcronymError.
        """
        valid_acronym = regex.compile(u'^[\p{Ll}\p{Lu}\p{Nd}]+$')
        acronyms = []
        for a in unsafe_acronyms:
            if valid_acronym.match(a):
                acronyms.append(a.upper())
            else:
                raise InvalidAcronymError(a)
        return acronyms

    @staticmethod
    def _normalize_words(words, acronyms):
        """Normalize case of each word to PascalCase."""
        for i, _ in enumerate(words):
            # if detect_acronyms:
            if words[i].upper() in acronyms:
                # Convert known acronyms to upper-case.
                words[i] = words[i].upper()
            else:
                # Fallback behavior: Preserve case on upper-case words.
                if not words[i].isupper():
                    words[i] = words[i].capitalize()
        return words

    @classmethod
    def _segment_string(cls, string):
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
            char = string[curr_i:curr_i + 1]

            split = False
            if curr_i < len(string):
                # Detect upper-case letter as boundary.
                if UPPER.match(char):
                    split = True
                # Detect transition from separator to not separator.
                elif NOTSEP.match(char) and SEP.match(prev_i):
                    split = True
                # Detect transition not separator to separator.
                elif SEP.match(char) and NOTSEP.match(prev_i):
                    split = True
            else:
                # The looprev_igoes one extra iteration so that it can
                # handle the remaining text after the last boundary.
                split = True

            if split:
                if NOTSEP.match(prev_i):
                    words.append(string[seq_i:curr_i])
                else:
                    # stringiable contains at least one separator.
                    # Use the first one as the stringiable's primary separator.
                    if not separator:
                        separator = string[seq_i:seq_i + 1]

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
    def parse_case(cls, string, acronyms=None, preserve_case=False):
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
            if word is not None and UPPER.match(word):
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
    def camel(cls, text, acronyms=None):
        """Return text in camelCase style.

        Args:
            text: input string to convert case
            detect_acronyms: should attempt to detect acronyms
            acronyms: a list of acronyms to detect

        >>> camelcase("hello world")
        'helloWorld'
        >>> camelcase("HELLO_HTML_WORLD", True, ["HTML"])
        'helloHTMLWorld'
        """
        words, _case, _sep = cls.parse_case(text, acronyms)
        if words:
            words[0] = words[0].lower()
        return ''.join(words)

    @alias('mixed')
    @classmethod
    def pascal(cls, text, acronyms=None):
        """Return text in PascalCase style (aka MixedCase).

        Args:
            text: input string to convert case
            detect_acronyms: should attempt to detect acronyms
            acronyms: a list of acronyms to detect

        >>> pascalcase("hello world")
        'HelloWorld'
        >>> pascalcase("HELLO_HTML_WORLD", True, ["HTML"])
        'HelloHTMLWorld'
        """
        words, _case, _sep = cls.parse_case(text, acronyms)
        return ''.join(words)

    @classmethod
    def snake(cls, text, acronyms=None):
        """Return text in snake_case style.

        Args:
            text: input string to convert case
            detect_acronyms: should attempt to detect acronyms
            acronyms: a list of acronyms to detect

        >>> snakecase("hello world")
        'hello_world'
        >>> snakecase("HelloHTMLWorld", True, ["HTML"])
        'hello_html_world'
        """
        words, _case, _sep = cls.parse_case(text, acronyms)
        return '_'.join([w.lower() for w in words])

    @alias('kebap', 'spinal', 'slug')
    @classmethod
    def dash(cls, text, acronyms=None):
        """Return text in dash-case style (aka kebab-case, spinal-case).

        Args:
            text: input string to convert case
            detect_acronyms: should attempt to detect acronyms
            acronyms: a list of acronyms to detect

        >>> dashcase("hello world")
        'hello-world'
        >>> dashcase("HelloHTMLWorld", True, ["HTML"])
        'hello-html-world'
        """
        words, _case, _sep = cls.parse_case(text, acronyms)
        return '-'.join([w.lower() for w in words])

    @alias('screaming')
    @classmethod
    def const(cls, text, acronyms=None):
        """Return text in CONST_CASE style (aka SCREAMING_SNAKE_CASE).

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
        return '_'.join([w.upper() for w in words])

    @classmethod
    def dot(cls, text, acronyms=None):
        """Return text in dot.case style.

        Args:
            text: input string to convert case
            detect_acronyms: should attempt to detect acronyms
            acronyms: a list of acronyms to detect

        >>> dotcase("hello world")
        'hello.world'
        >>> dotcase("helloHTMLWorld", True, ["HTML"])
        'hello.html.world'
        """
        words, _case, _sep = cls.parse_case(text, acronyms)
        return '.'.join([w.lower() for w in words])

    @classmethod
    def separate_words(cls, text, acronyms=None):
        """Return text in "seperate words" style.

        Args:
            text: input string to convert case
            detect_acronyms: should attempt to detect acronyms
            acronyms: a list of acronyms to detect

        >>> separate_words("HELLO_WORLD")
        'HELLO WORLD'
        >>> separate_words("helloHTMLWorld", True, ["HTML"])
        'hello HTML World'
        """
        words, _case, _sep = cls.parse_case(text, acronyms, preserve_case=True)
        return ' '.join(words)

    @classmethod
    def slash(cls, text, acronyms=None):
        """Return text in slash/case style.

        Args:
            text: input string to convert case
            detect_acronyms: should attempt to detect acronyms
            acronyms: a list of acronyms to detect

        >>> slashcase("HELLO_WORLD")
        'HELLO/WORLD'
        >>> slashcase("helloHTMLWorld", True, ["HTML"])
        'hello/HTML/World'
        """
        words, _case, _sep = cls.parse_case(text, acronyms, preserve_case=True)
        return '/'.join(words)

    @classmethod
    def backslash(cls, text, acronyms=None):
        r"""Return text in backslash\case style.

        Args:
            text: input string to convert case
            detect_acronyms: should attempt to detect acronyms
            acronyms: a list of acronyms to detect

        >>> backslashcase("HELLO_WORLD") == r'HELLO\WORLD'
        True
        >>> backslashcase("helloHTMLWorld",
            True, ["HTML"]) == r'hello\HTML\World'
        True
        """
        words, _case, _sep = cls.parse_case(text, acronyms, preserve_case=True)
        return '\\'.join(words)

    @alias('camel_snake')
    @classmethod
    def ada(cls, text, acronyms=None):
        r"""Return text in Ada_Case style."""
        words, _case, _sep = cls.parse_case(text, acronyms)
        return '_'.join([w.capitalize() for w in words])

    @classmethod
    def title(cls, text, acronyms=None):
        r"""Return text in Title_case style."""
        return cls.snake(text, acronyms).capitalize()

    @classmethod
    def lower(cls, text, acronyms=None):
        r"""Return text in lowercase style."""
        return text.lower()

    @classmethod
    def upper(cls, text, acronyms=None):
        r"""Return text in UPPERCASE style."""
        return text.upper()

    @classmethod
    def capital(cls, text, acronyms=None):
        r"""Return text in UPPERCASE style."""
        return text.capitalize()

    @classmethod
    def http_header(cls, text, acronyms=None):
        r"""Return text in Http-Header-Case style."""
        words, _case, _sep = cls.parse_case(text, acronyms)
        return '-'.join([w.capitalize() for w in words])
