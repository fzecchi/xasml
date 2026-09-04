# Databases: Summary of Remaining Compounds and Files

This document summarizes all remaining compound data, CIF files, and XAS spectra in the `databases/` directory.

---

## 1. Single-Site Iron Compounds

These compounds possess one symmetry-inequivalent iron site:

| Compound / Mineral | Formula | Fe Oxidation State | Fe Site Symmetry & Wyckoff | Available Files in `databases/` |
| :--- | :--- | :---: | :---: | :--- |
| **Almandine** | $\text{Fe}_3\text{Al}_2(\text{SiO}_4)_3$ | 2+ | $222$ ($D_2$, $24c$) | `NIST/Fe-Almandine.xdi` |
| **Augite** | $\text{Ca}(\text{Mg},\text{Fe})\text{Si}_2\text{O}_6$ | 2+ | $2$ ($C_2$, $4e$) | `NIST/Fe-Augite.xdi`, `COD/cod_9009664.cif` |
| **Carpholite** | $\text{FeAl}_2\text{Si}_2\text{O}_6(\text{OH})_4$ | 2+ | $2$ ($C_2$, $8f$) | `NIST/Fe-K-Carpholite.xdi`, `XASDB/Carpholite_idn2wd2b.dat`, `COD/cod_9009381.cif` |
| **Petedunnite** | $\text{Ca}(\text{Zn},\text{Fe})\text{Si}_2\text{O}_6$ | 2+ | $2$ ($C_2$, $4e$) | `NIST/Fe-K-Petedunnite.xdi`, `COD/cod_9010858.cif` |
| **Phosphosiderite** | $\text{FePO}_4 \cdot 2\text{H}_2\text{O}$ | 3+ | $1$ ($C_1$, $4e$) | `XASDB/Iron (III) Phospahte-x2H2O_id3q20lp.dat`, `COD/cod_9000140.cif` |
| **Heterosite** | $\text{FePO}_4$ | 3+ | $m$ ($C_s$, $4c$) | `COD/cod_9015219.cif` |

---

## 2. Multi-Site Iron Compounds

These compounds possess two or more distinct crystallographic iron sites:

