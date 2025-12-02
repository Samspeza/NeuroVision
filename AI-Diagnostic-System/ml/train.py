# ml/train.py
"""
Treinamento de modelo para diagnóstico iridológico (íris).
- Carrega dataset pré-processado em data/processed/dataset_prepared.npz
- Constrói um modelo CNN simples com Keras/TensorFlow
- Rastreia parâmetros, métricas e o modelo com MLflow
- Salva o modelo final em /ml/models (compatível com backend do projeto)
- Uso: python train.py
"""

import os
import sys
import time
import json
import argparse
from pathlib import Path

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models, callbacks
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
import mlflow
import mlflow.keras


ROOT = Path(__file__).resolve().parents[1]  
PROCESSED_PATH = ROOT / "data" / "processed" / "dataset_prepared.npz"
MODELS_DIR = ROOT / "models"
DEFAULT_EPOCHS = 30
BATCH_SIZE = 32
IMG_SHAPE = (224, 224, 3)
RANDOM_SEED = 42

tf.random.set_seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)


def carregar_dataset(npz_path: Path):
    if not npz_path.exists():
        raise FileNotFoundError(f"Arquivo de dataset não encontrado: {npz_path}")
    data = np.load(npz_path, allow_pickle=True)
    X_train = data["X_train"]
    y_train = data["y_train"]
    X_val = data["X_val"]
    y_val = data["y_val"]
    X_test = data["X_test"]
    y_test = data["y_test"]
    return (X_train, y_train), (X_val, y_val), (X_test, y_test)


def codificar_labels(y_train, y_val, y_test):
    le = LabelEncoder()
    le.fit(y_train)
    y_train_enc = le.transform(y_train)
    y_val_enc = le.transform(y_val)
    y_test_enc = le.transform(y_test)
    num_classes = len(le.classes_)
    return y_train_enc, y_val_enc, y_test_enc, num_classes, le


def construir_modelo(input_shape, num_classes):
    inp = layers.Input(shape=input_shape)
    x = layers.Conv2D(32, (3, 3), activation="relu", padding="same")(inp)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Conv2D(64, (3, 3), activation="relu", padding="same")(x)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Conv2D(128, (3, 3), activation="relu", padding="same")(x)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Flatten()(x)
    x = layers.Dense(256, activation="relu")(x)
    x = layers.Dropout(0.5)(x)
    out = layers.Dense(num_classes, activation="softmax")(x)

    model = models.Model(inputs=inp, outputs=out, name="iris_cnn")
    model.compile(
        optimizer=keras.optimizers.Adam(),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def treinar(args):
    (X_train, y_train), (X_val, y_val), (X_test, y_test) = carregar_dataset(PROCESSED_PATH)
    y_train_enc, y_val_enc, y_test_enc, num_classes, label_encoder = codificar_labels(y_train, y_val, y_test)

    epochs = args.epochs or DEFAULT_EPOCHS
    batch_size = args.batch_size or BATCH_SIZE

    mlflow_tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    mlflow.set_tracking_uri(mlflow_tracking_uri)
    mlflow.set_experiment(args.experiment_name or "iris_diagnostic_experiment")

    run_name = f"run_{int(time.time())}"
    with mlflow.start_run(run_name=run_name) as run:
        run_id = run.info.run_id

        mlflow.log_param("epochs", epochs)
        mlflow.log_param("batch_size", batch_size)
        mlflow.log_param("input_shape", IMG_SHAPE)
        mlflow.log_param("num_classes", num_classes)
        mlflow.log_param("model_name", "iris_cnn")

        model = construir_modelo(IMG_SHAPE, num_classes)
        model.summary(print_fn=lambda s: mlflow.log_text(s + "\\n", "model_summary.txt"))

        early_stop = callbacks.EarlyStopping(monitor="val_loss", patience=6, restore_best_weights=True)
        reduce_lr = callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=3)
        timestamp = int(time.time())
        checkpoint_path = MODELS_DIR / f"iris_model_checkpoint_{timestamp}.h5"
        MODEL_CHECKPOINT_DIR = MODELS_DIR
        MODEL_CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
        model_checkpoint = callbacks.ModelCheckpoint(
            str(checkpoint_path),
            monitor="val_loss",
            save_best_only=True,
            save_weights_only=False,
        )

        # Treinamento
        history = model.fit(
            X_train, y_train_enc,
            validation_data=(X_val, y_val_enc),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[early_stop, reduce_lr, model_checkpoint],
            verbose=2,
        )

        # Log de métricas de histórico por época (ex.: accuracy/val_accuracy)
        for key, values in history.history.items():
            for epoch_idx, v in enumerate(values):
                mlflow.log_metric(f"{key}", v, step=epoch_idx)

        # Avaliação final no conjunto de teste
        test_loss, test_acc = model.evaluate(X_test, y_test_enc, verbose=0)
        mlflow.log_metric("test_loss", float(test_loss))
        mlflow.log_metric("test_accuracy", float(test_acc))

        # Predição e relatório detalhado
        y_pred_probs = model.predict(X_test)
        y_pred = np.argmax(y_pred_probs, axis=1)
        report = classification_report(y_test_enc, y_pred, target_names=label_encoder.classes_, output_dict=True)
        confmat = confusion_matrix(y_test_enc, y_pred).tolist()

        # Log do relatório e matriz de confusão
        mlflow.log_dict(report, "classification_report.json")
        mlflow.log_dict({"confusion_matrix": confmat}, "confusion_matrix.json")
        mlflow.log_text(json.dumps(label_encoder.classes_.tolist()), "label_classes.json")

        # Salvar e logar o modelo com MLflow (formato Keras)
        final_model_dir = MODELS_DIR / f"iris_model_final_{timestamp}"
        final_model_dir.mkdir(parents=True, exist_ok=True)
        # Salva no formato SavedModel
        model_save_path = final_model_dir / "saved_model"
        model.save(model_save_path, include_optimizer=False)
        # Logar no MLflow
        mlflow.keras.log_model(keras_model=model, artifact_path=f"models/iris_model_{timestamp}")

        mlflow.log_artifact(str(model_save_path), artifact_path="saved_models")  # opcional: artefatos adicionais

        print("✅ Treinamento concluído.")
        print(f"Run ID: {run_id}")
        print(f"Modelo salvo em: {model_save_path}")
        print(f"Checkpoint salvo em: {checkpoint_path}")

        # Retornar informações úteis
        return {
            "run_id": run_id,
            "model_path": str(model_save_path),
            "checkpoint": str(checkpoint_path),
            "test_accuracy": float(test_acc),
            "test_loss": float(test_loss),
        }


def parse_args():
    parser = argparse.ArgumentParser(description="Treinar modelo de diagnóstico de íris com MLflow.")
    parser.add_argument("--epochs", type=int, help="Número de épocas de treinamento")
    parser.add_argument("--batch-size", dest="batch_size", type=int, help="Tamanho do batch")
    parser.add_argument("--experiment-name", type=str, help="Nome do experimento MLflow")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    try:
        result = treinar(args)
        print("\\nResumo do treinamento:")
        for k, v in result.items():
            print(f" - {k}: {v}")
    except Exception as e:
        print(f"[ERRO] Falha no treinamento: {e}")
        sys.exit(1)
