import typing as T

from ast_node import AstNode
from memoized_recursive_descent_parser import MemoizedRecursiveDescentParser
from regex_lexer import RegexLexer

import operator


_ops = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
}


def evaluate_expression(node: AstNode, get_var: T.Callable[[str], float]) -> T.Union[int, float]:
    if len(node.children) == 1:
        return evaluate_expression(node.children[0], get_var)
    elif node.name in ("AddExpr", "MulExpr"):
        op_lex = node.children[1].lexeme
        if op_lex is None:
            raise Exception("missing op")
        return _ops[op_lex.value](evaluate_expression(node.children[0], get_var), evaluate_expression(node.children[2], get_var))
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

    lexer = RegexLexer(expression_grammar.terminals)
    memoized_parser = MemoizedRecursiveDescentParser(expression_grammar.productions)

    def _test_evaluate(expression: str, values: T.Dict[str, float]):
        lexemes = list(lexer(expression))
        node = memoized_parser.parse(lexemes, expression_grammar.start_symbol, 0)
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
