from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer
from .services import register_user


@api_view(['POST'])
def register(request):
    serializer = RegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = register_user(**serializer.validated_data)
    except ValueError as error:
        return Response(
            {"error": str(error)},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        {"message": "User registered successfully", "username": user.username},
        status=status.HTTP_201_CREATED,
    )