import typing as T
from dataclasses import dataclass

from common_types import NamedTerminal, THead, TRule


@dataclass
class Grammar:
    name: str
    terminals: T.List[NamedTerminal]
    productions: T.List[TRule]
    start_symbol: THead
    examples: T.Dict[str, str]