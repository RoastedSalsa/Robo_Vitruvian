"""Height -> the arm stretched out horizontally: lengths, joint and motor positions, masses."""
from dataclasses import dataclass

LINKS = ("upper_arm", "forearm", "hand")


@dataclass
class Body:
    name: str
    mass: float         # kg
    x: float            # m from the shoulder, along the outstretched arm
    inertia: float      # kg m² about its own centre of mass
    last_joint: int     # index of the last joint it can load

    def loads(self, j: int, xj: float) -> bool:
        return j <= self.last_joint and self.x >= xj - 1e-9


@dataclass
class Arm:
    height: float
    lengths: dict[str, float]
    joint_x: list[float]    # J1..J7
    motor_x: list[float]    # each joint's motor body
    links: list[Body]       # upper arm, forearm, hand
    payload: Body

    @property
    def bodies(self) -> list[Body]:
        return [*self.links, self.payload]

    @property
    def structure_mass(self) -> float:
        return sum(b.mass for b in self.links)


def point(lengths: dict[str, float], where: list) -> float:
    """x of [link, fraction along it from its proximal end]."""
    link, fraction = where
    start = sum(lengths[name] for name in LINKS[:LINKS.index(link)])
    return start + fraction * lengths[link]


def rod(name: str, mass: float, start: float, length: float, last_joint: int) -> Body:
    return Body(name, mass, start + length / 2, mass * length**2 / 12, last_joint)


def build_arm(height: float, cfg: dict, payload_kg: float) -> Arm:
    s, p, joints = cfg["structure"], cfg["payload"], cfg["joint"]
    lengths = {name: height * cfg["proportions"][name] for name in LINKS}
    scale = (height / s["reference_height_m"]) ** s["mass_exponent"]
    elbow, wrist = lengths["upper_arm"], lengths["upper_arm"] + lengths["forearm"]
    last = len(joints) - 1
    if p["position"] <= 0:
        raise ValueError("the payload has to sit beyond the wrist")

    joint_x = [point(lengths, j["at"]) for j in joints]
    motor_x = [point(lengths, j["motor"]) for j in joints]
    for j, (xj, xm) in enumerate(zip(joint_x, motor_x)):
        if xm > xj + 1e-9:
            raise ValueError(f"{joints[j]['name']}: a motor sits at or before its joint")

    hand_kg = s["hand_kg"] * scale
    return Arm(
        height, lengths, joint_x, motor_x,
        links=[rod("upper arm", s["upper_arm_kg"] * scale, 0.0, lengths["upper_arm"], last),
               rod("forearm", s["forearm_kg"] * scale, elbow, lengths["forearm"], last),
               Body("hand", hand_kg, wrist + s["hand_com"] * lengths["hand"],
                    hand_kg * lengths["hand"]**2 / 12, last)],
        payload=Body("payload", payload_kg, wrist + p["position"] * lengths["hand"], 0.0, last),
    )
