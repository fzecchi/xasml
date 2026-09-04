# Experimental dataset: iron mineral structures and spectra

This dataset provides crystallographic space groups, macroscopic crystal point groups (crystal classes), and local iron site symmetries for the core iron mineral standards, together with a confidence grade for the correspondence between each recommended Fe K-edge spectrum and the structure files. The structure table compares experimental structures from the Crystallography Open Database (COD) with DFT-relaxed cells from the Materials Project (MP). Confidence follows the criteria of `CHECKLIST.md` step 17. Verification date 2026-08-21.

---

## Structures and confidence

| # | Compound | Formula | Fe Oxidation State | Fe Ligands | COD Reference | MP Entry | COD Fe Site Point Group | MP Fe Site Point Group | Δd(Fe-X) (MP vs COD) | Confidence |
| :-: | :--- | :--- | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: |
| 1 | **Aegirine** | $\text{NaFeSi}_2\text{O}_6$ | 3+ | 6 O | `cod_9013272.cif` (McCarthy 2008) | `mp-21867.cif` | $2$ ($C_2$) | $2$ ($C_2$) | $+0.028\text{ \AA}$ | Medium |
| 2 | **Andradite** | $\text{Ca}_3\text{Fe}_2(\text{SiO}_4)_3$ | 3+ | 6 O | `cod_2101484.cif` (Pilati 1996) | `mp-6672.cif` | $\bar{3}$ ($S_6$) | $\bar{3}$ ($S_6$) | $+0.026\text{ \AA}$ | Medium |
| 3 | **Chalcopyrite** | $\text{CuFeS}_2$ | 3+ | 4 S | `cod_9007572.cif` (Hall & Stewart 1973) | `mp-3497.cif` | $\bar{4}$ ($S_4$) | $\bar{4}$ ($S_4$) | $-0.023\text{ \AA}$ | High |
| 4 | **Cordierite** | $(\text{Mg},\text{Fe})_2\text{Al}_4\text{Si}_5\text{O}_{18}$ | 2+ | 6 O | `cod_1548717.cif` (Haefeker 2014) | `mp-1204107.cif` | $2$ ($C_2$) | $2$ ($C_2$) | $+0.030\text{ \AA}$ | Low |
| 5 | **Epidote** | $\text{Ca}_2\text{Al}_2\text{Fe}(\text{SiO}_4)(\text{Si}_2\text{O}_7)\text{O}(\text{OH})$ | 3+ | 6 O | `cod_1529622.cif` (Belov 1953) | `mp-696825.cif` | $m$ ($C_s$) | $m$ ($C_s$) | $+0.044\text{ \AA}$ | Medium |
| 6 | **Goethite** | $\alpha\text{-FeO(OH)}$ | 3+ | 3 O, 3 OH | `cod_2211652.cif` (Yang 2006) | `mp-605437.cif` | $m$ ($C_s$) | $m$ ($C_s$) | $+0.011\text{ \AA}$ | High |
| 7 | **Hedenbergite** | $\text{CaFeSi}_2\text{O}_6$ | 2+ | 6 O | `cod_9010468.cif` (Nestola 2008) | `mp-18890.cif` | $2$ ($C_2$) | $2$ ($C_2$) | $+0.029\text{ \AA}$ | Medium |
| 8 | **Hematite** | $\alpha\text{-Fe}_2\text{O}_3$ | 3+ | 6 O | `cod_2101167.cif` (Maslen 1994) | `mp-19770.cif` | $3$ ($C_3$) | $3$ ($C_3$) | $+0.015\text{ \AA}$ | High |
| 9 | **Humboldtine** | $\text{FeC}_2\text{O}_4 \cdot 2\text{H}_2\text{O}$ | 2+ | 6 O | `cod_9017265.cif` (Echigo 2008) | `mp-698316.cif` | $2$ ($C_2$) | $1$ ($C_1$)* | $+0.031\text{ \AA}$ | Medium |
| 10 | **Ilmenite** | $\text{FeTiO}_3$ | 2+ | 6 O | `cod_9000906.cif` (Wechsler 1984) | `mp-19417.cif` | $3$ ($C_3$) | $3$ ($C_3$) | $-0.051\text{ \AA}$ | Medium |
| 11 | **Iron** | $\text{Fe}$ | 0 | 8 Fe | `cod_9008536.cif` (Wyckoff 1963) | `mp-13.cif` | $m\bar{3}m$ ($O_h$) | $m\bar{3}m$ ($O_h$) | $-0.003\text{ \AA}$ | High |
| 12 | **Jarosite** | $\text{KFe}_3(\text{SO}_4)_2(\text{OH})_6$ | 3+ | 4 OH, 2 O | `cod_1557931.cif` (Mills 2013) | `mp-1192851.cif` | $2/m$ ($C_{2h}$) | $2/m$ ($C_{2h}$) | $+0.034\text{ \AA}$ | Medium |
| 13 | **Lepidocrocite** | $\gamma\text{-FeO(OH)}$ | 3+ | 4 O, 2 OH | `cod_1011026.cif` (Ewing 1935) | `mp-696580.cif` | $m2m$ ($C_{2v}$) | $m$ ($C_s$)* | $+0.050\text{ \AA}$ | High |
| 14 | **Pyrite** | $\text{FeS}_2$ | 2+ | 6 S | `cod_5000115.cif` (Brostigen 1969) | `mp-226.cif` | $\bar{3}$ ($S_6$) | $\bar{3}$ ($S_6$) | $-0.006\text{ \AA}$ | Medium |
| 15 | **Rodolicoite** | $\text{FePO}_4$ | 3+ | 4 O | `cod_9012512.cif` (Long 1983) | `mp-19109.cif` | $2$ ($C_2$) | $2$ ($C_2$) | $+0.016\text{ \AA}$ | Medium |
| 16 | **Scorodite** | $\text{FeAsO}_4 \cdot 2\text{H}_2\text{O}$ | 3+ | 4 O, 2 H2O | `cod_2212542.cif` (Xu 2007) | `mp-543041.cif` | $1$ ($C_1$) | $1$ ($C_1$) | $+0.026\text{ \AA}$ | Medium |
| 17 | **Scorzalite** | $\text{FeAl}_2(\text{PO}_4)_2(\text{OH})_2$ | 2+ | 6 O | `cod_9007451.cif` (Lindberg & Christ 1959) | no entry | $\bar{1}$ ($C_i$) | no entry | - | Medium |
| 18 | **Siderite** | $\text{FeCO}_3$ | 2+ | 6 O | `cod_5000036.cif` (Effenberger 1981) | `mp-18969.cif` | $\bar{3}$ ($S_6$) | $\bar{3}$ ($S_6$) | $-0.018\text{ \AA}$ | Medium |
| 19 | **Staurolite** | $\text{Fe}_2\text{Al}_9\text{Si}_4\text{O}_{23}(\text{OH})$ | 2+ | 4 O | `cod_2310641.cif` (Náray-Szabó 1958) | `mp-744386.cif` | $m$ ($C_s$) | $m$ ($C_s$) | $+0.103\text{ \AA}$ | Medium |
| 20 | **Tetrachloroferrate** | $[\text{N}(\text{C}_2\text{H}_5)_4][\text{FeCl}_4]$ | 3+ | 4 Cl | `cod_2019519.cif` (Lutz 2014) | `mp-1194614.cif` | $3m$ ($C_{3v}$) | $1$ ($C_1$)* | $+0.014\text{ \AA}$ | Medium |
| 21 | **Triphylite** | $\text{LiFePO}_4$ | 2+ | 6 O | `cod_2100916.cif` (Streltsov 1993) | `mp-19017.cif` | $m$ ($C_s$) | $m$ ($C_s$) | $-0.015\text{ \AA}$ | Medium |
| 22 | **Troilite** | $\text{FeS}$ | 2+ | 6 S | `cod_9004034.cif` (Skála 2006) | `mp-2779.cif` | $1$ ($C_1$) | $1$ ($C_1$)* | $-0.030\text{ \AA}$ | Low |
| 23 | **Wolframite** | $\text{FeWO}_4$ | 2+ | 6 O | `cod_9000223.cif` (Escobar 1971) | `mp-19421.cif` | $2$ ($C_2$) | $2$ ($C_2$) | $+0.003\text{ \AA}$ | Medium |
| 24 | **Wüstite** | $\text{FeO}$ | 2+ | 6 O | `cod_9009766.cif` (Fjellvåg 1996) | `mp-18905.cif` | $m\bar{3}m$ ($O_h$) | $m\bar{3}m$ ($O_h$) | $-0.032\text{ \AA}$ | Medium |

