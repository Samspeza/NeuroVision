"""
Helpers para integração centralizada com MLflow.
Fornece funções para:
- configurar o tracking URI a partir do .env
- criar/selecionar experiments
- usar um contexto auxiliar para runs automatizados
- logar parâmetros, métricas e artefatos de forma padronizada

Uso típico:
from mlflow_tracking import init_mlflow, mlflow_run

init_mlflow()  # configura URI e experimento padrão
with mlflow_run("nome_do_run") as run:
    mlflow.log_param("lr", 0.001)
    mlflow.log_metric("accuracy", 0.95)
"""

import os
import mlflow
from contextlib import contextmanager

DEFAULT_EXPERIMENT = os.getenv("MLFLOW_EXPERIMENT", "default_experiment")
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")


def init_mlflow(tracking_uri: str = None, experiment_name: str = None):
    """Configura MLflow com a URI e seleciona/cria o experimento.

    Args:
        tracking_uri: URI do servidor MLflow (se None, usa variável de ambiente).
        experiment_name: nome do experimento (se None, usa DEFAULT_EXPERIMENT).
    Returns:
        experiment_id (str)
    """
    uri = tracking_uri or MLFLOW_TRACKING_URI
    mlflow.set_tracking_uri(uri)
    exp_name = experiment_name or DEFAULT_EXPERIMENT
    try:
        exp = mlflow.get_experiment_by_name(exp_name)
        if exp is None:
            exp_id = mlflow.create_experiment(exp_name)
        else:
            exp_id = exp.experiment_id
        mlflow.set_experiment(exp_name)
        print(f"MLflow configurado. URI={uri} | experiment={exp_name} (id={exp_id})")
        return exp_id
    except Exception as e:
        print(f"Falha ao inicializar MLflow: {e}")
        raise


@contextmanager
def mlflow_run(run_name: str = None, experiment_name: str = None, nested: bool = False):
    """Context manager simplificado para criar um run MLflow.

    Exemplo:
        with mlflow_run("treino_v1") as run:
            mlflow.log_param(...)
    """
    if experiment_name:
        init_mlflow(experiment_name=experiment_name)
    else:
        init_mlflow()

    try:
        with mlflow.start_run(run_name=run_name, nested=nested) as run:
            yield run
    except Exception:
        raise


def log_model(model, artifact_path: str = "model", registered_model_name: str = None):
    """Loga um modelo Keras/TensorFlow no MLflow dentro do run atual.

    Args:
        model: objeto do modelo (keras.Model)
        artifact_path: caminho de artefatos onde o modelo será salvo
        registered_model_name: nome para registrar no Model Registry (opcional)
    """
    try:
        mlflow.keras.log_model(keras_model=model, artifact_path=artifact_path,
                               registered_model_name=registered_model_name)
        print(f"Modelo logado no MLflow em artifact_path={artifact_path}")
    except Exception as e:
        print(f"Falha ao logar modelo no MLflow: {e}")
        raise


def log_artifact(local_path: str, artifact_path: str = None):
    """Loga um arquivo ou diretório como artefato do run atual."""
    try:
        if artifact_path:
            mlflow.log_artifact(local_path, artifact_path=artifact_path)
        else:
            mlflow.log_artifact(local_path)
        print(f"Artefato '{local_path}' logado no MLflow.")
    except Exception as e:
        print(f"Falha ao logar artefato: {e}")
        raise
