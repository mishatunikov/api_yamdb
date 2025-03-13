from django.core.exceptions import ValidationError
from django.utils import timezone


def year_not_in_future(year: int):
    if year > timezone.now().year:
        raise ValidationError('Год не может быть больше текущего!')
    return year
