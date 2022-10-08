import logging
from collections import namedtuple
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
        m_start = "  " * self.depth + f"({self.start:3}) {self.symbol}"
        # return f'{m} - at {self.start}: {self.lexeme}'
        if not self.child_errors:
            return f"{m_start} {self.lexeme} | error: {m}"
        else:
            return f"{m_start} -> {m}\n" + "\n".join([str(child) for child in self.child_errors])


def parse(string: str, regex_lexemes: List[Tuple[str, str]], grammar: List[str], skip_lexemes=[]):
    g, keywords, start_symbol = preprocess_grammar(grammar)
    lexemes: List[Lexeme] = list(iter_lexemes(string, keywords, regex_lexemes))
    i = 0
    depth = 0

    def next_lexeme():
        nonlocal i
        while lexemes[i].type in skip_lexemes:
            i += 1
        return lexemes[i]

    def parse_(symbol: str):
        nonlocal i, depth
        depth += 1
        try:
            lexeme = next_lexeme()
            mstart = f"parse_\t({symbol})"
            br1 = " " * (20 - len(mstart))
            br2 = " " * (40 - len(f"{mstart}{br1}"))
            log.debug(f"{mstart}{br1}at {i}:{br2}{lexeme}")

            if symbol == "EOF":
                if i == len(lexemes):
                    return ParseNode("EOF", [])
                else:
                    raise ParseError(symbol, i, depth, lexeme=lexeme)

            if i >= len(lexemes):
                raise ParseError(symbol, i, depth, f"Out of bounds.")

            if symbol.startswith("'"):
                literal = symbol.strip("'")
                if literal in keywords and lexeme.type == _KEYWORD and lexeme.value == literal:
                    i += 1
                    result = ParseNode(_KEYWORD, [lexeme])
                else:
                    raise ParseError(symbol, i, depth, lexeme=lexeme)
            elif symbol.islower():
                if lexeme.type == symbol:
                    i += 1
                    result = ParseNode(symbol, [lexeme])
                else:
                    raise ParseError(symbol, i, depth, lexeme=lexeme)
            else:
                if symbol not in g:
                    raise ParseError(symbol, i, depth, f"Invalid symbol.")
                errors = []
                for alternative in g[symbol]:
                    _i = i
                    children = []
                    try:
                        for _symbol in alternative:
                            children.append(parse_(_symbol))
                        result = ParseNode(symbol, children)
                        break
                    except ParseError as e:
                        log.debug(e)
                        errors.append(e)
                        i = _i
                else:
                    raise ParseError(symbol, i, depth, child_errors=errors)

            log.debug(f"{mstart}{br1}at {i}: success")
            return result
        finally:
            depth -= 1

    return parse_(start_symbol)
