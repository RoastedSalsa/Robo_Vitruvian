"""Multi-objective solver (pymoo, Pareto front)."""
from pymoo.core.result import Result

from .problem import Problem


def solve_multi(problem: Problem, seed: int = 0, max_evals: int = 5000) -> Result:
    raise NotImplementedError
