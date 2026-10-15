from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .serializers import BankAccountSerializer
from .services import create_bank_account


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_account(request):
    serializer = BankAccountSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    account = create_bank_account(
        user_id=request.user.id,
        account_data=serializer.validated_data
    )
    return Response(account, status=status.HTTP_201_CREATED)