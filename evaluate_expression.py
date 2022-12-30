import typing as T

from ast_node import AstNode
from memoized_recursive_descent_parser import MemoizedRecursiveDescentParser
from regex_lexer import RegexLexer
from util import print_node

import logging
import operator

logging.basicConfig
log = logging.getLogger(__name__)

_associative_ops = {
    "+": operator.add,
    "*": operator.mul,
}

def _sub_op(l,r):
    log.debug(f'[_sub_op] {l} - {r} = {l - r}')
    return l - r

_non_associative_ops = {
    "/": operator.truediv,
    # "-": operator.sub,
    "-": _sub_op,
}


def evaluate_expression(
    node: AstNode,
    get_var: T.Callable[[str], float],
    eval_left: T.Callable[[float], float] = lambda x: x,
    node_handler: T.Optional[T.Callable[[AstNode], T.Union[int, float]]] = None,
) -> T.Union[int, float]:
    if len(node.children) == 1:
        return eval_left(evaluate_expression(node.children[0], get_var, node_handler=node_handler))
    elif node.name in ("AddExpr", "MulExpr"):
        op_lex = node.children[1].lexeme
        if op_lex is None:
            raise Exception("missing op")
        lhs = eval_left(evaluate_expression(node.children[0], get_var, node_handler=node_handler))
        if op_lex.value in _non_associative_ops:
            next_eval_left = lambda x: _non_associative_ops[op_lex.value](lhs, x)
            rhs = '??'
            result = evaluate_expression(node.children[2], get_var, next_eval_left, node_handler=node_handler)
        elif op_lex.value in _associative_ops:
            rhs = evaluate_expression(node.children[2], get_var, node_handler=node_handler)
            result = _associative_ops[op_lex.value](lhs, rhs)
        else:
            raise Exception(f"bad op {op_lex.value}")
        log.debug(f'[expr] {node.value} = {lhs} {op_lex.value} {rhs} = {result}')
        return result
    elif node.name == "Factor":
        return eval_left(evaluate_expression(node.children[1], get_var, node_handler=node_handler))
    elif node.lexeme is not None:
        if node.lexeme.name in ("var", "identifier"):
            return get_var(node.lexeme.value)
        elif node.lexeme.name == "int":
            return int(node.lexeme.value)
        elif node.lexeme.name == "float":
            return float(node.lexeme.value)
        raise Exception("bad lexeme")
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
evaluate_expression: {evaluate_expression(node, lambda name: values[name])}
eval_python:         {eval(' '.join(expression.split()), values)}
"""
        )

    _test_evaluate("x * y + z", {"x": 0, "y": 1, "z": 2})
    _test_evaluate("x - y + z", {"x": 1, "y": 1, "z": 1})
