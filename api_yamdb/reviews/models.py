from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from reviews.validators import year_not_in_future

from reviews.const import MIN_SCORE, MAX_SCORE


User = get_user_model()


class BaseNameSlug(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=256,
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=50,
        unique=True,
    )

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name


class Category(BaseNameSlug):
    """Категории произведений."""

    class Meta(BaseNameSlug.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(BaseNameSlug):
    """Жанр произведения."""

    class Meta(BaseNameSlug.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    """Модель для представления произведения."""

    name = models.CharField(
        max_length=256, verbose_name='Название произведения'
    )
    description = models.TextField(
        max_length=200,
        verbose_name='Краткое описание произведения',
        blank=True,
    )

    year = models.SmallIntegerField(
        verbose_name='Год издания',
        validators=[
            year_not_in_future,
        ],
        db_index=True,
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles',
        verbose_name='Категория',
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='genres',
        verbose_name='Жанр',
    )

    class Meta:
        ordering = ('category', 'name')
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return f'{self.name}, {str(self.year)}, {self.category}'


class ReviewCommentModel(models.Model):
    """Абстрактная модель для отзывов и комментариев."""

    text = models.TextField('Текст')
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        on_delete=models.CASCADE,
    )
    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        abstract = True
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text


class Review(ReviewCommentModel):
    """Модель для отзывов пользователей на произведения."""

    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    score = models.SmallIntegerField(
        'Оценка произведения',
        validators=[
            MinValueValidator(
                MIN_SCORE, message='Оценка должна быть больше или равна 1'
            ),
            MaxValueValidator(
                MAX_SCORE, message='Оценка должна быть меньше или равна 10'
            ),
        ],
    )

    class Meta(ReviewCommentModel.Meta):
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author'), name='unique_review'
            ),
        ]


class Comment(ReviewCommentModel):
    """Модель комментариев к отзывам."""

    review = models.ForeignKey(
        Review,
        verbose_name='Отзыв',
        on_delete=models.CASCADE,
        related_name='comments',
    )

    class Meta(ReviewCommentModel.Meta):
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
