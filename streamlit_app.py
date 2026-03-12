"""Streamlit desktop-style app for educational beam modal analysis."""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from beam_modal.plotting import make_mode_animation, make_static_mode_plot
from beam_modal.solver import solve_modes
from beam_modal.validation import validate_inputs

st.set_page_config(page_title="Beam Modal Analysis Tutor", layout="wide")
st.title("📘 Beam Modal Analysis Tutor (Finite Elements)")
st.write(
    "Use this app to compare **Euler–Bernoulli** and **Timoshenko** beam theories, "
    "inspect natural frequencies, and visualize mode shapes."
)

with st.sidebar:
    st.header("Model Inputs")
    L = st.number_input("Length L [m]", value=1.0, min_value=0.001, format="%.6f")
    E = st.number_input("Young's modulus E [Pa]", value=210e9, min_value=1.0, format="%.6e")
    G = st.number_input("Shear modulus G [Pa]", value=80e9, min_value=1.0, format="%.6e")
    rho = st.number_input("Density ρ [kg/m³]", value=7850.0, min_value=1.0, format="%.3f")
    A = st.number_input("Area A [m²]", value=1.0e-4, min_value=1e-10, format="%.6e")
    I = st.number_input("Second moment I [m⁴]", value=8.333e-10, min_value=1e-15, format="%.6e")
    kappa = st.number_input("Shear correction κ [-]", value=5.0 / 6.0, min_value=0.01, format="%.6f")

    bc = st.selectbox(
        "Boundary condition",
        ["clamped-free", "simply supported", "clamped-clamped", "clamped-simply supported"],
    )
    n_elements = st.slider("Number of finite elements", min_value=2, max_value=100, value=20)
    n_modes = st.slider("Number of modes", min_value=1, max_value=20, value=6)

params = {
    "L": L,
    "E": E,
    "G": G,
    "rho": rho,
    "A": A,
    "I": I,
    "kappa": kappa,
    "n_elements": n_elements,
    "n_modes": n_modes,
}

errors = validate_inputs(params)
if errors:
    for err in errors:
        st.error(err)
    st.stop()

try:
    res_eb = solve_modes("Euler-Bernoulli", bc, L, E, G, rho, A, I, kappa, n_elements, n_modes)
    res_tim = solve_modes("Timoshenko", bc, L, E, G, rho, A, I, kappa, n_elements, n_modes)
except Exception as exc:
    st.error(f"Could not solve modal problem: {exc}")
    st.stop()

mode_options = [f"Mode {i+1}" for i in range(len(res_eb.frequencies_hz))]
if not mode_options:
    st.warning("No positive modes found for this setup.")
    st.stop()

selected_mode = st.selectbox("Mode to visualize", mode_options, index=0)
mode_idx = int(selected_mode.split()[-1]) - 1

tab1, tab2, tab3, tab4 = st.tabs(["Frequencies", "Mode Shapes", "Participation", "Theory Notes"])

with tab1:
    st.subheader("Natural frequencies and theory comparison")
    n_common = min(len(res_eb.frequencies_hz), len(res_tim.frequencies_hz))
    df = pd.DataFrame(
        {
            "Mode": np.arange(1, n_common + 1),
            "Euler-Bernoulli [Hz]": res_eb.frequencies_hz[:n_common],
            "Timoshenko [Hz]": res_tim.frequencies_hz[:n_common],
        }
    )
    df["Difference [%]"] = 100.0 * (df["Timoshenko [Hz]"] - df["Euler-Bernoulli [Hz]"]) / df["Euler-Bernoulli [Hz]"]
    st.dataframe(df.style.format({"Euler-Bernoulli [Hz]": "{:.4f}", "Timoshenko [Hz]": "{:.4f}", "Difference [%]": "{:.2f}"}))

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(make_static_mode_plot(res_eb, mode_idx, "Euler-Bernoulli"), use_container_width=True)
        st.plotly_chart(make_mode_animation(res_eb, mode_idx, "Euler-Bernoulli"), use_container_width=True)
    with col2:
        st.plotly_chart(make_static_mode_plot(res_tim, mode_idx, "Timoshenko"), use_container_width=True)
        st.plotly_chart(make_mode_animation(res_tim, mode_idx, "Timoshenko"), use_container_width=True)

with tab3:
    st.subheader("Modal participation factors (transverse base excitation)")
    part_df = pd.DataFrame(
        {
            "Mode": np.arange(1, len(res_eb.frequencies_hz) + 1),
            "Gamma (Euler-Bernoulli)": res_eb.participation_factors,
            "Eff. mass ratio (Euler-Bernoulli)": res_eb.effective_mass_ratio,
            "Gamma (Timoshenko)": res_tim.participation_factors,
            "Eff. mass ratio (Timoshenko)": res_tim.effective_mass_ratio,
        }
    )
    st.dataframe(part_df.style.format({
        "Gamma (Euler-Bernoulli)": "{:.4f}",
        "Eff. mass ratio (Euler-Bernoulli)": "{:.4f}",
        "Gamma (Timoshenko)": "{:.4f}",
        "Eff. mass ratio (Timoshenko)": "{:.4f}",
    }))

with tab4:
    st.markdown(
        """
### Educational notes
- **Euler–Bernoulli** assumes plane sections remain plane and perpendicular to the neutral axis; shear deformation is neglected.
- **Timoshenko** includes shear deformation and rotary inertia, which become important for thick/short beams and higher modes.
- Finite elements here use 2 DOFs per node: transverse displacement \(w\) and rotation \(\theta\).
- Mode shapes are shown mass-normalized and scaled visually for clarity.
"""
    )

st.caption("Tip: increase element count to improve higher-mode accuracy.")
