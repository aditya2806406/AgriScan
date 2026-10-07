"""
Loads the trained MobileNetV2 checkpoint once at startup and exposes it
as a module-level singleton so every request reuses the same in-memory model
instead of reloading it from disk each time.
"""
import os
from pathlib import Path

import torch
import torch.nn as nn
from torchvision import models

MODEL_PATH = Path(os.getenv("MODEL_PATH", "../ml/models/mobilenetv2_plantvillage.pt"))

# Lets the full stack (frontend, backend, DB) be built, run, and demoed before
# a real model has been trained. NEVER leave this true in a real deployment —
# it exists purely so development isn't blocked on the ML pipeline finishing.
ALLOW_MOCK = os.getenv("ALLOW_MOCK", "true").lower() == "true"

# Kept in sync with the class names used in data/treatments.json, so mock
# predictions still resolve to real treatment copy.
MOCK_CLASSES = [
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___healthy",
    "Potato___Late_blight",
    "Corn_(maize)___Common_rust",
]

_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
_model = None
_classes = None
_mock_mode = False


def load_model():
    """
    Returns (model, classes). If no trained checkpoint exists yet and
    ALLOW_MOCK is set, returns (None, MOCK_CLASSES) — callers must check
    for model is None and use the mock inference path in that case.
    """
    global _model, _classes, _mock_mode
    if _model is not None or _mock_mode:
        return _model, _classes

    if not MODEL_PATH.exists():
        if ALLOW_MOCK:
            print(
                f"[agriscan] WARNING: no trained model found at {MODEL_PATH}. "
                "Running in MOCK MODE — responses are fabricated, not real predictions. "
                "Run ml/src/train.py and set ALLOW_MOCK=false before deploying."
            )
            _mock_mode = True
            _classes = MOCK_CLASSES
            return None, _classes
        raise RuntimeError(
            f"No trained model found at {MODEL_PATH}. "
            "Run ml/src/train.py first, or set the MODEL_PATH environment variable."
        )

    checkpoint = torch.load(MODEL_PATH, map_location=_device)
    classes = checkpoint["classes"]

    model = models.mobilenet_v2(weights=None)
    in_features = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(in_features, len(classes))
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(_device).eval()

    _model, _classes = model, classes
    return _model, _classes


def is_mock_mode() -> bool:
    return _mock_mode


def get_device():
    return _device
