from collections import defaultdict
from functools import lru_cache
from pprint import pprint

total_calls = defaultdict(int)

def fibonacci_naive(n: int) -> int:
    """Naive, exponential time complexity"""
    total_calls['fibonacci_1'] += 1
    return n if n in (0,1) else fibonacci_naive(n-1) + fibonacci_naive(n-2)

def fibonacci_optimized(n: int) -> int:
    """Straightforward optimization"""
    if n <= 1:
        return n
    prev_val = 0
    cur_val = 1
    i = 2
    while i <= n:
        tmp = cur_val
        cur_val = cur_val + prev_val
        prev_val = tmp
        i += 1
    return cur_val

def fibonacci_bottom_up(n: int) -> int:
    """General bottom-up dynamic programming"""
    if n == 0: return 0
    fib = [0,1]
    i = 2
    while i <= n:
        fib.append(fib[-1] + fib[-2])
        i += 1
    return fib[-1]

@lru_cache
def fibonacci_top_down(n: int) -> int:
    """Naive, exponential time complexity"""
    total_calls['fibonacci_4'] += 1
    return n if n in (0,1) else fibonacci_top_down(n-1) + fibonacci_top_down(n-2)


if __name__ == '__main__':
    n = 20
    results = [
        fibonacci_naive(n),
        fibonacci_optimized(n),
        fibonacci_bottom_up(n),
        fibonacci_top_down(n),
    ]
    print("* results *")
    pprint(results)
    print("* total_calls *")
    pprint(total_calls)