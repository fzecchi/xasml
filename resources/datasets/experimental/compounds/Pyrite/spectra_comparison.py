"""Plot the experimental Fe K-edge spectrum of pyrite in this folder.

Run from this directory. The output replaces spectra_comparison.png, which the
README links to.
"""

import matplotlib.pyplot as plt
import numpy as np
from larch import Group
from larch.xafs import pre_edge

OUTPUT = "spectra_comparison.png"

MEASUREMENTS = [
    ("M1  APS 13-BM-D, RT", "XASLIB/FeS2_rt_01.xdi", {"ratio": (1, 2)}, "#0072B2"),
]

PRE_EDGE_DEFAULTS = {"pre1": -150, "pre2": -30, "norm1": 150, "norm2": 800, "nnorm": 2, "nvict": 2}


def normalized(path, ratio=None):
    """Return a larch group with the normalized spectrum read from path."""
    data = np.loadtxt(path, comments="#")
    energy = data[:, 0]
    mu = np.log(data[:, ratio[0]] / data[:, ratio[1]])

    group = Group(energy=energy, mu=mu)
    pre_edge(group, **PRE_EDGE_DEFAULTS)
    return group


def main():
    plt.rcParams.update({"font.size": 7, "axes.linewidth": 0.6})
    fig, axes = plt.subplots(1, 3, figsize=(7.5, 2.4), constrained_layout=True)

    for label, path, kwargs, color in MEASUREMENTS:
        group = normalized(path, **kwargs)
        derivative = np.gradient(group.flat, group.energy)
        axes[0].plot(group.energy, group.flat, color=color, lw=0.9, label=label)
        axes[1].plot(group.energy, group.flat, color=color, lw=0.9)
        axes[2].plot(group.energy, derivative, color=color, lw=0.9)

    axes[0].set(
        xlim=(7100, 7180),
        ylim=(-0.05, 1.7),
        xlabel="Energy (eV)",
        ylabel=r"Normalized $\mu(E)$",
        title="XANES",
    )
    axes[0].legend(frameon=False, loc="upper left")

    axes[1].set(
        xlim=(7110, 7120),
        ylim=(-0.02, 0.4),
        xlabel="Energy (eV)",
        ylabel=r"Normalized $\mu(E)$",
        title="Pre-edge",
    )

    axes[2].set(
        xlim=(7105, 7140),
        ylim=(-0.02, 0.35),
        xlabel="Energy (eV)",
        ylabel=r"$d\mu/dE$ (eV$^{-1}$)",
        title="Derivative",
    )

    for ax in axes:
        ax.grid(True, lw=0.3, alpha=0.5)

    fig.savefig(OUTPUT, dpi=300)
    plt.close(fig)
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