Notes on the structures:

- COD site point groups follow from the symmetry operations written in the CIF and the Fe position, without tolerance-based detection. MP site point groups come from `spglib` at `symprec = 0.01`.
- Each compound folder keeps one or two COD entries whose ICSD ID links to the Materials Project entry (see the README of each compound). Where there are two, the table uses the most recent refinement.
- The Fe-X distance is the mean over the first coordination shell.
- **Lepidocrocite.** At `symprec = 0.01`, the DFT-relaxed cell shows a small monoclinic distortion, which gives Fe site symmetry $m$ ($C_s$). It recovers the experimental $Cmcm$ symmetry with Fe site symmetry $m2m$ ($C_{2v}$) at `symprec = 0.05` or looser.
- **Troilite.** At `symprec = 0.01`, the DFT-relaxed cell shows a small triclinic distortion, which gives Fe site symmetry $1$ ($C_1$). It recovers the experimental $P\bar{6}2c$ supercell symmetry with Fe site symmetry $1$ ($C_1$) at `symprec = 0.05` or looser.
- **Humboldtine.** At `symprec = 0.01`, the DFT-relaxed cell shows a small triclinic distortion, which gives Fe site symmetry $1$ ($C_1$). It recovers the experimental $C2/c$ symmetry with Fe site symmetry $2$ ($C_2$) at `symprec = 0.05` or looser.
- **Scorzalite.** The Materials Project has no scorzalite entry; `mp-1199432` is paravauxite and was removed from the folder.
- **Tetrachloroferrate.** The COD entry is the room-temperature $P6_3mc$ phase (Fe on the threefold axis), the phase present when the spectrum was measured; the Materials Project entry is the ordered 110 K $Pca2_1$ phase, where Fe has no site symmetry. The distance difference compares these two phases.
- **Staurolite.** Both structures are the ordered ideal end-member with Fe only on the tetrahedral T2 site; natural staurolite also carries 10 to 20% of its Fe on octahedral sites.

