import logging
from collections import namedtuple, defaultdict
from functools import reduce
from typing import List, Dict, Tuple, Set

from .lex import iter_lexemes, Lexeme, LexError, _KEYWORD
from .grammar import preprocess_grammar

logging.basicConfig()
log = logging.getLogger(__name__)
# log.setLevel(logging.DEBUG)

ParseNode = namedtuple("ParseNode", ["type", "children"])


class ParseError(Exception):
    def __init__(self, symbol, start, depth, *args, lexeme=None, child_errors=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.symbol = symbol
        self.start = start
        self.depth = depth
        self.lexeme = lexeme
        self.child_errors = child_errors

    def __str__(self):
        m = super().__str__()
        m_start = (
            f"({self.depth:3})" + "  " * (min(40, self.depth)) + f"({self.start:3}) {self.symbol}"
        )
        # return f'{m} - at {self.start}: {self.lexeme}'
        if not self.child_errors:
            return f"{m_start} {self.lexeme} | error: {m}"
        else:
            return f"{m_start} -> {m}\n" + "\n".join([str(child) for child in self.child_errors])


class RecoverableParseError(ParseError):
    pass


class OptionalParseFailure(RecoverableParseError):
    pass


def parse(
    string: str,
    regex_lexemes: List[Tuple[str, str]],
    grammar: List[str],
    preprocess_lexemes=[lambda x: x],
):
    g, keywords, start_symbol = preprocess_grammar(grammar)
    unprocessed_lexemes: List[Lexeme] = list(iter_lexemes(string, keywords, regex_lexemes))
    lexemes = reduce(lambda x, f: f(x), preprocess_lexemes, unprocessed_lexemes)
    lexeme_index = 0
    depth = 0

    stats = {
        "attempts": defaultdict(int),
        "successes": defaultdict(int),
    }

    def next_lexeme():
        nonlocal lexeme_index
        # while lexeme_index < len(lexemes) and lexemes[lexeme_index].type in skip_lexemes:
        #     lexeme_index += 1
        return lexemes[lexeme_index] if lexeme_index < len(lexemes) else None

    def parse_(symbol: str):
        nonlocal lexeme_index, depth
        depth += 1
        stats["attempts"][symbol] += 1
        try:
            lexeme = next_lexeme()
            # log.debug(f"trying parse_\t({symbol}) at (depth={depth:03}, lexeme_index={lexeme_index:03}, lexeme={lexeme})")
            log.debug(f"{' '*depth}{symbol} lexeme={lexeme}")

            def _make_error(
                *args, cls=RecoverableParseError, lexeme=None, child_errors=None, **kwargs
            ):
                assert args or lexeme or child_errors
                return cls(
                    symbol,
                    lexeme_index,
                    depth,
                    *args,
                    **kwargs,
                    lexeme=lexeme,
                    child_errors=child_errors,
                )

            if symbol == "EOF":
                if lexeme == None:
                    result = ParseNode("EOF", [])
                else:
                    raise _make_error(lexeme=lexeme)
            elif lexeme_index >= len(lexemes):
                raise _make_error(f"Out of bounds.")
            elif symbol == "Any":
                if lexeme is not None:
                    lexeme_index += 1
                    result = ParseNode("Any", [lexeme])
                else:
                    raise _make_error(lexeme=lexeme)
            elif symbol.startswith("'"):
                literal = symbol.strip("'")
                if literal in keywords and lexeme.type == _KEYWORD and lexeme.value == literal:
                    lexeme_index += 1
                    result = ParseNode(_KEYWORD, [lexeme])
                else:
                    raise _make_error(lexeme=lexeme)
            elif symbol.endswith("?"):
                _symbol = symbol[:-1]
                _index = lexeme_index
                try:
                    result = parse_(_symbol)
                except RecoverableParseError:
                    lexeme_index = _index
                    raise _make_error(cls=OptionalParseFailure, lexeme=lexeme)
            elif symbol.endswith("*"):
                _symbol = symbol[:-1]
                multi_matches = []
                while True:
                    _index = lexeme_index
                    try:
                        multi_matches.append(parse_(_symbol))
                    except RecoverableParseError:
                        lexeme_index = _index
                        # log.debug(f'multi finished at lexeme_index {lexeme_index}')
                        break
                result = ParseNode(symbol, multi_matches)
            elif symbol.islower():
                if lexeme.type == symbol or symbol.startswith("not_") and lexeme.type != symbol[4:]:
                    lexeme_index += 1
                    result = ParseNode(symbol, [lexeme])
                else:
                    raise _make_error(lexeme=lexeme)
            else:
                if symbol not in g:
                    raise _make_error(f"Invalid symbol.", cls=ParseError)
                errors = []
                for alternative in g[symbol]:
                    _i = lexeme_index
                    children = []
                    try:
                        for _symbol in alternative:
                            try:
                                children.append(parse_(_symbol))
                            except OptionalParseFailure:
                                pass
                        result = ParseNode(symbol, children)
                        break
                    except RecoverableParseError as e:
                        if lexeme.word_info.line > 128:
                            pass
                        # log.debug(e)
                        errors.append(e)
                        lexeme_index = _i
                        continue
                else:
                    raise _make_error(child_errors=errors)

            # log.debug(f"parse_\t({symbol}) at (depth={depth:03}, lexeme_index={lexeme_index:03}) success")
            stats["successes"][symbol] += 1
            log.debug(f"{' '*depth}{symbol} success")
            return result
        finally:
            depth -= 1

    try:
        return parse_(start_symbol)
    finally:
        from pprint import pprint

        pprint(stats)
