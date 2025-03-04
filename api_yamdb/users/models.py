from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    """Кастомная модель пользователя."""

    email = models.EmailField(
        _("email address"), verbose_name='электронная почта'
    )
    role = models.CharField(
        choices=[
            ('user', 'пользователь'),
            ('moderator', 'модератор'),
            ('admin', 'админ'),
        ],
        default='user',
        verbose_name='роль',
    )
    bio = models.TextField(
        max_length=512, blank=True, null=True, verbose_name='биография'
    )

    is_active = models.BooleanField(
        _("active"),
        default=False,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    confirmation_code = models.CharField(
        null=True, blank=True, verbose_name='код подтверждения'
    )
    confirmation_code_created_at = models.DateTimeField(
        null=True, blank=True, verbose_name='время создания кода'
    )

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_username_email'
            )
        ]
