"""Compare the FDMNES spectra of job15, job16 and job17 with the experimental references.

The three jobs differ only in the radius of the cluster (5, 6 and 7 Angstrom), so the
set shows how the calculated Fe K-edge XANES converges with the size of the cluster.

The script writes three figures next to this file:

- ``radius_convergence.png``: the spectra on the Epsii scale of the database.
- ``radius_convergence_aligned.png``: the same spectra, each shifted to the position
  that minimizes the difference with the measurement.
- ``radius_convergence_metrics.png``: the shifts and the residuals.
"""

import importlib.util
import os

import matplotlib.pyplot as plt
import numpy as np

from xasml.datasets.fdmnes.material import Material

MATERIALS_PATH = "/data/scisoft/xasml/materials"
ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
COMPOUNDS_PATH = os.path.join(ROOT_PATH, "resources/datasets/experimental/compounds")
CWD = os.path.dirname(os.path.abspath(__file__))

ELEMENT = "Fe"
RADII = {"job15": 5, "job16": 6, "job17": 7}
COLORS = {5: "#3F90DA", 6: "#FFA90E", 7: "#BD1F01"}

SPECTRUM_BROADENING_PARAMS = {
    "e_cent": 30,
    "e_larg": 30,
    "gamma_hole": 1.25,
    "gamma_max": 15.0,
}
# Puts the first inflection point of calculated Fe metal at 7112.0 eV.
EPSII_REFERENCE = 6974.5
FE_K_EDGE = 7112.0

# The compound of the experimental set and the Materials Project entry accepted for it
# by scripts/datasets/experimental/match_experimental_to_corpus.py. Cordierite,
# Scorzalite and Troilite have no calculation in this set.
COMPOUNDS = {
    "Iron": "mp-13",
    "Wustite": "mp-18905",
    "Hematite": "mp-19770",
    "Goethite": "mp-605437",
    "Lepidocrocite": "mp-696580",
    "Ilmenite": "mp-19417",
    "Siderite": "mp-18969",
    "Humboldtine": "mp-698316",
    "Andradite": "mp-6672",
    "Epidote": "mp-696825",
    "Aegirine": "mp-21867",
    "Hedenbergite": "mp-18890",
    "Staurolite": "mp-744386",
    "Wolframite": "mp-19421",
    "Jarosite": "mp-1192851",
    "Scorodite": "mp-543041",
    "Rodolicoite": "mp-19109",
    "Triphylite": "mp-19017",
    "Pyrite": "mp-226",
    "Chalcopyrite": "mp-3497",
    "Tetrachloroferrate": "mp-1194614",
}

# Common grid of the comparison, the window that sets the scale of the calculation, and
# the range of the search for the shift that aligns a calculation to a measurement.
GRID = np.arange(7100.0, 7180.0 + 0.1, 0.1)
SCALE_WINDOW = (7150.0, 7180.0)
SHIFTS = np.arange(-12.0, 12.0 + 0.05, 0.05)


def multiplicity_of_site(material, site):
    """Return the symmetry multiplicity that FDMNES reports for the site."""
    for data in material.calculation.data["sites"].values():
        for frac_coords in data["frac_coords"]:
            if np.allclose(frac_coords, site.frac_coords):
                return float(data["symmetry_multiplicity"])
    raise ValueError("Fractional coordinates mapping failed.")


def read_calculation(material_id, job):
    """Return the calculated spectrum of a material on the absolute energy axis.

    The inequivalent absorbing sites are averaged with the weight of their symmetry
    multiplicity. The third value is the Epsii shift, which is the correction that
    puts the calculation on the common energy scale of the database. Returns ``None``
    when the calculation is absent or incomplete.
    """
    material = Material(material_id, MATERIALS_PATH)
    sites = material.get_unique_sites(ELEMENT)
    material.parse_calculation(ELEMENT, job)
    if material.calculation.error:
        return None

    energies, weighted, total, shift = None, None, 0.0, 0.0
    for index in sites:
        spectrum = material.get_site_spectrum(
            index, epsii_reference=EPSII_REFERENCE, **SPECTRUM_BROADENING_PARAMS
        )
        data = spectrum["spectra"][ELEMENT][job]
        multiplicity = multiplicity_of_site(material, sites[index])
        if energies is None:
            energies = data["energies"] + FE_K_EDGE
            weighted = np.zeros_like(energies)
        weighted += multiplicity * data["intensities_convolved_shifted"]
        total += multiplicity
        shift = float(data["energy_shift"])

    return energies, weighted / total, shift


