"""Load and validate synthetic OCI Monitoring alarm + inventory exports."""
import json
import os

SEVERITIES = ("CRITICAL", "WARNING", "INFO")
RESOURCE_TYPES = ("compute-instance", "autonomous-db", "bucket")
REQUIRED_ALARM = ("id", "name", "enabled", "destinations", "covers")
REQUIRED_RESOURCE = ("id", "type", "name", "environment", "state")


class LoadError(Exception):
    pass


def _load_json(path):
    if not os.path.exists(path):
        raise LoadError("missing file: %s" % path)
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except json.JSONDecodeError as exc:
        raise LoadError("bad JSON in %s: %s" % (path, exc))


def _check_item(item, required, kind, index):
    if not isinstance(item, dict):
        raise LoadError("%s[%d] is not an object" % (kind, index))
    for field in required:
        if field not in item:
            raise LoadError("%s[%d] missing field %r" % (kind, index, field))


def load(alarms_path, inventory_path):
    """Return (alarms, resources) after structural validation."""
    alarms_doc = _load_json(alarms_path)
    inventory_doc = _load_json(inventory_path)
    if not isinstance(alarms_doc, dict) or not isinstance(alarms_doc.get("alarms"), list):
        raise LoadError("alarms export must be an object with an 'alarms' list")
    if not isinstance(inventory_doc, dict) or not isinstance(inventory_doc.get("resources"), list):
        raise LoadError("inventory export must be an object with a 'resources' list")
    alarms = alarms_doc["alarms"]
    resources = inventory_doc["resources"]
    for i, alarm in enumerate(alarms):
        _check_item(alarm, REQUIRED_ALARM, "alarms", i)
        if not isinstance(alarm["covers"], list):
            raise LoadError("alarms[%d].covers must be a list" % i)
        if not isinstance(alarm["destinations"], list):
            raise LoadError("alarms[%d].destinations must be a list" % i)
    for i, res in enumerate(resources):
        _check_item(res, REQUIRED_RESOURCE, "resources", i)
        if res["type"] not in RESOURCE_TYPES:
            raise LoadError("resources[%d] has unknown type %r" % (i, res["type"]))
    return alarms, resources


def active_resources(resources):
    return [r for r in resources if r["state"] == "ACTIVE"]


def coverage_map(alarms):
    """resource_id -> list of alarms covering it."""
    covers = {}
    for alarm in alarms:
        for rid in alarm["covers"]:
            covers.setdefault(rid, []).append(alarm)
    return covers
