import os
import mlflow
from contextlib import contextmanager

DEFAULT_EXPERIMENT = os.getenv("MLFLOW_EXPERIMENT", "default_experiment")
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")


def init_mlflow(tracking_uri: str = None, experiment_name: str = None):
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
    try:
        mlflow.keras.log_model(keras_model=model, artifact_path=artifact_path,
                               registered_model_name=registered_model_name)
        print(f"Modelo logado no MLflow em artifact_path={artifact_path}")
    except Exception as e:
        print(f"Falha ao logar modelo no MLflow: {e}")
        raise


def log_artifact(local_path: str, artifact_path: str = None):
    try:
        if artifact_path:
            mlflow.log_artifact(local_path, artifact_path=artifact_path)
        else:
            mlflow.log_artifact(local_path)
        print(f"Artefato '{local_path}' logado no MLflow.")
    except Exception as e:
        print(f"Falha ao logar artefato: {e}")
        raise