def read_experiment(name):
    """Return the energy and the flattened absorption of the recommended spectrum.

    The recommended spectrum is the first entry of the comparison script of the
    compound, which also carries the calibration of its energy axis.
    """
    path = os.path.join(COMPOUNDS_PATH, name, "spectra_comparison.py")
    spec = importlib.util.spec_from_file_location(f"spectra_comparison_{name}", path)
    module = importlib.util.module_from_spec(spec)
    cwd = os.getcwd()
    os.chdir(os.path.dirname(path))
    try:
        spec.loader.exec_module(module)
        _, relative_path, kwargs, _ = module.MEASUREMENTS[0]
        group = module.normalized(relative_path, **kwargs)
    finally:
        os.chdir(cwd)
    return group.energy, group.flat


def on_grid(energies, intensities, shift=0.0):
    """Interpolate a spectrum on GRID, after a rigid shift to higher energy."""
    return np.interp(GRID, energies + shift, intensities)


def scaled(calculated, measured):
    """Scale a calculation to a measurement over the post-edge window."""
    window = (GRID >= SCALE_WINDOW[0]) & (GRID <= SCALE_WINDOW[1])
    return calculated * measured[window].mean() / calculated[window].mean()


def rms(first, second):
    return float(np.sqrt(np.mean((first - second) ** 2)))


def align(energies, intensities, measured):
    """Return the shift, the scaled spectrum and the residual that best match."""
    residuals, candidates = [], []
    for shift in SHIFTS:
        candidate = scaled(on_grid(energies, intensities, shift), measured)
        candidates.append(candidate)
        residuals.append(rms(candidate, measured))
    best = int(np.argmin(residuals))
    return float(SHIFTS[best]), candidates[best], residuals[best]


def collect():
    """Return the measured and the calculated spectra of every compound, on GRID."""
    data = {}
    for name, material_id in COMPOUNDS.items():
        measured = on_grid(*read_experiment(name))
        entry = {"material_id": material_id, "measured": measured, "radii": {}}
        for job, radius in RADII.items():
            result = read_calculation(material_id, job)
            if result is None:
                print(f"{name}: {job} (radius {radius}) is not available.")
                continue
            energies, intensities, epsii_shift = result
            unaligned = scaled(on_grid(energies, intensities), measured)
            shift, aligned, residual = align(energies, intensities, measured)
            entry["radii"][radius] = {
                "unaligned": unaligned,
                "aligned": aligned,
                "epsii_shift": epsii_shift,
                "shift": shift,
                "rms_unaligned": rms(unaligned, measured),
                "rms_aligned": residual,
            }
        data[name] = entry
    return data


