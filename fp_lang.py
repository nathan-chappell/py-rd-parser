import typing as T
import logging
from dataclasses import dataclass
from pprint import pprint

from ast_node import AstNode
from evaluate_expression import evaluate_expression
from grammars import fp_language_grammar
from lexeme import Lexeme
from memoized_recursive_descent_parser import MemoizedRecursiveDescentParser
from recursive_descent_parser import RecursiveDescentParser, log as rd_log
from regex_lexer import RegexLexer

logging.basicConfig(level=logging.WARN)
log = logging.getLogger(__name__)

EvalResult = T.Any


class FpScope:
    def __init__(self, parent: T.Optional["FpScope"] = None):
        self.parent = parent
        self.expressions: T.Dict[str, EvalResult] = {}

    def get(self, name: str) -> EvalResult:
        if name in self.expressions:
            return self.expressions[name]
        elif self.parent is not None:
            return self.parent.get(name)
        else:
            raise KeyError(f"{name} not found in any parent scope")


def evaluate_fp_program(root_node: AstNode):
    global_scope = FpScope()

    passthrough_productions = (
        "Expression",
        "SubExpression",
        "FunctionIdentifier",
        "Args",
    )

    def eval_node(node: AstNode, current_scope: FpScope):
        log.debug(f"[eval_node] {node.name} {node.value}")
        if node.name == "Program":
            if len(node.children) == 1:
                return eval_node(node.children[0], current_scope)
            else:
                eval_node(node.children[0], current_scope)
                return eval_node(node.children[1], current_scope)

        elif node.name in passthrough_productions:
            return eval_node(node.children[0], current_scope)
        
        elif node.name in "BracedExpression":
            return eval_node(node.children[1], current_scope)

        elif node.name == "Statements":
            eval_node(node.children[0], current_scope)
            if len(node.children) > 1:
                eval_node(node.children[1], current_scope)
            return

        elif node.name == "Statement":
            identifier = T.cast(Lexeme, node.children[1].lexeme).value
            current_scope.expressions[identifier] = eval_node(node.children[3], current_scope)
            return

        elif node.name == "Abstraction":

            def f(x):
                variable_name = T.cast(Lexeme, node.children[0].lexeme).value
                inner_scope = FpScope(current_scope)
                inner_scope.expressions[variable_name] = x
                return eval_node(node.children[2], inner_scope)

            return f

        elif node.name == "Application":
            _fn = eval_node(node.children[0], current_scope)
            if not callable(_fn):
                raise Exception(f"[Application] subexpression was not callable: {node}")
            else:
                return _fn(eval_node(node.children[1], current_scope))

        elif node.name == "ComparisonExpression":
            _op = T.cast(Lexeme, node.children[1].lexeme).value
            _l = eval_node(node.children[0], current_scope)
            _r = eval_node(node.children[2], current_scope)
            if _op == "<":
                return _l < _r
            if _op == "<=":
                return _l <= _r
            if _op == "==":
                return _l == _r
            if _op == "!=":
                return _l != _r
            if _op == ">=":
                return _l >= _r
            if _op == ">":
                return _l > _r
            raise Exception(f"[ComparisonExpression] unhandled node: {node}")

        elif node.name == "IfElseExpression":
            _comparison_result = eval_node(node.children[2], current_scope)
            if not isinstance(_comparison_result, bool):
                raise Exception(f"[IfElseExpression] invalid comparison result: {_comparison_result}")
            if _comparison_result:
                return eval_node(node.children[4], current_scope)
            else:
                return eval_node(node.children[6], current_scope)

        elif node.name == "AddExpr":

            def get_var(name: str) -> T.Union[int, float]:
                scope_value = current_scope.get(name)
                if isinstance(scope_value, (int, float)):
                    return scope_value
                value = eval_node(scope_value, current_scope)
                if isinstance(value, (int, float)):
                    return value
                else:
                    raise Exception(f"could not evaluate {name}")

            def handle_node(ast_node: AstNode) -> T.Union[int, float]:
                result = "_NONE"
                if ast_node.name == "Application":
                    result = eval_node(ast_node, current_scope)
                    if isinstance(result, (int, float)):
                        return result
                raise Exception(f"could not handle {ast_node.value}: {result}")

            return evaluate_expression(
                node,
                get_var=get_var,
                node_handler=handle_node,
            )

        elif node.name == "identifier":
            return current_scope.get(T.cast(Lexeme, node.lexeme).value)

        else:
            raise Exception(f"[eval_node] unhandled node: {node.name}")

    return eval_node(root_node, global_scope)


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument("-v_rd", action="store_true")
    parser.add_argument("-v_eval", action="store_true")
    pprint(sys.argv[1:])
    args = parser.parse_args(sys.argv[1:])
    if args.v_rd:
        rd_log.setLevel(logging.DEBUG)
    if args.v_eval:
        log.setLevel(logging.DEBUG)

    lexer = RegexLexer(fp_language_grammar.terminals)

    include_examples = ["higher-order-fns"]

    for name, text in fp_language_grammar.examples.items():
        if name not in include_examples:
            continue
        lexemes = list(lexer(text))
        memoized_parser = MemoizedRecursiveDescentParser(fp_language_grammar.productions)
        root_node = memoized_parser.parse(lexemes, fp_language_grammar.start_symbol, 0)
        result = evaluate_fp_program(root_node)
        # pprint(root_node)
        from util import print_node

        # print_node(root_node)
        print(f"{name}: {text}")
        pprint(result)
