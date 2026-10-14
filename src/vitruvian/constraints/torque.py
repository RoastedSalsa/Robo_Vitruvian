"""Peak and continuous torque limits."""
import numpy as np


def torque_margin(required_Nm: np.ndarray, available_Nm: np.ndarray) -> np.ndarray:
    """g <= 0 when feasible."""
    return required_Nm - available_Nm
