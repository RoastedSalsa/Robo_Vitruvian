"""Assign actuators to joints."""
import numpy as np

from .actuator import Actuator
from .catalog import Gearbox, Motor


def select_actuators(peak_torque_Nm: np.ndarray, max_speed_rad_s: np.ndarray,
                     motors: list[Motor], gearboxes: list[Gearbox]) -> list[Actuator]:
    """Lightest feasible actuator per joint."""
    raise NotImplementedError
