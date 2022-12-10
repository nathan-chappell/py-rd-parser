from collections import defaultdict
from functools import wraps
import typing as T

P = T.ParamSpec("P")
Result = T.TypeVar("Result")
CacheKey = T.TypeVar("CacheKey")


def memoize(make_key: T.Callable[P, CacheKey]) -> T.Callable[[T.Callable[P, Result]], T.Callable[P, Result]]:
    cache: T.Dict[CacheKey, T.Union[Result, Exception]] = {}
    stats: T.DefaultDict[str, int] = defaultdict(int)

    def outer_wrapper(fn: T.Callable[P, Result]) -> T.Callable[P, Result]:
        @wraps(fn)
        def wrapped(*args: P.args, **kwargs: P.kwargs) -> Result:
            cache_key = make_key(*args, **kwargs)
            if cache_key not in cache:
                stats["cache_misses"] += 1
                try:
                    result = fn(*args, **kwargs)
                    cache[cache_key] = result
                    return result
                except Exception as e:
                    cache[cache_key] = e
                    raise e
            else:
                stats["cache_hits"] += 1
                cached_result = cache[cache_key]
                if isinstance(cached_result, Exception):
                    raise cached_result
                else:
                    return cached_result

        setattr(wrapped, "cache", cache)
        setattr(wrapped, "stats", stats)
        return wrapped

    return outer_wrapper


if __name__ == "__main__":
    calls = 0

    def fibonnaci(n: int) -> int:
        global calls
        calls += 1
        return 1 if n in (0, 1) else fibonnaci(n - 1) + fibonnaci(n - 2)

    print(f"fibonnaci(30): {fibonnaci(30)}")
    print(f"calls: {calls}")

    @memoize(lambda n: n)
    def fibonnaci_memoized(n: int) -> int:
        global calls
        calls += 1
        return 1 if n in (0, 1) else fibonnaci_memoized(n - 1) + fibonnaci_memoized(n - 2)

    print(f"fibonnaci_memoized(30): {fibonnaci_memoized(30)}")
    print(f"memoized.cache_hits: {fibonnaci_memoized.stats['cache_hits']}")
    print(f"memoized.cache_misses: {fibonnaci_memoized.stats['cache_misses']}")
