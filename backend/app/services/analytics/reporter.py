import structlog

logger = structlog.get_logger()


async def generate_report(user_id: str, account_id: str) -> dict:
    return {
        "user_id": user_id,
        "account_id": account_id,
        "summary": "Analytics report generated",
    }
