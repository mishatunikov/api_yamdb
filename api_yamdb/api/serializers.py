from django.contrib.auth.tokens import default_token_generator
from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from api import const
from reviews.models import Category, Comment, Genre, Review, Title, User


class UserBaseSerializer(serializers.ModelSerializer):
    """Базовый класс для сериализации модели User"""

    class Meta:
        model = User

    def validate_username(self, value):
        if value.lower() in const.FORBIDDEN_USERNAMES:
            raise serializers.ValidationError('Недопустимый username.')
        return value


class SignUpSerializer(UserBaseSerializer):
    """Сериализатор для свмостоятельной регистрации нового пользователя."""

    class Meta(UserBaseSerializer.Meta):
        fields = (
            'email',
            'username',
        )


class TokenAccessObtainSerializer(serializers.Serializer):
    """
    Сериализатор для аутентификации пользователя по коду подтверждения.
    """

    username = serializers.CharField(max_length=150, required=True)
    confirmation_code = serializers.CharField(required=True)

    def validate(self, attrs):
        user = get_object_or_404(User, username=attrs.get('username'))

        if not default_token_generator.check_token(
            user, attrs['confirmation_code']
        ):
            raise serializers.ValidationError('Введен неверный код')
        attrs['user'] = user
        return attrs


class UserSerializer(UserBaseSerializer):
    """Сериализатор для взаимодействия с данными пользователей."""

    class Meta(UserBaseSerializer.Meta):
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )


class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Category.
    """

    class Meta:
        model = Category
        exclude = ('id',)


class GenreSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Category.
    """

    class Meta:
        model = Genre
        exclude = ('id',)


class TitleGetSerializer(serializers.ModelSerializer):
    """
    Сериализатор на чтение для модели Title.
    """

    rating = serializers.IntegerField(read_only=True, default=None)
    genre = GenreSerializer(many=True)
    category = CategorySerializer()

    class Meta:
        model = Title
        fields = '__all__'


class TitleSerializer(TitleGetSerializer):
    """
    Сериализатор на запись для модели Title.
    """

    genre = serializers.SlugRelatedField(
        slug_field='slug',
        many=True,
        queryset=Genre.objects.all(),
        required=True,
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all(), required=True
    )

    class Meta(TitleGetSerializer.Meta):
        pass

    def to_representation(self, instance):
        return TitleGetSerializer(instance).to_representation(instance)

    def validate_genre(self, value):
        if not value:
            raise serializers.ValidationError(
                'Необходимо указать минимум один genre.'
            )
        return value


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов."""

    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )
    score = serializers.IntegerField(
        validators=[
            MinValueValidator(const.MIN_SCORE),
            MaxValueValidator(const.MAX_SCORE),
        ]
    )

    def validate(self, data):
        """Запрещает пользователям оставлять повторные отзывы."""
        request = self.context.get('request')
        view = self.context.get('view')

        if request and request.method == 'POST':
            author = request.user
            title_id = view.kwargs.get('title_id')
            if Review.objects.filter(
                title_id=title_id, author=author
            ).exists():
                raise serializers.ValidationError(
                    'Нельзя добавить больше 1 отзыва на произведение.',
                    code='unique',
                )
        return data

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('author',)


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('author',)
