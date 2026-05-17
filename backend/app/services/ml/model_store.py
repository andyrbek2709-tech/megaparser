import os
import pickle
import structlog

from app.config import settings

logger = structlog.get_logger()


def save_model(model: object, name: str) -> str:
    path = os.path.join(settings.ML_MODELS_PATH, f"{name}.pkl")
    os.makedirs(settings.ML_MODELS_PATH, exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(model, f)
    logger.info("model_saved", name=name, path=path)
    return path


def load_model(name: str) -> object | None:
    path = os.path.join(settings.ML_MODELS_PATH, f"{name}.pkl")
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return pickle.load(f)
