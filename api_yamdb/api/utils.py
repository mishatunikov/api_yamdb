from django.core.mail import send_mail


def send_confirmation_code(confirmation_code: str, email: str) -> None:
    """Отправляет письмо с кодом подтверждения ка указанный email."""
    send_mail(
        'Код подтверждения',
        f'Ваш код: {confirmation_code}',
        from_email='test_api@test.ru',
        recipient_list=[email],
    )