---

## Confidence in the spectrum-structure correspondence

The grade states how sure we are that the recommended Fe K-edge spectrum was measured on the phase described by the structure files. High requires all four conditions of `CHECKLIST.md` step 17: a synthetic or well-characterized sample of a stoichiometric phase, a single Fe site, a spectral class consistent with the structure, and at least one independent measurement or published spectrum that agrees. Medium misses exactly one condition, while the spectral class matches and no feature contradicts the structure. Low means the sample identity is uncertain or the spectrum contradicts the claimed phase. Counts: High 5, Medium 17, Low 2.

How the grades were established:

- Structures: space group from the CIF tags, symmetry detection with `spglib` at the stated `symprec`, Fe site point groups from the CIF symmetry operations. Cells, Wyckoff sites, coordination numbers and Fe-ligand distances recomputed with `pymatgen`; ICSD lists, stability and `material_id` read from the MP JSON files. AFLOW mirrors of eight ICSD entries were compared with the claimed cells. MP provenance references were not re-queried, because that check needs an API key.
- Spectra: every file reprocessed with the same larch pipeline as its `spectra_comparison.py`, and every foil derivative maximum, shift, $E_0$, pre-edge position and relative height recomputed. XASDB duplicates were compared column by column against the originals.
- Sample identity: header and deposit metadata read for every recommended spectrum, with the identification lines quoted in the compound README.
- Each grade was tested twice, once adversarially and once for checklist literalism, so that no condition is imported or ignored.

### High

- **Chalcopyrite.** BM08-LISA at 80 K and IDEAS at RT, both foil-calibrated, agree within $0.2\text{ eV}$ in $E_0$ ($7119.9$, $7120.0\text{ eV}$) and pre-edge ($7113.2$, $7113.4\text{ eV}$). The strong pre-edge is what the non-centrosymmetric tetrahedral Fe$^{3+}$ site requires.
- **Goethite.** Five usable measurements from four beamlines lie on a common axis within $0.3\text{ eV}$ and reproduce the split edge ($7124$, $7128\text{ eV}$) and the $7115.0\text{ eV}$ pre-edge. The M9 natural-mineral outlier, with a white line $2\text{ eV}$ high on an unresolved $1.2\text{ eV}$ grid, is excluded from the recommendation.
- **Hematite.** Calibrated measurements from five beamlines agree, and the $0.08\text{ eV}$ GILDA scan resolves the crystal-field pre-edge doublet at $7114.0$ and $7115.1\text{ eV}$. The 2011 APS axis problems are quantified and those scans are set aside.
- **Iron.** Elemental reference foil measured at five beamlines, with every axis offset quantified against M1 (M2 sits $1.1\text{ eV}$ below, $7111.9$ against $7110.8\text{ eV}$). The metallic edge with EXAFS beyond $7900\text{ eV}$ confirms the class.
- **Lepidocrocite.** The BMM scan and two independent CLS pairs agree after the stated shifts and reproduce the equal-height pre-edge doublet at $7113.8$ and $7115.0\text{ eV}$.