def plot_grid(data, key, filename, title):
    """Plot the measurement and the calculations of every compound."""
    names = list(data)
    columns = 3
    rows = -(-len(names) // columns)
    fig, axes = plt.subplots(
        rows, columns, figsize=(9.0, 2.0 * rows), sharex=True, constrained_layout=True
    )
    axes = axes.ravel()

    for ax, name in zip(axes, names):
        entry = data[name]
        ax.plot(GRID, entry["measured"], color="black", lw=1.1, label="experiment")
        for radius, result in sorted(entry["radii"].items()):
            label = rf"$r$ = {radius} $\mathrm{{\AA}}$"
            if key == "aligned":
                label += f", {result['shift']:+.1f} eV"
            ax.plot(GRID, result[key], color=COLORS[radius], lw=0.9, label=label)
        ax.set_title(f"{name} ({entry['material_id']})", fontsize=7)
        ax.tick_params(labelsize=6)
        ax.set_xlim(7100, 7180)
        ax.legend(fontsize=5.5, frameon=False, handlelength=1.0, labelspacing=0.2)

    for ax in axes[len(names) :]:
        ax.set_visible(False)
    for ax in axes[-columns:]:
        ax.set_xlabel("Energy (eV)")
    for ax in axes[::columns]:
        ax.set_ylabel(r"Normalized $\mu(E)$")

    fig.suptitle(title, fontsize=9)
    path = os.path.join(CWD, filename)
    fig.savefig(path, dpi=200)
    plt.close(fig)
    print(f"wrote {path}")


def plot_metrics(data):
    """Plot the shift and the residual of every calculation."""
    names = list(data)
    positions = np.arange(len(names))
    width = 0.27

    fig, axes = plt.subplots(3, 1, figsize=(9.0, 7.5), constrained_layout=True)

    for offset, radius in zip((-width, 0.0, width), (5, 6, 7)):
        present = [
            (i, data[name]["radii"][radius])
            for i, name in enumerate(names)
            if radius in data[name]["radii"]
        ]
        index = np.array([i for i, _ in present])
        label = rf"$r$ = {radius} $\mathrm{{\AA}}$"
        for ax, column in zip(axes, ("epsii_shift", "shift", "rms_aligned")):
            ax.bar(
                index + offset,
                [result[column] for _, result in present],
                width=width,
                color=COLORS[radius],
                label=label,
            )

    axes[0].set_ylabel("Epsii shift (eV)")
    axes[0].set_title(
        "Correction that puts the calculation on the common scale of the database",
        fontsize=9,
    )
    axes[1].set_ylabel("Residual shift (eV)")
    axes[1].set_title(
        "Shift that remains to align the calculation with the measurement", fontsize=9
    )
    axes[2].set_ylabel("RMS difference")
    axes[2].set_title("Residual of the aligned calculation", fontsize=9)

    for ax in axes:
        ax.axhline(0.0, color="black", lw=0.6)
        ax.margins(y=0.18)
        ax.set_xticks(positions)
        ax.set_xticklabels(names, rotation=60, ha="right", fontsize=7)
        ax.legend(fontsize=7, frameon=False, ncol=3)
        ax.tick_params(labelsize=7)

    path = os.path.join(CWD, "radius_convergence_metrics.png")
    fig.savefig(path, dpi=200)
    plt.close(fig)
    print(f"wrote {path}")


def print_table(data):
    """Print the shifts and the residuals of every compound and radius."""
    columns = ("epsii_shift", "shift", "rms_unaligned", "rms_aligned")
    titles = (
        "Epsii shift (eV)",
        "Residual shift (eV)",
        "RMS, Epsii scale",
        "RMS, aligned",
    )
    for column, title in zip(columns, titles):
        print(f"\n{title}")
        header = f"{'Compound':20s}" + "".join(f"{f'r = {r}':>10s}" for r in (5, 6, 7))
        print(header)
        print("-" * len(header))
        for name, entry in data.items():
            values = "".join(
                f"{entry['radii'][r][column]:10.3f}"
                if r in entry["radii"]
                else f"{'-':>10s}"
                for r in (5, 6, 7)
            )
            print(f"{name:20s}{values}")

    print("\nMean of the absolute value over the compounds calculated at every radius")
    complete = [e for e in data.values() if len(e["radii"]) == len(RADII)]
    header = f"{'Quantity':20s}" + "".join(f"{f'r = {r}':>10s}" for r in (5, 6, 7))
    print(header)
    print("-" * len(header))
    for column, title in zip(columns, titles):
        values = "".join(
            f"{np.mean([abs(e['radii'][r][column]) for e in complete]):10.3f}"
            for r in (5, 6, 7)
        )
        print(f"{title:20s}{values}")


def main():
    plt.rcParams.update({"font.size": 7, "axes.linewidth": 0.6})
    data = collect()
    print_table(data)
    plot_grid(
        data,
        "unaligned",
        "radius_convergence.png",
        "Fe K-edge XANES against the radius of the cluster, on the Epsii scale",
    )
    plot_grid(
        data,
        "aligned",
        "radius_convergence_aligned.png",
        "Fe K-edge XANES against the radius of the cluster, aligned to the measurement",
    )
    plot_metrics(data)


if __name__ == "__main__":
    main()
