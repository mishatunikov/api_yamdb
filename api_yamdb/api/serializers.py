from django.contrib.auth.tokens import default_token_generator
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from api import const
# from api.const import MIN_SCORE, MAX_SCORE
from reviews.models import Category, Comment, Genre, Review, Title, User


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
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category',
        )


class TitleSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Title.

    Включает в себя поля для жанров и категорий, которые представлены
    в виде SlugRelatedField.
    """

    genre = serializers.SlugRelatedField(
        slug_field='slug', many=True, queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = '__all__'

    def validate_year(self, value):
        year_today = timezone.now().year
        if value > year_today:
            raise serializers.ValidationError('Проверьте год издания!')
        return value


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов."""

    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )
    score = serializers.IntegerField(
        validators=[
            MinValueValidator(const.MIN_SCORE),
            MaxValueValidator(const.MAX_SCORE)
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
