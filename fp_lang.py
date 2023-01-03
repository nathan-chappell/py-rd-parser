import typing as T
import logging
import operator
from dataclasses import dataclass
from pprint import pprint

from ast_node import AstNode
from evaluate_expression import evaluate_expression, log as expr_log
from grammars import fp_language_grammar
from lexeme import Lexeme
from memoized_recursive_descent_parser import MemoizedRecursiveDescentParser
from recursive_descent_parser import RecursiveDescentParser, log as rd_log
from regex_lexer import RegexLexer

logging.basicConfig(level=logging.WARN)
log = logging.getLogger(__name__)

EvalResult = T.Any


@dataclass
class Lazy:
    factory: T.Callable[[], T.Any]

    @property
    def value(self) -> T.Any:
        try:
            result = getattr(self, "_value")
        except AttributeError:
            result = self.factory()
            setattr(self, "_value", result)
        return result

    @staticmethod
    def unlazy(item) -> T.Any:
        while isinstance(item, Lazy):
            item = item.value
        return item


class RecursionGuard(Exception):
    def __init__(self, max=1000):
        self.count = 0
        self.max = 1000

    def inc(self):
        self.count += 1
        if self.count >= self.max:
            raise self


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


_comparison_op_table = {
    "<": operator.lt,
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.ne,
    ">=": operator.ge,
    ">": operator.gt,
}


def get_application_sequence(node: AstNode) -> T.List[AstNode]:
    result = []
    while node.name == "Application":
        result.append(node.children[0])
    return result


def evaluate_fp_program(root_node: AstNode):
    global_scope = FpScope()

    recusion_guard = RecursionGuard(max=1000)

    def eval_node(node: AstNode, current_scope: FpScope):
        recusion_guard.inc()
        log.debug(f"[eval_node] {node.name} {node.value}")

        if node.name == "AddExpr":

            def handle_node(ast_node: AstNode) -> T.Union[int, float]:
                if ast_node.lexeme is not None:
                    result = Lazy.unlazy(current_scope.get(ast_node.lexeme.value))
                    if isinstance(result, AstNode):
                        result = Lazy.unlazy(eval_node(result, current_scope))
                elif ast_node.name == "Application":
                    result = Lazy.unlazy(eval_node(ast_node, current_scope))

                if isinstance(result, (int, float)):
                    return result
                else:
                    raise Exception(f"could not handle {ast_node.value}: {result}")

            return Lazy(lambda: evaluate_expression(node, node_handler=handle_node))

        elif node.name == "Abstraction":

            def f(x):
                variable_name = T.cast(Lexeme, node.children[0].lexeme).value
                inner_scope = FpScope(current_scope)
                inner_scope.expressions[variable_name] = x
                log.debug(f"[Abstraction] {node.value} [{variable_name} <- {x}]")
                return Lazy(lambda: eval_node(node.children[2], inner_scope))

            setattr(f, "name", {node.name})
            setattr(f, "value", {node.value})

            return f

        elif node.name == "Application":
            _fn = Lazy.unlazy(eval_node(node.children[0], current_scope))
            if not callable(_fn):
                raise Exception(f"[Application] subexpression was not callable: {node}")
            _arg = Lazy(lambda: eval_node(node.children[1], current_scope))
            return Lazy(lambda: _fn(_arg))

        elif len(node.children) == 1:
            return eval_node(node.children[0], current_scope)

        elif node.name == "BracedExpression":
            return Lazy(lambda: eval_node(node.children[1], current_scope))

        elif node.matches_production("Program", "Statements Expression"):
            eval_node(node.children[0], current_scope)
            return eval_node(node.children[1], current_scope)

        elif node.matches_production("Statements", "Statement Statements"):
            eval_node(node.children[0], current_scope)
            eval_node(node.children[1], current_scope)
            return

        elif node.name == "Statement":
            identifier = T.cast(Lexeme, node.children[1].lexeme).value
            current_scope.expressions[identifier] = eval_node(node.children[3], current_scope)
            return

        elif node.name == "ComparisonExpression":
            _op = T.cast(Lexeme, node.children[1].lexeme).value
            _l = Lazy.unlazy(eval_node(node.children[0], current_scope))
            _r = Lazy.unlazy(eval_node(node.children[2], current_scope))
            log.debug(f"[ComparisonExpression] {_l} {_op} {_r}")
            return _comparison_op_table[_op](_l, _r)

        elif node.name == "IfElseExpression":
            _comparison_result = Lazy.unlazy(eval_node(node.children[2], current_scope))
            if not isinstance(_comparison_result, bool):
                raise Exception(f"[IfElseExpression] invalid comparison result: {_comparison_result}")
            if _comparison_result:
                return Lazy(lambda: eval_node(node.children[4], current_scope))
            else:
                return Lazy(lambda: eval_node(node.children[6], current_scope))

        elif node.name == "identifier":
            return current_scope.get(T.cast(Lexeme, node.lexeme).value)

        else:
            raise Exception(f"[eval_node] unhandled node: {node.name}")

    return Lazy.unlazy(eval_node(root_node, global_scope))


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument("-v_rd", action="store_true")
    parser.add_argument("-v_fp", action="store_true")
    parser.add_argument("-v_expr", action="store_true")
    parser.add_argument("-i", choices=fp_language_grammar.examples.keys())

    args = parser.parse_args(sys.argv[1:])

    if args.v_rd:
        rd_log.setLevel(logging.DEBUG)
    if args.v_fp:
        log.setLevel(logging.DEBUG)
    if args.v_expr:
        expr_log.setLevel(logging.DEBUG)

    lexer = RegexLexer(fp_language_grammar.terminals)

    for name, text in fp_language_grammar.examples.items():
        if args.i is not None and name != args.i:
            continue
        lexemes = list(lexer(text))
        memoized_parser = MemoizedRecursiveDescentParser(fp_language_grammar.productions)
        root_node = memoized_parser.parse(lexemes, fp_language_grammar.start_symbol, 0)
        result = evaluate_fp_program(root_node)
        print(f"{name}: {text}")
        pprint(result)
