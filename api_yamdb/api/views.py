from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets, mixins
from rest_framework.pagination import PageNumberPagination

from reviews.models import Category, Genre, Title
from .filters import GenreCategoryFilter
from .permissions import IsAdminOrReadOnly
from .serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleGetSerializer,
    TitleSerializer,
)


class CategoryGenre(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class CategoryViewSet(CategoryGenre):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenre):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    http_method_names = ('get', 'post', 'patch', 'delete',)
    filter_backends = (
        DjangoFilterBackend,
        filters.OrderingFilter,
        GenreCategoryFilter,
    )
    filterset_fields = ('name', 'year', 'category__slug', 'genre__slug',)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitleGetSerializer
        return TitleSerializer
