import os
import json
from PIL import Image

DATASET_DIR = "ml/datasets/raw"
OUTPUT_FILE = "ml/datasets/metadata.json"

def generate_metadata():
    metadata = []

    for img_name in os.listdir(DATASET_DIR):
        if img_name.lower().endswith((".png", ".jpg", ".jpeg")):
            img_path = os.path.join(DATASET_DIR, img_name)
            with Image.open(img_path) as img:
                width, height = img.size

            metadata.append({
                "file": img_name,
                "width": width,
                "height": height,
                "mode": img.mode
            })

    with open(OUTPUT_FILE, "w") as f:
        json.dump(metadata, f, indent=4)

    print(f"Metadados gerados com sucesso → {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_metadata()
