"""Functions for calculating X-ray fluorescence spectra."""

import numpy as np
import xraylib
from pymatgen.core import Lattice, Structure

from xasml.models.physics import (
    calculate_weight_fractions,
    linear_attenuation,
    mixture_density,
)

AVOGADRO = 6.02214076e23
MBARN_TO_CM2 = 1e-18


def create_binder(name: str) -> Structure:
    """Creates a pymatgen Structure for a commonly used binder material.

    Args:
        name: The name of the binder material. Valid options are "boron nitride"
            and "cellulose".

    Returns:
        A pymatgen Structure with the correct stoichiometry and density.

    Raises:
        ValueError: If the binder name is not recognized.
    """
    if name == "boron nitride":
        return Structure(
            Lattice.hexagonal(2.504, 6.661),
            ["B", "B", "N", "N"],
            [
                [1 / 3, 2 / 3, 1 / 4],
                [2 / 3, 1 / 3, 3 / 4],
                [1 / 3, 2 / 3, 3 / 4],
                [2 / 3, 1 / 3, 1 / 4],
            ],
        )
    if name == "cellulose":
        # Cubic cell with C6H10O5 stoichiometry. The lattice parameter is
        # chosen to give a density of approximately 1.5 g/cm3.
        a = 5.641
        species = ["C"] * 6 + ["O"] * 5 + ["H"] * 10
        coords = []
        for i in range(len(species)):
            x = (i % 3 + 0.5) / 3
            y = ((i // 3) % 3 + 0.5) / 3
            z = ((i // 9) + 0.5) / 3
            coords.append([x, y, z])
        return Structure(Lattice.cubic(a), species, coords)

    raise ValueError(
        f"Unknown binder name: '{name}'. Valid options are "
        "'boron nitride' and 'cellulose'."
    )


def calculate_spectrum(
    energies: np.ndarray,
    intensity: np.ndarray,
    compound: Structure,
    compound_weight_fraction: float,
    binder: Structure | str,
    absorbing_element: str,
    phi: float,
    theta: float,
    thickness: float,
    edge: str = "K_SHELL",
    emission_line: str = "KA_LINE",
    solid_angle: float = 0.03927,
) -> np.ndarray:
    """Calculates the fluorescence detected X-ray absorption spectrum.

        If = I0 * (solid_angle / (4 * pi)) * eps * mu_abs
             / (mu_tot(E) + g * mu_tot(Ef))
             * [1 - exp(-(mu_tot(E)/sin(phi) + mu_tot(Ef)/sin(theta)) * d)]

    The calculated absorption cross section is in Mbarn/atom. The tabulated
    cross sections are in cm2/g, energies are in eV, and densities are in
    g/cm3. The resulting linear attenuation coefficients are in cm-1, and the
    thickness is in cm for the exponent to be dimensionless.

    Args:
        energies: Incident photon energies in eV.
        intensity: Calculated absorption cross section in Mbarn per absorbing
            atom.
        compound: The absorbing compound.
        compound_weight_fraction: Weight fraction of the absorbing compound
            in the mixture, dimensionless (between 0 and 1).
        binder: Binder material.
        absorbing_element: Symbol of the absorbing element (e.g. "Fe").
        phi: Incident angle in degrees.
        theta: Exit angle in degrees.
        thickness: Sample thickness in cm.
        edge: The edge in xraylib notation (e.g., "K_SHELL", "L1_SHELL").
        emission_line: The emission line in xraylib notation (e.g., "KA_LINE").
        solid_angle: Solid angle of the detector in steradians. Defaults to
            0.03927 (5 circular detectors of 10 cm diameter at 1 m).

    Returns:
        Fluorescence intensity array with the same shape as intensity.

    Raises:
        ValueError: If the absorbing element is not present in the compound.
    """
    compound_elements = [e.symbol for e in compound.composition.elements]
    if absorbing_element not in compound_elements:
        raise ValueError(
            f"Element '{absorbing_element}' is not present in the compound "
            f"'{compound.composition.reduced_formula}'. "
            f"Available elements: {compound_elements}"
        )

    phi = np.radians(phi)
    theta = np.radians(theta)
    g = np.sin(phi) / np.sin(theta)

    if isinstance(binder, str):
        binder = create_binder(binder)

    total_density = mixture_density(compound, compound_weight_fraction, binder)
    weight_fractions = calculate_weight_fractions(
        compound, compound_weight_fraction, binder
    )

    z = xraylib.SymbolToAtomicNumber(absorbing_element)
    fluorescence_efficiency = xraylib.FluorYield(z, getattr(xraylib, edge))
    fluorescence_energy = xraylib.LineEnergy(z, getattr(xraylib, emission_line))

    # Weight fractions.
    absorber_weight_fraction = {absorbing_element: weight_fractions[absorbing_element]}
    background_weight_fractions = {
        k: v for k, v in weight_fractions.items() if k != absorbing_element
    }

    # Linear attenuation from the background at the incident energies.
    mu_background = linear_attenuation(
        energies, background_weight_fractions, total_density
    )

    # Linear attenuation from the total mixture at fluorescence energy.
    fluorescence_energy = np.array([fluorescence_energy * 1000.0])
    mu_total_fluorescence = linear_attenuation(
        fluorescence_energy, weight_fractions, total_density
    )

    # Convert the calculated atomic cross section to linear attenuation using
    # the number density of absorbing atoms in the mixture.
    absorber_number_density = (
        total_density
        * absorber_weight_fraction[absorbing_element]
        * AVOGADRO
        / xraylib.AtomicWeight(z)
    )
    mu_absorber_calculated = intensity * MBARN_TO_CM2 * absorber_number_density

    # Reconstruct total calculated attenuation.
    mu_total_calculated = mu_background + mu_absorber_calculated

    # Final calculation.
    prefactor = (
        (solid_angle / (4.0 * np.pi))
        * fluorescence_efficiency
        * mu_absorber_calculated
        / (mu_total_calculated + g * mu_total_fluorescence)
    )
    exponent = (
        -(mu_total_calculated / np.sin(phi) + mu_total_fluorescence / np.sin(theta))
        * thickness
    )

    result = prefactor * (1.0 - np.exp(exponent))

    return result
