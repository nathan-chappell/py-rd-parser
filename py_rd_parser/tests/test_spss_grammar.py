import pytest

from py_rd_parser import parse
from py_rd_parser.grammars.spss_grammar import grammar, regex_lexemes, preprocess_lexemes


_test_files = [
    r"C:\Users\natha\programming\py\py-rd-parser\py_rd_parser\files\spss_test.txt",
    r"C:\Users\natha\programming\py\py-rd-parser\py_rd_parser\files\T0 Calculation Z-scores CNS VS variables_nw.TXT",
]


@pytest.mark.parametrize("file_name", _test_files)
def test_spss_grammar(file_name):
    with open(file_name, "r") as f:
        text = f.read()

    assert parse(
        text,
        regex_lexemes=regex_lexemes,
        grammar=grammar,
        preprocess_lexemes=preprocess_lexemes,
    )

if __name__ == '__main__':
    import logging
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    test_spss_grammar(_test_files[1])
