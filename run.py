import typing as T
from dataclasses import dataclass
from datetime import datetime, timedelta
from pprint import pprint, pformat
from ast_node import AstNode
from common_types import TProduction
from grammar import Grammar
from html_element import HtmlElement
from lexeme import Lexeme
from memoized_recursive_descent_parser import MemoizedRecursiveDescentParser

from recursive_descent_parser import RecursiveDescentParser
from memoize import memoize
from regex_lexer import RegexLexer

TParserType = T.Literal["normal", "memoized"]

def _format(item: T.Any) -> str:
    if isinstance(item, timedelta):
        return f'{item.microseconds:9}'
    else:
        return str(item)



@dataclass
class RunStats:
    grammar_name: str
    lexeme_count: int
    parser_type: TParserType
    result: AstNode
    span: T.Tuple[int, int]
    example_name: str
    example: str
    timedelta: timedelta
    total_calls: int

    cache_hits: T.Optional[int] = None
    cache_misses: T.Optional[int] = None

    _table_fields = [
        "example_name",
        "example",
        "parser_type",
        "total_calls",
        "timedelta",
        "lexeme_count",
        "cache_misses",
        "cache_hits",
    ]

    def to_tr(self) -> HtmlElement:
        return HtmlElement(
            "tr",
            children=[
                HtmlElement(
                    "td",
                    children=str(getattr(self, _field)),
                )
                for _field in self._table_fields
            ],
        )

    @classmethod
    def make_table(cls, run_stats: T.Iterable["RunStats"]) -> HtmlElement:
        return HtmlElement(
            "table",
            children=[
                HtmlElement(
                    "thead",
                    children=[
                        HtmlElement(
                            "tr",
                            children=[HtmlElement("th", children=_field_name) for _field_name in cls._table_fields],
                        )
                    ],
                ),
                HtmlElement(
                    "tbody",
                    children=[
                        HtmlElement(
                            "tr",
                            children=[
                                HtmlElement("td", children=_format(getattr(stats, _field_name)))
                                for _field_name in cls._table_fields
                            ],
                        )
                        for stats in run_stats
                    ],
                ),
            ],
        )


def run(grammar: Grammar, example_name: str, parser_type: TParserType = "normal") -> RunStats:
    lexer = RegexLexer(grammar.terminals)
    # for name, text in grammar.examples.items():
    example = grammar.examples[example_name]
    lexemes = list(lexer(example))
    if parser_type == "memoized":
        parser = MemoizedRecursiveDescentParser(grammar.productions)
    else:
        parser = RecursiveDescentParser(grammar.productions)

    start_time = datetime.now()
    result = parser.parse(lexemes, grammar.start_symbol, 0)
    finish_time = datetime.now()

    if parser_type == "memoized":
        _stats: T.Dict[str, int] = getattr(getattr(parser, "_parse"), "stats")
        cache_hits = _stats["cache_hits"]
        cache_misses = _stats["cache_misses"]
    else:
        cache_hits = None
        cache_misses = None

    return RunStats(
        example_name=example_name,
        example=example,
        grammar_name=grammar.name,
        lexeme_count=len(lexemes),
        parser_type=parser_type,
        result=result,
        span=(result.start, result.end),
        timedelta=finish_time - start_time,
        total_calls=parser.total_calls,
        cache_hits=cache_hits,
        cache_misses=cache_misses,
    )
    # split_time = datetime.now()
    # results.append(memoized_parser.parse(lexemes, grammar.start_symbol, 0))


#         print(
#             f"""
#     *** Text {name}***,
# {text}
# lexemes:     {len(lexemes)}
#     *** Parser ***,
# total_calls: {parser.total_calls}
# time:        {split_time - start_time}
# span:        {results[0].start}, {results[0].end}
#     *** Memoized Parser ***
# total_calls: {memoized_parser.total_calls}
# time:        {finish_time - split_time}
# span:        {results[1].start}, {results[1].end}
# stats:
# {pformat(getattr(memoized_parser._parse, "stats", None))}
# """
#         )
