import logging
from collections import namedtuple, defaultdict
from contextlib import contextmanager
from functools import reduce
from typing import List, Dict, Tuple, Set, Generator, Callable

from .lex import iter_lexemes, Lexeme, LexError, _KEYWORD
from .grammar import preprocess_grammar

logging.basicConfig()
log = logging.getLogger(__name__)
# log.setLevel(logging.DEBUG)

ParseNode = namedtuple("ParseNode", ["type", "children"])


def eof_parser(symbol, grammar, consume_lexeme, parse_symbol):
    if consume_lexeme() is None:
        log.debug(f"{eof_parser.__name__} success")
        yield ParseNode("EOF", [])
        log.debug(f"{eof_parser.__name__} exhausted {symbol}")


def keyword_parser(symbol, grammar, consume_lexeme, parse_symbol):
    literal = symbol.strip("'")
    lexeme = consume_lexeme()
    if lexeme is not None and lexeme.type == _KEYWORD and lexeme.value == literal:
        log.debug(f"{keyword_parser.__name__} success {literal}")
        yield ParseNode(_KEYWORD, [lexeme])
    log.debug(f"{keyword_parser.__name__} exhausted {symbol}")


def optional_parser(symbol, grammar, consume_lexeme, parse_symbol):
    _symbol = symbol[:-1]
    yield from parse_symbol(_symbol)
    yield ParseNode("EmptyOption", [])
    log.debug(f"{optional_parser.__name__} exhausted {symbol}")


def multi_parser(symbol, grammar, consume_lexeme, parse_symbol):
    _symbol = symbol[:-1]
    result = []
    _no_gc = []
    while True:
        _iter = parse_symbol(_symbol)
        _no_gc.append(_iter)
        try:
            result.append(next(_iter))
        except StopIteration:
            yield ParseNode(symbol, result)
            break
    for x in _no_gc:
        del x
    log.debug(f"{multi_parser.__name__} exhausted {symbol}")


def lexeme_parser(symbol, grammar, consume_lexeme, parse_symbol):
    lexeme = consume_lexeme()
    if lexeme is not None and lexeme.type == symbol or symbol.startswith("not_") and lexeme.type != symbol[4:]:
        log.debug(f"{lexeme_parser.__name__} success {symbol} {lexeme.type}")
        yield ParseNode(symbol, [lexeme])
    log.debug(f"{lexeme_parser.__name__} exhausted {symbol}")


def backtrack(symbols: List[str], parse_symbol):
    if not symbols:
        yield []
    else:
        for head in parse_symbol(symbols[0]):
            for rest in backtrack(symbols[1:], parse_symbol):
                yield [head, *rest]


def alternative_parser(symbol, grammar, consume_lexeme, parse_symbol):
    for alternative in grammar.get(symbol, []):
        for children in backtrack(alternative, parse_symbol):
            log.debug(f'{alternative_parser.__name__} success \t| {symbol} = [{" ".join(alternative)}]')
            yield ParseNode(symbol, children)
    log.debug(f"{alternative_parser.__name__} exhausted {symbol}")


def get_parser(symbol):
    if symbol == "EOF":
        return eof_parser
    elif symbol.startswith("'"):
        return keyword_parser
    elif symbol.endswith("?"):
        return optional_parser
    elif symbol.endswith("*"):
        return multi_parser
    elif symbol.islower():
        return lexeme_parser
    else:
        return alternative_parser


def parse(
    string: str,
    regex_lexemes: List[Tuple[str, str]],
    grammar: List[str],
    preprocess_lexemes=[lambda x: x],
):
    g, keywords, start_symbol = preprocess_grammar(grammar)
    unprocessed_lexemes: List[Lexeme] = list(iter_lexemes(string, keywords, regex_lexemes))
    lexemes = list(reduce(lambda x, f: f(x), preprocess_lexemes, unprocessed_lexemes))
    lexeme_index = 0
    depth = 0

    stats = {
        "attempts": defaultdict(int),
        "successes": defaultdict(int),
    }

    def consume_lexeme():
        nonlocal lexeme_index
        lexeme = lexemes[lexeme_index] if lexeme_index < len(lexemes) else None
        lexeme_index += 1
        return lexeme

    @contextmanager
    def restore_state(message: string):
        nonlocal lexeme_index, depth
        _lexeme_index = lexeme_index
        _depth = depth
        try:
            yield
        finally:
            log.debug(f"{message:40} | resetting state: {lexeme_index} -> {_lexeme_index}")
            lexeme_index = _lexeme_index
            depth = _depth

    def parse_(symbol: str):
        nonlocal depth, lexeme_index
        depth += 1
        stats["attempts"][symbol] += 1
        # log.debug(f"{' '*depth}{symbol} lexeme={lexemes[lexeme_index] if lexeme_index < len(lexemes) else 'EOF'}")
        log.debug(f"({depth:03}) {symbol:30} lexeme={lexemes[lexeme_index] if lexeme_index < len(lexemes) else 'EOF'}")

        parser = get_parser(symbol)
        with restore_state(f"{parser.__name__} ({symbol})"):
            # log.debug(f'({depth:03}) symbol: {symbol}, parser: {parser.__name__}')
            yield from parser(
                symbol,
                grammar=g,
                consume_lexeme=consume_lexeme,
                parse_symbol=parse_,
            )
        # log.debug(f'({depth:03}) symbol: {symbol}, parser: {parser.__name__} reset state {lexeme_index} -> {_lexeme_index}')

    try:
        return next(parse_(start_symbol))
    except Exception as e:
        pprint(e)
    finally:
        from pprint import pprint

        pprint(stats)
