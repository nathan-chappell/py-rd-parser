from dataclasses import dataclass
import typing as T


@dataclass
class Lexeme:
    """Comparable to str (value)"""

    name: str
    value: str
    start: int
    end: int
    line: T.Optional[int] = None
    column: T.Optional[int] = None

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Lexeme):
            return all(
                [
                    o.name == self.name,
                    o.value == self.value,
                    o.start == self.start,
                ]
            )
        elif isinstance(o, str):
            return o == self.name
        else:
            return super().__eq__(self, o)
