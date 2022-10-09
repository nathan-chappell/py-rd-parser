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


WordInfo = namedtuple("WordInfo", ["start", "line", "column"])


def iter_words2(string: str):
    """Very inefficient."""
    start: int = 0
    line: int = 1
    column: int = 0
    while start < len(string):
        match_length: int = yield string[start:], WordInfo(start, line, column)
        _match = string[start : start + match_length]
        start += match_length
        line += _match.count("\n")
        if '\n' in _match:
            column = match_length - (_match.rfind("\n") + 1)
        else:
            column += match_length


Lexeme = namedtuple("Lexeme", ["type", "value", "word_info"])
_KEYWORD = "keyword"


class LexError(Exception):
    def __init__(self, word_info, word, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.word_info = word_info
        self.word = word


def iter_lexemes(string: str, keywords: List[str], regex_lexemes: List[str], word_re=r"[^ \t]+"):
    # generator = iter_words(string, word_re)
    generator = iter_words2(string)
    match_length = None
    _regexes = [(name, re.compile(regex)) for name, regex in regex_lexemes]

    try:
        while True:
            word, word_info = generator.send(match_length)
            for kw in keywords:
                if word.startswith(kw):
                    match_length = len(kw)
                    yield Lexeme(_KEYWORD, kw, word_info)
                    break
            else:
                for name, regex in _regexes:
                    m = regex.match(word)
                    if m:
                        match_length = m.end() - m.start()
                        yield Lexeme(name, m.group(0), word_info)
                        break
                else:
                    raise LexError(word_info, word)
    except StopIteration:
        pass
