from pprint import pprint
from html_element import HtmlElement

from run import RunStats, run
from grammars import expression_grammar, bad_expression_grammar
from string_writer import StringWriter

if __name__ == "__main__":
    stats = [
        *[run(bad_expression_grammar, example_name) for example_name in bad_expression_grammar.examples.keys()],
        *[run(bad_expression_grammar, example_name, parser_type="memoized") for example_name in bad_expression_grammar.examples.keys()],
        *[run(expression_grammar, example_name) for example_name in expression_grammar.examples.keys()],
        *[run(expression_grammar, example_name, parser_type="memoized") for example_name in expression_grammar.examples.keys()],
    ]
    table = RunStats.make_table(stats)
    document = HtmlElement(
        "html",
        children=[
            HtmlElement(
                "head",
                children=[
                    HtmlElement("link", attributes={"rel": "stylesheet", "href": "./table.css"}),
                ],
            ),
            HtmlElement("body", children=[table]),
        ],
    )
    writer = StringWriter()
    document.compile(writer)
    print(writer)
