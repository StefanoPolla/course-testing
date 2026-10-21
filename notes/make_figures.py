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


def running_integral(y):
    return np.concatenate([[0.0], np.cumsum((y[1:] + y[:-1]) / 2 * np.diff(t))])


columns = [("resonant qubit", f_drive, ACCENT), ("off-resonant qubit", f_off, ORANGE)]
fig, axes = plt.subplots(3, 2, figsize=(7.2, 4.8), sharex=True, sharey="row",
                         gridspec_kw={"hspace": 0.55, "wspace": 0.08})
for col, (label, f_q, colour) in enumerate(columns):
    qubit = np.cos(2 * np.pi * f_q * t)
    product = pulse * qubit
    ax = axes[0, col]
    ax.plot(t, qubit, color=colour, lw=0.8, ls="--", alpha=0.7, label="qubit oscillation")
    ax.plot(t, pulse, color="black", lw=1.2, label="pulse")
    ax.set_title("(a) pulse and qubit oscillation", fontsize=9.5, loc="left")
    ax.text(0.5, 1.42, label.capitalize(), transform=ax.transAxes, ha="center",
            fontsize=10.5, fontweight="bold", color=colour)
    ax = axes[1, col]
    ax.plot(t, product, color=colour, lw=1.1)
    ax.axhline(0, color="0.75", lw=0.6, zorder=0)
    ax.set_title("(b) their product", fontsize=9.5, loc="left")
    ax = axes[2, col]
    ax.plot(t, running_integral(product), color=colour, lw=2.0)
    ax.axhline(0, color="0.75", lw=0.6, zorder=0)
    ax.set_title("(c) accumulated effect", fontsize=9.5, loc="left")
    ax.set_xlabel("time")
axes[0, 0].legend(loc="upper left", fontsize=8, frameon=False, ncol=2,
                  bbox_to_anchor=(0, 1.05))
axes[0, 0].set_ylim(-1.15, 1.75)
for ax in axes.flat:
    ax.set_yticks([])
    ax.set_xticks([])
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
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


# ------------------------------------------- brick-wall circuit (exercise)

n_q = 4
brick = QuantumCircuit(n_q)
k = 0
for layer in range(2):
    for q in range(n_q):
        brick.rz(Parameter(f"α{k}"), q)
        brick.rx(Parameter(f"β{k}"), q)
        k += 1
    for q in range(layer % 2, n_q - 1, 2):
        brick.cz(q, q + 1)
    brick.barrier()
save_fig(brick.draw("mpl", style=STYLE, scale=0.9, plot_barriers=True,
                    initial_state=False), "brick-wall")


# ------------------------------------------- L2: Bloch ball under single-qubit channels

