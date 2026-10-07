from pathlib import Path

import torch
import torch.nn as nn
from torchvision import models

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

from dataset_prep import test_loader, classes


# --------------------------------------------------
# 1. Device
# --------------------------------------------------

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("Using device:", DEVICE)

if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))


# --------------------------------------------------
# 2. Model path
# --------------------------------------------------

MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    / "models"
    / "mobilenetv2_test.pth"
)

print("\nLoading model:")
print(MODEL_PATH)


# --------------------------------------------------
# 3. Create MobileNetV2 architecture
# --------------------------------------------------

model = models.mobilenet_v2(
    weights=None
)


# --------------------------------------------------
# 4. Replace classifier
# --------------------------------------------------

num_classes = len(classes)

model.classifier[1] = nn.Linear(
    model.classifier[1].in_features,
    num_classes
)


# --------------------------------------------------
# 5. Load trained weights
# --------------------------------------------------

checkpoint = torch.load(
    MODEL_PATH,
    map_location=DEVICE
)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model = model.to(DEVICE)


# --------------------------------------------------
# 6. Evaluation mode
# --------------------------------------------------

model.eval()


print("\nModel loaded successfully.")
print("Number of classes:", num_classes)


# --------------------------------------------------
# 7. Test model
# --------------------------------------------------

all_predictions = []
all_labels = []


print("\nEvaluating on test dataset...")


with torch.no_grad():

    for images, labels in test_loader:

        images = images.to(DEVICE)
        labels = labels.to(DEVICE)

        outputs = model(images)

        predictions = outputs.argmax(dim=1)

        all_predictions.extend(
            predictions.cpu().numpy()
        )

        all_labels.extend(
            labels.cpu().numpy()
        )


# --------------------------------------------------
# 8. Accuracy
# --------------------------------------------------

accuracy = accuracy_score(
    all_labels,
    all_predictions
)


print("\n================================")
print("TEST RESULTS")
print("================================")

print(
    f"Test accuracy: {accuracy:.4f}"
)

print(
    f"Test accuracy: {accuracy * 100:.2f}%"
)


# --------------------------------------------------
# 9. Classification report
# --------------------------------------------------

print("\n================================")
print("CLASSIFICATION REPORT")
print("================================")

print(
    classification_report(
        all_labels,
        all_predictions,
        target_names=classes,
        digits=4,
        zero_division=0
    )
)


# --------------------------------------------------
# 10. Confusion matrix
# --------------------------------------------------

cm = confusion_matrix(
    all_labels,
    all_predictions
)

print("\n================================")
print("CONFUSION MATRIX")
print("================================")

print(cm)


# --------------------------------------------------
# 11. Save results
# --------------------------------------------------

OUTPUT_DIR = (
    Path(__file__).resolve().parent.parent
    / "outputs"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


REPORT_PATH = OUTPUT_DIR / "evaluation_report.txt"

with open(REPORT_PATH, "w", encoding="utf-8") as f:

    f.write("PlantVillage MobileNetV2 Evaluation\n")
    f.write("====================================\n\n")

    f.write(
        f"Test accuracy: {accuracy:.4f}\n"
    )

    f.write(
        f"Test accuracy percentage: "
        f"{accuracy * 100:.2f}%\n\n"
    )

    f.write("Classification Report\n")
    f.write("=====================\n")

    f.write(
        classification_report(
            all_labels,
            all_predictions,
            target_names=classes,
            digits=4,
            zero_division=0
        )
    )

    f.write("\n\nConfusion Matrix\n")
    f.write("================\n")

    f.write(
        str(cm)
    )


print("\nEvaluation completed successfully.")

print("\nReport saved to:")
print(REPORT_PATH)