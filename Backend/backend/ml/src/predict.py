from pathlib import Path
import gc

import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "mobilenetv2_test.pth"
OUTPUT_DIR = BASE_DIR / "app" / "outputs"

DEVICE = torch.device("cpu")

# IMPORTANT:
# Do NOT load the model when this file is imported.
# Render only has 512 MB RAM, so we load it when actually needed.

_model = None
_classes = None
_cam = None

# Keep CPU memory/thread usage low on Render
torch.set_num_threads(1)


def _ensure_model():
    """Load the ML model only when it is actually needed."""
    global _model, _classes

    if _model is not None:
        return _model, _classes

    print("Loading MobileNetV2 model...")

    checkpoint = torch.load(
        MODEL_PATH,
        map_location="cpu"
    )

    _classes = checkpoint["classes"]

    model = models.mobilenet_v2(weights=None)
    model.classifier[1] = nn.Linear(
        model.classifier[1].in_features,
        len(_classes)
    )

    model.load_state_dict(checkpoint["model_state_dict"])

    # Free checkpoint memory after loading
    del checkpoint
    gc.collect()

    model = model.to(DEVICE)
    model.eval()

    _model = model

    print("MobileNetV2 model loaded successfully.")

    return _model, _classes


def get_classes():
    """Return the supported disease classes."""
    _, classes = _ensure_model()
    return classes


def _ensure_cam():
    """Create Grad-CAM only when it is actually needed."""
    global _cam

    if _cam is not None:
        return _cam

    model, _ = _ensure_model()

    from pytorch_grad_cam import GradCAM

    target_layers = [model.features[-1]]

    _cam = GradCAM(
        model=model,
        target_layers=target_layers
    )

    return _cam


# Image preprocessing
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


def check_image_quality(image):
    """
    Basic image-quality check.

    Returns:
        (True, []) if acceptable
        (False, [issues]) if image quality is poor
    """

    issues = []

    width, height = image.size

    if width < 100 or height < 100:
        issues.append("Image resolution is too low.")

    if image.mode not in ["RGB", "RGBA"]:
        issues.append("Unsupported image format.")

    return len(issues) == 0, issues


def predict_image_bytes(image_bytes):
    """
    Run disease prediction on uploaded image bytes.
    """

    # Open image first
    try:
        import io

        image = Image.open(io.BytesIO(image_bytes))

        # Convert to RGB
        image = image.convert("RGB")

    except Exception as exc:
        return {
            "prediction_status": "image_quality_failed",
            "is_low_confidence": True,
            "error": f"Could not read image: {str(exc)}"
        }

    # Check image quality BEFORE loading the model.
    quality_ok, quality_issues = check_image_quality(image)

    if not quality_ok:
        return {
            "prediction_status": "image_quality_failed",
            "is_low_confidence": True,
            "quality_issues": quality_issues,
            "treatment": None
        }

    # Model is loaded only now.
    model, classes = _ensure_model()

    # Prepare image
    input_tensor = transform(image).unsqueeze(0).to(DEVICE)

    # Run prediction
    with torch.inference_mode():
        outputs = model(input_tensor)
        probabilities = torch.softmax(outputs, dim=1)

    confidence, predicted_index = torch.max(probabilities, dim=1)

    confidence_value = float(confidence.item())
    predicted_index = int(predicted_index.item())

    predicted_class = classes[predicted_index]

    # Top 3 predictions
    top_k = min(3, len(classes))

    top_probs, top_indices = torch.topk(
        probabilities,
        top_k,
        dim=1
    )

    top_predictions = []

    for probability, index in zip(
        top_probs[0],
        top_indices[0]
    ):
        top_predictions.append({
            "class": classes[int(index.item())],
            "confidence": float(probability.item())
        })

    # ---------------------------------------------------------
    # Grad-CAM
    # ---------------------------------------------------------

    gradcam_path = None

    try:
        cam = _ensure_cam()

        from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget
        from pytorch_grad_cam.utils.image import show_cam_on_image

        targets = [
            ClassifierOutputTarget(predicted_index)
        ]

        # Grad-CAM expects a batch of RGB images in [0,1]
        rgb_image = image.resize((224, 224))

        rgb_array = (
            torch.from_numpy(
                __import__("numpy").array(rgb_image)
            ).float() / 255.0
        ).numpy()

        grayscale_cam = cam(
            input_tensor=input_tensor,
            targets=targets
        )

        grayscale_cam = grayscale_cam[0]

        visualization = show_cam_on_image(
            rgb_array,
            grayscale_cam,
            use_rgb=True
        )

        OUTPUT_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        gradcam_path = OUTPUT_DIR / "gradcam_latest.jpg"

        Image.fromarray(visualization).save(
            gradcam_path
        )

    except Exception as exc:
        print(f"Grad-CAM generation failed: {exc}")

    # ---------------------------------------------------------
    # Confidence handling
    # ---------------------------------------------------------

    confidence_threshold = 0.70

    try:
        import os

        confidence_threshold = float(
            os.getenv(
                "CONFIDENCE_THRESHOLD",
                "0.70"
            )
        )
    except Exception:
        confidence_threshold = 0.70

    is_low_confidence = (
        confidence_value < confidence_threshold
    )

    if is_low_confidence:
        prediction_status = "low_confidence"
    else:
        prediction_status = "success"

    return {
        "prediction_status": prediction_status,
        "is_low_confidence": is_low_confidence,
        "predicted_class": predicted_class,
        "confidence": confidence_value,
        "top_predictions": top_predictions,
        "gradcam_path": str(gradcam_path)
        if gradcam_path
        else None,
        "quality_issues": []
    }


def predict_image(image_path):
    """
    Convenience function for predicting from an image file.
    """

    image_path = Path(image_path)

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    return predict_image_bytes(image_bytes)