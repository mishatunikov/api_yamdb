from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
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

from api.filters import TitleFilterSet
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


class SignUpAPIView(APIView):
    """Обрабатывает POST запрос на регистрацию нового пользователя."""

    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')

        user = User.objects.filter(username=username, email=email).first()

        if user:
            confirmation_code = default_token_generator.make_token(user)
            send_confirmation_code(confirmation_code, user.email)
            return Response(
                {'email': email, 'username': username},
                status=status.HTTP_200_OK,
            )

        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        confirmation_code = default_token_generator.make_token(user)
        send_confirmation_code(confirmation_code, user.email)
        return Response(
            serializer.validated_data,
            status=status.HTTP_200_OK,
        )


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
        OrderingFilter,
    )
    filterset_class = TitleFilterSet

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitleGetSerializer
        return TitleSerializer

    def get_queryset(self):
        return (
            Title.objects.prefetch_related('reviews')
            .all()
            .annotate(rating=Avg('reviews__score'))
            .order_by('name')
        )


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
        return get_object_or_404(
            Title.objects.select_related('category'),
            id=self.kwargs.get('title_id'),
        )

    def get_queryset(self):
        return self.get_title().reviews.select_related('author')

    def perform_create(self, serializer):
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
        return get_object_or_404(
            Review.objects.select_related('author', 'title'),
            id=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('title_id'),
        )

    def get_queryset(self):
        return (
            self.get_review()
            .comments.select_related('author')
            .prefetch_related('review')
        )

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review=self.get_review(),
        )
