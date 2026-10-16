from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .serializers import MoneyTransferSerializer
from .services import transfer_money, get_user_transactions

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def transfer(request):
    serializer = MoneyTransferSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        transaction = transfer_money(
            sender_account_id=serializer.validated_data["sender_account_id"],
            receiver_account_id=serializer.validated_data["receiver_account_id"],
            amount=serializer.validated_data["amount"],
            user_id=request.user.id
        )

        return Response(
            transaction,
            status=status.HTTP_201_CREATED
        )

    except ValueError as error:
        return Response(
            {"error": str(error)},
            status=status.HTTP_400_BAD_REQUEST
        )

    except Exception:
        return Response(
            {"error": "Transfer failed. No changes were committed."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transaction_history(request):
    transactions = get_user_transactions(request.user.id)

    return Response(
        transactions,
        status=status.HTTP_200_OK
    )