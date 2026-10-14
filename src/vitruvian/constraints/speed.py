"""Joint speed limits."""
import numpy as np


def speed_margin(required_rad_s: np.ndarray, available_rad_s: np.ndarray) -> np.ndarray:
    """g <= 0 when feasible."""
    return required_rad_s - available_rad_s
