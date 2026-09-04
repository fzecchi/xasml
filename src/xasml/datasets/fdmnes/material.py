"""A module that links the FDMNES spectrum to the local symmetry of the absorbing atom."""

import copy
import logging

import numpy as np
from pymatgen.analysis.bond_valence import BVAnalyzer  # noqa: F401
from pymatgen.analysis.chemenv.coordination_environments.coordination_geometry_finder import (
    LocalGeometryFinder,
)
from pymatgen.analysis.chemenv.coordination_environments.structure_environments import (
    LightStructureEnvironments,
)
from pymatgen.core.structure import Structure
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

from xasml.datasets.fdmnes.io import Fdmnes

logger = logging.getLogger(__name__)


class Material:
    def __init__(self, material_id, parent_path):
        self.material_id = material_id
        self.parent_path = parent_path

        path = f"{parent_path}/{material_id}/{material_id}.cif"
        self.structure = Structure.from_file(path)
        self.structure_environments = None
        self.coordination_environments = None
        self.unique_sites = None

        self.calculation = None
        self.job = None

    def get_unique_sites(self, element=None):
        try:
            spa = SpacegroupAnalyzer(self.structure, symprec=0.01, angle_tolerance=5)
        except ValueError as e:
            raise ValueError(f"The space group analyzer failed: {str(e)}") from e

        symmetry_data = spa.get_symmetry_dataset()
        equivalent_atoms_indices = sorted(set(symmetry_data.equivalent_atoms))
        self.unique_sites = {}
        if element is not None:
            for i in equivalent_atoms_indices:
                site = self.structure.sites[i]
                if site.specie.symbol == element:
                    self.unique_sites[i] = site
        else:
            for i in equivalent_atoms_indices:
                site = self.structure.sites[i]
                self.unique_sites[i] = site
        return self.unique_sites

    def determine_structure_environments(self, **kwargs):
        lgf = LocalGeometryFinder()
        lgf.setup_parameters(centering_type="standard")
        lgf.setup_structure(self.structure)

        self.structure_environments = lgf.compute_structure_environments(**kwargs)

        # The following code also passes the valences to the computation of the
        # structure environments.

        # bva = BVAnalyzer()
        # try:
        #     valences = bva.get_valences(structure=self.structure)
        # except ValueError:
        #     valences = "undefined"

        # self.structure_environments = lgf.compute_structure_environments(
        #     valences=valences, **kwargs
        # )

    def find_coordination_environments(self, strategy=None):
        lse = LightStructureEnvironments.from_structure_environments(
            strategy=strategy,
            structure_environments=self.structure_environments,
        )
        self.coordination_environments = copy.deepcopy(lse.coordination_environments)

    def parse_calculation(self, element, job):
        if self.calculation is None:
            parent_path = f"{self.parent_path}/{self.material_id}/{element}/{job}"
            self.calculation = Fdmnes(parent_path, "job", element)
            self.calculation.parse()
            self.job = job

    def get_site_spectrum(
        self,
        index,
        e_cut=0.0,
        e_cent=0.0,
        e_larg=0.0,
        gamma_hole=0.0,
        gamma_max=0.0,
        epsii_reference=None,
    ):
        if self.calculation is None:
            raise ValueError("No calculation available.")

        if not self.calculation.data:
            raise ValueError("No calculation data available.")

        # Get the site.
        if self.unique_sites is None:
            raise ValueError("Unique sites not available")

        site = self.unique_sites[index]
        frac_coords = site.frac_coords

        # Get the index from Fdmnes using the fractional coordinates.
        mapping = {}
        calc_sites = self.calculation.data["sites"]
        for calc_index in calc_sites.keys():
            for calc_frac_coords in calc_sites[calc_index]["frac_coords"]:
                if np.allclose(calc_frac_coords, frac_coords):
                    mapping[index] = calc_index

        if len(mapping) != 1:
            raise ValueError("Fractional coordinates mapping failed.")

        calc_index = mapping[index]
        data_at_calc_index = self.calculation.data["sites"][calc_index]

        symmetry_multiplicity = data_at_calc_index["symmetry_multiplicity"]
        spectrum = data_at_calc_index["spectrum"]

        energies = spectrum["energies"]
        intensities = spectrum["intensities"]
        e_cut = spectrum["e_cut"]

        intensities_normalized = intensities / symmetry_multiplicity

        gammas = self.calculation.arctan_gammas(
            energies, e_cut, e_cent, e_larg, gamma_hole, gamma_max
        )

        intensities_convolved = self.calculation.convolve(
            energies, intensities_normalized, gammas, x_cut=e_cut
        )

        element, job = self.calculation.element, self.job

        data = {}
        data["spectra"] = {}
        data["spectra"][element] = {}
        data["spectra"][element][job] = {}
        data["spectra"][element][job]["energies"] = energies
        data["spectra"][element][job]["intensities"] = intensities
        data["spectra"][element][job]["intensities_normalized"] = intensities_normalized
        data["spectra"][element][job]["intensities_convolved"] = intensities_convolved

        # Put the calculations on a common energy scale, as the Epsii keyword of
        # the convolution does. Resampled on the original grid because the loader
        # applies one energy axis to every site.
        if epsii_reference is not None:
            epsii = data_at_calc_index.get("epsii")
            if epsii is None:
                raise ValueError("No Epsii available for the site.")
            shift = epsii - epsii_reference
            data["spectra"][element][job]["intensities_convolved_shifted"] = np.interp(
                energies, energies + shift, intensities_convolved
            )
            data["spectra"][element][job]["epsii"] = epsii
            data["spectra"][element][job]["energy_shift"] = shift

        return data

    def get_site_coordination_environments_data(self, site_index):
        data = {}
        data["coordination_environments"] = {}
        ce_fractions, ce_symbols, csms = [], [], []
        if self.coordination_environments is None:
            raise ValueError("Coordination environments are not available.")
        try:
            for _, c in enumerate(self.coordination_environments[site_index]):
                ce_fractions.append(c["ce_fraction"])
                ce_symbols.append(c["ce_symbol"])
                csms.append(c["csm"])
            data["coordination_environments"]["fractions"] = ce_fractions
            data["coordination_environments"]["symbols"] = ce_symbols
            data["coordination_environments"]["csms"] = csms
        except TypeError:
            data = {}
        return data

    def get_site_structure(self, site_index):
        data = {}
        data["species"] = {}
        site = self.structure.sites[site_index]

        species = site.as_dict()["species"]
        elements, occupancies = [], []
        for _, specie in enumerate(species):
            elements.append(specie["element"])
            occupancies.append(specie["occu"])
        data["species"]["elements"] = elements
        data["species"]["occupancies"] = occupancies
        return data


if __name__ == "__main__":
    pass
