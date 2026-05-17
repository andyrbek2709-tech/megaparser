from collections import defaultdict
import structlog

logger = structlog.get_logger()


def compute_best_times(metrics_history: list[dict]) -> list[dict]:
    slot_scores: dict = defaultdict(list)
    for entry in metrics_history:
        day = entry.get("day_of_week")
        hour = entry.get("hour_of_day")
        er = entry.get("engagement_rate", 0)
        if day is not None and hour is not None:
            slot_scores[(day, hour)].append(er)

    best = []
    for (day, hour), scores in slot_scores.items():
        best.append({"day": day, "hour": hour, "avg_engagement": sum(scores) / len(scores)})

    return sorted(best, key=lambda x: x["avg_engagement"], reverse=True)[:10]
