"""Entry point: single-objective run from a config."""
import sys

from vitruvian.config import load_config
from vitruvian.optimize.problem import build_problem
from vitruvian.optimize.single import solve_single


def main(config_path: str) -> None:
    cfg = load_config(config_path)
    result = solve_single(build_problem(cfg), seed=cfg.optimizer["seed"],
                          max_evals=cfg.optimizer["max_evals"])
    print(result)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "configs/arm_humanoid.yaml")
