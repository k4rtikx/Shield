from datetime import timedelta
from decimal import Decimal

from bson.decimal128 import Decimal128

from config.mongodb import db


VELOCITY_WINDOW = timedelta(minutes=10)
RAPID_MOVEMENT_WINDOW = timedelta(minutes=30)
DAILY_WINDOW = timedelta(days=1)

SENDER_VELOCITY_LIMIT = 5
RECEIVER_VELOCITY_LIMIT = 10
DAILY_DEBIT_LIMIT = Decimal("50000.00")
DAILY_CREDIT_LIMIT = Decimal("100000.00")
COUNTERPARTY_LIMIT = 8


def _decimal(value):
    if isinstance(value, Decimal128):
        return value.to_decimal()
    return Decimal(str(value))


def assess_transfer_risk(
    sender_id,
    receiver_id,
    amount,
    now,
    session,
):
    sender_id = str(sender_id)
    receiver_id = str(receiver_id)
    amount = _decimal(amount)

    transactions = db["transactions"]
    signals = []
    score = 0

    def find_transactions(query):
        return list(
            transactions.find(
                query,
                {
                    "sender_account_id": 1,
                    "receiver_account_id": 1,
                    "amount": 1,
                    "created_at": 1,
                },
                session=session,
            )
        )

    completed = {"status": "completed"}

    # 1. Recent transfer velocity
    recent_start = now - VELOCITY_WINDOW

    sender_recent = find_transactions({
        **completed,
        "sender_account_id": sender_id,
        "created_at": {"$gte": recent_start, "$lt": now},
    })

    receiver_recent = find_transactions({
        **completed,
        "receiver_account_id": receiver_id,
        "created_at": {"$gte": recent_start, "$lt": now},
    })

    if len(sender_recent) + 1 >= SENDER_VELOCITY_LIMIT:
        score += 25
        signals.append("HIGH_SENDER_TRANSFER_VELOCITY")

    if len(receiver_recent) + 1 >= RECEIVER_VELOCITY_LIMIT:
        score += 25
        signals.append("HIGH_RECEIVER_TRANSFER_VELOCITY")

    # 2. Daily debit and credit totals
    day_start = now - DAILY_WINDOW

    sender_daily = find_transactions({
        **completed,
        "sender_account_id": sender_id,
        "created_at": {"$gte": day_start, "$lt": now},
    })

    receiver_daily = find_transactions({
        **completed,
        "receiver_account_id": receiver_id,
        "created_at": {"$gte": day_start, "$lt": now},
    })

    daily_debit = sum(
        (_decimal(tx["amount"]) for tx in sender_daily),
        Decimal("0"),
    )

    daily_credit = sum(
        (_decimal(tx["amount"]) for tx in receiver_daily),
        Decimal("0"),
    )

    projected_debit = daily_debit + amount
    projected_credit = daily_credit + amount

    if projected_debit > DAILY_DEBIT_LIMIT:
        score += 20
        signals.append("HIGH_DAILY_DEBIT_TOTAL")

    if projected_credit > DAILY_CREDIT_LIMIT:
        score += 20
        signals.append("HIGH_DAILY_CREDIT_TOTAL")

    # 3. Counterparty diversity
    sender_counterparties = {
        tx["receiver_account_id"]
        for tx in sender_daily
        if tx.get("receiver_account_id")
    }

    if len(sender_counterparties | {receiver_id}) >= COUNTERPARTY_LIMIT:
        score += 20
        signals.append("MANY_RECENT_COUNTERPARTIES")

    # 4. Possible rapid movement of received funds
    cutoff = now - RAPID_MOVEMENT_WINDOW

    recent_incoming = find_transactions({
        **completed,
        "receiver_account_id": sender_id,
        "created_at": {"$gte": cutoff, "$lt": now},
    })

    recent_outgoing = find_transactions({
        **completed,
        "sender_account_id": sender_id,
        "created_at": {"$gte": cutoff, "$lt": now},
    })

    rapid_movement = any(
        incoming["created_at"] < outgoing["created_at"] <= now
        and outgoing["created_at"] - incoming["created_at"]
        <= RAPID_MOVEMENT_WINDOW
        for incoming in recent_incoming
        for outgoing in recent_outgoing
    )

    if rapid_movement:
        score += 25
        signals.append("POSSIBLE_RAPID_FUND_MOVEMENT")

    score = min(score, 100)

    level = (
        "high" if score >= 70
        else "medium" if score >= 30
        else "low"
    )

    return {
        "risk_score": score,
        "risk_level": level,
        "signals": signals,
        "daily_debit": str(daily_debit),
        "projected_daily_debit": str(projected_debit),
        "daily_credit": str(daily_credit),
        "projected_daily_credit": str(projected_credit),
    }
