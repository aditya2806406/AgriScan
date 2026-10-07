from pathlib import Path

import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image

from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget
from pytorch_grad_cam.utils.image import show_cam_on_image

# --------------------------------------------------
# 1. Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "models" / "mobilenetv2_test.pth"


# --------------------------------------------------
# 2. Device
# --------------------------------------------------

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("Using device:", DEVICE)


# --------------------------------------------------
# 3. Load checkpoint
# --------------------------------------------------

checkpoint = torch.load(
    MODEL_PATH,
    map_location=DEVICE
)

classes = checkpoint["classes"]

print("Model checkpoint loaded.")
print("Number of classes:", len(classes))


# --------------------------------------------------
# 4. Create model
# --------------------------------------------------

model = models.mobilenet_v2(weights=None)

model.classifier[1] = nn.Linear(
    model.classifier[1].in_features,
    len(classes)
)


# --------------------------------------------------
# 5. Load trained weights
# --------------------------------------------------

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model = model.to(DEVICE)

model.eval()

print("Trained model loaded successfully.")



# --------------------------------------------------
# Grad-CAM setup
# --------------------------------------------------

target_layers = [
    model.features[-1]
]

cam = GradCAM(
    model=model,
    target_layers=target_layers
)

print("Grad-CAM ready.")


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
# 7. Prediction + Grad-CAM
# --------------------------------------------------

from PIL import Image, ImageFilter, ImageStat

def check_image_quality(image: Image.Image) -> tuple[bool, list[str]]:
    issues = []
    width, height = image.size
    
    # 1. Size check
    if width < 50 or height < 50:
        issues.append("Image is too small (minimum 50x50 pixels).")

    # 2. Brightness check (mean pixel value)
    stat = ImageStat.Stat(image.convert("L"))
    mean_brightness = stat.mean[0]
    if mean_brightness < 15:
        issues.append("Image is extremely dark.")
    elif mean_brightness > 240:
        issues.append("Image is extremely bright or overexposed.")

    # 3. Blur check (Laplacian variance)
    # Apply FIND_EDGES which acts similarly to a Laplacian filter
    edges = image.convert("L").filter(ImageFilter.FIND_EDGES)
    edge_stat = ImageStat.Stat(edges)
    # edge_stat.var[0] gives variance of the edges
    if edge_stat.var[0] < 50:  # conservative threshold
        issues.append("Image appears too blurry.")

    acceptable = len(issues) == 0
    return acceptable, issues

def predict_image_bytes(image_bytes):
    import io
    import base64
    import uuid
    import os
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    
    acceptable, issues = check_image_quality(image)
    if not acceptable:
        return {"acceptable": False, "issues": issues}, None, None

    image_tensor = transform(image)
    input_tensor = image_tensor.unsqueeze(0).to(DEVICE)

    # Prediction
    with torch.no_grad():
        outputs = model(input_tensor)

    probabilities = torch.softmax(outputs, dim=1)
    top_probabilities, top_indices = torch.topk(probabilities, 3, dim=1)

    results = []
    for probability, index in zip(top_probabilities[0], top_indices[0]):
        results.append({
            "disease": classes[index.item()],
            "confidence": probability.item() * 100
        })

    # Grad-CAM for top prediction
    predicted_index = top_indices[0][0].item()
    targets = [ClassifierOutputTarget(predicted_index)]
    
    grayscale_cam = cam(input_tensor=input_tensor, targets=targets)
    grayscale_cam = grayscale_cam[0]

    # Prepare original image for visualization
    original_image = image.resize((224, 224))
    rgb_image = (
        torch.tensor(list(original_image.getdata()), dtype=torch.float32)
        .reshape(224, 224, 3)
        .numpy() / 255.0
    )

    visualization = show_cam_on_image(rgb_image, grayscale_cam, use_rgb=True)
    
    filename = f"{uuid.uuid4().hex}.jpg"
    output_path = BASE_DIR.parent / "app" / "outputs" / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    Image.fromarray(visualization).save(output_path, format="JPEG")
    heatmap_url = f"/outputs/{filename}"

    return {"acceptable": True, "issues": []}, results, heatmap_url

def predict_image(image_path):

    image = Image.open(image_path).convert("RGB")

    image_tensor = transform(image)

    input_tensor = image_tensor.unsqueeze(0).to(DEVICE)

    # Prediction
    with torch.no_grad():
        outputs = model(input_tensor)

    probabilities = torch.softmax(
        outputs,
        dim=1
    )

    top_probabilities, top_indices = torch.topk(
        probabilities,
        3,
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

    # Grad-CAM for top prediction
    predicted_index = top_indices[0][0].item()

    targets = [
        ClassifierOutputTarget(predicted_index)
    ]

    grayscale_cam = cam(
        input_tensor=input_tensor,
        targets=targets
    )

    grayscale_cam = grayscale_cam[0]

    # Prepare original image for visualization
    original_image = Image.open(
        image_path
    ).convert("RGB")

    original_image = original_image.resize(
        (224, 224)
    )

    rgb_image = (
        torch.tensor(
            list(original_image.getdata()),
            dtype=torch.float32
        )
        .reshape(224, 224, 3)
        .numpy()
        / 255.0
    )

    visualization = show_cam_on_image(
        rgb_image,
        grayscale_cam,
        use_rgb=True
    )

    output_path = (
        BASE_DIR
        / "outputs"
        / "gradcam_result.jpg"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    Image.fromarray(
        visualization
    ).save(output_path)

    return results, output_path
# --------------------------------------------------
# 8. Test prediction
# --------------------------------------------------

if __name__ == "__main__":

    TEST_FOLDER = (
        BASE_DIR
        / "data"
        / "color"
        / "Apple___healthy"
    )

    images = list(TEST_FOLDER.glob("*"))

    if images:

        IMAGE_PATH = images[0]

        results, heatmap_path = predict_image(
            IMAGE_PATH
        )

        print("\n================================")
        print("TOP 3 PREDICTIONS")
        print("================================")

        print("Image:", IMAGE_PATH.name)
        print("Actual class: Apple___healthy")

        for i, result in enumerate(
            results,
            start=1
        ):
            print(
                f"{i}. {result['disease']} "
                f"-> {result['confidence']:.2f}%"
            )

        print("\nGrad-CAM saved to:")
        print(heatmap_path)

    else:

        print("No images found.")