| Compound / Mineral | Formula | Inequivalent Fe Sites | Available Files in `databases/` |
| :--- | :--- | :---: | :--- |
| **Axinite / ferro-Axinite** | $\text{Ca}_2\text{FeAl}_2\text{BSi}_4\text{O}_{15}(\text{OH})$ | 2 sites | `COD/cod_9000815.cif`, `NIST/Fe-ferro-Axinite.xdi`, `XASDB/Axinite_idnslp4y.dat` |
| **Bustamite** | $\text{CaFeSi}_2\text{O}_6$ | 4 sites | `COD/cod_8103622.cif`, `NIST/Fe-K-Bustamite.xdi`, `XASDB/Bustamite_idfx2qly.dat` |
| **Chondrodite** | $(\text{Mg},\text{Fe})_5(\text{SiO}_4)_2(\text{OH})_2$ | 3 sites | `COD/cod_9000654.cif`, `NIST/Fe-Chondrodite.xdi` |
| **Cohenite** | $\text{Fe}_3\text{C}$ | 2 sites ($8d + 4c$) | `COD/cod_1008725.cif`, `XASLIB/Fe3C_rt_01.xdi` |
| **Diadochite** | $\text{Fe}_2(\text{PO}_4)(\text{SO}_4)(\text{OH}) \cdot 5\text{H}_2\text{O}$ | 2 sites | `COD/cod_9009236.cif`, `NIST/Fe-Diadochite.xdi` |
| **Fayalite** | $\text{Fe}_2\text{SiO}_4$ | 2 sites ($4a + 4c$) | `COD/cod_9000469.cif`, `NIST/Fe-Fayalite.xdi` |
| **Ferrihydrite** | $\text{Fe}_5\text{O}_7(\text{OH}) \cdot 4\text{H}_2\text{O}$ | 3 sites | `COD/cod_9011571.cif`, `NIST/Fe-Ferrihydrite.xdi`, `XASLIB/Hansel2001_2lineFerrihydrite_xanes_001.xdi` |
| **Green Rusts (Cl, SO4)** | $\text{Fe}^{2+}_4\text{Fe}^{3+}_2(\text{OH})_{12}\text{X} \cdot n\text{H}_2\text{O}$ | Mixed valence | `XASLIB/Hansel2001_greenrust_Cl_001.xdi`, `..._002.xdi`, `..._SO4_...xdi` |
| **Hornblende** | $\text{Ca}_2(\text{Mg},\text{Fe},\text{Al})_5\text{Si}_8\text{O}_{22}(\text{OH})_2$ | 3 sites | `COD/cod_9001225.cif`, `NIST/Fe-Hornblende.xdi` |
| **Ilvaite** | $\text{CaFe}^{2+}_2\text{Fe}^{3+}\text{Si}_2\text{O}_8(\text{OH})$ | 3 sites | `COD/cod_9002233.cif`, `NIST/Fe-Ilvaite.xdi`, `XASDB/Ilvaite_id68fh1u.dat` |
| **Iron(III) Oxalate** | $\text{Fe}_2(\text{C}_2\text{O}_4)_3 \cdot x\text{H}_2\text{O}$ | 2 sites | `NIST/Fe-Fe3Oxalate.xdi` |
| **Iron(III) Sulfates** | $\text{Fe}_2(\text{SO}_4)_3$ | 2 to 5 sites | `COD/cod_9008258.cif`, `cod_9000251.cif` |
| **Jacobsite / Spinels** | $\text{MnFe}_2\text{O}_4, \text{NiFe}_2\text{O}_4, \text{ZnFe}_2\text{O}_4$ | 2 sites ($8a + 16d$) | `COD/cod_9005293.cif`, `cod_2300289.cif`, `cod_2300615.cif`, `NIST/Fe-K-Jacobsite.xdi`, `...NiFerrite...`, `...ZnFerrite...` |
| **Ludwigite** | $\text{Mg}_2\text{FeBO}_5$ | 4 sites | `COD/cod_1520786.cif`, `NIST/Fe-Ludwigite.xdi` |
| **Magnetite** | $\text{Fe}_3\text{O}_4$ | 2 sites ($8a + 16d$) | `COD/cod_1011032.cif`, `NIST/Fe-Magnetite.xdi`, `XASLIB/Fe3O4_rt_01.xdi`, `Hansel2001_magnetite_...xdi` |
| **Neotocite** | $(\text{Mn},\text{Fe})\text{SiO}_3 \cdot \text{H}_2\text{O}$ | Amorphous | `NIST/Fe-Neotocite.xdi` |
| **Olivine** | $(\text{Mg},\text{Fe})_2\text{SiO}_4$ | 2 sites ($4a + 4c$) | `COD/cod_9006875.cif`, `XASDB/Olivine_idaw4rkf.dat` |
| **Roaldite** | $\text{Fe}_4\text{N}$ | 2 sites ($1a + 3c$) | `COD/cod_9004225.cif`, `XASLIB/FeN_rt_01.xdi` |
| **Vesuvianite** | $\text{Ca}_{19}\text{Al}_{10}\text{Fe}_2\text{Si}_{18}\text{O}_{69}(\text{OH})_9$ | 4 sites | `COD/cod_1525586.cif`, `NIST/Fe-Vesuvianite.xdi` |
| **Vivianite** | $\text{Fe}_3(\text{PO}_4)_2 \cdot 8\text{H}_2\text{O}$ | 2 sites ($2a + 4g$) | `COD/cod_1001782.cif`, `NIST/Fe-Vivianite.xdi`, `XASLIB/Hansel2001_vivianite_xanes_001.xdi` |
