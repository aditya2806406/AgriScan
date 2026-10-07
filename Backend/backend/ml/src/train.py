from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import models

from dataset_prep import train_loader, val_loader, classes


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
# 2. Load pretrained MobileNetV2
# --------------------------------------------------

print("\nLoading MobileNetV2...")

model = models.mobilenet_v2(
    weights=models.MobileNet_V2_Weights.DEFAULT
)


# --------------------------------------------------
# 3. Freeze feature extractor
# --------------------------------------------------

for param in model.features.parameters():
    param.requires_grad = False


# --------------------------------------------------
# 4. Replace classifier
# --------------------------------------------------

num_classes = len(classes)

model.classifier[1] = nn.Linear(
    model.classifier[1].in_features,
    num_classes
)

model = model.to(DEVICE)


print("Number of classes:", num_classes)
print("Model output classes:", model.classifier[1].out_features)


# --------------------------------------------------
# 5. Loss
# --------------------------------------------------

criterion = nn.CrossEntropyLoss()


# --------------------------------------------------
# 6. Optimizer
# --------------------------------------------------

optimizer = optim.Adam(
    model.classifier[1].parameters(),
    lr=0.001
)


# --------------------------------------------------
# 7. Training
# --------------------------------------------------

def train_one_epoch():

    model.train()

    running_loss = 0
    correct = 0
    total = 0

    for images, labels in train_loader:

        images = images.to(DEVICE)
        labels = labels.to(DEVICE)

        optimizer.zero_grad()

        outputs = model(images)

        loss = criterion(outputs, labels)

        loss.backward()

        optimizer.step()

        running_loss += loss.item() * images.size(0)

        predictions = outputs.argmax(dim=1)

        correct += (predictions == labels).sum().item()

        total += labels.size(0)

    return (
        running_loss / total,
        correct / total
    )


# --------------------------------------------------
# 8. Validation
# --------------------------------------------------

def validate():

    model.eval()

    running_loss = 0
    correct = 0
    total = 0

    with torch.no_grad():

        for images, labels in val_loader:

            images = images.to(DEVICE)
            labels = labels.to(DEVICE)

            outputs = model(images)

            loss = criterion(outputs, labels)

            running_loss += loss.item() * images.size(0)

            predictions = outputs.argmax(dim=1)

            correct += (predictions == labels).sum().item()

            total += labels.size(0)

    return (
        running_loss / total,
        correct / total
    )


# --------------------------------------------------
# 9. Run one training epoch
# --------------------------------------------------

print("\nStarting training test...")

train_loss, train_acc = train_one_epoch()

print("Training completed.")

val_loss, val_acc = validate()


# --------------------------------------------------
# 10. Results
# --------------------------------------------------

print("\nResults")
print("--------------------------------")

print(f"Training loss:     {train_loss:.4f}")
print(f"Training accuracy: {train_acc:.4f}")

print(f"Validation loss:   {val_loss:.4f}")
print(f"Validation accuracy: {val_acc:.4f}")


# --------------------------------------------------
# 11. Save model
# --------------------------------------------------

MODEL_DIR = (
    Path(__file__).resolve().parent.parent
    / "models"
)

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)

MODEL_PATH = MODEL_DIR / "mobilenetv2_test.pth"

torch.save(
    {
        "model_state_dict": model.state_dict(),
        "classes": classes
    },
    MODEL_PATH
)

print("\nModel saved to:")
print(MODEL_PATH)

print("\nTraining test completed successfully.")