### Medium

Each entry states what holds, then what is missing for High.

- **Aegirine.** Weak $7115.0\text{ eV}$ pre-edge on the non-centrosymmetric M1 octahedron and a split Fe$^{3+}$ edge, foil-calibrated. Missing: one measurement, and the header does not say whether the specimen is natural or synthetic.
- **Andradite.** Centrosymmetric Fe$^{3+}$ with a pre-edge plateau at $7114$ to $7115\text{ eV}$ and derivative maxima at $7123$ and $7128\text{ eV}$; the structure link is verified down to the AFLOW mirror. Missing: one measurement, no published comparison.
- **Epidote.** Visible $7114.7\text{ eV}$ pre-edge for the non-centrosymmetric M3 site, split edge. Missing: one dilute measurement of unstated origin, and natural epidote carries less than 1 Fe per formula unit with Al-Fe disorder, so the end-member structures are an idealization.
- **Hedenbergite.** Two measurements agree, which secures the axis and the lineshape. Missing: both samples are natural with likely substitutions, the BMM edge step is only $0.04$, and the FAME scan has no foil channel ($0.3\text{ eV}$ tolerance).
- **Humboldtine.** One Fe site (`4e` in $C2/c$), pre-edge plateau at $7112.5$ to $7113.5\text{ eV}$, equal double maxima at $7121$ and $7125\text{ eV}$, and two independent calibrated measurements that agree. Missing: no file documents a synthetic sample. M1 gives only the formula and a courtesy line, M2 gives `FeC2O4` with no hydration state, and the synthetic tag in the structure table describes the Echigo and Kimata (2008) crystallographic sample, not the measured powders.
- **Ilmenite.** Fe$^{2+}$ edge at $7121.9\text{ eV}$ with an unresolved $1s \rightarrow 3d$ shoulder. Missing: one measurement of a specimen of unknown origin, and natural ilmenite commonly carries Mg, Mn and hematite exsolution.
- **Jarosite.** Centrosymmetric Fe$^{3+}$ with a weak $7114.0\text{ eV}$ pre-edge and $E_0$ at $7128.5\text{ eV}$, a verified $+1.0\text{ eV}$ foil shift, and a PXRD pattern referenced in the header. Missing: one measurement, at 77 K on BIOXAS-S, with no supplier metadata and no independent check.
- **Pyrite.** Low-spin Fe$^{2+}$ sulfide with the edge at $7117.0\text{ eV}$ and a pre-edge plateau at $7112.5$ to $7113.5\text{ eV}$. Missing: one measurement without a reference channel; the axis rests on a same-day foil and a magnetite cross-check and is good to $\pm0.5\text{ eV}$.
- **Rodolicoite.** The BMM measurement is emphatic for the structure, with the strong $7114.4\text{ eV}$ pre-edge of tetrahedral Fe$^{3+}$ on a calibrated axis. Missing: the only cross-check is a commercial sample that fails purity (pre-edge 40% weaker, no $7127\text{ eV}$ shoulder, unverified axis), for a phase with known hydrated and amorphous look-alikes.
- **Scorodite.** Fe$^{3+}$ octahedron without symmetry, visible $7114.5\text{ eV}$ pre-edge, split edge maxima at $7125$ and $7128.5\text{ eV}$, calibrated axis. Missing: one measurement, no independent check, no sample metadata.
- **Scorzalite.** Centrosymmetric Fe$^{2+}$ with a single $E_0$ at $7121.3\text{ eV}$ and no resolved pre-edge. Missing: a natural sample with Mg on the Fe site, one measurement, and a single 1959 photographic refinement. The low end of Medium, but nothing contradicts the structure.
- **Siderite.** Recomputed derivative maxima: M1 $7122.8\text{ eV}$ after the $+0.41\text{ eV}$ foil shift, M2 $7123.25\text{ eV}$, M3 $7122.5\text{ eV}$. The foil-calibrated pair M1 and M3 agrees within $0.31\text{ eV}$; the three-way spread is $0.75\text{ eV}$, because M2 rests on a same-day foil. Missing: no characterized end-member sample. The FAME deposit reads "Pellet of natural siderite FeCO3 mixed with BN" from a mineral collection, and its oxide table is the ideal composition computed from the formula, not an analysis. Natural siderite commonly carries Mg, Mn and Ca on the Fe site.
- **Staurolite.** Strong $7112.6\text{ eV}$ pre-edge and the low edge of tetrahedral Fe$^{2+}$. Missing: one measurement, and 10 to 20% of the Fe in natural staurolite sits on octahedral sites while both structures are the ordered end member. The dominant site still matches.
- **Tetrachloroferrate.** Synthetic, CAS-identified, single site, with the strong $7114.1\text{ eV}$ pre-edge of tetrahedral Fe$^{3+}$. Missing: a single 1983 scan that ends $25\text{ eV}$ above the edge with non-standard normalization, and the axis comes from a separate same-day foil scan ($+9.4\text{ eV}$).
- **Triphylite.** Fe$^{2+}$ octahedron with $E_0$ at $7120.0\text{ eV}$ and a pre-edge plateau, calibrated axis, and a header that gives preparation and temperature. Missing: one measurement, no provenance or polymorph statement.
- **Wolframite.** Fe$^{2+}$ octahedron with the derivative maximum at $7123.5\text{ eV}$ and an unresolved weak pre-edge, on a $0.1\text{ eV}$ grid with a verified $+0.8\text{ eV}$ shift. Missing: a natural (Fe,Mn)WO$_4$ sample with an unknown Mn fraction, measured once.
- **Wüstite.** Six synthetic samples from four beamlines lie within $0.5\text{ eV}$ of M1, an NNLS fit against Fe$_3$O$_4$, Fe$_2$O$_3$ and Fe metal finds no contamination, and the HERFD offset reproduces at $0.9\text{ eV}$ with $2.4\text{ eV}$ broadening. Missing: the structural target is an idealization. Both structure files describe ideal rock-salt FeO, while real wüstite is Fe$_{1-x}$O with $x \gtrsim 0.04$, cation vacancies and Fe$^{3+}$ in defect clusters, and no file documents a vacancy fraction or a diffraction pattern for any of the six samples.

