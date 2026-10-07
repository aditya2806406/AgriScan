from pathlib import Path

DATASET_DIR = Path(__file__).resolve().parent.parent / "data" / "color"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"}

classes = sorted(
    folder for folder in DATASET_DIR.iterdir()
    if folder.is_dir()
)

print("Dataset path:")
print(DATASET_DIR)

print("\nNumber of classes:", len(classes))

print("\nImage count per class:")
print("-" * 70)

total_images = 0

for i, folder in enumerate(classes):
    image_count = sum(
        1 for file in folder.iterdir()
        if file.suffix in IMAGE_EXTENSIONS
    )

    total_images += image_count

    print(f"{i:2d}. {folder.name:<50} {image_count}")

print("-" * 70)
print("Total images:", total_images)