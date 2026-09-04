"""Plot the unique experimental Fe K-edge spectra of wüstite in this folder.

Run from this directory. The output replaces spectra_comparison.png, which the
README links to.
"""

import matplotlib.pyplot as plt
import numpy as np
from larch import Group
from larch.xafs import pre_edge

OUTPUT = "spectra_comparison.png"

# One entry per unique measurement. The XASDB copies of M1 and M2 are omitted
# because they duplicate the XDI files and carry a min-max scaled mu column.
MEASUREMENTS = [
    ("M1  BMM, NSLS-II, RT", "NIST/Fe-Wustite.xdi", {"mu_column": 3}, "#0072B2"),
    ("M2  20-BM, APS, RT", "XASLIB/FeO_rt_01.xdi", {"ratio": (1, 2)}, "#E69F00"),
    (
        "M3  BM08, ESRF, 300 K",
        "XASDB/Iron (II) Oxide_idg74ufm.dat",
        {"mu_column": 1, "drop_last": True},
        "#009E73",
    ),
    (
        "M4  BM08, ESRF, 300 K",
        "XASDB/Iron (II) Oxide_idq2cv7k.dat",
        {"mu_column": 1, "drop_last": True},
        "#D55E00",
    ),
    (
        "M5  BM08, ESRF, 79 K",
        "XASDB/Iron (II) Oxide_idxvotm2.dat",
        {"mu_column": 1, "drop_last": True},
        "#CC79A7",
    ),
    (
        "M6  BM30B, ESRF, HERFD, 295 K",
        "FAME/Iron_(II)_Oxide_HERFD_SPECTRUM_SOC_20181115_004H.dat",
        {"mu_column": 2},
        "#5D3A00",
    ),
]


def normalized(path, mu_column=None, ratio=None, drop_last=False):
    """Return a larch group with the normalized spectrum read from path."""
    data = np.loadtxt(path, comments="#")
    energy = data[:, 0]
    if mu_column is not None:
        mu = data[:, mu_column]
    else:
        mu = np.log(data[:, ratio[0]] / data[:, ratio[1]])
    if drop_last:
        # The XASDB mu column is min-max scaled, so the last point is a hard 0.
        energy, mu = energy[:-1], mu[:-1]
    group = Group(energy=energy, mu=mu)
    pre_edge(group)
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
        xlim=(7108, 7120), ylim=(0, 0.45), title=r"Pre-edge (1s $\rightarrow$ 3d)"
    )
    axes[2].set(
        xlim=(7112, 7136),
        ylim=(-0.20, 0.24),
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
