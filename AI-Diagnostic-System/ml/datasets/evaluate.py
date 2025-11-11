# ml/evaluate.py
"""
Avaliação do modelo treinado de diagnóstico iridológico.
- Carrega modelo salvo em /ml/models (SavedModel ou Keras .h5)
- Carrega dataset pré-processado em data/processed/dataset_prepared.npz
- Calcula métricas: accuracy, precision, recall, F1, AUC (quando aplicável)
- Gera matriz de confusão e ROC curves (se binário)
- Salva relatórios em /ml/artifacts e faz log opcional no MLflow
"""

import os
import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix, roc_curve, auc
from sklearn.preprocessing import label_binarize
import mlflow
import tensorflow as tf

ROOT = Path(__file__).resolve().parents[1]
PROCESSED_PATH = ROOT / "data" / "processed" / "dataset_prepared.npz"
MODELS_DIR = ROOT / "models"
ARTIFACTS_DIR = ROOT / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


def carregar_dataset(npz_path: Path):
    if not npz_path.exists():
        raise FileNotFoundError(f"Arquivo de dataset não encontrado: {npz_path}")
    data = np.load(npz_path, allow_pickle=True)
    X_test = data["X_test"]
    y_test = data["y_test"]
    return X_test, y_test


def localizar_modelo(models_dir: Path):
    # Busca diretórios/saved_model mais recentes
    if not models_dir.exists():
        raise FileNotFoundError("Diretório de modelos não encontrado.")
    # Procurar por subpastas com saved_model ou arquivos .h5
    candidates = list(models_dir.glob("**/saved_model")) + list(models_dir.glob("**/*.h5"))
    if not candidates:
        raise FileNotFoundError("Nenhum modelo salvo encontrado em /ml/models.")
    # Ordenar por última modificação e retornar o mais recente
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0]


def carregar_modelo(path):
    # TensorFlow SavedModel ou .h5
    if path.is_dir():
        model = tf.keras.models.load_model(str(path))
    else:
        model = tf.keras.models.load_model(str(path))
    return model


def salvar_relatorio(rel, name="evaluation_report.json"):
    out_path = ARTIFACTS_DIR / name
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(rel, f, indent=2, ensure_ascii=False)
    print(f"Relatório salvo em: {out_path}")
    return out_path


def plot_confusion_matrix(cm, classes, out_path: Path):
    plt.figure(figsize=(6, 6))
    plt.imshow(cm, interpolation='nearest')
    plt.title('Confusion matrix')
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)
    fmt = 'd'
    thresh = cm.max() / 2.
    for i, j in np.ndindex(cm.shape):
        plt.text(j, i, format(cm[i, j], fmt), horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"Matriz de confusão salva em: {out_path}")


def plot_roc(y_true, y_score, classes, out_path: Path):
    # Multi-classe: binarizar
    y_test_bin = label_binarize(y_true, classes=range(len(classes)))
    plt.figure()
    for i in range(len(classes)):
        fpr, tpr, _ = roc_curve(y_test_bin[:, i], y_score[:, i])
        roc_auc = auc(fpr, tpr)
        plt.plot(fpr, tpr, lw=2, label=f"ROC curve class {classes[i]} (area = {roc_auc:.2f})")
    plt.plot([0, 1], [0, 1], 'k--', lw=2)
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC curves')
    plt.legend(loc="lower right")
    plt.savefig(out_path)
    plt.close()
    print(f"ROC salvo em: {out_path}")


def avaliar():
    X_test, y_test = carregar_dataset(PROCESSED_PATH)
    model_path = localizar_modelo(MODELS_DIR)
    print(f"Carregando modelo de: {model_path}")
    model = carregar_modelo(model_path)

    # Prever
    y_probs = model.predict(X_test)
    y_pred = np.argmax(y_probs, axis=1)

    # Se labels originais forem strings, tentar carregar classes do arquivo label_classes.json
    classes = None
    label_classes_file = MODELS_DIR / "label_classes.json"
    if label_classes_file.exists():
        try:
            classes = json.loads(label_classes_file.read_text(encoding="utf-8"))
        except Exception:
            classes = None
    if classes is None:
        classes = [str(i) for i in np.unique(y_test)]

    # Se y_test contiver strings, transformar para índices
    try:
        y_test_arr = np.array(y_test, dtype=int)
    except Exception:
        # map strings to indices based on classes
        mapping = {c: i for i, c in enumerate(classes)}
        y_test_arr = np.array([mapping.get(v, 0) for v in y_test])

    cm = confusion_matrix(y_test_arr, y_pred)
    report = classification_report(y_test_arr, y_pred, target_names=classes, output_dict=True)

    # Salvar relatórios
    rel = {
        "confusion_matrix": cm.tolist(),
        "classification_report": report,
    }
    salvar_relatorio(rel, name="evaluation_report.json")

    # Salvar matriz de confusão como imagem
    cm_path = ARTIFACTS_DIR / "confusion_matrix.png"
    plot_confusion_matrix(cm, classes, cm_path)

    # Tentar gerar ROC (se multi-classe)
    roc_path = ARTIFACTS_DIR / "roc.png"
    try:
        plot_roc(y_test_arr, y_probs, classes, roc_path)
    except Exception as e:
        print(f"Impossível calcular ROC: {e}")

    # Logar no MLflow (se disponível)
    mlflow_tracking_uri = os.getenv("MLFLOW_TRACKING_URI", None)
    if mlflow_tracking_uri:
        try:
            mlflow.set_tracking_uri(mlflow_tracking_uri)
            mlflow.set_experiment("iris_diagnostic_evaluation")
            with mlflow.start_run():
                mlflow.log_artifact(str(ARTIFACTS_DIR / "evaluation_report.json"))
                mlflow.log_artifact(str(cm_path))
                if roc_path.exists():
                    mlflow.log_artifact(str(roc_path))
                print("Relatórios enviados para MLflow.")
        except Exception as e:
            print(f"Falha ao logar no MLflow: {e}")

    print("✅ Avaliação concluída.")


if __name__ == '__main__':
    avaliar()
