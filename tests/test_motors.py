"""Tests for motors."""
from vitruvian.motors.catalog import load_gearboxes, load_motors


def test_catalog_loads():
    assert load_motors("data/motors/motors.yaml")
    assert load_gearboxes("data/motors/gearboxes.yaml")
