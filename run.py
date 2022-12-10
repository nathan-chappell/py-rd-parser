from dataclasses import dataclass
import typing as T
from datetime import datetime
from pprint import pprint, pformat
from ast_node import AstNode
from lexeme import Lexeme

from recursive_descent_parser import RecursiveDescentParser, TRule
from memoize import memoize
from regex_lexer import RegexLexer


class MemoizedRecursiveDescentParser(RecursiveDescentParser):
    def __init__(self, grammar: T.List[TRule], is_lexeme_name: T.Optional[T.Callable[[str], bool]] = None) -> None:
        super().__init__(grammar, is_lexeme_name)
        self.parse = memoize(lambda lexemes, target, index: (target, index))(self.parse)


def run(
    name_pattern_pairs: T.List[T.Tuple[str, str]],
    grammar: T.List[TRule],
    target: str,
    texts: T.List[str],
):
    lexer = RegexLexer(name_pattern_pairs)
    for text in texts:
        lexemes = list(lexer(text))
        pprint(lexemes)
        parser = RecursiveDescentParser(grammar)
        memoized_parser = MemoizedRecursiveDescentParser(grammar)

        start_time = datetime.now()
        results = [parser.parse(lexemes, target, 0)]
        split_time = datetime.now()
        results.append(memoized_parser.parse(lexemes, target, 0))
        finish_time = datetime.now()

        print(
            f"""
    *** Text ***,
{text}
lexemes:     {len(lexemes)}
    *** Parser ***,
total_calls: {parser.total_calls}
time:        {split_time - start_time}
span:        {results[0].start}, {results[0].end}
    *** Memoized Parser ***
total_calls: {memoized_parser.total_calls}
time:        {finish_time - split_time}
span:        {results[1].start}, {results[1].end}
stats:
{pformat(getattr(memoized_parser.parse, "stats"))}
"""
        )
