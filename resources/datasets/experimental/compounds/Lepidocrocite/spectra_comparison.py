"""Plot the experimental Fe K-edge spectra of lepidocrocite in this folder.

Run from this directory. The output replaces spectra_comparison.png, which the
README links to.
"""

import matplotlib.pyplot as plt
import numpy as np
from larch import Group
from larch.xafs import pre_edge

OUTPUT = "spectra_comparison.png"

MEASUREMENTS = [
    ("M1  BMM, NSLS-II, RT", "NIST/Fe-Lepidocrocite.xdi", {"ratio": (4, 5), "ref_ratio": (5, 6)}, "#0072B2"),
    ("M2  BIOXAS-S, CLS, 77 K", "XASDB/Lepidocrocite_id49zit3.dat", {"ratio": (1, 2), "ref_ratio": (2, 3)}, "#E69F00"),
]

FE_K_EDGE = 7112.0
PRE_EDGE_DEFAULTS = {"pre1": -150, "pre2": -30, "norm1": 150, "norm2": 950, "nnorm": 2, "nvict": 2}


def normalized(path, ratio=None, ref_ratio=None):
    """Return a larch group with the normalized spectrum read from path."""
    data = np.loadtxt(path, comments="#")
    energy = data[:, 0]
    mu = np.log(data[:, ratio[0]] / data[:, ratio[1]])

    if ref_ratio is not None:
        ref_mu = np.log(data[:, ref_ratio[0]] / data[:, ref_ratio[1]])
        ref_group = Group(energy=energy.copy(), mu=ref_mu)
        pre_edge(ref_group)
        eshift = FE_K_EDGE - ref_group.e0
        energy = energy + eshift

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
        title="Fe K-edge XANES",
        ylabel=r"Normalized $\mu(E)$",
    )
    axes[1].set(
        xlim=(7108, 7122),
        ylim=(0, 0.30),
        title=r"Pre-edge (1s $\rightarrow$ 3d)",
    )
    axes[2].set(
        xlim=(7112, 7140),
        ylim=(-0.10, 0.22),
        title="First derivative",
        ylabel=r"d$\mu$/d$E$ (eV$^{-1}$)",
    )
    for ax in axes:
        ax.set_xlabel("Energy (eV)")
        ax.tick_params(labelsize=6)

    axes[0].legend(
        loc="lower right",
        fontsize=5.2,
        frameon=False,
        handlelength=1.2,
        borderpad=0.2,
        labelspacing=0.25,
    )
    fig.savefig(OUTPUT, dpi=200)
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
