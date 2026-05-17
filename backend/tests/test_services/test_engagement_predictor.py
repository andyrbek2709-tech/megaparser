from app.services.ml.engagement_predictor import EngagementPredictor


def test_heuristic_predict():
    predictor = EngagementPredictor()
    features = {
        "hour_of_day": 9,
        "day_of_week": 1,
        "text_length": 250,
        "hashtag_count": 8,
        "has_image": 1,
        "image_brightness": 0.6,
        "image_colorfulness": 0.4,
        "text_sentiment": 0.5,
        "topic_category": 0,
        "account_avg_engagement_7d": 0.05,
        "account_post_frequency_7d": 7.0,
    }
    result = predictor.predict(features)
    assert 0 <= result <= 1


def test_feature_importance_untrained():
    predictor = EngagementPredictor()
    assert predictor.get_feature_importance() == {}
