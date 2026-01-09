import os
import json
from pathlib import Path
from typing import List, Tuple, Union

import numpy as np
import matplotlib.pyplot as plt
import mlflow
import tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix, roc_curve, auc
from sklearn.preprocessing import label_binarize

ROOT = Path(__file__).resolve().parents[1]
PROCESSED_PATH = ROOT / "data" / "processed" / "dataset_prepared.npz"
MODELS_DIR = ROOT / "models"
ARTIFACTS_DIR = ROOT / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

ModelPath = Union[Path, str]


def load_npz_dataset(npz_path: Path) -> Tuple[np.ndarray, np.ndarray]:
    if not npz_path.exists():
        raise FileNotFoundError(f"Dataset não encontrado: {npz_path}")
    data = np.load(npz_path, allow_pickle=True)
    return data["X_test"], data["y_test"]


def find_latest_model(models_dir: Path) -> Path:
    if not models_dir.exists():
        raise FileNotFoundError("Diretório de modelos não existe.")

    candidates = list(models_dir.glob("**/saved_model")) + list(models_dir.glob("**/*.h5"))
    if not candidates:
        raise FileNotFoundError("Nenhum modelo encontrado em /ml/models.")

    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0]


def load_keras_model(model_path: Path) -> tf.keras.Model:
    return tf.keras.models.load_model(str(model_path))


def resolve_classes(models_dir: Path, y_test: np.ndarray) -> List[str]:
    label_file = models_dir / "label_classes.json"
    if label_file.exists():
        try:
            return json.loads(label_file.read_text(encoding="utf-8"))
        except Exception:
            pass
    return [str(c) for c in np.unique(y_test)]


def encode_labels(y_test: np.ndarray, classes: List[str]) -> np.ndarray:
    try:
        return y_test.astype(int)
    except Exception:
        mapping = {label: idx for idx, label in enumerate(classes)}
        return np.array([mapping.get(label, 0) for label in y_test])


def save_json_report(report: dict, filename: str) -> Path:
    path = ARTIFACTS_DIR / filename
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Relatório salvo → {path}")
    return path


def plot_confusion(cm: np.ndarray, class_names: List[str], out_path: Path):
    plt.figure(figsize=(6, 6))
    plt.imshow(cm, interpolation="nearest")
    plt.title("Matriz de Confusão")
    plt.colorbar()

    ticks = np.arange(len(class_names))
    plt.xticks(ticks, class_names, rotation=45)
    plt.yticks(ticks, class_names)

    threshold = cm.max() / 2
    for i, j in np.ndindex(cm.shape):
        plt.text(j, i, f"{cm[i, j]}", ha="center", color="white" if cm[i, j] > threshold else "black")

    plt.ylabel("Label real")
    plt.xlabel("Predição")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"Matriz salva → {out_path}")


def plot_roc_curves(y_true: np.ndarray, y_probs: np.ndarray, class_names: List[str], out_path: Path):
    y_bin = label_binarize(y_true, classes=range(len(class_names)))

    plt.figure()
    for i, name in enumerate(class_names):
        fpr, tpr, _ = roc_curve(y_bin[:, i], y_probs[:, i])
        roc_auc = auc(fpr, tpr)
        plt.plot(fpr, tpr, lw=2, label=f"Classe {name} (AUC={roc_auc:.2f})")

    plt.plot([0, 1], [0, 1], "k--", lw=2)
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("Curvas ROC")
    plt.legend(loc="lower right")
    plt.savefig(out_path)
    plt.close()
    print(f"ROC salvo → {out_path}")


def log_mlflow(mlflow_uri: str, artifacts: List[Path]):
    try:
        mlflow.set_tracking_uri(mlflow_uri)
        mlflow.set_experiment("iris_diagnostic_evaluation")

        with mlflow.start_run():
            for artifact in artifacts:
                if artifact.exists():
                    mlflow.log_artifact(str(artifact))
        print("MLflow log concluído.")
    except Exception as e:
        print(f"Erro no MLflow log: {e}")


def evaluate_model():
    X_test, y_test = load_npz_dataset(PROCESSED_PATH)
    model_path = find_latest_model(MODELS_DIR)

    print(f"Carregando modelo → {model_path}")
    model = load_keras_model(model_path)

    y_probs = model.predict(X_test)
    y_pred = np.argmax(y_probs, axis=1)

    class_names = resolve_classes(MODELS_DIR, y_test)
    y_true = encode_labels(y_test, class_names)

    cm = confusion_matrix(y_true, y_pred)
    report = classification_report(y_true, y_pred, target_names=class_names, output_dict=True)

    results = {
        "accuracy": float(np.mean(y_pred == y_true)),
        "confusion_matrix": cm.tolist(),
        "classification_report": report,
    }

    report_path = save_json_report(results, "evaluation_report.json")
    cm_img_path = ARTIFACTS_DIR / "confusion_matrix.png"
    plot_confusion(cm, class_names, cm_img_path)

    roc_img_path = ARTIFACTS_DIR / "roc.png"
    try:
        plot_roc_curves(y_true, y_probs, class_names, roc_img_path)
    except Exception:
        print("Falha ao gerar curvas ROC.")

    mlflow_uri = os.getenv("MLFLOW_TRACKING_URI")
    if mlflow_uri:
        log_mlflow(mlflow_uri, [report_path, cm_img_path, roc_img_path])

    print("Avaliação finalizada com sucesso.")


if __name__ == "__main__":
    evaluate_model()
