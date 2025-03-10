"""
  Exhaustion to find all squares whose digit sums are divisible by a given amount
"""
from typing import Iterable
from math import sqrt, log, exp, floor
from itertools import islice

def sum_digits(arg: int) -> int:

    return sum(map(int, str(arg)))

def squares() -> Iterable[int]:

    val = 1
    elt = 0
    while True:
        yield val
        elt += 1
        val += 2 * elt + 1

def exhaust_digits(base: int, maxdigs: int, divisor: int,
                   trace: int = 0) -> Iterable[int]:
    found = False
    cnt = 0
    top = floor(0.5 + exp(0.5 * log(base) * maxdigs))
    print(f"top = {top}")
    for elt, val in islice(enumerate(squares(),start=1), top + 1):
        if trace > 0 and (elt % trace) == 0:
            print(f"At {elt}, count = {cnt}")
        if (sum_digits(val) % divisor) == 0:
            cnt += 1
            if found:
                if trace > 0:
                    print(f"Found pair: {elt - 1}, {elt}")
                yield elt
            found = True
        else:
            found = False
    print(f"Final count = {cnt}")
