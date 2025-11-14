import os
import numpy as np
import cv2

DATASET_DIR = "ml/datasets/raw"
OUTPUT_DIR = "ml/datasets/numpy"

os.makedirs(OUTPUT_DIR, exist_ok=True)

IMG_SIZE = (224, 224)

def convert():
    for file in os.listdir(DATASET_DIR):
        if not file.lower().endswith((".png", ".jpg", ".jpeg")):
            continue

        img_path = os.path.join(DATASET_DIR, file)
        img = cv2.imread(img_path)
        img = cv2.resize(img, IMG_SIZE)
        img = img.astype("float32") / 255.0

        np.save(os.path.join(OUTPUT_DIR, file.replace(".jpg", ".npy").replace(".png", ".npy")), img)

    print(f"Conversão concluída → {OUTPUT_DIR}")

if __name__ == "__main__":
    convert()
