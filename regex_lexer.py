import typing as T
import re

from lexeme import Lexeme
from lexer_exception import LexerException


class RegexLexer:
    matchers: T.List[T.Tuple[str, re.Pattern[str]]]

    def __init__(self, name_pattern_pairs: T.List[T.Tuple[str, str]]):
        self.matchers = [(name, re.compile(pattern)) for name, pattern in name_pattern_pairs]

    def __call__(self, text: str) -> T.Generator[Lexeme, None, None]:
        i = 0
        line = 0
        column = 0

        def update_position(matched: str):
            nonlocal line, column
            if "\n" not in matched:
                column += len(matched)
            else:
                lines = matched.split("\n")
                line += len(lines) - 1
                column = len(lines[-1])

        text_length = len(text)
        while i < text_length:
            for name, matcher in self.matchers:
                match = matcher.match(text, i)
                if match is not None:
                    matched = match[0]
                    matched_length = len(matched)
                    yield Lexeme(name, matched, i, i + matched_length, line, column)
                    update_position(matched)
                    i += matched_length
                    break
            else:
                raise LexerException(f"failed at ({i}, line {line}, column {column}) {text[i:20]}")


if __name__ == "__main__":
    lexer = RegexLexer([("ws", r"\s+"), ("int", r"\d+"), ("word", r"\w+")])
    from pprint import pprint

    pprint(list(lexer("This is 1 example")))
