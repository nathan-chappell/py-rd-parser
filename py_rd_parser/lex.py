import re
from collections import namedtuple
from typing import List


def iter_words(string: str, split=r"[^ \t]+"):
    """Doesn't work for sqstring.  Use iter_words2."""
    for match in re.finditer(split, string):
        chunk = match.group(0)
        i: int = 0
        while i < len(chunk):
            match_length: int = yield chunk[i:], i + match.start()
            i += match_length


def iter_words2(string: str):
    """Very inefficient."""
    i: int = 0
    while i < len(string):
        match_length: int = yield string[i:], i
        i += match_length


Lexeme = namedtuple("Lexeme", ["type", "value", "start"])
_KEYWORD = "keyword"


class LexError(Exception):
    def __init__(self, start, word, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start = start
        self.word = word


def iter_lexemes(string: str, keywords: List[str], regex_lexemes: List[str], word_re=r"[^ \t]+"):
    # generator = iter_words(string, word_re)
    generator = iter_words2(string)
    match_length = None
    _regexes = [(name, re.compile(regex)) for name, regex in regex_lexemes]

    try:
        while True:
            word, start = generator.send(match_length)
            for kw in keywords:
                if word.startswith(kw):
                    match_length = len(kw)
                    yield Lexeme(_KEYWORD, kw, start)
                    break
            else:
                for name, regex in _regexes:
                    m = regex.match(word)
                    if m:
                        match_length = m.end() - m.start()
                        yield Lexeme(name, m.group(0), start)
                        break
                else:
                    raise LexError(start, word)
    except StopIteration:
        pass
