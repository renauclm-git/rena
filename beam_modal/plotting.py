"""Plot helpers for modal results."""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go

from .solver import ModalResult


def mode_shape_trace(x: np.ndarray, modal_vector: np.ndarray, scale: float = 1.0) -> np.ndarray:
    """Extract nodal transverse displacement from full DOF mode vector."""
    w = modal_vector[0::2]
    max_abs = np.max(np.abs(w))
    if max_abs > 0:
        w = w / max_abs
    return scale * w


def make_static_mode_plot(result: ModalResult, mode_idx: int, theory: str) -> go.Figure:
    y = mode_shape_trace(result.x_coords, result.mode_shapes_mass_normalized[:, mode_idx])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=result.x_coords, y=y, mode="lines+markers", name=f"Mode {mode_idx + 1}"))
    fig.update_layout(
        title=f"{theory} - Mode {mode_idx + 1} (normalized shape)",
        xaxis_title="x [m]",
        yaxis_title="Normalized transverse displacement",
        template="plotly_white",
    )
    return fig


def make_mode_animation(result: ModalResult, mode_idx: int, theory: str, n_frames: int = 40) -> go.Figure:
    mode = mode_shape_trace(result.x_coords, result.mode_shapes_mass_normalized[:, mode_idx], scale=1.0)
    t_vals = np.linspace(0.0, 2.0 * np.pi, n_frames)

    frames = []
    for t in t_vals:
        y = mode * np.sin(t)
        frames.append(go.Frame(data=[go.Scatter(x=result.x_coords, y=y, mode="lines+markers")]))

    fig = go.Figure(
        data=[go.Scatter(x=result.x_coords, y=mode, mode="lines+markers")],
        frames=frames,
    )
    fig.update_layout(
        title=f"{theory} - Animated mode {mode_idx + 1}",
        xaxis_title="x [m]",
        yaxis_title="Relative displacement",
        yaxis=dict(range=[-1.2, 1.2]),
        template="plotly_white",
        updatemenus=[
            {
                "type": "buttons",
                "buttons": [
                    {
                        "label": "Play",
                        "method": "animate",
                        "args": [None, {"frame": {"duration": 50, "redraw": True}, "fromcurrent": True}],
                    },
                    {
                        "label": "Pause",
                        "method": "animate",
                        "args": [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}],
                    },
                ],
            }
        ],
    )
    return fig
