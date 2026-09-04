# Checklist: does the spectrum correspond to the structure?

Goal: for each compound folder, establish how confident we are that the experimental Fe K-edge spectrum was measured on the phase described by the structure files, and state that confidence (high, medium, low) with the evidence in the top-level `README.md`. Work through the four parts in order; the structure and the spectrum have to be right on their own before they can be compared.

## 1. The structure is the phase we claim

1. COD files: take the space group from the CIF tags (`_symmetry_space_group_name_H-M`, `_space_group_IT_number`) and the Fe site point group from the symmetry operations in the CIF applied to the Fe position; no tolerance-based detection. MP files: detect the space group and site symmetry at symprec 0.01 and compare with the experimental one. For both, recompute lattice parameters, number of inequivalent Fe sites with Wyckoff letter, coordination number, and Fe-ligand distance range, and compare with the table.
2. Check that the file is ordered (no partial occupancies) and that the formula matches the compound. When the only ordered file is an idealized model (old refinement, ideal end-member), say so and name the modern refinements it stands for.
3. Keep one or two COD files per compound, each with an ICSD ID that links to the MP entry. Verify the link, do not infer it from the numbering: compare the COD cell and coordinates with the original ICSD entry mirrored in AFLOW (`aflowlib.duke.edu/AFLOWDATA/ICSD_WEB/<lattice>/<formula>_ICSD_<id>/`, fields `geometry_orig` and `aflow_prototype_params_values_orig`), and check that the paper is in the MP provenance references (`MPRester().materials.provenance.search`). Remove old, low-quality or unlinked entries. State the verification in a note.
4. Temperature, pressure and reference: take them from the CIF tags if present; if absent, note that they come from the paper.
5. Flag any structure that is not the phase present at the measurement conditions (high pressure, low temperature, doped) or that MP marks as theoretical, and say which file to use for the comparison with the spectrum.
6. Site distribution. When Fe sits on more than one site in the real material, or substitutes on a site with other cations, state the fraction of Fe on the site named in the README and how that affects the comparison.

## 2. The spectrum is what the file says it is

7. Read the header and deposit metadata: beamline, date, mode, reference channel, mono $d$ spacing, processing already applied (rebinned, normalized, scaled columns), header notes. Give the mode and $\mu x$ per file. Do not report edge jump, noise, glitches, $I_0$ drift, duplicated points, or the number of scans.
8. Verify the energy axis.
   - Foil channel present: derivative maximum of the foil. State the shift only if one is needed; if the foil is already at 7112.0 eV, say that the axis is calibrated and nothing more.
   - No foil channel: use a foil from the `Iron/` folder measured on the same beamline and day; if none is there, copy it from `databases/` into `Iron/` and add it to the Iron README. Never use a proxy from another beamline or year. If no such foil exists, say that the axis is unverified and state a tolerance ("within 0.5 eV"); do not claim the axis is correct.
9. Give $E_0$ from the derivative only when it has one clear peak, otherwise list the maxima; give the pre-edge position. Quote a pre-edge height only as a relative comparison between measurements (step 13).
10. Scan range: say when the scan is too short for a standard normalization or for EXAFS, and how the comparison script normalizes it.

## 3. The spectrum belongs to the structure

11. Sample identity. From the header, deposit metadata and supplier information: formula, natural or synthetic, supplier and lot, preparation, characterization (PXRD, EPMA) if the database gives any. A natural mineral with variable composition, or a commercial product named only by formula ("iron(III) phosphate") with no stated polymorph or hydration, lowers the confidence.
12. Phase and polymorph. List the polymorphs and hydrates with the same nominal formula and say which spectral features distinguish them from the structure in the folder. If nothing in the file tells them apart, say so.
13. Spectral class. Compare $E_0$ and the pre-edge position and relative intensity (strong or weak) with the expected values for the oxidation state and site (Fe$^{2+}$ versus Fe$^{3+}$, centrosymmetric versus not, tetrahedral versus octahedral). A spectrum of the wrong class (for example a weak pre-edge at 7114.5 eV and $E_0$ near 7128 eV for a supposed tetrahedral Fe$^{3+}$ phosphate) does not enter the folder.
14. Cross-check between independent measurements. When two or more files exist, overlay them on the same shifted axis and compare $E_0$, pre-edge position and relative height, and the positions of the main XANES maxima. Report differences larger than 0.3 eV in position or 20% in pre-edge height, and state which measurement is the reference and why.
15. Literature and simulated spectra. Compare the pre-edge and XANES with a published spectrum of the same phase when one exists (give the reference), and with an FDMNES or FEFF calculation from the structure in the folder when the compound is otherwise unverified. Say which features agree and which do not.
16. EXAFS consistency, when the scan is long enough: a first-shell fit or a qualitative comparison of the first-shell distance with the structure (tetrahedral Fe-O about 1.9 to 2.0 Å, octahedral about 2.0 to 2.2 Å).

## 4. Confidence and writing

17. State the confidence level in the `Confidence` column of the structure table in the top-level `README.md`, and the evidence in the entry for the compound under `Confidence in the spectrum-structure correspondence`. Do not repeat the grade in the compound README:
    - High: synthetic or well-characterized sample of a stoichiometric phase, single Fe site, spectral class consistent with the structure, and at least one independent measurement or a published spectrum that agrees.
    - Medium: one of the above is missing (natural sample with substitution, one measurement only, no literature comparison), but the spectral class matches and no feature contradicts the structure.
    - Low: sample identity or polymorph is uncertain, or the measurement disagrees with the reference in position, pre-edge height or shape. Keep the file only if the entry explains what it is good for.
18. Terse bullets, no labels such as "Grid:" or "Signal:", no point counts or step lists, no repetition of what the tables already say. Do not write "do not shift" or similar when no action is needed.
19. Do not edit a number you did not recompute; do not recommend a shift unless step 8 supports it.
