"""
Splits a raw PlantVillage-style folder (one subfolder per class, full of images)
into train/val/test directories that torchvision.datasets.ImageFolder can read.

Expected input layout (after you download PlantVillage and unzip it):
    ml/data/raw/
        Tomato___Early_blight/
            img001.jpg
            img002.jpg
            ...
        Tomato___healthy/
            ...
        Potato___Late_blight/
            ...

Produces:
    ml/data/split/train/<class>/...
    ml/data/split/val/<class>/...
    ml/data/split/test/<class>/...

Usage:
    python dataset_prep.py --raw_dir ../data/raw --out_dir ../data/split \
        --train 0.7 --val 0.15 --test 0.15
"""
import argparse
import random
import shutil
from pathlib import Path


def split_dataset(raw_dir: Path, out_dir: Path, train_frac: float, val_frac: float, test_frac: float, seed: int = 42):
    assert abs(train_frac + val_frac + test_frac - 1.0) < 1e-6, "Splits must sum to 1.0"
    random.seed(seed)

    class_dirs = [d for d in raw_dir.iterdir() if d.is_dir()]
    if not class_dirs:
        raise SystemExit(f"No class subfolders found in {raw_dir}. Did you point --raw_dir at the right place?")

    summary = {}
    for class_dir in class_dirs:
        images = [p for p in class_dir.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"}]
        random.shuffle(images)

        n = len(images)
        n_train = int(n * train_frac)
        n_val = int(n * val_frac)
        splits = {
            "train": images[:n_train],
            "val": images[n_train:n_train + n_val],
            "test": images[n_train + n_val:],
        }

        for split_name, split_images in splits.items():
            dest = out_dir / split_name / class_dir.name
            dest.mkdir(parents=True, exist_ok=True)
            for img_path in split_images:
                shutil.copy2(img_path, dest / img_path.name)

        summary[class_dir.name] = {k: len(v) for k, v in splits.items()}

    print("Split complete. Per-class counts:")
    for cls, counts in summary.items():
        print(f"  {cls}: {counts}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw_dir", type=str, required=True)
    parser.add_argument("--out_dir", type=str, required=True)
    parser.add_argument("--train", type=float, default=0.7)
    parser.add_argument("--val", type=float, default=0.15)
    parser.add_argument("--test", type=float, default=0.15)
    args = parser.parse_args()

    split_dataset(Path(args.raw_dir), Path(args.out_dir), args.train, args.val, args.test)
