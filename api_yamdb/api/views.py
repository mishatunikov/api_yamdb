from django.db.models import Avg
from django.utils import timezone
from django.utils.crypto import get_random_string
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework_simplejwt.tokens import AccessToken

from api import const
from api.filters import GenreCategoryFilter
from api.permissions import (
    IsAdminOrOwnerOrReadOnly,
    IsAdminOrReadOnly,
    IsAdminOrSuperuser,
)
from api.serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    SignUpSerializer,
    TitleGetSerializer,
    TitleSerializer,
    TokenAccessObtainSerializer,
    UserSerializer,
)
from api.utils import send_confirmation_code
from reviews.models import Category, Genre, Review, Title, User
from users.models import ConfirmationCode


class SignUpAPIView(APIView):
    """Обрабатывает POST запрос на регистрацию нового пользователя."""

    def post(self, request):
        data = request.data
        serializer = SignUpSerializer(data=data)
        user = User.objects.filter(
            username=data.get('username'), email=data.get('email')
        ).first()
        if user:
            updated_confirmation_code = get_random_string(const.CODE_LENGTH)
            # Т.к. создание админа через createsuperuser или создание админом
            # нового пользователя не создает кода и не отправляет его через
            # email -> нужна дополнительная проверка.
            confirmation_code, created = (
                ConfirmationCode.objects.get_or_create(
                    user=user, defaults={'code': updated_confirmation_code}
                )
            )
            # if not created:
            #     diff_time = (
            #         timezone.now() - user.confirmation_code.created_at
            #     ).seconds
            #     if diff_time < const.TIMEOUT:
            #         return Response(
            #             {
            #                 'message': f'Повторная отправка кода возможна '
            #                 f'через {const.TIMEOUT - diff_time} секунд.'
            #             },
            #             status=status.HTTP_200_OK,
            #         )
            confirmation_code.code = updated_confirmation_code
            confirmation_code.save()

            send_confirmation_code(confirmation_code.code, user.email)
            return Response(
                serializer.initial_data,
                status=status.HTTP_200_OK,
            )

        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        confirmation_code = ConfirmationCode.objects.create(
            user=instance, code=get_random_string(const.CODE_LENGTH)
        )
        send_confirmation_code(confirmation_code, instance.email)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenAccessObtainView(APIView):
    """Обрабатывает POST запрос на получения токена."""

    def post(self, request):
        serializer = TokenAccessObtainSerializer(
            data=request.data, context=request.data
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        access_token = AccessToken.for_user(user)

        return Response(
            {'token': str(access_token)}, status=status.HTTP_200_OK
        )


class UserViewSet(ModelViewSet):
    """Обрабатывает запросы к данным пользователей."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminOrSuperuser,)
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    http_method_names = (
        'get',
        'post',
        'patch',
        'delete',
    )

    def get_permissions(self):
        if 'me' in self.request.path:
            return [
                IsAuthenticated(),
            ]
        return super().get_permissions()

    @action(methods=['get'], detail=False, url_name='me')
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @me.mapping.patch
    def me_update(self, request):
        serializer = UserSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.validated_data.pop('role', None)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class CategoryGenre(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    """Класс для работы с категориями и жанрами."""

    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class CategoryViewSet(CategoryGenre):
    """ViewSet для работы с категориями."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenre):
    """ViewSet для работы с жанрами."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(ModelViewSet):
    """ViewSet для работы с объектами модели Title."""

    queryset = Title.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    http_method_names = (
        'get',
        'post',
        'patch',
        'delete',
    )
    filter_backends = (
        DjangoFilterBackend,
        GenreCategoryFilter,
        OrderingFilter,
    )
    filterset_fields = (
        'name',
        'year',
        'category__slug',
        'genre__slug',
    )

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitleGetSerializer
        return TitleSerializer

    def get_queryset(self):
        if self.action in ('list', 'retrieve'):
            queryset = (
                Title.objects.prefetch_related('reviews')
                .all()
                .annotate(rating=Avg('reviews__score'))
                .order_by('name')
            )
            return queryset
        return Title.objects.all()


class ReviewViewSet(ModelViewSet):
    """Вьюсет для работы с отзывами."""

    http_method_names = (
        'get',
        'post',
        'patch',
        'delete',
    )
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminOrOwnerOrReadOnly,)

    def get_title(self):
        """Получает произведение с предзагрузкой связанных данных."""
        return get_object_or_404(
            Title.objects.select_related("category"),
            id=self.kwargs.get("title_id"),
        )

    def get_queryset(self):
        """Возвращает список отзывов для конкретного произведения."""
        return self.get_title().reviews.select_related("author")

    def perform_create(self, serializer):
        """Создаёт отзыв с указанием автора и произведения."""
        serializer.save(
            author=self.request.user,
            title=self.get_title(),
        )


class CommentViewSet(ModelViewSet):
    """Вьюсет для работы с комментариями."""

    http_method_names = (
        'get',
        'post',
        'patch',
        'delete',
    )
    serializer_class = CommentSerializer
    permission_classes = (IsAdminOrOwnerOrReadOnly,)

    def get_review(self):
        """Получает отзыв с предзагрузкой автора и произведения."""
        return get_object_or_404(
            Review.objects.select_related("author", "title"),
            id=self.kwargs.get("review_id"),
        )

    def get_queryset(self):
        """Возвращает список комментариев для конкретного отзыва."""
        return (
            self.get_review()
            .comments.select_related("author")
            .prefetch_related("review")
        )

    def perform_create(self, serializer):
        """Создаёт комментарий с указанием автора и отзыва."""
        serializer.save(
            author=self.request.user,
            review=self.get_review(),
        )
