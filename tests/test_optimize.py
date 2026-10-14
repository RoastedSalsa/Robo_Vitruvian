"""Tests for optimize."""
import pytest


@pytest.mark.skip(reason="template")
def test_single_and_multi_agree_on_one_objective():
    """Pareto front of one objective collapses to the single-objective optimum."""
