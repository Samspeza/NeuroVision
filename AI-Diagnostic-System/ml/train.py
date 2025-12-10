# ml/train.py - Versão SUPER FODA com Transfer Learning e Augmentation
"""
Treinamento de modelo robusto para diagnóstico iridológico (íris) usando Transfer Learning.
- Carrega dataset pré-processado.
- Utiliza uma rede pré-treinada (MobileNetV3Large) como base (Transfer Learning).
- Implementa Aumento de Dados (Data Augmentation) para maior robustez.
- Rastreia parâmetros, métricas, figuras de treinamento e o modelo com MLflow.
"""

import os
import sys
import time
import json
import argparse
from pathlib import Path
import matplotlib.pyplot as plt

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models, callbacks # type: ignore
from tensorflow.keras.applications import MobileNetV3Large # type: ignore # ⚡️ Nova Base
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
import mlflow
import mlflow.keras


# --- Configurações Globais ---
ROOT = Path(__file__).resolve().parents[1]
PROCESSED_PATH = ROOT / "data" / "processed" / "dataset_prepared.npz"
MODELS_DIR = ROOT / "models"
DEFAULT_EPOCHS = 50 # Aumentado
BATCH_SIZE = 32
IMG_SHAPE = (224, 224, 3)
RANDOM_SEED = 42
LEARNING_RATE = 1e-4 

tf.random.set_seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

def carregar_dataset(npz_path: Path):
    # ... (Função idêntica à original)
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
    # ... (Função idêntica à original)
    le = LabelEncoder()
    le.fit(y_train)
    y_train_enc = le.transform(y_train)
    y_val_enc = le.transform(y_val)
    y_test_enc = le.transform(y_test)
    num_classes = len(le.classes_)
    return y_train_enc, y_val_enc, y_test_enc, num_classes, le




def construir_modelo_avancado(input_shape, num_classes, base_model_trainable=False):
    data_augmentation = keras.Sequential([
        layers.RandomFlip("horizontal"),
        layers.RandomRotation(0.1),
        layers.RandomZoom(0.2),
        layers.RandomContrast(0.1), 
    ], name="data_augmentation")
    
    base_model = MobileNetV3Large(
        input_shape=input_shape,
        include_top=False, 
        weights="imagenet",
        pooling="avg" 
    )
    base_model.trainable = base_model_trainable 

    inp = layers.Input(shape=input_shape, name="input_layer")
    x = data_augmentation(inp) 
    x = tf.keras.applications.mobilenet_v3.preprocess_input(x) 
    x = base_model(x, training=False) 

    x = layers.Dropout(0.7)(x) 
    x = layers.Dense(128, activation="relu", kernel_regularizer=keras.regularizers.l2(0.01))(x) 
    out = layers.Dense(num_classes, activation="softmax", name="output_layer")(x)

    model = models.Model(inputs=inp, outputs=out, name="iris_mobilenet_tl")
    
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE), 
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model

def log_confusion_matrix_plot(y_true_enc, y_pred, label_names):
    """Gera e loga um plot da Matriz de Confusão."""
    fig, ax = plt.subplots(figsize=(10, 10))
    cm = confusion_matrix(y_true_enc, y_pred)
    im = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    ax.figure.colorbar(im, ax=ax)
    ax.set(xticks=np.arange(cm.shape[1]),
           yticks=np.arange(cm.shape[0]),
           xticklabels=label_names, yticklabels=label_names,
           title='Matriz de Confusão Normalizada',
           ylabel='True label',
           xlabel='Predicted label')

    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
             rotation_mode="anchor")

    thresh = cm.max() / 2.
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, format(cm[i, j], 'd'),
                    ha="center", va="center",
                    color="white" if cm[i, j] > thresh else "black")
    fig.tight_layout()
    
    mlflow.log_figure(fig, "confusion_matrix.png")
    plt.close(fig) 

