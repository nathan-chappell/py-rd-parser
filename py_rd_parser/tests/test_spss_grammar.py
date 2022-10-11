from pathlib import Path

import pytest

from py_rd_parser import parse
from py_rd_parser.grammars.spss_grammar import grammar, regex_lexemes, preprocess_lexemes


ROOT_PATH = Path(r"D:\misc\py-rd-parser\py_rd_parser")

_test_files = [
    ROOT_PATH / r"files\spss_test.txt",
    ROOT_PATH / r"files\T0 Calculation Z-scores CNS VS variables_nw.TXT",
]


@pytest.mark.parametrize("file_like", _test_files)
def test_spss_grammar(file_like):
    with open(file_like, "r", encoding="utf_8_sig") as f:
        text = f.read()

    parse_result = parse(
        text,
        regex_lexemes=regex_lexemes,
        grammar=grammar,
        preprocess_lexemes=preprocess_lexemes,
    )
    assert parse_result
    return parse_result


if __name__ == "__main__":
    import logging

    logging.basicConfig()
    # logging.getLogger().setLevel(logging.DEBUG)
    parse_result = test_spss_grammar(_test_files[1])

    def print_node(parse_node, depth=0):
        if parse_node.type != 'EmptyOption':
            print(f"{' '*depth}{parse_node.type}")
        if not parse_node.type.islower():
            for child in getattr(parse_node, "children", []):
                print_node(child, depth + 1)

    print_node(parse_result)
