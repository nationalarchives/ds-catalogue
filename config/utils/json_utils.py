import json
from urllib.parse import unquote


def parse_json(s):
    try:
        unquoted_string = unquote(s)
        return json.loads(unquoted_string)
    except Exception:
        return {}


def dump_json(obj):
    return json.dumps(obj, indent=2)
