import random
import string

from django.contrib.auth import authenticate
from django.core.cache import cache  
from django.db import transaction
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from .models import CustomUser  
from .serializers import (
    AuthValidateSerializer,
    ConfirmationSerializer,
    RegisterValidateSerializer,
)


class AuthorizationAPIView(CreateAPIView):
    serializer_class = AuthValidateSerializer

    def post(self, request):
        print(request.auth.get("email"))
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get("user")

        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response(data={"key": token.key}, status=status.HTTP_200_OK)

        return Response(
            status=status.HTTP_401_UNAUTHORIZED,
            data={"error": "User credentials are wrong!"},
        )


class RegistrationAPIView(CreateAPIView):
    serializer_class = RegisterValidateSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            user = serializer.save(is_active=False)

            code = "".join(random.choices(string.digits, k=8))

            cache.set(f"code{user.id}", code, timeout=300)

        return Response(
            status=status.HTTP_201_CREATED,
            data={"user_id": user.id, "confirmation_code": code},
        )


class ConfirmUserAPIView(CreateAPIView):
    serializer_class = ConfirmationSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data["user_id"]
        user_code = serializer.validated_data.get("code")  
        cached_code = cache.get(f"code{user_id}")

        if not cached_code or cached_code != str(user_code):
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"error": "wrong confirmation code or code has expired!!!!!!!!!!!!"},
            )

        with transaction.atomic():
            user = CustomUser.objects.get(id=user_id)
            user.is_active = True
            user.save()

            token, _ = Token.objects.get_or_create(user=user)
            cache.delete(f"code{user_id}")

        return Response(
            status=status.HTTP_200_OK,
            data={"message": "account successfully activated", "key": token.key},
        )
