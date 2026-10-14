"""Config loading: YAML -> typed dataclasses."""
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class Config:
    robot: dict
    payload: dict
    workspace: dict
    trajectory: dict
    catalog: dict
    bounds: dict
    optimizer: dict


def load_config(path: str | Path) -> Config:
    with open(path) as f:
        return Config(**yaml.safe_load(f))
