from pathlib import Path

import torch
import torch.nn as nn
import matplotlib.pyplot as plt
import seaborn as sns

from torchvision import models

from sklearn.metrics import confusion_matrix

from dataset_prep import test_loader, classes


# --------------------------------------------------
# 1. Device
# --------------------------------------------------

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("Using device:", DEVICE)


# --------------------------------------------------
# 2. Model path
# --------------------------------------------------

MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    / "models"
    / "mobilenetv2_test.pth"
)


# --------------------------------------------------
# 3. Create MobileNetV2
# --------------------------------------------------

model = models.mobilenet_v2(weights=None)

model.classifier[1] = nn.Linear(
    model.classifier[1].in_features,
    len(classes)
)


# --------------------------------------------------
# 4. Load trained model
# --------------------------------------------------

checkpoint = torch.load(
    MODEL_PATH,
    map_location=DEVICE
)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model = model.to(DEVICE)

model.eval()


print("Model loaded successfully.")


# --------------------------------------------------
# 5. Predictions
# --------------------------------------------------

all_labels = []
all_predictions = []


print("Generating predictions...")


with torch.no_grad():

    for images, labels in test_loader:

        images = images.to(DEVICE)

        outputs = model(images)

        predictions = outputs.argmax(dim=1)

        all_predictions.extend(
            predictions.cpu().numpy()
        )

        all_labels.extend(
            labels.numpy()
        )


# --------------------------------------------------
# 6. Confusion matrix
# --------------------------------------------------

cm = confusion_matrix(
    all_labels,
    all_predictions
)


# --------------------------------------------------
# 7. Plot
# --------------------------------------------------

plt.figure(
    figsize=(24, 20)
)

sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=classes,
    yticklabels=classes
)

plt.xlabel("Predicted Label")

plt.ylabel("True Label")

plt.title(
    "PlantVillage - MobileNetV2 Confusion Matrix"
)

plt.xticks(
    rotation=90,
    fontsize=8
)

plt.yticks(
    rotation=0,
    fontsize=8
)

plt.tight_layout()


# --------------------------------------------------
# 8. Save
# --------------------------------------------------

OUTPUT_DIR = (
    Path(__file__).resolve().parent.parent
    / "outputs"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


OUTPUT_PATH = (
    OUTPUT_DIR
    / "confusion_matrix.png"
)


plt.savefig(
    OUTPUT_PATH,
    dpi=300
)

plt.close()


print("\nConfusion matrix saved to:")

print(OUTPUT_PATH)

print("\nDone.")from pathlib import Path

import torch
import torch.nn as nn
import matplotlib.pyplot as plt
import seaborn as sns

from torchvision import models

from sklearn.metrics import confusion_matrix

from dataset_prep import test_loader, classes


# --------------------------------------------------
# 1. Device
# --------------------------------------------------

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("Using device:", DEVICE)


# --------------------------------------------------
# 2. Model path
# --------------------------------------------------

MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    / "models"
    / "mobilenetv2_test.pth"
)


# --------------------------------------------------
# 3. Create MobileNetV2
# --------------------------------------------------

model = models.mobilenet_v2(weights=None)

model.classifier[1] = nn.Linear(
    model.classifier[1].in_features,
    len(classes)
)


# --------------------------------------------------
# 4. Load trained model
# --------------------------------------------------

checkpoint = torch.load(
    MODEL_PATH,
    map_location=DEVICE
)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model = model.to(DEVICE)

model.eval()


print("Model loaded successfully.")


# --------------------------------------------------
# 5. Predictions
# --------------------------------------------------

all_labels = []
all_predictions = []


print("Generating predictions...")


with torch.no_grad():

    for images, labels in test_loader:

        images = images.to(DEVICE)

        outputs = model(images)

        predictions = outputs.argmax(dim=1)

        all_predictions.extend(
            predictions.cpu().numpy()
        )

        all_labels.extend(
            labels.numpy()
        )


# --------------------------------------------------
# 6. Confusion matrix
# --------------------------------------------------

cm = confusion_matrix(
    all_labels,
    all_predictions
)


# --------------------------------------------------
# 7. Plot
# --------------------------------------------------

plt.figure(
    figsize=(24, 20)
)

sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=classes,
    yticklabels=classes
)

plt.xlabel("Predicted Label")

plt.ylabel("True Label")

plt.title(
    "PlantVillage - MobileNetV2 Confusion Matrix"
)

plt.xticks(
    rotation=90,
    fontsize=8
)

plt.yticks(
    rotation=0,
    fontsize=8
)

plt.tight_layout()


# --------------------------------------------------
# 8. Save
# --------------------------------------------------

OUTPUT_DIR = (
    Path(__file__).resolve().parent.parent
    / "outputs"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


OUTPUT_PATH = (
    OUTPUT_DIR
    / "confusion_matrix.png"
)


plt.savefig(
    OUTPUT_PATH,
    dpi=300
)

plt.close()


print("\nConfusion matrix saved to:")

print(OUTPUT_PATH)

print("\nDone.")