"""Hand-written rigid-body dynamics: joint torques for a trajectory."""
import numpy as np

from .parameters import Arm
from .payload import Payload


def inverse_dynamics(arm: Arm, q: np.ndarray, qd: np.ndarray, qdd: np.ndarray,
                     payload: Payload) -> np.ndarray:
    """tau = M(q) qdd + C(q, qd) qd + g(q), shape (n,)."""
    raise NotImplementedError
