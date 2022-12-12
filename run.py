from dataclasses import dataclass
import typing as T
from datetime import datetime
from pprint import pprint, pformat
from ast_node import AstNode
from common_types import TProduction
from grammar import Grammar
from lexeme import Lexeme
from memoized_recursive_descent_parser import MemoizedRecursiveDescentParser

from recursive_descent_parser import RecursiveDescentParser
from memoize import memoize
from regex_lexer import RegexLexer


def run(grammar: Grammar, print_lexemes: bool = False):
    print(f"    *** GRAMMAR: {grammar.name} ***")
    lexer = RegexLexer(grammar.terminals)
    for name, text in grammar.examples.items():
        lexemes = list(lexer(text))
        if print_lexemes:
            pprint(lexemes)
        parser = RecursiveDescentParser(grammar.productions)
        memoized_parser = MemoizedRecursiveDescentParser(grammar.productions)

        start_time = datetime.now()
        results = [parser.parse(lexemes, grammar.start_symbol, 0)]
        split_time = datetime.now()
        results.append(memoized_parser.parse(lexemes, grammar.start_symbol, 0))
        finish_time = datetime.now()

        print(
            f"""
    *** Text {name}***,
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
{pformat(getattr(memoized_parser._parse, "stats", None))}
"""
        )
