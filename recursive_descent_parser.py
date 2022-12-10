import logging
import typing as T
from collections import defaultdict
from dataclasses import dataclass, field
from functools import wraps

from lexeme import Lexeme
from ast_node import AstNode
from parse_exception import ParseException


logging.basicConfig(level=logging.WARN)
log = logging.getLogger(__name__)

THead = str
TProduction = str
TRule = T.Tuple[THead, TProduction]


class RecursiveDescentParser:
    grammar: T.List[TRule]
    is_lexeme_name: T.Callable[[str], bool] = lambda s: s[0].islower()

    def __init__(self, grammar: T.List[TRule], is_lexeme_name: T.Optional[T.Callable[[str], bool]] = None) -> None:
        self.grammar = grammar
        if is_lexeme_name is not None:
            self.is_lexeme_name = is_lexeme_name

    def parse(self, lexemes: T.List[Lexeme], target: str, index: int = 0) -> AstNode:
        productions = [production for head, production in self.grammar if head == target]
        log.info(f"parse({target}, {index})")
        for production in productions:
            children: T.List[AstNode] = []
            _start = index
            try:
                for symbol in production.split():
                    if index >= len(lexemes):
                        raise ParseException()
                    elif self.is_lexeme_name(symbol) and lexemes[index] == symbol:
                        log.debug(f"  _LEXX {symbol} ({index})")
                        children.append(AstNode(symbol, [], lexemes[index], index, index + 1))
                        index += 1
                    elif not self.is_lexeme_name(symbol):
                        children.append(self.parse(lexemes=lexemes, target=symbol, index=index))
                        index = children[-1].end
                    elif symbol == "":
                        continue
                    else:
                        raise ParseException()
                log.debug(f"  _SUCC {target} ({production})")
                return AstNode(target, children, None, _start, children[-1].end)
            except ParseException:
                log.debug(f"  _FAIL {target} ({production})")
                children = []
                index = _start
        else:
            raise ParseException()
