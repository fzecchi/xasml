import h5py
import numpy as np
from pymatgen.core import Structure

DEFAULT_CHEMENV_FRACTION_THRESHOLD = 0.95


def read_from_h5(filename, element="Fe", job="job", thresholds=None):
    """Read the data from the HDF5 file.

    Args:
        filename: Path to the HDF5 file.
        element: The absorbing element.
        job: The calculation job identifier.
        thresholds: Dictionary with ``fraction`` threshold.

    The spectra are shifted onto the common Epsii scale of the database.

    Returns:
        A tuple of (spectra, coordinations, metas) where metas is a list
        of dictionaries, one per spectrum. Each dictionary contains
        ``material_id``, ``site_id``, ``energies``, and ``structure``.
    """
    if thresholds is None:
        thresholds = {"fraction": DEFAULT_CHEMENV_FRACTION_THRESHOLD}

    energies, spectra, coordinations, metas = None, [], [], []
    with h5py.File(filename, "r") as h5:
        materials = h5["materials"]
        if not isinstance(materials, h5py.Group):
            raise TypeError("No materials found in the HDF5 file.")

        for material_id in materials:
            material = materials[material_id]
            if not isinstance(material, h5py.Group):
                raise TypeError(f"Unexpected entry for material {material_id}.")

            # Read the structure stored once per material.
            structure = material["structure"]
            if not isinstance(structure, h5py.Dataset):
                raise TypeError(f"No structure found for the material {material_id}.")
            structure = structure[()]
            if isinstance(structure, bytes):
                structure = structure.decode("utf-8")
            structure = Structure.from_str(structure, "json")

            sites = material["sites"]
            if not isinstance(sites, h5py.Group):
                raise TypeError(f"No sites found for the material {material_id}.")

            for site_id in sites:
                site_data = sites[site_id]
                if not isinstance(site_data, h5py.Group):
                    raise TypeError(
                        f"No data found for the site {site_id}"
                        f" in the material {material_id}."
                    )

                if "coordination_environments/fractions" not in site_data:
                    continue

                fractions = site_data["coordination_environments/fractions"]

                if isinstance(fractions, h5py.Dataset):
                    fractions_data = fractions[()]
                    if fractions_data.size == 0:
                        continue
                    fraction = fractions_data[0]
                else:
                    raise TypeError("No fractions found for the site.")

                # Skip if the largest fraction is below the threshold.
                if fraction < thresholds["fraction"]:
                    continue

                symbols = site_data["coordination_environments/symbols"]

                if isinstance(symbols, h5py.Dataset):
                    symbol = symbols[()][0]
                else:
                    raise TypeError("No symbols found for the site.")

                if isinstance(symbol, bytes):
                    symbol = symbol.decode("utf-8")

                if energies is None:
                    energies = site_data[f"spectra/{element}/{job}/energies"]
                    if isinstance(energies, h5py.Dataset):
                        energies = energies[()]
                    else:
                        raise ValueError("No energies found.")

                path = f"spectra/{element}/{job}/intensities_convolved_shifted"
                if path not in site_data:
                    raise KeyError(f"Rebuild the database to add {path}.")
                spectrum = site_data[path]
                if isinstance(spectrum, h5py.Dataset):
                    spectrum = spectrum[()]
                else:
                    raise TypeError("No spectrum found.")

                spectra.append(spectrum)
                coordinations.append(symbol)
                metas.append(
                    {
                        "material_id": material_id,
                        "site_id": site_id,
                        "energies": energies,
                        "structure": structure,
                    }
                )

        spectra = np.array(spectra)
        coordinations = np.array(coordinations)

    return (spectra, coordinations, metas)
