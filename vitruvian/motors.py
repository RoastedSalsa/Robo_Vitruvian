"""Motor catalog. Torques and speeds are at the module output, after its gearbox."""
import math
import tomllib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Motor:
    name: str
    rated_Nm: float
    peak_Nm: float
    mass_kg: float
    ratio: float
    rotor_inertia_gcm2: float           # motor side
    rated_rpm: float
    no_load_rpm: float
    rated_V: float
    max_V: float | None = None          # only where the datasheet allows more than rated_V
    estimated: list[str] = field(default_factory=list)
    source: str = ""
    local: bool = False                 # from the local catalog: keep outputs that use it private

    @property
    def supply_V(self) -> float:
        return self.max_V or self.rated_V

    def speed_rad_s(self, torque_Nm: float) -> float:
        """Output speed while delivering torque_Nm at supply_V: the line through no-load and
        the rated point, shifted with voltage (no-load speed ∝ voltage, slope unchanged)."""
        rpm = (self.no_load_rpm * self.supply_V / self.rated_V
               - (self.no_load_rpm - self.rated_rpm) * torque_Nm / self.rated_Nm)
        return max(rpm, 0.0) * 2 * math.pi / 60


def load_motors(path: str | Path, local: str | Path | None = None) -> list[Motor]:
    """Catalog, lightest first, plus the local catalog when it is given and exists."""
    motors = []
    for file, is_local in [(path, False), (local, True)]:
        if file is None or (is_local and not Path(file).exists()):
            continue
        with open(file, "rb") as f:
            motors += [Motor(**m, local=is_local) for m in tomllib.load(f)["motor"]]
    names = [m.name for m in motors]
    if dupes := sorted({n for n in names if names.count(n) > 1}):
        raise ValueError(f"motor listed twice: {', '.join(dupes)}")
    return sorted(motors, key=lambda m: m.mass_kg)
