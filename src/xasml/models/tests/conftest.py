import os

import h5py
import numpy as np
import pytest
from pymatgen.core import Lattice, Structure


@pytest.fixture(scope="session")
def resources(pytestconfig):
    return os.path.join(pytestconfig.rootdir, "data")


@pytest.fixture
def fe2o3():
    """A simplified Fe2O3 structure."""
    lattice = Lattice.rhombohedral(5.427, 55.28)
    species = ["Fe"] * 4 + ["O"] * 6
    coords = [
        [0.3553, 0.3553, 0.3553],
        [0.6447, 0.6447, 0.6447],
        [0.1447, 0.1447, 0.1447],
        [0.8553, 0.8553, 0.8553],
        [0.556, 0.944, 0.25],
        [0.944, 0.25, 0.556],
        [0.25, 0.556, 0.944],
        [0.444, 0.056, 0.75],
        [0.056, 0.75, 0.444],
        [0.75, 0.444, 0.056],
    ]
    return Structure(lattice, species, coords)


@pytest.fixture
def make_test_h5(tmp_path):
    """Create a minimal HDF5 file matching the expected layout."""
    structure = Structure(Lattice.cubic(5.0), ["Fe", "O"], [[0, 0, 0], [0.5, 0.5, 0.5]])
    energies = np.linspace(7000, 7200, 50)
    spectrum = np.random.default_rng(42).random(len(energies))

    path = str(tmp_path / "test.h5")
    material_id = "mp-1"
    site_id = "0"
    element = "Fe"
    job = "job"

    with h5py.File(path, "w") as h5:
        material_group = h5.create_group(f"materials/{material_id}")
        material_group.create_dataset("structure", data=structure.to_json())

        site_path = f"materials/{material_id}/sites/{site_id}"
        h5.create_dataset(
            f"{site_path}/coordination_environments/fractions", data=[0.99]
        )
        h5.create_dataset(
            f"{site_path}/coordination_environments/symbols", data=["O:6"]
        )
        h5.create_dataset(
            f"{site_path}/spectra/{element}/{job}/energies", data=energies
        )
        h5.create_dataset(
            f"{site_path}/spectra/{element}/{job}/intensities_convolved",
            data=spectrum,
        )
        h5.create_dataset(
            f"{site_path}/spectra/{element}/{job}/intensities_convolved_shifted",
            data=spectrum,
        )

    return path, structure, energies, spectrum