### Low

- **Cordierite.** The measured sample is not the phase of the structures: the header names a natural (Mg,Fe) cordierite while both structure files are the Fe end member. The edge step is $0.09$ on a pellet absorbing $1.5$, so the normalized amplitudes are unreliable. Usable for energies only, with a sharp $E_0$ at $7125.8\text{ eV}$ on a calibrated axis.
- **Troilite.** The spectrum is not FeS. Both channels of the single SXRMB measurement match Fe$^{3+}$ oxides: hematite gives RMS $0.087$ at a $-0.82\text{ eV}$ shift, FeO needs $+3\text{ eV}$, and pyrite fits worst (RMS $0.145$). The pre-edge sits near $7114\text{ eV}$ and the edge lies far above a sulfide edge. The axis is unverifiable. Kept only as a documented negative example.

### Corrections applied to the folders

- Scorodite: the foil derivative maximum recomputes to $7112.0\text{ eV}$, not $7111.8\text{ eV}$. The $+0.2\text{ eV}$ shift was removed and the maxima restated on the calibrated axis.
- Pyrite: the edge jump, noise, glitch, $I_0$ drift and scan-count notes and the shift instruction were removed (steps 7, 9, 18); the pre-edge was restated as a plateau, the step growth above $7132\text{ eV}$ corrected, and the magnetite path corrected to `databases/`.
- Iron: the M2 offset is $1.1\text{ eV}$ below M1, not $1.2\text{ eV}$.
- Foil shifts restated to the recomputed values where they differed by $0.02\text{ eV}$ or more: Andradite $+0.40$, Cordierite $+0.41$, Epidote $+0.41$, Humboldtine $+0.41$, Ilmenite $+0.41$, Scorzalite $+0.40$, Siderite $+0.41$, Goethite M8 $7111.8\text{ eV}$ and $+0.2\text{ eV}$.
- Jarosite: the figure legend read "IDEAS, CLS, RT" while the measurement is BIOXAS-S at 77 K. The legend was corrected and the figure regenerated.

### Open items

- Hematite: the M4 axis problem is stated in the compound README but not resolved. M4 is not the recommended spectrum.
- Hedenbergite: the compound README dates the FAME scan 2016, while the SSHADE dataset identifier and the same-day foil are dated 2017-07-06.
