import re
import logging
from collections import namedtuple, defaultdict
from typing import List, Dict, Tuple, Set

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

def iter_words(string: str, split=r"[^ \t]+"):
    for match in re.finditer(split, string):
        chunk = match.group(0)
        i: int = 0
        while i < len(chunk):
            match_length: int = yield chunk[i:], i + match.start()
            i += match_length

def iter_words2(string: str):
    i: int = 0
    while i < len(string):
        match_length: int = yield string[i:], i
        i += match_length


Lexeme = namedtuple("Lexeme", ["type", "value", "start"])
_KEYWORD = 'keyword'

class LexError(Exception):
    def __init__(self, start, word, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start = start
        self.word = word


def iter_lexemes(string: str, keywords: List[str], regex_lexemes: List[str], word_re=r"[^ \t]+"):
    # generator = iter_words(string, word_re)
    generator = iter_words2(string)
    match_length = None
    _regexes = [(name, re.compile(regex)) for name, regex in regex_lexemes]

    try:
        while True:
            word, start = generator.send(match_length)
            for kw in keywords:
                if word.startswith(kw):
                    match_length = len(kw)
                    yield Lexeme(_KEYWORD, kw, start)
                    break
            else:
                for name, regex in _regexes:
                    m = regex.match(word)
                    if m:
                        match_length = m.end() - m.start()
                        yield Lexeme(name, m.group(0), start)
                        break
                else:
                    raise LexError(start, word)
    except StopIteration:
        pass


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


ParseNode = namedtuple('ParseNode', ['type', 'children'])

class ParseError(Exception):
    def __init__(self, start, lexeme, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start = start
        self.lexeme = lexeme
    
    def __str__(self):
        m = super().__str__()
        # return f'{m} - at {self.start}: {self.lexeme}'
        return f'{m} - at {self.start}'

def parse(string: str, regex_lexemes: List[Tuple[str, str]], grammar: List[str], skip_lexemes=[]):
    g, keywords, start_symbol = preprocess_grammar(grammar)
    lexemes = list(iter_lexemes(string, keywords, regex_lexemes))
    i = 0

    def next_lexeme():
        nonlocal i
        while lexemes[i].type in skip_lexemes:
            i += 1
        return lexemes[i]

    def parse_(symbol: str):
        nonlocal i
        lexeme = next_lexeme()
        mstart = f'parse_\t({symbol})'
        br1 = ' '*(20 - len(mstart))
        br2 = ' '*(40 - len(f'{mstart}{br1}'))
        log.debug(f'{mstart}{br1}at {i}:{br2}{lexeme}')
        
        if symbol == "EOF":
            if i == len(lexemes):
                return ParseNode('EOF', [])
            else:
                raise ParseError(i, lexeme, f'Expected: {symbol}')
        
        if i >= len(lexemes):
            raise ParseError(i, None, f"Out of bounds parsing {symbol}")
        
        if symbol.startswith("'"):
            literal = symbol.strip("'")
            if literal in keywords and lexeme.type == _KEYWORD and lexeme.value == literal:
                i += 1
                result = ParseNode(_KEYWORD, [lexeme])
            else:
                raise ParseError(i, lexeme, f"Expected: {symbol}")
        elif symbol.islower():
            if lexeme.type == symbol:
                i += 1
                result = ParseNode(symbol, [lexeme])
            else:
                raise ParseError(i, lexeme, f"Expected: {symbol}")
        else:
            if symbol not in g:
                raise RuntimeError(i, lexeme, f"Invalid symbol: {symbol}")
            for alternative in g[symbol]:
                _i = i
                try:
                    children = [parse_(_symbol) for _symbol in alternative]
                    result = ParseNode(symbol, children)
                    break
                except ParseError as e:
                    log.debug(e)
                    i = _i
            else:
                raise ParseError(i, lexeme, f'FAILED to parse {symbol}')
        
        log.debug(f'{mstart}{br1}at {i}: success')
        return result

    return parse_(start_symbol)