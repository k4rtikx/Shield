from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import BankAccountSerializer
from .services import create_bank_account, get_user_accounts


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def create_account(request):

    if request.method == 'GET':  # its just retrive the account data
        accounts = get_user_accounts(request.user.id)
        return Response(accounts, status=status.HTTP_200_OK)

    serializer = BankAccountSerializer(data=request.data) # it create the new account 

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