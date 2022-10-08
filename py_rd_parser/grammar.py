from collections import defaultdict
from typing import List, Dict, Tuple, Set


def preprocess_grammar(grammar: List[str]) -> Tuple[Dict[str, List[str]], Set[str], str]:
    g = defaultdict(list)
    keywords: Set[str] = set()
    start_symbol = None
    for prod in grammar:
        head, body = prod.split("->")
        _head = head.strip()
        if start_symbol is None:
            start_symbol = _head
        _split = body.split()
        for prod in _split:
            if prod.startswith("'"):
                keywords.add(prod.strip("'"))
        g[_head].append(_split)
    return g, sorted(keywords, reverse=True), start_symbol
