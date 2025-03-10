"""
  Exhaustion to find all squares whose digit sums are divisible by a given amount
"""
from typing import Iterable
from math import sqrt, log, exp, floor

def sum_digits(arg: int) -> int:

    return sum(map(int, str(arg)))

def exhaust_digits(base: int, maxdigs: int, divisor: int,
                   trace: int = 0) -> Iterable[int]:
    found = False
    cnt = 0
    val = 1
    for elt in range(1, floor(exp(0.5 * log(base) * maxdigs))):
        if trace > 0 and (elt % trace) == 0:
            print(f"At {val}, count = {cnt}")
        if sum_digits(val) % divisor == 0:
            cnt += 1
            if found:
                yield val
            found = True
        else:
            found = False
        val += 2 * elt + 1
    print(f"Final count = {cnt}")
