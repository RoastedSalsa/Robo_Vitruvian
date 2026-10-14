"""Result tables (CSV / markdown)."""
from pathlib import Path


def write_table(rows: list[dict], path: str | Path) -> None:
    raise NotImplementedError
