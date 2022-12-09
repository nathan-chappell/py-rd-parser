import logging
import typing as T
from collections import defaultdict
from dataclasses import dataclass, field


logging.basicConfig(level=logging.WARN)
log = logging.getLogger(__name__)
cache_log = logging.getLogger("cache")
cache_log.setLevel(logging.WARN)

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

    def parse(self, lexemes: T.List[str], target: str, index: int = 0) -> Match:
        # CACHE / STATS
        self.stats[("__CALL__", -1)] += 1
        _cache_key = (target, index)
        if self.use_cache:
            cached_result = self.cache.get(_cache_key, None)
            if isinstance(cached_result, ParseException):
                raise cached_result
            elif cached_result is not None:
                cache_log.info(f"[HIT] ({target},{index})")
                return cached_result
            cache_log.info(f"[MISS] ({target},{index})")
        self.stats[_cache_key] += 1
        # CACHE / STATS

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

                result = Match(option_name, match, _start, _end)
                # CACHE / STATS
                if self.use_cache:
                    self.cache[_cache_key] = result
                # CACHE / STATS
                return result
            except ParseException:
                log.debug(f"  _FAIL {option_name} ({option})")
                match = []
                index = _start
        else:
            exception = ParseException()
            # CACHE / STATS
            if self.use_cache:
                self.cache[_cache_key] = exception
            # CACHE / STATS
            raise exception
