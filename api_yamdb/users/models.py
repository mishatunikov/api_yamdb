from django.contrib.auth.models import AbstractUser
from django.db import models

from users.const import MAX_BIO_LENGHT, MAX_ROLE_LENGTH


class CustomUser(AbstractUser):
    """Кастомная модель пользователя."""

    class Role(models.TextChoices):
        USER = 'user', 'пользователь'
        MODERATOR = 'moderator', 'модератор'
        ADMIN = 'admin', 'админ'

    email = models.EmailField(unique=True)
    role = models.CharField(
        choices=Role.choices,
        max_length=MAX_ROLE_LENGTH,
        default='user',
        verbose_name=Role.USER,
    )
    bio = models.TextField(
        max_length=MAX_BIO_LENGHT, blank=True, verbose_name='биография'
    )

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('date_joined', 'role')

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_admin_or_moderator(self):
        return self.is_admin or self.role == self.Role.MODERATOR
