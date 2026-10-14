"""Design-variable vector: names, bounds, vector <-> robot mapping."""
from dataclasses import dataclass

import numpy as np


@dataclass
class Arm:
    link_lengths_m: np.ndarray   # (n,)
    link_masses_kg: np.ndarray   # (n,)


@dataclass
class DesignSpace:
    names: list[str]
    lower: np.ndarray
    upper: np.ndarray

    def to_arm(self, x: np.ndarray) -> Arm:
        raise NotImplementedError
