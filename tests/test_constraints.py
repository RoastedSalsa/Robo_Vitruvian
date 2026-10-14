"""Tests for constraints."""
import numpy as np

from vitruvian.constraints.torque import torque_margin


def test_torque_margin_sign():
    assert (torque_margin(np.array([1.0]), np.array([2.0])) < 0).all()
