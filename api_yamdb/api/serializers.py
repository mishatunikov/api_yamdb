from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from api import const
from reviews.models import User, Review, Comment


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов."""

    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )
    score = serializers.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )

    def validate(self, data):
        """Запрещает пользователям оставлять повторные отзывы."""
        request = self.context.get('request')
        view = self.context.get('view')

        if request and request.method == 'POST':
            author = request.user
            title_id = view.kwargs.get('title_id')
            if not title_id:
                raise serializers.ValidationError(
                    'Ошибка: отсутствует ID произведения.', code='invalid'
                )
            if Review.objects.filter(title_id=title_id, author=author).exists():
                raise serializers.ValidationError(
                    'Нельзя добавить больше 1 отзыва на произведение.',
                    code='unique'
                )
        return data

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date', 'title')
        read_only_fields = ('author', 'title',)


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев."""
    author = serializers.SlugRelatedField(read_only=True, slug_field='username')

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('author',)


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
