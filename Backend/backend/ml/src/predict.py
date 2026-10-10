
from pathlib import Path
import gc
import io
import uuid

import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image, ImageFilter, ImageStat

# --------------------------------------------------
# 1. Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "mobilenetv2_test.pth"

# --------------------------------------------------
# 2. Device
# --------------------------------------------------

# Render Free has no GPU.
DEVICE = torch.device("cpu")

# Keep CPU/thread memory usage low on Render.
torch.set_num_threads(1)

# --------------------------------------------------
# 3. Lazy-loaded model variables
# --------------------------------------------------

_model = None
_classes = None

# --------------------------------------------------
# 4. Lazy model loader
# --------------------------------------------------

def _ensure_model():
    """
    Load MobileNetV2 only when a real prediction is requested.
    This prevents Render from loading the model during startup.
    """
    global _model, _classes

    if _model is not None:
        return _model, _classes

    print("Loading MobileNetV2 model...")

    checkpoint = torch.load(
        str(MODEL_PATH),
        map_location="cpu",
        mmap=True
    )

    _classes = checkpoint["classes"]

    model = models.mobilenet_v2(weights=None)
    model.classifier[1] = nn.Linear(
        model.classifier[1].in_features,
        len(_classes)
    )

    model.load_state_dict(
        checkpoint["model_state_dict"],
        assign=True
    )

    del checkpoint
    gc.collect()

    model = model.to(DEVICE)
    model.eval()

    _model = model

    print("Trained MobileNetV2 model loaded successfully.")
    print("Number of classes:", len(_classes))

    return _model, _classes


# --------------------------------------------------
# 5. Supported classes
# --------------------------------------------------

def get_classes():
    """Return the model's supported classes."""
    _, classes = _ensure_model()
    return classes


# --------------------------------------------------
# 6. Image preprocessing
# --------------------------------------------------

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


# --------------------------------------------------
# 7. Image quality checking
# --------------------------------------------------

def check_image_quality(image: Image.Image) -> tuple[bool, list[str]]:
    issues = []
    width, height = image.size

    if width < 50 or height < 50:
        issues.append("Image is too small (minimum 50x50 pixels).")

    stat = ImageStat.Stat(image.convert("L"))
    mean_brightness = stat.mean[0]

    if mean_brightness < 15:
        issues.append("Image is extremely dark.")
    elif mean_brightness > 240:
        issues.append("Image is extremely bright or overexposed.")

    edges = image.convert("L").filter(ImageFilter.FIND_EDGES)
    edge_stat = ImageStat.Stat(edges)

    if edge_stat.var[0] < 50:
        issues.append("Image appears too blurry.")

    return len(issues) == 0, issues


# --------------------------------------------------
# 8. Prediction + Grad-CAM
# --------------------------------------------------

def predict_image_bytes(image_bytes):
    import PIL

    # Limit decoded image size to help prevent excessive memory use.
    PIL.Image.MAX_IMAGE_PIXELS = 16_000_000

    try:
        image = Image.open(io.BytesIO(image_bytes))

        # Reduce the decoded image dimensions before converting to RGB.
        image.thumbnail((2000, 2000), Image.Resampling.LANCZOS)
        image = image.convert("RGB")

    except PIL.Image.DecompressionBombError:
        return (
            {
                "acceptable": False,
                "issues": [
                    "Image exceeds maximum pixel limit. Please upload a smaller image."
                ],
                "is_malformed": True
            },
            None,
            None
        )

    except Exception:
        return (
            {
                "acceptable": False,
                "issues": ["Invalid image file or cannot be decoded."],
                "is_malformed": True
            },
            None,
            None
        )

    # Check image quality before loading the model.
    acceptable, issues = check_image_quality(image)

    if not acceptable:
        return (
            {
                "acceptable": False,
                "issues": issues
            },
            None,
            None
        )

    # Load the model only after image validation.
    model, classes = _ensure_model()

    image_tensor = transform(image)
    input_tensor = image_tensor.unsqueeze(0).to(DEVICE)

    # Prediction
    with torch.inference_mode():
        outputs = model(input_tensor)
        probabilities = torch.softmax(outputs, dim=1)

    # Top 3 predictions
    top_probabilities, top_indices = torch.topk(
        probabilities,
        min(3, probabilities.shape[1]),
        dim=1
    )

    results = []

    for probability, index in zip(
        top_probabilities[0],
        top_indices[0]
    ):
        results.append({
            "disease": classes[index.item()],
            "confidence": probability.item() * 100
        })

    # Grad-CAM
    heatmap_url = None

    try:
        from pytorch_grad_cam import GradCAM
        from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget
        from pytorch_grad_cam.utils.image import show_cam_on_image
        import numpy as np

        predicted_index = top_indices[0][0].item()
        targets = [ClassifierOutputTarget(predicted_index)]
        target_layers = [model.features[-1]]

        with GradCAM(model=model, target_layers=target_layers) as cam:
            grayscale_cam = cam(
                input_tensor=input_tensor,
                targets=targets
            )

        grayscale_cam = grayscale_cam[0]

        original_image = image.resize((224, 224))
        rgb_image = np.asarray(original_image).astype("float32") / 255.0

        visualization = show_cam_on_image(
            rgb_image,
            grayscale_cam,
            use_rgb=True
        )

        filename = f"{uuid.uuid4().hex}.jpg"
        output_path = (
            BASE_DIR.parent
            / "app"
            / "outputs"
            / filename
        )

        output_path.parent.mkdir(parents=True, exist_ok=True)

        Image.fromarray(visualization).save(
            output_path,
            format="JPEG"
        )

        heatmap_url = f"/outputs/{filename}"

    except Exception as exc:
        print(f"Grad-CAM generation failed: {exc}")
        heatmap_url = None

    # Memory cleanup
    model.zero_grad(set_to_none=True)

    if "cam" in locals():
        del cam

    del input_tensor, outputs, probabilities
    gc.collect()

    return (
        {
            "acceptable": True,
            "issues": []
        },
        results,
        heatmap_url
    )


# --------------------------------------------------
# 9. File-based prediction
# --------------------------------------------------

def predict_image(image_path):
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    return predict_image_bytes(image_bytes)


# --------------------------------------------------
# 10. Local test
# --------------------------------------------------

if __name__ == "__main__":
    TEST_FOLDER = BASE_DIR / "data" / "color" / "Apple___healthy"
    images = list(TEST_FOLDER.glob("*"))

    if images:
        IMAGE_PATH = images[0]
        quality_info, results, heatmap = predict_image(IMAGE_PATH)

        print("\n================================")
        print("TOP 3 PREDICTIONS")
        print("================================")
        print("Image:", IMAGE_PATH.name)

        if results:
            for i, result in enumerate(results, start=1):
                print(
                    f"{i}. {result['disease']} -> "
                    f"{result['confidence']:.2f}%"
                )
        else:
            print("Image quality check failed:", quality_info["issues"])

        print("\nGrad-CAM:")
        print(heatmap)

    else:
        print("No images found.")
