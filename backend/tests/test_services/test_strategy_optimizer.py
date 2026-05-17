from app.services.ml.strategy_optimizer import StrategyOptimizer


def test_default_strategy():
    optimizer = StrategyOptimizer()
    strategy = optimizer._default_strategy()
    assert "best_post_times" in strategy
    assert "recommended_topics" in strategy
    assert "content_mix" in strategy


def test_generate_weekly_plan_empty():
    optimizer = StrategyOptimizer()
    plan = optimizer.generate_weekly_plan("account_1", [], [], None)
    assert "best_post_times" in plan
    assert "content_mix" in plan
    assert plan["recommended_frequency"] == 7
