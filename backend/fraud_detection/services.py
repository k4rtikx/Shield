
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from bson import ObjectId
from bson.decimal128 import Decimal128
from config.mongodb import db
from fraud_detection.policy import evaluate_policy


LARGE_TRANSFER_THRESHOLD = Decimal("10000.00")
REPEATED_TRANSFER_LIMIT = 3
TIME_WINDOW_MINUTES = 10


def analyze_transaction(transaction_id):
    try:
        transaction_id = (
            transaction_id
            if isinstance(transaction_id, ObjectId)
            else ObjectId(str(transaction_id))
        )
    except Exception:
        raise ValueError("Invalid transaction ID")

    transaction = db["transactions"].find_one({
        "_id": transaction_id
    })

    if not transaction:
        raise ValueError("Transaction not found")

    risk_score = 0
    risk_factors = []

    amount_value = transaction["amount"]
    if isinstance(amount_value, Decimal128):
        amount = amount_value.to_decimal()
    else:
        amount = Decimal(str(amount_value))

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
            "_id": {"$ne": transaction["_id"]},
            "created_at": {
                "$gte": window_start,
                "$lte": created_at,
            },
            "status": "completed",
        })

        if repeated_count + 1 >= REPEATED_TRANSFER_LIMIT:
            risk_score += 30
            risk_factors.append(
                "Repeated transfers within 10 minutes"
            )

    risk_score = min(risk_score, 100)

    risk_level = (
        "high" if risk_score >= 70
        else "medium" if risk_score >= 30
        else "low"
    )

    risk_assessment = {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "signals": risk_factors,
    }

    policy_result = evaluate_policy(risk_assessment)

    result = {
        "transaction_id": str(transaction["_id"]),
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "decision": policy_result["decision"],
        "policy_version": policy_result["policy_version"],
        "analyzed_at": datetime.now(timezone.utc),
    }

    db["fraud_alerts"].insert_one(result)

    result["_id"] = str(result["_id"])
    result["analyzed_at"] = result["analyzed_at"].isoformat()

    return result
