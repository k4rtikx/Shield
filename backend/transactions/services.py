
from datetime import datetime, timezone
from decimal import Decimal

from fraud_detection.audit import build_fraud_event, record_fraud_event
from fraud_detection.pre_transfer import assess_transfer_risk
from bson import ObjectId
from bson.decimal128 import Decimal128
from pymongo.errors import DuplicateKeyError

from config.mongodb import db, client


def to_decimal(value):  #calculation
    if isinstance(value, Decimal128):
        return value.to_decimal()
    return Decimal(str(value))


def serialize_transaction(transaction): # for sendin json
    transaction["_id"] = str(transaction["_id"])
    transaction["amount"] = str(to_decimal(transaction["amount"]))
    return transaction


def transfer_money(
    sender_account_id,
    receiver_account_id,
    amount,
    user_id,
    idempotency_key,
):
    amount = to_decimal(amount)

    if not amount.is_finite() or amount <= 0:
        raise ValueError("Amount must be greater than zero")

    if not idempotency_key or not idempotency_key.strip(): # remove space from back and front
        raise ValueError("Idempotency key is required")

    idempotency_key = idempotency_key.strip()

    try:
        sender_id = ObjectId(sender_account_id)
        receiver_id = ObjectId(receiver_account_id)
    except Exception:
        raise ValueError("Invalid account ID")

    if sender_id == receiver_id:
        raise ValueError("Cannot transfer to the same account")

    amount_bson = Decimal128(amount)
    audit_event = None

    def find_existing(session=None):
        return db["transactions"].find_one(
            {
                "initiated_by_user_id": user_id,
                "idempotency_key": idempotency_key,
            },
            session=session,
        )

    def validate_existing(transaction):
        same_request = (
            transaction["sender_account_id"] == str(sender_id)
            and transaction["receiver_account_id"] == str(receiver_id)
            and to_decimal(transaction["amount"]) == amount
        )

        if not same_request:
            raise ValueError(
                "Idempotency key was already used with different details"
            )

        return serialize_transaction(transaction)

    def execute_transfer(session):
        nonlocal audit_event

        existing = find_existing(session)

        if existing:
            return validate_existing(existing)

        sender = db["bank_accounts"].find_one(
            {"_id": sender_id, "user_id": user_id},
            session=session,
        )

        if not sender:
            raise ValueError("Sender account not found")

        receiver = db["bank_accounts"].find_one(
            {"_id": receiver_id},
            session=session,
        )

        if not receiver:
            raise ValueError("Receiver account not found")

        now = datetime.now(timezone.utc)

        risk = assess_transfer_risk(
            sender_id=sender_id,
            receiver_id=receiver_id,
            amount=amount,
            now=now,
            session=session,
        )

        decision = risk["decision"]

        audit_event = build_fraud_event(
            initiated_by_user_id=user_id,
            idempotency_key=idempotency_key,
            sender_account_id=sender_id,
            receiver_account_id=receiver_id,
            amount=amount,
            risk=risk,
            outcome="transfer_failed",
        )

        if decision == "decline":
            audit_event["outcome"] = "declined"
            raise ValueError("Transfer declined by fraud risk assessment")

        if decision == "review":
            audit_event["outcome"] = "review_required"
            raise ValueError("Transfer requires manual review")

        if decision != "allow":
            raise ValueError("Invalid fraud policy decision")

        debit = db["bank_accounts"].update_one(
            {
                "_id": sender_id,
                "user_id": user_id,
                "balance": {"$gte": amount_bson},
            },
            {"$inc": {"balance": Decimal128(-amount)}},
            session=session,
        )

        if debit.modified_count != 1:
            raise ValueError("Insufficient balance")

        credit = db["bank_accounts"].update_one(
            {"_id": receiver_id},
            {"$inc": {"balance": amount_bson}},
            session=session,
        )

        if credit.modified_count != 1:
            raise ValueError("Receiver account update failed")

        transaction = {
            "initiated_by_user_id": user_id,
            "idempotency_key": idempotency_key,
            "sender_account_id": str(sender_id),
            "receiver_account_id": str(receiver_id),
            "amount": amount_bson,
            "status": "completed",
            "created_at": now,
        }

        result = db["transactions"].insert_one(
            transaction,
            session=session,
        )

        transaction["_id"] = result.inserted_id

        audit_event["outcome"] = "completed"
        audit_event["transaction_id"] = str(result.inserted_id)

        record_fraud_event(audit_event, session=session)

        return serialize_transaction(transaction)

    try:
        with client.start_session() as session:
            return session.with_transaction(execute_transfer)

    except DuplicateKeyError:
        existing = find_existing()

        if existing:
            return validate_existing(existing)

        raise

    except Exception:
        if audit_event is not None:
            if audit_event["outcome"] == "completed":
                audit_event["outcome"] = "transfer_failed"
                audit_event["transaction_id"] = None

            try:
                # Persist outside the aborted transfer transaction.
                record_fraud_event(audit_event)
            except Exception:
                # Preserve the original transfer exception.
                pass

        raise


def get_user_transactions(user_id):
    accounts = db["bank_accounts"].find(
        {"user_id": user_id},
        {"_id": 1},
    )

    account_ids = [str(account["_id"]) for account in accounts]

    transactions = db["transactions"].find({
        "$or": [
            {"sender_account_id": {"$in": account_ids}},
            {"receiver_account_id": {"$in": account_ids}},
        ]
    }).sort("created_at", -1)

    return [
        serialize_transaction(transaction)
        for transaction in transactions
    ]
