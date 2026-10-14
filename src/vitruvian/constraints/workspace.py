"""Workspace / reach requirements."""
import numpy as np

from ..model.parameters import Arm


def reach_margin(arm: Arm, min_reach_m: float) -> np.ndarray:
    """g <= 0 when the arm reaches at least min_reach_m."""
    raise NotImplementedError
