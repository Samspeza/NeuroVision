# ml/preprocess.py
"""
Pré-processamento de imagens de íris para diagnósticos iridológicos.
Etapas:
- Carregamento das imagens brutas em data/raw/
- Segmentação circular para isolar a íris
- Remoção de reflexos e normalização
- Redimensionamento para entrada da rede neural
- Divisão em conjuntos de treino, validação e teste
"""

import os
import cv2
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split

RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"
IMG_SIZE = (224, 224)

def segmentar_iris(imagem):
    """Isola a região da íris por detecção de círculos de borda."""
    gray = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=100,
        param1=100,
        param2=30,
        minRadius=30,
        maxRadius=120
    )

    if circles is not None:
        circles = np.uint16(np.around(circles))
        x, y, r = circles[0][0]
        mask = np.zeros_like(gray)
        cv2.circle(mask, (x, y), r, (255, 255, 255), -1)
        result = cv2.bitwise_and(imagem, imagem, mask=mask)
        return result
    return imagem

def remover_reflexos(imagem):
    """Reduz reflexos especulares através de threshold adaptativo e inpainting."""
    gray = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)[1]
    inpainted = cv2.inpaint(imagem, mask, 5, cv2.INPAINT_TELEA)
    return inpainted

def preprocessar_imagem(path):
    """Aplica o pipeline completo a uma imagem individual."""
    imagem = cv2.imread(path)
    if imagem is None:
        raise ValueError(f"Não foi possível carregar {path}")

    imagem = segmentar_iris(imagem)
    imagem = remover_reflexos(imagem)
    imagem = cv2.resize(imagem, IMG_SIZE)
    imagem = imagem / 255.0  # normalização
    return imagem

def carregar_dataset():
    """Carrega todas as imagens do diretório raw e gera os splits."""
    imagens, labels = [], []

    for classe in os.listdir(RAW_DIR):
        classe_path = os.path.join(RAW_DIR, classe)
        if not os.path.isdir(classe_path):
            continue
        for arquivo in os.listdir(classe_path):
            if arquivo.lower().endswith(('.jpg', '.png', '.jpeg')):
                path = os.path.join(classe_path, arquivo)
                try:
                    img = preprocessar_imagem(path)
                    imagens.append(img)
                    labels.append(classe)
                except Exception as e:
                    print(f"[ERRO] Falha ao processar {arquivo}: {e}")

    imagens = np.array(imagens, dtype=np.float32)
    labels = np.array(labels)

    X_train, X_temp, y_train, y_temp = train_test_split(imagens, labels, test_size=0.3, stratify=labels, random_state=42)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, stratify=y_temp, random_state=42)

    os.makedirs(PROCESSED_DIR, exist_ok=True)
    np.savez_compressed(os.path.join(PROCESSED_DIR, "dataset_prepared.npz"),
                        X_train=X_train, y_train=y_train,
                        X_val=X_val, y_val=y_val,
                        X_test=X_test, y_test=y_test)

    print(f"✅ Dataset pré-processado e salvo em {PROCESSED_DIR}/dataset_prepared.npz")
    return (X_train, y_train), (X_val, y_val), (X_test, y_test)

if __name__ == "__main__":
    carregar_dataset()