"""The module reads the spectra from the finished FDMNES calculations, determines the coordination
environment of the absorbing site, and stores the data in an HDF5 file."""

import concurrent.futures
import json
import logging
import multiprocessing
import os
from datetime import datetime, timezone

import h5py
from monty.json import MontyDecoder
from pymatgen.analysis.chemenv.coordination_environments.chemenv_strategies import (
    MultiWeightsChemenvStrategy,
    SimplestChemenvStrategy,  # noqa: F401
    WeightedNbSetChemenvStrategy,  # noqa: F401
)
from silx.io.dictdump import dicttoh5
from tqdm import tqdm

from xasml import resource_path
from xasml.datasets.fdmnes.material import Material

logger = logging.getLogger(__name__)

# Constants
NUM_PROCESSES = min(multiprocessing.cpu_count(), 8)
# The paths are resolved from the repository root, three levels above this script.
ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
MATERIALS_PATH = os.path.join(ROOT_PATH, "materials")
LOGS_PATH = os.path.join(ROOT_PATH, "logs")
ELEMENT = "Fe"
JOBS = ["job15"]
SELECTED_MATERIALS = None  # ["mp-13", "mp-226", "mp-1005", "mp-10188"]
REFERENCE_MATERIALS = ["mp-19770"]  # hematite
HDF5_FILENAME = "tmp.h5" if SELECTED_MATERIALS is not None else "materials.h5"

# Structure environment configuration
STRUCTURE_ENVIRONMENT_CONFIGURATION = {
    "min_cn": 4,
    "max_cn": 6,
    "only_symbols": ["S:4", "T:4", "T:5", "S:5", "O:6", "T:6"],
}
# STRATEGY = SimplestChemenvStrategy()
STRATEGY = MultiWeightsChemenvStrategy.stats_article_weights_parameters()

# Spectrum configuration
SPECTRUM_BROADENING_PARAMS = {
    "e_cent": 30,
    "e_larg": 30,
    "gamma_hole": 1.25,
    "gamma_max": 15.0,
}
# Puts the first inflection point of calculated Fe metal at 7112.0 eV.
EPSII_REFERENCE = 6974.5


def process_material(material):
    """Process a single material."""
    material_id = material["material_id"]
    is_reference = material_id in REFERENCE_MATERIALS

    # Skip materials without ICSD entry, unless they are reference materials.
    if not is_reference:
        try:
            material["database_IDs"]["icsd"]
        except KeyError:
            return None

    # For debugging purposes analyze only specific materials_ids.
    if SELECTED_MATERIALS is not None and material_id not in SELECTED_MATERIALS:
        return None

    try:
        material = Material(material_id, MATERIALS_PATH)
    except TypeError as e:
        logger.error("%s, %s", material_id, e)
        return None

    unique_sites = material.get_unique_sites(ELEMENT)
    structure_environment_kwargs = {
        "only_indices": list(unique_sites),
        **STRUCTURE_ENVIRONMENT_CONFIGURATION,
    }
    material.determine_structure_environments(**structure_environment_kwargs)
    material.find_coordination_environments(STRATEGY)

    results = []
    for index in list(unique_sites):
        # Get coordination environment data first.
        ce = material.get_site_coordination_environments_data(index)
        if not ce or ce is None:
            if not is_reference:
                logger.error(
                    "No coordination environment available for %s and index %d.",
                    material_id,
                    index,
                )
                continue
            ce = {}

        # Parse through jobs for each site.
        for job in JOBS:
            material.parse_calculation(ELEMENT, job)

            if material.calculation is None:
                logger.error("%s, No calculation available.", material_id)
                continue

            if material.calculation.error:
                logger.error("%s, %s", material_id, material.calculation.error)
                continue

            # Get coordination environment details.
            symbols = ce.get("coordination_environments", {}).get("symbols", [])
            fractions = ce.get("coordination_environments", {}).get("fractions", [])
            csms = ce.get("coordination_environments", {}).get("csms", [])

            if not symbols:
                if not is_reference:
                    logger.error(
                        "No coordination environment symbols available for %s and index %d.",
                        material_id,
                        index,
                    )
                    continue
                logger.info(
                    "%s, %d, reference material (no coordination environment).",
                    material_id,
                    index,
                )
            else:
                if csms[0] is None:
                    csms[0] = 0.0

                logger.info(
                    "%s, %d, %s, %.3f, %.3f",
                    material_id,
                    index,
                    symbols[0],
                    fractions[0],
                    csms[0],
                )

            # Spectrum of the absorbing site.
            try:
                spectrum = material.get_site_spectrum(
                    index,
                    epsii_reference=EPSII_REFERENCE,
                    **SPECTRUM_BROADENING_PARAMS,
                )
            except (KeyError, ValueError) as e:
                logger.error("%s, %s", material_id, e)
                continue

            results.append({
                "material_id": material_id,
                "index": index,
                "ce": ce,
                "spectrum": spectrum,
                "structure": material.structure.to_json(),
            })

    return results


