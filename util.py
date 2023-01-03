import typing as T

from ast_node import AstNode


def print_node(node: AstNode):
    def yield_lines(_node: AstNode, depth=0) -> T.Generator[T.Tuple[int, str], None, None]:
        """Get (depth, match-string) tuples recursively"""
        yield (depth, f"{_node.name} [{_node.start}, {_node.end} {_node.value})")
        for child in _node.children:
            if child.lexeme is not None:
                yield (depth + 1, f"{child.name} {child.value}")
            else:
                yield from yield_lines(child, depth + 1)

    for depth, line in yield_lines(node):
        print(" " * depth + line)


