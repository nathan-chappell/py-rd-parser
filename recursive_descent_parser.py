import logging
import typing as T
from collections import defaultdict
from dataclasses import dataclass, field
from functools import wraps
from common_types import TProduction

from lexeme import Lexeme
from ast_node import AstNode
from parse_exception import ParseException


logging.basicConfig(level=logging.WARN)
log = logging.getLogger(__name__)

class LenParseException(ParseException):
    node: AstNode

    def __init__(self, node: AstNode, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.node = node


class RecursiveDescentParser:
    productions: T.List[TProduction]
    is_lexeme_name: T.Callable[[str], bool]
    total_calls = 0
    first_call = True

    def __init__(self, productions: T.List[TProduction], is_lexeme_name: T.Optional[T.Callable[[str], bool]] = None) -> None:
        self.productions = productions
        self.is_lexeme_name = (lambda s: s[0].islower()) if is_lexeme_name is None else is_lexeme_name
        self.reset()
    
    def reset(self):
        self.total_calls = 0
    
    def parse(self, lexemes: T.List[Lexeme], target: str, index: int) -> AstNode:
        if self.total_calls == 0:
            for i,lexeme in enumerate(lexemes):
                log.debug(f' [{i:3}] {lexeme.value}')
        self.total_calls += 1
        productions = [production for head, production in self.productions if head == target]
        log.info(f"parse({target}, {index}, {lexemes[index]})")
        for production in productions:
            children: T.List[AstNode] = []
            _start = index
            try:
                for symbol in production.split():
                    if index >= len(lexemes):
                        raise ParseException()
                    elif self.is_lexeme_name(symbol) and lexemes[index] == symbol:
                        log.debug(f"  _LEXX {symbol} ({index})")
                        children.append(AstNode(symbol, [], lexemes[index], index, index + 1, lexemes))
                        index += 1
                    elif not self.is_lexeme_name(symbol):
                        children.append(self.parse(lexemes=lexemes, target=symbol, index=index))
                        index = children[-1].end
                    elif symbol == "":
                        continue
                    else:
                        log.debug(f"  _FAIL [sym:{index}] {target} ({production})")
                        raise ParseException()
                log.debug(f"--_SUCC {target} ({production})")
                return AstNode(target, children, None, _start, children[-1].end, lexemes)
            except ParseException:
                log.debug(f"  _FAIL [pro:{index}] {target} ({production})")
                children = []
                index = _start
        else:
            raise ParseException()
