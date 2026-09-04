__version__ = "2026.0.dev0"

import os

from silx.resources import register_resource_directory, resource_filename

path = os.path.join(os.path.dirname(__file__), "..", "..", "resources")
register_resource_directory("xasml", "xasml.resources", forced_path=path)

resource_path = resource_filename
