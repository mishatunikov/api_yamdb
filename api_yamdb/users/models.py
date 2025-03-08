from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from api.const import CODE_LENGTH


class CustomUser(AbstractUser):
    """Кастомная модель пользователя."""

    email = models.EmailField(_("email address"), unique=True)
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


class ConfirmationCode(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name='confirmation_code'
    )
    code = models.CharField(max_length=CODE_LENGTH)
    created_at = models.DateTimeField(
        auto_now=True, verbose_name='время создания'
    )

    def __str__(self):
        return self.code
