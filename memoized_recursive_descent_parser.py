import typing as T
from ast_node import AstNode

from common_types import TProduction
from lexeme import Lexeme
from recursive_descent_parser import RecursiveDescentParser
from memoize import memoize


class MemoizedRecursiveDescentParser(RecursiveDescentParser):
    def __init__(self, productions: T.List[TProduction], is_lexeme_name: T.Optional[T.Callable[[str], bool]] = None) -> None:
        super().__init__(productions, is_lexeme_name)
        # self._parse = memoize(lambda lexemes, target, index: (target, index))(self.parse)
        self._parse = memoize(lambda self, lexemes, target, index: (target, index))(RecursiveDescentParser.parse)
    
    def parse(self, lexemes: T.List[Lexeme], target: str, index: int) -> AstNode:
        return self._parse(self, lexemes, target, index)