def configure_logging(log_path):
    """Configure logging to write to the file given by ``log_path``.

    The spawn start method re-imports this module in every worker process, so
    the configuration applied in ``main`` is not inherited. Each worker calls
    this function to keep the per-material diagnostics.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_path)],
    )
    logging.captureWarnings(True)


def process_materials(materials, log_path):
    """Process materials in parallel with progress tracking."""
    data = []

    with concurrent.futures.ProcessPoolExecutor(
        max_workers=NUM_PROCESSES,
        initializer=configure_logging,
        initargs=(log_path,),
    ) as executor:
        # Submit all materials for processing.
        futures = {
            executor.submit(process_material, material): material
            for material in materials
        }

        # Process results with progress bar.
        with tqdm(total=len(materials), desc="Processing materials") as pbar:
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    if result is not None:
                        data.append(result)
                except Exception:
                    material_id = futures[future].get("material_id", "unknown")
                    logger.exception("Error processing material %s.", material_id)
                finally:
                    pbar.update(1)

    return data


def write_results_to_hdf5(results, h5file):
    """Write the results to the HDF5 file."""
    for result in results:
        if result is None:
            continue

        material_id = result["material_id"]
        index = result["index"]
        site_path = f"materials/{material_id}/sites/{index}"

        # Create the material group if it does not exist.
        material_path = f"materials/{material_id}"
        if material_path not in h5file:
            h5file.create_group(material_path)

        # Store the full structure JSON once per material.
        structure_path = f"{material_path}/structure"
        if structure_path not in h5file:
            h5file.create_dataset(structure_path, data=result["structure"])

        if result["ce"]:
            dicttoh5(result["ce"], h5file, h5path=site_path)
        dicttoh5(result["spectrum"], h5file, h5path=site_path)


def main():
    # Configure logging.
    now = datetime.now(tz=timezone.utc).strftime("%Y.%m.%d_%H.%M")
    name = os.path.splitext(os.path.basename(__file__))[0]
    os.makedirs(LOGS_PATH, exist_ok=True)
    log_path = os.path.join(LOGS_PATH, f"{name}_{now}.log")
    configure_logging(log_path)

    # Load the materials.
    path = resource_path(f"xasml:datasets/materials_project/{ELEMENT}.jsonl")
    with open(path) as fp:
        materials = [json.loads(line, cls=MontyDecoder) for line in fp]

    logger.info("Loaded %d materials for processing.", len(materials))

    results = process_materials(materials, log_path)

    # Flatten the list of results.
    results = [item for items in results if items is not None for item in items]

    results = sorted(results, key=lambda r: int(r["material_id"].split("-")[1]))

    # Write results to disk.
    path = resource_path(f"xasml:datasets/fdmnes/{HDF5_FILENAME}")
    with h5py.File(path, "w") as h5file:
        write_results_to_hdf5(results, h5file)

    # Count the total number of processed sites.
    number_of_sites = len(results)

    logger.info("Number of sites processed: %d", number_of_sites)


if __name__ == "__main__":
    main()
