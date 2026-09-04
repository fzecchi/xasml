import numpy as np
import pytest

from xasml.models.noise import (
    estimate_local_linear_noise,
    rms_in_region,
)


def test_local_linear_noise_recovers_injected_noise():
    rng = np.random.default_rng(42)
    energies = np.arange(0.0, 100.1, 0.1)
    expected = 0.02
    intensities = 1.0 + 0.002 * energies + rng.normal(0.0, expected, energies.size)

    noise = estimate_local_linear_noise(energies, intensities, window_ev=3.0)

    assert rms_in_region(energies, noise, 10.0, 90.0) == pytest.approx(
        expected, rel=0.05
    )


def test_local_linear_noise_supports_nonuniform_grid():
    energies = np.array([0.0, 0.5, 1.2, 2.0, 3.1, 4.5])
    intensities = 2.0 * energies + 1.0

    noise = estimate_local_linear_noise(energies, intensities)

    assert noise == pytest.approx(0.0, abs=1e-14)


def test_local_linear_noise_rejects_unsorted_grid():
    with pytest.raises(ValueError, match="strictly increasing"):
        estimate_local_linear_noise(np.array([0.0, 2.0, 1.0]), np.ones(3))
