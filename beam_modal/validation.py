"""Input validation helpers."""

from __future__ import annotations


def validate_inputs(params: dict) -> list[str]:
    errors: list[str] = []
    positive_fields = ["L", "E", "G", "rho", "A", "I", "kappa"]
    for name in positive_fields:
        if params[name] <= 0:
            errors.append(f"{name} must be > 0.")

    if params["n_elements"] < 1:
        errors.append("Number of elements must be at least 1.")
    if params["n_modes"] < 1:
        errors.append("Number of modes must be at least 1.")
    if params["n_modes"] > 2 * (params["n_elements"] + 1):
        errors.append("Number of modes is too large for the selected mesh size.")

    return errors
