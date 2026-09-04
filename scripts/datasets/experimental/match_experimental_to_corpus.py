"""Match every experimental reference compound to an entry of the FDMNES corpus.

The rule is structural. A corpus entry is a candidate when it has the composition of
the mineral, and it is accepted when pymatgen StructureMatcher maps it onto the
reference structure, when both structures give the same space group at a common
tolerance, and when the absorbing iron site carries the same ChemEnv symbol.

Every space group in this script is determined at symprec 0.1. The corpus build uses
0.01, which is tight enough that a relaxed structure loses the symmetry of its parent,
so the space group recorded in the corpus must not be used to decide a match.
"""

import json
import re
import sys
from pathlib import Path

from pymatgen.analysis.structure_matcher import ElementComparator, StructureMatcher
from pymatgen.core import Composition, Structure
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

ROOT = Path(__file__).resolve().parents[3]
DB = ROOT / "resources/datasets/experimental/databases"
LOG = max((ROOT / "logs").glob("build_materials_database_*.log"))

SYMPREC, ANGLE_TOL = 0.1, 5
MATCHER = StructureMatcher(
    ltol=0.2,
    stol=0.3,
    angle_tol=5,
    primitive_cell=True,
    scale=True,
    comparator=ElementComparator(),
)

# The reference structure of each mineral, the ChemEnv symbol of its iron site, and the
# nominal composition including hydrogen. Hydrogen is kept separate because the X-ray
# refinements of the hydrates do not locate it.
COMPOUNDS = {
    "Aegirine": ("COD/Aegerine/cod_9000327.cif", "O:6", "NaFeSi2O6"),
    "Andradite": ("COD/Andradite/cod_2101484.cif", "O:6", "Ca3Fe2Si3O12"),
    "Chalcopyrite": ("COD/Chalcopyrite/cod_1010940.cif", "T:4", "CuFeS2"),
    "Goethite": ("COD/Goethite/cod_2211652.cif", "O:6", "FeHO2"),
    "Hedenbergite": ("COD/Hedenbergite/cod_9000336.cif", "O:6", "CaFeSi2O6"),
    "Hematite": ("COD/Hematite/cod_1532119.cif", "O:6", "Fe2O3"),
    "Heterosite": ("COD/Iron Phosphate/cod_9015219.cif", "O:6", "FePO4"),
    "Humboldtine": ("COD/Iron (II) Oxalate/cod_9017265.cif", "O:6", "FeH4C2O6"),
    "Ilmenite": ("COD/Ilmenite/cod_1011033.cif", "O:6", "FeTiO3"),
    "Lepidocrocite": ("COD/Lepidocrocite/cod_1011026.cif", "O:6", "FeHO2"),
    "Pyrite": ("COD/Pyrite/cod_1544891.cif", "O:6", "FeS2"),
    "Rodolicoite": ("COD/Iron (III) Phosphate/cod_9012512.cif", "T:4", "FePO4"),
    "Scorodite": ("COD/Scorodite/cod_2212542.cif", "O:6", "FeH4AsO6"),
    "Scorzalite": ("COD/Scorzalite/cod_9007451.cif", "O:6", "FeAl2P2O10H2"),
    "Siderite": ("COD/Siderite/cod_2104746.cif", "O:6", "FeCO3"),
    "Wolframite": ("COD/Wolframite/cod_9000223.cif", "O:6", "FeWO4"),
    "Wustite": ("COD/Wustite/cod_1011169.cif", "O:6", "FeO"),
}


def heavy(structure):
    """Return the structure without hydrogen and without oxidation states."""
    s = structure.copy()
    s.remove_oxidation_states()
    s.remove_species(["H"])
    return s


def heavy_key(composition):
    c = Composition(composition).element_composition
    return Composition(
        {el.symbol: n for el, n in c.items() if el.symbol != "H"}
    ).reduced_composition


def symmetry(structure):
    spa = SpacegroupAnalyzer(structure, symprec=SYMPREC, angle_tolerance=ANGLE_TOL)
    orbits = spa.get_symmetrized_structure().equivalent_sites
    n_fe = sum(1 for g in orbits if g[0].specie.symbol == "Fe")
    return spa.get_space_group_symbol(), spa.get_space_group_number(), n_fe


