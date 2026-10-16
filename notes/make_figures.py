"""Draw the figures for the lecture notes (circuits with Qiskit, diagrams with Matplotlib).

Writes each figure as SVG (web) and PDF (LaTeX) into figures/. White background
(not transparent), so the black lines stay visible when a site is in dark mode.
Run with the ntqc-tutorials venv:
    ~/.venvs/ntqc-tutorials/bin/python make_figures.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, Rectangle
from qiskit import QuantumCircuit
from qiskit.circuit import Gate, Parameter

OUT = Path(__file__).parent / "figures"
OUT.mkdir(exist_ok=True)
STYLE = {"name": "bw"}
ACCENT = "#1f5fa8"  # one accent colour, readable on white

plt.rcParams.update({
    "font.size": 10,
    "pdf.fonttype": 42,
})


def save_fig(fig, name):
    for ext in ("svg", "pdf"):
        fig.savefig(OUT / f"{name}.{ext}", bbox_inches="tight", facecolor="white", pad_inches=0.08)
    plt.close(fig)


def save(qc, name):
    save_fig(qc.draw("mpl", style=STYLE, scale=0.9), name)


# ------------------------------------------------------------------ circuits

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


# Virtual Z: the same circuit before and after pushing R_Z(α) to the end.
def prx(t, phi):
    return Gate("PRX", 1, [t, phi])


t1, t2, t3, alpha = (Parameter(s) for s in ("θ₁", "θ₂", "θ₃", "α"))

before = QuantumCircuit(2, 2)
before.rz(alpha, 0)
before.append(prx(t1, 0), [0])
before.append(prx(t3, 0), [1])
before.cz(0, 1)
before.append(prx(t2, 0), [0])
before.measure([0, 1], [0, 1])

after = QuantumCircuit(2, 2)
after.append(prx(t1, -alpha), [0])
after.append(prx(t3, 0), [1])
after.cz(0, 1)
after.append(prx(t2, -alpha), [0])
after.measure([0, 1], [0, 1])

save(before, "virtual-z-before")
save(after, "virtual-z-after")


# ------------------------------------------------------------- level diagrams

def levels(ax, energies, title, note):
    for n, e in enumerate(energies):
        ax.plot([0.25, 0.85], [e, e], color="black", lw=1.6)
        ax.text(0.2, e, f"$|{n}\\rangle$", ha="right", va="center")
    # arrows for the 0→1 and 1→2 transitions
    for n, x in ((0, 0.45), (1, 0.65)):
        arrow = FancyArrowPatch((x, energies[n] + 0.03), (x, energies[n + 1] - 0.03),
                                arrowstyle="<->", mutation_scale=10, lw=1.2,
                                color=ACCENT)
        ax.add_patch(arrow)
        ax.text(x + 0.03, (energies[n] + energies[n + 1]) / 2, f"$f_{{{n}{n + 1}}}$",
                va="center", color=ACCENT)
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.25, max(energies) + 0.35)
    ax.set_title(title, fontsize=10)
    ax.text(0.5, -0.2, note, ha="center", va="top", fontsize=9)
    ax.axis("off")


fig, axes = plt.subplots(1, 2, figsize=(6.4, 3.0))
levels(axes[0], [0, 1, 2, 3], "Oscillator: even spacing",
       "$f_{12} = f_{01}$: a pulse at $f_{01}$\nalso drives $|1\\rangle \\to |2\\rangle$")
levels(axes[1], [0, 1, 1.78, 2.4], "Transmon: uneven spacing",
       "$f_{12} < f_{01}$: a pulse at $f_{01}$\ndrives only $|0\\rangle \\to |1\\rangle$")
fig.subplots_adjust(bottom=0.22)
save_fig(fig, "energy-levels")


# ---------------------------------------------------------------- ion chain

def spring(ax, x0, x1, y, coils=6, amp=0.07, **kw):
    xs = np.linspace(x0, x1, 2 * coils + 3)
    ys = np.full_like(xs, y)
    ys[1:-1:2] += amp
    ys[2:-1:2] -= amp
    ys[-2] = y
    ax.plot(xs, ys, color="0.45", lw=1.0, **kw)


fig, ax = plt.subplots(figsize=(6.4, 2.0))
xs = np.arange(5) * 1.0
r = 0.17
# trap walls, with springs to the outer ions
for xw, side in ((-1.0, 1), (5.0, -1)):
    ax.add_patch(Rectangle((xw - 0.08 if side == 1 else xw, -0.35), 0.08, 0.7,
                           color="0.75", hatch="////", fill=False, lw=0))
    ax.plot([xw, xw], [-0.35, 0.35], color="0.3", lw=1.2)
spring(ax, -1.0, xs[0] - r, 0)
spring(ax, xs[-1] + r, 5.0, 0)
for a, b in zip(xs[:-1], xs[1:]):
    spring(ax, a + r, b - r, 0)
for x in xs:
    ax.add_patch(plt.Circle((x, 0), r, color=ACCENT, zorder=3))
    ax.text(x, 0, "+", color="white", ha="center", va="center", fontsize=11, zorder=4)
    arrow = FancyArrowPatch((x - 0.22, 0.42), (x + 0.22, 0.42), arrowstyle="->",
                            mutation_scale=10, lw=1.2, color="black")
    ax.add_patch(arrow)
ax.text(2.0, 0.6, "the whole chain moves together", ha="center", va="bottom", fontsize=9)
# a laser beam on one ion
ax.plot([3.0, 3.0], [-0.95, -r - 0.02], color="#c0392b", lw=2.2, alpha=0.8)
ax.text(3.08, -0.85, "laser beam on one ion", va="center", fontsize=9, color="#c0392b")
ax.set_xlim(-1.3, 5.3)
ax.set_ylim(-1.05, 0.85)
ax.set_aspect("equal")
ax.axis("off")
save_fig(fig, "ion-chain")


# ----------------------------------------------------------- coupling graphs

def draw_graph(ax, pos, edges, title, special=()):
    for a, b in edges:
        ax.plot([pos[a][0], pos[b][0]], [pos[a][1], pos[b][1]], color="0.35", lw=1.0, zorder=1)
    for k, (x, y) in pos.items():
        if k in special:
            ax.add_patch(Rectangle((x - 0.22, y - 0.22), 0.44, 0.44, color="0.25", zorder=2))
        else:
            ax.add_patch(plt.Circle((x, y), 0.13, color=ACCENT, zorder=2))
    cx = (min(p[0] for p in pos.values()) + max(p[0] for p in pos.values())) / 2
    cy = (min(p[1] for p in pos.values()) + max(p[1] for p in pos.values())) / 2
    half = 2.0  # same window in every panel, so the scales match
    ax.set_xlim(cx - half, cx + half)
    ax.set_ylim(cy - half, cy + half)
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=9.5)
    ax.axis("off")


fig, axes = plt.subplots(1, 4, figsize=(8.0, 2.3))

# (a) square lattice, 4 x 4
pos = {(i, j): (1.1 * i, 1.1 * j) for i in range(4) for j in range(4)}
edges = [((i, j), (i + 1, j)) for i in range(3) for j in range(4)]
edges += [((i, j), (i, j + 1)) for i in range(4) for j in range(3)]
draw_graph(axes[0], pos, edges, "(a) square lattice")

# (b) heavy-hex patch: two hexagons with an extra qubit on every edge
rad = 0.95
centres = [(0.0, 0.0), (np.sqrt(3) * rad, 0.0)]
verts = {}
hex_edges = set()
for cx, cy in centres:
    ring = []
    for ang in (90, 150, 210, 270, 330, 30):
        p = (round(cx + rad * np.cos(np.radians(ang)), 6), round(cy + rad * np.sin(np.radians(ang)), 6))
        verts[p] = p
        ring.append(p)
    for a, b in zip(ring, ring[1:] + ring[:1]):
        hex_edges.add(tuple(sorted((a, b))))
pos, edges = dict(verts), []
for a, b in hex_edges:
    m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    pos[m] = m
    edges += [(a, m), (m, b)]
draw_graph(axes[1], pos, edges, "(b) heavy-hex")

# (c) star: qubits around a central resonator
n = 8
pos = {"R": (0.0, 0.0)}
pos.update({k: (1.2 * np.cos(2 * np.pi * k / n), 1.2 * np.sin(2 * np.pi * k / n)) for k in range(n)})
draw_graph(axes[2], pos, [("R", k) for k in range(n)], "(c) star", special=("R",))

# (d) all-to-all, as in a small ion chain
n = 6
pos = {k: (1.4 * np.cos(2 * np.pi * k / n + np.pi / 2), 1.4 * np.sin(2 * np.pi * k / n + np.pi / 2)) for k in range(n)}
edges = [(a, b) for a in range(n) for b in range(a + 1, n)]
draw_graph(axes[3], pos, edges, "(d) all-to-all")

fig.subplots_adjust(wspace=0.15)
save_fig(fig, "coupling-graphs")


# ------------------------------------------------------- pulse and resonance

ORANGE = "#c2560c"  # second series colour; with ACCENT, passes the CVD checks on white

t = np.linspace(-6, 6, 4000)  # time, in periods of the carrier
sigma = 1.6
envelope = np.exp(-t**2 / (2 * sigma**2))
f_drive, f_off = 1.0, 1.35
pulse = envelope * np.cos(2 * np.pi * f_drive * t)
products = {
    "resonant qubit": (pulse * np.cos(2 * np.pi * f_drive * t), ACCENT),
    "off-resonant qubit": (pulse * np.cos(2 * np.pi * f_off * t), ORANGE),
}


def running_integral(y):
    return np.concatenate([[0.0], np.cumsum((y[1:] + y[:-1]) / 2 * np.diff(t))])


fig, axes = plt.subplots(3, 1, figsize=(6.4, 4.6), sharex=True,
                         gridspec_kw={"height_ratios": [1, 1, 1.1], "hspace": 0.45})
ax = axes[0]
ax.plot(t, envelope, color="0.55", lw=1.0, ls="--")
ax.plot(t, -envelope, color="0.55", lw=1.0, ls="--")
ax.plot(t, pulse, color="black", lw=1.2)
ax.text(1.9, 0.75, "envelope", color="0.4", fontsize=9)
ax.set_title("(a) the pulse: an oscillation at the carrier frequency, with a Gaussian envelope",
             fontsize=9.5, loc="left")
ax = axes[1]
for label, (y, colour) in products.items():
    ax.plot(t, y, color=colour, lw=1.1, label=label)
ax.axhline(0, color="0.75", lw=0.6, zorder=0)
ax.legend(loc="upper right", fontsize=8.5, frameon=False)
ax.set_title("(b) the pulse times the oscillation of each qubit", fontsize=9.5, loc="left")
ax = axes[2]
for label, (y, colour) in products.items():
    s = running_integral(y)
    ax.plot(t, s, color=colour, lw=2.0)
    ax.text(t[-1] + 0.15, s[-1], label.replace(" qubit", ""), color=colour, va="center", fontsize=9)
ax.axhline(0, color="0.75", lw=0.6, zorder=0)
ax.set_title("(c) accumulated effect: the running integral of (b)", fontsize=9.5, loc="left")
ax.set_xlabel("time")
for ax in axes:
    ax.set_yticks([])
    ax.set_xticks([])
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
axes[2].set_xlim(t[0], t[-1] + 2.6)
save_fig(fig, "pulse-resonance")


# ------------------------------------------- Pauli rotation from CZ and R_X

from qiskit import QuantumRegister

q1, q2, q3 = (QuantumRegister(1, name) for name in ("q1", "q2", "q3"))
pauli = QuantumCircuit(q1, q2, q3)
pauli.rx(np.pi / 2, q2)
pauli.cz(q1, q3)
pauli.cz(q2, q3)
pauli.rx(theta, q3)
pauli.cz(q2, q3)
pauli.cz(q1, q3)
pauli.rx(-np.pi / 2, q2)
save(pauli, "pauli-rotation-cz")


# ------------------------------------------- Bloch sphere rotated by PRX (static, PDF)

def view(az=np.radians(30), el=np.radians(20)):
    d = np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])
    r = np.array([-np.sin(az), np.cos(az), 0.0])
    u = np.array([-np.sin(el) * np.cos(az), -np.sin(el) * np.sin(az), np.cos(el)])
    return lambda p: (np.asarray(p) @ r, np.asarray(p) @ u, np.asarray(p) @ d)


def curve(ax, proj, pts, colour, lw=1.0, back_style="--", **kw):
    """Draw a 3D curve, dashed and faint where it runs behind the sphere."""
    x, y, depth = proj(pts)
    front = depth >= -1e-9
    for mask, style, alpha in ((front, "-", 1.0), (~front, back_style, 0.45)):
        xs, ys = np.where(mask, x, np.nan), np.where(mask, y, np.nan)
        ax.plot(xs, ys, color=colour, lw=lw, ls=style, alpha=alpha, **kw)


proj = view()
fig, ax = plt.subplots(figsize=(3.6, 3.6))
ax.add_patch(plt.Circle((0, 0), 1, fill=False, color="0.35", lw=1.0))
s = np.linspace(0, 2 * np.pi, 400)
curve(ax, proj, np.stack([np.cos(s), np.sin(s), 0 * s], 1), "0.55", lw=0.8)  # equator
for vec, name in (((1, 0, 0), "$x$"), ((0, 1, 0), "$y$"), ((0, 0, 1), "$z$")):
    x, y, _ = proj(np.array(vec) * 1.0)
    ax.plot([0, x], [0, y], color="0.35", lw=0.8)
    x, y, _ = proj(np.array(vec) * 1.18)
    ax.text(x, y, name, ha="center", va="center")
phi_ex, theta_ex = np.radians(50), np.radians(120)
n = np.array([np.cos(phi_ex), np.sin(phi_ex), 0.0])
curve(ax, proj, np.outer(np.linspace(-1, 0, 60), n), ORANGE, lw=1.8)  # back half, dashed
x, y, _ = proj(n * 1.25)
ax.annotate("", xy=(x, y), xytext=(0, 0),
            arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=1.8, mutation_scale=12))
ax.text(x - 0.05, y - 0.1, "rotation\naxis", color=ORANGE, fontsize=9, va="top", ha="center")
arc = np.linspace(0, phi_ex, 50)
curve(ax, proj, 0.35 * np.stack([np.cos(arc), np.sin(arc), 0 * arc], 1), ORANGE, lw=1.0)
x, y, _ = proj(0.45 * np.array([np.cos(phi_ex / 2), np.sin(phi_ex / 2), 0]))
ax.text(x, y - 0.02, r"$\varphi$", color=ORANGE, ha="center", va="top")
# path of |0> under the rotation: (sin φ sin t, -cos φ sin t, cos t)
ts = np.linspace(0, theta_ex, 120)
path = np.stack([np.sin(phi_ex) * np.sin(ts), -np.cos(phi_ex) * np.sin(ts), np.cos(ts)], 1)
curve(ax, proj, path, ACCENT, lw=2.0)
for p, label, dx in ((path[0], r"$|0\rangle$", 0.08), (path[-1], "", 0)):
    x, y, _ = proj(p)
    ax.plot(x, y, "o", color=ACCENT, ms=5)
    ax.text(x + dx, y + 0.05, label, fontsize=10)
x, y, _ = proj(path[60] * 1.12)
ax.text(x, y, r"$\theta$", color=ACCENT, ha="center", va="center")
ax.set_xlim(-1.35, 1.35)
ax.set_ylim(-1.3, 1.35)
ax.set_aspect("equal")
ax.axis("off")
save_fig(fig, "prx-bloch")
