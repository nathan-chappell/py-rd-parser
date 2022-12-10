from functools import wraps
import typing as T

P = T.ParamSpec("P")
Result = T.TypeVar("Result")
CacheKey = T.TypeVar("CacheKey")


class Memoizer(T.Generic[P, Result, CacheKey]):
    cache: T.Dict[CacheKey, T.Union[Result, Exception]] = {}
    cache_hits: int = 0
    cache_misses: int = 0

    def __call__(self, make_key: T.Callable[P, CacheKey]) -> T.Callable[[T.Callable[P, Result]], T.Callable[P, Result]]:
        def decorator(fn: T.Callable[P, Result]) -> T.Callable[P, Result]:
            @wraps(fn)
            def wrapped(*args: P.args, **kwargs: P.kwargs) -> Result:
                cache_key = make_key(*args, **kwargs)
                if cache_key not in self.cache:
                    self.cache_misses += 1
                    try:
                        result = fn(*args, **kwargs)
                        self.cache[cache_key] = result
                        return result
                    except ParseException as e:
                        self.cache[cache_key] = e
                        raise e
                else:
                    self.cache_hits += 1
                    cached_result = self.cache[cache_key]
                    if isinstance(cached_result, Exception):
                        raise cached_result
                    else:
                        return cached_result

            return wrapped

        return decorator


if __name__ == "__main__":
    calls = 0

    def fibonnaci(n: int) -> int:
        global calls
        calls += 1
        return 1 if n in (0, 1) else fibonnaci(n - 1) + fibonnaci(n - 2)

    print(f"fibonnaci(30): {fibonnaci(30)}")
    print(f"calls: {calls}")

    memoized = Memoizer()

    @memoized(lambda n: n)
    def fibonnaci(n: int) -> int:
        global calls
        calls += 1
        return 1 if n in (0, 1) else fibonnaci(n - 1) + fibonnaci(n - 2)

    print(f"fibonnaci(30): {fibonnaci(30)}")
    print(f"memoized.cache_hits: {memoized.cache_hits}")
    print(f"memoized.cache_misses: {memoized.cache_misses}")
