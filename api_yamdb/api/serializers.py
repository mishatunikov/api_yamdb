from rest_framework import serializers
from datetime import datetime as dt
from reviews.models import Category, Genre, Title, User
from django.utils import timezone
from rest_framework.generics import get_object_or_404
from api import const
from django.utils import timezone


class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Category.

    Используется для преобразования объектов модели Category,
    Исключает поле 'id' из сериализации.
    """

    class Meta:
        model = Category
        exclude = ('id',)


class GenreSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Category.

    Используется для преобразования объектов модели Genre,
    Исключает поле 'id' из сериализации.
    """

    class Meta:
        model = Genre
        exclude = ('id',)


class TitleGetSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Title.

    Все поля модели Title доступны для чтения, но не для записи.
    """
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer()
    rating = serializers.IntegerField()

    class Meta:
        model = Title
        fields = '__all__'
        read_only_fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category')


class TitleSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Title.

    Включает в себя поля для жанров и категорий, которые представлены
    в виде SlugRelatedField.
    """
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        many=True,
        queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = '__all__'

    def validate_year(self, value):
        year_today = timezone.now().year
        if value > year_today:
            raise serializers.ValidationError('Проверьте год издания!')
        return value


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
