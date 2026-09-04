# Issues

## 2024/07/31

The already existing calculations have been created with an older version of
Pymatgen, and with the current version (2024.07.18), the generation of the
FDMNES input file fails in some cases because the structure cannot be
determined. An example is `mp-556507`.

There is some duplication in the `get_unique_sites` method from `material.py`
and the `make_input` method from `fdmnes.py`. The code should be refactored.
