"""
Wraps the ml/src/gradcam.py GradCAM class for use inside a request handler:
takes raw uploaded image bytes, runs inference, and returns the predicted
class, confidence, and a base64-encoded heatmap overlay ready to send to
the frontend.
"""
import base64
import io
import sys
from pathlib import Path

from PIL import Image

# ml/src is a sibling directory to backend/ — add it to the path so we can
# reuse the same GradCAM implementation used during training/evaluation.
sys.path.append(str(Path(__file__).resolve().parents[3] / "ml" / "src"))
from gradcam import GradCAM, IMG_SIZE, NORMALIZE  # noqa: E402
from torchvision import transforms  # noqa: E402
import torch  # noqa: E402
import torch.nn.functional as F  # noqa: E402
import numpy as np  # noqa: E402

from .model_loader import get_device


def run_diagnosis(model, classes, image_bytes: bytes):
    if model is None:
        # No trained checkpoint yet — see model_loader.ALLOW_MOCK.
        return run_mock_diagnosis(classes, image_bytes)

    device = get_device()

    original = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    resized = original.resize((IMG_SIZE, IMG_SIZE))

    tensor = transforms.ToTensor()(resized)
    tensor = NORMALIZE(tensor).unsqueeze(0).to(device)
    tensor.requires_grad_(True)

    target_layer = model.features[-1]  # last conv block of MobileNetV2
    cam = GradCAM(model, target_layer)
    heatmap, class_idx, confidence = cam.generate(tensor)

    overlay = _overlay_heatmap(resized, heatmap)
    heatmap_b64 = _image_to_base64(overlay)

    return {
        "disease": classes[class_idx],
        "confidence": round(confidence, 4),
        "heatmap_base64": heatmap_b64,
    }


def run_mock_diagnosis(classes, image_bytes: bytes):
    """
    Fabricates a plausible-looking diagnosis without running any real model,
    so the API contract, frontend, and database wiring can all be built and
    tested before training is done. The response shape is identical to the
    real path — only the numbers are fake.
    """
    import hashlib

    original = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    resized = original.resize((IMG_SIZE, IMG_SIZE))

    # Deterministic-but-varied pick so the same image always gets the same
    # mock result within a session, instead of random flicker on retries.
    digest = hashlib.md5(image_bytes).hexdigest()
    class_idx = int(digest, 16) % len(classes)
    confidence = 0.75 + (int(digest[:4], 16) % 2000) / 10000  # ~0.75-0.95

    overlay = _mock_heatmap_overlay(resized, seed=int(digest[:8], 16))
    heatmap_b64 = _image_to_base64(overlay)

    return {
        "disease": classes[class_idx],
        "confidence": round(confidence, 4),
        "heatmap_base64": heatmap_b64,
    }


def _mock_heatmap_overlay(image: Image.Image, seed: int) -> Image.Image:
    """Draws a few soft colored blobs over the image to visually stand in
    for a Grad-CAM heatmap, without running any model."""
    import random

    from PIL import ImageDraw, ImageFilter

    rng = random.Random(seed)
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    colors = [(255, 77, 46, 160), (255, 176, 32, 130)]
    for i in range(rng.randint(2, 3)):
        cx, cy = rng.randint(60, 164), rng.randint(60, 164)
        r = rng.randint(20, 45)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=colors[i % len(colors)])

    overlay = overlay.filter(ImageFilter.GaussianBlur(12))
    return Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")


def _overlay_heatmap(original: Image.Image, heatmap: np.ndarray, alpha: float = 0.45) -> Image.Image:
    import matplotlib.cm as cm

    colored = (cm.jet(heatmap)[:, :, :3] * 255).astype("uint8")
    colored_img = Image.fromarray(colored)
    return Image.blend(original, colored_img, alpha=alpha)


def _image_to_base64(img: Image.Image) -> str:
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")
