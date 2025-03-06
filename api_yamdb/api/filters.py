from rest_framework import filters


class GenreCategoryFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        category = request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        genre = request.query_params.get('genre')
        if genre:
            queryset = queryset.filter(genre__slug=genre)
        return queryset
