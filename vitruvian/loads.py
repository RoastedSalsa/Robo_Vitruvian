"""Joint loads in the worst case: arm horizontal, the joint alone accelerating the payload upwards.

Speed is zero at the instant of peak acceleration, so there are no Coriolis or centrifugal terms.
"""
from dataclasses import dataclass

from .arm import Arm, Body

G = 9.81


@dataclass
class JointLoad:
    mass_out: float         # kg beyond the joint
    inertia: float          # kg m² about the joint, its own reflected rotor included
    alpha: float            # rad/s² that gives the payload its max acceleration
    force_hold: float       # N through the joint, holding still
    force_peak: float       # N through the joint, at max acceleration
    torque_hold: float      # Nm, gravity
    torque_accel: float     # Nm, inertia × alpha

    @property
    def torque_peak(self) -> float:
        return self.torque_hold + self.torque_accel


def joint_load(arm: Arm, j: int, bodies: list[Body], reflected_inertia: float,
               accel: float) -> JointLoad:
    xj = arm.joint_x[j]
    out = [(b, b.x - xj) for b in bodies if b.loads(j, xj)]
    alpha = accel / (arm.payload.x - xj)
    inertia = sum(b.mass * r**2 + b.inertia for b, r in out) + reflected_inertia
    return JointLoad(
        mass_out=sum(b.mass for b, _ in out),
        inertia=inertia,
        alpha=alpha,
        force_hold=sum(b.mass * G for b, _ in out),
        force_peak=sum(b.mass * (G + alpha * r) for b, r in out),
        torque_hold=sum(b.mass * G * r for b, r in out),
        torque_accel=inertia * alpha,
    )
