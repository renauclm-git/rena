"""Modal analysis solver and post-processing utilities."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.linalg import eigh

from .fem import (
    assemble_global_matrices,
    euler_bernoulli_element_matrices,
    timoshenko_element_matrices,
)


BC_MAP = {
    "clamped-free": {"fixed": ["w0", "th0"]},
    "simply supported": {"fixed": ["w0", "wL"]},
    "clamped-clamped": {"fixed": ["w0", "th0", "wL", "thL"]},
    "clamped-simply supported": {"fixed": ["w0", "th0", "wL"]},
}


@dataclass
class ModalResult:
    frequencies_hz: np.ndarray
    mode_shapes_full: np.ndarray
    mode_shapes_mass_normalized: np.ndarray
    participation_factors: np.ndarray
    effective_mass_ratio: np.ndarray
    x_coords: np.ndarray


def _boundary_conditions_to_fixed_dofs(bc: str, n_nodes: int) -> list[int]:
    fixed_tokens = BC_MAP[bc]["fixed"]
    last_node = n_nodes - 1

    token_to_dof = {
        "w0": 0,
        "th0": 1,
        "wL": 2 * last_node,
        "thL": 2 * last_node + 1,
    }
    return sorted(token_to_dof[t] for t in fixed_tokens)


def _build_global(theory: str, L: float, E: float, G: float, rho: float, A: float, I: float, kappa: float, n_elements: int):
    Le = L / n_elements
    if theory == "Euler-Bernoulli":
        return assemble_global_matrices(n_elements, euler_bernoulli_element_matrices, E, I, rho, A, Le)
    return assemble_global_matrices(n_elements, timoshenko_element_matrices, E, G, I, rho, A, kappa, Le)


def solve_modes(
    theory: str,
    bc: str,
    L: float,
    E: float,
    G: float,
    rho: float,
    A: float,
    I: float,
    kappa: float,
    n_elements: int,
    n_modes: int,
) -> ModalResult:
    """Solve generalized eigenvalue problem and return modal quantities."""
    n_nodes = n_elements + 1
    ndof = 2 * n_nodes
    K, M = _build_global(theory, L, E, G, rho, A, I, kappa, n_elements)

    fixed_dofs = _boundary_conditions_to_fixed_dofs(bc, n_nodes)
    free_dofs = np.array([i for i in range(ndof) if i not in fixed_dofs], dtype=int)

    Kff = K[np.ix_(free_dofs, free_dofs)]
    Mff = M[np.ix_(free_dofs, free_dofs)]

    evals, evecs = eigh(Kff, Mff)
    positive = evals > 1e-10
    evals = evals[positive]
    evecs = evecs[:, positive]

    count = min(n_modes, len(evals))
    evals = evals[:count]
    evecs = evecs[:, :count]

    omegas = np.sqrt(evals)
    freqs = omegas / (2.0 * np.pi)

    # Mass-normalize eigenvectors and expand to full DOF vector with constrained zeros.
    modes_full = np.zeros((ndof, count), dtype=float)
    modes_mass_norm = np.zeros((ndof, count), dtype=float)
    for i in range(count):
        phi_f = evecs[:, i]
        norm = float(np.sqrt(phi_f.T @ Mff @ phi_f))
        phi_f = phi_f / norm
        phi = np.zeros(ndof)
        phi[free_dofs] = phi_f
        modes_full[:, i] = phi
        modes_mass_norm[:, i] = phi

    # Participation for base excitation in transverse translation (w DOFs).
    r = np.zeros(ndof)
    r[0::2] = 1.0
    r[fixed_dofs] = 0.0
    r_f = r[free_dofs]
    denom = float(r_f.T @ Mff @ r_f)

    participation = np.zeros(count)
    eff_mass_ratio = np.zeros(count)
    for i in range(count):
        phi_f = modes_mass_norm[free_dofs, i]
        gamma = float(phi_f.T @ Mff @ r_f)
        participation[i] = gamma
        eff_mass_ratio[i] = (gamma**2) / denom if denom > 0 else 0.0

    x = np.linspace(0.0, L, n_nodes)

    return ModalResult(
        frequencies_hz=freqs,
        mode_shapes_full=modes_full,
        mode_shapes_mass_normalized=modes_mass_norm,
        participation_factors=participation,
        effective_mass_ratio=eff_mass_ratio,
        x_coords=x,
    )
