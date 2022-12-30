import typing as T
import logging
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
            result = getattr(self, '_value')
        except AttributeError:
            result = self.factory()
            setattr(self, '_value', result)
        return result
    
    @staticmethod
    def unlazy(item) -> T.Any:
        while isinstance(item, Lazy):
            item = item.value
        return item

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

    _total_calls = 0

    def eval_node(node: AstNode, current_scope: FpScope):
        nonlocal _total_calls
        _total_calls += 1
        if _total_calls > 1000:
            raise RuntimeError(f'[eval_node] _total_calls: {_total_calls}')
        log.debug(f"[eval_node] {node.name} {node.value}")
        if node.name == "Program":
            if len(node.children) == 1:
                return eval_node(node.children[0], current_scope)
            else:
                eval_node(node.children[0], current_scope)
                return eval_node(node.children[1], current_scope)

        elif node.name in passthrough_productions:
            return Lazy(lambda: eval_node(node.children[0], current_scope))
        
        elif node.name in "BracedExpression":
            return Lazy(lambda: eval_node(node.children[1], current_scope))

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
                log.debug(f'[Abstraction] {node.value} [{variable_name} <- {x}]')
                return Lazy(lambda: eval_node(node.children[2], inner_scope))
            
            setattr(f, 'name', {node.name})
            setattr(f, 'value', {node.value})

            return f

        elif node.name == "Application":
            def _application_factory():
                _fn = Lazy.unlazy(eval_node(node.children[0], current_scope))
                if not callable(_fn):
                    raise Exception(f"[Application] subexpression was not callable: {node}")
                else:
                    _arg = Lazy(lambda: eval_node(node.children[1], current_scope))
                    return Lazy(lambda: _fn(_arg))
            return Lazy(_application_factory)

        elif node.name == "ComparisonExpression":
            _op = T.cast(Lexeme, node.children[1].lexeme).value
            _l = Lazy.unlazy(eval_node(node.children[0], current_scope))
            _r = Lazy.unlazy(eval_node(node.children[2], current_scope))
            log.debug(f'[ComparisonExpression] {_l} {_op} {_r}')
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
            _comparison_result = Lazy.unlazy(eval_node(node.children[2], current_scope))
            if not isinstance(_comparison_result, bool):
                raise Exception(f"[IfElseExpression] invalid comparison result: {_comparison_result}")
            if _comparison_result:
                return Lazy(lambda: eval_node(node.children[4], current_scope))
            else:
                return Lazy(lambda: eval_node(node.children[6], current_scope))

        elif node.name == "AddExpr":

            def get_var(name: str) -> T.Union[int, float]:
                scope_value = Lazy.unlazy(current_scope.get(name))
                if isinstance(scope_value, (int, float)):
                    log.debug(f'[get_var] {name} scope_value: {scope_value}')
                    return scope_value
                value = Lazy.unlazy(eval_node(scope_value, current_scope))
                log.debug(f'[get_var] {name} value: {value}')
                if isinstance(value, (int, float)):
                    return value
                else:
                    raise Exception(f"could not evaluate {name}")

            def handle_node(ast_node: AstNode) -> T.Union[int, float]:
                result = "_NONE"
                if ast_node.name == "Application":
                    result = Lazy.unlazy(eval_node(ast_node, current_scope))
                    if isinstance(result, (int, float)):
                        return result
                raise Exception(f"could not handle {ast_node.value}: {result}")

            def _eval_factory():
                result = evaluate_expression(
                    node,
                    get_var=get_var,
                    node_handler=handle_node,
                )
                log.debug(f'[_eval_factory] {node.value} result {result}')
                return result

            return Lazy(_eval_factory)

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
    pprint(sys.argv[1:])
    args = parser.parse_args(sys.argv[1:])
    if args.v_rd:
        rd_log.setLevel(logging.DEBUG)
    if args.v_fp:
        log.setLevel(logging.DEBUG)
    if args.v_expr:
        expr_log.setLevel(logging.DEBUG)

    lexer = RegexLexer(fp_language_grammar.terminals)

    include_examples = ["statements"]
    # include_examples = ["application"]

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
