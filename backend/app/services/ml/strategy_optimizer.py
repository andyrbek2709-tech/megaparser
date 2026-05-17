import structlog
from app.services.ml.engagement_predictor import EngagementPredictor
from app.services.ml.optimal_time import compute_best_times

logger = structlog.get_logger()


class StrategyOptimizer:
    def generate_weekly_plan(
        self,
        account_id: str,
        posts_history: list,
        metrics_history: list,
        current_strategy: dict | None = None,
    ) -> dict:
        best_times = compute_best_times(metrics_history)

        engagement_rates = [m.get("engagement_rate", 0) for m in metrics_history]
        avg_er = sum(engagement_rates) / len(engagement_rates) if engagement_rates else 0.05

        underperforming = []
        for post in posts_history:
            er = post.get("engagement_rate", 0)
            if er < avg_er * 0.5:
                params = post.get("generation_params", {})
                if params.get("tone"):
                    underperforming.append(f"{params['tone']} tone")

        return {
            "best_post_times": [{"day": t["day"], "hours": [t["hour"]]} for t in best_times[:7]],
            "recommended_topics": current_strategy.get("recommended_topics", ["lifestyle", "tips"]) if current_strategy else ["lifestyle", "tips"],
            "recommended_tone": "casual",
            "recommended_frequency": 7,
            "content_mix": {"photo": 0.5, "carousel": 0.3, "video": 0.2},
            "underperforming_patterns": list(set(underperforming))[:5],
            "ab_test_suggestion": {"variable": "tone", "variants": ["casual", "inspirational"]},
        }

    def _default_strategy(self) -> dict:
        return {
            "best_post_times": [
                {"day": "monday", "hours": [9, 18]},
                {"day": "wednesday", "hours": [12, 19]},
                {"day": "friday", "hours": [17, 20]},
            ],
            "recommended_topics": ["lifestyle", "tips", "behind-the-scenes"],
            "recommended_tone": "casual",
            "recommended_frequency": 7,
            "content_mix": {"photo": 0.5, "carousel": 0.3, "video": 0.2},
            "underperforming_patterns": [],
            "ab_test_suggestion": {"variable": "tone", "variants": ["casual", "inspirational"]},
        }
