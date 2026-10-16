from datetime import datetime, timedelta, timezone
from decimal import Decimal

from config.mongodb import db


LARGE_TRANSFER_THRESHOLD = Decimal("10000.00")
REPEATED_TRANSFER_LIMIT = 3
TIME_WINDOW_MINUTES = 10


def analyze_transaction(transaction_id):
    transaction = db["transactions"].find_one({
        "_id": transaction_id
    })

    if not transaction:
        raise ValueError("Transaction not found")

    risk_score = 0
    risk_factors = []

    amount = Decimal(str(transaction["amount"]))

    # Rule 1: Large transfer
    if amount >= LARGE_TRANSFER_THRESHOLD:
        risk_score += 40
        risk_factors.append("Large transfer amount")

    # Rule 2: Repeated transfers by the same sender
    created_at = transaction.get("created_at")

    if created_at:
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        window_start = created_at - timedelta(
            minutes=TIME_WINDOW_MINUTES
        )

        repeated_count = db["transactions"].count_documents({
            "sender_account_id": transaction["sender_account_id"],
            "created_at": {
                "$gte": window_start,
                "$lte": created_at
            },
            "status": "completed"
        })

        if repeated_count >= REPEATED_TRANSFER_LIMIT:
            risk_score += 30
            risk_factors.append(
                "Repeated transfers within 10 minutes"
            )

    risk_score = min(risk_score, 100)

    if risk_score >= 70:
        risk_level = "high"
    elif risk_score >= 40:
        risk_level = "medium"
    else:
        risk_level = "low"

    result = {
        "transaction_id": str(transaction["_id"]),
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "analyzed_at": datetime.now(timezone.utc)
    }

    db["fraud_alerts"].insert_one(result)

    result["_id"] = str(result["_id"]) if "_id" in result else None
    result["analyzed_at"] = result["analyzed_at"].isoformat()

    return result