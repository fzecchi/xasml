"""Estimate noise in the experimental spectra on their native energy grids."""

import pickle

import numpy as np

from xasml import resource_path
from xasml.models.noise import (
    estimate_local_linear_noise,
    rms_in_region,
)

EDGE_ENERGY = 7112.0
POST_EDGE = (EDGE_ENERGY + 30.0, EDGE_ENERGY + 70.0)
MODEL_STEP = 0.1
NOISE_WINDOW = 3.0


def second_difference_noise(intensities: np.ndarray) -> float:
    """Estimate point-to-point noise with the second difference."""
    differences = np.diff(intensities, n=2)
    return float(np.std(differences) / np.sqrt(6.0))


def merge_duplicate_energies(
    energies: np.ndarray, intensities: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Average intensities recorded at duplicate energy values."""
    unique_energies, inverse = np.unique(energies, return_inverse=True)
    if unique_energies.size == energies.size:
        return energies, intensities

    sums = np.bincount(inverse, weights=intensities)
    counts = np.bincount(inverse)
    return unique_energies, sums / counts


def main():
    """Print post-edge noise estimates for the experimental reference set."""
    path = resource_path("xasml:datasets/experimental/normalized_experimental_data.pkl")
    with open(path, "rb") as stream:
        spectra = pickle.load(stream)

    header = (
        "Compound,points,step_min_eV,step_max_eV,sigma_native,snr_native,"
        "sigma_0.1_eV,snr_0.1_eV,sigma_second_difference"
    )
    print(header)

    for compound, (energies, intensities, _) in spectra.items():
        energies = np.asarray(energies, dtype=float)
        intensities = np.asarray(intensities, dtype=float)
        mask = (energies >= POST_EDGE[0]) & (energies <= POST_EDGE[1])
        selected_energies = energies[mask]
        selected_intensities = intensities[mask]
        selected_energies, selected_intensities = merge_duplicate_energies(
            selected_energies, selected_intensities
        )
        point_steps = np.gradient(selected_energies)

        local_noise = estimate_local_linear_noise(
            selected_energies,
            selected_intensities,
            window_ev=NOISE_WINDOW,
        )
        sigma = rms_in_region(selected_energies, local_noise, *POST_EDGE)
        snr_native = 1.0 / sigma
        model_grid_noise = local_noise * np.sqrt(point_steps / MODEL_STEP)
        sigma_model = rms_in_region(selected_energies, model_grid_noise, *POST_EDGE)
        snr_model = 1.0 / sigma_model
        sigma_second = second_difference_noise(selected_intensities)

        print(
            f"{compound},{selected_energies.size},{point_steps.min():.6f},"
            f"{point_steps.max():.6f},{sigma:.8f},{snr_native:.1f},"
            f"{sigma_model:.8f},{snr_model:.1f},{sigma_second:.8f}"
        )


if __name__ == "__main__":
    main()
