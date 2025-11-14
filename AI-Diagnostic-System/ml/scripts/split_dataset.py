import os
import shutil
import random

DATASET_DIR = "ml/datasets/raw"
OUTPUT_DIR = "ml/datasets/splitted"

SPLIT_RATIOS = {
    "train": 0.7,
    "val": 0.15,
    "test": 0.15
}

def create_dirs():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for split in SPLIT_RATIOS.keys():
        os.makedirs(os.path.join(OUTPUT_DIR, split), exist_ok=True)

def split_dataset():
    create_dirs()

    images = [f for f in os.listdir(DATASET_DIR) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    random.shuffle(images)

    total = len(images)
    train_end = int(SPLIT_RATIOS["train"] * total)
    val_end = train_end + int(SPLIT_RATIOS["val"] * total)

    splits = {
        "train": images[:train_end],
        "val": images[train_end:val_end],
        "test": images[val_end:]
    }

    for split, files in splits.items():
        for img in files:
            shutil.copy(os.path.join(DATASET_DIR, img), os.path.join(OUTPUT_DIR, split, img))

    print(f"Dataset dividido com sucesso → {OUTPUT_DIR}")

if __name__ == "__main__":
    split_dataset()
