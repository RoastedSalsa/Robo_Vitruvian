"""Forward kinematics, Jacobian, reach and workspace sampling."""
import numpy as np

from .parameters import Arm


def forward(arm: Arm, q: np.ndarray) -> np.ndarray:
    """Joint frame origins for configuration q, shape (n+1, 3)."""
    raise NotImplementedError


def jacobian(arm: Arm, q: np.ndarray) -> np.ndarray:
    raise NotImplementedError


def max_reach(arm: Arm) -> float:
    raise NotImplementedError


def sample_workspace(arm: Arm, n: int, seed: int = 0) -> np.ndarray:
    """End-effector positions for n random configurations, shape (n, 3)."""
    raise NotImplementedError
