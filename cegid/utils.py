import json
from collections import namedtuple


def _json_object_hook(d): 
    return namedtuple('X', d.keys())(*d.values())

def json2obj(data): 
    """
        Convertit un 
    """
    return json.loads(data, object_hook=_json_object_hook)