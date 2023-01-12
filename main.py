from pprint import pprint
from html_element import HtmlElement

from run import RunStats, run
from grammars import expression_grammar, bad_expression_grammar
from string_writer import StringWriter

if __name__ == "__main__":
    import argparse
    import sys
    import pickle
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--save-data')
    argparser.add_argument('--load-data')
    args = argparser.parse_args(sys.argv[1:])

    if args.load_data is not None:
        with open(args.load_data, 'rb') as f:
            stats = pickle.load(f)
    else:
        stats = [
            *[run(bad_expression_grammar, example_name) for example_name in bad_expression_grammar.examples.keys()],
            *[run(bad_expression_grammar, example_name, parser_type="memoized") for example_name in bad_expression_grammar.examples.keys()],
            *[run(expression_grammar, example_name) for example_name in expression_grammar.examples.keys()],
            *[run(expression_grammar, example_name, parser_type="memoized") for example_name in expression_grammar.examples.keys()],
        ]

    if args.save_data is not None:
        with open(args.save_data, 'wb') as f:
            pickle.dump(stats, f)
    
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
            HtmlElement("body", children=[
                table, 
                HtmlElement("script", attributes={"src": "./script.js"}),
            ]),
        ],
    )
    writer = StringWriter()
    document.compile(writer)
    print(writer)
