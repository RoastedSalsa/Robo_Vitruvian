"""Humanoid proportions: total height -> segment lengths and masses."""
import numpy as np


def segment_lengths(total_height_m: float, fractions: np.ndarray) -> np.ndarray:
    raise NotImplementedError


def segment_masses(total_mass_kg: float, fractions: np.ndarray) -> np.ndarray:
    raise NotImplementedError
