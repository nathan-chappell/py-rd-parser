import logging
import typing as T
from collections import defaultdict
from dataclasses import dataclass, field
from functools import wraps


logging.basicConfig(level=logging.WARN)
log = logging.getLogger(__name__)

TokenMatch = T.List[T.Tuple[str, T.Union[str, "Match"]]]


class ParseException(Exception):
    pass


@dataclass
class Match:
    name: str
    match: TokenMatch
    # NOTE: Open interval [start, end)
    start: int
    end: int


    def print_result(self):
        def yield_lines(match: Match, depth=0) -> T.Generator[T.Tuple[int, str], None, None]:
            """Get (depth, match-string) tuples recursively"""
            yield (depth, f"{match.name} [{match.start}, {match.end})")
            for _match in match.match:
                if isinstance(_match, str):
                    yield (depth + 1, f"{match.name}")
                else:
                    yield from yield_lines(_match, depth + 1)

        for depth, line in yield_lines(self):
            print("  " * depth + line)


TParseFn = T.Callable[[T.Any, T.List[str], str, int], Match]

def cache_stats_decorator(fn: TParseFn) -> TParseFn:
    @wraps(TParseFn)
    def wrapped(self, lexemes: T.List[str], target: str, index: int = 0) -> Match:
        use_cache: bool = getattr(self, 'use_cache', False)
        cache: T.DefaultDict[T.Tuple[str, int], Match] = getattr(self, 'cache', None)
        stats: T.DefaultDict[T.Tuple[str, int], int] = getattr(self, 'stats', None)

        if stats is not None:
            stats[("__CALL__", -1)] += 1

        if not use_cache or cache is None or stats is None:
            return fn(self, lexemes, target, index)
        else:
            _cache_key = (target, index)
            cached_result = cache.get(_cache_key, None)
            if isinstance(cached_result, ParseException):
                raise cached_result
            elif cached_result is not None:
                return cached_result
            else:
                stats[_cache_key] += 1
                try:
                    result = fn(self, lexemes, target, index)
                    cache[_cache_key] = result
                    return result
                except ParseException as e:
                    cache[_cache_key] = e
                    raise e
    return wrapped

@dataclass
class RecursiveDescentParser:
    lexemes: T.List[str]
    grammar: T.List[T.Tuple[str, str]]
    # CACHE / STATS
    use_cache: bool = True
    cache: T.DefaultDict[T.Tuple[str, int], Match] = field(default_factory=lambda: dict())
    stats: T.DefaultDict[T.Tuple[str, int], int] = field(default_factory=lambda: defaultdict(int))
    # CACHE / STATS

    def is_lexeme(self, name: str) -> bool:
        return name in self.lexemes

    @cache_stats_decorator
    def parse(self, lexemes: T.List[str], target: str, index: int = 0) -> Match:
        options = [(k, v) for k, v in self.grammar if k == target]
        log.info(f"parse({target}, {index})")
        for option_name, option in options:
            match: TokenMatch = []
            _start = index
            try:
                for name in option.split():
                    if index >= len(lexemes):
                        raise ParseException()
                    if name.endswith("*") and name != "*":
                        _name = name[:-1]
                        _matches: T.List[T.Union[str, Match]] = []
                        while True:
                            try:
                                match.append(self.parse(lexemes=lexemes, target=_name, index=index))
                                index = match[-1].end
                            except ParseException:
                                break
                        match.append(Match(name[:-1], _matches, _start, index))
                    elif not self.is_lexeme(name):
                        match.append(self.parse(lexemes=lexemes, target=name, index=index))
                        index = match[-1].end
                    elif self.is_lexeme(name) and lexemes[index] == name:
                        log.debug(f"  _LEXX {name} ({index})")
                        match.append(Match(name, [name], index, index + 1))
                        index += 1
                    elif name == "":
                        continue
                    else:
                        raise ParseException()
                _end = _start if len(match) == 0 else match[-1].end
                log.debug(f"  _SUCC {option_name} ({option})")

                return Match(option_name, match, _start, _end)
            except ParseException:
                log.debug(f"  _FAIL {option_name} ({option})")
                match = []
                index = _start
        else:
            raise ParseException()
