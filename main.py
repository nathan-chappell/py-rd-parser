from run import run

from grammars import expression_grammar, bad_expression_grammar

if __name__ == "__main__":
    run(expression_grammar)
    run(bad_expression_grammar)
