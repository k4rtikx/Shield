from config.mongodb import db


def create_bank_account(user_id, account_data):
    account = {
        "user_id": user_id,
        "account_holder": account_data["account_holder"],
        "account_type": account_data["account_type"],
        "balance": float(account_data["initial_balance"]),
    }

    result = db["bank_accounts"].insert_one(account)

    account["_id"] = str(result.inserted_id)
    return account

# Logic: It return only bank accounts whose user_id matches the authenticated user. 
def get_user_accounts(user_id):
    accounts = db["bank_accounts"].find({"user_id": user_id})

    result = []

    for account in accounts:
        account["_id"] = str(account["_id"])
        result.append(account)

    return result