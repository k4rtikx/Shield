# The key requirement is that every assessed transfer attempt has an auditable outcome—even when it is declined or 
# requires review. A fraud record must not disappear simply because the money-transfer transaction rolls back.

from datetime import datetime, timezone
from config.mongodb import db

def ensure_fraud_event_indexes():
    """Create the indexes required for durable, idempotent audit records."""
    db["fraud_events"].create_index(
        [
            ("initiated_by_user_id", 1),
            ("idempotency_key", 1),
        ],
        unique=True,  # combination will not repeated 
        name="unique_fraud_event_per_transfer_request",
    )

    db["fraud_events"].create_index(
        [("created_at", -1)],  # both for performance and searching
        name="fraud_events_created_at",
    )

    db["fraud_events"].create_index(
        [("decision", 1), ("outcome", 1), ("created_at", -1)], # 1 for ascending (operation can be done ) and -1 for descending
        name="fraud_events_investigation",
    )


def build_fraud_event(
    *, #The * means all arguments after it must be passed by keyword, such as outcome="completed"
    initiated_by_user_id,
    idempotency_key,
    sender_account_id,
    receiver_account_id,
    amount,
    risk,
    outcome,
    transaction_id=None,
):
    """Build a structured, timestamped fraud audit event."""
    required = {
        "risk_score",
        "signals",
        "decision",
        "policy_version",
    }
    missing = required.difference(risk)
    if missing:
        raise ValueError(
            f"Fraud assessment missing fields: {sorted(missing)}"
        )

    if outcome not in {
        "completed",
        "review_required",
        "declined",
        "transfer_failed",
    }:
        raise ValueError("Invalid fraud event outcome")

    return {
        "initiated_by_user_id": initiated_by_user_id,
        "idempotency_key": idempotency_key,
        "sender_account_id": str(sender_account_id),
        "receiver_account_id": str(receiver_account_id),
        "amount": str(amount),
        "risk_score": risk["risk_score"],
        "signals": list(risk["signals"]),
        "decision": risk["decision"],
        "policy_version": risk["policy_version"],
        "outcome": outcome,
        "transaction_id": (
            str(transaction_id) if transaction_id is not None else None
        ),
        "created_at": datetime.now(timezone.utc),
    }



def record_fraud_event(event, session=None):
    """Create or update the audit record for one idempotent transfer request.""" #docstring
    from datetime import datetime, timezone

    event = dict(event)
    created_at = event.pop("created_at", datetime.now(timezone.utc))
    event["updated_at"] = datetime.now(timezone.utc)

    key = {
        "initiated_by_user_id": event["initiated_by_user_id"],
        "idempotency_key": event["idempotency_key"],
    }

    return db["fraud_events"].update_one(
        key,
        {
            "$set": event,
            "$setOnInsert": {"created_at": created_at},
        },
        upsert=True, # if found update and if not found create a new record 
        session=session,
    )
