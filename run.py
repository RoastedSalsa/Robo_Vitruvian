"""Sweep robot heights and payloads and pick the lightest drive per joint of the arm."""
import argparse
import tomllib
from pathlib import Path

from vitruvian.arm import build_arm
from vitruvian.drives import drive_options
from vitruvian.excel import write_workbook
from vitruvian.motors import Motor, load_motors
from vitruvian.report import detail, overview, preamble, summary
from vitruvian.selection import max_payload, select_drives
from vitruvian.tables import write_csvs


def override(cfg: dict, catalog: list[Motor], direct: bool, exclude: list[str] | None) -> None:
    """Apply --direct and --exclude to the config, so every output records what ran."""
    if direct:
        cfg["drive"] = []
    if exclude is not None:
        unknown = set(exclude) - {m.name for m in catalog}
        if unknown:
            raise SystemExit(f"unknown motor: {', '.join(sorted(unknown))}")
        cfg["motors"]["exclude"] = exclude
        for spec in cfg["joint"]:
            spec.pop("allow", None)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("config", nargs="?", default="config.toml")
    ap.add_argument("--height", type=float, help="show only this height, m")
    ap.add_argument("--payload", type=float, help="only this payload, kg")
    ap.add_argument("--direct", action="store_true",
                    help="no belt or capstan stage: each module's own gearbox only")
    ap.add_argument("--exclude", nargs="*", metavar="MOTOR",
                    help="keep these motors off every joint and allow every other motor at every "
                         "joint, replacing the config's exclude and allow lists; "
                         "with no names, every motor is allowed everywhere")
    ap.add_argument("--out", type=Path,
                    help="output path without extension (default results/sweep): writes "
                         "<out>.xlsx, <out>.csv and <out>-joints.csv")
    args = ap.parse_args()

    path = Path(args.config)
    cfg = tomllib.loads(path.read_text())
    payloads = [args.payload] if args.payload is not None else cfg["payload"]["mass_kg"]
    m = cfg["motors"]
    catalog = load_motors(path.parent / m["catalog"],
                          path.parent / m["local_catalog"] if "local_catalog" in m else None)
    override(cfg, catalog, args.direct, args.exclude)
    options = drive_options(catalog, cfg)
    print(preamble(catalog, cfg))

    if args.height:
        for kg in payloads:
            print(detail(select_drives(build_arm(args.height, cfg, kg), options, cfg), cfg))
        print(f"\nmax payload at {args.height:g} m: {max_payload(args.height, options, cfg):.1f} kg")
        return

    sw = cfg["sweep"]
    mm = lambda metres: round(metres * 1000)
    heights = [h / 1000 for h in range(mm(sw["height_min_m"]), mm(sw["height_max_m"]) + 1,
                                       mm(sw["step_m"]))]
    results = {kg: [select_drives(build_arm(h, cfg, kg), options, cfg) for h in heights]
               for kg in payloads}
    limits = [max_payload(h, options, cfg) for h in heights]
    for kg, sels in results.items():
        print(summary(kg, sels, cfg))
    print(overview(heights, limits, cfg))
    out = args.out or path.parent / "results" / "sweep"
    xlsx = out.with_name(out.name + ".xlsx")
    write_workbook(xlsx, results, heights, limits, catalog, options, cfg)
    files = [xlsx, *write_csvs(out, results, limits, cfg)]
    print("\nevery joint, height and payload:\n  " + "\n  ".join(map(str, files)))


if __name__ == "__main__":
    main()
