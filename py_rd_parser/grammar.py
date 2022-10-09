from collections import defaultdict, namedtuple
from typing import List, Dict, Tuple, Set


def preprocess_grammar(grammar: List[str]) -> Tuple[Dict[str, List[str]], Set[str], str]:
    g = defaultdict(list)
    keywords: Set[str] = set()
    start_symbol = None

    def add_keywords(_split: List[str]):
        keywords.update(prod.strip("'") for prod in _split if prod.startswith("'"))

    for prod in grammar:
        head, body = prod.split("->")
        _head = head.strip()
        if start_symbol is None:
            start_symbol = _head
        if "|" in body:
            choices = [s.strip() for s in body.split("|")]
            add_keywords(choices)
            g[_head].extend([choice] for choice in choices)
        else:
            _split = body.split()
            add_keywords(_split)
            g[_head].append(_split)
    return g, sorted(keywords, reverse=True), start_symbol
