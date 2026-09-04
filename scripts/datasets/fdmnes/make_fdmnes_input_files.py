"""Creates a submission script to run FDMNES jobs on the cluster."""

import concurrent.futures
import filecmp  # noqa
import json
import logging
import multiprocessing
import os
from datetime import datetime, timezone

import mendeleev
from monty.json import MontyDecoder
from ruamel.yaml import YAML
from tqdm import tqdm

from xasml import resource_path
from xasml.datasets.fdmnes.io import Fdmnes

logger = logging.getLogger(__name__)

# Constants
NUM_PROCESSES = min(multiprocessing.cpu_count(), 8)
ROOT_PATH = "/data/scisoft/xasml"
ELEMENT = "Fe"
ATOMIC_NUMBER = mendeleev.element(ELEMENT).atomic_number
JOB = "job17"
JOBS_FILE = "jobs.yaml"
SELECTED_MATERIALS = [
    "mp-21867",  # Aegirine
    "mp-6672",  # Andradite
    "mp-3497",  # Chalcopyrite
    "mp-696825",  # Epidote
    "mp-605437",  # Goethite
    "mp-18890",  # Hedenbergite
    "mp-19770",  # Hematite
    "mp-698316",  # Humboldtine
    "mp-19417",  # Ilmenite
    "mp-13",  # Iron
    "mp-1192851",  # Jarosite
    "mp-696580",  # Lepidocrocite
    "mp-226",  # Pyrite
    "mp-19109",  # Rodolicoite
    "mp-543041",  # Scorodite
    "mp-18969",  # Siderite
    "mp-744386",  # Staurolite
    "mp-1194614",  # Tetrachloroferrate
    "mp-19017",  # Triphylite
    "mp-19421",  # Wolframite
    "mp-18905",  # Wustite
]
FORCE_CIF_WRITE = False
CHECK_FDMNES_JOBS = True
CREATE_SBATCH_SCRIPT = True
PARSING_ERRORS = [
    "the output file does not exist",
    "partial output file",
    "the bav file does not exist",
    "error reading the bav file",
    "point group not found",
    "failed to parse the spectrum",
]


def process_material(material):
    """Process a single material."""
    try:
        material["database_IDs"]["icsd"]
    except KeyError:
        return None

    material_id = material["material_id"]

    # Check if material should be processed.
    if SELECTED_MATERIALS and material_id not in SELECTED_MATERIALS:
        return None

    logger.debug(f"Processing {material_id}.")

    # Create material directory.
    parent_path = os.path.join(ROOT_PATH, "materials", material_id)
    os.makedirs(parent_path, exist_ok=True)

    # Write CIF file if required.
    cif_filename = os.path.join(parent_path, f"{material_id}.cif")
    if not os.path.exists(cif_filename) or FORCE_CIF_WRITE:
        structure = material["structure"]
        structure.to(cif_filename, symprec=0.01, angle_tolerance=5)

    # Check FDMNES jobs if required.
    if CHECK_FDMNES_JOBS:
        job_path = os.path.join(parent_path, ELEMENT, JOB)
        calculation = Fdmnes(job_path, "job", ELEMENT)
        calculation.parse()

        if calculation.error in PARSING_ERRORS:
            logger.error(f"{material_id}: {calculation.error}")
            return material
    else:
        return material


def process_materials(materials):
    """Process materials in parallel with progress tracking."""
    materials_with_jobs_to_run = []

    with concurrent.futures.ProcessPoolExecutor(max_workers=NUM_PROCESSES) as executor:
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
                        materials_with_jobs_to_run.append(result)
                except Exception as e:
                    material_id = futures[future].get("material_id", "unknown")
                    logger.exception(f"Error processing material {material_id}: {e!s}")
                finally:
                    pbar.update(1)

    return materials_with_jobs_to_run


def create_sbatch_script(materials) -> None:
    """Create the SBATCH script with improved error handling."""
    with open(resource_path(f"xasml:datasets/fdmnes/{JOBS_FILE}")) as fp:
        yaml = YAML(typ="safe")
        jobs_data = yaml.load(fp)

    logger.info("Creating the submission script.")
    data = ["#!/usr/bin/env bash"]

    for material in materials:
        material_id = material["material_id"]
        job_path = os.path.join(ROOT_PATH, "materials", material_id, ELEMENT, JOB)
        os.makedirs(job_path, exist_ok=True)

        parent_path = os.path.join(ROOT_PATH, "materials", material_id)
        cif_filename = os.path.join(parent_path, f"{material_id}.cif")

        try:
            calculation = Fdmnes(job_path, "job", ELEMENT)
            template = resource_path("xasml:datasets/fdmnes/templates/fdmnes.template")
            calculation.make_input(
                cif_filename,
                template=template,
                atomic_number=ATOMIC_NUMBER,
                **jobs_data[JOB],
            )
            template = resource_path("xasml:datasets/fdmnes/templates/sbatch.template")
            calculation.make_sbatch(template=template, **jobs_data[JOB])
        except ValueError:
            logger.exception("%s, failed to create the input", material_id)
            continue
        data.append(f"SWD=$(pwd); cd {job_path}; sbatch job.sbatch; cd $SWD")

    with open("sbatch.sh", "w") as fp:
        fp.write("\n".join(data) + "\n")

    os.chmod("sbatch.sh", 0o755)
    logger.info("Successfully created sbatch.sh.")


def main():
    now = datetime.now(tz=timezone.utc).strftime("%Y.%m.%d_%H.%M")
    name = os.path.splitext(os.path.basename(__file__))[0]
    file_handler = logging.FileHandler(f"logs/{name}_{now}.log")
    file_handler.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    handlers = [stream_handler, file_handler]
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )
    logging.captureWarnings(True)

    # Load materials.
    path = resource_path(f"xasml:datasets/materials_project/{ELEMENT}.jsonl")
    with open(path) as fp:
        materials = [json.loads(line, cls=MontyDecoder) for line in fp]

    # Process materials in parallel.
    materials_with_jobs_to_run = process_materials(materials)

    # Create SBATCH script if requested.
    if CREATE_SBATCH_SCRIPT and materials_with_jobs_to_run:
        create_sbatch_script(materials_with_jobs_to_run)


if __name__ == "__main__":
    main()
