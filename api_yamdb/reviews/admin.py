from django.contrib import admin
from .models import Category, Genre, Title, Review, Comment


class CategoryGenreAdminBase(admin.ModelAdmin):

    list_display = (
        'name',
        'slug',
        'id',
    )
    list_filter = search_fields = (
        'name',
        'slug',
    )


@admin.register(Category)
class CategoryAdmin(CategoryGenreAdminBase):
    pass


@admin.register(Genre)
class GenreAdmin(CategoryGenreAdminBase):
    pass


class CommentReviewAdmin(admin.ModelAdmin):

    @admin.display(description='Сокращенный текст')
    def short_text(self, obj) -> str:
        """Выводит сокращенный текст."""
        max_words = 10
        words = obj.text.split()
        shortened_text = ' '.join(words[:max_words])
        if len(words) > max_words:
            shortened_text += '...'
        return shortened_text


@admin.register(Comment)
class CommentAdmin(CommentReviewAdmin):

    list_display = (
        'short_text',
        'author',
        'pub_date',
        'review_id',
    )
    search_fields = (
        'author',
        'review_id',
    )
    list_filter = ('pub_date',)


@admin.register(Review)
class ReviewAdmin(CommentReviewAdmin):

    list_display = (
        'short_text',
        'author',
        'title',
        'score',
        'pub_date',
    )
    search_fields = (
        'author',
        'title',
    )
    list_filter = (
        'score',
        'pub_date',
    )


class ReviewInline(admin.StackedInline):

    model = Review
    extra = 0


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):

    inlines = (ReviewInline,)
    list_display = (
        'name',
        'year',
        'category',
        'genres',
    )

    @admin.display(description='Жанры')
    def genres(self, obj):
        return '/'.join(genre.name for genre in obj.genre.all())

    list_editable = ('category',)
    filter_horizontal = ('genre',)


admin.site.empty_value_display = 'На задано'
