"""Finite-element matrices for beam elements."""

from __future__ import annotations

import numpy as np


def euler_bernoulli_element_matrices(E: float, I: float, rho: float, A: float, Le: float) -> tuple[np.ndarray, np.ndarray]:
    """Return 4x4 element stiffness and mass matrices for Euler-Bernoulli beam."""
    k = (E * I / Le**3) * np.array(
        [
            [12.0, 6.0 * Le, -12.0, 6.0 * Le],
            [6.0 * Le, 4.0 * Le**2, -6.0 * Le, 2.0 * Le**2],
            [-12.0, -6.0 * Le, 12.0, -6.0 * Le],
            [6.0 * Le, 2.0 * Le**2, -6.0 * Le, 4.0 * Le**2],
        ]
    )

    m = (rho * A * Le / 420.0) * np.array(
        [
            [156.0, 22.0 * Le, 54.0, -13.0 * Le],
            [22.0 * Le, 4.0 * Le**2, 13.0 * Le, -3.0 * Le**2],
            [54.0, 13.0 * Le, 156.0, -22.0 * Le],
            [-13.0 * Le, -3.0 * Le**2, -22.0 * Le, 4.0 * Le**2],
        ]
    )
    return k, m


def timoshenko_element_matrices(
    E: float,
    G: float,
    I: float,
    rho: float,
    A: float,
    kappa: float,
    Le: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Return 4x4 element stiffness and mass matrices for Timoshenko beam.

    This uses a standard shear-corrected stiffness matrix and a practical
    consistent mass with translational + rotary inertia terms.
    """
    phi = 12.0 * E * I / (kappa * G * A * Le**2)
    coef = E * I / (Le**3 * (1.0 + phi))

    k = coef * np.array(
        [
            [12.0, 6.0 * Le, -12.0, 6.0 * Le],
            [6.0 * Le, (4.0 + phi) * Le**2, -6.0 * Le, (2.0 - phi) * Le**2],
            [-12.0, -6.0 * Le, 12.0, -6.0 * Le],
            [6.0 * Le, (2.0 - phi) * Le**2, -6.0 * Le, (4.0 + phi) * Le**2],
        ]
    )

    m_trans = (rho * A * Le / 420.0) * np.array(
        [
            [156.0, 22.0 * Le, 54.0, -13.0 * Le],
            [22.0 * Le, 4.0 * Le**2, 13.0 * Le, -3.0 * Le**2],
            [54.0, 13.0 * Le, 156.0, -22.0 * Le],
            [-13.0 * Le, -3.0 * Le**2, -22.0 * Le, 4.0 * Le**2],
        ]
    )

    rho_I = rho * I
    m_rot = (rho_I * Le / 30.0) * np.array(
        [
            [0.0, 0.0, 0.0, 0.0],
            [0.0, 4.0, 0.0, -1.0],
            [0.0, 0.0, 0.0, 0.0],
            [0.0, -1.0, 0.0, 4.0],
        ]
    )

    return k, m_trans + m_rot


def assemble_global_matrices(
    n_elements: int,
    element_builder,
    *element_args,
) -> tuple[np.ndarray, np.ndarray]:
    """Assemble global stiffness and mass matrices for a 2-DOF/node beam mesh."""
    n_nodes = n_elements + 1
    ndof = 2 * n_nodes
    K = np.zeros((ndof, ndof), dtype=float)
    M = np.zeros((ndof, ndof), dtype=float)

    for e in range(n_elements):
        ke, me = element_builder(*element_args)
        dofs = [2 * e, 2 * e + 1, 2 * (e + 1), 2 * (e + 1) + 1]
        for i, gi in enumerate(dofs):
            for j, gj in enumerate(dofs):
                K[gi, gj] += ke[i, j]
                M[gi, gj] += me[i, j]

    return K, M
