"""Mass budget."""


def mass_margin(total_mass_kg: float, budget_kg: float) -> float:
    """g <= 0 when within budget."""
    return total_mass_kg - budget_kg
