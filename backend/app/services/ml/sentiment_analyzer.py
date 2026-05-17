import structlog

logger = structlog.get_logger()

_pipeline = None


def get_sentiment(text: str) -> float:
    global _pipeline
    if _pipeline is None:
        try:
            from transformers import pipeline
            _pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
        except Exception:
            return 0.0

    try:
        result = _pipeline(text[:512])[0]
        score = result["score"]
        return score if result["label"] == "POSITIVE" else -score
    except Exception:
        return 0.0
