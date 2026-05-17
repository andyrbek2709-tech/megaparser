import io
from datetime import datetime

import numpy as np
import structlog

logger = structlog.get_logger()


def extract_features(post_data: dict) -> dict:
    published_at = post_data.get("published_at")
    if isinstance(published_at, str):
        published_at = datetime.fromisoformat(published_at)

    features: dict = {
        "hour_of_day": published_at.hour if published_at else 12,
        "day_of_week": published_at.weekday() if published_at else 0,
        "text_length": len(post_data.get("content_text") or ""),
        "hashtag_count": len([w for w in (post_data.get("content_text") or "").split() if w.startswith("#")]),
        "has_image": 1 if post_data.get("image_url") else 0,
        "image_brightness": 0.5,
        "image_colorfulness": 0.5,
        "text_sentiment": 0.0,
        "topic_category": 0,
        "account_avg_engagement_7d": post_data.get("account_avg_engagement_7d", 0.0),
        "account_post_frequency_7d": post_data.get("account_post_frequency_7d", 0.0),
    }

    if post_data.get("image_local_path"):
        try:
            from PIL import Image
            img = Image.open(post_data["image_local_path"]).convert("RGB")
            arr = np.array(img).astype(float)
            features["image_brightness"] = float(arr.mean() / 255)
            r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
            rg = np.abs(r - g)
            yb = np.abs(0.5 * (r + g) - b)
            features["image_colorfulness"] = float((rg.std() + yb.std()) / 255)
        except Exception:
            pass

    return features
