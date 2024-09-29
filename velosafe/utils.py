import dataclasses
import datetime
import hashlib
import json

__all__ = ["get_hash"]
def json_default(thing):
    try:
        return dataclasses.asdict(thing)
    except TypeError:
        pass
    if isinstance(thing, datetime.datetime):
        return thing.isoformat(timespec='microseconds')
    raise TypeError(f"object of type {type(thing).__name__} not serializable")

def json_dumps(thing: object):
    return json.dumps(
        thing,
        default=json_default,
        ensure_ascii=False,
        sort_keys=True,
        indent=None,
        separators=(',', ':'),
    )

def get_hash(thing):
    return hashlib.md5(json_dumps(thing).encode('utf-8')).digest()