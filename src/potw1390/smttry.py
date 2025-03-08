"""
  Use SMT
"""
from typing import Iterable
from math import isqrt
from sympy import nextprime
from pysmt.shortcuts import Symbol, Equals, Or, And, Plus, Int, Times, GE, NotEquals
from pysmt.typing import INT
from pysmt.fnode import FNode
from pysmt.shortcuts import Solver

def moduli (bound: float) -> Iterable[int]:

    value = 8
    yield 8
    myprime = 2
    while value < bound:
        myprime = nextprime(myprime)
        yield myprime
        value *= myprime

def feasible_ints(base: int, maxdigs: int, sumdigs: int, sievemult: float = 2.0) -> Iterable[FNode]:
    """
      Create the formula for positive integers in base B (base)
      whose digit sum is S (sumdigs)
      and which is a square (we relax my forcing the the reduction
      mod q to be a square, for a lot of relatively prime q)
    """
    mymoduli = list(moduli(sievemult * base ** (maxdigs + 1)))
    digits = [Symbol('d_%d' % _, INT) for _ in range(maxdigs + 1)]
    yield from (GE(_, Int(0)) for _ in digits)
    yield from (GE(Int(base-1), _) for _ in digits)
    yield GE(digits[-1], Int(1)) # Can't start with a 0
    yield Equals(Plus(*digits), Int(sumdigs))
    for modulus in mymoduli:
        digit_mults = (Times(Int((base ** _) % modulus), digits[_]) for _ in range(maxdigs + 1))
        reduced_sum = Plus(*digit_mults)
        square_var = Symbol('s_%d' % modulus, INT)
        square_quo = Symbol('q_%d' % modulus, INT)
        yield GE(square_var, Int(0))
        yield GE(Int(modulus - 1), square_var)
        yield Equals(reduced_sum, Plus(Times(square_var, square_var), Times(Int(modulus), square_quo)))
        upper_bound = base * (maxdigs + 1) * (modulus - 1)

def primary_filter(base: int, maxdigs: int, sumdigs: int, sievemult: float = 2.0) -> Iterable[int]:
    """
      Get all solutions of the SMT problem and then filter out those that aren't actual squares.
    """
    digits = [Symbol('d_%d' % _, INT) for _ in range(maxdigs + 1)]
    mults = [base ** _ for _ in range(maxdigs + 1)]
    with Solver() as solver:
        for constraint in feasible_ints(base, maxdigs, sumdigs, sievemult = sievemult):
            solver.add_assertion(constraint)
        # Now get all solutions
        while solver.solve():

            # get the actual filtered value
            # and test if it's really a square
            rdigits = list(map(solver.get_value, digits))
            value = sum((_[0] * _[1].constant_value() for _ in zip(mults, rdigits)))
            check = isqrt(value)
            if value == check ** 2:
                print(f"Accepted {value}")
                yield value
            else:
                print(f"Rejected {value}")
            # Now block this value
            solver.add_assertion(Or(*(NotEquals(_[0], _[1]) for _ in zip(digits, rdigits))))
