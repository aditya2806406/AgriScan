from pathlib import Path

import numpy as np
import torch
from sklearn.model_selection import train_test_split
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, Subset


# --------------------------------------------------
# 1. Dataset path
# --------------------------------------------------

DATASET_DIR = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "color"
)


# --------------------------------------------------
# 2. Transformations
# --------------------------------------------------

train_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(15),
    transforms.ColorJitter(
        brightness=0.2,
        contrast=0.2
    ),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


eval_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


# --------------------------------------------------
# 3. Load datasets
# --------------------------------------------------

train_full = datasets.ImageFolder(
    root=DATASET_DIR,
    transform=train_transform
)

eval_full = datasets.ImageFolder(
    root=DATASET_DIR,
    transform=eval_transform
)


classes = train_full.classes
targets = np.array(train_full.targets)

print("Dataset path:")
print(DATASET_DIR)

print("\nNumber of images:", len(train_full))
print("Number of classes:", len(classes))


# --------------------------------------------------
# 4. Stratified train/validation/test split
# --------------------------------------------------

indices = np.arange(len(train_full))

train_indices, temp_indices = train_test_split(
    indices,
    test_size=0.30,
    random_state=42,
    stratify=targets
)

val_indices, test_indices = train_test_split(
    temp_indices,
    test_size=0.50,
    random_state=42,
    stratify=targets[temp_indices]
)


# --------------------------------------------------
# 5. Create subsets
# --------------------------------------------------

train_dataset = Subset(
    train_full,
    train_indices
)

val_dataset = Subset(
    eval_full,
    val_indices
)

test_dataset = Subset(
    eval_full,
    test_indices
)


print("\nDataset split:")
print("Training:", len(train_dataset))
print("Validation:", len(val_dataset))
print("Testing:", len(test_dataset))


# --------------------------------------------------
# 6. DataLoaders
# --------------------------------------------------

BATCH_SIZE = 16

train_loader = DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True,
    num_workers=0
)

val_loader = DataLoader(
    val_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=0
)

test_loader = DataLoader(
    test_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=0
)


# --------------------------------------------------
# 7. Test a batch
# --------------------------------------------------

images, labels = next(iter(train_loader))

print("\nFirst training batch:")
print("Image shape:", images.shape)
print("Label shape:", labels.shape)

print("\nDataset preparation completed successfully.")