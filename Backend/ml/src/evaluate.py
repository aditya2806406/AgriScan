"""
Evaluates the trained model on the held-out test split and reports
per-class precision/recall — not just overall accuracy, since some
disease classes are much rarer than others in PlantVillage.

Usage:
    python evaluate.py --data_dir ../data/split --model ../models/mobilenetv2_plantvillage.pt
"""
import argparse
from pathlib import Path

import torch
from sklearn.metrics import classification_report, confusion_matrix
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms
import torch.nn as nn

IMG_SIZE = 224


def load_model(model_path: Path, device):
    checkpoint = torch.load(model_path, map_location=device)
    classes = checkpoint["classes"]

    model = models.mobilenet_v2(weights=None)
    in_features = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(in_features, len(classes))
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device).eval()
    return model, classes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, required=True)
    parser.add_argument("--model", type=str, required=True)
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model, classes = load_model(Path(args.model), device)

    eval_tf = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    test_ds = datasets.ImageFolder(Path(args.data_dir) / "test", transform=eval_tf)
    assert test_ds.classes == classes, "Test set classes don't match the trained model's classes."
    test_loader = DataLoader(test_ds, batch_size=32, shuffle=False, num_workers=2)

    all_preds, all_labels = [], []
    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(device)
            outputs = model(images)
            preds = outputs.argmax(1).cpu()
            all_preds.extend(preds.tolist())
            all_labels.extend(labels.tolist())

    print(classification_report(all_labels, all_preds, target_names=classes, zero_division=0))
    print("Confusion matrix (rows=actual, cols=predicted):")
    print(confusion_matrix(all_labels, all_preds))


if __name__ == "__main__":
    main()
