from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.contrib.auth import get_user_model


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
    """Категории произведений.

    Произведения относятся к категориям: «Книги», «Фильмы», «Музыка».
    Новая категория может быть добавленаа администратором.
    """

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(BaseNameSlug):
    """Жанр произведения.

    Произведению может быть присвоен жанр «Сказка», «Рок», «Артхаус».
    Добавить жанр может только администратор.
    """

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    """Произведение.

    """
    name = models.CharField(
        max_length=256,
        verbose_name='Название произведения'
    )
    description = models.TextField(
        max_length=200,
        verbose_name='Краткое описание произведения',
        null=True,
        blank=True,
    )

    year = models.PositiveSmallIntegerField(
        verbose_name='Год издания',
    )

    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        null=True,
        related_name='titles',
        verbose_name='Категория'
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
        Title, verbose_name='Произведение', on_delete=models.CASCADE,
        related_name='reviews'
    )
    score = models.SmallIntegerField(
        'Оценка произведения',
        validators=[
            MinValueValidator(
                1, message='Оценка должна быть больше или равна 1'
            ),
            MaxValueValidator(
                10, message='Оценка должна быть меньше или равна 10'
            ),
        ]
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
        Review, verbose_name='Отзыв', on_delete=models.CASCADE,
        related_name='comments'
    )

    class Meta(ReviewCommentModel.Meta):
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
