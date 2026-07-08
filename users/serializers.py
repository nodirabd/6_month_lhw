from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import ConfirmationCode, CustomUser

class OAuthCodeSeroializer(serializers.Serializer):
    code = serializers.CharField()
    registration_source = serializers.ChoiceField(choices=["google", "facebook", "vk"])


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["is_active"] = user.is_active
        token["is_staff"] = user.is_staff
        token["birthdate"] = user.birthdate.isoformat() if user.birthdate else None
        return token

class UserBaseSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=150)
    password = serializers.CharField()

class AuthValidateSerializer(UserBaseSerializer):

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(email=email, password=password)

            if not user:
                raise ValidationError("Неверный email или пароль.")
            if not user.is_active:
                raise ValidationError("Этот аккаунт еще не активирован.")
        else:
            raise ValidationError("Необходимо заполнить поля email и password.")

        attrs["user"] = user
        return attrs



class RegisterValidateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, min_length=6
    )
    phone_number = serializers.CharField(required=False, max_length=20)
    birthdate = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = CustomUser
        fields = ["email", "phone_number", "birthdate", "password"]

    def validate_email(self, email):
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с таким email уже существует!")
        return email

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)


class ConfirmationSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        user_id = attrs.get("user_id")
        code = attrs.get("code")

        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            raise ValidationError("Пользователь не существует!")

        try:
            confirmation_code = ConfirmationCode.objects.get(user=user)
        except ConfirmationCode.DoesNotExist:
            raise ValidationError("Код подтверждения не найден!")

        if confirmation_code.code != code:
            raise ValidationError("Неверный код подтверждения!")

       
        user.is_active = True
        user.save()

        return attrs