def chemenv_labels():
    out = {}
    pattern = re.compile(r"INFO - (mp-\d+), (\d+), (\S+), ([\d.]+), ([\d.]+)")
    for line in LOG.read_text().splitlines():
        if m := pattern.search(line):
            out.setdefault(m.group(1), []).append(
                (int(m.group(2)), m.group(3), float(m.group(5)))
            )
    return out


def load_corpus():
    calculated = {
        p.name
        for p in (ROOT / "materials").iterdir()
        if re.fullmatch(r"mp-\d+", p.name)
    }
    with open(ROOT / "resources/datasets/materials_project/Fe.jsonl") as f:
        return [d for line in f if (d := json.loads(line))["material_id"] in calculated]


def main():
    labels = chemenv_labels()
    index = {}
    for d in load_corpus():
        index.setdefault(heavy_key(d["composition"]), []).append(d)

    rows = []
    for name, (rel, symbol, formula) in COMPOUNDS.items():
        ref_h = heavy(Structure.from_file(DB / rel))
        ref_sg, ref_no, ref_orbits = symmetry(ref_h)
        candidates = index.get(heavy_key(ref_h.composition), [])

        accepted, rejected = [], []
        for d in candidates:
            mid = d["material_id"]
            cand_h = heavy(Structure.from_dict(d["structure"]))
            if not MATCHER.fit(cand_h, ref_h):
                rejected.append({"mp": mid, "reasons": ["structure"]})
                continue
            rms, max_d = MATCHER.get_rms_dist(cand_h, ref_h)
            sg, no, orbits = symmetry(cand_h)
            env = labels.get(mid, [])
            reasons = []
            if no != ref_no:
                reasons.append(f"space group {sg}")
            if (
                Composition(d["composition"]).reduced_composition
                != Composition(formula).reduced_composition
            ):
                reasons.append(f"composition {d['formula_pretty']}")
            if not env or {e[1] for e in env} != {symbol}:
                reasons.append(f"environment {sorted({e[1] for e in env}) or ['none']}")
            record = {
                "mp": mid,
                "rms": round(float(rms), 4),
                "max_d": round(float(max_d), 4),
                "sg": sg,
                "orbits": orbits,
                "ehull": round(d["energy_above_hull"], 3),
                "csm": [e[2] for e in env],
                "reasons": reasons,
            }
            (rejected if reasons else accepted).append(record)

        # Rank by stability first. Candidates that survive the structural test differ
        # only by the relaxation, so the displacement cannot separate them reliably;
        # the mineral is the phase that sits lowest above the convex hull.
        accepted.sort(key=lambda r: (r["ehull"], r["rms"]))
        rows.append(
            {
                "name": name,
                "formula": formula,
                "ref_sg": ref_sg,
                "ref_orbits": ref_orbits,
                "n_candidates": len(candidates),
                "accepted": accepted,
                "rejected": rejected,
            }
        )

    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text(json.dumps(rows, indent=1))

    print(
        f"{'Compound':14s} {'ref sg':9s} {'mp id':11s} {'mp sg':9s} {'Fe':>2s} "
        f"{'rms':>6s} {'max':>6s} {'ehull':>6s} {'CSM':>6s}  next best"
    )
    print("-" * 100)
    for r in rows:
        if not r["accepted"]:
            print(
                f"{r['name']:14s} {r['ref_sg']:9s} {'none':11s} "
                f"{r['n_candidates']} candidates, all rejected"
            )
            continue
        b = r["accepted"][0]
        csm = f"{b['csm'][0]:.3f}" if b["csm"] else "-"
        alt = (
            ", ".join(
                f"{a['mp']} (rms {a['rms']:.3f}, hull {a['ehull']:.3f})"
                for a in r["accepted"][1:3]
            )
            or "-"
        )
        print(
            f"{r['name']:14s} {r['ref_sg']:9s} {b['mp']:11s} {b['sg']:9s} "
            f"{b['orbits']:>2d} {b['rms']:>6.3f} {b['max_d']:>6.3f} {b['ehull']:>6.3f} "
            f"{csm:>6s}  {alt}"
        )


if __name__ == "__main__":
    main()
