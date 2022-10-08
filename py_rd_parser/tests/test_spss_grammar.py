import pytest

from py_rd_parser import parse
from py_rd_parser.grammars.spss_grammar import grammar, regex_lexemes, skip_lexemes


@pytest.fixture
def spss_test():
    with open(
        r"C:\Users\natha\programming\py\py-rd-parser\py_rd_parser\files\spss_test.txt", "r"
    ) as f:
        return f.read()


def test_spss_grammar(spss_test):
    assert parse(
        spss_test,
        regex_lexemes=regex_lexemes,
        grammar=grammar,
        skip_lexemes=skip_lexemes,
    )
