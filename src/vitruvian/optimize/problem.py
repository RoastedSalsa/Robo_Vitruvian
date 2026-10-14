"""Objectives + constraints as one problem definition, shared by both solvers."""
from dataclasses import dataclass
from typing import Callable

import numpy as np

from ..config import Config
from ..model.parameters import DesignSpace


@dataclass
class Problem:
    space: DesignSpace
    objectives: list[Callable]   # each: x -> float
    constraints: list[Callable]  # each: x -> array, feasible when <= 0

    def evaluate(self, x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Return (objective values, constraint values)."""
        f = np.array([obj(x) for obj in self.objectives])
        g = np.concatenate([np.atleast_1d(c(x)) for c in self.constraints])
        return f, g


def build_problem(cfg: Config) -> Problem:
    raise NotImplementedError
