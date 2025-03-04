from django.db import models
from pytils.translit import slugify


class Category(models.Model):
    """Категории произведений.

    Произведения относятся к категориям: «Книги», «Фильмы», «Музыка».
    Новая категория может быть добавленаа администратором.
    """
    name = models.CharField(
        max_length=100,
        unique=True
    )
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Genre(models.Model):
    """Жанр произведения.

    Произведению может быть присвоен жанр «Сказка», «Рок», «Артхаус».
    Добавить новый жанр может только администратор.
    """
    name = models.CharField(
        max_length=100,
        unique=True
    )
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Title(models.Model):
    """Произведение.

    """
    name = models.CharField(
        max_length=100,
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
