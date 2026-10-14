"""Objective functions: mass, cost, energy, ..."""
from ..model.parameters import Arm
from ..motors.actuator import Actuator


def total_mass(arm: Arm, actuators: list[Actuator]) -> float:
    raise NotImplementedError


def total_cost(actuators: list[Actuator]) -> float:
    raise NotImplementedError
