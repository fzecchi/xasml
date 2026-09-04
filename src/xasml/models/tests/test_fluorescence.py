import numpy as np
import pytest
from pymatgen.core.composition import Composition

from xasml.models.fluorescence import calculate_spectrum, create_binder
from xasml.models.physics import calculate_weight_fractions


def test_weight_fractions_fe2o3_bn(fe2o3):
    """Weight fractions are correct for a Fe2O3/BN mixture."""
    bn = create_binder("boron nitride")
    result = calculate_weight_fractions(fe2o3, 0.5, bn)

    w_fe_in_fe2o3 = Composition("Fe2O3").get_wt_fraction("Fe")
    assert result["Fe"] == pytest.approx(0.5 * w_fe_in_fe2o3, rel=1e-4)


def test_weight_fractions_invalid_weight_fraction(fe2o3):
    """Raises ValueError for out-of-range weight fraction."""
    bn = create_binder("boron nitride")
    with pytest.raises(ValueError, match="must be between 0.0 and 1.0"):
        calculate_weight_fractions(fe2o3, -0.1, bn)

    with pytest.raises(ValueError, match="must be between 0.0 and 1.0"):
        calculate_weight_fractions(fe2o3, 1.1, bn)


def test_fluorescence_spectrum_output_shape(fe2o3):
    """Output array has the same shape as intensity."""
    bn = create_binder("boron nitride")
    energy = np.array([7000, 7100, 7200, 7300])
    intensity = np.ones_like(energy)
    result = calculate_spectrum(
        energies=energy,
        intensity=intensity,
        compound=fe2o3,
        compound_weight_fraction=0.1,
        binder=bn,
        absorbing_element="Fe",
        phi=45.0,
        theta=45.0,
        thickness=0.1,
    )
    assert result.shape == intensity.shape


def test_fluorescence_spectrum_positive_values(fe2o3):
    """Fluorescence intensity is positive for valid inputs."""
    bn = create_binder("boron nitride")
    energy = np.array([7000, 7100, 7200, 7300])
    intensity = np.ones_like(energy)
    result = calculate_spectrum(
        energies=energy,
        intensity=intensity,
        compound=fe2o3,
        compound_weight_fraction=0.1,
        binder=bn,
        absorbing_element="Fe",
        phi=45.0,
        theta=45.0,
        thickness=0.1,
    )
    assert np.all(result > 0)


def test_fluorescence_spectrum_edge_jump(fe2o3):
    """Fluorescence intensity increases across the Fe K-edge (~7112 eV)."""
    bn = create_binder("boron nitride")
    energy = np.array([7000, 7200])
    intensity = np.array([0.001, 0.03])
    result = calculate_spectrum(
        energies=energy,
        intensity=intensity,
        compound=fe2o3,
        compound_weight_fraction=0.1,
        binder=bn,
        absorbing_element="Fe",
        phi=45.0,
        theta=45.0,
        thickness=0.1,
    )
    # Above the edge the fluorescence should be larger.
    assert result[1] > result[0]


def test_fluorescence_uses_absolute_cross_section(fe2o3):
    """The absolute cross-section scale affects the self-absorption distortion."""
    energies = np.linspace(7102, 7172, 100)
    intensity = np.linspace(0.01, 0.04, 100)
    kwargs = {
        "energies": energies,
        "compound": fe2o3,
        "compound_weight_fraction": 0.1,
        "binder": "boron nitride",
        "absorbing_element": "Fe",
        "phi": 45.0,
        "theta": 45.0,
        "thickness": 0.1,
    }

    result = calculate_spectrum(intensity=intensity, **kwargs)
    scaled_result = calculate_spectrum(intensity=2 * intensity, **kwargs)
    result /= np.trapezoid(result, energies)
    scaled_result /= np.trapezoid(scaled_result, energies)

    assert not np.allclose(result, scaled_result)


def test_create_binder_bn():
    """BN binder has the correct composition and reasonable density."""
    bn = create_binder("boron nitride")
    assert {e.symbol for e in bn.composition.elements} == {"B", "N"}
    density = float(bn.density)
    assert 1.5 < density < 3.0


def test_create_binder_cellulose():
    """Cellulose binder has C6H10O5 stoichiometry and reasonable density."""
    cellulose = create_binder("cellulose")
    elements = {e.symbol for e in cellulose.composition.elements}
    assert elements == {"C", "H", "O"}
    density = float(cellulose.density)
    assert 1.0 < density < 2.0


def test_create_binder_invalid():
    """ValueError is raised for an unknown binder name."""
    with pytest.raises(ValueError, match="Unknown binder name"):
        create_binder("unknown")
