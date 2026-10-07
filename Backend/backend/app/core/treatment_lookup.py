import json
import os
from pathlib import Path

_TREATMENTS_PATH = Path(os.getenv("TREATMENTS_PATH", "../data/treatments.json"))
_treatments = None


def _load():
    global _treatments
    if _treatments is None:
        with open(_TREATMENTS_PATH) as f:
            _treatments = json.load(f)
    return _treatments


def get_treatment(disease_class: str) -> dict:
    """
    Looks up curated treatment info for a PlantVillage class name
    (e.g. "Tomato___Early_blight"). Falls back to a generic entry
    for classes that haven't been curated yet, rather than failing —
    the model can predict more classes than we've written treatment
    copy for.
    """
    treatments = _load()
    return treatments.get(disease_class, treatments["_default"])
