from decimal import Decimal
from bson.decimal128 import Decimal128

from config.mongodb import db


def create_bank_account(user_id, account_data):
    balance = Decimal(str(account_data["initial_balance"]))

    account = {
        "user_id": user_id,
        "account_holder": account_data["account_holder"],
        "account_type": account_data["account_type"],
        "balance": Decimal128(balance),
    }

    result = db["bank_accounts"].insert_one(account)

    return {
        "_id": str(result.inserted_id),
        "user_id": user_id,
        "account_holder": account["account_holder"],
        "account_type": account["account_type"],
        "balance": str(balance),
    }


def get_user_accounts(user_id):
    accounts = db["bank_accounts"].find({"user_id": user_id})
    result = []

    for account in accounts:
        result.append({
            "_id": str(account["_id"]),
            "user_id": account["user_id"],
            "account_holder": account["account_holder"],
            "account_type": account["account_type"],
            "balance": str(Decimal(str(account["balance"]))),
        })

    return result
