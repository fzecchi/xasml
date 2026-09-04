"""Functions for X-ray physics calculations."""

from functools import lru_cache

import numpy as np
import xraylib
from pymatgen.core import Composition
from pymatgen.core.structure import Structure


def calculate_weight_fractions(
    compound: Structure,
    compound_weight_fraction: float,
    binder: Structure,
) -> dict[str, float]:
    """Calculates elemental weight fractions for a mixture with a binder."""
    if not (0.0 <= compound_weight_fraction <= 1.0):
        raise ValueError(
            f"Compound weight fraction ({compound_weight_fraction}) "
            "must be between 0.0 and 1.0."
        )

    compound: Composition = compound.composition
    binder: Composition = binder.composition
    binder_weight_fraction = 1.0 - compound_weight_fraction

    elements = set(compound.elements) | set(binder.elements)

    result = {}
    for element in elements:
        weight_fraction_in_compound = (
            compound.get_wt_fraction(element) if element in compound.elements else 0.0
        )
        weight_fraction_in_binder = (
            binder.get_wt_fraction(element) if element in binder.elements else 0.0
        )
        result[element.symbol] = (
            compound_weight_fraction * weight_fraction_in_compound
            + binder_weight_fraction * weight_fraction_in_binder
        )

    return result


def mixture_density(
    compound: Structure,
    compound_weight_fraction: float,
    binder: Structure,
) -> float:
    """Calculates the density of the mixture."""
    binder_weight_fraction = 1.0 - compound_weight_fraction
    compound_density = float(compound.density)
    binder_density = float(binder.density)
    return 1.0 / (
        compound_weight_fraction / compound_density
        + binder_weight_fraction / binder_density
    )


@lru_cache(maxsize=None)
def total_mass_attenuation_coefficient(symbol: str, energies: bytes) -> np.ndarray:
    """Retrieve the total mass attenuation coefficient for an element at energies."""
    z = xraylib.SymbolToAtomicNumber(symbol)
    energies_as_array = np.frombuffer(energies, dtype=np.float64)
    # CS_Total returns mass attenuation coefficient despite the name acronym
    # standing for cross section. The units are cm2/g.
    return np.array([xraylib.CS_Total(z, float(e) / 1000.0) for e in energies_as_array])


def linear_attenuation(
    energies: np.ndarray,
    weight_fractions: dict[str, float],
    density: float,
) -> np.ndarray:
    """Calculates the linear attenuation coefficient of a mixture."""
    total_mass_attenuation = np.zeros_like(energies, dtype=np.float64)
    energies_as_bytes = energies.astype(np.float64).tobytes()

    for symbol, weight_fraction in weight_fractions.items():
        mass_attenuation = total_mass_attenuation_coefficient(symbol, energies_as_bytes)
        total_mass_attenuation += float(weight_fraction) * mass_attenuation

    return density * total_mass_attenuation
