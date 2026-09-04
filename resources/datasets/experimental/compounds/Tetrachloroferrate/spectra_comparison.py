"""Plot the experimental Fe K-edge spectrum of tetraethylammonium tetrachloroferrate(III) in this folder.

Run from this directory. The output replaces spectra_comparison.png, which the
README links to.
"""

import matplotlib.pyplot as plt
import numpy as np
from larch import Group
from larch.xafs import pre_edge

OUTPUT = "spectra_comparison.png"

MEASUREMENTS = [
    (
        "M1  PF, 1983, RT",
        "MDR/K_NC2H54FeCl4_Si311_19831201.txt",
        {"foil": "MDR/K_FeFoil_Si311_19831201_ref.txt"},
        "#0072B2",
    ),
]

FE_K_EDGE = 7112.0
# The scan stops at 7127.5 eV (7137 eV after the shift), so the post-edge
# normalization range is short and linear.
PRE_EDGE_DEFAULTS = {"pre1": -30, "pre2": -12, "norm1": 11, "norm2": 16, "nnorm": 1}


def read_two_columns(path):
    """Return energy and mu from a two-column MDR text file, duplicates removed."""
    data = np.loadtxt(path)
    energy, index = np.unique(data[:, 0], return_index=True)
    return energy, data[index, 1]


def normalized(path, foil=None):
    """Return a larch group with the normalized spectrum read from path."""
    energy, mu = read_two_columns(path)

    if foil is not None:
        ref_energy, ref_mu = read_two_columns(foil)
        ref_group = Group(energy=ref_energy, mu=ref_mu)
        pre_edge(ref_group)
        energy = energy + (FE_K_EDGE - ref_group.e0)

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
        xlim=(7100, 7140),
        ylim=(-0.05, 1.4),
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
        ylim=(-0.05, 0.45),
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
