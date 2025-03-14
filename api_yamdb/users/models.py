from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Кастомная модель пользователя."""

    email = models.EmailField(unique=True)
    role = models.CharField(
        choices=[
            ('user', 'пользователь'),
            ('moderator', 'модератор'),
            ('admin', 'админ'),
        ],
        max_length=9,
        default='user',
        verbose_name='роль',
    )
    bio = models.TextField(
        max_length=512, blank=True, verbose_name='биография'
    )

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('date_joined', 'role')

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser

    @property
    def is_admin_or_moderator(self):
        return self.is_admin or self.role == 'moderator'
