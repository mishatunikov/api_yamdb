from django.utils import timezone
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from api import const
from reviews.models import User


class SignUpSerializer(serializers.ModelSerializer):
    """Сериализатор для свмостоятельной регистрации нового пользователя."""

    class Meta:
        model = User
        fields = (
            'email',
            'username',
        )

    def validate_username(self, value):
        if value.lower() in const.FORBIDDEN_USERNAMES:
            raise serializers.ValidationError('Недопустимый username.')
        return value


class TokenAccessObtainSerializer(serializers.Serializer):
    """
    Сериализатор для аутентификации пользователя по коду подтверждения.
    """

    username = serializers.CharField(max_length=150, required=True)
    confirmation_code = serializers.CharField(
        max_length=const.CODE_LENGTH, required=True
    )

    def validate(self, attrs):
        user = get_object_or_404(User, username=attrs.get('username'))
        if user.confirmation_code.code != attrs.get('confirmation_code'):
            raise serializers.ValidationError('Введён неверный код')

        if (
            timezone.now() - user.confirmation_code.created_at
        ).seconds > const.CODE_LIFETIME:
            raise serializers.ValidationError(
                'Срок действия кода истек. Получите новый.'
            )

        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для взаимодействия с данными пользователей."""

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )
