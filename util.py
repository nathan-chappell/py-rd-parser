import typing as T

from ast_node import AstNode


def print_result(match: AstNode):
    def yield_lines(_match: AstNode, depth=0) -> T.Generator[T.Tuple[int, str], None, None]:
        """Get (depth, match-string) tuples recursively"""
        yield (depth, f"{_match.name} [{_match.start}, {_match.end})")
        for _match in _match.children:
            if isinstance(_match, str):
                yield (depth + 1, f"{_match.name}")
            else:
                yield from yield_lines(_match, depth + 1)

    for depth, line in yield_lines(match):
        print("  " * depth + line)
