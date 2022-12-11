import typing as T

from ast_node import AstNode
from memoized_recursive_descent_parser import MemoizedRecursiveDescentParser
from regex_lexer import RegexLexer
from util import print_node

import operator


_associative_ops = {
    "+": operator.add,
    "*": operator.mul,
}

_non_associative_ops = {
    "/": operator.truediv,
    "-": operator.sub,
}


def evaluate_expression(
    node: AstNode, get_var: T.Callable[[str], float], eval_left: T.Callable[[float], float] = lambda x: x
) -> T.Union[int, float]:
    if len(node.children) == 1:
        return evaluate_expression(node.children[0], get_var)
    elif node.name in ("AddExpr", "MulExpr"):
        op_lex = node.children[1].lexeme
        if op_lex is None:
            raise Exception("missing op")
        lhs = eval_left(evaluate_expression(node.children[0], get_var))
        if op_lex.value in _non_associative_ops:
            next_eval_left = lambda x: _non_associative_ops[op_lex.value](lhs, x)
            return evaluate_expression(node.children[0], get_var, next_eval_left)
        elif op_lex.value in _associative_ops:
            return _associative_ops[op_lex.value](lhs, evaluate_expression(node.children[2], get_var))
        else:
            raise Exception(f"bad op {op_lex.value}")
    elif node.name == "Factor":
        return evaluate_expression(node.children[1], get_var)
    elif node.lexeme is not None:
        if node.lexeme.name == "var":
            return get_var(node.lexeme.value)
        elif node.lexeme.name == "int":
            return int(node.lexeme.value)
        elif node.lexeme.name == "float":
            return float(node.lexeme.value)
        raise Exception("bad lexeme")
    else:
        raise Exception("missing op")


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
