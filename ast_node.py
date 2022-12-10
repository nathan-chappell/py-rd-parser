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
