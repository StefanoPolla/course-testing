"""Draw the circuit figures for the lecture notes with Qiskit.

Writes each figure as SVG (web) and PDF (LaTeX) into figures/. White background
(not transparent), so the black circuit lines stay visible when a site is in
dark mode. Run with the ntqc-tutorials venv:
    ~/.venvs/ntqc-tutorials/bin/python make_figures.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter

OUT = Path(__file__).parent / "figures"
OUT.mkdir(exist_ok=True)
STYLE = {"name": "bw"}


def save(qc, name):
    fig = qc.draw("mpl", style=STYLE, scale=0.9)
    for ext in ("svg", "pdf"):
        fig.savefig(OUT / f"{name}.{ext}", bbox_inches="tight", facecolor="white", pad_inches=0.08)


theta = Parameter("θ")

# R_ZZ(θ) = CNOT · (I ⊗ R_Z(θ)) · CNOT
rzz = QuantumCircuit(2)
rzz.cx(0, 1)
rzz.rz(theta, 1)
rzz.cx(0, 1)
save(rzz, "rzz-decomposition")

# SWAP = three CNOTs
swap = QuantumCircuit(2)
swap.cx(0, 1)
swap.cx(1, 0)
swap.cx(0, 1)
save(swap, "swap-three-cnots")
