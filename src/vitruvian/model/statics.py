"""Static joint torques (gravity + payload) at given poses."""
import numpy as np

from .parameters import Arm
from .payload import Payload


def gravity_torques(arm: Arm, q: np.ndarray, payload: Payload) -> np.ndarray:
    """Joint torques (n,) holding configuration q."""
    raise NotImplementedError
