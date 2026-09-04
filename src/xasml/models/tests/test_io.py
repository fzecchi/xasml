import tempfile

import h5py
import numpy as np
from pymatgen.core import Lattice, Structure

from xasml.models.io import DEFAULT_CHEMENV_FRACTION_THRESHOLD, read_from_h5


def test_read_from_h5_returns_structure(make_test_h5):
    """The structure stored in HDF5 round-trips through read_from_h5."""
    path, structure, energies, spectrum = make_test_h5

    spectra, coordinations, metas = read_from_h5(path, element="Fe", job="job")

    assert spectra.shape == (1, len(energies))
    assert np.allclose(spectra[0], spectrum)
    assert coordinations[0] == "O:6"

    assert len(metas) == 1
    m = metas[0]
    assert m["material_id"] == "mp-1"
    assert m["site_id"] == "0"
    assert np.allclose(m["energies"], energies)

    # The reconstructed structure must match the original.
    assert isinstance(m["structure"], Structure)
    assert m["structure"].lattice.a == structure.lattice.a
    assert len(m["structure"]) == len(structure)


def test_read_from_h5_fraction_filter(make_test_h5):
    """Sites with fraction below the threshold are skipped."""
    path, *_ = make_test_h5

    # Use a threshold higher than the stored 0.99 fraction.
    spectra, _, metas = read_from_h5(
        path,
        element="Fe",
        job="job",
        thresholds={"fraction": 1.0, "intensity": 1.5},
    )

    assert len(spectra) == 0
    assert len(metas) == 0


def test_default_chemenv_fraction_threshold():
    assert DEFAULT_CHEMENV_FRACTION_THRESHOLD == 0.95


def test_read_from_h5_multiple_sites():
    """Multiple sites from the same material share one structure."""
    with tempfile.NamedTemporaryFile(suffix=".h5") as tmp:
        structure = Structure(
            Lattice.cubic(5.0), ["Fe", "O"], [[0, 0, 0], [0.5, 0.5, 0.5]]
        )
        energies = np.linspace(7000, 7200, 50)
        rng = np.random.default_rng(42)

        with h5py.File(tmp.name, "w") as h5:
            mat = h5.create_group("materials/mp-42")
            mat.create_dataset("structure", data=structure.to_json())

            for site_id in ["0", "3"]:
                site_path = f"materials/mp-42/sites/{site_id}"
                h5.create_dataset(
                    f"{site_path}/coordination_environments/fractions", data=[0.98]
                )
                h5.create_dataset(
                    f"{site_path}/coordination_environments/symbols", data=["T:4"]
                )
                h5.create_dataset(f"{site_path}/spectra/Fe/job/energies", data=energies)
                h5.create_dataset(
                    f"{site_path}/spectra/Fe/job/intensities_convolved",
                    data=rng.random(len(energies)),
                )
                h5.create_dataset(
                    f"{site_path}/spectra/Fe/job/intensities_convolved_shifted",
                    data=rng.random(len(energies)),
                )

        spectra, _, metas = read_from_h5(tmp.name, element="Fe", job="job")

    assert spectra.shape[0] == 2
    assert all(m["structure"].lattice.a == 5.0 for m in metas)
