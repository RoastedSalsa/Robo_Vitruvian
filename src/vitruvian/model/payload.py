"""Payload and end-effector definition."""
from dataclasses import dataclass

import numpy as np


@dataclass
class Payload:
    mass_kg: float
    com_offset_m: np.ndarray  # (3,) in the end-effector frame
