from datetime import datetime
from pprint import pprint

from recursive_descent_parser import RecursiveDescentParser
from memoizer import Memoizer

def test_0n1n():
    lexemes = ["0", "1"]
    grammar = [("S", "0 S 1"), ("S", "")]
    parser = RecursiveDescentParser(lexemes, grammar)
    result = parser.parse("0 0 1 1".split(), "S")
    result.print_result()
    pprint(parser.stats)


def run_parser():
    ...


def test_exp(use_cache: bool):
    lexemes = ["x", "y", "z", "+", "*", "(", ")"]
    grammar = [
        ("E", "ME + E"),
        ("E", "ME"),
        ("ME", "F * E"),
        ("ME", "F"),
        ("F", "( E )"),
        ("F", "Var"),
        ("Var", "x"),
        ("Var", "y"),
        ("Var", "z"),
    ]
    parser = RecursiveDescentParser(lexemes, grammar, use_cache=use_cache)
    # result = parser.parse("x * y + z * ( x + y )".split(), "E")
    start_time = datetime.now()
    expression = """
    x * y + z * ( x + y * ( z + z * x + y * z + x ) * ( z + x * y ) ) *
        ( x * y + z * ( x + y * ( z + z * x + y * z + x ) * ( z + x * y ) ) +
            x * y + z * ( x + y * ( z + z * x + y * z + x ) * ( z + x * y ) ) )
    """
    result = parser.parse(expression.split(), "E")
    end_time = datetime.now()
    # print_result(result)
    # pprint(parser.stats)
    total_calls = parser.stats.pop(("__CALL__", -1))
    total_parses = sum(parser.stats.values())
    delta = end_time - start_time
    print(f"total calls:    {total_calls}")
    print(f"calls/ms:       {total_calls / (1000 * delta.total_seconds())}")
    print(f"total parses:   {total_parses}")
    print(f"parses/ms:      {total_parses / (1000 * delta.total_seconds())}")
    print(f"total time:     {delta}")


if __name__ == "__main__":
    # test_0n1n()
    print("  WITH CACHE  \n")
    test_exp(True)
    print("\n  WITHOUT CACHE  \n")
    test_exp(False)
