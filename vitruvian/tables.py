"""Result tables, shared by the workbook and the CSV files."""
import csv
from pathlib import Path

from .report import failing
from .selection import Selection

JOINT_HEADER = ["height m", "joint", "label", "motor", "drive", "extra ratio", "total ratio",
                "stages", "x m", "out kg", "inertia kgm²", "alpha rad/s²", "F hold N", "F peak N",
                "τ hold Nm", "τ accel Nm", "τ peak Nm", "rated used", "peak used", "speed rad/s",
                "speed req rad/s", "Ø out mm", "Ø max mm", "ok", "fails"]


def summary_header(cfg: dict) -> list[str]:
    return ["payload kg", "height m", "feasible", "fails", *(j["name"] for j in cfg["joint"]),
            "drives kg", "structure kg", "arm kg", "max payload kg"]


def summary_rows(results: dict[float, list[Selection]], limits: list[float], cfg: dict) -> list[list]:
    """One row per payload and height; limits[i] is the max payload at the i-th height."""
    return [[kg, s.arm.height, "OK" if s.feasible else "no", failing(s, cfg),
             *(c.drive.name for c in s.joints), s.drive_mass, s.arm.structure_mass, s.arm_mass,
             round(limit, 2)]
            for kg, sels in results.items() for s, limit in zip(sels, limits)]


def joint_rows(sels: list[Selection], cfg: dict) -> list[list]:
    """Every joint at every height, one payload."""
    rows = []
    for s in sels:
        for spec, xj, c in zip(cfg["joint"], s.arm.joint_x, s.joints):
            l, d = c.load, c.drive
            rows.append([s.arm.height, spec["name"], spec["label"], d.motor.name, d.kind,
                         d.ratio, d.total_ratio, d.stages, xj, l.mass_out, l.inertia, l.alpha,
                         l.force_hold, l.force_peak, l.torque_hold, l.torque_accel, l.torque_peak,
                         c.rated_use, c.peak_use, c.speed, c.speed_req, c.diameter,
                         c.diameter_max, "OK" if c.ok else "no", " ".join(c.fails)])
    return rows


def write_csv(path: Path, header: list[str], rows: list[list]) -> None:
    with path.open("w", newline="") as f:
        out = csv.writer(f)
        out.writerow(header)
        out.writerows([round(v, 4) if isinstance(v, float) else v for v in row] for row in rows)


def write_csvs(stem: Path, results: dict[float, list[Selection]], limits: list[float],
               cfg: dict) -> list[Path]:
    """<stem>.csv: one row per payload and height. <stem>-joints.csv: every joint, with a
    payload column in front. Shares are fractions (rated used 0.8 = 80%)."""
    stem.parent.mkdir(parents=True, exist_ok=True)
    summary, joints = stem.with_name(stem.name + ".csv"), stem.with_name(stem.name + "-joints.csv")
    write_csv(summary, summary_header(cfg), summary_rows(results, limits, cfg))
    write_csv(joints, ["payload kg", *JOINT_HEADER],
              [[kg, *row] for kg, sels in results.items() for row in joint_rows(sels, cfg)])
    return [summary, joints]
