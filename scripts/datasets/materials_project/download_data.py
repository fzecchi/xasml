import json
import logging
import os

from monty.json import MontyEncoder
from mp_api.client import MPRester

from xasml import resource_path


def main():
    logging.captureWarnings(True)
    logging.basicConfig(level=logging.INFO)

    ELEMENT = "Fe"

    mpr = MPRester(os.environ["MP_API_KEY"], use_document_model=False)
    materials = mpr.materials.summary.search(elements=[ELEMENT])

    materials = sorted(materials, key=lambda x: int(x["material_id"].split("-")[1]))

    path = resource_path(f"xasml:datasets/materials_project/{ELEMENT}.jsonl")
    with open(path, "w") as f:
        for material in materials:
            f.write(json.dumps(material, cls=MontyEncoder) + "\n")


if __name__ == "__main__":
    main()
