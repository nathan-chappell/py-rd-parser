import typing as T

from ast_node import AstNode
from lexeme import Lexeme
from memoized_recursive_descent_parser import MemoizedRecursiveDescentParser
from regex_lexer import RegexLexer
from util import print_node

import logging
import operator

logging.basicConfig
log = logging.getLogger(__name__)

_op_table = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
}

OperandList = T.List[T.Tuple[AstNode, T.Optional[str]]]


def get_operand_sequence(node: AstNode) -> OperandList:
    """Get the longest contiguous sequence of operands of operators of the same precedence"""
    if node.matches_productions(
        [("MulExpr", "Factor mul_op MulExpr"), ("AddExpr", "MulExpr add_op AddExpr")],
    ):
        operand = (node.children[0], T.cast(Lexeme, node.children[1].lexeme).value)
        return [operand, *get_operand_sequence(node.children[2])]
    elif node.matches_productions([("MulExpr", "Factor"), ("AddExpr", "MulExpr")]):
        return [(node, None)]
    else:
        return []


def _default_handler(node: AstNode):
    raise Exception(f"[evaluate_expression] failed to handle node: {node}")


def evaluate_expression(
    node: AstNode,
    node_handler: T.Callable[[AstNode], T.Union[int, float]] = _default_handler,
) -> T.Union[int, float]:
    if len(node.children) == 1:
        return evaluate_expression(node.children[0], node_handler=node_handler)
    elif node.name in ("AddExpr", "MulExpr"):
        # we handle left-associativity here...
        operand_sequence = get_operand_sequence(node)
        acc = evaluate_expression(operand_sequence[0][0], node_handler=node_handler)
        op = operand_sequence[0][1]
        for operand, next_op in operand_sequence[1:]:
            if op is None:
                raise RuntimeError(f"No op provided for {operand.value} at {node.value}")
            rhs = evaluate_expression(operand, node_handler=node_handler)
            acc = _op_table[op](acc, rhs)
            op = next_op
        return acc
    elif node.matches_production("Factor", "lbrace AddExpr rbrace"):
        return evaluate_expression(node.children[1], node_handler=node_handler)
    elif node.lexeme is not None:
        if node.lexeme.name == "int":
            return int(node.lexeme.value)
        elif node.lexeme.name == "float":
            return float(node.lexeme.value)
        else:
            return node_handler(node)
    elif node_handler is not None:
        return node_handler(node)
    else:
        raise Exception(f"[evaluate_expression] failed to handle node: {node}")


if __name__ == "__main__":
    from pprint import pformat
    from grammars import expression_grammar

    def _test_evaluate(expression: str, values: T.Dict[str, float]):
        lexer = RegexLexer(expression_grammar.terminals)
        memoized_parser = MemoizedRecursiveDescentParser(expression_grammar.productions)
        lexemes = list(lexer(expression))
        node = memoized_parser.parse(lexemes, expression_grammar.start_symbol, 0)

        print_node(node)
        print(
            f"""
    *** Expression ***
{expression}
    *** Values ***
{pformat(values)}
    *** Results ***
evaluate_expression: {evaluate_expression(node, lambda node: values[T.cast(Lexeme, node.lexeme).value])}
eval_python:         {eval(' '.join(expression.split()), values)}
"""
        )

    _test_evaluate("x * y + z", {"x": 0, "y": 1, "z": 2})
    _test_evaluate("x - y", {"x": 1, "y": 1, "z": 1})
    _test_evaluate("x - y + z", {"x": 1, "y": 1, "z": 1})