def convex_hull(points):
    """Monotone-chain convex hull of 2D points, as a closed list of vertices."""
    pts = sorted(set(map(tuple, np.round(points, 6))))
    if len(pts) < 3:
        return np.array(pts)

    def turn(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    def half(seq):
        out = []
        for p in seq:
            while len(out) >= 2 and turn(out[-2], out[-1], p) <= 0:
                out.pop()
            out.append(p)
        return out[:-1]
    return np.array(half(pts) + half(pts[::-1]))


def bloch_channel(ax, f, c=(0.0, 0.0, 0.0), title="", note=""):
    """The Bloch sphere (grey) and its image under r -> (f_x r_x, f_y r_y, f_z r_z) + c (blue)."""
    proj = view()
    f, c = np.asarray(f, float), np.asarray(c, float)
    d = proj(np.eye(3))[2]  # viewing direction, as the depth of the unit vectors
    # reference sphere: outline, equator and axes
    ax.add_patch(plt.Circle((0, 0), 1, fill=False, color="0.55", lw=0.9))
    s = np.linspace(0, 2 * np.pi, 400)
    curve(ax, proj, np.stack([np.cos(s), np.sin(s), 0 * s], 1), "0.6", lw=0.7)
    for vec, name in (((1, 0, 0), "$x$"), ((0, 1, 0), "$y$"), ((0, 0, 1), "$z$")):
        x, y, _ = proj(np.array(vec) * 1.0)
        ax.plot([0, x], [0, y], color="0.55", lw=0.7)
        x, y, _ = proj(np.array(vec) * 1.17)
        ax.text(x, y, name, ha="center", va="center", fontsize=9, color="0.3")
    # image of the sphere: filled silhouette, then grid lines, dashed where hidden
    uu, vv = np.meshgrid(np.linspace(0, np.pi, 40), np.linspace(0, 2 * np.pi, 80))
    sphere = np.stack([np.sin(uu) * np.cos(vv), np.sin(uu) * np.sin(vv), np.cos(uu)], -1).reshape(-1, 3)
    xy = np.stack(proj(sphere * f + c)[:2], 1)
    hull = convex_hull(xy)
    if len(hull) >= 3:
        ax.fill(hull[:, 0], hull[:, 1], color=ACCENT, alpha=0.13, lw=0)
    cof = np.array([f[1] * f[2], f[0] * f[2], f[0] * f[1]])  # normal of the image ~ cof * u

    def grid_line(u, lw):
        x, y, _ = proj(u * f + c)
        front = (u * cof) @ d >= -1e-9
        for mask, style, alpha in ((front, "-", 1.0), (~front, "--", 0.4)):
            ax.plot(np.where(mask, x, np.nan), np.where(mask, y, np.nan), color=ACCENT,
                    lw=lw, ls=style, alpha=alpha)
    for z in (-0.6, 0.0, 0.6):
        r = np.sqrt(1 - z * z)
        grid_line(np.stack([r * np.cos(s), r * np.sin(s), z + 0 * s], 1), 1.4 if z == 0 else 0.9)
    for k in range(4):
        b = k * np.pi / 4
        grid_line(np.stack([np.sin(s) * np.cos(b), np.sin(s) * np.sin(b), np.cos(s)], 1), 0.9)
    for pole, label in (((0, 0, 1), r"$|0\rangle$"), ((0, 0, -1), r"$|1\rangle$")):
        x, y, _ = proj(np.array(pole) * f + c)
        ax.plot(x, y, "o", color=ACCENT, ms=3.5)
        x0, y0, _ = proj(np.array(pole) * 1.0)
        ax.text(x0 + 0.12, y0 + (0.1 if pole[2] > 0 else -0.12), label, fontsize=9,
                ha="left", va="center", color="0.3")
    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-1.3, 1.3)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=10)
    ax.text(0, -1.42, note, ha="center", va="top", fontsize=9)


fig, axes = plt.subplots(1, 3, figsize=(7.6, 2.95))
bloch_channel(axes[0], (1, 0.5, 0.5), title="(a) bit flip, $p = 0.25$",
              note="$f_x = 1,\\ f_y = f_z = 0.5$")
bloch_channel(axes[1], (0.5, 0.5, 1), title="(b) phase flip, $p = 0.25$",
              note="$f_x = f_y = 0.5,\\ f_z = 1$")
bloch_channel(axes[2], (0.6, 0.6, 0.6), title="(c) depolarising, $p = 0.4$",
              note="$f_x = f_y = f_z = 0.6$")
fig.subplots_adjust(wspace=0.05, bottom=0.12)
save_fig(fig, "bloch-pauli-channels")

g = 0.5
fig, axes = plt.subplots(1, 2, figsize=(5.4, 3.1))
bloch_channel(axes[0], (np.sqrt(1 - g), np.sqrt(1 - g), 1 - g), c=(0, 0, g),
              title=r"(a) amplitude damping, $\gamma = 0.5$",
              note="$f_x = f_y = 0.71,\\ f_z = 0.5$,\ncentre moved up by $0.5$")
bloch_channel(axes[1], (0.3, 0.3, 1), title="(b) pure dephasing",
              note="$f_x = f_y = 0.3,\\ f_z = 1$\n ")
fig.subplots_adjust(wspace=0.05, bottom=0.12)
save_fig(fig, "bloch-relaxation-dephasing")


# ------------------------------------------- L2: Ramsey and echo sequences, decay curves

