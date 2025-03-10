"""
  Use SMT
"""
from typing import Iterable
from math import isqrt, log
from sympy import nextprime
from pysmt.shortcuts import Symbol, Equals, Or, And, Plus, Int, Times, GE, NotEquals
from pysmt.typing import INT
from pysmt.fnode import FNode
from pysmt.shortcuts import Solver

# From Bach-Sorenson: Explicit Bounds, Table 3 for quadratic fields
# The key gives the ranges of log Delta (discriiminant)
# Bonunds for norm of least prime in residue class
# N(p) <= (A log Delta + B N + C)^2
# where (A,B,C) are the 3 values
CHEBOTAREV = {(1,5): (3.29, 1.49, 4,9),
              (5,10): (2.662, 0.75, 4.8),
              (10,25): (2.301, 0.52, 5),
              (25,100): (1.881, 0.34, 5.5),
              (100, 1000): (1.446, 0.23, 6.8),
              (1000,10000): (1.125, 0.63, 10.9),
              (100000, 1000000): (1.032, 0.44, 20.2),
              (1000000, None): (1.008, -0.006, 47.7)
              }

def moduli (bound: float) -> Iterable[int]:
    """
      We want an upper bound on the least nonsplit prime
      in Q(sqrt(d))
    """

    log_discrim = log(4 * bound)
    # Look up to find the range
    mykey = [_ for _ in CHEBOTAREV.keys()
        if log_discrim >= _[0] and (_[1] is None or log_discrim < _[1])][0]
    aval, bval, cval = CHEBOTAREV[mykey]
    # Note that N(frakp) = p^2 if frakp is nonsplit
    ubound = (aval * log_discrim + 2.0 * bval + cval)
    print(f"ubound = {ubound}")
    yield 4
    myprime = 2
    while True:
        myprime = nextprime(myprime)
        if myprime <= ubound:
            yield myprime

def feasible_ints(base: int, maxdigs: int, sumdigs: int) -> Iterable[FNode]:
    """
      Create the formula for positive integers in base B (base)
      whose digit sum is S (sumdigs)
      and which is a square (we relax my forcing the the reduction
      mod q to be a square, for a lot of relatively prime q)
    """
    mymoduli = list(moduli(base ** (maxdigs + 1)))
    digits = [Symbol('d_%d' % _, INT) for _ in range(maxdigs + 1)]
    yield from (GE(_, Int(0)) for _ in digits)
    yield from (GE(Int(base-1), _) for _ in digits)
    yield GE(digits[-1], Int(1)) # Can't start with a 0
    sum_mult = Symbol('sum_mult', INT)
    yield GE(sum_mult, Int(0))
    yield Equals(Plus(*digits), Times(Int(sumdigs), sum_mult))
    for modulus in mymoduli:
        reduced_sum = Plus(*(Times(Int((base ** ind) % modulus), val)
            for ind, val in enumerate(digits)))
        mod_var = Symbol('s_%d' % modulus, INT)
        quo_var = Symbol('q_%d' % modulus, INT)
        yield GE(mod_var, Int(0))
        yield GE(Int(modulus - 1), mod_var)
        yield Equals(reduced_sum, Plus(mod_var, Times(Int(modulus), quo_var)))
        # Find all of the squares
        mod_squares = {(_ **2) % modulus for _ in range(modulus)}
        non_squares = set(range(modulus)).difference(mod_squares)
        yield from (NotEquals(mod_var, Int(_)) for _ in non_squares)
        # yield Or(*(Equals(mod_var, Int(_)) for _ in mod_squares))

def primary_filter(base: int, maxdigs: int, sumdigs: int) -> Iterable[int]:
    """
      Get all solutions of the SMT problem and then filter out those that aren't actual squares.
    """
    digits = [Symbol('d_%d' % _, INT) for _ in range(maxdigs + 1)]
    mults = [base ** _ for _ in range(maxdigs + 1)]
    with Solver() as solver:
        for constraint in feasible_ints(base, maxdigs, sumdigs):
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
