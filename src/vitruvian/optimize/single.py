"""Single-objective solver (scipy)."""
from scipy.optimize import differential_evolution, OptimizeResult

from .problem import Problem


def solve_single(problem: Problem, seed: int = 0, max_evals: int = 5000) -> OptimizeResult:
    raise NotImplementedError
