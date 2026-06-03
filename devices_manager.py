import json
from pathlib import Path


def get_devices_file(base_file):
    return Path(base_file).resolve().parent / "devices.json"


def load_devices(devices_file):
    if not devices_file.exists():
        return []
    devices = json.loads(devices_file.read_text(encoding="utf-8"))
    if not isinstance(devices, list):
        return []
    return devices


def save_devices(devices_file, devices):
    devices_file.write_text(json.dumps(devices, indent=2), encoding="utf-8")
