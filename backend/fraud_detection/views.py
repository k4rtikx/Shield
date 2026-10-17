from bson import ObjectId
from bson.errors import InvalidId

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .serializers import FraudAnalysisSerializer
from .services import analyze_transaction
from config.mongodb import db


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def analyze_fraud(request):
    serializer = FraudAnalysisSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        transaction_id = ObjectId(
            serializer.validated_data["transaction_id"]
        )
    except InvalidId:
        return Response(
            {"error": "Invalid transaction ID"},
            status=status.HTTP_400_BAD_REQUEST
        )

    transaction = db["transactions"].find_one({
        "_id": transaction_id
    })

    if not transaction:
        return Response(
            {"error": "Transaction not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Only allow analysis of transactions involving
    # an account owned by the authenticated user.
    account_ids = {
        str(account["_id"])
        for account in db["bank_accounts"].find(
            {"user_id": request.user.id},
            {"_id": 1}
        )
    }

    if (
        transaction["sender_account_id"] not in account_ids
        and transaction["receiver_account_id"] not in account_ids
    ):
        return Response(
            {"error": "You are not authorized to analyze this transaction"},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        result = analyze_transaction(transaction_id)
        return Response(result, status=status.HTTP_200_OK)

    except ValueError as error:
        return Response(
            {"error": str(error)},
            status=status.HTTP_400_BAD_REQUEST
        )