def treinar(args):
    (X_train, y_train), (X_val, y_val), (X_test, y_test) = carregar_dataset(PROCESSED_PATH)
    y_train_enc, y_val_enc, y_test_enc, num_classes, label_encoder = codificar_labels(y_train, y_val, y_test)
    label_names = label_encoder.classes_

    epochs = args.epochs or DEFAULT_EPOCHS
    batch_size = args.batch_size or BATCH_SIZE

    mlflow_tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    mlflow.set_tracking_uri(mlflow_tracking_uri)
    mlflow.set_experiment(args.experiment_name or "iris_diagnostic_tl_experiment") 

    run_name = f"run_tl_{int(time.time())}"
    with mlflow.start_run(run_name=run_name) as run:
        run_id = run.info.run_id

        mlflow.log_param("epochs", epochs)
        mlflow.log_param("batch_size", batch_size)
        mlflow.log_param("input_shape", IMG_SHAPE)
        mlflow.log_param("num_classes", num_classes)
        mlflow.log_param("model_name", "iris_cnn")

        # Construir modelo
        model = construir_modelo(IMG_SHAPE, num_classes)
        model.summary(print_fn=lambda s: mlflow.log_text(s + "\\n", "model_summary.txt"))

        # Callbacks
        early_stop = callbacks.EarlyStopping(monitor="val_loss", patience=6, restore_best_weights=True)
        reduce_lr = callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=3)
        timestamp = int(time.time())
        checkpoint_path = MODELS_DIR / f"iris_model_checkpoint_{timestamp}.h5"
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        model_checkpoint = callbacks.ModelCheckpoint(
            str(checkpoint_path),
            monitor="val_accuracy", 
            mode="max",
            save_best_only=True,
            save_weights_only=False,
        )

        print("\nIniciando treinamento com Transfer Learning...")
        history = model.fit(
            X_train, y_train_enc,
            validation_data=(X_val, y_val_enc),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[early_stop, reduce_lr, model_checkpoint],
            verbose=2,
        )
        print("Fase 1 de Treinamento concluída (Fine-tuning apenas do Head).")

        for key, values in history.history.items():
            for epoch_idx, v in enumerate(values):
                mlflow.log_metric(f"{key}", v, step=epoch_idx)

        test_loss, test_acc = model.evaluate(X_test, y_test_enc, verbose=0)
        mlflow.log_metric("test_loss", float(test_loss))
        mlflow.log_metric("test_accuracy", float(test_acc))

        y_pred_probs = model.predict(X_test)
        y_pred = np.argmax(y_pred_probs, axis=1)

        report = classification_report(y_test_enc, y_pred, target_names=label_names, output_dict=True)
        mlflow.log_dict(report, "classification_report.json")
        mlflow.log_text(json.dumps(label_names.tolist()), "label_classes.json")
        
        log_confusion_matrix_plot(y_test_enc, y_pred, label_names) 
        
        final_model_dir = MODELS_DIR / f"iris_model_final_{timestamp}"
        final_model_dir.mkdir(parents=True, exist_ok=True)
        model_save_path = final_model_dir / "saved_model"
        
        try:
            model = models.load_model(str(checkpoint_path)) 
            print(f"Carregado o melhor modelo do checkpoint: {checkpoint_path}")
        except Exception as e:
            print(f"Aviso: Não foi possível carregar o checkpoint. Usando o modelo final treinado. Erro: {e}")

        model.save(model_save_path, include_optimizer=False)
        mlflow.keras.log_model(keras_model=model, artifact_path=f"models/iris_model_tl_{timestamp}")

        mlflow.log_artifact(str(model_save_path), artifact_path="saved_models")

        print("✅ Treinamento robusto concluído.")
        print(f"Run ID: {run_id}")
        print(f"Melhor Modelo salvo em: {model_save_path}")

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
        print("\nResumo do treinamento:")
        for k, v in result.items():
            print(f" - {k}: {v}")
    except Exception as e:
        print(f"[ERRO] Falha no treinamento: {e}")
        sys.exit(1)