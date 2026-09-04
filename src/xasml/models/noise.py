"""Noise estimates for one-dimensional spectra."""

import numpy as np


def estimate_local_linear_noise(
    energies: np.ndarray,
    intensities: np.ndarray,
    window_ev: float = 3.0,
) -> np.ndarray:
    """Estimate local noise from residuals around a linear fit.

    The method follows the sliding-window procedure described by Aidukas et al.
    (2026), DOI 10.1107/S1600577526001712. Each window is defined on the energy
    axis, which supports non-uniform experimental grids. The residual variance
    includes a correction for the two fitted linear parameters.

    Args:
        energies: Strictly increasing energy values in eV.
        intensities: Spectrum values on the energy grid.
        window_ev: Full width of each centred fitting window in eV.

    Returns:
        Local noise standard deviation at each energy point.

    Raises:
        ValueError: If the inputs cannot define the local linear fits.
    """
    energies = np.asarray(energies, dtype=float)
    intensities = np.asarray(intensities, dtype=float)

    if energies.ndim != 1 or intensities.ndim != 1:
        raise ValueError("The energy and intensity arrays must be one-dimensional.")
    if energies.shape != intensities.shape:
        raise ValueError("The energy and intensity arrays must have the same shape.")
    if energies.size < 3:
        raise ValueError("At least three points are required.")
    if not np.all(np.isfinite(energies)) or not np.all(np.isfinite(intensities)):
        raise ValueError("The energy and intensity arrays must contain finite values.")
    if not np.all(np.diff(energies) > 0):
        raise ValueError("The energy values must be strictly increasing.")
    if window_ev <= 0:
        raise ValueError("The window width must be positive.")

    half_width = window_ev / 2.0
    noise = np.empty_like(intensities)

    for index, energy in enumerate(energies):
        left = np.searchsorted(energies, energy - half_width, side="left")
        right = np.searchsorted(energies, energy + half_width, side="right")

        if right - left < 3:
            left = min(max(index - 1, 0), energies.size - 3)
            right = left + 3

        x_window = energies[left:right]
        y_window = intensities[left:right]
        x_scaled = x_window - np.mean(x_window)
        design = np.column_stack((x_scaled, np.ones_like(x_scaled)))
        coefficients, _, _, _ = np.linalg.lstsq(design, y_window, rcond=None)
        residuals = y_window - design @ coefficients
        degrees_of_freedom = y_window.size - design.shape[1]
        noise[index] = np.sqrt(np.sum(residuals**2) / degrees_of_freedom)

    return noise


def rms_in_region(
    energies: np.ndarray,
    values: np.ndarray,
    lower: float,
    upper: float,
) -> float:
    """Return the root-mean-square value within an energy interval.

    Args:
        energies: Energy values in eV.
        values: Values on the energy grid.
        lower: Inclusive lower energy limit in eV.
        upper: Inclusive upper energy limit in eV.

    Returns:
        Root-mean-square value in the selected interval.

    Raises:
        ValueError: If the inputs or interval are invalid.
    """
    energies = np.asarray(energies, dtype=float)
    values = np.asarray(values, dtype=float)
    if energies.shape != values.shape:
        raise ValueError("The energy and value arrays must have the same shape.")
    if lower >= upper:
        raise ValueError("The lower limit must be less than the upper limit.")

    mask = (energies >= lower) & (energies <= upper)
    if not np.any(mask):
        raise ValueError("The selected interval contains no points.")
    return float(np.sqrt(np.mean(values[mask] ** 2)))
