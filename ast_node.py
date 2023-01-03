import typing as T
from dataclasses import dataclass

from lexeme import Lexeme


@dataclass
class AstNode:
    name: str
    children: T.List["AstNode"]  # I'm a tree!
    lexeme: T.Optional[Lexeme]
    # NOTE: Open interval [start, end)
    start: int
    end: int
    lexemes: T.List[Lexeme]

    @property
    def value(self) -> str:
        return " ".join([l.value for l in self.lexemes[self.start : self.end]])

    def matches_production(self, head: str, body: str) -> bool:
        split_body = body.split()
        return (
            head == self.name
            and len(self.children) == len(split_body)
            and all(
                [
                    child.name == symbol
                    for child, symbol in zip(self.children, body.split())
                ]
            )
        )
    
    def matches_productions(self, productions: T.List[T.Tuple[str,str]]) -> bool:
        return any(self.matches_production(head, body) for head,body in productions)
