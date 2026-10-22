
from datetime import timedelta
from decimal import Decimal

from bson import ObjectId
from bson.decimal128 import Decimal128

from config.mongodb import db


VELOCITY_WINDOW = timedelta(minutes=10)
RAPID_MOVEMENT_WINDOW = timedelta(minutes=30)
DAILY_WINDOW = timedelta(days=1)


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
    recent_start = now - VELOCITY_WINDOW # past 10 minutes transations

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

    if len(sender_recent) >= 5: # len of sender tranasctions
        score += 25
        signals.append("HIGH_SENDER_TRANSFER_VELOCITY")

    if len(receiver_recent) >= 10:
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
        (_decimal(tx["amount"]) for tx in sender_daily), # Sum of sender's daily debits
        Decimal("0"),
    )

    daily_credit = sum(
        (_decimal(tx["amount"]) for tx in receiver_daily),
        Decimal("0"),
    )

    if daily_debit + amount > Decimal("50000"):
        score += 20
        signals.append("HIGH_DAILY_DEBIT_TOTAL")

    if daily_credit + amount > Decimal("100000"):
        score += 20
        signals.append("HIGH_DAILY_CREDIT_TOTAL")

    # 3. Counterparty diversity   /  sender has sent to 7 different people and now sending to 8th person
    sender_counterparties = {
        tx["receiver_account_id"]
        for tx in sender_daily
        if tx.get("receiver_account_id")
    }

    if len(sender_counterparties | {receiver_id}) >= 8: #{"A", "B", "C", "D", "E", "F", "G"} | {"C"} this add c to set
        score += 20
        signals.append("MANY_RECENT_COUNTERPARTIES")

    # 4. Possible rapid movement of received funds  # receiver transfer funds to different account within 30 minutes
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

    rapid_movement = False

    for incoming in recent_incoming:
        incoming_time = incoming["created_at"]

        for outgoing in recent_outgoing:
            outgoing_time = outgoing["created_at"]

            # Outgoing transfer must occur after incoming transfer,
            # within the configured 30-minute window.
            if (
                incoming_time < outgoing_time <= now  # 10 am < 10:15 am <= 10:30 am
                and outgoing_time - incoming_time <= RAPID_MOVEMENT_WINDOW  #within 30 minutes
            ):
                rapid_movement = True
                break

        if rapid_movement:
            break

    if rapid_movement:
        score += 25
        signals.append("POSSIBLE_RAPID_FUND_MOVEMENT")

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
        "daily_credit": str(daily_credit),
    }
