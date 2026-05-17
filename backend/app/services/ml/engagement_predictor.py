import os
import pickle
import structlog
import numpy as np

logger = structlog.get_logger()

FEATURE_COLUMNS = [
    "hour_of_day", "day_of_week", "text_length", "hashtag_count",
    "has_image", "image_brightness", "image_colorfulness", "text_sentiment",
    "topic_category", "account_avg_engagement_7d", "account_post_frequency_7d",
]


class EngagementPredictor:
    def __init__(self) -> None:
        self.model = None
        self.is_trained = False

    def train(self, posts_df) -> dict:
        try:
            import lightgbm as lgb
            import pandas as pd

            X = posts_df[FEATURE_COLUMNS].fillna(0)
            y = posts_df["engagement_rate"].fillna(0)

            model = lgb.LGBMRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
            model.fit(X, y)

            self.model = model
            self.is_trained = True

            from sklearn.metrics import mean_absolute_error
            preds = model.predict(X)
            mae = mean_absolute_error(y, preds)
            return {"mae": float(mae), "samples": len(y), "feature_count": len(FEATURE_COLUMNS)}
        except Exception as e:
            logger.error("training_failed", error=str(e))
            return {"error": str(e)}

    def predict(self, features: dict) -> float:
        if not self.is_trained or self.model is None:
            return self._heuristic_predict(features)
        import pandas as pd
        row = pd.DataFrame([{col: features.get(col, 0) for col in FEATURE_COLUMNS}])
        prediction = self.model.predict(row)[0]
        return float(max(0, min(prediction, 1)))

    def get_feature_importance(self) -> dict:
        if not self.is_trained or self.model is None:
            return {}
        return dict(zip(FEATURE_COLUMNS, self.model.feature_importances_.tolist()))

    def _heuristic_predict(self, features: dict) -> float:
        score = 0.05
        hour = features.get("hour_of_day", 12)
        if hour in [9, 10, 11, 18, 19, 20]:
            score += 0.02
        if features.get("has_image"):
            score += 0.02
        hashtags = features.get("hashtag_count", 0)
        if 5 <= hashtags <= 15:
            score += 0.01
        text_len = features.get("text_length", 0)
        if 100 <= text_len <= 500:
            score += 0.01
        return round(min(score, 0.15), 4)

    def save(self, path: str) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, path: str) -> "EngagementPredictor":
        with open(path, "rb") as f:
            return pickle.load(f)
