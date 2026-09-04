"""A module to create a FDMNES input file and parse the output."""

import gzip
import logging
import os

import mendeleev
import numpy as np
from pymatgen.io.cif import CifParser
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

logger = logging.getLogger(__name__)


class Fdmnes:
    def __init__(self, parent_path: str, filename_prefix: str, element: str):
        self.parent_path = parent_path
        self.filename_prefix = filename_prefix
        self.element = element

        self.inp, self.out, self.bav = None, None, None
        self.data: dict = {}

    @staticmethod
    def arctan_gammas(
        x, x_cut=0.0, x_cent=0.0, x_larg=0.0, gamma_hole=0.0, gamma_max=0.0
    ):
        f = (x - x_cut) / x_cent
        a = np.pi * gamma_max * (f - 1 / f**2) / (3 * x_larg)
        gammas = gamma_hole + gamma_max * (0.5 + 1 / np.pi * np.arctan(a))

        # Set gamma to the gamma_hole below the cutoff energy.
        mask = np.where(x < x_cut)
        gammas[mask] = gamma_hole

        return gammas

    @staticmethod
    def convolve(x, y, gammas, x_cut=0.0, num=501, step=0.1):
        """A significantly faster version of the previous function, without the
        inner `for` loop. Note that the results are also slightly different, but
        the difference is negligible.
        """
        if step is None:
            raise ValueError("The convolution step must be specified.")

        # Extend the X-axis array.
        start = x[-1]
        stop = start + num * step
        x_ext = np.append(x, np.arange(start + step, stop, step))

        ids = x_ext > x_cut

        x1 = x_ext[ids]
        x1[0] = x_cut

        # Extend the intensity array by coping the last value `num - 1` times.
        y = y[x > x_cut]
        y = np.append(y, np.ones(num - 1) * y[-1])

        y_conv = np.zeros_like(x)
        for i, (xi, gamma) in enumerate(zip(x, gammas)):
            # gamma = gamma / 2.0
            lorentzian_at_xi = -(gamma / 2) / ((xi - x1) ** 2 + (gamma / 2) ** 2)
            # Multiplying by the step turns the sum into the convolution
            # integral.
            y_conv[i] = -np.sum(lorentzian_at_xi * y) / np.pi * step

        return y_conv

    def make_directory_structure(self):
        try:
            os.makedirs(self.parent_path, mode=0o755)
        except FileExistsError:
            pass

    def make_input(self, cif, **kwargs):
        cif = CifParser(cif)

        # FDMNES needs the cell of the file, not the primitive one.
        structure = cif.parse_structures(primitive=False)[0]

        # The structure read from file should be the conventional one. Here we
        # instantiate the SpacegroupAnalyzer to use it for symmetry analysis.
        try:
            spa = SpacegroupAnalyzer(structure, symprec=0.01, angle_tolerance=5)
        except ValueError as e:
            raise ValueError(f"The space group analyzer failed: {e}") from e

        # The file can use another setting of the space group. Standardize, so that the
        # cell, the sites and the space group agree.
        structure = spa.get_refined_structure()
        spa = SpacegroupAnalyzer(structure, symprec=0.01, angle_tolerance=5)

        symmetry_dataset = spa.get_symmetry_dataset()
        if symmetry_dataset is None:
            raise ValueError("The symmetry data is None.")
        group_number = symmetry_dataset.number
        group_choice = symmetry_dataset.choice

        # FDMNES doesn't recognize 2 as a space group.
        if group_number == 2:
            group_number = "P-1"

        replacements: dict = {}
        replacements.update(**kwargs)

        # The method needs to be specified only when the Green's function is
        # used.
        if replacements["method"] == "green":
            pass
        else:
            replacements["method"] = ""

        if replacements["scf"] is True:
            replacements["scf"] = "scf"
        else:
            replacements["scf"] = ""

        group = f"{group_number}"
        if group_choice:
            group += f":{group_choice}"
        replacements["group"] = group

        lattice = structure.lattice
        replacements["lattice"] = (
            f"{lattice.a:<12.8f} {lattice.b:12.8f} {lattice.c:12.8f} "
            f"{lattice.alpha:12.8f} {lattice.beta:12.8f} {lattice.gamma:12.8f}"
        )

        unique_sites = []
        for sites in spa.get_symmetrized_structure().equivalent_sites:
            sites = sorted(sites, key=lambda s: tuple(abs(x) for x in s.frac_coords))
            unique_sites.append((sites[0], len(sites)))

        sites = ""
        for i, (site, _) in enumerate(unique_sites):
            e = site.specie
            sites += (
                f"{e.Z:>2d} {site.a:12.8f} {site.b:12.8f} {site.c:12.8f} {e.name:>4s}"
            )
            if i < len(unique_sites) - 1:
                sites += "\n"
        replacements["sites"] = sites

        self.make_directory_structure()

        # Write the input file.
        filename = os.path.join(self.parent_path, f"{self.filename_prefix}_inp.txt")
        with open(filename, "w") as fp, open(kwargs["template"]) as tp:
            self.inp = tp.read().format(**replacements)
            fp.write(self.inp)

        # Write the fdmfile.txt.
        with open(os.path.join(self.parent_path, "fdmfile.txt"), "w") as fp:
            fp.write("1\njob_inp.txt")

    def make_sbatch(self, **kwargs):
        self.make_directory_structure()
        filename = os.path.join(self.parent_path, f"{self.filename_prefix}.sbatch")
        with open(filename, "w") as fp, open(kwargs["template"]) as tp:
            fp.write(tp.read().format(**kwargs))

    def parse_sites_indices(self, line):
        # ipr
        #    - non equivalent atom index in the unit cell
        #    - used to label the spectrum
        # igr
        #    - atom index in the unit cell, likely the same as in pymatgen.
        data = {}
        if self.bav is None:
            raise ValueError("The bav file must be set.")
        line = next(self.bav)
        while "-------" not in line:
            if "ipr =" in line:
                tokens = line.split()
                ipr = int(tokens[2][:-1])
                atomic_number = int(tokens[5][:-1])
                symmetry_multiplicity = int(tokens[8])
                line = next(self.bav)
                line = next(self.bav)
                line = next(self.bav)
                frac_coords = []
                while line.split():
                    tokens = line.split()
                    x, y, z = map(float, tokens[1:4])
                    frac_coords.append([x, y, z])
                    line = next(self.bav)
                data[ipr] = {
                    "atomic_number": atomic_number,
                    "symmetry_multiplicity": symmetry_multiplicity,
                    "frac_coords": np.array(frac_coords),
                }
            line = next(self.bav)

        for ipr, site_data in data.items():
            atomic_number = mendeleev.element(self.element).atomic_number
            if site_data["atomic_number"] != atomic_number:
                continue
            if ipr not in self.data["sites"]:
                self.data["sites"][ipr] = {}
            self.data["sites"][ipr].update(site_data)

    def parse_site_data(self, line):
        if self.out is None:
            raise ValueError("The output file must be set.")

        line = next(self.out)
        line = next(self.out)

        # Find the ipr for the element by looking at the sites information.
        # As soon as the atomic number matches, break the loop.
        ipr = None
        if self.data["nabsorbers"] == 1:
            if self.element is None:
                raise ValueError("The element needs to be set")
            atomic_number = mendeleev.element(self.element).atomic_number
            for ipr in self.data["sites"]:
                if self.data["sites"][ipr]["atomic_number"] == atomic_number:
                    break

        # In the case of multiple absorber sites, the ipr is given in the output.
        else:
            ipr = int(line.split("_")[-1])

        if ipr is None:
            raise ValueError("The ipr is not set")

        if ipr not in self.data["sites"]:
            self.data["sites"][ipr] = {}

        site_data = self.data["sites"][ipr]
        site_data["error"] = None

        fermi_energies = {}
        # There should be an error message for the sites, and should include the
        # site index (ipr). The error is not saved in self.data because of the
        # return statements.
        while "Energy    <xanes>" not in line:
            if "Point group not found" in line:
                site_data["error"] = "point group not found"
                return
            if "Reduce the maximum energy" in line:
                site_data["error"] = "maximum energy too large"
                return
            if "The turning point is beyond the atomic radius" in line:
                site_data["error"] = "the turning point is beyond the atomic radius"
                return
            if "Two atoms are too close" in line:
                site_data["error"] = "two atoms are too close"
                return
            if "Fermi energy =" in line:
                tokens = line.split()
                cycle = int(tokens[1][:-1])
                value = float(tokens[5])
                fermi_energies[cycle] = value
            if "Epsii used" in line:
                site_data["epsii"] = float(line.split()[3])
            # There is no error, but the calculation has not finished.
            try:
                line = next(self.out)
            except StopIteration:
                site_data["error"] = "partial output file"
                return

        line = next(self.out)

        site_data["scf"] = {}
        site_data["scf"]["fermi_energies"] = fermi_energies

        energies, intensities = [], []
        while line.split():
            if "ERROR RETURN ** FROM" in line:
                site_data["error"] = "mumps returned an error"
                return
            try:
                energy, intensity = map(float, line.split())
            except ValueError:
                site_data["error"] = "failed to parse the spectrum"
                return
            # There is no error, but the calculation has not finished.
            try:
                line = next(self.out)
            except StopIteration:
                site_data["error"] = "partial output file"
                return
            energies.append(energy)
            intensities.append(intensity)

        site_data["spectrum"] = {}
        site_data["spectrum"]["energies"] = np.array(energies)
        site_data["spectrum"]["intensities"] = np.array(intensities)

    def parse_site_convolution_parameters(self, line):
        if self.out is None:
            raise ValueError("The output file must be set.")
        data: list = []
        while line.split():
            if "E_cut" in line:
                tokens = line.split()
                e_cut = float(tokens[5][:-1])
                shift = float(tokens[8])
                data.append({"e_cut": e_cut, "shift": shift})
            try:
                line = next(self.out)
            except StopIteration:
                break

        if not data:
            self.data["error"] = "partial output file"
            return

        for i, site_data in enumerate(self.data["sites"].values()):
            if "spectrum" not in site_data:
                site_data["spectrum"] = {}
            site_data["spectrum"]["e_cut"] = data[i]["e_cut"]
            site_data["spectrum"]["shift"] = data[i]["shift"]

    def parse(self):
        # If there is an error in any place of the calculation, all the data is not
        # usable as the broadening parameters are at the very end of the output file.
        # Later edit: Actually, it might be possible to get this information
        # from the bav file.
        self.data["error"] = None
        self.data["sites"] = {}

        path = os.path.join(self.parent_path, f"{self.filename_prefix}_bav.txt.gz")

        if not os.path.isfile(path):
            self.data["error"] = "the bav file does not exist"
            return

        try:
            with gzip.open(path, "rt") as self.bav:
                for line in self.bav:
                    if "---- Symsite ----" in line:
                        self.parse_sites_indices(line)
        except (StopIteration, EOFError):
            self.data["error"] = "error reading the bav file"
            return

        path = os.path.join(self.parent_path, f"{self.filename_prefix}_out.txt")

        if not os.path.isfile(path):
            self.data["error"] = "the output file does not exist"
            return

        with open(path) as self.out:
            for line in self.out:
                if "No such file or directory" in line:
                    self.data["error"] = "partial output file"
                    return
                if "not found in the fdmnes basis" in line:
                    self.data["error"] = "space group not found"
                    return
                if "Number of calculated non equivalent absorbing atom" in line:
                    self.data["nabsorbers"] = int(line.split("=")[1])
                # Extract the data for the site.
                if "E_edge" in line:
                    self.parse_site_data(line)
                # Extract the convolution parameters.
                if "Arctangent model" in line:
                    self.parse_site_convolution_parameters(line)

    @property
    def error(self) -> str | None:
        if not self.data:
            raise ValueError("No data; the calculation must be parsed first.")
        for site_data in self.data["sites"].values():
            if "error" in site_data and site_data["error"] is not None:
                return site_data["error"]
        if "error" in self.data and self.data["error"] is not None:
            return self.data["error"]
        return None


def main():
    logging.captureWarnings(True)
    logging.basicConfig(level=logging.WARNING)

    PARENT_PATH = "/data/scisoft/xasml/materials/mp-226/Fe/job15"
    FILENAME_PREFIX = "job"
    ELEMENT = "Fe"

    # Create the FDMNES calculation object.
    calculation = Fdmnes(PARENT_PATH, FILENAME_PREFIX, element=ELEMENT)

    # Test the parsing of the FDMNES output.
    calculation.parse()


if __name__ == "__main__":
    main()