fig, (ax_seq, ax_dec) = plt.subplots(1, 2, figsize=(7.4, 2.5), gridspec_kw={"width_ratios": [1.15, 1]})


def sequence(ax, y, pulses, label):
    ax.plot([0, 10.3], [y, y], color="0.4", lw=1.0, zorder=1)
    ax.text(-0.3, y, label, ha="right", va="center", fontsize=9.5)
    for x, text in pulses:
        ax.add_patch(Rectangle((x - 0.6, y - 0.3), 1.2, 0.6, facecolor="white", edgecolor="black", lw=1.0, zorder=2))
        ax.text(x, y, text, ha="center", va="center", fontsize=8.5, zorder=3)
    ax.add_patch(Rectangle((10.3, y - 0.3), 0.9, 0.6, facecolor="0.85", edgecolor="black", lw=1.0, zorder=2))
    ax.text(10.75, y, "M", ha="center", va="center", fontsize=8.5, zorder=3)


sequence(ax_seq, 1.6, [(0.6, r"$\pi/2$"), (9.3, r"$\pi/2$")], "Ramsey")
sequence(ax_seq, 0.0, [(0.6, r"$\pi/2$"), (4.95, "$X$"), (9.3, r"$\pi/2$")], "echo")
for y, (a, b, text) in ((1.6, (1.2, 8.7, "wait $t$")), (0.0, (1.2, 4.35, "$t/2$")), (0.0, (5.55, 8.7, "$t/2$"))):
    ax_seq.annotate("", xy=(b, y + 0.5), xytext=(a, y + 0.5),
                    arrowprops=dict(arrowstyle="<->", lw=0.8, color="0.3"))
    ax_seq.text((a + b) / 2, y + 0.62, text, ha="center", va="bottom", fontsize=8.5)
ax_seq.set_xlim(-2.2, 11.4)
ax_seq.set_ylim(-0.6, 2.6)
ax_seq.axis("off")
ax_seq.set_title("(a) pulse sequences", fontsize=9.5, loc="left")

tt = np.linspace(0, 2.5, 300)  # time in units of T2
t_slow = 0.6                   # time of the slow, shot-to-shot noise, in units of T2
ax_dec.plot(tt, np.exp(-tt), color=ACCENT, lw=1.8, label=r"echo: $e^{-t/T_2}$")
ax_dec.plot(tt, np.exp(-tt) * np.exp(-(tt / t_slow) ** 2), color=ORANGE, lw=1.8,
            label=r"Ramsey: decays with $T_2^*$")
ax_dec.set_xlabel(r"waiting time $t / T_2$")
ax_dec.set_ylabel("coherence left")
ax_dec.set_ylim(0, 1.05)
ax_dec.set_xlim(0, 2.5)
ax_dec.legend(frameon=False, fontsize=8.5)
for side in ("top", "right"):
    ax_dec.spines[side].set_visible(False)
ax_dec.set_title("(b) decay of the coherence", fontsize=9.5, loc="left")
fig.subplots_adjust(wspace=0.25)
save_fig(fig, "ramsey-echo")


# ------------------------------------------- L2: coherent vs incoherent accumulation

eps = 0.02
n = np.arange(1, 101)
fig, ax = plt.subplots(figsize=(4.6, 2.9))
ax.loglog(n, np.sin(n * eps / 2) ** 2, color=ORANGE, lw=1.8,
          label=r"fixed angle $\varepsilon$: grows as $n^2$")
ax.loglog(n, (1 - np.exp(-n * eps**2 / 2)) / 2, color=ACCENT, lw=1.8,
          label=r"random angles, $\sigma = \varepsilon$: grows as $n$")
ax.set_xlabel("number of gates $n$")
ax.set_ylabel("error probability")
ax.set_xlim(1, 100)
ax.set_ylim(5e-5, 1)
ax.legend(frameon=False, fontsize=8.5, loc="upper left")
for side in ("top", "right"):
    ax.spines[side].set_visible(False)
save_fig(fig, "coherent-incoherent")
