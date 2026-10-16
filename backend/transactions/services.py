from bson import ObjectId
from decimal import Decimal
from config.mongodb import db, client
from datetime import datetime, timezone 

def transfer_money(sender_account_id, receiver_account_id, amount, user_id):
    amount = Decimal(str(amount))

    if amount <= 0:
        raise ValueError("Amount must be greater than zero")

    try:
        sender_id = ObjectId(sender_account_id)
        receiver_id = ObjectId(receiver_account_id) # Converts both IDs to MongoDB's ObjectId type. Invalid IDs cause an error.
    except Exception:
        raise ValueError("Invalid account ID")

    if sender_id == receiver_id:
        raise ValueError("Cannot transfer to the same account")

    amount_value = float(amount)

    def execute_transfer(session):
        sender = db["bank_accounts"].find_one(
            {"_id": sender_id, "user_id": user_id},
            session=session
        )

        if not sender:
            raise ValueError("Sender account not found")

        receiver = db["bank_accounts"].find_one(
            {"_id": receiver_id},
            session=session
        )

        if not receiver:
            raise ValueError("Receiver account not found")

        # Deduct money only if sufficient balance exists.
        result = db["bank_accounts"].update_one(
            {
                "_id": sender_id,
                "user_id": user_id,
                "balance": {"$gte": amount_value} #$gte means greater than or equal to.
            },
            {"$inc": {"balance": -amount_value}}, # 
            session=session
        )

        if result.modified_count != 1:
            raise ValueError("Insufficient balance")

        # Credit the receiver.
        result = db["bank_accounts"].update_one(
            {"_id": receiver_id},
            {"$inc": {"balance": amount_value}},
            session=session
        )

        if result.modified_count != 1:
            raise ValueError("Receiver account update failed")

        # Record the transfer in the same transaction.
        transaction = {
            "sender_account_id": str(sender_id),
            "receiver_account_id": str(receiver_id),
            "amount": amount_value,
            "status": "completed",
            "created_at": datetime.now(timezone.utc),
        }

        result = db["transactions"].insert_one(
            transaction,
            session=session
        )

        transaction["_id"] = str(result.inserted_id)
        return transaction

    # MongoDB commits everything or aborts the transaction.
    with client.start_session() as session:
        return session.with_transaction(execute_transfer)


def get_user_transactions(user_id):

    # Find the user's bank accounts
    accounts = db["bank_accounts"].find(
        {"user_id": user_id},
        {"_id": 1} #{"_id": 1} means retrieve only the _id field, not the other account details
    )

    account_ids = [str(account["_id"]) for account in accounts]

    # Find transactions involving these accounts
    transactions = db["transactions"].find({
        "$or": [
            {"sender_account_id": {"$in": account_ids}},
            {"receiver_account_id": {"$in": account_ids}}
        ]
    }).sort("_id", -1) #sorts by MongoDB's transaction ID in descending order, usually placing newer transactions first when IDs are generated normally.

    result = []

    for transaction in transactions:
        transaction["_id"] = str(transaction["_id"])
        result.append(transaction)

    return result