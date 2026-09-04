# Convergence of the Fe K-edge XANES with the Radius of the Cluster

`radius_convergence.py` compares job15, job16 and job17 with the experimental
references. The three jobs differ only in the radius of the cluster: 5, 6 and 7
Angstrom. The set covers 21 compounds of the experimental database. Cordierite,
Scorzalite and Troilite have no calculation in this set.

Run the script from this directory. It writes three figures next to itself:

- `radius_convergence.png`: the spectra on the Epsii scale of the database.
- `radius_convergence_aligned.png`: the same spectra, each shifted to the position that
  minimizes the difference with the measurement.
- `radius_convergence_metrics.png`: the shifts and the residuals.

## Results

Mean of the absolute value over the 21 compounds:

| Quantity            | r = 5 | r = 6 | r = 7 |
| ------------------- | ----- | ----- | ----- |
| Epsii shift (eV)    | 3.105 | 1.995 | 1.706 |
| Residual shift (eV) | 2.071 | 4.948 | 4.643 |
| RMS, Epsii scale    | 0.143 | 0.242 | 0.225 |
| RMS, aligned        | 0.078 | 0.079 | 0.076 |

The shape of the spectrum is converged at r = 5 Angstrom. After the alignment the
residual does not depend on the radius: 0.078, 0.079 and 0.076. For 17 of the 21
compounds the three values differ by less than 0.01. Lepidocrocite (0.102, 0.108,
0.068) and Rodolicoite (0.060, 0.052, 0.049) improve at r = 7. Iron degrades a little
(0.065, 0.066, 0.075).

The Epsii scale is not transferable between the radii. For most oxides the Epsii shift
changes sign between r = 5 and r = 6. Wustite goes from +4.8 to -2.8 and -3.7 eV.
Hedenbergite goes from +5.7 to -4.4 and -3.8 eV. The energy that the Epsii scale loses
returns as a residual shift: r = 6 and r = 7 need 4 to 10 eV, r = 5 needs about 2 eV.
Iron is stable at every radius (2.15 to 2.35 eV), so `EPSII_REFERENCE = 6974.5` still
calibrates the metal. It does not place the compounds against the metal at r = 6 and
r = 7. This is the reason why the RMS on the Epsii scale gets worse with the radius
while the aligned RMS does not.

Two consequences:

1. Select the radius on the cost of the calculation. The shape of the spectrum does not
   change with the radius.
2. Repeat the calibration of the energy axis for each radius, or replace Epsii with a
   reference that does not move with the size of the cluster.
