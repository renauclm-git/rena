# Beam Modal Analysis Tutor (Streamlit)

Educational Streamlit app for finite-element modal analysis of a uniform prismatic beam.

## Features

- Finite-element beam modal analysis (2 DOF per node: transverse displacement and rotation)
- Two theories:
  - Euler–Bernoulli
  - Timoshenko (shear deformation + rotary inertia)
- Boundary conditions:
  - clamped-free
  - simply supported
  - clamped-clamped
  - clamped-simply supported
- Inputs: `L, E, G, rho, A, I, kappa, number of elements, number of modes`
- Outputs:
  - natural frequencies
  - mass-normalized mode shapes
  - modal participation factors
  - static mode plots
  - animated mode shapes
- Side-by-side comparison between Euler–Bernoulli and Timoshenko results
- Input validation and basic error handling

## Project structure

```text
.
├── beam_modal/
│   ├── __init__.py
│   ├── fem.py           # element matrices and assembly
│   ├── plotting.py      # static + animated Plotly figures
│   ├── solver.py        # eigenvalue solve + participation factors
│   └── validation.py    # input checks
├── streamlit_app.py     # Streamlit GUI entrypoint
├── requirements.txt
└── README.md
```

## Local execution

1. Create/activate a Python 3.10+ environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:

   ```bash
   streamlit run streamlit_app.py
   ```

4. Open the local URL shown by Streamlit (usually `http://localhost:8501`).

## Implementation notes

- Global mass and stiffness matrices are assembled from 2-node beam elements.
- Modal extraction solves the generalized eigenproblem:
  \[ K \phi = \omega^2 M \phi \]
- Boundary conditions are enforced by reducing to free DOFs.
- Eigenvectors are mass-normalized before post-processing.
- Participation factors are computed for transverse base excitation using a displacement influence vector on translational DOFs.

