from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg
from django.utils.crypto import get_random_string
from rest_framework import status, mixins
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework_simplejwt.tokens import AccessToken

from api import const
from api.permissions import IsAdminOrSuperuser, IsAdminOrReadOnly
from api.filters import GenreCategoryFilter
from api.serializers import (
    SignUpSerializer,
    TokenAccessObtainSerializer,
    UserSerializer,
    CategorySerializer,
    GenreSerializer,
    TitleGetSerializer,
    TitleSerializer,
)
from api.utils import send_confirmation_code
from reviews.models import User, Category, Genre, Title
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
            if not created:
                diff_time = (
                    timezone.now() - user.confirmation_code.created_at
                ).seconds
                if diff_time < const.TIMEOUT:
                    return Response(
                        {
                            'message': f'Повторная отправка кода возможна '
                            f'через {const.TIMEOUT - diff_time} секунд.'
                        },
                        status=status.HTTP_200_OK,
                    )
                confirmation_code.code = updated_confirmation_code
                confirmation_code.save()

            send_confirmation_code(confirmation_code.code, user.email)
            return Response(
                {'message': 'Код отправлен на ваш email'},
                status=status.HTTP_200_OK,
            )

        if serializer.is_valid():
            instance = serializer.save()
            confirmation_code = ConfirmationCode.objects.create(
                user=instance, code=get_random_string(const.CODE_LENGTH)
            )
            send_confirmation_code(confirmation_code, instance.email)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenAccessObtainView(APIView):
    """Обрабатывает POST запрос на получения токена."""

    def post(self, request):
        serializer = TokenAccessObtainSerializer(
            data=request.data, context=request.data
        )
        if serializer.is_valid():
            user = serializer.validated_data['user']
            access_token = AccessToken.for_user(user)

            return Response(
                {'token': str(access_token)}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
            return [IsAuthenticated(),]
        return super().get_permissions()

    @action(methods=['get', 'patch'], detail=False, url_name='me')
    def current_user_data(self, request):
        if request.method == 'PATCH':
            serializer = UserSerializer(
                request.user, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.validated_data.pop('role', None)
                serializer.save()
                return Response(
                    data=serializer.data, status=status.HTTP_200_OK
                )
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(request.user)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class CategoryGenre(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class CategoryViewSet(CategoryGenre):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenre):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(ModelViewSet):
    queryset = Title.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete',)
    filter_backends = (
        DjangoFilterBackend,
        OrderingFilter,
        GenreCategoryFilter,
    )
    filterset_fields = ('name', 'year', 'category__slug', 'genre__slug',)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitleGetSerializer
        return TitleSerializer

    def get_queryset(self):
        if self.action in ('list', 'retrieve'):
            queryset = (Title.objects.prefetch_related('reviews').all().
                        annotate(rating=Avg('reviews__score')).
                        order_by('name'))
            return queryset
        return Title.objects.all()
