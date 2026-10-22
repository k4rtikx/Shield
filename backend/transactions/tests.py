from decimal import Decimal
from unittest import TestCase
from unittest.mock import MagicMock, patch

from bson import Decimal128, ObjectId

from transactions.services import transfer_money
from fraud_detection.policy import evaluate_policy


class TransferSafetyTests(TestCase):
    def setUp(self):
        self.sender_id = ObjectId()
        self.receiver_id = ObjectId()
        self.user_id = "test-user"

        self.sender = {
            "_id": self.sender_id,
            "user_id": self.user_id,
            "balance": Decimal128("400.00"),
        }
        self.receiver = {
            "_id": self.receiver_id,
            "balance": Decimal128("14600.00"),
        }

        self.session = MagicMock()
        self.client_patcher = patch(
            "transactions.services.client"
        )
        self.mock_client = self.client_patcher.start()
        self.addCleanup(self.client_patcher.stop)

        session_context = self.mock_client.start_session.return_value
        session_context.__enter__.return_value = self.session

        def run_transaction(callback):
            return callback(self.session)

        self.session.with_transaction.side_effect = run_transaction

        self.db_patcher = patch("transactions.services.db")
        self.db = self.db_patcher.start()
        self.addCleanup(self.db_patcher.stop)

        self.accounts = self.db.__getitem__.return_value
        self.transactions = self.db.__getitem__.return_value

        # Route collection lookups to distinct mock collections.
        self.accounts_collection = MagicMock()
        self.transactions_collection = MagicMock()

        def get_collection(name):
            if name == "bank_accounts":
                return self.accounts_collection
            if name == "transactions":
                return self.transactions_collection
            raise AssertionError(f"Unexpected collection: {name}")

        self.db.__getitem__.side_effect = get_collection

        self.transactions_collection.find_one.return_value = None
        self.accounts_collection.find_one.side_effect = [
            self.sender,
            self.receiver,
        ]

        self.accounts_collection.update_one.side_effect = [
            MagicMock(modified_count=1),
            MagicMock(modified_count=1),
        ]
        self.transactions_collection.insert_one.return_value = MagicMock(
            inserted_id=ObjectId()
        )

        self.risk_patcher = patch(
            "transactions.services.assess_transfer_risk",
            return_value={"risk_level": "low", "risk_score": 10, "signals": []},
        )
        self.mock_risk = self.risk_patcher.start()
        self.addCleanup(self.risk_patcher.stop)

    def transfer(self, key="test-key", amount="100.00"):
        return transfer_money(
            str(self.sender_id),
            str(self.receiver_id),
            amount,
            self.user_id,
            key,
        )

    def test_database_insert_failure_propagates(self):
        self.transactions_collection.insert_one.side_effect = RuntimeError(
            "Simulated database failure"
        )

        with self.assertRaises(RuntimeError):
            print("Risk mock:", self.mock_risk)
            print("Account lookup:", self.accounts_collection.find_one.call_args_list)
            print("Transaction lookup:", self.transactions_collection.find_one.call_args_list)
            self.transfer()

        # The mocked transaction runner does not simulate rollback.
        # Verify the failure reaches the transaction boundary.
        self.transactions_collection.insert_one.assert_called_once()

    def test_receiver_credit_failure_stops_transfer(self):
        self.accounts_collection.update_one.side_effect = [
            MagicMock(modified_count=1),
            RuntimeError("Simulated receiver credit failure"),
        ]

        with self.assertRaises(RuntimeError):
            print("Risk mock:", self.mock_risk)
            print("Account lookup:", self.accounts_collection.find_one.call_args_list)
            print("Transaction lookup:", self.transactions_collection.find_one.call_args_list)
            self.transfer()

        self.transactions_collection.insert_one.assert_not_called()

    def test_high_risk_transfer_is_rejected_before_balance_updates(self):
        self.mock_risk.return_value = {
            "risk_level": "high",
            "risk_score": 85,
            "signals": ["HIGH_RISK"],
        }

        with self.assertRaisesRegex(
            ValueError, "Transfer declined by fraud risk assessment"
        ):
            print("Risk mock:", self.mock_risk)
            print("Account lookup:", self.accounts_collection.find_one.call_args_list)
            print("Transaction lookup:", self.transactions_collection.find_one.call_args_list)
            self.transfer()

        self.accounts_collection.update_one.assert_not_called()
        self.transactions_collection.insert_one.assert_not_called()

    def test_fraud_policy_decisions(self):
        self.assertEqual(
            evaluate_policy({"risk_score": 15})["decision"], "allow"
        )
        self.assertEqual(
            evaluate_policy({"risk_score": 45})["decision"], "review"
        )
        self.assertEqual(
            evaluate_policy({"risk_score": 80})["decision"], "decline"
        )
