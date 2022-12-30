import typing as T
from dataclasses import dataclass

from lexeme import Lexeme


@dataclass
class AstNode:
    name: str
    children: T.List['AstNode'] # I'm a tree!
    lexeme: T.Optional[Lexeme]
    # NOTE: Open interval [start, end)
    start: int
    end: int
    lexemes: T.List[Lexeme]

    @property
    def value(self) -> str:
        return ' '.join([l.value for l in self.lexemes[self.start:self.end]])
