from pprint import pprint

from run import RunStats, run
from grammars import expression_grammar, bad_expression_grammar
from string_writer import StringWriter

if __name__ == "__main__":
    # run(expression_grammar)
    # run(bad_expression_grammar)
    stats = [run(bad_expression_grammar, example_name) for example_name in bad_expression_grammar.examples.keys()]
    pprint(stats)
    table = RunStats.make_table(stats)
    pprint(table)
    writer = StringWriter()
    table.compile(writer)
    print(writer.s)
    print(id(writer))
