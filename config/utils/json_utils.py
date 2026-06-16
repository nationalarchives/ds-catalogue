"""
JSON serialisation utilities.
"""

import json
from urllib.parse import unquote


def parse_json(s) -> dict:
    try:
        return json.loads(unquote(s))
    except Exception:
        return {}


def dump_json(obj) -> str:
    return json.dumps(obj, indent=2)
