"""Tests for model."""
import pytest


@pytest.mark.skip(reason="template")
def test_gravity_torques_single_link():
    """Single link, horizontal: tau = m * g * l/2 + payload * g * l."""
