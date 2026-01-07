import os
import logging
import importlib
from contextlib import contextmanager
from typing import Optional, Any, Generator

import mlflow

# Configuração básica de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_EXPERIMENT = os.getenv("MLFLOW_EXPERIMENT", "default_experiment")
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")


def _check_module(module_name: str) -> bool:
    """Verifica se um módulo está disponível para import."""
    return importlib.util.find_spec(module_name) is not None


def init_mlflow(
    tracking_uri: Optional[str] = None,
    experiment_name: Optional[str] = None
) -> str:
    """
    Inicializa o MLflow e define o experimento ativo.
    Retorna o experiment_id configurado.
    """
    uri = tracking_uri or MLFLOW_TRACKING_URI
    exp_name = experiment_name or DEFAULT_EXPERIMENT

    mlflow.set_tracking_uri(uri)

    try:
        existing_exp = mlflow.get_experiment_by_name(exp_name)

        if existing_exp is None:
            experiment_id = mlflow.create_experiment(exp_name)
            logger.info(f"Experimento '{exp_name}' criado (id={experiment_id})")
        else:
            experiment_id = existing_exp.experiment_id
            logger.info(f"Experimento '{exp_name}' carregado (id={experiment_id})")

        mlflow.set_experiment(exp_name)
        logger.info(f"MLflow configurado. URI={uri} | experiment={exp_name}")
        return experiment_id

    except Exception as e:
        logger.error(f"Falha ao inicializar MLflow: {e}", exc_info=True)
        raise RuntimeError("Erro crítico ao configurar MLflow") from e


@contextmanager
def mlflow_run(
    run_name: Optional[str] = None,
    experiment_name: Optional[str] = None,
    nested: bool = False
) -> Generator[Any, None, None]:
    """
    Context manager para iniciar uma run do MLflow.
    Pode ser nested e opcionalmente inicializar outro experimento.
    """
    init_mlflow(experiment_name=experiment_name) if experiment_name else init_mlflow()

    try:
        run = mlflow.start_run(run_name=run_name, nested=nested)
        logger.info(f"Run iniciada: {run.info.run_id} | nested={nested}")
        yield run
        mlflow.end_run()
        logger.info(f"Run finalizada: {run.info.run_id}")

    except Exception as e:
        logger.error(f"Erro dentro da run MLflow: {e}", exc_info=True)
        mlflow.end_run(status="FAILED")
        raise RuntimeError("A run do MLflow falhou") from e


def log_model(
    model: Any,
    artifact_path: str = "model",
    registered_model_name: Optional[str] = None
) -> str:
    """
    Loga um modelo Keras no MLflow.
    Retorna o caminho do artefato salvo.
    """
    if not _check_module("keras"):
        raise ImportError("Keras não está instalado no ambiente")

    if not hasattr(mlflow, "keras"):
        raise ImportError("mlflow.keras não está disponível. Instale MLflow com suporte Keras.")

    try:
        model_uri = mlflow.keras.log_model(
            keras_model=model,
            artifact_path=artifact_path,
            registered_model_name=registered_model_name
        )
        logger.info(f"Modelo logado em artifact_path='{artifact_path}'")
        return model_uri

    except Exception as e:
        logger.error(f"Falha ao logar modelo no MLflow: {e}", exc_info=True)
        raise RuntimeError("Erro ao registrar o modelo no MLflow") from e


def log_artifact(
    local_path: str,
    artifact_path: Optional[str] = None
) -> str:

    if not os.path.exists(local_path):
        raise FileNotFoundError(f"Arquivo '{local_path}' não encontrado")

    try:
        mlflow.log_artifact(local_path, artifact_path=artifact_path) if artifact_path else mlflow.log_artifact(local_path)
        logger.info(f"Artefato '{local_path}' logado com sucesso")
        return os.path.join(artifact_path or "", os.path.basename(local_path))

    except Exception as e:
        logger.error(f"Falha ao logar artefato: {e}", exc_info=True)
        raise RuntimeError("Erro ao registrar artefato no MLflow") from e
